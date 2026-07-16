; ============================================================================
;  WhisperVoice v3.4  —  instalator Inno Setup
;  build 14.06.2026
;
;  Cel:        lokalny voice-to-text (Whisper / faster-whisper) dla Windows 11
;  Autor:      Mariusz Świerguła  (Copyright (c) 2026)
;  Licencja:   MIT  (plik LICENSE)
;
;  Wymagania kompilacji:
;     - Inno Setup 6.3 lub nowszy (wbudowany CreateDownloadPage do pobierania
;       z paskiem postępu — od 6.1; identyfikator architektury x64compatible —
;       od 6.3). Na Inno Setup 6.1–6.2 zmień x64compatible na x64.
;     - Skompiluj z katalogu projektu (build_installer.bat albo ISCC.exe),
;       bo sekcja [Files] używa ścieżek względnych do tego pliku .iss.
;
;  ZASADY TRANSPARENTNOŚCI (zaimplementowane poniżej):
;     - instalacja per-użytkownik, BEZ uprawnień administratora;
;     - żaden komponent nie jest pobierany ani instalowany po cichu —
;       przed pobraniem użytkownik widzi pełną listę (nazwa, wersja, źródło,
;       cel, licencja, lokalizacja) i musi ją zatwierdzić;
;     - pobierany Python jest weryfikowany sumą kontrolną MD5 publikowaną
;       oficjalnie przez python.org;
;     - brak internetu i błędy pobierania kończą się czytelnym komunikatem,
;       a instalacja NIE jest oznaczana jako udana, jeśli zależności nie
;       zostały poprawnie zainstalowane;
;     - autostart jest opcjonalny i DOMYŚLNIE WYŁĄCZONY;
;     - deinstalator NIE usuwa danych użytkownika ani logów bez pytania.
; ============================================================================

#define AppName        "WhisperVoice"
#define AppVersion     "3.4"
#define AppBuild       "15.07.2026"
#define AppPublisher   "Mariusz Świerguła"
#define AppURL         "https://github.com/"
#define AppExeVbs      "run_silent.vbs"
#define AppExeBat      "run.bat"

; --- Komponent pobierany: Python (gdy brak na komputerze) -------------------
#define PyVersion      "3.12.8"
#define PyFile         "python-3.12.8-amd64.exe"
#define PyUrl          "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe"
; MD5 oficjalnie publikowane na https://www.python.org/downloads/release/python-3128/
#define PyMD5          "2f2ab2472a6aa29f8755c72c58f58f4b"
#define PySizeText     "~25,8 MB"

