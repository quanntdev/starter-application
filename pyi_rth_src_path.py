"""
Runtime hook to add src directory to sys.path for PyInstaller builds.
This ensures modules can be imported correctly.
This hook runs BEFORE main.py, so it sets up the path correctly.
"""
import sys
import os
from pathlib import Path

# If running as frozen executable
if getattr(sys, 'frozen', False):
    # Get the bundle directory (_MEIPASS is where PyInstaller extracts files)
    bundle_dir = getattr(sys, '_MEIPASS', None)
    
    if bundle_dir:
        # PyInstaller bundles modules directly in _MEIPASS root
        # So 'ui', 'i18n', etc. are directly accessible
        if str(bundle_dir) not in sys.path:
            sys.path.insert(0, str(bundle_dir))
        
        # Debug: Check if ui module exists
        ui_path = Path(bundle_dir) / "ui"
        if not ui_path.exists():
            # Try to find where modules are
            import os
            try:
                files = os.listdir(bundle_dir)
                # Filter for Python modules
                py_files = [f for f in files if f.endswith('.py') or (os.path.isdir(Path(bundle_dir) / f) and not f.startswith('_'))]
                # Modules should be in root of bundle_dir
                pass
            except:
                pass




