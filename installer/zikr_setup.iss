; Inno Setup script for Kundalik Zikrlar desktop app
; Build prerequisites:
; 1) Run scripts\build_windows_exe.bat
; 2) Install Inno Setup 6+

#define MyAppName "Kundalik Zikrlar"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Kundalik Zikrlar Team"
#define MyAppExeName "KundalikZikrlar.exe"

[Setup]
AppId={{6C92895A-A746-4B2A-8A5A-CAAB8E209001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=dist_installer
OutputBaseFilename=KundalikZikrlarSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "dist\KundalikZikrlar\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
