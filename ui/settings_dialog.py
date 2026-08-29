from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QFormLayout,
    QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, QLineEdit,
    QMessageBox, QDialogButtonBox, QLabel, QFrame, QScrollArea
)
from core.mame_ini_manager import MAMEIniManager
from utils.i18n import tr

class MAMESettingsDialog(QDialog):
    """
    Diálogo de Opciones del Core de MAME.
    Lee y escribe directamente sobre mame.ini a través de MAMEIniManager,
    exponiendo las opciones más comunes organizadas por pestañas.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dialog.title"))
        self.resize(540, 440)

        self.ini_manager = MAMEIniManager()
        self.ui_ini_manager = MAMEIniManager(ini_filename="ui.ini")
        self.plugin_ini_manager = MAMEIniManager(ini_filename="plugin.ini")
        # storage_key ("<ini_filename>:<key>") -> (tipo, widget, manager, key)
        self._widgets = {}

        self._init_ui()
        self._load_values()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        if not self.ini_manager.ini_path.exists():
            warn = QLabel(tr("dialog.warning_no_ini"))
            warn.setStyleSheet("color: #f59e0b; font-weight: bold;")
            layout.addWidget(warn)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tabs.addTab(self._build_video_tab(), tr("tab.video"))
        self.tabs.addTab(self._build_screen_tab(), tr("tab.screen"))
        self.tabs.addTab(self._build_sound_tab(), tr("tab.sound"))
        self.tabs.addTab(self._build_input_tab(), tr("tab.input"))
        self.tabs.addTab(self._build_misc_tab(), tr("tab.misc"))
        self.tabs.addTab(self._build_ui_misc_tab(), tr("tab.ui_misc"))
        self.tabs.addTab(self._build_advanced_tab(), tr("tab.advanced"))
        self.tabs.addTab(self._build_plugins_tab(), tr("tab.plugins"))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # --- Helpers de construcción de campos ---
    def _combo(self, key: str, options, form: QFormLayout, label: str, manager=None):
        manager = manager or self.ini_manager
        combo = QComboBox()
        combo.setEditable(True)
        combo.addItems(options)
        form.addRow(label, combo)
        self._widgets[f"{manager.ini_filename}:{key}"] = ("combo", combo, manager, key)
        return combo

    def _check(self, key: str, label: str, form: QFormLayout, manager=None):
        manager = manager or self.ini_manager
        chk = QCheckBox(label)
        form.addRow("", chk)
        self._widgets[f"{manager.ini_filename}:{key}"] = ("bool", chk, manager, key)
        return chk

    def _check_str(self, key: str, label: str, form: QFormLayout, true_val: str, false_val: str, manager=None):
        """Checkbox para claves de ini que usan valores de texto (ej. auto/none) en vez de 1/0."""
        manager = manager or self.ini_manager
        chk = QCheckBox(label)
        form.addRow("", chk)
        self._widgets[f"{manager.ini_filename}:{key}"] = (f"boolstr:{true_val}:{false_val}", chk, manager, key)
        return chk

    def _spin(self, key: str, minv: int, maxv: int, form: QFormLayout, label: str, manager=None):
        manager = manager or self.ini_manager
        spin = QSpinBox()
        spin.setRange(minv, maxv)
        form.addRow(label, spin)
        self._widgets[f"{manager.ini_filename}:{key}"] = ("int", spin, manager, key)
        return spin

    def _dspin(self, key: str, minv: float, maxv: float, form: QFormLayout, label: str, step: float = 0.1, manager=None):
        manager = manager or self.ini_manager
        spin = QDoubleSpinBox()
        spin.setRange(minv, maxv)
        spin.setSingleStep(step)
        spin.setDecimals(2)
        form.addRow(label, spin)
        self._widgets[f"{manager.ini_filename}:{key}"] = ("float", spin, manager, key)
        return spin

    def _line(self, key: str, form: QFormLayout, label: str, manager=None):
        manager = manager or self.ini_manager
        line = QLineEdit()
        form.addRow(label, line)
        self._widgets[f"{manager.ini_filename}:{key}"] = ("str", line, manager, key)
        return line

    def _scan_shader_options(self) -> list:
        """Lista dinámica de shaders GLSL disponibles (cualquier .vsh en la carpeta shader/ del usuario)."""
        shader_dir = self.ini_manager.mame_dir / "shader"
        if not shader_dir.is_dir():
            return []
        names = sorted(p.stem for p in shader_dir.glob("*.vsh"))
        return [f"shader/{name}" for name in names]

    # --- Pestañas ---
    def _build_video_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._combo("video", ["auto", "gdi", "d3d", "bgfx", "opengl"], form, tr("opt.video"))
        self._check("window", tr("opt.window"), form)
        self._check("keepaspect", tr("opt.keepaspect"), form)
        self._check("maximize", tr("opt.maximize"), form)
        self._check("waitvsync", tr("opt.waitvsync"), form)
        self._check("syncrefresh", tr("opt.syncrefresh"), form)
        self._check("triplebuffer", tr("opt.triplebuffer"), form)
        self._check("filter", tr("opt.filter"), form)
        self._check("hlsl_enable", tr("opt.hlsl_enable"), form)
        self._check("gl_glsl", tr("opt.gl_glsl"), form)
        shader_options = ["none"] + self._scan_shader_options()
        self._combo("glsl_shader_mame0", shader_options, form, tr("opt.glsl_shader_mame0"))
        self._spin("prescale", 1, 3, form, tr("opt.prescale"))
        self._spin("numscreens", 1, 4, form, tr("opt.numscreens"))
        return w

    def _build_screen_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._line("resolution", form, tr("opt.resolution"))
        self._line("aspect", form, tr("opt.aspect"))
        self._dspin("brightness", 0.2, 2.0, form, tr("opt.brightness"))
        self._dspin("contrast", 0.2, 2.0, form, tr("opt.contrast"))
        self._dspin("gamma", 0.1, 3.0, form, tr("opt.gamma"))
        return w

    def _build_sound_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._check_str("sound", tr("opt.sound"), form, "auto", "none")
        self._combo("samplerate", ["11025", "22050", "44100", "48000", "96000"], form, tr("opt.samplerate"))
        self._check("samples", tr("opt.samples"), form)
        self._spin("volume", -32, 0, form, tr("opt.volume"))
        return w

    def _build_input_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)

        device_options = ["keyboard", "mouse", "joystick", "lightgun", "none"]
        self._combo("lightgun_device", device_options, form, tr("opt.lightgun_device"))
        self._combo("trackball_device", device_options, form, tr("opt.trackball_device"))
        self._combo("pedal_device", device_options, form, tr("opt.pedal_device"))
        self._combo("adstick_device", device_options, form, tr("opt.adstick_device"))
        self._combo("paddle_device", device_options, form, tr("opt.paddle_device"))
        self._combo("dial_device", device_options, form, tr("opt.dial_device"))
        self._combo("positional_device", device_options, form, tr("opt.positional_device"))
        self._combo("mouse_device", device_options, form, tr("opt.mouse_device"))

        provider_options = ["auto", "dinput", "rawinput", "win32", "xinput", "none"]
        self._combo("keyboardprovider", provider_options, form, tr("opt.keyboardprovider"))
        self._combo("mouseprovider", provider_options, form, tr("opt.mouseprovider"))
        self._combo("lightgunprovider", provider_options, form, tr("opt.lightgunprovider"))
        self._combo("joystickprovider", provider_options, form, tr("opt.joystickprovider"))
        return w

    def _build_misc_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._check("plugins", tr("opt.plugins"), form)
        return w

    def _build_ui_misc_tab(self) -> QWidget:
        """Opciones de 'Miscellaneous Options' del menú interno de MAME (ui.ini + mame.ini), en el mismo orden que el back."""
        w = QWidget()
        form = QFormLayout(w)
        m = self.ui_ini_manager
        self._check("menu_pause", tr("opt.menu_pause"), form, manager=m)
        self._check("ui_follow_focus", tr("opt.ui_follow_focus"), form, manager=m)
        self._check("skip_warnings", tr("opt.skip_warnings"), form, manager=m)
        self._check("remember_last", tr("opt.remember_last"), form, manager=m)
        self._check("enlarge_snaps", tr("opt.enlarge_snaps"), form, manager=m)
        self._check("cheat", tr("opt.cheat"), form)
        self._check("ui_mouse", tr("opt.ui_mouse"), form)
        self._check("confirm_quit", tr("opt.confirm_quit"), form)
        self._check("skip_gameinfo", tr("opt.skip_gameinfo"), form)
        self._check("forced4x3", tr("opt.forced4x3"), form, manager=m)
        self._check("use_background", tr("opt.use_background"), form, manager=m)
        self._check("skip_biosmenu", tr("opt.skip_biosmenu"), form, manager=m)
        self._check("skip_partsmenu", tr("opt.skip_partsmenu"), form, manager=m)
        self._check("info_audit_enabled", tr("opt.info_audit_enabled"), form, manager=m)
        self._check("hide_romless", tr("opt.hide_romless"), form, manager=m)
        return w

    def _section(self, form: QFormLayout, label_key: str, first: bool = False):
        """Encabezado visual de sección dentro de una pestaña (no es un campo editable)."""
        if not first:
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet("background-color: #3f3f46; max-height: 1px; border: none; margin-top: 10px;")
            form.addRow(line)
        lbl = QLabel(tr(label_key))
        lbl.setStyleSheet("font-weight: bold; color: #94a3b8; margin-top: 4px;")
        form.addRow(lbl)

    def _build_advanced_tab(self) -> QWidget:
        """Réplica de 'Advanced Options' del menú interno de MAME, agrupada por bloques."""
        w = QWidget()
        form = QFormLayout(w)

        self._section(form, "section.performance", first=True)
        self._check("autoframeskip", tr("opt.autoframeskip"), form)
        self._spin("frameskip", 0, 10, form, tr("opt.frameskip"))
        self._check("throttle", tr("opt.throttle"), form)
        self._check("unthrottle_mute", tr("opt.unthrottle_mute"), form, manager=self.ui_ini_manager)
        self._check("sleep", tr("opt.sleep"), form)
        self._dspin("speed", 0.1, 5.0, form, tr("opt.speed"), step=0.1)
        self._check("refreshspeed", tr("opt.refreshspeed"), form)
        self._check("lowlatency", tr("opt.lowlatency"), form)
        self._line("numprocessors", form, tr("opt.numprocessors"))

        self._section(form, "section.rotation")
        self._check("rotate", tr("opt.rotate"), form)
        self._check("ror", tr("opt.ror"), form)
        self._check("rol", tr("opt.rol"), form)
        self._check("autoror", tr("opt.autoror"), form)
        self._check("autorol", tr("opt.autorol"), form)
        self._check("flipx", tr("opt.flipx"), form)
        self._check("flipy", tr("opt.flipy"), form)

        self._section(form, "section.artwork")
        self._check("artwork_crop", tr("opt.artwork_crop"), form)

        self._section(form, "section.state_playback")
        self._check("autosave", tr("opt.autosave"), form)
        self._check("rewind", tr("opt.rewind"), form)
        self._spin("rewind_capacity", 1, 500, form, tr("opt.rewind_capacity"))
        self._check("snapbilinear", tr("opt.snapbilinear"), form)
        self._check("burnin", tr("opt.burnin"), form)

        self._section(form, "section.input_advanced")
        self._check("coin_lockout", tr("opt.coin_lockout"), form)
        self._check("mouse", tr("opt.mouse"), form)
        self._check("joystick", tr("opt.joystick"), form)
        self._check("lightgun", tr("opt.lightgun"), form)
        self._check("multikeyboard", tr("opt.multikeyboard"), form)
        self._check("multimouse", tr("opt.multimouse"), form)
        self._check("steadykey", tr("opt.steadykey"), form)
        self._check("ui_active", tr("opt.ui_active"), form)
        self._dspin("joystick_deadzone", 0.0, 1.0, form, tr("opt.joystick_deadzone"), step=0.05)
        self._dspin("joystick_saturation", 0.0, 1.0, form, tr("opt.joystick_saturation"), step=0.05)
        self._dspin("joystick_threshold", 0.0, 1.0, form, tr("opt.joystick_threshold"), step=0.05)
        self._check("natural", tr("opt.natural"), form)
        self._check("joystick_contradictory", tr("opt.joystick_contradictory"), form)
        self._spin("coin_impulse", 0, 10, form, tr("opt.coin_impulse"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(w)
        return scroll

    def _build_plugins_tab(self) -> QWidget:
        """Plugins Lua individuales del menú interno de MAME (plugin.ini)."""
        w = QWidget()
        form = QFormLayout(w)
        m = self.plugin_ini_manager
        self._check("autofire", tr("opt.plugin_autofire"), form, manager=m)
        self._check("cheat", tr("opt.plugin_cheat"), form, manager=m)
        self._check("cheatfind", tr("opt.plugin_cheatfind"), form, manager=m)
        self._check("console", tr("opt.plugin_console"), form, manager=m)
        self._check("data", tr("opt.plugin_data"), form, manager=m)
        self._check("discord", tr("opt.plugin_discord"), form, manager=m)
        self._check("dummy", tr("opt.plugin_dummy"), form, manager=m)
        self._check("gdbstub", tr("opt.plugin_gdbstub"), form, manager=m)
        self._check("hiscore", tr("opt.plugin_hiscore"), form, manager=m)
        self._check("inputmacro", tr("opt.plugin_inputmacro"), form, manager=m)
        self._check("keypress", tr("opt.plugin_keypress"), form, manager=m)
        self._check("layout", tr("opt.plugin_layout"), form, manager=m)
        self._check("offscreenreload", tr("opt.plugin_offscreenreload"), form, manager=m)
        self._check("portname", tr("opt.plugin_portname"), form, manager=m)
        self._check("timecode", tr("opt.plugin_timecode"), form, manager=m)
        self._check("timer", tr("opt.plugin_timer"), form, manager=m)
        self._check("vector", tr("opt.plugin_vector"), form, manager=m)
        return w

    # --- Carga / Guardado ---
    def _load_values(self):
        for storage_key, (kind, widget, manager, key) in self._widgets.items():
            if kind == "bool":
                widget.setChecked(manager.get_bool(key))
            elif kind.startswith("boolstr:"):
                _, true_val, false_val = kind.split(":", 2)
                current = manager.get(key, false_val)
                widget.setChecked(current.strip().lower() == true_val.lower())
            elif kind == "int":
                try:
                    widget.setValue(int(manager.get(key, "0") or 0))
                except ValueError:
                    widget.setValue(0)
            elif kind == "float":
                try:
                    widget.setValue(float(manager.get(key, "0") or 0))
                except ValueError:
                    widget.setValue(0.0)
            elif kind in ("str", "combo"):
                value = manager.get(key, "")
                if kind == "combo":
                    widget.setCurrentText(value)
                else:
                    widget.setText(value)

    def _on_save(self):
        for storage_key, (kind, widget, manager, key) in self._widgets.items():
            if kind == "bool":
                manager.set_bool(key, widget.isChecked())
            elif kind.startswith("boolstr:"):
                _, true_val, false_val = kind.split(":", 2)
                manager.set(key, true_val if widget.isChecked() else false_val)
            elif kind == "int":
                manager.set(key, str(widget.value()))
            elif kind == "float":
                manager.set(key, str(widget.value()))
            elif kind in ("str", "combo"):
                text = widget.currentText() if kind == "combo" else widget.text()
                manager.set(key, text.strip())

        if self.ini_manager.save() and self.ui_ini_manager.save() and self.plugin_ini_manager.save():
            QMessageBox.information(self, tr("dialog.save_title"), tr("dialog.save_message"))
            self.accept()
        else:
            QMessageBox.critical(self, tr("dialog.error_title"), tr("dialog.error_message"))
