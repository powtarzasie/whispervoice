@echo off
title WhisperVoice v3.4 - Autostart

set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SCRIPT=%~dp0run_silent.vbs"
set "LINK=%STARTUP%\WhisperVoice.lnk"

echo.
echo  WhisperVoice v3.4  |  Autostart
echo  Tworze skrot autostartu...

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%LINK%'); $s.TargetPath = 'wscript.exe'; $s.Arguments = '\"'%SCRIPT%'\"'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'WhisperVoice v3.4 voice-to-text'; $s.Save()"

if exist "%LINK%" (
    echo  [OK] Autostart wlaczony.
    echo       Skrot dodany do: %STARTUP%
    echo.
    echo       Aby WYLACZYC autostart, usun plik:
    echo       %LINK%
) else (
    echo  [BLAD] Nie udalo sie utworzyc skrotu.
    echo         Sprobuj uruchomic jako Administrator.
)

echo.
pause
