import subprocess
import xml.etree.ElementTree as ET
from PyQt6.QtCore import QThread, pyqtSignal
from database.db_manager import DatabaseManager
from core.mame_parser import clean_bytes_to_text
from utils.path_helper import PathHelper


class RomsetImportThread(QThread):
    """
    Importa el catálogo COMPLETO de juegos soportados por el core ejecutando
    `mame.exe -listxml` (sin argumentos) e insertando/actualizando cada máquina
    jugable en la base de datos local, replicando el conteo total de MAMEP/MAMEUI.
    """
    progress = pyqtSignal(str)
    import_finished = pyqtSignal(int)
    import_error = pyqtSignal(str)

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

    def run(self):
        mame_exe = PathHelper.get_mame_executable()
        if not mame_exe or not mame_exe.exists():
            self.import_error.emit("No se encontró mame.exe. Configura su ruta antes de importar el romset.")
            return

        self.progress.emit("Ejecutando mame.exe -listxml (esto puede tardar un momento)...")
        try:
            result = subprocess.run([str(mame_exe), "-listxml"], capture_output=True)
        except Exception as e:
            self.import_error.emit(f"Error ejecutando mame.exe -listxml: {e}")
            return

        if not result.stdout:
            self.import_error.emit("mame.exe -listxml no devolvió datos.")
            return

        self.progress.emit("Analizando catálogo XML del core...")
        try:
            xml_text = clean_bytes_to_text(result.stdout)
            root = ET.fromstring(xml_text)
        except Exception as e:
            self.import_error.emit(f"Error analizando el XML del romset: {e}")
            return

        rows = []
        for machine in root.findall("machine"):
            # Excluir slots/dispositivos internos que no son juegos jugables
            if machine.get("isdevice") == "yes":
                continue

            rom_name = machine.get("name", "").lower()
            if not rom_name:
                continue

            is_clone = 1 if "cloneof" in machine.attrib else 0
            parent_rom = machine.get("cloneof", "")

            desc_elem = machine.find("description")
            title = desc_elem.text if desc_elem is not None and desc_elem.text else rom_name

            year_elem = machine.find("year")
            year = year_elem.text if year_elem is not None and year_elem.text else "Desconocido"

            manuf_elem = machine.find("manufacturer")
            manufacturer = manuf_elem.text if manuf_elem is not None and manuf_elem.text else "Desconocido"

            driver_elem = machine.find("driver")
            driver_status = driver_elem.get("status", "good") if driver_elem is not None else "good"

            source_file = machine.get("sourcefile", "")

            rows.append((rom_name, title, year, manufacturer, source_file, driver_status, is_clone, parent_rom))

        self.progress.emit(f"Guardando {len(rows)} juegos en la base de datos local...")
        with self.db_manager.get_connection() as conn:
            conn.executemany("""
                INSERT INTO games (rom_name, title, year, manufacturer, driver, driver_status, is_clone, parent_rom, has_rom)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                ON CONFLICT(rom_name) DO UPDATE SET
                    title = excluded.title,
                    year = excluded.year,
                    manufacturer = excluded.manufacturer,
                    driver = excluded.driver,
                    driver_status = excluded.driver_status,
                    is_clone = excluded.is_clone,
                    parent_rom = excluded.parent_rom
            """, rows)
            conn.commit()

        self.import_finished.emit(len(rows))
