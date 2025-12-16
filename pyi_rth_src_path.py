"""
Runtime hook to add src directory to sys.path for PyInstaller builds.
This ensures modules can be imported correctly.
"""
import sys
import os
from pathlib import Path

# If running as frozen executable
if getattr(sys, 'frozen', False):
    # Get the bundle directory
    bundle_dir = getattr(sys, '_MEIPASS', Path(sys.executable).parent)
    
    # Add bundle dir to path if not already there
    if str(bundle_dir) not in sys.path:
        sys.path.insert(0, str(bundle_dir))
    
    # Also try adding src subdirectory if it exists
    src_in_bundle = Path(bundle_dir) / "src"
    if src_in_bundle.exists() and str(src_in_bundle) not in sys.path:
        sys.path.insert(0, str(src_in_bundle))




