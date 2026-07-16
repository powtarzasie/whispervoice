@echo off
chcp 65001 >nul
title WhisperVoice — Budowanie instalatora

echo.
echo  =====================================================
echo   WhisperVoice v3.4  ^|  build 15.07.2026
echo   Kompilacja instalatora Inno Setup
echo  =====================================================
echo.

:: ── Szukaj ISCC.exe w typowych lokalizacjach ─────────────────
set "ISCC="

if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    goto :found
)

if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
    goto :found
)

if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
    goto :found
)

:: Sprawdź PATH
where ISCC.exe >nul 2>&1
if not errorlevel 1 (
    set "ISCC=ISCC.exe"
    goto :found
)

echo  [BLAD] Nie znaleziono Inno Setup (ISCC.exe)!
echo.
echo  Pobierz i zainstaluj Inno Setup 6 ze strony:
echo  https://jrsoftware.org/isdl.php
echo.
echo  Po instalacji uruchom ponownie ten skrypt.
echo.
pause
exit /b 1

:found
echo  [OK] Znaleziono Inno Setup: %ISCC%
echo.

:: ── Sprawdź obecność skryptu .iss ────────────────────────────
set "SCRIPT=%~dp0final_installer_v3.4.iss"

if not exist "%SCRIPT%" (
    echo  [BLAD] Nie znaleziono pliku: %SCRIPT%
    echo         Upewnij sie ze skrypt .iss jest w tym samym folderze.
    pause
    exit /b 1
)

:: ── Utwórz folder Output\ ────────────────────────────────────
if not exist "%~dp0Output" (
    mkdir "%~dp0Output"
    echo  [OK] Utworzono folder Output\
)

:: ── Kompiluj ─────────────────────────────────────────────────
echo  Kompiluje instalator...
echo  (moze potrwac chwile — kompresja lzma2/ultra64)
echo.

"%ISCC%" "%SCRIPT%"

if errorlevel 1 (
    echo.
    echo  [BLAD] Kompilacja nie powiodla sie.
    echo         Sprawdz komunikaty powyzej.
    echo.
    pause
    exit /b 1
)

echo.
echo  =====================================================
echo   [OK] Instalator zostal utworzony!
echo.

set "OUTPUT=%~dp0Output\WhisperVoice_Setup_v3.4.exe"
if exist "%OUTPUT%" (
    echo   Plik: %OUTPUT%
    echo.
    echo   Rozmiar:
    for %%F in ("%OUTPUT%") do echo     %%~zF bajtow
) else (
    echo   Szukaj pliku .exe w folderze: %~dp0Output\
)

echo  =====================================================
echo.

:: Zapytaj czy otworzyc folder Output
set /p OPEN="  Otworzyc folder Output w Eksploratorze? [T/N]: "
if /i "%OPEN%"=="T" (
    explorer "%~dp0Output"
)

echo.
pause
