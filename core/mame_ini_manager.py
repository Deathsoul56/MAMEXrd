import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
from utils.path_helper import PathHelper

class MAMEIniManager:
    """
    Gestor de configuración mame.ini de MAME.
    Lee, parsea y guarda la configuración oficial de MAME respetando su formato interno.
    """
    def __init__(self, mame_dir: Optional[Path] = None):
        if mame_dir:
            self.mame_dir = mame_dir
        else:
            exe = PathHelper.get_mame_executable()
            self.mame_dir = exe.parent if exe else PathHelper.get_base_dir()

        self.ini_path = self.mame_dir / "mame.ini"
        self.settings: Dict[str, str] = {}
        self.lines_raw = []
        self.load_ini()

    def ensure_ini_exists(self) -> bool:
        """Garantiza la existencia de mame.ini ejecutando -createconfig si es necesario."""
        if not self.ini_path.exists():
            exe = PathHelper.get_mame_executable()
            if exe and exe.exists():
                try:
                    res = subprocess.run([str(exe), "-createconfig"], capture_output=True, cwd=str(self.mame_dir))
                    return self.ini_path.exists()
                except Exception as e:
                    print(f"Error generando mame.ini: {e}")
        return self.ini_path.exists()

    def load_ini(self):
        """Parsea mame.ini en pares clave-valor manteniendo el formato original."""
        self.ensure_ini_exists()
        if not self.ini_path.exists():
            return

        self.settings.clear()
        self.lines_raw = []

        try:
            with open(self.ini_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    self.lines_raw.append(line)
                    line_str = line.strip()
                    if not line_str or line_str.startswith("#"):
                        continue
                    
                    # Separar clave y valor por espacio en el formato de mame.ini
                    parts = line_str.split(maxsplit=1)
                    key = parts[0].strip()
                    val = parts[1].strip() if len(parts) > 1 else ""
                    self.settings[key] = val
        except Exception as e:
            print(f"Error cargando mame.ini: {e}")

    def get(self, key: str, fallback: str = "") -> str:
        """Obtiene el valor de una clave de configuración."""
        return self.settings.get(key, fallback)

    def get_bool(self, key: str, fallback: bool = False) -> bool:
        """Obtiene un valor booleano (1 o 0)."""
        val = self.get(key, "1" if fallback else "0")
        return val.strip() in ("1", "yes", "true")

    def set(self, key: str, value: str):
        """Establece el valor de una clave de configuración."""
        self.settings[key] = str(value)

    def set_bool(self, key: str, value: bool):
        """Establece un valor booleano como 1 o 0."""
        self.settings[key] = "1" if value else "0"

    def save(self) -> bool:
        """Escribe los cambios actualizados en mame.ini."""
        if not self.ini_path.exists():
            if not self.ensure_ini_exists():
                return False

        try:
            # Reconstruir el archivo mame.ini preservando comentarios y estructura
            new_lines = []
            updated_keys = set()

            with open(self.ini_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line in lines:
                line_str = line.strip()
                if not line_str or line_str.startswith("#"):
                    new_lines.append(line)
                    continue

                parts = line_str.split(maxsplit=1)
                key = parts[0].strip()
                if key in self.settings:
                    new_val = self.settings[key]
                    # Formato nativo de MAME con tabulación fija
                    new_lines.append(f"{key:<25} {new_val}\n")
                    updated_keys.add(key)
                else:
                    new_lines.append(line)

            # Escribir el archivo final
            with open(self.ini_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            print(f"mame.ini guardado exitosamente en: {self.ini_path}")
            return True
        except Exception as e:
            print(f"Error guardando mame.ini: {e}")
            return False
