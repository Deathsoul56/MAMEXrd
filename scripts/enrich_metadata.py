from database.db_manager import DatabaseManager
from core.mame_parser import MAMEInfoParser

def enrich_games():
    """
    Extrae y enriquece los metadatos reales de MAME (Títulos oficiales, Año, Desarrollador, Clones)
    para todos los juegos registrados en la base de datos local.
    """
    db = DatabaseManager()
    games = db.get_all_games()
    
    if not games:
        print("No hay juegos en la base de datos para enriquecer.")
        return

    rom_names = [g["rom_name"] for g in games]
    print(f"Iniciando enriquecimiento de metadatos para {len(rom_names)} juegos...")

    parser = MAMEInfoParser(db_manager=db)

    # 1. Actualización ultrarrápida de títulos oficiales con -listfull
    print("Obteniendo títulos oficiales con mame.exe -listfull...")
    count_full = parser.update_titles_from_listfull(rom_names)

    # 2. Extracción profunda de XML (Año, Fabricante, Driver, CloneOf)
    print("Obteniendo metadatos detallados con mame.exe -listxml...")
    count_xml = parser.update_metadata_from_listxml(rom_names)

    print(f"¡Enriquecimiento completado! Se actualizaron títulos para {count_full} juegos y XML para {count_xml} juegos.")

if __name__ == "__main__":
    enrich_games()
