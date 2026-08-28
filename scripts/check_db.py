from database.db_manager import DatabaseManager

def main():
    db = DatabaseManager()
    games = db.get_all_games()
    print(f"Total juegos enriquecidos: {len(games)}\n")
    print(f"{'ROM':<12} | {'AÑO':<6} | {'FABRICANTE':<22} | TÍTULO OFICIAL")
    print("=" * 85)

    for g in games[:15]:
        rom = g.get('rom_name', '')
        year = g.get('year', '')
        manuf = (g.get('manufacturer', '') or '')[:22]
        title = g.get('title', '')
        print(f"{rom:<12} | {year:<6} | {manuf:<22} | {title}")

if __name__ == "__main__":
    main()
