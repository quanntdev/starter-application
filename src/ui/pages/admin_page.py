"""Admin settings page with Languages, Trigger, and Rules tabs."""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from ui.tabs.languages_tab import LanguagesTab
from ui.tabs.trigger_tab import TriggerTab
from ui.tabs.rules_tab import RulesTab


class AdminPage(QWidget):
    """Admin settings page with tabs."""
    
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
        self.languages_tab = LanguagesTab(self.config_store, self.translator, self.main_window)
        self.trigger_tab = TriggerTab(self.config_store, self.translator)
        self.rules_tab = RulesTab(self.config_store, self.translator)
        
        self.tab_widget.addTab(
            self.languages_tab,
            self.translator.t("admin.tabs.languages")
        )
        self.tab_widget.addTab(
            self.trigger_tab,
            self.translator.t("admin.tabs.trigger")
        )
        self.tab_widget.addTab(
            self.rules_tab,
            self.translator.t("admin.tabs.rules")
        )
        
        layout.addWidget(self.tab_widget)
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.tab_widget.setTabText(0, self.translator.t("admin.tabs.languages"))
        self.tab_widget.setTabText(1, self.translator.t("admin.tabs.trigger"))
        self.tab_widget.setTabText(2, self.translator.t("admin.tabs.rules"))
        
        self.languages_tab.refresh_ui()
        self.trigger_tab.refresh_ui()
        self.rules_tab.refresh_ui()

