import subprocess
from pathlib import Path
from typing import Optional
from core.ini_base import IniKeyValueStore
from utils.path_helper import PathHelper

class MAMEIniManager(IniKeyValueStore):
    """
    Gestor de configuración de archivos .ini de MAME (mame.ini, ui.ini, etc).
    Lee, parsea y guarda la configuración oficial de MAME respetando su formato interno.
    """
    def __init__(self, mame_dir: Optional[Path] = None, ini_filename: str = "mame.ini"):
        super().__init__()
        if mame_dir:
            self.mame_dir = mame_dir
        else:
            exe = PathHelper.get_mame_executable()
            self.mame_dir = exe.parent if exe else PathHelper.get_base_dir()

        self.ini_filename = ini_filename
        self.ini_path = self.mame_dir / ini_filename
        self.lines_raw = []
        self.load_ini()

    def ensure_ini_exists(self) -> bool:
        """Garantiza la existencia del archivo .ini ejecutando -createconfig si es necesario."""
        if not self.ini_path.exists():
            exe = PathHelper.get_mame_executable()
            if exe and exe.exists():
                try:
                    subprocess.run([str(exe), "-createconfig"], capture_output=True, cwd=str(self.mame_dir))
                except Exception as e:
                    print(f"Error generando {self.ini_filename}: {e}")
        return self.ini_path.exists()

    def load_ini(self):
        """Parsea el archivo .ini en pares clave-valor manteniendo el formato original."""
        self.ensure_ini_exists()
        if not self.ini_path.exists():
            return

        self.settings.clear()
        self.lines_raw = []

        try:
            with open(self.ini_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    self.lines_raw.append(line)
                    parsed = self.parse_line(line)
                    if parsed:
                        self.settings[parsed[0]] = parsed[1]
        except Exception as e:
            print(f"Error cargando mame.ini: {e}")

    def save(self) -> bool:
        """Escribe los cambios actualizados en el archivo .ini."""
        if not self.ini_path.exists():
            if not self.ensure_ini_exists():
                return False

        try:
            # Reconstruir el archivo preservando comentarios y estructura
            new_lines = []

            with open(self.ini_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line in lines:
                parsed = self.parse_line(line)
                if parsed and parsed[0] in self.settings:
                    # Formato nativo de MAME con tabulación fija
                    new_lines.append(f"{parsed[0]:<25} {self.settings[parsed[0]]}\n")
                else:
                    new_lines.append(line)

            # Escribir el archivo final
            with open(self.ini_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            print(f"{self.ini_filename} guardado exitosamente en: {self.ini_path}")
            return True
        except Exception as e:
            print(f"Error guardando {self.ini_filename}: {e}")
            return False
