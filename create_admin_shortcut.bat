@echo off
REM Create shortcut that always runs as administrator

echo Creating administrator shortcut...
echo.

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Starter App Launcher (Admin).lnk'); $Shortcut.TargetPath = '%~dp0dist\StarterAppLauncher.exe'; $Shortcut.WorkingDirectory = '%~dp0dist'; $Shortcut.Description = 'Starter App Launcher with Administrator privileges'; $Shortcut.Save(); $bytes = [System.IO.File]::ReadAllBytes('%USERPROFILE%\Desktop\Starter App Launcher (Admin).lnk'); $bytes[0x15] = $bytes[0x15] -bor 0x20; [System.IO.File]::WriteAllBytes('%USERPROFILE%\Desktop\Starter App Launcher (Admin).lnk', $bytes)"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Shortcut created successfully!
    echo ========================================
    echo.
    echo Location: Desktop\Starter App Launcher (Admin).lnk
    echo.
    echo This shortcut will always request admin privileges.
    echo.
) else (
    echo.
    echo Failed to create shortcut.
    echo Please create it manually.
    echo.
)

pause

