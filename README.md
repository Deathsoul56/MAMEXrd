# MAMEXrd

**MAMEXrd** (MAMEP S E X Edition) es un *frontend* moderno, nativo y altamente portable para [MAME](https://www.mamedev.org/), escrito en Python 3 con PyQt6 y SQLite. Es una evolución espiritual del clásico MAMEPGUI / M+GUI: rápido, ligero, sin dependencias web, pensado para vivir junto a `mame.exe`.

![MAMEXrd Overview](screenshots/MAMEX%20Overview.png)

## Características

- **Portable de verdad:** se ejecuta desde la raíz de tu carpeta de MAME y resuelve todas las rutas (`roms/`, `snap/`, `titles/`, `ini/`, `cfg/`) de forma relativa. Nunca escribe fuera de esa carpeta.
- **Tabla de juegos virtualizada** con caché local en SQLite (`mame_cache.db`) para un arranque y scroll instantáneos, incluso con catálogos grandes.
- **Árbol de carpetas/categorías** (favoritos, fabricante, año, estado del driver, etc.) al estilo M+GUI clásico.
- **Panel de medios** con vista previa de Snapshot, Title, Marquee, Flyer, Cabinet, Control Panel y PCB.
- **Configuración global de MAME** (`mame.ini`, `ui.ini`, `plugin.ini`) desde una interfaz gráfica con pestañas por categoría.
- **Configuración por juego**, con overrides individuales guardados en `ini/<rom>.ini` que respetan la prioridad de configuración nativa de MAME.
- **Escaneo de ROMs en segundo plano** (`QThread`/`QProcess`) para no bloquear la interfaz.
- **Interfaz 100% nativa** (PyQt6), sin Electron ni tecnologías web.

## Capturas de pantalla

| Vista general | Configuración global | Configuración por juego |
|---|---|---|
| ![Overview](screenshots/MAMEX%20Overview.png) | ![Core Settings](screenshots/MAMEX%20Core%20Settings.png) | ![Game Settings](screenshots/MAMEX%20Game%20Settings.png) |

## Requisitos

- Python 3.10+
- Una instalación de MAME (`mame.exe`) en la misma carpeta desde donde se ejecuta MAMEXrd

## Instalación

```powershell
git clone https://github.com/Deathsoul56/MAMEXrd.git
cd MAMEXrd
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Uso

Copia (o compila) MAMEXrd en la raíz de tu carpeta de MAME, junto a `mame.exe`, y ejecútalo:

```powershell
python main.py
```

En el primer arranque, si no se detecta `mame.exe` automáticamente, se pedirá su ubicación mediante un diálogo de configuración inicial.

![Primer inicio](screenshots/MAMEX%20Primer%20Inicio.png)

## Estructura del proyecto

```text
MAMEXrd/
├── main.py                # Punto de entrada
├── core/                  # Lógica de negocio: escaneo de ROMs, parsers, gestores de .ini
├── database/              # Persistencia SQLite (mame_cache.db)
├── ui/                     # Interfaz PyQt6 (ventana principal, tabla, diálogos, paneles)
├── utils/                 # Utilidades (rutas relativas, configuración, i18n)
├── scripts/                # Scripts auxiliares (importar favoritos, enriquecer metadatos)
└── docs/                  # Documentación técnica y de arquitectura
```

Más detalles de arquitectura en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) y del alcance del MVP en [docs/MVP_SPECIFICATION.md](docs/MVP_SPECIFICATION.md).

## Licencia

Distribuido bajo licencia MIT. Ver [LICENSE](LICENSE) para más información.
