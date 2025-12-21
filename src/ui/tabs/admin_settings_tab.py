"""Admin Settings tab combining Trigger and Rules."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt
import ctypes
import sys

from services.startup_service import StartupService


class AdminSettingsTab(QWidget):
    """Admin Settings tab combining Trigger and Rules functionality."""
    
    def __init__(self, config_store, translator, parent=None):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        self.startup_service = StartupService()
        self.init_ui()
        self.load_status()
    
    def is_admin(self):
        """Check if running with administrator privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def init_ui(self):
        """Initialize tab UI."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.rebuild_ui()
    
    def rebuild_ui(self):
        """Rebuild UI based on current admin status."""
        # Clear existing widgets
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Title
        self.title_label = QLabel(self.translator.t("admin.settings.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        self.main_layout.addWidget(self.title_label)
        
        self.main_layout.addSpacing(20)
        
        # Admin privilege warning (if not admin)
        is_admin = self.is_admin()
        if not is_admin:
            warning_widget = QWidget()
            warning_widget.setStyleSheet("""
                QWidget {
                    background-color: #664d03;
                    border: 1px solid #997404;
                    border-radius: 6px;
                    padding: 12px;
                }
            """)
            warning_layout = QVBoxLayout(warning_widget)
            
            warning_icon_label = QLabel("⚠️ " + self.translator.t("admin.trigger.warning_title"))
            warning_icon_label.setStyleSheet("color: #ffda6a; font-weight: 600; font-size: 14px;")
            warning_layout.addWidget(warning_icon_label)
            
            warning_text = QLabel(self.translator.t("admin.trigger.warning_message"))
            warning_text.setStyleSheet("color: #ffda6a; font-size: 12px;")
            warning_text.setWordWrap(True)
            warning_layout.addWidget(warning_text)
            
            self.main_layout.addWidget(warning_widget)
            self.main_layout.addSpacing(10)
        
        # Trigger Section Card
        trigger_card = QWidget()
        trigger_card.setProperty("class", "card")
        trigger_card.setMaximumWidth(600)
        trigger_card_layout = QVBoxLayout(trigger_card)
        
        # Trigger section title
        trigger_title = QLabel(self.translator.t("admin.trigger.title"))
        trigger_title.setStyleSheet("font-size: 16px; font-weight: 600; margin-bottom: 10px;")
        trigger_card_layout.addWidget(trigger_title)
        
        # Autostart checkbox
        self.autostart_checkbox = QCheckBox(
            self.translator.t("admin.trigger.autostart_app")
        )
        self.autostart_checkbox.stateChanged.connect(self.on_autostart_changed)
        
        # Disable checkbox if not admin
        if not is_admin:
            self.autostart_checkbox.setEnabled(False)
            self.autostart_checkbox.setToolTip(self.translator.t("admin.trigger.disabled_tooltip"))
        
        trigger_card_layout.addWidget(self.autostart_checkbox)
        
        trigger_card_layout.addSpacing(10)
        
        # Trigger status label
        self.trigger_status_label = QLabel("")
        self.trigger_status_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        self.trigger_status_label.setWordWrap(True)
        trigger_card_layout.addWidget(self.trigger_status_label)
        
        self.main_layout.addWidget(trigger_card)
        
        self.main_layout.addSpacing(20)
        
        # Rules Section Card
        rules_card = QWidget()
        rules_card.setProperty("class", "card")
        rules_card.setMaximumWidth(600)
        rules_card_layout = QVBoxLayout(rules_card)
        
        # Rules section title
        rules_title = QLabel(self.translator.t("admin.rules.title"))
        rules_title.setStyleSheet("font-size: 16px; font-weight: 600; margin-bottom: 10px;")
        rules_card_layout.addWidget(rules_title)
        
        # Admin privilege checkbox
        self.admin_checkbox = QCheckBox(self.translator.t("admin.rules.run_as_admin"))
        self.admin_checkbox.setStyleSheet("font-size: 14px; padding: 8px;")
        
        # Check if currently running as admin OR user preference is set
        require_admin = self.config_store.get_require_admin()
        self.admin_checkbox.setChecked(is_admin or require_admin)
        
        # Connect signal
        self.admin_checkbox.stateChanged.connect(self.on_admin_changed)
        
        rules_card_layout.addWidget(self.admin_checkbox)
        
        # Description
        self.rules_desc_label = QLabel(self.translator.t("admin.rules.run_as_admin_desc"))
        self.rules_desc_label.setStyleSheet("color: #a0a0a0; font-size: 12px; padding-left: 30px;")
        self.rules_desc_label.setWordWrap(True)
        rules_card_layout.addWidget(self.rules_desc_label)
        
        self.main_layout.addWidget(rules_card)
        
        # Status info
        self.main_layout.addSpacing(20)
        self.rules_status_label = QLabel()
        self.rules_status_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        self.update_rules_status_label()
        self.main_layout.addWidget(self.rules_status_label)
        
        self.main_layout.addStretch()
    
    def load_status(self):
        """Load current autostart status."""
        enabled = self.startup_service.is_enabled()
        self.autostart_checkbox.setChecked(enabled)
        self.update_trigger_status_label(enabled)
    
    def on_autostart_changed(self, state):
        """Handle autostart checkbox change."""
        enabled = (state == Qt.CheckState.Checked.value)
        
        # Double check admin privileges (should be disabled if not admin)
        if not self.is_admin():
            self.autostart_checkbox.setChecked(not enabled)
            return
        
        if enabled:
            success = self.startup_service.enable()
            if success:
                self.config_store.set_autostart_enabled(True)
                self.update_trigger_status_label(True)
            else:
                self.autostart_checkbox.setChecked(False)
                QMessageBox.warning(
                    self,
                    self.translator.t("admin.trigger.error_title"),
                    self.translator.t("admin.trigger.enable_failed")
                )
        else:
            success = self.startup_service.disable()
            if success:
                self.config_store.set_autostart_enabled(False)
                self.update_trigger_status_label(False)
            else:
                self.autostart_checkbox.setChecked(True)
                QMessageBox.warning(
                    self,
                    self.translator.t("admin.trigger.error_title"),
                    self.translator.t("admin.trigger.disable_failed")
                )
    
    def update_trigger_status_label(self, enabled):
        """Update trigger status label."""
        if enabled:
            self.trigger_status_label.setText(
                self.translator.t("admin.trigger.status_enabled")
            )
            self.trigger_status_label.setStyleSheet("color: #198754; font-size: 12px;")
        else:
            self.trigger_status_label.setText(
                self.translator.t("admin.trigger.status_disabled")
            )
            self.trigger_status_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
    
    def on_admin_changed(self, state):
        """Handle admin privilege checkbox change."""
        wants_admin = state == Qt.CheckState.Checked.value
        is_admin = self.is_admin()
        
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
        
        self.update_rules_status_label()
    
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
    
    def update_rules_status_label(self):
        """Update the rules status label."""
        is_admin = self.is_admin()
        if is_admin:
            status_text = self.translator.t("admin.rules.status_admin")
            self.rules_status_label.setStyleSheet("color: #198754; font-size: 12px; font-weight: 500;")
        else:
            status_text = self.translator.t("admin.rules.status_normal")
            self.rules_status_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        
        self.rules_status_label.setText(f"ℹ️ {status_text}")
    
    def refresh_ui(self):
        """Refresh UI after language change or admin status change."""
        # Rebuild entire UI to reflect current admin status
        self.rebuild_ui()
        # Reload autostart status
        self.load_status()

