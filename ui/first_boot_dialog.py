from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from pathlib import Path
from utils.config_manager import ConfigManager
from utils.path_helper import PathHelper

class FirstBootDialog(QDialog):
    """
    Diálogo modal de primer inicio (réplica de Legacy/Primer Inicio.png)
    para la selección de la ruta de mame.exe cuando no se detecta automáticamente.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MAME/MESS executable:")
        self.resize(550, 160)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.selected_path: str = ""
        self.config_manager = ConfigManager()

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        label = QLabel("Select the location of the mame.exe executable to continue:")
        label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(label)

        # File selection row
        file_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Example: C:/MAME/mame.exe")

        # Auto-suggest if a mame.exe is detected in the current folder or known subfolders
        suggested = PathHelper.get_mame_executable()
        if suggested and suggested.exists():
            self.path_input.setText(str(suggested))

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._on_browse)

        file_layout.addWidget(self.path_input, stretch=3)
        file_layout.addWidget(self.browse_btn, stretch=1)
        layout.addLayout(file_layout)

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setDefault(True)
        self.ok_btn.clicked.connect(self._on_accept)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def _on_browse(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select MAME executable",
            str(PathHelper.get_base_dir()),
            "MAME executables (mame.exe mame*.exe);;All files (*.*)"
        )
        if file_path:
            self.path_input.setText(file_path)

    def _on_accept(self):
        path_str = self.path_input.text().strip()
        if not path_str:
            QMessageBox.warning(self, "Path Required", "You must select a MAME executable.")
            return

        p = Path(path_str)
        if not p.exists() or not p.is_file():
            QMessageBox.critical(self, "File Not Found", f"Could not find the executable at:\n{path_str}")
            return

        # Guardar en configuración
        self.config_manager.set_mame_path(p)
        self.selected_path = str(p)
        self.accept()
