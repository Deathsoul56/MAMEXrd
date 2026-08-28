from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QFormLayout,
    QComboBox, QCheckBox, QSpinBox, QDoubleSpinBox, QLineEdit,
    QMessageBox, QDialogButtonBox, QLabel
)
from core.mame_ini_manager import MAMEIniManager


class MAMESettingsDialog(QDialog):
    """
    Diálogo de Opciones del Core de MAME.
    Lee y escribe directamente sobre mame.ini a través de MAMEIniManager,
    exponiendo las opciones más comunes organizadas por pestañas.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Opciones de MAME (Core)")
        self.resize(560, 520)

        self.ini_manager = MAMEIniManager()
        # widget_key -> (tipo, widget)
        self._widgets = {}

        self._init_ui()
        self._load_values()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        if not self.ini_manager.ini_path.exists():
            warn = QLabel(
                "⚠ No se encontró mame.ini (configura la ruta de mame.exe primero)."
            )
            warn.setStyleSheet("color: #f59e0b; font-weight: bold;")
            layout.addWidget(warn)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tabs.addTab(self._build_video_tab(), "Video")
        self.tabs.addTab(self._build_screen_tab(), "Pantalla")
        self.tabs.addTab(self._build_sound_tab(), "Sonido")
        self.tabs.addTab(self._build_input_tab(), "Controles")
        self.tabs.addTab(self._build_misc_tab(), "Interfaz")
        self.tabs.addTab(self._build_performance_tab(), "Rendimiento")

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # --- Helpers de construcción de campos ---
    def _combo(self, key: str, options, form: QFormLayout, label: str):
        combo = QComboBox()
        combo.setEditable(True)
        combo.addItems(options)
        form.addRow(label, combo)
        self._widgets[key] = ("combo", combo)
        return combo

    def _check(self, key: str, label: str, form: QFormLayout):
        chk = QCheckBox(label)
        form.addRow("", chk)
        self._widgets[key] = ("bool", chk)
        return chk

    def _spin(self, key: str, minv: int, maxv: int, form: QFormLayout, label: str):
        spin = QSpinBox()
        spin.setRange(minv, maxv)
        form.addRow(label, spin)
        self._widgets[key] = ("int", spin)
        return spin

    def _dspin(self, key: str, minv: float, maxv: float, form: QFormLayout, label: str, step: float = 0.1):
        spin = QDoubleSpinBox()
        spin.setRange(minv, maxv)
        spin.setSingleStep(step)
        spin.setDecimals(2)
        form.addRow(label, spin)
        self._widgets[key] = ("float", spin)
        return spin

    def _line(self, key: str, form: QFormLayout, label: str):
        line = QLineEdit()
        form.addRow(label, line)
        self._widgets[key] = ("str", line)
        return line

    # --- Pestañas ---
    def _build_video_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._combo("video", ["auto", "gdi", "d3d", "bgfx", "opengl"], form, "Motor de video")
        self._check("window", "Iniciar en modo ventana", form)
        self._check("maximize", "Maximizar ventana al iniciar", form)
        self._check("waitvsync", "Esperar sincronismo vertical (VSync)", form)
        self._check("syncrefresh", "Sincronizar con la frecuencia de la pantalla", form)
        self._check("filter", "Filtrado de imagen (bilinear)", form)
        self._spin("prescale", 1, 3, form, "Prescalado")
        self._spin("numscreens", 1, 4, form, "Número de pantallas")
        return w

    def _build_screen_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._line("resolution", form, "Resolución (auto o AnchoxAlto@Hz)")
        self._line("aspect", form, "Relación de aspecto (auto o Ancho:Alto)")
        self._check("keepaspect", "Mantener relación de aspecto", form)
        self._check("rotate", "Permitir rotación de pantalla", form)
        self._check("flipx", "Invertir horizontalmente", form)
        self._check("flipy", "Invertir verticalmente", form)
        self._dspin("brightness", 0.2, 2.0, form, "Brillo")
        self._dspin("contrast", 0.2, 2.0, form, "Contraste")
        self._dspin("gamma", 0.1, 3.0, form, "Gamma")
        return w

    def _build_sound_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._combo("samplerate", ["11025", "22050", "44100", "48000", "96000"], form, "Frecuencia de muestreo")
        self._check("samples", "Usar samples de audio", form)
        self._spin("volume", -32, 0, form, "Volumen (dB)")
        return w

    def _build_input_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._check("mouse", "Habilitar ratón", form)
        self._check("joystick", "Habilitar joystick / mando", form)
        self._check("lightgun", "Habilitar pistola óptica", form)
        self._check("multikeyboard", "Múltiples teclados", form)
        self._check("multimouse", "Múltiples ratones", form)
        self._check("steadykey", "Modo tecla estable (Steadykey)", form)
        self._check("coin_lockout", "Bloqueo de monedero (coin lockout)", form)
        return w

    def _build_misc_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._check("autosave", "Autoguardar estado al salir", form)
        self._check("rewind", "Habilitar función de rebobinado", form)
        self._check("cheat", "Habilitar motor de trucos (cheats)", form)
        self._check("skip_gameinfo", "Omitir pantalla de información del juego", form)
        self._check("confirm_quit", "Confirmar antes de salir", form)
        self._check("ui_mouse", "Mostrar cursor del ratón en la UI", form)
        self._check("plugins", "Habilitar plugins Lua", form)
        return w

    def _build_performance_tab(self) -> QWidget:
        w = QWidget()
        form = QFormLayout(w)
        self._check("autoframeskip", "Frameskip automático", form)
        self._spin("frameskip", 0, 10, form, "Frameskip manual")
        self._check("throttle", "Limitar velocidad (throttle)", form)
        self._check("sleep", "Ceder CPU en tiempo libre (sleep)", form)
        self._line("numprocessors", form, "Núm. de procesadores (auto o número)")
        return w

    # --- Carga / Guardado ---
    def _load_values(self):
        for key, (kind, widget) in self._widgets.items():
            if kind == "bool":
                widget.setChecked(self.ini_manager.get_bool(key))
            elif kind == "int":
                try:
                    widget.setValue(int(self.ini_manager.get(key, "0") or 0))
                except ValueError:
                    widget.setValue(0)
            elif kind == "float":
                try:
                    widget.setValue(float(self.ini_manager.get(key, "0") or 0))
                except ValueError:
                    widget.setValue(0.0)
            elif kind in ("str", "combo"):
                value = self.ini_manager.get(key, "")
                if kind == "combo":
                    widget.setCurrentText(value)
                else:
                    widget.setText(value)

    def _on_save(self):
        for key, (kind, widget) in self._widgets.items():
            if kind == "bool":
                self.ini_manager.set_bool(key, widget.isChecked())
            elif kind == "int":
                self.ini_manager.set(key, str(widget.value()))
            elif kind == "float":
                self.ini_manager.set(key, str(widget.value()))
            elif kind in ("str", "combo"):
                text = widget.currentText() if kind == "combo" else widget.text()
                self.ini_manager.set(key, text.strip())

        if self.ini_manager.save():
            QMessageBox.information(self, "Opciones guardadas", "mame.ini se actualizó correctamente.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar mame.ini. Verifica la ruta de mame.exe.")
