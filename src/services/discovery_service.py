"""Discovery service for scanning installed apps."""
import os
from pathlib import Path
from typing import List, Dict
from PySide6.QtCore import QThread, Signal

from utils.paths import get_start_menu_paths


class AppInfo:
    """Information about a discovered app."""
    
    def __init__(self, name: str, lnk_path: str, icon_path: str = None):
        self.name = name
        self.lnk_path = lnk_path
        self.icon_path = icon_path


class DiscoveryWorker(QThread):
    """Worker thread for scanning apps without blocking UI."""
    
    apps_found = Signal(list)  # Signal emits list of AppInfo
    
    def run(self):
        """Scan Start Menu for .lnk files."""
        apps = []
        start_menu_paths = get_start_menu_paths()
        
        for base_path in start_menu_paths:
            if not base_path.exists():
                continue
            
            # Walk through all subdirectories
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.endswith('.lnk'):
                        lnk_path = Path(root) / file
                        # Extract app name from filename (remove .lnk extension)
                        app_name = file[:-4]
                        
                        # Skip common non-app shortcuts
                        skip_keywords = ['uninstall', 'readme', 'help', 'documentation']
                        if any(keyword in app_name.lower() for keyword in skip_keywords):
                            continue
                        
                        apps.append(AppInfo(
                            name=app_name,
                            lnk_path=str(lnk_path),
                            icon_path=None  # Can be extracted later if needed
                        ))
        
        # Remove duplicates by name (keep first occurrence)
        seen_names = set()
        unique_apps = []
        for app in apps:
            if app.name not in seen_names:
                seen_names.add(app.name)
                unique_apps.append(app)
        
        # Sort alphabetically
        unique_apps.sort(key=lambda x: x.name.lower())
        
        self.apps_found.emit(unique_apps)


class DiscoveryService:
    """Service for discovering installed apps from Start Menu."""
    
    def __init__(self):
        self.worker = None
    
    def scan_installed_apps(self, callback):
        """
        Scan Start Menu for installed apps asynchronously.
        
        Args:
            callback: Function to call with list of AppInfo when scan completes
        """
        if self.worker is not None and self.worker.isRunning():
            return  # Already scanning
        
        self.worker = DiscoveryWorker()
        self.worker.apps_found.connect(callback)
        self.worker.start()
    
    def is_scanning(self):
        """Check if a scan is in progress."""
        return self.worker is not None and self.worker.isRunning()

