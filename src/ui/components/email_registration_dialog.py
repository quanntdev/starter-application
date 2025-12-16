"""Email registration blocking dialog."""
import re
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QWidget
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QKeyEvent, QFocusEvent
import qtawesome as qta


class EmailRegistrationDialog(QDialog):
    """Blocking email registration dialog - cannot be closed until email is submitted."""
    
    email_submitted = Signal(str)  # Signal emitted when email is successfully submitted
    
    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        
        self.setWindowTitle(self.translator.t("email_registration.title"))
        self.setModal(True)
        self.setWindowFlags(
            Qt.WindowType.Dialog |
            Qt.WindowType.MSWindowsFixedSizeDialogHint |
            Qt.WindowType.CustomizeWindowHint
        )
        # Remove close button
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        
        self.setFixedSize(500, 450)
        self.init_ui()
        self.apply_theme()
        
        # Focus on email input
        QTimer.singleShot(100, lambda: self.email_input.setFocus())
    
    def init_ui(self):
        """Initialize dialog UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)
        
        # Title
        self.title_label = QLabel(self.translator.t("email_registration.title"))
        self.title_label.setStyleSheet("font-size: 20px; font-weight: 600; color: #e0e0e0;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Description
        self.description_label = QLabel(self.translator.t("email_registration.description"))
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("font-size: 14px; color: #a0a0a0; line-height: 1.6;")
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.description_label)
        
        layout.addSpacing(10)
        
        # Email input
        self.email_label = QLabel(self.translator.t("email_registration.email_label"))
        self.email_label.setStyleSheet("font-size: 14px; color: #e0e0e0; font-weight: 500;")
        layout.addWidget(self.email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText(self.translator.t("email_registration.email_placeholder"))
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 2px solid #3a3a3a;
                border-radius: 8px;
                padding: 12px 15px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4a9eff;
                background-color: #333333;
            }
            QLineEdit:invalid {
                border-color: #dc3545;
            }
        """)
        self.email_input.returnPressed.connect(self.on_submit)
        self.email_input.textChanged.connect(self.validate_email)
        layout.addWidget(self.email_input)
        
        # Error message label (initially hidden)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("font-size: 12px; color: #dc3545; padding: 5px 0;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        layout.addStretch()
        
        # Submit button
        self.submit_button = QPushButton(self.translator.t("email_registration.submit_button"))
        self.submit_button.setMinimumHeight(45)
        self.submit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #4a9eff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 30px;
                font-size: 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3a8eef;
            }
            QPushButton:pressed {
                background-color: #2a7edf;
            }
            QPushButton:disabled {
                background-color: #3a3a3a;
                color: #666666;
            }
        """)
        self.submit_button.clicked.connect(self.on_submit)
        self.submit_button.setEnabled(False)  # Initially disabled until valid email
        layout.addWidget(self.submit_button)
        
        # Loading indicator (initially hidden)
        self.loading_label = QLabel()
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.hide()
        layout.addWidget(self.loading_label)
    
    def apply_theme(self):
        """Apply dark theme to dialog."""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 12px;
            }
        """)
    
    def validate_email(self, text: str):
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(email_pattern, text.strip()))
        
        self.submit_button.setEnabled(is_valid and len(text.strip()) > 0)
        
        if text.strip() and not is_valid:
            self.error_label.setText(self.translator.t("email_registration.error_invalid"))
            self.error_label.show()
        else:
            self.error_label.hide()
    
    def on_submit(self):
        """Handle submit button click."""
        email = self.email_input.text().strip()
        
        if not email:
            self.error_label.setText(self.translator.t("email_registration.error_required"))
            self.error_label.show()
            return
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            self.error_label.setText(self.translator.t("email_registration.error_invalid"))
            self.error_label.show()
            return
        
        # Disable input and button during submission
        self.email_input.setEnabled(False)
        self.submit_button.setEnabled(False)
        
        # Show loading indicator
        self.loading_label.setText(self.translator.t("email_registration.submitting"))
        self.loading_label.setStyleSheet("font-size: 14px; color: #4a9eff;")
        self.loading_label.show()
        self.error_label.hide()
        
        # Emit signal to parent to handle submission
        self.email_submitted.emit(email)
    
    def show_success(self):
        """Show success message."""
        self.loading_label.setText(self.translator.t("email_registration.success"))
        self.loading_label.setStyleSheet("font-size: 14px; color: #28a745;")
    
    def show_error(self, error_message: str):
        """Show error message and re-enable input."""
        self.email_input.setEnabled(True)
        self.submit_button.setEnabled(True)
        self.loading_label.hide()
        # Format error message with translation
        error_text = self.translator.t("email_registration.error_generic", error=error_message)
        self.error_label.setText(error_text)
        self.error_label.show()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Override key press to prevent ESC from closing dialog."""
        if event.key() == Qt.Key.Key_Escape:
            # Ignore ESC key - dialog cannot be closed
            event.ignore()
            return
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Override close event to prevent closing."""
        # Only allow closing if email is registered (handled by parent)
        event.ignore()