[Setup]
AppId={{B6F3A1D2-4C57-4E89-9A1B-7D2E5F8C0A36}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion} (build {#AppBuild})
AppPublisher={#AppPublisher}
VersionInfoVersion=3.4.0.0
VersionInfoCompany={#AppPublisher}
VersionInfoDescription=WhisperVoice {#AppVersion} — lokalny voice-to-text (instalator)
VersionInfoProductName={#AppName}

; Instalacja per-użytkownik — NIE wymaga administratora.
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Domyślny katalog: %LOCALAPPDATA%\Programs\WhisperVoice (zapisywalny bez admina).
; Użytkownik może go zmienić na ekranie wyboru katalogu.
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
DisableDirPage=no
DisableProgramGroupPage=yes
AllowNoIcons=yes

; Cel: Windows 11 (główna platforma). Windows 10 pozostaje kompatybilny,
; dlatego nie blokujemy go sztucznie (MinVersion 10.0 = Windows 10/11 64-bit).
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

OutputDir=Output
OutputBaseFilename=WhisperVoice_Setup_v{#AppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

LicenseFile=LICENSE
SetupLogging=yes
UninstallDisplayName={#AppName} {#AppVersion}
; --- Spójna ikona aplikacji ---
; whispervoice.ico ma identyczny wygląd (niebieskie koło z literą "W") jak ikona
; w zasobniku systemowym (tray, stan IDLE) — generowana z tej samej geometrii co
; main._draw_icon (zob. make_icon.py). Używana JEDNOCZEŚNIE przez: plik Setup.exe,
; skróty po instalacji oraz pozycję w „Programy i funkcje”. Dzięki temu ikona jest
; identyczna na każdym etapie: instalacja → zainstalowana aplikacja → tray.
SetupIconFile=whispervoice.ico
UninstallDisplayIcon={app}\whispervoice.ico

[Languages]
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "autostart";   Description: "Uruchamiaj WhisperVoice automatycznie przy starcie Windows (opcjonalnie)"; GroupDescription: "Autostart:"; Flags: unchecked
; CUDA: pozycja pojawia się tylko gdy wykryto kartę NVIDIA i jest DOMYŚLNIE
; ZAZNACZONA — akceleracja GPU znacząco (wielokrotnie) przyspiesza transkrypcję.
Name: "installcuda"; Description: "Zainstaluj komponenty GPU NVIDIA CUDA (~400 MB) — MOCNO ZALECANE: transkrypcja na GPU jest nawet kilkanaście razy szybsza niż na CPU"; GroupDescription: "Akceleracja GPU (NVIDIA):"; Check: IsNvidiaPresent

[Files]
; --- Ikona aplikacji (spójna: Setup.exe / skróty / tray) ---
Source: "whispervoice.ico";        DestDir: "{app}"; Flags: ignoreversion
; --- Aplikacja ---
Source: "main.py";                 DestDir: "{app}"; Flags: ignoreversion
Source: "config.py";               DestDir: "{app}"; Flags: ignoreversion
Source: "hallucinations.py";       DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt";        DestDir: "{app}"; Flags: ignoreversion
Source: "run.bat";                 DestDir: "{app}"; Flags: ignoreversion
Source: "run_silent.vbs";          DestDir: "{app}"; Flags: ignoreversion
Source: "install.bat";             DestDir: "{app}"; Flags: ignoreversion
Source: "fix_python_path.bat";     DestDir: "{app}"; Flags: ignoreversion
Source: "autostart_install.bat";   DestDir: "{app}"; Flags: ignoreversion

; --- Dokumentacja i licencje ---
Source: "LICENSE";                          DestDir: "{app}"; Flags: ignoreversion
Source: "README.md";                        DestDir: "{app}"; Flags: ignoreversion
Source: "INSTALL.md";                       DestDir: "{app}"; Flags: ignoreversion
Source: "TROUBLESHOOTING.md";               DestDir: "{app}"; Flags: ignoreversion
Source: "THIRD_PARTY_LICENSES.md";          DestDir: "{app}"; Flags: ignoreversion
Source: "THIRD_PARTY_LICENSES.txt";         DestDir: "{app}"; Flags: ignoreversion
Source: "NOTICE.md";                        DestDir: "{app}"; Flags: ignoreversion
Source: "CHANGELOG.md";                     DestDir: "{app}"; Flags: ignoreversion
Source: "DEPENDENCIES_AND_LICENSES_v3.0.md"; DestDir: "{app}"; Flags: ignoreversion
; Dokumenty Word (instrukcja, słowniczek) — dołączane jeśli istnieją
Source: "WhisperVoice_Instrukcja_v3.4.docx";    DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "Slowniczek_Techniczny.docx";           DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
; Skrót główny (tryb cichy, bez konsoli) — uruchamiany przez wscript.exe.
; IconFilename wymusza spójną ikonę "W" (a nie domyślną ikonę wscript.exe).
Name: "{group}\{#AppName}"; Filename: "wscript.exe"; Parameters: """{app}\{#AppExeVbs}"""; WorkingDir: "{app}"; IconFilename: "{app}\whispervoice.ico"; Comment: "WhisperVoice — lokalny voice-to-text"
; Skrót diagnostyczny (z konsolą)
Name: "{group}\{#AppName} (tryb diagnostyczny)"; Filename: "{app}\{#AppExeBat}"; WorkingDir: "{app}"; IconFilename: "{app}\whispervoice.ico"; Comment: "WhisperVoice — uruchomienie z konsolą diagnostyczną"
; Skróty do dokumentacji
Name: "{group}\Dokumentacja\Instrukcja użytkownika (Word)"; Filename: "{app}\WhisperVoice_Instrukcja_v3.4.docx"
Name: "{group}\Dokumentacja\Instrukcja instalacji (INSTALL)"; Filename: "{app}\INSTALL.md"
Name: "{group}\Dokumentacja\Rozwiązywanie problemów (TROUBLESHOOTING)"; Filename: "{app}\TROUBLESHOOTING.md"
Name: "{group}\Dokumentacja\Licencje komponentów (THIRD_PARTY_LICENSES)"; Filename: "{app}\THIRD_PARTY_LICENSES.md"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
; Skrót na pulpicie (opcjonalny)
Name: "{autodesktop}\{#AppName}"; Filename: "wscript.exe"; Parameters: """{app}\{#AppExeVbs}"""; WorkingDir: "{app}"; IconFilename: "{app}\whispervoice.ico"; Tasks: desktopicon
; Skrót autostartu (opcjonalny, domyślnie wyłączony) — w folderze Autostart użytkownika
Name: "{userstartup}\{#AppName}"; Filename: "wscript.exe"; Parameters: """{app}\{#AppExeVbs}"""; WorkingDir: "{app}"; IconFilename: "{app}\whispervoice.ico"; Tasks: autostart

[Run]
; Opcjonalne uruchomienie aplikacji po zakończeniu instalacji
Filename: "wscript.exe"; Parameters: """{app}\{#AppExeVbs}"""; WorkingDir: "{app}"; Description: "Uruchom {#AppName} teraz"; Flags: nowait postinstall skipifsilent
; Opcjonalne otwarcie instrukcji
Filename: "{app}\INSTALL.md"; Description: "Otwórz instrukcję instalacji"; Flags: shellexec nowait postinstall skipifsilent unchecked

[UninstallRun]
; Usuń skrót autostartu (jeśli był założony) — bez naruszania innych danych
Filename: "{cmd}"; Parameters: "/C del ""{userstartup}\{#AppName}.lnk"""; Flags: runhidden; RunOnceId: "DelAutostart"

; UWAGA: celowo NIE ma sekcji [UninstallDelete] usuwającej %APPDATA%\WhisperVoice.
; Logi diagnostyczne (error.log) oraz ustawienia użytkownika muszą przetrwać
; deinstalację. O ich usunięcie pytamy użytkownika w [Code] (CurUninstallStepChanged).

[Code]
var
  DownloadPage:   TDownloadWizardPage;
  ProgressPage:   TOutputProgressWizardPage;
  ComponentsPage: TOutputMsgMemoWizardPage;
  PythonExe:      String;
  PythonFound:    Boolean;
  HasNvidia:      Boolean;

{ ---------- Pomocnicze: log instalacji w %APPDATA%\WhisperVoice ---------- }
function InstallLogPath(): String;
begin
  Result := ExpandConstant('{userappdata}\WhisperVoice\install.log');
end;

procedure EnsureDataDir();
begin
  ForceDirectories(ExpandConstant('{userappdata}\WhisperVoice'));
end;

procedure AppendInstallLog(const Msg: String);
var
  Existing: AnsiString;
  Line: String;
begin
  EnsureDataDir();
  Line := '[' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', '-', ':') + '] ' + Msg + #13#10;
  Existing := '';
  LoadStringFromFile(InstallLogPath(), Existing);
  SaveStringToFile(InstallLogPath(), Existing + AnsiString(Line), False);
end;

{ ---------- Wykrywanie Pythona: PATH -> rejestr HKCU/HKLM -> foldery ----- }
function DetectPython(): String;
var
  rc: Integer;
  exe, ver: String;
  i: Integer;
begin
  Result := '';

  { 1. PATH }
  if Exec(ExpandConstant('{cmd}'), '/C python --version', '', SW_HIDE, ewWaitUntilTerminated, rc) and (rc = 0) then
  begin
    Result := 'python';
    Exit;
  end;

  { 2. Rejestr HKCU / HKLM PythonCore 3.16 .. 3.10 }
  for i := 16 downto 10 do
  begin
    ver := '3.' + IntToStr(i);
    if RegQueryStringValue(HKCU, 'SOFTWARE\Python\PythonCore\' + ver + '\InstallPath', 'ExecutablePath', exe) then
      if FileExists(exe) then begin Result := exe; Exit; end;
    if RegQueryStringValue(HKLM, 'SOFTWARE\Python\PythonCore\' + ver + '\InstallPath', 'ExecutablePath', exe) then
      if FileExists(exe) then begin Result := exe; Exit; end;
  end;

  { 3. Typowe foldery instalacji per-użytkownik }
  for i := 16 downto 10 do
  begin
    exe := ExpandConstant('{localappdata}') + '\Programs\Python\Python3' + IntToStr(i) + '\python.exe';
    if FileExists(exe) then begin Result := exe; Exit; end;
    exe := 'C:\Python3' + IntToStr(i) + '\python.exe';
    if FileExists(exe) then begin Result := exe; Exit; end;
  end;
end;

{ ---------- Wykrywanie karty NVIDIA (nvidia-smi w PATH) ------------------ }
function DetectNvidia(): Boolean;
var
  rc: Integer;
begin
  Result := Exec(ExpandConstant('{cmd}'), '/C where nvidia-smi', '', SW_HIDE, ewWaitUntilTerminated, rc) and (rc = 0);
end;

{ Check dla [Tasks]: pozycja CUDA pojawia się tylko gdy wykryto kartę NVIDIA.
  Domyślnie zaznaczona (brak flagi 'unchecked') — akceleracja GPU jest zalecana. }
function IsNvidiaPresent(): Boolean;
begin
  Result := HasNvidia;
end;

{ ---------- Treść ekranu "Komponenty do pobrania" ----------------------- }
function BuildComponentsMemo(): String;
var
  s: String;
begin
  s := 'Poniżej znajduje się PEŁNA, jawna lista komponentów, które instalator' + #13#10 +
       'może pobrać lub zainstalować. Nic nie jest pobierane po cichu.' + #13#10 + #13#10;

  s := s + '== 1. Python ' + '{#PyVersion}' + ' (środowisko uruchomieniowe) ==' + #13#10;
  if PythonFound then
    s := s + '   Status:      WYKRYTY na tym komputerze — NIE zostanie pobrany.' + #13#10
  else
  begin
    s := s + '   Status:      BRAK — zostanie POBRANY i zainstalowany.' + #13#10;
    s := s + '   Wersja:      {#PyVersion}' + #13#10;
    s := s + '   Rozmiar:     {#PySizeText}' + #13#10;
    s := s + '   Źródło:      {#PyUrl}' + #13#10;
    s := s + '   Po co:       interpreter potrzebny do uruchomienia aplikacji.' + #13#10;
    s := s + '   Licencja:    PSF License (permisywna, zgodna z MIT).' + #13#10;
    s := s + '   Weryfikacja: suma kontrolna MD5 (oficjalna z python.org).' + #13#10;
    s := s + '   Lokalizacja: instalacja per-użytkownik (bez administratora).' + #13#10;
  end;
  s := s + #13#10;

  s := s + '== 2. Biblioteki Python (z PyPI, przez pip) ==' + #13#10;
  s := s + '   Pakiety:     faster-whisper, numpy, sounddevice, keyboard,' + #13#10;
  s := s + '                pystray, Pillow, pyperclip' + #13#10;
  s := s + '   Rozmiar:     ~150–550 MB (zależnie od zależności)' + #13#10;
  s := s + '   Źródło:      https://pypi.org/ (oficjalne repozytorium PyPI)' + #13#10;
  s := s + '   Po co:       silnik transkrypcji, audio, schowek, hotkey, tray.' + #13#10;
  s := s + '   Licencje:    MIT / BSD-3-Clause / HPND / LGPL-3.0 (szczegóły:' + #13#10;
  s := s + '                THIRD_PARTY_LICENSES.md).' + #13#10;
  s := s + '   Lokalizacja: środowisko Python użytkownika.' + #13#10 + #13#10;

  s := s + '== 3. Komponenty GPU NVIDIA CUDA (MOCNO ZALECANE dla NVIDIA) ==' + #13#10;
  if HasNvidia then
  begin
    s := s + '   Status:      WYKRYTO kartę NVIDIA — zadanie jest DOMYŚLNIE' + #13#10;
    s := s + '                ZAZNACZONE (zalecane, możesz odznaczyć).' + #13#10;
  end
  else
    s := s + '   Status:      nie wykryto karty NVIDIA — krok zostanie pominięty.' + #13#10;
  s := s + '   Pakiet:      nvidia-cublas-cu12  (~400 MB)' + #13#10;
  s := s + '   Źródło:      https://pypi.org/project/nvidia-cublas-cu12/' + #13#10;
  s := s + '   Po co:       AKCELERACJA GPU. Transkrypcja na karcie NVIDIA jest' + #13#10;
  s := s + '                ZNACZĄCO szybsza niż na CPU — nawet kilkanaście razy' + #13#10;
  s := s + '                (np. ~5x szybciej niż real-time dla large-v3 na GPU,' + #13#10;
  s := s + '                vs. wolniej niż real-time na CPU). MOCNO REKOMENDOWANE,' + #13#10;
  s := s + '                jeśli masz kartę NVIDIA.' + #13#10;
  s := s + '   Licencja:    NVIDIA Software License Agreement (własnościowa).' + #13#10;
  s := s + '   Instalowany: gdy zaznaczone zadanie "komponenty GPU" (NVIDIA).' + #13#10 + #13#10;

  s := s + '== 4. Model Whisper large-v3 (NIE w instalatorze) ==' + #13#10;
  s := s + '   Rozmiar:     ~3 GB' + #13#10;
  s := s + '   Źródło:      https://huggingface.co/Systran/faster-whisper-large-v3' + #13#10;
  s := s + '   Po co:       wagi modelu rozpoznawania mowy.' + #13#10;
  s := s + '   Licencja:    MIT (OpenAI).' + #13#10;
  s := s + '   Kiedy:       pobierany przy PIERWSZYM uruchomieniu aplikacji,' + #13#10;
  s := s + '                NIE podczas tej instalacji. Aplikacja uprzedzi.' + #13#10 + #13#10;

  s := s + 'Klikając "Dalej" akceptujesz pobranie i instalację powyższych' + #13#10 +
           'komponentów wymaganych do działania aplikacji.';
  Result := s;
end;

{ ---------- Inicjalizacja kreatora -------------------------------------- }
procedure InitializeWizard();
begin
  { Wykrycie środowiska — wynik pokazany użytkownikowi na ekranie komponentów }
  PythonExe   := DetectPython();
  PythonFound := PythonExe <> '';
  HasNvidia   := DetectNvidia();

  { Strona z jawną listą komponentów (po wyborze zadań, przed instalacją) }
  ComponentsPage := CreateOutputMsgMemoPage(wpSelectTasks,
    'Komponenty wymagane i pobierane',
    'Co dokładnie zostanie zainstalowane i pobrane',
    'Przeczytaj uważnie — instalator działa w pełni jawnie:',
    BuildComponentsMemo());

  { Strona pobierania z paskiem postępu (wbudowana w Inno Setup 6.1+) }
  DownloadPage := CreateDownloadPage(
    'Pobieranie komponentów',
    'Trwa pobieranie wymaganych plików...', nil);

  { Strona postępu instalacji pakietów }
  ProgressPage := CreateOutputProgressPage(
    'Instalacja komponentów',
    'Trwa konfiguracja środowiska i instalacja bibliotek...');
end;

{ ---------- Memo na ekranie "Gotowy do instalacji" ---------------------- }
function UpdateReadyMemo(Space, NewLine, MemoUserInfoInfo, MemoDirInfo,
  MemoTypeInfo, MemoComponentsInfo, MemoGroupInfo, MemoTasksInfo: String): String;
var
  s: String;
begin
  s := MemoDirInfo + NewLine + NewLine;
  s := s + 'Komponenty do pobrania / instalacji:' + NewLine;
  if PythonFound then
    s := s + Space + '- Python: wykryty, nie będzie pobierany' + NewLine
  else
    s := s + Space + '- Python {#PyVersion} ({#PySizeText}) — zostanie pobrany z python.org' + NewLine;
  s := s + Space + '- Biblioteki Python z PyPI (faster-whisper i zależności)' + NewLine;
  if HasNvidia then
    s := s + Space + '- Komponenty GPU NVIDIA CUDA (MOCNO ZALECANE — duże przyspieszenie)' + NewLine;
  s := s + NewLine + MemoTasksInfo;
  Result := s;
end;

{ ---------- Pobranie i instalacja Pythona ------------------------------- }
function DownloadAndInstallPython(): Boolean;
var
  rc: Integer;
  gotMD5, downloadedPath: String;
begin
  Result := False;
  downloadedPath := ExpandConstant('{tmp}\') + '{#PyFile}';

  { --- Pobieranie z paskiem postępu i obsługą anulowania --- }
  DownloadPage.Clear;
  DownloadPage.Add('{#PyUrl}', '{#PyFile}', '');  { '' = brak sprawdzania SHA256 na stronie; MD5 weryfikujemy poniżej }
  DownloadPage.Show;
  try
    try
      DownloadPage.Download;
    except
      MsgBox('Nie udało się pobrać Pythona.' + #13#10 + #13#10 +
             'Najczęstsza przyczyna: brak połączenia z internetem lub blokada' + #13#10 +
             'firewall/proxy.' + #13#10 + #13#10 +
             'Sprawdź internet i uruchom instalator ponownie, albo zainstaluj' + #13#10 +
             'Python ręcznie z https://www.python.org/downloads/' + #13#10 +
             '(zaznacz "Add Python to PATH").' + #13#10 + #13#10 +
             'Szczegóły: ' + GetExceptionMessage, mbCriticalError, MB_OK);
      AppendInstallLog('BŁĄD pobierania Pythona: ' + GetExceptionMessage);
      DownloadPage.Hide;
      Exit;
    end;
  finally
    DownloadPage.Hide;
  end;

  { --- Weryfikacja integralności: MD5 oficjalny z python.org --- }
  gotMD5 := '';
  try
    gotMD5 := GetMD5OfFile(downloadedPath);
  except
    gotMD5 := '';
  end;
  if CompareText(gotMD5, '{#PyMD5}') <> 0 then
  begin
    MsgBox('Pobrany plik Pythona jest USZKODZONY lub niekompletny' + #13#10 +
           '(niezgodna suma kontrolna MD5).' + #13#10 + #13#10 +
           'Oczekiwano: {#PyMD5}' + #13#10 +
           'Otrzymano:  ' + gotMD5 + #13#10 + #13#10 +
           'Ze względów bezpieczeństwa instalator NIE uruchomi tego pliku.' + #13#10 +
           'Uruchom instalator ponownie (pobierze plik od nowa).',
           mbCriticalError, MB_OK);
    AppendInstallLog('BŁĄD MD5 Pythona. Oczekiwano {#PyMD5}, otrzymano ' + gotMD5);
    Exit;
  end;
  AppendInstallLog('Python pobrany i zweryfikowany (MD5 OK): ' + downloadedPath);

  { --- Cicha (z paskiem) instalacja per-użytkownik --- }
  ProgressPage.SetText('Instaluję Python {#PyVersion}...', 'To może potrwać 1–2 minuty.');
  ProgressPage.Show;
  try
    if not Exec(downloadedPath,
        '/passive InstallAllUsers=0 PrependPath=1 Include_pip=1 Include_launcher=1 Include_test=0',
        '', SW_SHOWNORMAL, ewWaitUntilTerminated, rc) then
    begin
      MsgBox('Nie udało się uruchomić instalatora Pythona.', mbCriticalError, MB_OK);
      AppendInstallLog('BŁĄD uruchomienia instalatora Pythona.');
      Exit;
    end;
  finally
    ProgressPage.Hide;
  end;
  AppendInstallLog('Instalator Pythona zakończony, kod: ' + IntToStr(rc));

  { --- Ponowne wykrycie Pythona --- }
  PythonExe := DetectPython();
  Result := PythonExe <> '';
  if not Result then
    MsgBox('Python został zainstalowany, ale instalator nie może go odnaleźć.' + #13#10 +
           'Uruchom ponownie ten instalator albo plik fix_python_path.bat' + #13#10 +
           'z folderu aplikacji po instalacji.', mbError, MB_OK);
end;

{ ---------- Uruchomienie pip (ukryte okno, log do pliku) ---------------- }
function RunPip(const Args: String; UseUser: Boolean): Integer;
var
  rc: Integer;
  full, userflag: String;
begin
  userflag := '';
  if UseUser then userflag := '--user ';
  { Wszystko leci przez cmd /C z przekierowaniem do logu — okno ukryte (SW_HIDE),
    a użytkownik widzi postęp na stronie kreatora, nie w terminalu. }
  full := '/C ""' + PythonExe + '" -m pip ' + userflag + Args +
          ' >> "' + InstallLogPath() + '" 2>&1"';
  if not Exec(ExpandConstant('{cmd}'), full, '', SW_HIDE, ewWaitUntilTerminated, rc) then
    rc := -1;
  Result := rc;
end;

{ ---------- Instalacja bibliotek Python -------------------------------- }
function InstallPythonPackages(): Boolean;
var
  rc: Integer;
  req: String;
begin
  Result := False;
  req := ExpandConstant('{app}\requirements.txt');

  ProgressPage.SetText('Aktualizuję menedżer pakietów pip...', '');
  ProgressPage.SetProgress(1, 5);
  ProgressPage.Show;

  RunPip('install --upgrade pip', False);  { ostrzeżenie nieblokujące }

  ProgressPage.SetText('Instaluję biblioteki: faster-whisper i zależności...',
                       'Pobieranie z PyPI — może potrwać kilka minut.');
  ProgressPage.SetProgress(2, 5);

  rc := RunPip('install -r "' + req + '"', False);
  if rc <> 0 then
  begin
    ProgressPage.SetText('Ponawiam instalację (tryb --user)...', '');
    rc := RunPip('install -r "' + req + '"', True);
  end;
  if rc <> 0 then
  begin
    ProgressPage.Hide;
    MsgBox('Instalacja bibliotek Python nie powiodła się.' + #13#10 + #13#10 +
           'Możliwe przyczyny:' + #13#10 +
           '  - brak połączenia z internetem (PyPI),' + #13#10 +
           '  - blokada przez firewall/proxy lub antywirus,' + #13#10 +
           '  - brak miejsca na dysku.' + #13#10 + #13#10 +
           'Szczegóły zapisano w:' + #13#10 + InstallLogPath() + #13#10 + #13#10 +
           'Po naprawieniu przyczyny uruchom instalator ponownie lub plik' + #13#10 +
           'install.bat z folderu aplikacji.', mbCriticalError, MB_OK);
    AppendInstallLog('BŁĄD instalacji pakietów (kod ' + IntToStr(rc) + ').');
    Exit;
  end;

  { --- Opcjonalne komponenty GPU NVIDIA --- }
  if HasNvidia and WizardIsTaskSelected('installcuda') then
  begin
    ProgressPage.SetText('Instaluję komponenty GPU NVIDIA CUDA (~400 MB)...', '');
    ProgressPage.SetProgress(3, 5);
    rc := RunPip('install nvidia-cublas-cu12', False);
    if rc <> 0 then RunPip('install nvidia-cublas-cu12', True);
    { Niepowodzenie CUDA nie jest krytyczne — aplikacja zadziała na CPU. }
  end;

  { --- Weryfikacja importów --- }
  ProgressPage.SetText('Weryfikuję poprawność instalacji...', '');
  ProgressPage.SetProgress(4, 5);
  rc := RunPip('--version', False);  { szybki sanity check pip }

  { Pełna weryfikacja importów przez python -c }
  if not Exec(ExpandConstant('{cmd}'),
      '/C ""' + PythonExe + '" -c "import faster_whisper, sounddevice, keyboard, pystray, PIL, pyperclip, numpy" >> "' + InstallLogPath() + '" 2>&1"',
      '', SW_HIDE, ewWaitUntilTerminated, rc) then
    rc := -1;
  if rc <> 0 then
  begin
    ProgressPage.Hide;
    MsgBox('Weryfikacja zależności nie powiodła się — nie wszystkie biblioteki' + #13#10 +
           'zaimportowały się poprawnie.' + #13#10 + #13#10 +
           'Szczegóły: ' + InstallLogPath() + #13#10 + #13#10 +
           'Uruchom install.bat z folderu aplikacji, aby dokończyć instalację.',
           mbCriticalError, MB_OK);
    AppendInstallLog('BŁĄD weryfikacji importów (kod ' + IntToStr(rc) + ').');
    Exit;
  end;

  ProgressPage.SetProgress(5, 5);
  ProgressPage.Hide;
  AppendInstallLog('Instalacja pakietów Python zakończona pomyślnie.');
  Result := True;
end;

{ ---------- Główny przepływ: po skopiowaniu plików --------------------- }
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    EnsureDataDir();
    AppendInstallLog('=== Instalacja WhisperVoice {#AppVersion} (build {#AppBuild}) ===');

    { 1. Python }
    if not PythonFound then
    begin
      if not DownloadAndInstallPython() then
        RaiseException('Instalacja przerwana: nie udało się przygotować środowiska Python. ' +
                       'Żadne biblioteki nie zostały zainstalowane. Uruchom instalator ponownie.');
    end
    else
      AppendInstallLog('Python wykryty: ' + PythonExe);

    { 2. Biblioteki Python }
    if not InstallPythonPackages() then
      RaiseException('Instalacja przerwana: biblioteki Python nie zostały poprawnie zainstalowane.');
  end;
end;

{ ---------- Deinstalacja: pytanie o dane użytkownika -------------------- }
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  dataDir: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    dataDir := ExpandConstant('{userappdata}\WhisperVoice');
    if DirExists(dataDir) then
    begin
      if MsgBox('Usunąć także dane użytkownika WhisperVoice?' + #13#10 + #13#10 +
                'Folder: ' + dataDir + #13#10 +
                'Zawiera: ustawienia (config_user.json), akceptację warunków' + #13#10 +
                'oraz logi diagnostyczne (error.log, install.log).' + #13#10 + #13#10 +
                'TAK  = usuń wszystko (pełne wyczyszczenie).' + #13#10 +
                'NIE  = zachowaj ustawienia i logi (zalecane).',
                mbConfirmation, MB_YESNO or MB_DEFBUTTON2) = IDYES then
      begin
        DelTree(dataDir, True, True, True);
      end;
    end;

    { Co NIE jest usuwane (informacyjnie dla użytkownika): }
    { - Python, pip i pakiety PyPI (mogły istnieć wcześniej / służyć innym programom) }
    { - sterowniki i komponenty NVIDIA }
    { - pobrany model Whisper w cache HuggingFace (~3 GB) — w razie potrzeby usuń ręcznie: }
    {   %USERPROFILE%\.cache\huggingface\hub }
  end;
end;
