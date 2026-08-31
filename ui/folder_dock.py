from PyQt6.QtWidgets import (
    QDockWidget, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
    QPushButton, QInputDialog, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import Optional
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

        self.new_folder_btn = QPushButton("+ New Folder")
        self.new_folder_btn.clicked.connect(self._on_new_folder_clicked)

        self.reload_tree()

        layout.addWidget(self.tree)
        layout.addWidget(self.new_folder_btn)
        self.setWidget(container)

    def _on_new_folder_clicked(self):
        """Crea una nueva carpeta personalizada vacía desde el Folder List."""
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if not ok or not name.strip():
            return
        if not self.db_manager.create_custom_folder(name.strip()):
            QMessageBox.warning(self, "New Folder", "Invalid folder name.")
            return
        self.reload_tree()

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

        # Categoría: Carpetas personalizadas creadas por el usuario
        custom_root = QTreeWidgetItem(["Custom Folders"])
        custom_root.setData(0, Qt.ItemDataRole.UserRole, ("root", "custom_folder"))
        for folder_name in self.db_manager.get_custom_folders():
            child = QTreeWidgetItem([folder_name])
            child.setData(0, Qt.ItemDataRole.UserRole, ("custom_folder", folder_name))
            custom_root.addChild(child)
        self.tree.addTopLevelItem(custom_root)

        self.tree.collapseAll()

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            filter_type, filter_value = data
            if filter_type != "root":
                self.category_selected.emit(filter_type, filter_value)

    def select_category(self, filter_type: str, filter_value: str):
        """Selecciona visualmente la categoría indicada (restauración de la última sesión al abrir)."""
        def _search(item: QTreeWidgetItem) -> Optional[QTreeWidgetItem]:
            if item.data(0, Qt.ItemDataRole.UserRole) == (filter_type, filter_value):
                return item
            for i in range(item.childCount()):
                found = _search(item.child(i))
                if found:
                    return found
            return None

        for i in range(self.tree.topLevelItemCount()):
            found = _search(self.tree.topLevelItem(i))
            if found:
                if found.parent():
                    found.parent().setExpanded(True)
                self.tree.setCurrentItem(found)
                self.category_selected.emit(filter_type, filter_value)
                return
