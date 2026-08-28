import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
from utils.path_helper import PathHelper
from database.db_manager import DatabaseManager

def clean_bytes_to_text(raw_bytes: bytes) -> str:
    """Elimina caracteres nulos a nivel de byte antes de decodificar a texto."""
    if not raw_bytes:
        return ""
    if raw_bytes.startswith(b'\xff\xfe') or raw_bytes.startswith(b'\xfe\xff'):
        text = raw_bytes.decode("utf-16", errors="ignore")
    else:
        clean_b = raw_bytes.replace(b'\x00', b'')
        text = clean_b.decode("utf-8", errors="ignore")
    return text.replace('\x00', '')

class MAMEInfoParser:
    """
    Parser oficial de metadatos de MAME.
    Utiliza mame.exe (-listfull y -listxml) para obtener títulos exactos,
    años de lanzamiento, desarrolladores, relaciones de clones y estado de los drivers.
    """
    def __init__(self, mame_executable: Optional[Path] = None, db_manager: Optional[DatabaseManager] = None):
        self.mame_exe = mame_executable or PathHelper.get_mame_executable()
        if not self.mame_exe.exists():
            local_dev_mame = PathHelper.get_base_dir() / "MAME 0.289" / "mame.exe"
            if local_dev_mame.exists():
                self.mame_exe = local_dev_mame

        self.db_manager = db_manager or DatabaseManager()

    def update_titles_from_listfull(self, rom_list: Optional[List[str]] = None) -> int:
        """
        Ejecuta `mame.exe -listfull` para obtener títulos limpios y oficiales de las ROMs.
        """
        if not self.mame_exe.exists():
            print(f"mame.exe no encontrado en: {self.mame_exe}")
            return 0

        cmd = [str(self.mame_exe), "-listfull"]
        if rom_list:
            cmd.extend(rom_list[:200])

        try:
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode != 0:
                return 0

            stdout_text = clean_bytes_to_text(result.stdout)

            updates = []
            for line in stdout_text.splitlines():
                line_str = line.strip()
                if not line_str or line_str.startswith("Name:") or line_str.startswith("----"):
                    continue
                
                parts = line_str.split(maxsplit=1)
                if len(parts) == 2:
                    rom_name = parts[0].strip().lower()
                    description = parts[1].strip().strip('"')
                    updates.append((description, rom_name))

            if updates:
                with self.db_manager.get_connection() as conn:
                    conn.executemany(
                        "UPDATE games SET title = ? WHERE rom_name = ?",
                        updates
                    )
                    conn.commit()
                print(f"Títulos actualizados para {len(updates)} juegos vía -listfull.")
                return len(updates)

        except Exception as e:
            import traceback
            print(f"Excepción en update_titles_from_listfull: {e}")
            traceback.print_exc()

        return 0

    def update_metadata_from_listxml(self, rom_list: List[str]) -> int:
        """
        Ejecuta `mame.exe -listxml <roms>` para extraer año, fabricante, clones y driver status.
        """
        if not self.mame_exe.exists() or not rom_list:
            return 0

        batch_size = 100
        total_updated = 0

        for i in range(0, len(rom_list), batch_size):
            chunk = rom_list[i:i + batch_size]
            cmd = [str(self.mame_exe), "-listxml"] + chunk

            try:
                result = subprocess.run(cmd, capture_output=True)
                if result.returncode != 0 or not result.stdout:
                    continue

                xml_clean = clean_bytes_to_text(result.stdout)
                root = ET.fromstring(xml_clean)
                updates = []

                for machine in root.findall("machine"):
                    rom_name = machine.get("name", "").lower()
                    is_clone = 1 if "cloneof" in machine.attrib else 0
                    parent_rom = machine.get("cloneof", "")

                    desc_elem = machine.find("description")
                    title = desc_elem.text if desc_elem is not None else rom_name

                    year_elem = machine.find("year")
                    year = year_elem.text if year_elem is not None else "Desconocido"

                    manuf_elem = machine.find("manufacturer")
                    manufacturer = manuf_elem.text if manuf_elem is not None else "Desconocido"

                    driver_elem = machine.find("driver")
                    driver_status = driver_elem.get("status", "good") if driver_elem is not None else "good"

                    updates.append((
                        title,
                        year,
                        manufacturer,
                        driver_status,
                        is_clone,
                        parent_rom,
                        rom_name
                    ))

                if updates:
                    with self.db_manager.get_connection() as conn:
                        conn.executemany("""
                            UPDATE games 
                            SET title = ?, year = ?, manufacturer = ?, driver_status = ?, is_clone = ?, parent_rom = ?
                            WHERE rom_name = ?
                        """, updates)
                        conn.commit()
                    total_updated += len(updates)

            except Exception as e:
                print(f"Excepción parseando XML para lote {i}: {e}")

        print(f"Metadatos completos XML actualizados para {total_updated} juegos.")
        return total_updated
