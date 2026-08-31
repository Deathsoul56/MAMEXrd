import base64
from PyQt6.QtCore import QByteArray
from PyQt6.QtGui import QIcon, QPixmap
from utils.app_icon_data import MAMEX_ICON_BASE64


def get_app_icon() -> QIcon:
    """Icono de MAMEXrd decodificado desde datos embebidos (funciona igual en dev y en el .exe compilado)."""
    raw = QByteArray(base64.b64decode(MAMEX_ICON_BASE64))
    pixmap = QPixmap()
    pixmap.loadFromData(raw, "ICO")
    return QIcon(pixmap)
