"""Main entry point for Starter App Launcher."""
import sys
import os
import ctypes
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Add src to path - handle both frozen (PyInstaller) and development mode
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = Path(sys.executable).parent
    # Add the bundle dir to path
    bundle_dir = getattr(sys, '_MEIPASS', application_path)
    sys.path.insert(0, str(bundle_dir))
else:
    # Running in development
    sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.main_window import MainWindow
from i18n.translator import Translator
from storage.config_store import ConfigStore


def is_admin():
    """Check if running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def request_admin_restart():
    """Restart the application with administrator privileges."""
    try:
        if getattr(sys, 'frozen', False):
            # Running as compiled executable - use the exe itself
            exe_path = sys.executable
            # No arguments needed for exe
            params = ""
        else:
            # Running as Python script
            exe_path = sys.executable
            script_path = sys.argv[0]
            params = f'"{script_path}"'
        
        # Request UAC elevation using ShellExecuteW
        # SW_SHOWNORMAL = 1
        result = ctypes.windll.shell32.ShellExecuteW(
            None,           # hwnd
            "runas",        # lpOperation - request admin
            exe_path,       # lpFile - executable path
            params,         # lpParameters
            None,           # lpDirectory
            1               # nShowCmd - SW_SHOWNORMAL
        )
        
        # ShellExecuteW returns > 32 on success
        if result > 32:
            return True
        else:
            return False
            
    except Exception:
        return False


def main():
    """Initialize and run the application."""
    # Load config first to check admin requirement
    temp_config = ConfigStore()
    temp_config.load()
    
    # Check if user wants admin and we don't have it yet
    if temp_config.get_require_admin() and not is_admin():
        if request_admin_restart():
            # Successfully triggered UAC, exit this instance immediately
            import time
            time.sleep(0.5)
            sys.exit(0)
    
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    try:
        from src import __version__
    except ImportError:
        __version__ = "1.0.0"
    app.setApplicationName("Starter App Launcher")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("StarterAppLauncher")
    
    # Initialize config store
    config_store = ConfigStore()
    config_store.load()
    
    # Initialize translator
    translator = Translator()
    language = config_store.get_language()
    translator.set_language(language)
    
    # Get icon path - handle both frozen and development mode
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        bundle_dir = getattr(sys, '_MEIPASS', Path(sys.executable).parent)
        icon_path = Path(bundle_dir) / "images" / "avatar.png"
    else:
        # Running in development
        icon_path = Path(__file__).parent.parent / "images" / "avatar.png"
    
    # Set application and window icon
    if icon_path.exists():
        icon = QIcon(str(icon_path))
        app.setWindowIcon(icon)
    
    # Create and show main window
    window = MainWindow(config_store, translator, icon_path if icon_path.exists() else None)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

