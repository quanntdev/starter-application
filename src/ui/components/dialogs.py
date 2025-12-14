"""Custom dialog components."""
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
import qtawesome as qta


class ConfirmDeleteDialog(QDialog):
    """Custom styled confirmation dialog for delete actions."""
    
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(400)
        self.init_ui(title, message)
        self.apply_theme()
    
    def init_ui(self, title, message):
        """Initialize dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Icon + Title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Warning icon
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.exclamation-triangle', color='#ffc107').pixmap(32, 32))
        header_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #e0e0e0;")
        header_layout.addWidget(title_label, 1)
        
        layout.addLayout(header_layout)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 14px; color: #a0a0a0; padding: 10px 0;")
        layout.addWidget(message_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        # Cancel button
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setMinimumWidth(100)
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)
        
        # Delete button
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setMinimumWidth(100)
        self.btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete.setProperty("class", "danger")
        self.btn_delete.clicked.connect(self.accept)
        button_layout.addWidget(self.btn_delete)
        
        layout.addLayout(button_layout)
    
    def apply_theme(self):
        """Apply dark theme to dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 12px;
            }
            
            QPushButton {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            
            QPushButton[class="danger"] {
                background-color: #dc3545;
                color: white;
            }
            
            QPushButton[class="danger"]:hover {
                background-color: #bb2d3b;
            }
        """)

