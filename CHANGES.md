# Changelog

## v0.2 (2026-09-26)

- Detección automática de `mame.exe` mejorada, con opción de reconfigurar la ruta manualmente.
- Limpieza automática de entradas obsoletas en la base de datos al re-escanear (juegos/carpetas que ya no reporta el core de MAME).
- Lanzar el juego seleccionado con Enter desde la tabla.
- Buscar al presionar Enter en la barra de búsqueda.
- El panel Title/Media recuerda la última pestaña activa entre sesiones.

## v0.1 (2026-08-31)

Primer release de MAMEXrd.

- Tabla de juegos virtualizada con caché local en SQLite (`mame_cache.db`).
- Árbol de carpetas/categorías (favoritos, fabricante, año, estado del driver).
- Panel de medios con vista previa de Snapshot, Title, Marquee, Flyer, Cabinet, Control Panel y PCB.
- Configuración global de MAME (`mame.ini`, `ui.ini`, `plugin.ini`) desde una interfaz con pestañas.
- Configuración por juego con overrides individuales en `ini/<rom>.ini`.
- Escaneo de ROMs en segundo plano sin bloquear la interfaz.
- Diálogo de primer arranque para localizar `mame.exe` cuando no se detecta automáticamente.
- Diálogo "Acerca de" e interfaz completamente en inglés.
- Icono de la aplicación embebido en el ejecutable, independiente de archivos externos.
