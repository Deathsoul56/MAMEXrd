import sys
import os
from pathlib import Path
from typing import Optional

class PathHelper:
    """
    Gestor de rutas relativas y resolución de MAME para garantizar portabilidad.
    """
    @staticmethod
    def get_base_dir() -> Path:
        """Retorna el directorio base del ejecutable o script."""
        main_module = sys.modules.get("__main__")
        if hasattr(main_module, "__compiled__"):
            # Nuitka --onefile se auto-extrae y reejecuta desde una carpeta temporal,
            # por lo que sys.executable no sirve aquí: usar el argv0 original del .exe.
            original_argv0 = getattr(main_module.__compiled__, "original_argv0", None)
            if original_argv0:
                return Path(original_argv0).resolve().parent
            return Path(sys.executable).resolve().parent
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        return Path(os.getcwd())

    @classmethod
    def get_mame_executable(cls) -> Optional[Path]:
        """
        Busca y devuelve la ruta al ejecutable mame.exe.
        1. Comprueba mamexrd.ini
        2. Comprueba ./mame.exe
        3. Comprueba carpetas de pruebas locales (MAME 0.289, MAME 0.289+GUI)
        """
        # 1. Importación diferida para evitar ciclos
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        saved_path = config.get_mame_path()
        if saved_path and saved_path.exists():
            return saved_path

        base = cls.get_base_dir()
        
        # 2. Raíz estándar
        root_mame = base / "mame.exe"
        if root_mame.exists():
            return root_mame

        # 3. Directorios locales de desarrollo
        dev_mame = base / "MAME 0.289" / "mame.exe"
        if dev_mame.exists():
            return dev_mame

        dev_mame_gui = base / "MAME 0.289+GUI" / "mame.exe"
        if dev_mame_gui.exists():
            return dev_mame_gui

        return None

    @classmethod
    def get_dir(cls, folder_name: str) -> Path:
        """Devuelve la ruta a un subdirectorio específico (roms, snap, titles, etc.)."""
        # Si mame.exe está en una subcarpeta (ej. MAME 0.289), usar el directorio del ejecutable
        mame_exe = cls.get_mame_executable()
        if mame_exe and mame_exe.exists():
            mame_root = mame_exe.parent
            target = mame_root / folder_name
            if target.exists():
                return target

        return cls.get_base_dir() / folder_name

    @classmethod
    def ensure_dir(cls, folder_name: str) -> Path:
        """Garantiza la existencia de una carpeta local creando si no existe."""
        target = cls.get_dir(folder_name)
        target.mkdir(parents=True, exist_ok=True)
        return target

    @classmethod
    def get_db_path(cls) -> Path:
        """Devuelve la ruta a la base de datos de caché local."""
        return cls.get_base_dir() / "mame_cache.db"
