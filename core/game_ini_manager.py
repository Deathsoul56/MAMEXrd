from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET
from core.ini_base import IniKeyValueStore
from utils.path_helper import PathHelper


class GameIniManager(IniKeyValueStore):
    """
    Gestor de archivos .ini específicos por ROM (ej. ini/sf2ce.ini).
    MAME carga automáticamente estos archivos (según inipath en mame.ini) y sus
    valores tienen prioridad sobre mame.ini solo para ese juego en particular.
    A diferencia de MAMEIniManager, no depende de -createconfig: el archivo
    solo contiene las claves que el usuario decide sobreescribir para el juego.
    """
    def __init__(self, rom_name: str, mame_dir: Optional[Path] = None):
        super().__init__()
        if mame_dir:
            self.mame_dir = mame_dir
        else:
            exe = PathHelper.get_mame_executable()
            self.mame_dir = exe.parent if exe else PathHelper.get_base_dir()

        self.rom_name = rom_name
        self.ini_filename = f"{rom_name}.ini"
        self.ini_path = self.mame_dir / "ini" / self.ini_filename
        self.load_ini()

    def load_ini(self):
        """Parsea el .ini específico del juego (si existe) en pares clave-valor."""
        self.settings.clear()
        if not self.ini_path.exists():
            return
        try:
            with open(self.ini_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    parsed = self.parse_line(line)
                    if parsed:
                        self.settings[parsed[0]] = parsed[1]
        except Exception as e:
            print(f"Error cargando {self.ini_filename}: {e}")

    def clear(self, key: str):
        """Quita el override de una clave: el juego vuelve a heredar el valor global de mame.ini."""
        self.settings.pop(key, None)

    def save(self) -> bool:
        """Escribe solo las claves con override real. Si no queda ninguna, borra el archivo."""
        try:
            if not self.settings:
                if self.ini_path.exists():
                    self.ini_path.unlink()
                return True

            self.ini_path.parent.mkdir(parents=True, exist_ok=True)
            lines = [f"# Configuración específica para '{self.rom_name}' (generado por MAMEXrd)\n"]
            for key, value in self.settings.items():
                lines.append(f"{key:<25} {value}\n")

            with open(self.ini_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True
        except Exception as e:
            print(f"Error guardando {self.ini_filename}: {e}")
            return False

    def sync_cfg_view(self, view_name: Optional[str], target_index: int = 0) -> bool:
        """
        MAME guarda la última vista de pantalla usada en cfg/<rom>.cfg
        (<system><video><target index view="..."/>) y esa vista GUARDADA tiene
        prioridad sobre mame.ini/ini/<rom>.ini al iniciar. Sin este ajuste, un
        override de view0 por .ini nunca se vería reflejado si el juego ya se
        jugó antes y quedó un valor distinto grabado en su .cfg.
        `view_name=None` borra el valor guardado para volver a heredar el .ini.
        No hace nada si el juego nunca generó un .cfg (nada que sincronizar).
        """
        cfg_path = self.mame_dir / "cfg" / f"{self.rom_name}.cfg"
        if not cfg_path.exists():
            return True
        try:
            tree = ET.parse(cfg_path)
            root = tree.getroot()
            system = root.find("system")
            if system is None:
                return True
            video = system.find("video")

            if view_name is None:
                if video is not None:
                    target = video.find(f"./target[@index='{target_index}']")
                    if target is not None:
                        video.remove(target)
                    if not list(video):
                        system.remove(video)
            else:
                if video is None:
                    video = ET.SubElement(system, "video")
                target = video.find(f"./target[@index='{target_index}']")
                if target is None:
                    target = ET.SubElement(video, "target")
                    target.set("index", str(target_index))
                target.set("view", view_name)

            tree.write(cfg_path, encoding="utf-8", xml_declaration=True)
            return True
        except Exception as e:
            print(f"Error sincronizando cfg/{self.rom_name}.cfg: {e}")
            return False
