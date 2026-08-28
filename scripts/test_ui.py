import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def test_ui_instantiation():
    app = QApplication(sys.argv)
    window = MainWindow()
    assert window.windowTitle().startswith("MAMEXrd")
    assert window.table_model.rowCount() > 0
    print(f"UI instanciada con éxito. Juegos cargados en la tabla: {window.table_model.rowCount()}")
    app.quit()

if __name__ == "__main__":
    test_ui_instantiation()
