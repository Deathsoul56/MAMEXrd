# Changelog

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
