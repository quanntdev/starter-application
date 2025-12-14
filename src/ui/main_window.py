"""Main application window with sidebar and content area."""
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
import qtawesome as qta

from ui.theme import apply_theme
from ui.pages.starter_page import StarterPage
from ui.pages.dashboard_page import DashboardPage
from ui.pages.admin_page import AdminPage
from ui.pages.coming_soon_page import ComingSoonPage
try:
    from src import __version__
except ImportError:
    __version__ = "1.0.0"


class Sidebar(QWidget):
    """Left sidebar with menu navigation."""
    
    menu_changed = Signal(str)  # Signal when menu item is clicked
    
    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.setObjectName("sidebar")
        self.setFixedWidth(240)
        self.init_ui()
    
    def init_ui(self):
        """Initialize sidebar UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top section - Avatar and title
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(16, 20, 16, 20)
        
        # Avatar image
        avatar_label = QLabel()
        avatar_path = Path(__file__).parent.parent / "images" / "avatar.png"
        if avatar_path.exists():
            pixmap = QPixmap(str(avatar_path))
            # Scale to reasonable size (64x64)
            scaled_pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            avatar_label.setPixmap(scaled_pixmap)
        else:
            # Fallback to emoji if image not found
            avatar_label.setText("👤")
            avatar_label.setStyleSheet("font-size: 32px;")
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel("Starter App Launcher")
        title_label.setStyleSheet("font-size: 16px; font-weight: 600;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Version label
        version_label = QLabel(f"v{__version__}")
        version_label.setStyleSheet("font-size: 11px; color: #888;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        top_layout.addWidget(avatar_label)
        top_layout.addWidget(title_label)
        top_layout.addWidget(version_label)
        
        layout.addWidget(top_widget)
        
        # Middle section - Menu items
        self.menu_buttons = {}
        
        # Dashboard button (default page)
        btn_dashboard = QPushButton("  " + self.translator.t("sidebar.dashboard"))
        btn_dashboard.setIcon(qta.icon('fa5s.chart-line', color='#e0e0e0'))
        btn_dashboard.setCheckable(True)
        btn_dashboard.setChecked(True)
        btn_dashboard.clicked.connect(lambda: self.menu_changed.emit("dashboard"))
        self.menu_buttons["dashboard"] = btn_dashboard
        layout.addWidget(btn_dashboard)
        
        # Starter App button
        btn_starter = QPushButton("  " + self.translator.t("sidebar.starter_app"))
        btn_starter.setIcon(qta.icon('fa5s.mobile-alt', color='#e0e0e0'))
        btn_starter.setCheckable(True)
        btn_starter.clicked.connect(lambda: self.menu_changed.emit("starter"))
        self.menu_buttons["starter"] = btn_starter
        layout.addWidget(btn_starter)
        
        # Coming soon button (1 placeholder)
        btn_soon = QPushButton("  " + self.translator.t("sidebar.coming_soon"))
        btn_soon.setIcon(qta.icon('fa5s.rocket', color='#e0e0e0'))
        btn_soon.setCheckable(True)
        btn_soon.clicked.connect(lambda: self.menu_changed.emit("soon_0"))
        self.menu_buttons["soon_0"] = btn_soon
        layout.addWidget(btn_soon)
        
        layout.addStretch()
        
        # Bottom section - Admin settings
        btn_admin = QPushButton("  " + self.translator.t("sidebar.admin_settings"))
        btn_admin.setIcon(qta.icon('fa5s.cog', color='#e0e0e0'))
        btn_admin.setCheckable(True)
        btn_admin.clicked.connect(lambda: self.menu_changed.emit("admin"))
        self.menu_buttons["admin"] = btn_admin
        layout.addWidget(btn_admin)
        
        layout.addSpacing(20)
    
    def set_active_menu(self, menu_key):
        """Set the active menu item."""
        for key, btn in self.menu_buttons.items():
            btn.setChecked(key == menu_key)
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.menu_buttons["dashboard"].setText("  " + self.translator.t("sidebar.dashboard"))
        self.menu_buttons["starter"].setText("  " + self.translator.t("sidebar.starter_app"))
        self.menu_buttons["soon_0"].setText("  " + self.translator.t("sidebar.coming_soon"))
        self.menu_buttons["admin"].setText("  " + self.translator.t("sidebar.admin_settings"))


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, config_store, translator, icon_path=None):
        super().__init__()
        self.config_store = config_store
        self.translator = translator
        
        self.setWindowTitle("Starter App Launcher")
        self.setMinimumSize(1200, 800)
        
        # Set window icon (for taskbar)
        if icon_path:
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Apply theme
        apply_theme(self)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize main window UI."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar(self.translator)
        self.sidebar.menu_changed.connect(self.on_menu_changed)
        main_layout.addWidget(self.sidebar)
        
        # Content area (stacked widget for different pages)
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("content")
        
        # Create pages
        self.dashboard_page = DashboardPage(self.config_store, self.translator)
        self.starter_page = StarterPage(self.config_store, self.translator)
        self.admin_page = AdminPage(self.config_store, self.translator, self)
        self.coming_soon_page = ComingSoonPage(self.translator)
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.starter_page)
        self.content_stack.addWidget(self.admin_page)
        self.content_stack.addWidget(self.coming_soon_page)
        
        # Set Dashboard as default page
        self.content_stack.setCurrentWidget(self.dashboard_page)
        
        main_layout.addWidget(self.content_stack, 1)
    
    def on_menu_changed(self, menu_key):
        """Handle menu item change."""
        self.sidebar.set_active_menu(menu_key)
        
        if menu_key == "starter":
            self.content_stack.setCurrentWidget(self.starter_page)
        elif menu_key == "dashboard":
            self.content_stack.setCurrentWidget(self.dashboard_page)
        elif menu_key == "admin":
            self.content_stack.setCurrentWidget(self.admin_page)
        elif menu_key.startswith("soon_"):
            self.content_stack.setCurrentWidget(self.coming_soon_page)
    
    def refresh_ui(self):
        """Refresh all UI elements after language change."""
        self.sidebar.refresh_ui()
        self.dashboard_page.refresh_ui()
        self.starter_page.refresh_ui()
        self.admin_page.refresh_ui()
        self.coming_soon_page.refresh_ui()

