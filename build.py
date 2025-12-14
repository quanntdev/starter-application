"""Build script for creating executable with icon."""
import PyInstaller.__main__
import sys
from pathlib import Path

def build():
    """Build the application executable."""
    # Paths
    src_dir = Path(__file__).parent / "src"
    avatar_path = src_dir / "images" / "avatar.png"
    main_script = src_dir / "app" / "main.py"
    
    # Convert PNG to ICO if needed (Windows requires .ico)
    icon_path = avatar_path
    if avatar_path.exists() and avatar_path.suffix == ".png":
        # Try to use .ico if exists, otherwise use .png (PyInstaller can handle both)
        ico_path = avatar_path.with_suffix(".ico")
        if not ico_path.exists():
            print(f"Note: Using PNG icon. For best results, convert {avatar_path.name} to .ico format")
            icon_path = avatar_path
        else:
            icon_path = ico_path
    
    # PyInstaller arguments
    args = [
        str(main_script),
        "--name=StarterAppLauncher",
        "--onefile",
        "--windowed",  # No console window
        "--clean",
        "--noconfirm",
    ]
    
    # Add icon if exists
    if icon_path.exists():
        args.append(f"--icon={icon_path}")
        print(f"Using icon: {icon_path}")
    else:
        print(f"Warning: Icon not found at {icon_path}")
    
    # Add data files (images, locales)
    if (src_dir / "images").exists():
        args.append(f"--add-data={src_dir / 'images'};images")
    
    if (src_dir / "i18n" / "locales").exists():
        args.append(f"--add-data={src_dir / 'i18n' / 'locales'};i18n/locales")
    
    # Hidden imports
    args.extend([
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=qtawesome",
    ])
    
    print("Building executable...")
    print(f"Arguments: {' '.join(args)}")
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()

