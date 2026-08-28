from PyQt6.QtWidgets import (
    QDockWidget, QTabWidget, QLabel, QTextEdit, QVBoxLayout, QWidget
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize
from utils.path_helper import PathHelper
from core.dat_parser import DATParser

class ScalableImageLabel(QLabel):
    """
    QLabel personalizado que reescala automáticamente la imagen al cambiar el tamaño del panel.
    """
    def __init__(self, folder_name: str, parent=None):
        super().__init__(parent)
        self.folder_name = folder_name
        self.current_rom: str = ""
        self.original_pixmap: Optional[QPixmap] = None
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(220, 160)
        self.setText(f"Sin {folder_name}")

    def load_rom_image(self, rom_name: str):
        self.current_rom = rom_name
        dir_path = PathHelper.get_dir(self.folder_name)
        img_path = dir_path / f"{rom_name}.png"
        if not img_path.exists():
            img_path = dir_path / f"{rom_name}.jpg"
        if not img_path.exists():
            img_path = dir_path / f"{rom_name}.ico"

        if img_path.exists():
            self.original_pixmap = QPixmap(str(img_path))
            self._update_scaled_pixmap()
        else:
            self.original_pixmap = None
            self.setText(f"Sin {self.folder_name[:-1] if self.folder_name.endswith('s') else self.folder_name}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_scaled_pixmap()

    def _update_scaled_pixmap(self):
        if self.original_pixmap and not self.original_pixmap.isNull():
            scaled = self.original_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled)


class MediaDockWidget(QDockWidget):
    """
    Panel acoplable superior derecho para Medios y Artes Gráficas (Réplica Legacy).
    Pestañas verticales a la derecha: Title, Snapshot, Marquee, Flyer, Cabinet, Control Panel, PCB.
    """
    def __init__(self, parent=None):
        super().__init__("Title / Media", parent)
        self.setObjectName("MediaDockWidget")
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)

        self._init_ui()

    def _init_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.East)

        self.title_label = ScalableImageLabel("titles")
        self.snap_label = ScalableImageLabel("snap")
        self.marquee_label = ScalableImageLabel("marquees")
        self.flyer_label = ScalableImageLabel("flyers")
        self.cabinet_label = ScalableImageLabel("cabinets")
        self.cpanel_label = ScalableImageLabel("cpanel")
        self.pcb_label = ScalableImageLabel("pcb")

        self.tabs.addTab(self.title_label, "Title")
        self.tabs.addTab(self.snap_label, "Snapshot")
        self.tabs.addTab(self.marquee_label, "Marquee")
        self.tabs.addTab(self.flyer_label, "Flyer")
        self.tabs.addTab(self.cabinet_label, "Cabinet")
        self.tabs.addTab(self.cpanel_label, "Control Panel")
        self.tabs.addTab(self.pcb_label, "PCB")

        layout.addWidget(self.tabs)
        self.setWidget(container)

    def update_media(self, rom_name: str):
        """Carga y muestra los medios gráficos para la ROM seleccionada."""
        self.title_label.load_rom_image(rom_name)
        self.snap_label.load_rom_image(rom_name)
        self.marquee_label.load_rom_image(rom_name)
        self.flyer_label.load_rom_image(rom_name)
        self.cabinet_label.load_rom_image(rom_name)
        self.cpanel_label.load_rom_image(rom_name)
        self.pcb_label.load_rom_image(rom_name)


class InfoDockWidget(QDockWidget):
    """
    Panel acoplable inferior derecho para información extendida (DATs) (Réplica Legacy).
    Pestañas verticales a la derecha: History, MAMEInfo, DriverInfo, Story, Command.
    """
    def __init__(self, parent=None):
        super().__init__("History / Info", parent)
        self.setObjectName("InfoDockWidget")
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea | Qt.DockWidgetArea.LeftDockWidgetArea)

        self.history_parser = DATParser("history.dat")
        self.history_parser.parse()

        self.mameinfo_parser = DATParser("mameinfo.dat")
        self.mameinfo_parser.parse()

        self._init_ui()

    def _init_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.East)

        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)

        self.mameinfo_text = QTextEdit()
        self.mameinfo_text.setReadOnly(True)

        self.driver_text = QTextEdit()
        self.driver_text.setReadOnly(True)

        self.tabs.addTab(self.history_text, "History")
        self.tabs.addTab(self.mameinfo_text, "MAMEInfo")
        self.tabs.addTab(self.driver_text, "DriverInfo")

        layout.addWidget(self.tabs)
        self.setWidget(container)

    def update_info(self, rom_name: str, driver_info: str = ""):
        hist = self.history_parser.get_info(rom_name)
        self.history_text.setText(hist if hist else "Sin información disponible en history.dat.")

        minfo = self.mameinfo_parser.get_info(rom_name)
        self.mameinfo_text.setText(minfo if minfo else "Sin información disponible en mameinfo.dat.")

        self.driver_text.setText(f"Driver MAME: {driver_info}\nEstado del sistema: Emulación soportada (Good).")
