# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Starter App Launcher
Run: pyinstaller build.spec
"""

import sys
from pathlib import Path

block_cipher = None

# Paths
src_dir = Path(SPECPATH) / "src"
app_dir = src_dir / "app"
images_dir = src_dir / "images"
locales_dir = src_dir / "i18n" / "locales"

# Icon path
icon_path = images_dir / "avatar.png"
if not icon_path.exists():
    icon_path = None
else:
    # Try .ico version first
    ico_path = images_dir / "avatar.ico"
    if ico_path.exists():
        icon_path = ico_path

a = Analysis(
    [str(app_dir / "main.py")],
    pathex=[str(src_dir)],
    binaries=[],
    datas=[
        (str(images_dir), "images") if images_dir.exists() else None,
        (str(locales_dir), "i18n/locales") if locales_dir.exists() else None,
    ],
    hiddenimports=[
        "PySide6.QtCore",
        "PySide6.QtGui",
        "PySide6.QtWidgets",
        "qtawesome",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="StarterAppLauncher",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_path) if icon_path and icon_path.exists() else None,
)

