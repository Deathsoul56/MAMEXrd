import sys
import traceback
import tempfile
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.app_icon import get_app_icon

def _log_crash(exc_type, exc_value, exc_tb):
    log_path = Path(tempfile.gettempdir()) / "mamexrd_crash.log"
    with open(log_path, "w", encoding="utf-8") as f:
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)

sys.excepthook = _log_crash

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MAMEXrd")
    app.setWindowIcon(get_app_icon())

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
