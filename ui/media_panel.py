from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTabWidget, QTextEdit, QFrame
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from utils.path_helper import PathHelper
from core.dat_parser import DATParser

class MediaPreviewPanel(QFrame):
    """
    Panel lateral multi-tab para la visualización de artes (Snapshots, Marquesinas,
    Títulos, Muebles) e información histórica (DATs).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mediaFrame")
        
        self.history_parser = DATParser("history.dat")
        self.history_parser.parse()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Tabs de Medios
        self.tabs = QTabWidget()

        # Tab Captura (Snap)
        self.snap_label = QLabel("Selecciona un juego")
        self.snap_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabs.addTab(self.snap_label, "Snap")

        # Tab Título
        self.title_label = QLabel("Selecciona un juego")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabs.addTab(self.title_label, "Título")

        # Tab Marquesina
        self.marquee_label = QLabel("Selecciona un juego")
        self.marquee_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tabs.addTab(self.marquee_label, "Marquee")

        # Tab Historia
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.tabs.addTab(self.history_text, "Historia")

        layout.addWidget(self.tabs)

    def update_media(self, rom_name: str):
        """Carga y escala los medios gráficos e historia para la ROM seleccionada."""
        self._load_image(self.snap_label, "snap", rom_name)
        self._load_image(self.title_label, "titles", rom_name)
        self._load_image(self.marquee_label, "marquees", rom_name)

        # Cargar texto de Historia
        info = self.history_parser.get_info(rom_name)
        if info:
            self.history_text.setText(info)
        else:
            self.history_text.setText("Sin información histórica disponible para este juego.")

    def _load_image(self, target_label: QLabel, folder: str, rom_name: str):
        """Busca y carga la imagen correspondiente en el QLabel objetivo."""
        dir_path = PathHelper.get_dir(folder)

        # Convención MAME: snap/<rom>/0000.png (subcarpeta por rom, no archivo plano)
        img_path = dir_path / rom_name / "0000.png"
        if not img_path.exists():
            img_path = dir_path / f"{rom_name}.png"
        if not img_path.exists():
            img_path = dir_path / f"{rom_name}.jpg"

        if img_path.exists():
            pixmap = QPixmap(str(img_path))
            scaled = pixmap.scaled(
                target_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            target_label.setPixmap(scaled)
        else:
            target_label.setText(f"Sin {folder[:-1]} disponible")
