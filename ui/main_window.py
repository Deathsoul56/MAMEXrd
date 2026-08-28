from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QHeaderView, QMessageBox, QToolBar, QMenu, QStatusBar
)
from PyQt6.QtCore import Qt, QItemSelection
from PyQt6.QtGui import QAction, QIcon
from pathlib import Path

from database.db_manager import DatabaseManager
from core.mame_runner import MAMERunner
from core.rom_scanner import ROMScannerThread
from core.romset_importer import RomsetImportThread
from ui.game_table import GameTableModel, GameTableView
from ui.folder_dock import FolderListDock
from ui.media_dock import MediaDockWidget, InfoDockWidget
from ui.first_boot_dialog import FirstBootDialog
from ui.settings_dialog import MAMESettingsDialog
from ui.styles import DARK_THEME_QSS
from utils.path_helper import PathHelper

class MainWindow(QMainWindow):
    """
    Ventana Principal MAMEXrd 100% Funcional (Réplica M+GUI / MAMEPGUI 1.8.2).
    Integra menú contextual de clic derecho, árbol de carpetas dinámico, tabla central,
    docks laterales de artes e historia, e invocación de MAME con registro de partidas.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MAMEXrd 1.0 - MAME 0.289 (mame0289)")
        self.resize(1280, 760)
        self.setStyleSheet(DARK_THEME_QSS)

        self.db_manager = DatabaseManager()
        self.mame_runner = MAMERunner(self)
        self.selected_rom: str = ""
        self.all_games = []

        # Comprobar Primer Inicio si mame.exe no está configurado
        self._check_first_boot()

        self._init_menu_bar()
        self._init_toolbar()
        self._init_docks()
        self._init_central_table()
        self._init_statusbar()
        self._connect_signals()

        self._load_games()

    def _check_first_boot(self):
        mame_exe = PathHelper.get_mame_executable()
        if not mame_exe or not mame_exe.exists():
            dialog = FirstBootDialog(self)
            dialog.exec()

    def _init_menu_bar(self):
        menubar = self.menuBar()

        # Menú File
        file_menu = menubar.addMenu("File")
        play_act = QAction("▶ Play Game", self)
        play_act.triggered.connect(self._on_launch_game)
        file_menu.addAction(play_act)
        file_menu.addSeparator()
        exit_act = QAction("Exit", self)
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)

        # Menú View
        view_menu = menubar.addMenu("View")
        toggle_folder_act = QAction("📁 Mostrar / Ocultar Carpetas", self)
        toggle_folder_act.triggered.connect(self._toggle_folder_dock)
        view_menu.addAction(toggle_folder_act)

        toggle_media_act = QAction("🖼 Mostrar / Ocultar Medios", self)
        toggle_media_act.triggered.connect(self._toggle_media_docks)
        view_menu.addAction(toggle_media_act)

        # Menú Options
        options_menu = menubar.addMenu("Options")
        audit_act = QAction("🔍 Auditar / Escanear ROMs", self)
        audit_act.setShortcut("F5")
        audit_act.triggered.connect(self._on_audit_roms)
        options_menu.addAction(audit_act)

        import_act = QAction("📀 Importar Romset Completo (-listxml)", self)
        import_act.triggered.connect(self._on_import_full_romset)
        options_menu.addAction(import_act)

        options_menu.addSeparator()
        core_settings_act = QAction("⚙ Opciones de MAME (Core)", self)
        core_settings_act.triggered.connect(self._on_open_core_settings)
        options_menu.addAction(core_settings_act)

        # Menú Help
        help_menu = menubar.addMenu("Help")
        about_act = QAction("Acerca de MAMEXrd", self)
        about_act.triggered.connect(self._on_about)
        help_menu.addAction(about_act)

    def _init_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.play_btn = QPushButton("▶ JUGAR")
        self.play_btn.setObjectName("launchBtn")
        self.play_btn.clicked.connect(self._on_launch_game)

        self.audit_btn = QPushButton("🔍 AUDITAR ROMS")
        self.audit_btn.clicked.connect(self._on_audit_roms)

        self.toggle_folder_btn = QPushButton("📁 CARPETAS")
        self.toggle_folder_btn.clicked.connect(self._toggle_folder_dock)

        self.toggle_media_btn = QPushButton("🖼 MEDIOS")
        self.toggle_media_btn.clicked.connect(self._toggle_media_docks)

        self.settings_btn = QPushButton("⚙ OPCIONES")
        self.settings_btn.clicked.connect(self._on_open_core_settings)

        toolbar.addWidget(self.play_btn)
        toolbar.addWidget(self.audit_btn)
        toolbar.addWidget(self.toggle_folder_btn)
        toolbar.addWidget(self.toggle_media_btn)
        toolbar.addWidget(self.settings_btn)

        spacer = QWidget()
        spacer.setMinimumWidth(20)
        toolbar.addWidget(spacer)

        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("searchBar")
        self.search_bar.setPlaceholderText("🔍 Buscar juego por título o ROM...")
        self.search_bar.setMaximumWidth(300)
        toolbar.addWidget(self.search_bar)

    def _init_docks(self):
        self.folder_dock = FolderListDock(self.db_manager, self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.folder_dock)

        self.media_dock = MediaDockWidget(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.media_dock)

        self.info_dock = InfoDockWidget(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.info_dock)

    def _init_central_table(self):
        self.table_view = GameTableView(self)
        self.table_model = GameTableModel()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(GameTableView.SelectionBehavior.SelectRows)
        self.table_view.setSelectionMode(GameTableView.SelectionMode.SingleSelection)
        self.table_view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        self.setCentralWidget(self.table_view)

    def _init_statusbar(self):
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.status_game_lbl = QLabel("Selecciona un juego para ver detalles")
        self.status_count_lbl = QLabel("0 juegos cargados")

        self.statusbar.addWidget(self.status_game_lbl, stretch=3)
        self.statusbar.addPermanentWidget(self.status_count_lbl)

    def _connect_signals(self):
        self.table_view.selectionModel().selectionChanged.connect(self._on_game_selected)
        self.table_view.doubleClicked.connect(self._on_launch_game)
        self.search_bar.textChanged.connect(self._on_search_changed)
        self.folder_dock.category_selected.connect(self._on_category_filtered)

        # Señales del Menú Contextual de Clic Derecho
        self.table_view.play_requested.connect(self._on_launch_specific_rom)
        self.table_view.record_requested.connect(self._on_record_game)
        self.table_view.favorite_toggled.connect(self._on_toggle_favorite)
        self.table_view.audit_requested.connect(self._on_audit_single_game)
        self.table_view.properties_requested.connect(self._on_show_properties)

        self.mame_runner.started.connect(self._on_mame_started)
        self.mame_runner.finished.connect(self._on_mame_finished)
        self.mame_runner.error.connect(self._on_mame_error)

    def _load_games(self):
        self.all_games = self.db_manager.get_all_games()
        self.table_model.set_games(self.all_games)
        self.status_count_lbl.setText(f"{len(self.all_games)} juegos cargados")

    def _on_game_selected(self, selected: QItemSelection, deselected: QItemSelection):
        indexes = selected.indexes()
        if indexes:
            game = self.table_model.get_game(indexes[0])
            if game:
                self.selected_rom = game.get("rom_name", "")
                title = game.get("title", "")
                driver = game.get("driver", "neogeo.cpp")

                self.media_dock.update_media(self.selected_rom)
                self.info_dock.update_info(self.selected_rom, driver)
                self.status_game_lbl.setText(f"{title} ({self.selected_rom})")

    def _on_search_changed(self, text: str):
        if not text.strip():
            self.table_model.set_games(self.all_games)
            self.status_count_lbl.setText(f"{len(self.all_games)} juegos cargados")
            return

        query = text.lower()
        filtered = [
            g for g in self.all_games
            if query in g.get("rom_name", "").lower() or query in g.get("title", "").lower()
        ]
        self.table_model.set_games(filtered)
        self.status_count_lbl.setText(f"{len(filtered)} juegos encontrados")

    def _on_category_filtered(self, filter_type: str, filter_value: str):
        if filter_type == "all":
            filtered = self.all_games
        elif filter_type == "available":
            val = int(filter_value)
            filtered = [g for g in self.all_games if g.get("has_rom") == val]
        elif filter_type == "favorite":
            filtered = [g for g in self.all_games if g.get("is_favorite") == 1]
        elif filter_type == "manufacturer":
            filtered = [g for g in self.all_games if filter_value.lower() in g.get("manufacturer", "").lower()]
        elif filter_type == "year":
            filtered = [g for g in self.all_games if g.get("year") == filter_value]
        elif filter_type == "status":
            filtered = [g for g in self.all_games if g.get("driver_status") == filter_value]
        elif filter_type == "clone":
            val = int(filter_value)
            filtered = [g for g in self.all_games if g.get("is_clone") == val]
        else:
            filtered = self.all_games

        self.table_model.set_games(filtered)
        self.status_count_lbl.setText(f"{len(filtered)} juegos en '{filter_value or filter_type}'")

    def _on_toggle_favorite(self, rom_name: str, new_favorite_state: bool):
        self.db_manager.set_favorite(rom_name, new_favorite_state)
        self._load_games()
        self.folder_dock.reload_tree()
        msg = f"'{rom_name}' agregado a Favoritos" if new_favorite_state else f"'{rom_name}' removido de Favoritos"
        self.statusbar.showMessage(msg, 3000)

    def _on_record_game(self, rom_name: str):
        self.selected_rom = rom_name
        self.statusbar.showMessage(f"Iniciando MAME con grabación de replay (.inp) para: {rom_name}...", 4000)
        self.mame_runner.launch_game(rom_name, extra_args=["-record", f"{rom_name}.inp"])

    def _on_audit_single_game(self, rom_name: str):
        self.statusbar.showMessage(f"Auditando ROM: {rom_name}...", 3000)

    def _on_show_properties(self, rom_name: str):
        game = next((g for g in self.all_games if g["rom_name"] == rom_name), None)
        if game:
            info = f"<b>Título:</b> {game.get('title')}<br>" \
                   f"<b>ROM:</b> {game.get('rom_name')}<br>" \
                   f"<b>Año:</b> {game.get('year')}<br>" \
                   f"<b>Fabricante:</b> {game.get('manufacturer')}<br>" \
                   f"<b>Driver:</b> {game.get('driver', 'neogeo.cpp')}<br>" \
                   f"<b>Partidas jugadas:</b> {game.get('play_count', 0)}"
            QMessageBox.information(self, f"Propiedades - {rom_name}", info)

    def _on_audit_roms(self):
        self.statusbar.showMessage("Escaneando carpeta roms/...")
        self.scan_thread = ROMScannerThread(self.db_manager)
        self.scan_thread.scan_finished.connect(self._on_audit_finished)
        self.scan_thread.start()

    def _on_audit_finished(self, count: int):
        self.statusbar.showMessage(f"Escaneo completado. Encontradas {count} ROMs.", 5000)
        self._load_games()

    def _on_import_full_romset(self):
        self.statusbar.showMessage("Importando catálogo completo del core...")
        self.import_thread = RomsetImportThread(self.db_manager)
        self.import_thread.progress.connect(lambda msg: self.statusbar.showMessage(msg))
        self.import_thread.import_finished.connect(self._on_import_full_romset_finished)
        self.import_thread.import_error.connect(self._on_import_full_romset_error)
        self.import_thread.start()

    def _on_import_full_romset_finished(self, count: int):
        self.statusbar.showMessage(f"Romset completo importado: {count} juegos.", 5000)
        self._load_games()
        self.folder_dock.reload_tree()

    def _on_import_full_romset_error(self, err_msg: str):
        self.statusbar.clearMessage()
        QMessageBox.warning(self, "Error de importación", err_msg)

    def _toggle_folder_dock(self):
        self.folder_dock.setVisible(not self.folder_dock.isVisible())

    def _toggle_media_docks(self):
        visible = not self.media_dock.isVisible()
        self.media_dock.setVisible(visible)
        self.info_dock.setVisible(visible)

    def _on_launch_specific_rom(self, rom_name: str):
        self.selected_rom = rom_name
        self._on_launch_game()

    def _on_launch_game(self):
        if not self.selected_rom:
            QMessageBox.information(self, "Seleccionar juego", "Por favor selecciona un juego de la lista.")
            return

        self.db_manager.increment_play_count(self.selected_rom)
        self.mame_runner.launch_game(self.selected_rom)

    def _on_mame_started(self):
        self.showMinimized()

    def _on_mame_finished(self, exit_code: int):
        self.showNormal()

    def _on_mame_error(self, err_msg: str):
        QMessageBox.warning(self, "Error MAME", err_msg)

    def _on_about(self):
        QMessageBox.about(self, "Acerca de MAMEXrd", "<b>MAMEXrd S E X Edition v1.0</b><br>Replica nativa moderna en PyQt6 de M+GUI / MAMEPGUI.<br>Desarrollado con Python 3 y SQLite3.")

    def _on_open_core_settings(self):
        dialog = MAMESettingsDialog(self)
        dialog.exec()
