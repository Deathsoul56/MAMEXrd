from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QSizePolicy
)
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtCore import Qt, QPoint
from utils.app_icon import get_app_icon

MAMEXRD_VERSION = "v0.1"


class AboutDialog(QDialog):
    """Diálogo 'Acerca de' con barra de título personalizada, réplica del estilo usado en snes9xrd."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setFixedSize(500, 480)
        self._drag_pos = QPoint()

        self.setStyleSheet("""
            QDialog { background-color: #1a1d29; border: 1px solid #333852; border-radius: 10px; }
            QLabel { color: #e1e4ed; }
            QLabel a { color: #8b8ff8; }
            QPushButton {
                background-color: #6366f1;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 22px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #7577f5; }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_title_bar())
        root.addWidget(self._build_body(), stretch=1)

    def _build_title_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(40)
        bar.setStyleSheet("background-color: #6366f1; border-top-left-radius: 10px; border-top-right-radius: 10px;")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 0, 8, 0)

        title = QLabel(f"About MAMEXrd")
        title.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 10.5pt; background: transparent;")
        layout.addWidget(title)
        layout.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton { background-color: transparent; border: none; color: #ffffff; font-weight: bold; border-radius: 4px; }
            QPushButton:hover { background-color: #e5484d; }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        bar.mousePressEvent = self._title_bar_mouse_press
        bar.mouseMoveEvent = self._title_bar_mouse_move
        return bar

    def _title_bar_mouse_press(self, event: QMouseEvent):
        self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def _title_bar_mouse_move(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def _build_body(self) -> QWidget:
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(10)

        header = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(get_app_icon().pixmap(48, 48))
        header.addWidget(icon_label)

        header_text = QLabel(f"<b>MAMEXrd {MAMEXRD_VERSION}</b> for Windows.")
        header_text.setStyleSheet("font-size: 11pt;")
        header.addWidget(header_text)
        header.addStretch()
        layout.addLayout(header)

        info = QLabel(
            f"(c) Copyright 2026 - 2026 DeAtSoUl56<br><br>"
            "MAMEXrd is a modern, lightweight and portable native frontend for MAME "
            "(Multiple Arcade Machine Emulator), built with Python 3 and PyQt6.<br><br>"
            "Please visit <a href=\"https://www.mamedev.org\">https://www.mamedev.org</a> for "
            "up-to-the-minute information and help on MAME.<br><br>"
            "Visit the MAMEXrd GitHub at<br>"
            "<a href=\"https://github.com/Deathsoul56/MAMEXrd/tree/main\">"
            "https://github.com/Deathsoul56/MAMEXrd/tree/main</a><br><br>"
            "This is MAMEXrd <s>sex edition</s>."
        )
        info.setWordWrap(True)
        info.setTextFormat(Qt.TextFormat.RichText)
        info.setOpenExternalLinks(True)
        info.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout.addWidget(info, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

        return body
