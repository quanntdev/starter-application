; Inno Setup Script for Starter App Launcher
; Build command: iscc installer.iss

#define MyAppName "Starter App Launcher"
#define MyAppVersion "1.0.0-beta"
#define MyAppPublisher "StarterApp Team"
#define MyAppURL "https://github.com/your-repo/starter-app-launcher"
#define MyAppExeName "StarterAppLauncher.exe"

[Setup]
; App identity
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Install location
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
DisableProgramGroupPage=yes

; Output
OutputDir=installer_output
OutputBaseFilename=StarterAppLauncher-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes

; UI
WizardStyle=modern
WizardSizePercent=120,100
WizardResizable=no
; SetupIconFile=assets\app.ico  ; Uncomment when icon exists

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Misc
Uninstallable=yes
CreateUninstallRegKey=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce
Name: "startmenuicon"; Description: "Create a Start Menu shortcut"; GroupDescription: "Additional shortcuts:"; Flags: checkedonce

[Files]
; Main executable
Source: "dist\StarterAppLauncher.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Desktop shortcut
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
; Start Menu shortcut
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startmenuicon
; Start Menu uninstall
Name: "{autoprograms}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Run]
; Option to run app after install (with admin privileges)
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent runascurrentuser shellexec

[UninstallDelete]
; Clean up app data on uninstall (optional - comment out to keep user data)
; Type: filesandordirs; Name: "{userappdata}\StarterAppLauncher"

[Messages]
SelectTasksLabel2=Select the shortcuts you would like to create, then click Next.
WelcomeLabel1=Welcome to [name] Setup
WelcomeLabel2=This will install [name/ver] on your computer.%n%nIt is recommended that you close all other applications before continuing.
FinishedHeadingLabel=Installation Complete!
FinishedLabel=Setup has finished installing [name] on your computer.%n%nClick Finish to exit Setup.

[Code]
// Custom code if needed

