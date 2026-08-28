import os
from pathlib import Path
from typing import List, Set
from PyQt6.QtCore import QThread, pyqtSignal
from utils.path_helper import PathHelper
from database.db_manager import DatabaseManager

class ROMScannerThread(QThread):
    """
    Hilo en segundo plano para escanear la carpeta roms/ y marcar en la BD
    qué ROMs existen localmente (.zip, .7z, .chd).
    """
    scan_finished = pyqtSignal(int)  # Emite el número de ROMs encontradas

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager

    def run(self):
        roms_dir = PathHelper.get_dir("roms")
        if not roms_dir.exists():
            self.scan_finished.emit(0)
            return

        existing_roms: Set[str] = set()
        
        # Buscar archivos .zip y .7z
        for entry in os.scandir(roms_dir):
            if entry.is_file() and (entry.name.endswith(".zip") or entry.name.endswith(".7z")):
                rom_name = Path(entry.name).stem.lower()
                existing_roms.add(rom_name)
            elif entry.is_dir():
                # Directorios de CHD
                existing_roms.add(entry.name.lower())

        # Actualizar en base de datos
        with self.db_manager.get_connection() as conn:
            # Primero resetear estado
            conn.execute("UPDATE games SET has_rom = 0")
            
            # Marcar existentes
            for rom in existing_roms:
                conn.execute("UPDATE games SET has_rom = 1 WHERE rom_name = ?", (rom,))
            
            conn.commit()

        self.scan_finished.emit(len(existing_roms))
