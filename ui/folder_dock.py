from PyQt6.QtWidgets import (
    QDockWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
)
from PyQt6.QtCore import pyqtSignal, Qt
from database.db_manager import DatabaseManager

class FolderListDock(QDockWidget):
    """
    Panel acoplable lateral izquierdo 'Folder List' (Réplica exacta de Legacy/Pantalla Inicio.png).
    Permite filtrar los juegos por categorías, fabricantes, años, estados y favoritos.
    """
    category_selected = pyqtSignal(str, str)  # (tipo_filtro, valor_filtro)

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__("Folder List", parent)
        self.setObjectName("FolderListDock")
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        self.db_manager = db_manager
        self._init_ui()

    def _init_ui(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self._on_item_clicked)

        self.reload_tree()

        layout.addWidget(self.tree)
        self.setWidget(container)

    def reload_tree(self):
        """Puebla dinámicamente el árbol de categorías con datos de la BD."""
        self.tree.clear()

        # Categorías principales
        all_item = QTreeWidgetItem(["All Arcades"])
        all_item.setData(0, Qt.ItemDataRole.UserRole, ("all", ""))
        self.tree.addTopLevelItem(all_item)

        avail_item = QTreeWidgetItem(["Available Arcades"])
        avail_item.setData(0, Qt.ItemDataRole.UserRole, ("available", "1"))
        self.tree.addTopLevelItem(avail_item)

        unavail_item = QTreeWidgetItem(["Unavailable Arcades"])
        unavail_item.setData(0, Qt.ItemDataRole.UserRole, ("available", "0"))
        self.tree.addTopLevelItem(unavail_item)

        fav_item = QTreeWidgetItem(["Favorites"])
        fav_item.setData(0, Qt.ItemDataRole.UserRole, ("favorite", "1"))
        self.tree.addTopLevelItem(fav_item)

        # Categoría: Fabricantes (Manufacturer) desde la BD
        manuf_root = QTreeWidgetItem(["Manufacturer"])
        manuf_root.setData(0, Qt.ItemDataRole.UserRole, ("root", "manufacturer"))
        manufacturers = self.db_manager.get_manufacturers()
        for m in manufacturers:
            child = QTreeWidgetItem([m])
            child.setData(0, Qt.ItemDataRole.UserRole, ("manufacturer", m))
            manuf_root.addChild(child)
        self.tree.addTopLevelItem(manuf_root)

        # Categoría: Año (Year) desde la BD
        year_root = QTreeWidgetItem(["Year"])
        year_root.setData(0, Qt.ItemDataRole.UserRole, ("root", "year"))
        years = self.db_manager.get_years()
        for y in years[:30]:  # Mostrar principales 30 años
            child = QTreeWidgetItem([y])
            child.setData(0, Qt.ItemDataRole.UserRole, ("year", y))
            year_root.addChild(child)
        self.tree.addTopLevelItem(year_root)

        # Categoría: Estado de Trabajo (Working / Not Working)
        working_item = QTreeWidgetItem(["Working"])
        working_item.setData(0, Qt.ItemDataRole.UserRole, ("status", "good"))
        self.tree.addTopLevelItem(working_item)

        not_working_item = QTreeWidgetItem(["Not Working"])
        not_working_item.setData(0, Qt.ItemDataRole.UserRole, ("status", "preliminary"))
        self.tree.addTopLevelItem(not_working_item)

        # Categoría: Originales / Clones
        orig_item = QTreeWidgetItem(["Originals"])
        orig_item.setData(0, Qt.ItemDataRole.UserRole, ("clone", "0"))
        self.tree.addTopLevelItem(orig_item)

        clones_item = QTreeWidgetItem(["Clones"])
        clones_item.setData(0, Qt.ItemDataRole.UserRole, ("clone", "1"))
        self.tree.addTopLevelItem(clones_item)

        self.tree.collapseAll()

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            filter_type, filter_value = data
            if filter_type != "root":
                self.category_selected.emit(filter_type, filter_value)
