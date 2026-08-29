import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from utils.path_helper import PathHelper

class DatabaseManager:
    """
    Gestor de base de datos SQLite (mame_cache.db) para almacenamiento de metadatos,
    caché de ROMs, favoritos, listas personalizadas y estadísticas de juego.
    """
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or PathHelper.get_db_path()
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Abre y devuelve una conexión a SQLite con soporte de diccionarios."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Crea las tablas e índices necesarios si no existen."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla principal de juegos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    rom_name TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    year TEXT,
                    manufacturer TEXT,
                    genre TEXT,
                    driver_status TEXT,
                    driver TEXT,
                    is_clone BOOLEAN DEFAULT 0,
                    parent_rom TEXT,
                    has_rom BOOLEAN DEFAULT 0,
                    is_favorite BOOLEAN DEFAULT 0,
                    play_count INTEGER DEFAULT 0,
                    last_played DATETIME
                );
            """)

            # Índices de optimización de búsquedas
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_has_rom ON games(has_rom);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_favorite ON games(is_favorite);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_title ON games(title);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_manufacturer ON games(manufacturer);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_games_year ON games(year);")

            # Tabla de listas / carpetas personalizadas (compatibilidad con Favorites.ini)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS custom_folders (
                    folder_name TEXT NOT NULL,
                    rom_name TEXT NOT NULL,
                    PRIMARY KEY (folder_name, rom_name),
                    FOREIGN KEY (rom_name) REFERENCES games(rom_name) ON DELETE CASCADE
                );
            """)

            # Tabla de nombres de carpetas personalizadas (permite crear carpetas vacías)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS folders (
                    name TEXT PRIMARY KEY
                );
            """)

            conn.commit()

            self._migrate_schema(conn)

    def _migrate_schema(self, conn: sqlite3.Connection):
        """Agrega columnas faltantes a bases de datos creadas con un esquema anterior."""
        expected_columns = {
            "genre": "TEXT",
            "driver_status": "TEXT",
            "driver": "TEXT",
            "is_clone": "BOOLEAN DEFAULT 0",
            "parent_rom": "TEXT",
            "has_rom": "BOOLEAN DEFAULT 0",
            "is_favorite": "BOOLEAN DEFAULT 0",
            "play_count": "INTEGER DEFAULT 0",
            "last_played": "DATETIME",
        }

        existing_columns = {row["name"] for row in conn.execute("PRAGMA table_info(games)")}

        for column, definition in expected_columns.items():
            if column not in existing_columns:
                conn.execute(f"ALTER TABLE games ADD COLUMN {column} {definition};")

        conn.commit()

    def set_favorite(self, rom_name: str, is_favorite: bool):
        """Marca o desmarca un juego como favorito en la BD y sincroniza con custom_folders."""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE games SET is_favorite = ? WHERE rom_name = ?",
                (1 if is_favorite else 0, rom_name)
            )
            if is_favorite:
                conn.execute(
                    "INSERT OR IGNORE INTO custom_folders (folder_name, rom_name) VALUES ('Favorites', ?)",
                    (rom_name,)
                )
            else:
                conn.execute(
                    "DELETE FROM custom_folders WHERE folder_name = 'Favorites' AND rom_name = ?",
                    (rom_name,)
                )
            conn.commit()
        
        self.export_favorites_ini()

    def export_favorites_ini(self):
        """Exporta la lista de favoritos a folders/Favorites.ini local."""
        try:
            fav_dir = PathHelper.ensure_dir("folders")
            fav_ini = fav_dir / "Favorites.ini"

            fav_games = self.get_all_games(favorite_only=True)
            with open(fav_ini, "w", encoding="utf-8") as f:
                f.write("[FOLDER_SETTINGS]\nRootFolderIcon golden\nSubFolderIcon cust2\n\n[ROOT_FOLDER]\n")
                for g in fav_games:
                    f.write(f"{g['rom_name']}\n")
        except Exception as e:
            print(f"Error exportando Favorites.ini: {e}")

    def get_custom_folders(self) -> List[str]:
        """Devuelve los nombres de las carpetas personalizadas creadas por el usuario."""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT name FROM folders ORDER BY name COLLATE NOCASE").fetchall()
            return [row["name"] for row in rows]

    def create_custom_folder(self, folder_name: str) -> bool:
        """Crea una nueva carpeta personalizada (vacía) si no existe ya."""
        folder_name = folder_name.strip()
        if not folder_name:
            return False
        with self.get_connection() as conn:
            conn.execute("INSERT OR IGNORE INTO folders (name) VALUES (?)", (folder_name,))
            conn.commit()
        return True

    def add_rom_to_folder(self, folder_name: str, rom_name: str):
        """Agrega un rom a una carpeta personalizada (la crea si aún no existe)."""
        with self.get_connection() as conn:
            conn.execute("INSERT OR IGNORE INTO folders (name) VALUES (?)", (folder_name,))
            conn.execute(
                "INSERT OR IGNORE INTO custom_folders (folder_name, rom_name) VALUES (?, ?)",
                (folder_name, rom_name)
            )
            conn.commit()

    def get_roms_in_folder(self, folder_name: str) -> List[str]:
        """Devuelve los rom_name que pertenecen a una carpeta personalizada."""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT rom_name FROM custom_folders WHERE folder_name = ?", (folder_name,)
            ).fetchall()
            return [row["rom_name"] for row in rows]

    def increment_play_count(self, rom_name: str):
        """Incrementa el contador de ejecuciones y registra la última fecha de partida."""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE games 
                SET play_count = play_count + 1, last_played = CURRENT_TIMESTAMP 
                WHERE rom_name = ?
            """, (rom_name,))
            conn.commit()

    def get_all_games(self, filter_roms_exist: bool = False, favorite_only: bool = False) -> List[Dict[str, Any]]:
        """Obtiene la lista de juegos filtrada."""
        query = "SELECT * FROM games WHERE 1=1"
        params = []

        if filter_roms_exist:
            query += " AND has_rom = 1"
        if favorite_only:
            query += " AND is_favorite = 1"

        query += " ORDER BY title ASC"

        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_manufacturers(self) -> List[str]:
        """Obtiene la lista de fabricantes únicos con más de 1 juego."""
        query = """
            SELECT manufacturer, COUNT(*) as cnt 
            FROM games 
            WHERE manufacturer IS NOT NULL AND manufacturer != '' AND manufacturer != 'Desconocido'
            GROUP BY manufacturer 
            HAVING cnt >= 1 
            ORDER BY manufacturer ASC
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query)
            return [row["manufacturer"] for row in cursor.fetchall()]

    def get_years(self) -> List[str]:
        """Obtiene la lista de años de lanzamiento únicos."""
        query = """
            SELECT DISTINCT year 
            FROM games 
            WHERE year IS NOT NULL AND year != '' AND year != 'Desconocido'
            ORDER BY year DESC
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query)
            return [row["year"] for row in cursor.fetchall()]
