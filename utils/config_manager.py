import configparser
from pathlib import Path
from typing import Optional
from utils.path_helper import PathHelper

class ConfigManager:
    """
    Gestor de configuración mamexrd.ini para guardar la ruta del ejecutable MAME,
    carpetas de medios, preferencias visuales y estado de las ventanas.
    """
    INI_FILENAME = "mamexrd.ini"

    def __init__(self):
        self.ini_path = PathHelper.get_base_dir() / self.INI_FILENAME
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """Carga el archivo .ini o crea una configuración por defecto."""
        if self.ini_path.exists():
            try:
                self.config.read(self.ini_path, encoding="utf-8")
            except Exception as e:
                print(f"Error leyendo {self.ini_path}: {e}")

        if "General" not in self.config:
            self.config["General"] = {}

    def save_config(self):
        """Guarda la configuración actual en el disco."""
        try:
            with open(self.ini_path, "w", encoding="utf-8") as f:
                self.config.write(f)
        except Exception as e:
            print(f"Error guardando {self.ini_path}: {e}")

    def get_mame_path(self) -> Optional[Path]:
        """Obtiene la ruta guardada de mame.exe."""
        raw_path = self.config.get("General", "mame_binary", fallback="")
        if raw_path:
            p = Path(raw_path)
            if p.exists():
                return p
        return None

    def set_mame_path(self, path: Path):
        """Establece y guarda la ruta de mame.exe."""
        self.config["General"]["mame_binary"] = str(path)
        self.save_config()
