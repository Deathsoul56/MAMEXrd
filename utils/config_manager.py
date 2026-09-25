import configparser
import base64
from pathlib import Path
from typing import Optional, Tuple
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

    def get_window_geometry(self) -> Optional[bytes]:
        """Obtiene la geometría (posición/tamaño) guardada de la ventana principal."""
        raw = self.config.get("Window", "geometry", fallback="")
        if raw:
            try:
                return base64.b64decode(raw)
            except Exception:
                return None
        return None

    def set_window_geometry(self, data: bytes):
        """Guarda la geometría (posición/tamaño) de la ventana principal."""
        if "Window" not in self.config:
            self.config["Window"] = {}
        self.config["Window"]["geometry"] = base64.b64encode(data).decode("ascii")
        self.save_config()

    def get_window_state(self) -> Optional[bytes]:
        """Obtiene el estado guardado de docks/toolbars de la ventana principal."""
        raw = self.config.get("Window", "state", fallback="")
        if raw:
            try:
                return base64.b64decode(raw)
            except Exception:
                return None
        return None

    def set_window_state(self, data: bytes):
        """Guarda el estado de docks/toolbars de la ventana principal."""
        if "Window" not in self.config:
            self.config["Window"] = {}
        self.config["Window"]["state"] = base64.b64encode(data).decode("ascii")
        self.save_config()

    def get_last_category(self) -> Tuple[str, str]:
        """Obtiene la última categoría del Folder List seleccionada (para restaurarla al abrir)."""
        filter_type = self.config.get("State", "last_category_type", fallback="all")
        filter_value = self.config.get("State", "last_category_value", fallback="")
        return filter_type, filter_value

    def set_last_category(self, filter_type: str, filter_value: str):
        """Guarda la última categoría del Folder List seleccionada."""
        if "State" not in self.config:
            self.config["State"] = {}
        self.config["State"]["last_category_type"] = filter_type
        self.config["State"]["last_category_value"] = filter_value
        self.save_config()

    def get_last_media_tab(self) -> int:
        """Obtiene el índice de la última pestaña activa del panel Title/Media."""
        return self.config.getint("State", "last_media_tab", fallback=0)

    def set_last_media_tab(self, index: int):
        """Guarda el índice de la pestaña activa del panel Title/Media."""
        if "State" not in self.config:
            self.config["State"] = {}
        self.config["State"]["last_media_tab"] = str(index)
        self.save_config()
