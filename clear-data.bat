@echo off
REM Script to clear app data (favorites, settings, etc.)
REM This will delete the config.json file

echo ========================================
echo Clear Starter App Launcher Data
echo ========================================
echo.

set CONFIG_DIR=%APPDATA%\StarterAppLauncher
set CONFIG_FILE=%CONFIG_DIR%\config.json

if exist "%CONFIG_FILE%" (
    echo Found config file: %CONFIG_FILE%
    echo.
    echo WARNING: This will delete all your favorites, settings, and configuration!
    echo.
    set /p CONFIRM="Are you sure you want to delete? (yes/no): "
    
    if /i "%CONFIRM%"=="yes" (
        del "%CONFIG_FILE%"
        echo.
        echo Config file deleted successfully!
        echo App will start with default settings next time.
    ) else (
        echo.
        echo Operation cancelled.
    )
) else (
    echo Config file not found: %CONFIG_FILE%
    echo Nothing to delete.
)

echo.
pause



