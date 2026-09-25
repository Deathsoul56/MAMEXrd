from typing import List, Dict, Any, Optional
from pathlib import Path
import zipfile
from PyQt6.QtCore import QAbstractItemModel, Qt, QModelIndex, pyqtSignal, QPoint, QSize
from PyQt6.QtWidgets import QTreeView, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from utils.path_helper import PathHelper


class GameNode:
    """Nodo del árbol de juegos: representa un juego padre o un clon anidado bajo su padre."""
    __slots__ = ("game", "parent", "children")

    def __init__(self, game: Dict[str, Any], parent: Optional["GameNode"] = None):
        self.game = game
        self.parent = parent
        self.children: List["GameNode"] = []


class GameTableModel(QAbstractItemModel):
    """
    Modelo de árbol de juegos (Réplica del agrupamiento Padre/Clon de MAMEP/MAMEUI).
    Los juegos originales aparecen como nodos raíz y sus clones se anidan como hijos
    expandibles, en lugar de listarse todos en un único nivel plano.
    Columns: Description | Name | Year | Manufacturer | Driver | ROM | Clone of
    """
    COLUMNS = ["Description", "Name", "Year", "Manufacturer", "Driver", "ROM", "Clone of"]

    def __init__(self, games: Optional[List[Dict[str, Any]]] = None):
        super().__init__()
        self._icon_cache: Dict[str, Optional[QIcon]] = {}
        self._icon_zip: Optional[zipfile.ZipFile] = None
        self._icon_zip_names: Dict[str, str] = {}
        self._icon_zip_loaded = False
        self._root_nodes: List[GameNode] = []
        self._sort_column = 0
        self._sort_order = Qt.SortOrder.AscendingOrder
        self.set_games(games or [])

    def _sort_key(self, game: Dict[str, Any], column: int):
        if column == 0:
            return (game.get("title") or "").lower()
        elif column == 1:
            return (game.get("rom_name") or "").lower()
        elif column == 2:
            return self._year_sort_value(game.get("year"))
        elif column == 3:
            return (game.get("manufacturer") or "").lower()
        elif column == 4:
            return (game.get("driver") or "").lower()
        elif column == 5:
            return 1 if game.get("has_rom") else 0
        elif column == 6:
            return (game.get("parent_rom") or ("1" if game.get("is_clone") else "")).lower()
        return ""

    def _year_sort_value(self, year: Optional[str]):
        year_str = str(year or "")
        digits = "".join(ch for ch in year_str if ch.isdigit())
        if digits:
            return (0, int(digits[:4]))
        return (1, year_str.lower())

    def _sort_nodes_recursive(self, nodes: List[GameNode]):
        reverse = self._sort_order == Qt.SortOrder.DescendingOrder
        nodes.sort(key=lambda n: self._sort_key(n.game, self._sort_column), reverse=reverse)
        for n in nodes:
            self._sort_nodes_recursive(n.children)

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder):
        self._sort_column = column
        self._sort_order = order

        self.layoutAboutToBeChanged.emit()

        old_persistent = self.persistentIndexList()
        old_nodes = [idx.internalPointer() for idx in old_persistent]

        self._sort_nodes_recursive(self._root_nodes)

        new_persistent = []
        for idx, node in zip(old_persistent, old_nodes):
            siblings = node.parent.children if node.parent else self._root_nodes
            row = siblings.index(node)
            new_persistent.append(self.createIndex(row, idx.column(), node))
        self.changePersistentIndexList(old_persistent, new_persistent)

        self.layoutChanged.emit()
        self.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, len(self.COLUMNS) - 1)

    def _build_tree(self, games: List[Dict[str, Any]]):
        nodes_by_rom: Dict[str, GameNode] = {
            g.get("rom_name", ""): GameNode(g) for g in games
        }

        roots: List[GameNode] = []
        for g in games:
            node = nodes_by_rom[g.get("rom_name", "")]
            parent_rom = g.get("parent_rom") or ""
            parent_node = nodes_by_rom.get(parent_rom) if g.get("is_clone") else None

            if parent_node:
                node.parent = parent_node
                parent_node.children.append(node)
            else:
                roots.append(node)

        self._root_nodes = roots
        self._sort_nodes_recursive(self._root_nodes)

    def set_games(self, games: List[Dict[str, Any]]):
        self.beginResetModel()
        self._icon_cache.clear()  # el estado (has_rom/driver_status) pudo cambiar tras un audit/F5
        self._build_tree(games)
        self.endResetModel()

    def get_game(self, index: QModelIndex) -> Optional[Dict[str, Any]]:
        if index.isValid():
            return index.internalPointer().game
        return None

    # --- API de jerarquía QAbstractItemModel ---
    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_node = parent.internalPointer() if parent.isValid() else None
        children = parent_node.children if parent_node else self._root_nodes
        if 0 <= row < len(children):
            return self.createIndex(row, column, children[row])
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        node: GameNode = index.internalPointer()
        parent_node = node.parent
        if parent_node is None:
            return QModelIndex()

        grandparent = parent_node.parent
        siblings = grandparent.children if grandparent else self._root_nodes
        row = siblings.index(parent_node)
        return self.createIndex(row, 0, parent_node)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.column() > 0:
            return 0
        parent_node = parent.internalPointer() if parent.isValid() else None
        children = parent_node.children if parent_node else self._root_nodes
        return len(children)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        game: Dict[str, Any] = index.internalPointer().game
        col = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return game.get("title", "")
            elif col == 1:
                return game.get("rom_name", "")
            elif col == 2:
                return game.get("year", "")
            elif col == 3:
                return game.get("manufacturer", "")
            elif col == 4:
                return game.get("driver", "neogeo/neogeo.cpp")
            elif col == 5:
                return "Yes" if game.get("has_rom") else "No"
            elif col == 6:
                return game.get("parent_rom", "") or ("Yes" if game.get("is_clone") else "")

        elif role == Qt.ItemDataRole.DecorationRole and col == 0:
            rom_name = game.get("rom_name", "")
            parent_rom = game.get("parent_rom", "") if game.get("is_clone") else ""
            return self._get_game_icon(rom_name, parent_rom, bool(game.get("has_rom")), game.get("driver_status", "good"))

        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if col in (1, 2, 5, 6):
                return Qt.AlignmentFlag.AlignCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        elif role == Qt.ItemDataRole.ForegroundRole:
            if col == 5:  # Columna ROM (Yes/No)
                return QColor("#10b981") if game.get("has_rom") else QColor("#ef4444")
            if col == 0 and game.get("has_rom") and game.get("driver_status") == "preliminary":
                return QColor("#ef4444")  # Driver preliminary/no jugable (misma convención de color que MAMEP)

        return None

    # Colores de estado de emulación (misma convención que MAMEP/MAMEUI, tomada del atributo status de -listxml)
    _STATUS_COLORS = {
        "good": "#10b981",         # Verde: funciona correctamente
        "imperfect": "#f59e0b",    # Amarillo/naranja: emulación imperfecta pero jugable
        "preliminary": "#ef4444",  # Rojo: preliminar / no jugable
    }

    # Dimensiones del ícono compuesto: [cuadro de color][ícono del rom o espacio en blanco]
    _SQUARE_WIDTH = 14
    _ICON_SIZE = 24
    _ICON_SPACING = 4
    _COMPOSITE_WIDTH = _SQUARE_WIDTH + _ICON_SPACING + _ICON_SIZE

    def _get_game_icon(self, rom_name: str, parent_rom: str = "", has_rom: bool = False, driver_status: str = "good") -> Optional[QIcon]:
        if rom_name in self._icon_cache:
            return self._icon_cache[rom_name]

        real_pixmap = self._load_pixmap_from_folder(rom_name) or self._load_pixmap_from_zip(rom_name)
        if not real_pixmap and parent_rom:
            real_pixmap = self._load_pixmap_from_folder(parent_rom) or self._load_pixmap_from_zip(parent_rom)

        icon = self._build_composite_icon(has_rom, driver_status, real_pixmap)
        self._icon_cache[rom_name] = icon
        return icon

    def _build_composite_icon(self, has_rom: bool, driver_status: str, real_pixmap: Optional[QPixmap]) -> QIcon:
        """Compone [cuadro de estado][ícono propio del rom]; si no hay ícono propio deja el espacio en
        blanco para que todos los nombres arranquen desde la misma posición (igual que MAMEP)."""
        color = QColor(self._STATUS_COLORS.get(driver_status, "#10b981")) if has_rom else QColor("#6b7280")

        canvas = QPixmap(self._COMPOSITE_WIDTH, self._ICON_SIZE)
        canvas.fill(Qt.GlobalColor.transparent)

        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(color)
        painter.setPen(QColor("#1f2937"))
        painter.drawRoundedRect(0, 2, self._SQUARE_WIDTH, self._ICON_SIZE - 4, 2, 2)

        if real_pixmap and not real_pixmap.isNull():
            scaled = real_pixmap.scaled(
                self._ICON_SIZE, self._ICON_SIZE,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            x = self._SQUARE_WIDTH + self._ICON_SPACING + (self._ICON_SIZE - scaled.width()) // 2
            y = (self._ICON_SIZE - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        # Si no hay ícono propio, el espacio queda transparente (alineación consistente entre filas)

        painter.end()
        return QIcon(canvas)

    def _load_pixmap_from_folder(self, rom_name: str) -> Optional[QPixmap]:
        icons_dir = PathHelper.get_dir("icons")
        for ext in (".ico", ".png"):
            icon_path = icons_dir / f"{rom_name}{ext}"
            if icon_path.exists():
                pixmap = QPixmap(str(icon_path))
                if not pixmap.isNull():
                    return pixmap
        return None

    def _load_pixmap_from_zip(self, rom_name: str) -> Optional[QPixmap]:
        self._ensure_icon_zip_index()
        if not self._icon_zip:
            return None

        for ext in (".ico", ".png"):
            entry = self._icon_zip_names.get(f"{rom_name}{ext}")
            if entry:
                try:
                    pixmap = QPixmap()
                    pixmap.loadFromData(self._icon_zip.read(entry))
                    if not pixmap.isNull():
                        return pixmap
                except Exception:
                    return None
        return None

    def _ensure_icon_zip_index(self):
        """Indexa icons.zip una sola vez (convención de packs de iconos MAMEUI/MAMEP sin descomprimir)."""
        if self._icon_zip_loaded:
            return
        self._icon_zip_loaded = True

        mame_exe = PathHelper.get_mame_executable()
        root_dir = mame_exe.parent if mame_exe and mame_exe.exists() else PathHelper.get_base_dir()
        zip_path = root_dir / "icons.zip"
        if not zip_path.exists():
            return

        try:
            self._icon_zip = zipfile.ZipFile(zip_path, "r")
            self._icon_zip_names = {Path(name).name.lower(): name for name in self._icon_zip.namelist()}
        except Exception:
            self._icon_zip = None

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            name = self.COLUMNS[section]
            if section == self._sort_column:
                arrow = "▲" if self._sort_order == Qt.SortOrder.AscendingOrder else "▼"
                return f"{name} {arrow}"
            return name
        return None


class GameTableView(QTreeView):
    """
    Vista de árbol con fondo MAME y Menú de Clic Derecho (Réplica exactas de Legacy/Click Derecho Menu.png).
    Agrupa los clones bajo su juego padre, igual que MAMEP/MAMEUI.
    """
    play_requested = pyqtSignal(str)
    record_requested = pyqtSignal(str)
    favorite_toggled = pyqtSignal(str, bool)
    audit_requested = pyqtSignal(str)
    properties_requested = pyqtSignal(str)
    add_to_folder_requested = pyqtSignal(str, str)  # (rom_name, folder_name)
    new_folder_requested = pyqtSignal(str)  # (rom_name) -> main_window pide el nombre y crea la carpeta
    video_settings_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg_pixmap: Optional[QPixmap] = None
        self.custom_folders_provider = None  # Callable[[], List[str]] inyectado por MainWindow
        self._load_bg_pixmap()

        self.setRootIsDecorated(True)
        self.setUniformRowHeights(True)
        self.setIconSize(QSize(GameTableModel._COMPOSITE_WIDTH, GameTableModel._ICON_SIZE))
        self.setItemsExpandable(True)
        self.setExpandsOnDoubleClick(False)  # el doble clic lanza el juego, no expande/contrae
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.header().setSortIndicatorShown(False)  # usamos flecha de texto propia en el título de columna
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.expandAll()

        # Menú contextual de Clic Derecho
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            index = self.currentIndex()
            game = self.model().get_game(index) if self.model() and index.isValid() else None
            if game:
                self.play_requested.emit(game.get("rom_name", ""))
                return
        super().keyPressEvent(event)

    def setModel(self, model):
        super().setModel(model)
        model.modelReset.connect(self.expandAll)
        self.expandAll()

    def _load_bg_pixmap(self):
        bg_dir = PathHelper.get_dir("bkground")
        bg_path = bg_dir / "MAME.jpg"
        if not bg_path.exists():
            bg_path = bg_dir / "MAME.png"

        if bg_path.exists():
            self.bg_pixmap = QPixmap(str(bg_path))

    def paintEvent(self, event):
        if self.bg_pixmap and not self.bg_pixmap.isNull():
            painter = QPainter(self.viewport())
            painter.setOpacity(0.15)
            painter.drawPixmap(
                (self.viewport().width() - self.bg_pixmap.width()) // 2,
                (self.viewport().height() - self.bg_pixmap.height()) // 2,
                self.bg_pixmap
            )
            painter.end()
        super().paintEvent(event)

    def _show_context_menu(self, pos: QPoint):
        index = self.indexAt(pos)
        if not index.isValid():
            return

        model: GameTableModel = self.model()
        game = model.get_game(index)
        if not game:
            return

        rom_name = game.get("rom_name", "")
        title = game.get("title", "")
        is_fav = bool(game.get("is_favorite", False))
        driver = game.get("driver", "neogeo/neogeo.cpp")

        menu = QMenu(self)

        # 1. Play <rom_name>
        game_icon = model._get_game_icon(
            rom_name,
            game.get("parent_rom", "") if game.get("is_clone") else "",
            bool(game.get("has_rom")),
            game.get("driver_status", "good"),
        )
        play_act = QAction(game_icon if game_icon else QIcon(), f"Play {rom_name}", menu)
        play_act.triggered.connect(lambda: self.play_requested.emit(rom_name))
        menu.addAction(play_act)

        # 2. Record Input...
        record_act = QAction("Record Input...", menu)
        record_act.triggered.connect(lambda: self.record_requested.emit(rom_name))
        menu.addAction(record_act)

        # 3. Clean Up >
        cleanup_menu = menu.addMenu("Clean Up")
        clean_nvram = QAction("Clean NVRAM", menu)
        clean_cfg = QAction("Clean Configuration", menu)
        clean_sta = QAction("Clean Savestate", menu)
        cleanup_menu.addAction(clean_nvram)
        cleanup_menu.addAction(clean_cfg)
        cleanup_menu.addAction(clean_sta)

        menu.addSeparator()

        # 4. Add to Custom Folder >
        custom_folder_menu = menu.addMenu("Add to Custom Folder")
        folder_names = self.custom_folders_provider() if self.custom_folders_provider else []
        for folder_name in folder_names:
            add_folder_act = QAction(folder_name, menu)
            add_folder_act.triggered.connect(
                lambda checked=False, fn=folder_name: self.add_to_folder_requested.emit(rom_name, fn)
            )
            custom_folder_menu.addAction(add_folder_act)
        if folder_names:
            custom_folder_menu.addSeparator()
        new_folder_act = QAction("New folder...", menu)
        new_folder_act.triggered.connect(lambda: self.new_folder_requested.emit(rom_name))
        custom_folder_menu.addAction(new_folder_act)

        # 5. Remove From "Favorites" / Add to "Favorites"
        fav_label = 'Remove From "Favorites"' if is_fav else 'Add to "Favorites"'
        fav_act = QAction(fav_label, menu)
        fav_act.triggered.connect(lambda: self.favorite_toggled.emit(rom_name, not is_fav))
        menu.addAction(fav_act)

        menu.addSeparator()

        # 6. Audit
        audit_act = QAction("Audit", menu)
        audit_act.triggered.connect(lambda: self.audit_requested.emit(rom_name))
        menu.addAction(audit_act)

        # 7. Memcard: [Empty slot] >
        memcard_menu = menu.addMenu("Memcard: [Empty slot]")
        memcard_menu.addAction(QAction("Insert Memory Card...", menu))

        menu.addSeparator()

        # 7b. Settings for <rom_name>...
        video_settings_act = QAction(f"Settings for {rom_name}...", menu)
        video_settings_act.triggered.connect(lambda: self.video_settings_requested.emit(rom_name))
        menu.addAction(video_settings_act)

        menu.addSeparator()

        # 8. Properties for <driver>
        driver_act = QAction(f"Properties for {driver}", menu)
        driver_act.triggered.connect(lambda: self.properties_requested.emit(rom_name))
        menu.addAction(driver_act)

        # 9. Properties
        prop_act = QAction("Properties", menu)
        prop_act.triggered.connect(lambda: self.properties_requested.emit(rom_name))
        menu.addAction(prop_act)

        menu.exec(self.viewport().mapToGlobal(pos))

