"""Modern dark theme stylesheet for the application."""

DARK_THEME = """
/* Global styles */
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}

/* Main window */
QMainWindow {
    background-color: #1e1e1e;
}

/* Sidebar */
#sidebar {
    background-color: #252525;
    border-right: 1px solid #3a3a3a;
}

/* Sidebar buttons */
#sidebar QPushButton {
    background-color: transparent;
    color: #e0e0e0;
    border: none;
    border-radius: 0px;
    padding: 12px 16px;
    text-align: left;
    margin: 2px 8px;
}

#sidebar QPushButton:hover {
    background-color: #2d2d2d;
}

#sidebar QPushButton:checked {
    background-color: #0d6efd;
    color: white;
}

/* Content area */
#content {
    background-color: #1e1e1e;
}

/* Tab widget */
QTabWidget::pane {
    border: none;
    background-color: #1e1e1e;
}

QTabBar::tab {
    background-color: transparent;
    color: #a0a0a0;
    border: none;
    border-radius: 0px;
    padding: 10px 20px;
    margin-right: 4px;
}

QTabBar::tab:hover {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QTabBar::tab:selected {
    background-color: transparent;
    color: #0d6efd;
    border-bottom: 2px solid #0d6efd;
}

/* Cards */
.card {
    background-color: transparent;
    border-radius: 12px;
    border: 1px solid #3a3a3a;
    padding: 20px;
}

/* Input fields */
QLineEdit, QTextEdit {
    background-color: #2d2d2d;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    padding: 8px 12px;
    color: #e0e0e0;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #0d6efd;
}

/* Buttons */
QPushButton {
    background-color: #0d6efd;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #0b5ed7;
}

QPushButton:pressed {
    background-color: #0a58ca;
}

QPushButton:disabled {
    background-color: #3a3a3a;
    color: #6c6c6c;
}

/* Secondary button */
QPushButton[class="secondary"] {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QPushButton[class="secondary"]:hover {
    background-color: #3a3a3a;
}

/* Danger button */
QPushButton[class="danger"] {
    background-color: #dc3545;
}

QPushButton[class="danger"]:hover {
    background-color: #bb2d3b;
}

/* Icon button */
QPushButton[class="icon"] {
    background-color: transparent;
    padding: 6px;
    border-radius: 6px;
}

QPushButton[class="icon"]:hover {
    background-color: #3a3a3a;
}

/* ComboBox */
QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    padding: 8px 12px;
    color: #e0e0e0;
}

QComboBox:hover {
    border: 1px solid #0d6efd;
}

QComboBox::drop-down {
    border: none;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    border: 1px solid #3a3a3a;
    selection-background-color: #0d6efd;
    color: #e0e0e0;
}

/* CheckBox */
QCheckBox {
    color: #e0e0e0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #3a3a3a;
    background-color: #2d2d2d;
}

QCheckBox::indicator:hover {
    border-color: #0d6efd;
}

QCheckBox::indicator:checked {
    background-color: #0d6efd;
    border-color: #0d6efd;
    image: url(none);
}

/* RadioButton */
QRadioButton {
    color: #e0e0e0;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #3a3a3a;
    background-color: #2d2d2d;
}

QRadioButton::indicator:hover {
    border-color: #0d6efd;
}

QRadioButton::indicator:checked {
    background-color: #0d6efd;
    border-color: #0d6efd;
}

/* ScrollBar */
QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #3a3a3a;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4a4a4a;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
}

QScrollBar:horizontal {
    background-color: #1e1e1e;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #3a3a3a;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #4a4a4a;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    border: none;
    background: none;
}

/* List widget */
QListWidget {
    background-color: #2d2d2d;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    padding: 4px;
}

QListWidget::item {
    background-color: transparent;
    border-radius: 6px;
    padding: 8px;
    color: #e0e0e0;
}

QListWidget::item:hover {
    background-color: #3a3a3a;
}

QListWidget::item:selected {
    background-color: #0d6efd;
    color: white;
}

/* Label */
QLabel {
    color: #e0e0e0;
}

/* Badge */
QLabel[class="badge"] {
    background-color: #0d6efd;
    color: white;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 12px;
}

QLabel[class="badge-browser"] {
    background-color: #0dcaf0;
}

QLabel[class="badge-app"] {
    background-color: #6c757d;
}

QLabel[class="badge-working"] {
    background-color: #198754;
}
"""


def apply_theme(app):
    """Apply the dark theme to the application."""
    app.setStyleSheet(DARK_THEME)

