DARK_THEME_QSS = """
/* Estilo Base MAMEXrd Modern Dark Theme */

QMainWindow {
    background-color: #12141c;
    color: #e1e4ed;
}

QWidget {
    font-family: 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    font-size: 13px;
    color: #e1e4ed;
}

/* Panel Lateral y Contenedores */
QFrame#sidebarFrame, QFrame#mediaFrame {
    background-color: #1a1d29;
    border-radius: 8px;
    border: 1px solid #282c3f;
}

/* Barra de Búsqueda */
QLineEdit#searchBar {
    background-color: #202436;
    border: 1px solid #333852;
    border-radius: 6px;
    padding: 8px 14px;
    color: #ffffff;
    font-size: 14px;
}

QLineEdit#searchBar:focus {
    border: 1px solid #6366f1;
    background-color: #252a3f;
}

/* Botones Principales */
QPushButton {
    background-color: #6366f1;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #4f46e5;
}

QPushButton:pressed {
    background-color: #4338ca;
}

QPushButton#launchBtn {
    background-color: #10b981;
    font-size: 15px;
    padding: 10px 24px;
}

QPushButton#launchBtn:hover {
    background-color: #059669;
}

/* Tabla de Juegos */
QTableView {
    background-color: #161925;
    gridline-color: #24283b;
    border: 1px solid #282c3f;
    border-radius: 8px;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
    alternate-background-color: #1a1d2d;
}

QHeaderView::section {
    background-color: #1f2334;
    color: #94a3b8;
    padding: 8px;
    border: none;
    border-bottom: 2px solid #2d3248;
    font-weight: bold;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #282c3f;
    background-color: #1a1d29;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #161823;
    color: #94a3b8;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #1a1d29;
    color: #6366f1;
    border-bottom: 2px solid #6366f1;
    font-weight: bold;
}

/* Scrollbars */
QScrollBar:vertical {
    background: #161925;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #333852;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #4f46e5;
}
"""
