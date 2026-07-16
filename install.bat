@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1
title WhisperVoice v3.4 - Instalacja pakietow
cd /d "%~dp0"

:: Folder na pliki runtime (logi, cuda_check itd.) - zawsze zapisywalny
set "WV_DATA=%APPDATA%\WhisperVoice"
if not exist "%WV_DATA%" mkdir "%WV_DATA%"

echo.
echo =====================================================
echo   WhisperVoice v3.4  ^|  build 15.07.2026
echo   Instalacja wymaganych komponentow
echo =====================================================
echo.
echo   Co zostanie zainstalowane:
echo     [1/4] Aktualizacja pip (menedzer pakietow Python)
echo     [2/4] Biblioteka Whisper AI (faster-whisper ~150 MB)
echo           oraz pakiety: sounddevice, keyboard, pystray,
echo           Pillow, pyperclip, numpy
echo     [3/4] Komponenty GPU NVIDIA CUDA (~400 MB, tylko NVIDIA)
echo     [4/4] Weryfikacja instalacji
echo.
echo   UWAGA: Przy pierwszym uruchomieniu aplikacji zostanie
echo   pobrany model Whisper large-v3 (~3 GB). Wymagany internet.
echo.
echo =====================================================
echo.

set "PYTHON="

python --version >nul 2>&1
if not errorlevel 1 ( set "PYTHON=python" & goto :found )

for /L %%V in (16,-1,10) do (
    for /f "tokens=2*" %%A in ('reg query "HKCU\SOFTWARE\Python\PythonCore\3.%%V\InstallPath" /v ExecutablePath 2^>nul') do (
        if exist "%%B" ( set "PYTHON=%%B" & goto :found )
    )
)

for /L %%V in (16,-1,10) do (
    for /f "tokens=2*" %%A in ('reg query "HKLM\SOFTWARE\Python\PythonCore\3.%%V\InstallPath" /v ExecutablePath 2^>nul') do (
        if exist "%%B" ( set "PYTHON=%%B" & goto :found )
    )
)

for /L %%V in (16,-1,10) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python3%%V\python.exe" (
        set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python3%%V\python.exe"
        goto :found
    )
    if exist "C:\Python3%%V\python.exe" (
        set "PYTHON=C:\Python3%%V\python.exe"
        goto :found
    )
    if exist "C:\Program Files\Python3%%V\python.exe" (
        set "PYTHON=C:\Program Files\Python3%%V\python.exe"
        goto :found
    )
)

echo [BLAD] Nie znaleziono Pythona 3.10 lub nowszego!
echo.
echo Pobierz Python ze strony: https://www.python.org/downloads/
echo.
pause
exit /b 1

:found
echo [OK] Python znaleziony: !PYTHON!
echo.

echo [1/4] Aktualizacja pip...
"!PYTHON!" -m pip install --upgrade pip -q
if errorlevel 1 (
    echo [OSTRZEZENIE] Aktualizacja pip nie powiodla sie - kontynuuje.
)
echo [OK] pip gotowy.
echo.

echo [2/4] Instalacja Whisper AI i pakietow pomocniczych...
echo.
echo   Lista pobieranych pakietow:
echo     - faster-whisper  : silnik Whisper AI (OpenAI) ~150 MB
echo     - numpy           : obliczenia numeryczne dla audio
echo     - sounddevice     : nagrywanie dzwieku z mikrofonu
echo     - keyboard        : globalny skrot klawiszowy (Scroll Lock)
echo     - pystray         : ikona w zasobniku systemowym (tray)
echo     - Pillow          : grafika ikony trayu
echo     - pyperclip       : operacje na schowku systemowym (wklejanie CTRL+V)
echo.
echo   Moze potrwac kilka minut - prosze czekac...
echo.
"!PYTHON!" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo [INFO] Pierwsza proba pip install nie powiodla sie.
    echo        Probuje ponownie z flaga --user (instalacja per-uzytkownik)...
    echo.
    "!PYTHON!" -m pip install --user -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [BLAD] Instalacja pakietow nie powiodla sie (rowniez z --user).
        echo        Sprawdz komunikaty powyzej i polaczenie z internetem.
        echo        Mozliwe przyczyny:
        echo          - brak polaczenia z PyPI ^(firewall/proxy^)
        echo          - brak miejsca na dysku
        echo          - antywirus blokujacy pip
        echo.
        pause
        exit /b 1
    )
    echo [OK] Pakiety zainstalowane przez pip --user.
)
echo.
echo [OK] Whisper AI i pakiety pomocnicze zainstalowane.
echo.

