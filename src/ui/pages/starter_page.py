"""Starter App page with Startup Status, Favourite, Application, and Settings tabs."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from ui.tabs.startup_status_tab import StartupStatusTab
from ui.tabs.favourite_tab import FavouriteTab
from ui.tabs.all_apps_tab import AllAppsTab
from ui.tabs.settings_tab import SettingsTab


class StarterPage(QWidget):
    """Starter App main page with tabs."""
    
    def __init__(self, config_store, translator, parent=None, is_startup_launch=False):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        self.is_startup_launch = is_startup_launch
        self.init_ui()
    
    def init_ui(self):
        """Initialize the page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.startup_status_tab = StartupStatusTab(self.config_store, self.translator)
        self.favourite_tab = FavouriteTab(self.config_store, self.translator)
        self.all_apps_tab = AllAppsTab(self.config_store, self.translator)
        self.settings_tab = SettingsTab(self.config_store, self.translator, is_startup_launch=self.is_startup_launch)
        
        # Connect all_apps_tab to favourite_tab for refresh
        self.all_apps_tab.favourite_added.connect(self.on_favourite_added)
        
        # Add tabs in order - Favourite first
        self.tab_widget.addTab(
            self.favourite_tab,
            self.translator.t("starter.tabs.favourite")
        )
        self.tab_widget.addTab(
            self.startup_status_tab,
            self.translator.t("starter.tabs.startup_status")
        )
        self.tab_widget.addTab(
            self.all_apps_tab,
            self.translator.t("starter.tabs.all_apps")
        )
        self.tab_widget.addTab(
            self.settings_tab,
            self.translator.t("starter.tabs.settings")
        )
        
        # Set default tab to Favourite (index 0)
        self.tab_widget.setCurrentIndex(0)
        
        layout.addWidget(self.tab_widget)
    
    def on_favourite_added(self):
        """Handle when a new favourite is added."""
        self.favourite_tab.load_favourites()
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.tab_widget.setTabText(0, self.translator.t("starter.tabs.favourite"))
        self.tab_widget.setTabText(1, self.translator.t("starter.tabs.startup_status"))
        self.tab_widget.setTabText(2, self.translator.t("starter.tabs.all_apps"))
        self.tab_widget.setTabText(3, self.translator.t("starter.tabs.settings"))
        
        self.startup_status_tab.refresh_ui()
        self.favourite_tab.refresh_ui()
        self.all_apps_tab.refresh_ui()
        self.settings_tab.refresh_ui()

