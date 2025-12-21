@echo off
REM Build Installer for Starter App Launcher
REM Requires: Inno Setup installed (https://jrsoftware.org/isinfo.php)

echo ========================================
echo Building Starter App Launcher Installer
echo ========================================
echo.

REM Check if Inno Setup is installed
set ISCC_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
) else (
    echo ERROR: Inno Setup not found!
    echo.
    echo Please install Inno Setup from:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo Found Inno Setup: %ISCC_PATH%
echo.

REM Check if exe exists
if not exist "dist\StarterAppLauncher.exe" (
    echo ERROR: dist\StarterAppLauncher.exe not found!
    echo.
    echo Please run build.bat first to create the executable.
    echo.
    pause
    exit /b 1
)

REM Create output directory
if not exist installer_output mkdir installer_output

REM Build installer
echo Building installer...
echo.
"%ISCC_PATH%" installer.iss

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Installer built successfully!
    echo ========================================
    echo.
    echo Output: installer_output\StarterAppLauncher-Setup-1.0.0-beta.exe
    echo.
) else (
    echo.
    echo ========================================
    echo Installer build failed!
    echo ========================================
    echo.
)

pause







