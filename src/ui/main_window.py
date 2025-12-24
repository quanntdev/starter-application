"""Main application window with sidebar and content area."""
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
import qtawesome as qta

from ui.theme import apply_theme
from ui.pages.starter_page import StarterPage
from ui.pages.admin_page import AdminPage
from ui.pages.coming_soon_page import ComingSoonPage
from ui.pages.tools_page import ToolsPage
from ui.pages.clipboard_history_page import ClipboardHistoryPage
from ui.components.email_registration_dialog import EmailRegistrationDialog
from services.email_registration_service import EmailRegistrationService
from tools.clipboard.storage import ClipboardStorage
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
        
        title_label = QLabel("Starter App Launcher (Beta)")
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
        
        # Starter App button (default page)
        btn_starter = QPushButton("  " + self.translator.t("sidebar.starter_app"))
        btn_starter.setIcon(qta.icon('fa5s.mobile-alt', color='#e0e0e0'))
        btn_starter.setCheckable(True)
        btn_starter.setChecked(True)
        btn_starter.clicked.connect(lambda: self.menu_changed.emit("starter"))
        self.menu_buttons["starter"] = btn_starter
        layout.addWidget(btn_starter)
        
        # Tools button
        btn_tools = QPushButton("  " + self.translator.t("sidebar.tools"))
        btn_tools.setIcon(qta.icon('fa5s.tools', color='#e0e0e0'))
        btn_tools.setCheckable(True)
        btn_tools.clicked.connect(lambda: self.menu_changed.emit("tools"))
        self.menu_buttons["tools"] = btn_tools
        layout.addWidget(btn_tools)
        
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
        self.menu_buttons["starter"].setText("  " + self.translator.t("sidebar.starter_app"))
        self.menu_buttons["tools"].setText("  " + self.translator.t("sidebar.tools"))
        self.menu_buttons["soon_0"].setText("  " + self.translator.t("sidebar.coming_soon"))
        self.menu_buttons["admin"].setText("  " + self.translator.t("sidebar.admin_settings"))


class BlurOverlay(QWidget):
    """Overlay widget to blur and disable interaction with background."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);")
    
    def paintEvent(self, event):
        """Paint blur effect."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 200))  # Semi-transparent black


