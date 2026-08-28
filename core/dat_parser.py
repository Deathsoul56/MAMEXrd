from pathlib import Path
from typing import Dict, Optional
from utils.path_helper import PathHelper

class DATParser:
    """
    Parser para archivos de información extendida (history.dat, mameinfo.dat).
    Permite obtener descripciones, curiosidades y guías de los juegos.
    """
    def __init__(self, dat_filename: str = "history.dat"):
        self.dat_path = PathHelper.get_base_dir() / dat_filename
        self.entries: Dict[str, str] = {}

    def parse(self):
        """Lee el archivo DAT e indexa las entradas por nombre de ROM."""
        if not self.dat_path.exists():
            return

        current_roms = []
        current_text = []
        in_entry = False

        try:
            with open(self.dat_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line_str = line.strip()
                    if line_str.startswith("$info="):
                        # Extraer nombres de roms: $info=garou,garouh,...
                        raw_roms = line_str.split("=", 1)[1]
                        current_roms = [r.strip().lower() for r in raw_roms.split(",") if r.strip()]
                        current_text = []
                        in_entry = True
                    elif line_str.startswith("$bio"):
                        continue
                    elif line_str.startswith("$end"):
                        if in_entry:
                            text_block = "\n".join(current_text)
                            for r in current_roms:
                                self.entries[r] = text_block
                            in_entry = False
                            current_roms = []
                            current_text = []
                    elif in_entry:
                        current_text.append(line)
        except Exception as e:
            print(f"Error parseando {self.dat_path.name}: {e}")

    def get_info(self, rom_name: str) -> Optional[str]:
        """Obtiene la información asociada a una ROM."""
        return self.entries.get(rom_name.lower())
