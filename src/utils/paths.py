"""Path utilities for Windows paths."""
import os
from pathlib import Path
from typing import List


def get_start_menu_paths() -> List[Path]:
    """Get Start Menu program paths."""
    paths = []
    
    # User Start Menu
    user_path = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    if user_path.exists():
        paths.append(user_path)
    
    # All Users Start Menu
    all_users_path = Path(os.getenv("PROGRAMDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    if all_users_path.exists():
        paths.append(all_users_path)
    
    return paths


def get_app_data_dir() -> Path:
    """Get application data directory."""
    return Path(os.getenv("APPDATA")) / "StarterAppLauncher"

