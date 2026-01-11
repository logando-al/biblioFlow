; BiblioFlow Inno Setup Installer Script
; Requires Inno Setup 6.0 or later

#define MyAppName "BiblioFlow"
#define MyAppVersion "0.3.0"
#define MyAppPublisher "BiblioFlow"
#define MyAppURL "https://github.com/logando-al/biblioFlow"
#define MyAppExeName "BiblioFlow.exe"

[Setup]
; App information
AppId={{B1BL10FL0W-4PP1-1D00-0000-000000000001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}/releases

; Installation paths
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Output settings
OutputDir=installer_output
OutputBaseFilename=BiblioFlow-{#MyAppVersion}-Setup
SetupIconFile=src\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; Compression
Compression=lzma2
SolidCompression=yes

; Windows settings
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Appearance - wizard images removed (require BMP format)

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main executable (built by PyInstaller)
Source: "dist\BiblioFlow.exe"; DestDir: "{app}"; Flags: ignoreversion

; You can also include additional files if needed:
; Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Registry]
; Add to "Open with" for PDF files (optional)
Root: HKCU; Subkey: "Software\Classes\.pdf\OpenWithProgids"; ValueType: string; ValueName: "BiblioFlow.PDF"; ValueData: ""; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\Classes\BiblioFlow.PDF"; ValueType: string; ValueName: ""; ValueData: "BiblioFlow PDF Document"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\BiblioFlow.PDF\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKCU; Subkey: "Software\Classes\BiblioFlow.PDF\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""

[Code]
// Check if .NET Framework or other dependencies are needed
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
