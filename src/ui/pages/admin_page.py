"""Admin settings page with Settings and Logs tabs."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from ui.tabs.admin_settings_tab import AdminSettingsTab
from ui.tabs.logs_tab import LogsTab


class AdminPage(QWidget):
    """Admin settings page with Settings and Logs tabs."""
    
    def __init__(self, config_store, translator, main_window, parent=None):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        self.main_window = main_window
        self.init_ui()
    
    def init_ui(self):
        """Initialize the page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.settings_tab = AdminSettingsTab(self.config_store, self.translator)
        self.logs_tab = LogsTab(self.config_store, self.translator)
        
        self.tab_widget.addTab(
            self.settings_tab,
            self.translator.t("admin.tabs.settings")
        )
        self.tab_widget.addTab(
            self.logs_tab,
            self.translator.t("admin.tabs.logs")
        )
        
        layout.addWidget(self.tab_widget)
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.tab_widget.setTabText(0, self.translator.t("admin.tabs.settings"))
        self.tab_widget.setTabText(1, self.translator.t("admin.tabs.logs"))
        
        self.settings_tab.refresh_ui()
        self.logs_tab.refresh_ui()