echo [3/4] Sprawdzam dostepnosc GPU NVIDIA (CUDA)...
where nvidia-smi >nul 2>&1
if not errorlevel 1 (
    echo [GPU] Wykryto sterowniki NVIDIA. Sprawdzam karte...
    nvidia-smi --query-gpu=name --format=csv,noheader 2>nul
    echo.
    echo [GPU] Instalowanie komponentow CUDA (nvidia-cublas-cu12 ~400 MB)...
    echo       Wymagane do szybkiej transkrypcji na karcie NVIDIA.
    "!PYTHON!" -m pip install nvidia-cublas-cu12 -q
    if errorlevel 1 (
        "!PYTHON!" -m pip install --user nvidia-cublas-cu12 -q
        if errorlevel 1 (
            echo [OSTRZEZENIE] Instalacja nvidia-cublas-cu12 nie powiodla sie.
            echo              Aplikacja bedzie dzialac w trybie CPU.
        ) else (
            echo [OK] Komponenty CUDA GPU zainstalowane (pip --user).
        )
    ) else (
        echo [OK] Komponenty CUDA GPU zainstalowane.
    )
) else (
    echo [INFO] Brak sterownikow NVIDIA - pomijam CUDA (~400 MB oszczednosci).
    echo        Aplikacja bedzie dzialac w trybie CPU.
    echo        Karta NVIDIA? Zainstaluj sterowniki: https://www.nvidia.com/drivers
)

echo.
:: cuda_check.tmp - pelna sciezka w %APPDATA%\WhisperVoice (zapisywalne nawet gdy app w Program Files)
"!PYTHON!" -c "import os, ctranslate2; n=ctranslate2.get_cuda_device_count(); d=os.environ.get('APPDATA',''); p=os.path.join(d,'WhisperVoice'); os.makedirs(p, exist_ok=True); open(os.path.join(p,'cuda_check.tmp'),'w').write(str(n)); print('[OK] Wykryto', n, 'GPU NVIDIA z CUDA.' if n > 0 else '[INFO] Tryb CPU aktywny.')" 2>nul
echo.

echo [4/4] Weryfikacja instalacji...
"!PYTHON!" -c "import faster_whisper, sounddevice, keyboard, pystray, PIL, pyperclip, numpy; print('[OK] Wszystkie pakiety zaladowane poprawnie.')"
if errorlevel 1 (
    echo [BLAD] Weryfikacja nie powiodla sie - sprawdz powyzsze komunikaty.
    pause
    exit /b 1
)
echo.

echo =====================================================
echo   [OK] Instalacja zakonczona pomyslnie!
echo.
echo   WAZNE - PIERWSZE URUCHOMIENIE:
echo   Aplikacja pobierze model Whisper AI (~3 GB) automatycznie.
echo   Wymagane polaczenie z internetem - tylko raz!
echo   Kolejne uruchomienia nie wymagaja internetu.
echo.
echo   Uruchomienie aplikacji:
echo     - Skrot w Menu Start (WhisperVoice)
echo     - run_silent.vbs  (bez konsoli, codzienne uzycie)
echo     - run.bat         (tryb debug z konsola)
echo =====================================================
echo.
pause
endlocal
