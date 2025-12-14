@echo off
REM Build script for Starter App Launcher

echo ========================================
echo Building Starter App Launcher...
echo ========================================
echo.

REM Clean previous build
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build with PyInstaller using spec file
pyinstaller --clean StarterAppLauncher.spec

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Build completed successfully!
    echo ========================================
    echo.
    
    REM Sign EXE if certificate exists
    if exist "code-signing-cert.pfx" (
        echo Signing executable...
        powershell -ExecutionPolicy Bypass -File "sign-exe.ps1" -ExePath "dist\StarterAppLauncher.exe"
        echo.
    ) else (
        echo Note: No certificate found. EXE will not be signed.
        echo       Create code-signing-cert.pfx to enable signing.
        echo       See CODE_SIGNING_GUIDE.md for instructions.
        echo.
    )
    
    echo Output: dist\StarterAppLauncher.exe
    echo.
    echo Note: App runs as normal user by default.
    echo       Use "Run as Administrator" when needed.
    echo.
    pause
) else (
    echo.
    echo ========================================
    echo Build failed!
    echo ========================================
    echo.
    pause
    exit /b 1
)

