"""All Apps (List APP) tab for discovering installed apps."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QListWidgetItem, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal
import qtawesome as qta
import uuid

from services.discovery_service import DiscoveryService, AppInfo
from models.config_models import Favourite


class AppListItem(QWidget):
    """Widget for a single app in the list."""
    
    def __init__(self, app_info, translator, on_add_callback, parent=None):
        super().__init__(parent)
        self.app_info = app_info
        self.translator = translator
        self.on_add_callback = on_add_callback
        self.init_ui()
    
    def init_ui(self):
        """Initialize item UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # App icon placeholder
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.cube', color='#a0a0a0').pixmap(24, 24))
        layout.addWidget(icon_label)
        
        # App name
        name_label = QLabel(self.app_info.name)
        name_label.setStyleSheet("font-weight: 500;")
        layout.addWidget(name_label, 1)
        
        # Add button
        btn_add = QPushButton(self.translator.t("all_apps.add"))
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(lambda: self.on_add_callback(self.app_info))
        btn_add.setMaximumWidth(80)
        layout.addWidget(btn_add)


class AllAppsTab(QWidget):
    """All Apps tab with search and list."""
    
    # Signal emitted when a favourite is added
    favourite_added = Signal()
    
    def __init__(self, config_store, translator, parent=None):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        self.discovery = DiscoveryService()
        self.all_apps = []
        self.filtered_apps = []
        self.init_ui()
        self.start_scan()
    
    def init_ui(self):
        """Initialize tab UI."""
        layout = QVBoxLayout(self)
        
        # Title
        self.title_label = QLabel(self.translator.t("all_apps.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        layout.addWidget(self.title_label)
        
        layout.addSpacing(10)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.translator.t("all_apps.search_placeholder"))
        self.search_input.textChanged.connect(self.on_search_changed)
        layout.addWidget(self.search_input)
        
        layout.addSpacing(10)
        
        # Status label
        self.status_label = QLabel("Scanning for apps...")
        self.status_label.setStyleSheet("color: #a0a0a0;")
        layout.addWidget(self.status_label)
        
        # Scroll area for apps list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Apps list container
        self.apps_container = QWidget()
        self.apps_layout = QVBoxLayout(self.apps_container)
        self.apps_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.apps_layout.setSpacing(4)
        
        scroll_area.setWidget(self.apps_container)
        layout.addWidget(scroll_area, 1)
    
    def start_scan(self):
        """Start scanning for installed apps."""
        self.status_label.setText("Scanning for apps...")
        self.discovery.scan_installed_apps(self.on_apps_discovered)
    
    def on_apps_discovered(self, apps):
        """Handle discovered apps."""
        self.all_apps = apps
        self.filtered_apps = apps
        self.status_label.setText(f"Found {len(apps)} apps")
        self.display_apps()
    
    def on_search_changed(self, text):
        """Handle search input change."""
        search_text = text.lower().strip()
        
        if not search_text:
            self.filtered_apps = self.all_apps
        else:
            self.filtered_apps = [
                app for app in self.all_apps
                if search_text in app.name.lower()
            ]
        
        self.display_apps()
    
    def display_apps(self):
        """Display filtered apps list."""
        # Clear existing widgets
        while self.apps_layout.count():
            item = self.apps_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add app items - SHOW ALL (no limit)
        for app in self.filtered_apps:
            item_widget = AppListItem(app, self.translator, self.on_add_app)
            self.apps_layout.addWidget(item_widget)
    
    def on_add_app(self, app_info: AppInfo):
        """Handle add app to favourites."""
        # Check if already in favourites
        favourites = self.config_store.get_favourites()
        for fav in favourites:
            if fav.lnk_path == app_info.lnk_path:
                QMessageBox.information(
                    self,
                    "Already added",
                    self.translator.t("common.messages.duplicate", name=app_info.name)
                )
                return
        
        # Detect kind (browser or app)
        kind = self.detect_app_kind(app_info.name)
        label = self.translator.t(f"favourites.label.{kind}")
        
        # Create favourite
        fav = Favourite(
            id=f"fav::{uuid.uuid4()}",
            name=app_info.name,
            lnk_path=app_info.lnk_path,
            kind=kind,
            label=label,
            selected=False,
            browser_links=[]
        )
        
        self.config_store.add_favourite(fav)
        
        # Emit signal to refresh favourite tab
        self.favourite_added.emit()
        
        QMessageBox.information(
            self,
            "Added",
            f"{app_info.name} added to favourites!"
        )
    
    def detect_app_kind(self, app_name: str) -> str:
        """Detect app kind based on name."""
        app_name_lower = app_name.lower()
        
        browsers = ["chrome", "firefox", "edge", "brave", "opera", "vivaldi", "safari"]
        
        for browser in browsers:
            if browser in app_name_lower:
                return "browser"
        
        return "app"
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.title_label.setText(self.translator.t("all_apps.title"))
        self.search_input.setPlaceholderText(self.translator.t("all_apps.search_placeholder"))
        self.display_apps()