class EmailSubmissionThread(QThread):
    """Thread for submitting email to avoid blocking UI."""
    
    finished = Signal(bool, str)  # success, error_message
    
    def __init__(self, email: str, service: EmailRegistrationService):
        super().__init__()
        self.email = email
        self.service = service
    
    def run(self):
        """Run email submission in background."""
        success, error_msg = self.service.submit_email(self.email)
        self.finished.emit(success, error_msg or "")


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, config_store, translator, icon_path=None, is_startup_launch=False):
        super().__init__()
        self.config_store = config_store
        self.translator = translator
        self.is_startup_launch = is_startup_launch
        self.email_service = EmailRegistrationService()
        
        self.setWindowTitle("Starter App Launcher (Beta)")
        self.setMinimumSize(1200, 800)
        
        # Set window icon (for taskbar)
        if icon_path:
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Apply theme
        apply_theme(self)
        
        self.init_ui()
        
        # Check email registration after UI is initialized
        QTimer.singleShot(100, self.check_email_registration)
    
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
        
        # Create clipboard storage (shared)
        self.clipboard_storage = ClipboardStorage()
        
        # Create pages
        self.starter_page = StarterPage(self.config_store, self.translator, is_startup_launch=self.is_startup_launch)
        self.tools_page = ToolsPage(self.config_store, self.translator, clipboard_storage=self.clipboard_storage)
        self.admin_page = AdminPage(self.config_store, self.translator, self)
        self.coming_soon_page = ComingSoonPage(self.translator)
        # Pass clipboard service from tools_page to history page
        clipboard_service = None
        if hasattr(self.tools_page, 'clipboard_manager') and hasattr(self.tools_page.clipboard_manager, 'service'):
            clipboard_service = self.tools_page.clipboard_manager.service
        self.clipboard_history_page = ClipboardHistoryPage(self.clipboard_storage, self.translator, clipboard_service=clipboard_service)
        
        # Connect tools page signal to navigate to clipboard history
        self.tools_page.view_clipboard_history.connect(self.show_clipboard_history)
        
        self.content_stack.addWidget(self.starter_page)
        self.content_stack.addWidget(self.tools_page)
        self.content_stack.addWidget(self.admin_page)
        self.content_stack.addWidget(self.coming_soon_page)
        self.content_stack.addWidget(self.clipboard_history_page)
        
        # Set Starter App as default page
        self.content_stack.setCurrentWidget(self.starter_page)
        
        main_layout.addWidget(self.content_stack, 1)
    
    def on_menu_changed(self, menu_key):
        """Handle menu item change."""
        self.sidebar.set_active_menu(menu_key)
        
        if menu_key == "starter":
            self.content_stack.setCurrentWidget(self.starter_page)
        elif menu_key == "tools":
            self.content_stack.setCurrentWidget(self.tools_page)
        elif menu_key == "admin":
            self.content_stack.setCurrentWidget(self.admin_page)
        elif menu_key.startswith("soon_"):
            self.content_stack.setCurrentWidget(self.coming_soon_page)
    
    def show_clipboard_history(self):
        """Show clipboard history page."""
        self.content_stack.setCurrentWidget(self.clipboard_history_page)
        self.clipboard_history_page.refresh_content()
    
    def check_email_registration(self):
        """Check if email is registered, show dialog if not."""
        if not self.config_store.is_email_registered():
            self.show_email_registration_dialog()
    
    def show_email_registration_dialog(self):
        """Show blocking email registration dialog."""
        # Create blur overlay
        self.blur_overlay = BlurOverlay(self)
        self.blur_overlay.setGeometry(self.rect())
        self.blur_overlay.show()
        
        # Create and show email registration dialog
        self.email_dialog = EmailRegistrationDialog(self.translator, self)
        self.email_dialog.email_submitted.connect(self.on_email_submitted)
        self.email_dialog.show()
        
        # Center dialog
        dialog_rect = self.email_dialog.geometry()
        dialog_rect.moveCenter(self.geometry().center())
        self.email_dialog.setGeometry(dialog_rect)
    
    def on_email_submitted(self, email: str):
        """Handle email submission."""
        # Show loading in dialog
        self.email_dialog.show_success()
        
        # Submit email in background thread
        self.email_thread = EmailSubmissionThread(email, self.email_service)
        self.email_thread.finished.connect(lambda success, error: self.on_email_submission_finished(success, error, email))
        self.email_thread.start()
    
    def on_email_submission_finished(self, success: bool, error_message: str, email: str):
        """Handle email submission result."""
        if success:
            # Save registration status
            self.config_store.set_email_registered(True)
            
            # Close dialog and remove overlay
            self.email_dialog.close()
            self.blur_overlay.hide()
            self.blur_overlay.deleteLater()
            self.email_dialog.deleteLater()
            
            print(f"Email registration successful: {email}")
        else:
            # Show error and allow retry
            self.email_dialog.show_error(error_message)
            print(f"Email registration failed: {error_message}")
    
    def resizeEvent(self, event):
        """Handle window resize to update overlay position."""
        super().resizeEvent(event)
        if hasattr(self, 'blur_overlay') and self.blur_overlay:
            self.blur_overlay.setGeometry(self.rect())
        if hasattr(self, 'email_dialog') and self.email_dialog:
            # Keep dialog centered
            dialog_rect = self.email_dialog.geometry()
            dialog_rect.moveCenter(self.geometry().center())
            self.email_dialog.setGeometry(dialog_rect)
    
    def refresh_ui(self):
        """Refresh all UI elements after language change."""
        self.sidebar.refresh_ui()
        self.starter_page.refresh_ui()
        self.tools_page.refresh_ui()
        self.admin_page.refresh_ui()
        self.coming_soon_page.refresh_ui()

