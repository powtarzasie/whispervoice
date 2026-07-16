# WhisperVoice v3.4 — Instrukcja instalacji

**Platforma docelowa: Windows 11** (64-bit). Windows 10 64-bit pozostaje
kompatybilny.

---

## 1. Co robi instalator

`WhisperVoice_Setup_v3.4.exe` to kreator instalacji (Inno Setup). Działa
**w trybie per-użytkownik — nie wymaga uprawnień administratora**. Krok po
kroku, w pełni jawnie:

1. **Ekran powitalny** — informacja o aplikacji i wersji.
2. **Licencja** — treść licencji MIT (plik `LICENSE`).
3. **Wybór katalogu** — domyślnie
   `%LOCALAPPDATA%\Programs\WhisperVoice`; można zmienić.
4. **Opcje dodatkowe** (wszystkie domyślnie wyłączone):
   - skrót na pulpicie,
   - autostart przy starcie Windows,
   - instalacja komponentów GPU NVIDIA CUDA — **mocno zalecane, jeśli masz kartę
     NVIDIA** (transkrypcja nawet kilkanaście razy szybsza niż na CPU). Gdy
     wykryto kartę NVIDIA, ta opcja jest **domyślnie zaznaczona**.
5. **Ekran komponentów** — **pełna, jawna lista** tego, co zostanie pobrane
   i zainstalowane: nazwa, wersja, źródło, przeznaczenie, licencja i lokalizacja
   każdego elementu. To jest ekran potwierdzenia przed pobieraniem.
6. **Podsumowanie (Gotowy do instalacji)** — skrót wybranych opcji.
7. **Pobieranie i instalacja** — z paskiem postępu:
   - jeśli brak Pythona → pobranie Pythona z `python.org` i weryfikacja sumy
     kontrolnej MD5 przed uruchomieniem,
   - instalacja bibliotek Python z PyPI (`faster-whisper` i zależności)
     **bez okna terminala**,
   - opcjonalnie komponenty CUDA.
8. **Ekran końcowy** — możliwość natychmiastowego uruchomienia aplikacji.

> **Nic nie jest pobierane ani instalowane po cichu.** Przed pobraniem
> czegokolwiek widzisz pełną listę i ją zatwierdzasz.

---

## 2. Co zostaje pobrane i skąd

| Komponent | Wersja | Rozmiar | Źródło | Kiedy |
|---|---|---|---|---|
| Python | 3.12.8 | ~25,8 MB | python.org | tylko gdy brak na komputerze |
| Biblioteki Python (faster-whisper, numpy, sounddevice, keyboard, pystray, Pillow, pyperclip) | wg `requirements.txt` | ~150–550 MB | PyPI (pypi.org) | zawsze podczas instalacji |
| nvidia-cublas-cu12 (GPU, **mocno zalecane dla NVIDIA**) | najnowsza | ~400 MB | PyPI | gdy karta NVIDIA (opcja domyślnie zaznaczona) |
| Model Whisper large-v3 | — | ~3 GB | huggingface.co | **przy pierwszym uruchomieniu aplikacji**, nie podczas instalacji |

Po pierwszym pobraniu modelu aplikacja działa **w pełni offline**.

---

## 3. Wymagania

- Windows 11 (lub Windows 10) 64-bit.
- Mikrofon.
- Połączenie z internetem przy instalacji i pierwszym uruchomieniu.
- Ok. 4–5 GB wolnego miejsca (biblioteki + model).
- Opcjonalnie: karta NVIDIA z ≥4 GB VRAM (szybsza transkrypcja).

---

## 4. Instalacja krok po kroku

1. Pobierz / otrzymaj `WhisperVoice_Setup_v3.4.exe`.
2. Uruchom plik dwukrotnym kliknięciem.
   - Jeśli Windows pokaże **SmartScreen „Nieznany wydawca”** (plik nie jest
     podpisany certyfikatem) — kliknij **Więcej informacji → Uruchom mimo to**.
     To normalne dla darmowego, niepodpisanego oprogramowania.
3. Przejdź przez kolejne ekrany kreatora.
4. Na ekranie komponentów przeczytaj listę i kliknij **Dalej**.
5. Poczekaj na pobranie i instalację (pasek postępu).
6. Na końcu zaznacz „Uruchom WhisperVoice teraz” (opcjonalnie).

---

## 5. Pierwsze uruchomienie

Przy pierwszym starcie:
- pojawi się okno **akceptacji warunków** (jednorazowo),
- aplikacja pobierze **model Whisper large-v3 (~3 GB)** — okno informacyjne
  uprzedzi o rozmiarze i źródle,
- ikona w zasobniku systemowym (tray) zmieni kolor z **pomarańczowego**
  (ładowanie) na **niebieski** (gotowy).

Następnie: przytrzymaj **Scroll Lock**, mów, puść — tekst pojawi się w aktywnym
polu. Hotkey można zmienić w menu trayu (prawy klik na ikonę → Hotkey).

---

## 6. Instalacja alternatywna (bez instalatora EXE)

Jeśli wolisz nie używać instalatora, w folderze aplikacji znajdziesz skrypty:

- `install.bat` — instaluje biblioteki Python (wymaga zainstalowanego Pythona),
- `fix_python_path.bat` — dodaje Python do PATH, jeśli aplikacja go nie widzi,
- `run.bat` — uruchomienie z konsolą (diagnostyka),
- `run_silent.vbs` — uruchomienie bez konsoli (codzienne użycie),
- `autostart_install.bat` — ręczne włączenie autostartu.

---

## 7. Deinstalacja

Panel sterowania → *Aplikacje* → **WhisperVoice 3.4** → *Odinstaluj*
(lub skrót „Odinstaluj WhisperVoice” w menu Start).

Deinstalator:
- usuwa pliki aplikacji i skróty (w tym skrót autostartu),
- **pyta**, czy usunąć też dane użytkownika
  (`%APPDATA%\WhisperVoice\` — ustawienia i logi). Domyślnie **zachowuje**.
- **nie usuwa** Pythona, bibliotek pip, sterowników NVIDIA ani pobranego modelu
  (mogły istnieć wcześniej lub służyć innym programom). Model można usunąć
  ręcznie z `%USERPROFILE%\.cache\huggingface\hub`.

W razie problemów zobacz `TROUBLESHOOTING.md`.
