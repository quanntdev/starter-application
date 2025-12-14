@echo off
REM Quick run script for Starter App Launcher

echo Starting Starter App Launcher...
echo.

if exist "dist\StarterAppLauncher.exe" (
    start "" "dist\StarterAppLauncher.exe"
) else (
    echo Error: StarterAppLauncher.exe not found!
    echo Please run build.bat first.
    echo.
    pause
)

