from typing import Dict, Optional, Tuple


class IniKeyValueStore:
    """Almacén clave-valor compartido por los gestores de archivos .ini de MAME
    (MAMEIniManager, GameIniManager), que solo difieren en cómo leen/escriben el
    archivo en disco pero comparten el mismo formato "clave  valor" por línea.
    """

    def __init__(self):
        self.settings: Dict[str, str] = {}

    @staticmethod
    def parse_line(line: str) -> Optional[Tuple[str, str]]:
        """Devuelve (clave, valor) o None si la línea es un comentario o está vacía."""
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            return None
        parts = line_str.split(maxsplit=1)
        return parts[0].strip(), (parts[1].strip() if len(parts) > 1 else "")

    def get(self, key: str, fallback: str = "") -> str:
        """Obtiene el valor de una clave de configuración."""
        return self.settings.get(key, fallback)

    def get_bool(self, key: str, fallback: bool = False) -> bool:
        """Obtiene un valor booleano (1 o 0)."""
        val = self.get(key, "1" if fallback else "0")
        return val.strip().lower() in ("1", "yes", "true")

    def set(self, key: str, value: str):
        """Establece el valor de una clave de configuración."""
        self.settings[key] = str(value)

    def set_bool(self, key: str, value: bool):
        """Establece un valor booleano como 1 o 0."""
        self.settings[key] = "1" if value else "0"
