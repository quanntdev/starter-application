# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

# Get the directory containing this spec file
try:
    spec_dir = Path(SPECPATH)
except NameError:
    # If SPECPATH is not defined, use current directory
    spec_dir = Path.cwd()

src_dir = spec_dir / "src"

# Add src to path so collect_submodules can find modules
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Collect all submodules - this should work now
try:
    ui_modules = collect_submodules('ui')
    i18n_modules = collect_submodules('i18n')
    storage_modules = collect_submodules('storage')
    services_modules = collect_submodules('services')
    models_modules = collect_submodules('models')
    utils_modules = collect_submodules('utils')
    print(f"Successfully collected modules: ui={len(ui_modules)}, services={len(services_modules)}")
except Exception as e:
    print(f"Warning: collect_submodules failed: {e}")
    # Fallback: manually list all modules
    ui_modules = [
        'ui', 'ui.main_window', 'ui.theme',
        'ui.pages', 'ui.pages.dashboard_page', 'ui.pages.starter_page', 
        'ui.pages.admin_page', 'ui.pages.coming_soon_page',
        'ui.tabs', 'ui.tabs.startup_status_tab', 'ui.tabs.favourite_tab',
        'ui.tabs.all_apps_tab', 'ui.tabs.settings_tab', 'ui.tabs.languages_tab',
        'ui.tabs.trigger_tab', 'ui.tabs.rules_tab',
        'ui.components', 'ui.components.dialogs'
    ]
    i18n_modules = ['i18n', 'i18n.translator']
    storage_modules = ['storage', 'storage.config_store']
    services_modules = [
        'services', 'services.system_metrics_service', 'services.startup_monitor_service',
        'services.discovery_service', 'services.launcher_service',
        'services.startup_service', 'services.url_service'
    ]
    models_modules = ['models', 'models.config_models']
    utils_modules = ['utils', 'utils.paths']

a = Analysis(
    ['src/app/main.py'],
    pathex=['src', str(src_dir)],
    binaries=[],
    datas=[
        ('src/images', 'images'),
        ('src/i18n/locales', 'i18n/locales')
    ],
    hiddenimports=[
        # Collect all submodules
        *ui_modules,
        *i18n_modules,
        *storage_modules,
        *services_modules,
        *models_modules,
        *utils_modules,
        # Explicit imports
        'ui.main_window',
        'ui.pages.dashboard_page',
        'ui.pages.starter_page',
        'ui.pages.admin_page',
        'ui.pages.coming_soon_page',
        'ui.tabs.startup_status_tab',
        'ui.tabs.favourite_tab',
        'ui.tabs.all_apps_tab',
        'ui.tabs.settings_tab',
        'ui.tabs.languages_tab',
        'ui.tabs.trigger_tab',
        'ui.tabs.rules_tab',
        'ui.theme',
        'i18n.translator',
        'storage.config_store',
        'services.system_metrics_service',
        'services.startup_monitor_service',
        'services.discovery_service',
        'services.launcher_service',
        'services.startup_service',
        'services.url_service',
        'models.config_models',
        'utils.paths',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'qtawesome',
        'psutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_src_path.py'],
    excludes=[],
    noarchive=False,
    optimize=0,
)
# Include all collected modules in the archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='StarterAppLauncher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/images/avatar.png',
    uac_admin=True,
    uac_uiaccess=False,
    manifest='app.manifest',
)
