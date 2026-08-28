import os
from pathlib import Path
from database.db_manager import DatabaseManager

def fix_and_reimport():
    prod_fav_path = Path(r"E:\asdf\MAME 0.27\folders\Favorites.ini")
    if not prod_fav_path.exists():
        print(f"No se encontró {prod_fav_path}")
        return

    # Leer archivo con autodetección de codificación UTF-16 / UTF-8 y desinfección de null bytes
    raw_content = prod_fav_path.read_bytes()
    if raw_content.startswith(b'\xff\xfe') or raw_content.startswith(b'\xfe\xff'):
        text = raw_content.decode("utf-16", errors="ignore")
    else:
        text = raw_content.replace(b'\x00', b'').decode("utf-8", errors="ignore")
    
    text_clean = text.replace('\x00', '')

    roms_to_import = []
    in_root_folder = False

    for line in text_clean.splitlines():
        line_str = line.strip()
        if line_str == "[ROOT_FOLDER]":
            in_root_folder = True
            continue
        if in_root_folder and line_str and not line_str.startswith("["):
            clean_rom = line_str.replace('\x00', '').strip().lower()
            if clean_rom:
                roms_to_import.append(clean_rom)

    print(f"Encontrados {len(roms_to_import)} juegos limpios en Favorites.ini de producción.")

    db = DatabaseManager()
    
    # Recrear tabla de juegos limpia
    with db.get_connection() as conn:
        conn.execute("DELETE FROM games;")
        for rom in roms_to_import:
            title_display = rom.upper().replace("_", " ")
            conn.execute("""
                INSERT INTO games (rom_name, title, year, manufacturer, is_favorite, has_rom)
                VALUES (?, ?, ?, ?, 1, 1)
                ON CONFLICT(rom_name) DO UPDATE SET is_favorite = 1, has_rom = 1;
            """, (rom, title_display, "Arcade", "Desconocido"))
        conn.commit()

    print("¡Base de datos limpiada y re-importada con éxito!")

if __name__ == "__main__":
    fix_and_reimport()
