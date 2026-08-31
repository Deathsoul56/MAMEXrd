from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QWidget


class SpinnerWidget(QWidget):
    """Spinner circular dibujado a mano (sin GIF/recursos externos) para indicar actividad en curso."""

    def __init__(self, parent=None, size: int = 36):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.start(60)

    def _rotate(self):
        self._angle = (self._angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(3, 3, -3, -3)

        dots = 8
        for i in range(dots):
            fade = ((i * 30 + self._angle) % 360) / 360
            opacity = 1.0 - fade
            color = QColor("#6366f1")
            color.setAlphaF(max(0.15, opacity))
            pen = QPen(color)
            pen.setWidth(3)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawArc(rect, (i * 360 // dots) * 16, 28 * 16)


class LoadingDialog(QDialog):
    """
    Diálogo modal no bloqueante (usa show(), no exec()) para mostrar progreso
    durante operaciones largas en segundo plano (ej. importar el romset completo
    con -listxml), evitando la sensación de que la app se congeló.
    """

    def __init__(self, parent=None, message: str = "Cargando..."):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setFixedSize(360, 130)
        self.setStyleSheet("""
            QDialog { background-color: #1a1d29; border: 1px solid #333852; border-radius: 10px; }
            QLabel { color: #e1e4ed; font-size: 10pt; }
            QProgressBar {
                background-color: #202436;
                border: 1px solid #333852;
                border-radius: 6px;
                height: 8px;
            }
            QProgressBar::chunk { background-color: #6366f1; border-radius: 6px; }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        self.spinner = SpinnerWidget(self)
        layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)

        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminado: no conocemos el % real de -listxml
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

    def set_message(self, text: str):
        self.message_label.setText(text)
