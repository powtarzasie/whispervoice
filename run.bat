@echo off
setlocal EnableDelayedExpansion
title WhisperVoice v3.4
cd /d "%~dp0"

echo WhisperVoice v3.4  --  build 15.07.2026
echo.

:: Szukaj python.exe (nie wymaga PATH)
set "PYTHON="

:: 1. PATH
python --version >nul 2>&1
if not errorlevel 1 ( set "PYTHON=python" & goto :run )

:: 2. Rejestr HKCU (instalacja dla biezacego uzytkownika)
for /L %%V in (16,-1,10) do (
    for /f "tokens=2*" %%A in ('reg query "HKCU\SOFTWARE\Python\PythonCore\3.%%V\InstallPath" /v ExecutablePath 2^>nul') do (
        if exist "%%B" (
            set "PYTHON=%%B"
            goto :run
        )
    )
)

:: 3. Rejestr HKLM (instalacja dla wszystkich uzytkownikow)
for /L %%V in (16,-1,10) do (
    for /f "tokens=2*" %%A in ('reg query "HKLM\SOFTWARE\Python\PythonCore\3.%%V\InstallPath" /v ExecutablePath 2^>nul') do (
        if exist "%%B" (
            set "PYTHON=%%B"
            goto :run
        )
    )
)

:: 4. Typowe foldery instalacji
for /L %%V in (16,-1,10) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python3%%V\python.exe" (
        set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python3%%V\python.exe"
        goto :run
    )
    if exist "C:\Python3%%V\python.exe" (
        set "PYTHON=C:\Python3%%V\python.exe"
        goto :run
    )
)

echo [BLAD] Nie znaleziono Pythona 3.10 lub nowszego!
echo.
echo Zainstaluj Python z: https://www.python.org/downloads/
echo Lub uruchom fix_python_path.bat z tego folderu.
echo.
pause
exit /b 1

:run
echo Python: !PYTHON!
echo Uruchamianie main.py...
echo.

:: Log trafia do %APPDATA%\WhisperVoice\ (zawsze zapisywalny, nawet gdy app jest w Program Files)
set "LOGDIR=%APPDATA%\WhisperVoice"
if not exist "!LOGDIR!" mkdir "!LOGDIR!"
set "LOGFILE=!LOGDIR!\error.log"

:: Dopisuj (>>) zamiast nadpisywac (>) — historia bledow nie ginie po restarcie
echo. >> "!LOGFILE!"
echo [%date% %time%] --- Uruchomienie WhisperVoice (run.bat) --- >> "!LOGFILE!"

"!PYTHON!" main.py 2>> "!LOGFILE!"

if errorlevel 1 (
    echo.
    echo [BLAD] Aplikacja zakonczyla sie z bledem.
    echo        Szczegoly w: !LOGFILE!
    echo.
    type "!LOGFILE!"
    echo.
    pause
)
endlocal
