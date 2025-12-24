"""Settings tab for configuring startup trigger."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QComboBox, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
import qtawesome as qta
import time

from services.launcher_service import LauncherService
from services.startup_service import StartupService
from services.logging_service import get_logging_service
from models.config_models import StarterSettings


class SettingsTab(QWidget):
    """Settings tab with trigger and delay options."""
    
    def __init__(self, config_store, translator, parent=None, is_startup_launch=False):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        self.launcher = LauncherService()
        self.startup_service = StartupService()
        self.logging_service = get_logging_service()
        self.startup_processed = False
        self.is_startup_launch = is_startup_launch
        self.init_ui()
        self.load_settings()
        
        # Check if we should trigger on startup (delayed)
        # Only trigger if app was started from Windows boot, not manually
        QTimer.singleShot(1000, self.check_startup_trigger)
    
    def init_ui(self):
        """Initialize tab UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Title
        self.title_label = QLabel(self.translator.t("starter_settings.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(self.title_label)
        
        # Description
        self.description_label = QLabel(self.translator.t("starter_settings.description"))
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("font-size: 13px; color: #a0a0a0; margin-top: 8px;")
        layout.addWidget(self.description_label)
        
        layout.addSpacing(20)
        
        # Settings card
        card = QWidget()
        card.setProperty("class", "card")
        card.setMaximumWidth(600)
        card_layout = QVBoxLayout(card)
        
        # Autostart status info
        self.autostart_status_label = QLabel()
        self.autostart_status_label.setWordWrap(True)
        self.autostart_status_label.setStyleSheet("font-size: 12px; padding: 10px; border-radius: 6px; margin-bottom: 10px;")
        self.update_autostart_status()
        card_layout.addWidget(self.autostart_status_label)
        
        card_layout.addSpacing(10)
        
        # Trigger toggle
        self.trigger_checkbox = QCheckBox(
            self.translator.t("starter_settings.trigger_selected")
        )
        self.trigger_checkbox.stateChanged.connect(self.on_trigger_changed)
        card_layout.addWidget(self.trigger_checkbox)
        
        card_layout.addSpacing(20)
        
        # Delay dropdown
        delay_layout = QHBoxLayout()
        delay_label = QLabel(self.translator.t("starter_settings.delay_seconds"))
        delay_layout.addWidget(delay_label)
        
        self.delay_combo = QComboBox()
        self.delay_combo.addItems(["1", "2", "3", "4", "5", "10", "15", "20"])
        self.delay_combo.setMaximumWidth(100)
        delay_layout.addWidget(self.delay_combo)
        delay_layout.addStretch()
        
        card_layout.addLayout(delay_layout)
        
        card_layout.addSpacing(20)
        
        # Save button with icon
        self.save_button = QPushButton("  " + self.translator.t("starter_settings.save"))
        self.save_button.setIcon(qta.icon('fa5s.save', color='white'))
        self.save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_button.clicked.connect(self.on_save)
        self.save_button.setMaximumWidth(150)
        card_layout.addWidget(self.save_button)
        
        layout.addWidget(card)
        layout.addStretch()
    
    def load_settings(self):
        """Load settings from config."""
        settings = self.config_store.get_starter_settings()
        
        # Always default to True (migrate old configs that have False)
        # This ensures checkbox is always checked by default
        if not settings.trigger_selected_on_startup:
            settings.trigger_selected_on_startup = True
            self.config_store.update_starter_settings(settings)
        
        # Always set checkbox to True (default behavior)
        self.trigger_checkbox.setChecked(True)
        
        # Set delay combo
        delay_str = str(settings.delay_seconds)
        index = self.delay_combo.findText(delay_str)
        if index >= 0:
            self.delay_combo.setCurrentIndex(index)
        else:
            # Default to 1 second if not found
            index = self.delay_combo.findText("1")
            if index >= 0:
                self.delay_combo.setCurrentIndex(index)
        
        # Update autostart status
        self.update_autostart_status()
    
    def update_autostart_status(self):
        """Update autostart status label."""
        autostart_enabled = self.startup_service.is_enabled()
        
        if autostart_enabled:
            self.autostart_status_label.setText(
                "✓ Autostart is enabled. The app will launch when Windows starts.\n"
                "Selected favourites will be launched automatically after the delay."
            )
            self.autostart_status_label.setStyleSheet(
                "font-size: 12px; padding: 10px; border-radius: 6px; margin-bottom: 10px; "
                "background-color: rgba(25, 135, 84, 0.15); color: #198754; border: 1px solid rgba(25, 135, 84, 0.3);"
            )
        else:
            self.autostart_status_label.setText(
                "⚠ Autostart is not enabled!\n"
                "To enable auto-launch of favourites on Windows startup, please go to:\n"
                "Admin Settings → Settings → Enable 'Always start this app when Windows starts'"
            )
            self.autostart_status_label.setStyleSheet(
                "font-size: 12px; padding: 10px; border-radius: 6px; margin-bottom: 10px; "
                "background-color: rgba(255, 193, 7, 0.15); color: #ffc107; border: 1px solid rgba(255, 193, 7, 0.3);"
            )
    
    def on_trigger_changed(self, state):
        """Handle trigger checkbox change - auto-save."""
        settings = StarterSettings(
            trigger_selected_on_startup=(state == Qt.CheckState.Checked),
            delay_seconds=int(self.delay_combo.currentText())
        )
        self.config_store.update_starter_settings(settings)
    
    def on_save(self):
        """Handle save button click."""
        settings = StarterSettings(
            trigger_selected_on_startup=self.trigger_checkbox.isChecked(),
            delay_seconds=int(self.delay_combo.currentText())
        )
        
        self.config_store.update_starter_settings(settings)
        
        QMessageBox.information(
            self,
            "Saved",
            self.translator.t("common.messages.saved")
        )
    
    def _is_windows_boot_recent(self) -> bool:
        """
        Check if app was started from Windows boot (not manually).
        
        Returns:
            True if app was started from Windows boot, False otherwise
        """
        # Check if app was started with --startup argument
        if self.is_startup_launch:
            self.logging_service.info("App was started from Windows boot (--startup argument detected)")
            return True
        
        self.logging_service.info("App was not started from Windows boot (no --startup argument)")
        return False
    
    def check_startup_trigger(self):
        """Check if we should launch selected favourites on startup.
        Only triggers if app was started from Windows boot, not manually opened.
        """
        self.logging_service.info("=" * 60)
        self.logging_service.info("check_startup_trigger() called")
        self.logging_service.info("=" * 60)
        
        if self.startup_processed:
            self.logging_service.info("Startup already processed, skipping...")
            return
        
        # Check if autostart is enabled
        autostart_enabled = self.startup_service.is_enabled()
        self.logging_service.info(f"Autostart enabled: {autostart_enabled}")
        
        if not autostart_enabled:
            self.logging_service.warning("Autostart is not enabled! Please enable it in Admin Settings → Settings")
        
        # Check if app was started from Windows boot (not manually)
        if not self._is_windows_boot_recent():
            self.logging_service.info("App was not started from Windows boot, skipping auto-launch...")
            return
        
        # Get settings and ensure trigger is enabled (migrate old configs)
        settings = self.config_store.get_starter_settings()
        self.logging_service.info(f"trigger_selected_on_startup (before migration): {settings.trigger_selected_on_startup}")
        
        # Force enable trigger if it's False (migrate old configs)
        if not settings.trigger_selected_on_startup:
            self.logging_service.info("Migrating trigger_selected_on_startup from False to True...")
            settings.trigger_selected_on_startup = True
            self.config_store.update_starter_settings(settings)
            self.logging_service.info("Migration complete: trigger_selected_on_startup is now True")
        
        self.logging_service.info(f"trigger_selected_on_startup (after migration): {settings.trigger_selected_on_startup}")
        self.logging_service.info(f"delay_seconds: {settings.delay_seconds}")
        
        # Double-check after migration
        settings = self.config_store.get_starter_settings()
        if not settings.trigger_selected_on_startup:
            self.logging_service.warning("Trigger is still disabled after migration, skipping...")
            return
        
        self.startup_processed = True
        
        # Get selected favourites
        favourites = self.config_store.get_favourites()
        self.logging_service.info(f"Total favourites: {len(favourites)}")
        selected_favourites = [f for f in favourites if f.selected]
        self.logging_service.info(f"Selected favourites: {len(selected_favourites)}")
        
        for fav in selected_favourites:
            self.logging_service.info(f"  - {fav.name} (kind: {fav.kind}, selected: {fav.selected}, lnk_path: {fav.lnk_path})")
        
        if not selected_favourites:
            self.logging_service.warning("No selected favourites, skipping...")
            return
        
        # Wait for delay
        delay = settings.delay_seconds
        self.logging_service.info(f"Scheduling launch after {delay} seconds...")
        
        # Use QTimer for non-blocking delay
        QTimer.singleShot(delay * 1000, lambda: self.launch_favourites(selected_favourites))
    
    def launch_favourites(self, favourites):
        """Launch selected favourites."""
        self.logging_service.info(f"Starting to launch {len(favourites)} favourites...")
        for i, fav in enumerate(favourites):
            try:
                self.logging_service.info(f"[{i+1}/{len(favourites)}] Launching {fav.name} (kind: {fav.kind}, selected: {fav.selected})...")
                self.logging_service.info(f"  lnk_path: {fav.lnk_path}")
                
                success = self.launcher.test_favourite(fav)
                if not success:
                    self.logging_service.error(f"  ❌ Failed to launch {fav.name}")
                else:
                    self.logging_service.info(f"  ✅ Successfully launched {fav.name}")
                
                # Delay between launches to avoid overwhelming the system
                # Longer delay for startup to ensure apps have time to initialize
                if i < len(favourites) - 1:  # Don't delay after the last one
                    self.logging_service.info(f"  Waiting 1.5 seconds before next launch...")
                    time.sleep(1.5)  # Increased delay for startup
            except Exception as e:
                self.logging_service.error(f"  ❌ Error launching {fav.name}: {e}", exc_info=True)
        
        self.logging_service.info(f"Finished launching favourites.")
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.title_label.setText(self.translator.t("starter_settings.title"))
        self.description_label.setText(self.translator.t("starter_settings.description"))
        self.trigger_checkbox.setText(self.translator.t("starter_settings.trigger_selected"))
        self.save_button.setText("  " + self.translator.t("starter_settings.save"))

