"""Rules tab for application permissions and settings."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QMessageBox, QPushButton
)
from PySide6.QtCore import Qt
import ctypes
import sys


class RulesTab(QWidget):
    """Rules tab with application permission settings."""
    
    def __init__(self, config_store, translator, parent=None):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        self.init_ui()
    
    def init_ui(self):
        """Initialize tab UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title
        self.title_label = QLabel(self.translator.t("admin.rules.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(self.title_label)
        
        layout.addSpacing(20)
        
        # Rules card
        card = QWidget()
        card.setProperty("class", "card")
        card.setMaximumWidth(600)
        card_layout = QVBoxLayout(card)
        
        # Admin privilege checkbox
        self.admin_checkbox = QCheckBox(self.translator.t("admin.rules.run_as_admin"))
        self.admin_checkbox.setStyleSheet("font-size: 14px; padding: 8px;")
        
        # Check if currently running as admin OR user preference is set
        is_admin = self.is_running_as_admin()
        require_admin = self.config_store.get_require_admin()
        self.admin_checkbox.setChecked(is_admin or require_admin)
        
        # Connect signal
        self.admin_checkbox.stateChanged.connect(self.on_admin_changed)
        
        card_layout.addWidget(self.admin_checkbox)
        
        # Description
        desc_label = QLabel(self.translator.t("admin.rules.run_as_admin_desc"))
        desc_label.setStyleSheet("color: #a0a0a0; font-size: 12px; padding-left: 30px;")
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)
        
        layout.addWidget(card)
        
        # Status info
        layout.addSpacing(20)
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        self.update_status_label()
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def is_running_as_admin(self) -> bool:
        """Check if the application is running with administrator privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def on_admin_changed(self, state):
        """Handle admin privilege checkbox change."""
        wants_admin = state == Qt.CheckState.Checked.value
        is_admin = self.is_running_as_admin()
        
        if wants_admin and not is_admin:
            # Save preference BEFORE restart
            self.config_store.set_require_admin(True)
            
            # Request to run as admin
            reply = QMessageBox.question(
                self,
                self.translator.t("admin.rules.restart_title"),
                self.translator.t("admin.rules.restart_message"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.restart_as_admin()
            else:
                # User declined, uncheck and remove preference
                self.admin_checkbox.setChecked(False)
                self.config_store.set_require_admin(False)
        
        elif not wants_admin and is_admin:
            # User wants to disable auto-admin
            self.config_store.set_require_admin(False)
            QMessageBox.information(
                self,
                self.translator.t("admin.rules.info_title"),
                self.translator.t("admin.rules.disabled_admin_message")
            )
            # Keep it checked since we're currently admin
            self.admin_checkbox.setChecked(True)
        
        elif not wants_admin and not is_admin:
            # User unchecked and we're not admin - just save preference
            self.config_store.set_require_admin(False)
        
        self.update_status_label()
    
    def restart_as_admin(self):
        """Restart the application with administrator privileges."""
        try:
            # Get the main script path
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                script = sys.executable
            else:
                # Running as Python script
                script = sys.argv[0]
            
            # Request UAC elevation
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                sys.executable, 
                f'"{script}"', 
                None, 
                1
            )
            
            # Exit current instance
            QMessageBox.information(
                self,
                self.translator.t("admin.rules.restarting_title"),
                self.translator.t("admin.rules.restarting_message")
            )
            sys.exit(0)
        except Exception as e:
            QMessageBox.warning(
                self,
                self.translator.t("admin.rules.error_title"),
                f"{self.translator.t('admin.rules.error_message')}: {e}"
            )
            self.admin_checkbox.setChecked(False)
    
    def update_status_label(self):
        """Update the status label."""
        is_admin = self.is_running_as_admin()
        if is_admin:
            status_text = self.translator.t("admin.rules.status_admin")
            self.status_label.setStyleSheet("color: #198754; font-size: 12px; font-weight: 500;")
        else:
            status_text = self.translator.t("admin.rules.status_normal")
            self.status_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        
        self.status_label.setText(f"ℹ️ {status_text}")
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.title_label.setText(self.translator.t("admin.rules.title"))
        self.admin_checkbox.setText(self.translator.t("admin.rules.run_as_admin"))
        
        # Find and update description label
        card = self.findChild(QWidget)
        if card:
            labels = card.findChildren(QLabel)
            if len(labels) > 0:
                labels[0].setText(self.translator.t("admin.rules.run_as_admin_desc"))
        
        self.update_status_label()

