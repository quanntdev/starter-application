"""Trigger tab for autostart configuration."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCheckBox, QMessageBox, QPushButton
)
from PySide6.QtCore import Qt
import ctypes

from services.startup_service import StartupService


class TriggerTab(QWidget):
    """Trigger tab with autostart toggle."""
    
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
        self.title_label = QLabel(self.translator.t("admin.trigger.title"))
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
        
        # Settings card
        card = QWidget()
        card.setProperty("class", "card")
        card.setMaximumWidth(600)
        card_layout = QVBoxLayout(card)
        
        # Autostart checkbox
        self.autostart_checkbox = QCheckBox(
            self.translator.t("admin.trigger.autostart_app")
        )
        self.autostart_checkbox.stateChanged.connect(self.on_autostart_changed)
        
        # Disable checkbox if not admin
        if not is_admin:
            self.autostart_checkbox.setEnabled(False)
            self.autostart_checkbox.setToolTip(self.translator.t("admin.trigger.disabled_tooltip"))
        
        card_layout.addWidget(self.autostart_checkbox)
        
        card_layout.addSpacing(10)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
        self.status_label.setWordWrap(True)
        card_layout.addWidget(self.status_label)
        
        self.main_layout.addWidget(card)
        self.main_layout.addStretch()
    
    def load_status(self):
        """Load current autostart status."""
        enabled = self.startup_service.is_enabled()
        self.autostart_checkbox.setChecked(enabled)
        self.update_status_label(enabled)
    
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
                self.update_status_label(True)
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
                self.update_status_label(False)
            else:
                self.autostart_checkbox.setChecked(True)
                QMessageBox.warning(
                    self,
                    self.translator.t("admin.trigger.error_title"),
                    self.translator.t("admin.trigger.disable_failed")
                )
    
    def update_status_label(self, enabled):
        """Update status label."""
        if enabled:
            self.status_label.setText(
                self.translator.t("admin.trigger.status_enabled")
            )
            self.status_label.setStyleSheet("color: #198754; font-size: 12px;")
        else:
            self.status_label.setText(
                self.translator.t("admin.trigger.status_disabled")
            )
            self.status_label.setStyleSheet("color: #a0a0a0; font-size: 12px;")
    
    def refresh_ui(self):
        """Refresh UI after language change or admin status change."""
        # Rebuild entire UI to reflect current admin status
        self.rebuild_ui()
        # Reload autostart status
        self.load_status()

