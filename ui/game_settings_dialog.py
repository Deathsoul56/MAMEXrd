from math import gcd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QListWidget, QListWidgetItem, QStackedWidget,
    QButtonGroup, QRadioButton, QCheckBox,
    QMessageBox, QDialogButtonBox, QLabel
)
from core.mame_ini_manager import MAMEIniManager
from core.game_ini_manager import GameIniManager
from core.mame_parser import get_screen_display_info
from utils.i18n import tr


class GameSettingsDialog(QDialog):
    """
    Configuración específica por ROM (ej. sf2ce.ini), separada de las opciones
    globales de mame.ini. Navegación en dos paneles (categorías a la izquierda,
    opciones a la derecha) que replica exactamente los menús nativos de MAME
    (mismos nombres, mismas opciones, nada más). Cada campo tiene un checkbox
    "Override": si está desmarcado el juego hereda el valor global de mame.ini;
    si se marca, se guarda un override propio en ini/<rom>.ini (leído
    automáticamente por MAME gracias a su inipath por defecto).
    """
    def __init__(self, rom_name: str, parent=None):
        super().__init__(parent)
        self.rom_name = rom_name
        self.setWindowTitle(f"{tr('game_dialog.title')} — {rom_name}")
        self.resize(520, 380)

        self.global_ini = MAMEIniManager()
        self.game_ini = GameIniManager(rom_name)
        # key -> (kind, override_checkbox, field_widget)
        self._rows = {}

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        hint = QLabel(tr("game_dialog.hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #94a3b8;")
        layout.addWidget(hint)

        content = QHBoxLayout()
        layout.addLayout(content)

        self.category_list = QListWidget()
        self.category_list.setFixedWidth(160)
        self.pages = QStackedWidget()

        self._add_category(tr("game_dialog.category_video"), self._build_video_page(), enabled=True)
        self._add_category(tr("game_dialog.category_audio"), self._build_placeholder_page(), enabled=False)

        self.category_list.setCurrentRow(0)
        self.category_list.currentRowChanged.connect(self.pages.setCurrentIndex)

        content.addWidget(self.category_list)
        content.addWidget(self.pages, 1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _add_category(self, label: str, page: QWidget, enabled: bool):
        item = QListWidgetItem(label)
        if not enabled:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
        self.category_list.addItem(item)
        self.pages.addWidget(page)

    def _override_row(self, key: str, label: str, form: QFormLayout, kind: str):
        global_value = self.global_ini.get(key, "")
        has_override = key in self.game_ini.settings

        chk = QCheckBox(f"{label} ({tr('game_dialog.global_value')}: {global_value})")
        chk.setChecked(has_override)

        field = QCheckBox()
        field.setChecked(self.game_ini.get_bool(key) if has_override else self.global_ini.get_bool(key))
        field.setEnabled(has_override)
        chk.toggled.connect(field.setEnabled)

        form.addRow(chk, field)
        self._rows[key] = (kind, chk, field)
        return field

    def _override_radio_row(self, key: str, label: str, form: QFormLayout, options):
        """
        Fila de opción única (radio buttons), como el listado exclusivo
        "Screen 0 Standard / Pixel Aspect / Cocktail" del menú nativo de MAME:
        solo se puede elegir una entre varias, como en un examen de opción múltiple.
        `options` es una lista de tuplas (valor_ini, texto_mostrado).
        """
        global_value = self.global_ini.get(key, "auto")
        has_override = key in self.game_ini.settings
        current = self.game_ini.get(key) if has_override else global_value

        chk = QCheckBox(f"{label} ({tr('game_dialog.global_value')}: {global_value})")
        chk.setChecked(has_override)

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        group = QButtonGroup(container)
        for value, display in options:
            rb = QRadioButton(display)
            rb.setProperty("ini_value", value)
            group.addButton(rb)
            vbox.addWidget(rb)
            if value == current:
                rb.setChecked(True)
        if not group.checkedButton() and group.buttons():
            group.buttons()[0].setChecked(True)
        container.button_group = group

        container.setEnabled(has_override)
        chk.toggled.connect(container.setEnabled)

        form.addRow(chk, container)
        self._rows[key] = ("radio", chk, container)
        return container

    def _screen0_view_options(self):
        """
        Nombres EXACTOS de vista que usa MAME internamente (los mismos que graba
        en cfg/<rom>.cfg, ej. "Screen 0 Pixel Aspect (12:7)"), calculados a partir
        de la resolución real de la ROM para que coincidan con el menú nativo.
        """
        info = get_screen_display_info(self.rom_name)
        if info and info["width"] and info["height"]:
            w, h = info["width"], info["height"]
            divisor = gcd(w, h) or 1
            std_ratio = "3:4" if info["rotate"] in (90, 270) else "4:3"
            standard_value = f"Screen 0 {tr('game_opt.view0_standard')} ({std_ratio})"
            pixel_value = f"Screen 0 {tr('game_opt.view0_pixel_aspect')} ({w // divisor}:{h // divisor})"
        else:
            standard_value = f"Screen 0 {tr('game_opt.view0_standard')}"
            pixel_value = f"Screen 0 {tr('game_opt.view0_pixel_aspect')}"
        return [
            (standard_value, standard_value.replace("Screen 0 ", "")),
            (pixel_value, pixel_value.replace("Screen 0 ", "")),
            (tr("game_opt.view0_cocktail"), tr("game_opt.view0_cocktail")),
        ]

    def _build_video_page(self) -> QWidget:
        # Replica el menú nativo "Video Options: Screen #0" (mismos campos, mismo orden).
        w = QWidget()
        form = QFormLayout(w)
        self._override_radio_row("view0", tr("game_opt.view0"), form, options=self._screen0_view_options())
        self._override_row("rotate", tr("game_opt.rotate"), form, "bool")
        self._override_row("artwork_crop", tr("game_opt.artwork_crop"), form, "bool")
        self._override_row("unevenstretch", tr("game_opt.unevenstretch"), form, "bool")
        self._override_row("keepaspect", tr("game_opt.keepaspect"), form, "bool")
        return w

    def _build_placeholder_page(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        label = QLabel(tr("game_dialog.coming_soon"))
        label.setStyleSheet("color: #94a3b8;")
        layout.addWidget(label)
        layout.addStretch()
        return w

    def _on_save(self):
        for key, (kind, chk, field) in self._rows.items():
            if not chk.isChecked():
                self.game_ini.clear(key)
                if key == "view0":
                    self.game_ini.sync_cfg_view(None)
                continue
            if kind == "bool":
                self.game_ini.set_bool(key, field.isChecked())
            elif kind == "radio":
                checked = field.button_group.checkedButton()
                value = checked.property("ini_value") if checked else "auto"
                self.game_ini.set(key, value)
                if key == "view0":
                    self.game_ini.sync_cfg_view(value)
            else:
                self.game_ini.set(key, field.currentText().strip())

        if self.game_ini.save():
            QMessageBox.information(self, tr("dialog.save_title"), tr("dialog.save_message"))
            self.accept()
        else:
            QMessageBox.critical(self, tr("dialog.error_title"), tr("dialog.error_message"))
