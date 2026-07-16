@echo off
setlocal EnableDelayedExpansion
title WhisperVoice - Naprawa PATH Pythona

echo.
echo  =====================================================
echo   WhisperVoice - Naprawa PATH Pythona
echo   Uruchom raz, jesli aplikacja nie startuje.
echo  =====================================================
echo.

set "PYEXE="
set "PYDIR="

:: Sprawdz czy python juz jest w PATH
python --version >nul 2>&1
if not errorlevel 1 (
    echo  [OK] Python jest juz w PATH - nie trzeba nic robic.
    echo.
    python --version
    echo.
    pause
    exit /b 0
)

echo  Python nie jest w PATH. Szukam instalacji...
echo.

:: Szukaj w rejestrze HKCU
for /L %%V in (16,-1,10) do (
    for /f "tokens=2*" %%A in ('reg query "HKCU\SOFTWARE\Python\PythonCore\3.%%V\InstallPath" /v ExecutablePath 2^>nul') do (
        if exist "%%B" (
            set "PYEXE=%%B"
            for %%F in ("%%B") do set "PYDIR=%%~dpF"
            set "PYDIR=!PYDIR:~0,-1!"
            echo  [OK] Znaleziono Python 3.%%V
            echo       Sciezka: !PYDIR!
            goto :found
        )
    )
)

:: Szukaj w rejestrze HKLM
for /L %%V in (16,-1,10) do (
    for /f "tokens=2*" %%A in ('reg query "HKLM\SOFTWARE\Python\PythonCore\3.%%V\InstallPath" /v ExecutablePath 2^>nul') do (
        if exist "%%B" (
            set "PYEXE=%%B"
            for %%F in ("%%B") do set "PYDIR=%%~dpF"
            set "PYDIR=!PYDIR:~0,-1!"
            echo  [OK] Znaleziono Python 3.%%V
            echo       Sciezka: !PYDIR!
            goto :found
        )
    )
)

:: Szukaj w typowych folderach
for /L %%V in (16,-1,10) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python3%%V\python.exe" (
        set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python3%%V\python.exe"
        set "PYDIR=%LOCALAPPDATA%\Programs\Python\Python3%%V"
        echo  [OK] Znaleziono Python 3.%%V
        echo       Sciezka: !PYDIR!
        goto :found
    )
    if exist "C:\Python3%%V\python.exe" (
        set "PYEXE=C:\Python3%%V\python.exe"
        set "PYDIR=C:\Python3%%V"
        echo  [OK] Znaleziono Python 3.%%V
        echo       Sciezka: !PYDIR!
        goto :found
    )
)

echo  [BLAD] Nie znaleziono zadnej instalacji Pythona 3.10+.
echo.
echo  Zainstaluj Python z: https://www.python.org/downloads/
echo  Podczas instalacji zaznacz: "Add Python to PATH"
echo.
pause
exit /b 1

:found
echo.
echo  Dodaje Python do PATH uzytkownika...

:: Pobierz aktualny PATH uzytkownika z rejestru
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "CURPATH=%%B"

:: Sprawdz czy sciezka juz jest w PATH
echo !CURPATH! | find /i "!PYDIR!" >nul 2>&1
if not errorlevel 1 (
    echo  [OK] Sciezka juz jest w PATH.
    goto :verify
)

:: Zbuduj nowy PATH
if "!CURPATH!"=="" (
    set "NEWPATH=!PYDIR!"
) else (
    set "NEWPATH=!CURPATH!;!PYDIR!"
)

:: Zapisz do rejestru uzytkownika (nie wymaga admina)
reg add "HKCU\Environment" /v Path /t REG_EXPAND_SZ /d "!NEWPATH!" /f >nul 2>&1

if errorlevel 1 (
    echo  [BLAD] Nie udalo sie zapisac do rejestru.
    echo         Sprobuj uruchomic jako Administrator.
    pause
    exit /b 1
)

echo  [OK] Python dodany do PATH!

:verify
echo.
echo  Weryfikacja:
"!PYEXE!" --version
echo.
echo  =====================================================
echo   Gotowe! Uruchom WhisperVoice przez run.bat
echo   lub run_silent.vbs
echo.
echo   UWAGA: Otwarte okna cmd nie widza zmian PATH.
echo   Zamknij to okno i otworz nowe cmd jesli potrzeba.
echo  =====================================================
echo.
pause
endlocal
