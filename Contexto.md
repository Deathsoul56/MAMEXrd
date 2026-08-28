# Blueprint del Proyecto: MAMEXrd S E X Edition (PyQt6 Frontend)

## 1. Visión General del Proyecto
Crear un *frontend* moderno, ligero, descarado y altamente portable para **MAME**, escrito en **Python** con **PyQt6**. El nombre oficial es **MAMEP S E X Edition** (una evolución espiritual y humorística del clásico MAMEPGUI). El objetivo es mantener la filosofía de un archivo ejecutable portable (`.exe`) que se ubica en la raíz de MAME, hereda su estructura y ofrece una interfaz rápida y personalizable.

## 2. Requisitos Técnicos y Restricciones
* **Framework GUI:** PyQt6 (nativo, alto rendimiento, bajo consumo de memoria, sin tecnologías web).
* **Lenguaje:** Python 3.x.
* **Portabilidad:** Se ejecuta directamente desde el directorio raíz de MAME (`MAMEXrd.exe`), detectando rutas de forma relativa mediante `os.getcwd()` o `pathlib.Path`.
* **Base de datos local:** SQLite (`mame_cache.db`) para almacenar metadatos de los juegos, índices y acelerar el arranque.
* **Comunicación Backend:** `QProcess` o `subprocess` para invocar `mame.exe` heredando el entorno de trabajo.

## 3. Estructura de Directorios Real (MAME 0.289)
```text
raiz_mame/
├── mame.exe               (Ejecutable principal de MAME)
├── MAMEXrd.exe            (Este proyecto compilado / ejecutable del frontend)
├── mame_cache.db          (Base de datos/Caché local autogenerada)
├── chdman.exe, romcmp.exe (Herramientas auxiliares de MAME)
├── artwork/               (Layouts de pantalla y artwork)
├── bgfx/                  (Shaders BGFX)
├── ctrlr/                 (Perfiles de mandos y controladores)
├── docs/                  (Documentación oficial MAME)
├── hash/                  (XML de Software Lists / Hash)
├── hlsl/                  (Shaders Direct3D HLSL)
├── ini/                   (Archivos de configuración .ini)
├── language/              (Traducciones oficiales MAME)
├── plugins/               (Plugins Lua de MAME)
├── roms/                  (Directorio de ROMs y juegos)
├── samples/               (Efectos de sonido y samples de audio)
└── Directores dinámicos (generados por MAME / Frontend):
    ├── snap/              (Capturas de pantalla / Snaps)
    ├── sta/               (Estados guardados / Savestates)
    ├── nvram/             (Datos de memoria no volátil)
    ├── cfg/               (Configuraciones específicas de juegos)
    ├── diff/              (Diferenciales de discos duros / CHD)
    ├── comments/          (Notas y comentarios)
    └── inp/               (Grabaciones de partidas / Replays)
```


## 4. Referencias Visuales Legacy y Objetivo del MVP
El objetivo primario es **replicar con fidelidad la experiencia del emulador M+GUI / MAMEPGUI clásico**, apoyándonos en las imágenes de referencia provistas en `Legacy/`:

* **`Legacy/Primer Inicio.png`:** Cuadro de diálogo modal que solicita la ruta de `mame.exe` cuando la aplicación arranca por primera vez y no encuentra el ejecutable automáticamente.
* **`Legacy/Pantalla Inicio.png`:** Interfaz principal M+GUI 1.8.2 con:
  - Árbol de carpetas/categorías en el lateral izquierdo (`Folder List`).
  - Tabla central virtualizada con fondo con marca de agua MAME, iconos, ROM, título completo, año, fabricante, driver, disponibilidad y juegos padre/clon.
  - Paneles acoplables laterales derechos con pestañas verticales para Medios (`Snapshot`, `Title`, `Marquee`, `Flyer`, `Cabinet`, `Control Panel`, `PCB`) e Información (`History`, `MAMEInfo`, `DriverInfo`, `Story`, `Command`).
  - Barra de herramientas con botones de acción (Jugar, Configurar, Escanear, Alternar paneles) y campo de búsqueda.
  - Barra de estado inferior con descripción de ROM y contador total de juegos.

---

## 5. Entorno de Producción del Usuario (Solo Lectura)
* **Ruta de producción actual:** `E:\asdf\MAME 0.27\` (Strict Read-Only).