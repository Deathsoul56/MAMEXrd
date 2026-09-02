import base64
import tempfile
from pathlib import Path
from PyQt6.QtGui import QIcon
from utils.app_icon_data import MAMEX_ICON_BASE64

_cached_icon: QIcon | None = None


def get_app_icon() -> QIcon:
    """Icono de MAMEXrd decodificado desde datos embebidos (funciona igual en dev y en el .exe compilado).

    Se escribe a un archivo temporal porque QIcon(path) sí conserva todas las
    resoluciones embebidas en el .ico (16/24/32/48/64/128/256), a diferencia de
    QPixmap.loadFromData(), que solo decodifica un único frame.
    """
    global _cached_icon
    if _cached_icon is None:
        ico_path = Path(tempfile.gettempdir()) / "mamexrd_app_icon.ico"
        ico_path.write_bytes(base64.b64decode(MAMEX_ICON_BASE64))
        _cached_icon = QIcon(str(ico_path))
    return _cached_icon
