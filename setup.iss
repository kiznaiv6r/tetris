[Setup]
AppName=Тетрис
AppVersion=1.0
AppPublisher=Ваше Имя
DefaultDirName={autopf}\Тетрис
DefaultGroupName=Тетрис
UninstallDisplayName=Тетрис
OutputBaseFilename=Установка_Тетриса
Compression=lzma2
SolidCompression=yes
LicenseFile=LICENSE.txt
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\Тетрис.exe
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
AlwaysShowDirOnReadyPage=yes
DisableDirPage=no

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon"; Description: "Создать ярлык на Рабочем столе"; GroupDescription: "Ярлыки:"

[Files]
; 1. Главный EXE-файл
Source: "dist\Тетрис.exe"; DestDir: "{app}"; Flags: ignoreversion

; 2. Конфигурационный файл (только если нет у пользователя)
Source: "config.ini"; DestDir: "{userappdata}\Тетрис"; Flags: onlyifdoesntexist

; 3. Все ресурсы игры
Source: "resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs

; 4. Шаблоны для папки data (не перезаписываем существующие)
Source: "data\*"; DestDir: "{userappdata}\Тетрис\data"; Flags: onlyifdoesntexist recursesubdirs

; 5. Документация
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Тетрис"; Filename: "{app}\Тетрис.exe"
Name: "{group}\Удалить Тетрис"; Filename: "{uninstallexe}"
Name: "{userdesktop}\Тетрис"; Filename: "{app}\Тетрис.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\Тетрис.exe"; Description: "Запустить Тетрис"; Flags: nowait postinstall skipifsilent

[InstallDelete]
; Удаляем старые версии config.ini из корня
Type: files; Name: "{app}\config.ini"

[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\Тетрис"

[Code]
// Функция для определения пути к AppData
function GetUserDataPath(Param: String): String;
begin
  Result := ExpandConstant('{userappdata}') + '\Тетрис';
end;