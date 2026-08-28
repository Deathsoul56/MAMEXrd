# Guía para Agentes AI: MAMEXrd (MAMEP S E X Edition)

Bienvenido a **MAMEXrd**. Este proyecto es un *frontend* moderno, nativo, ligero y altamente portable para MAME, desarrollado en Python 3 con PyQt6 y SQLite.

## 1. Principios Sagrados del Proyecto

1. **Portabilidad Relativa Estricta:**
   - MAMEXrd se ejecuta en la raíz de MAME (`mame.exe`).
   - NUNCA codificar rutas absolutas (como `C:\MAME\` o `E:\asdf\`).
   - Usar SIEMPRE `utils/path_helper.py` o `pathlib.Path.cwd()` para la localización de archivos y carpetas (`roms/`, `snap/`, `titles/`, `ini/`, etc.).

2. **REGLA DE ORO DE PRODUCCIÓN (READ-ONLY EN ENTORNO EXTERNO):**
   - El directorio `E:\asdf\MAME 0.27\` es el entorno de **producción del usuario**.
   - **SOLO LECTURA:** Ningún agente ni proceso automático puede crear, modificar ni borrar nada en esa ruta.
   - Cualquier archivo generado (caché, logs, BD) debe crearse exclusivamente en el directorio de trabajo local de MAMEXrd.

3. **Fluidez de UI No Bloqueante (60 FPS):**
   - NUNCA realizar operaciones de I/O pesadas (escaneo de ROMs, parseo de XML/DATs grandes, lecturas intensivas de disco) en el hilo principal de la interfaz (`GUI Thread`).
   - Usar siempre `QThread`, `QThreadPool` o `QProcess` para mantener la interfaz 100% responsiva.
   - Usar `QAbstractTableModel` y `QTableView` para renderizado virtualizado de la lista de juegos.

4. **Robustez e Integridad del Stack:**
   - GUI: **PyQt6** (Evitar tecnologías web/Electron).
   - DB: **SQLite3** (`mame_cache.db`).
   - Invocación Backend: **`QProcess`**.

---

## 2. Estructura de Directorios del Código Fuente

```text
MAMEXrd/
├── main.py                    # Punto de entrada principal
├── requirements.txt           # Dependencias de Python
├── AGENTS.md                  # Reglas e instrucciones para Agentes AI
├── Contexto.md                # Blueprint y contexto del proyecto
├── docs/                      # Arquitectura y documentación técnica
├── core/                      # Lógica de negocio y backend
│   ├── __init__.py
│   ├── mame_runner.py         # Manejador de QProcess para mame.exe
│   ├── rom_scanner.py         # Escaneo y verificación de ROMs en segundo plano
│   └── dat_parser.py          # Parser de history.dat y mameinfo.dat
├── database/                  # Persistencia SQLite
│   ├── __init__.py
│   └── db_manager.py          # Gestor de base de datos mame_cache.db
├── ui/                        # Componentes de la interfaz PyQt6
│   ├── __init__.py
│   ├── main_window.py         # Ventana principal
│   ├── game_table.py          # Tabla virtualizada de juegos
│   ├── media_panel.py         # Panel de vista previa (Snap, Marquee, Title)
│   └── styles.py              # Hoja de estilos (Dark Mode Moderno)
└── utils/                     # Utilidades generales
    ├── __init__.py
    └── path_helper.py         # Resolución de rutas relativas de MAME
```

---

## 3. Normas de Estilo y Código

* **Python 3.10+**: Usar `type hints` explícitos en funciones y métodos.
* **Separación de Capas**: La interfaz de usuario (`ui/`) no debe ejecutar consultas SQL directas ni invocar subprocessos; debe comunicarse a través del controlador/gestor (`core/` y `database/`).
* **Manejo de Excepciones**: Capturar errores con try-except explícitos y loguear mensajes comprensibles sin crash de la app.
