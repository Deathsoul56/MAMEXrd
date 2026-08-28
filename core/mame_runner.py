from PyQt6.QtCore import QObject, QProcess, pyqtSignal
from pathlib import Path
from typing import List, Optional
from utils.path_helper import PathHelper

class MAMERunner(QObject):
    """
    Gestor de ejecución asíncrona de mame.exe mediante QProcess.
    Maneja el directorio de trabajo correcto, argumentos de video de respaldo y
    captura completa de mensajes de error de MAME.
    """
    started = pyqtSignal()
    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.last_rom: str = ""
        
        # Conexión de señales
        self.process.started.connect(self._on_started)
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._on_error)

    def launch_game(self, rom_name: str, extra_args: Optional[List[str]] = None) -> bool:
        """Inicia un juego invocando mame.exe desde el directorio del ejecutable."""
        mame_exe = PathHelper.get_mame_executable()
        if not mame_exe or not mame_exe.exists():
            self.error.emit(f"No se encontró el ejecutable mame.exe.")
            return False

        self.last_rom = rom_name
        
        # Establecer el directorio de trabajo exacto donde vive mame.exe
        working_dir = mame_exe.parent
        self.process.setWorkingDirectory(str(working_dir))

        args = [rom_name]
        
        # Agregar argumentos extra opcionales
        if extra_args:
            args.extend(extra_args)

        self.process.start(str(mame_exe), args)
        return True

    def _on_started(self):
        self.started.emit()

    def _on_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        if exit_code != 0:
            stderr_bytes = self.process.readAllStandardError().data()
            stdout_bytes = self.process.readAllStandardOutput().data()
            
            err_msg = stderr_bytes.decode("utf-8", errors="ignore").strip()
            if not err_msg:
                err_msg = stdout_bytes.decode("utf-8", errors="ignore").strip()

            if not err_msg:
                err_msg = f"MAME finalizó con código de salida {exit_code}."

            self.error.emit(f"No se pudo ejecutar '{self.last_rom}':\n\n{err_msg}")
        
        self.finished.emit(exit_code)

    def _on_error(self, error_code: QProcess.ProcessError):
        self.error.emit(f"Error al iniciar el proceso MAME: {error_code}")
