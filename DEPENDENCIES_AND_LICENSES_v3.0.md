# Zależności i licencje — WhisperVoice v3.0

build 01.06.2026

Dokument łączy **audyt zależności** (co aplikacja importuje, czym jest pokryte)
z **audytem licencyjnym**. Pełne noty atrybucyjne: `THIRD_PARTY_LICENSES.md`,
`NOTICE.md`.

---

## 1. Wymagana wersja Pythona

- **Minimum: Python 3.10** (kod używa składni `tuple[dict, str]`,
  `WhisperModel | None` — adnotacje typów z PEP 604, dostępne od 3.10).
- **Instalator pobiera: Python 3.12.8** (gdy brak na komputerze) — stabilna
  wersja z pełnym wsparciem kół (wheels) dla `ctranslate2`/`faster-whisper`.
- Detekcja w skryptach obsługuje 3.10–3.16.

---

## 2. Zależności jawne (`requirements.txt`)

| Pakiet | Przypięcie | Import w kodzie | Rola |
|--------|-----------|-----------------|------|
| faster-whisper | `>=1.0.0` | `from faster_whisper import WhisperModel` | transkrypcja |
| sounddevice | `>=0.4.6` | `import sounddevice as sd` | nagrywanie audio |
| numpy | `>=1.24.0` | `import numpy as np` | bufory/operacje audio |
| keyboard | `>=0.13.5` | `import keyboard` | globalny hotkey |
| pystray | `>=0.19.5` | `import pystray` | ikona/menu trayu |
| Pillow | `>=10.0.0` | `from PIL import Image, ImageDraw` | grafika ikony |
| pyperclip | `>=1.8.2` | `import pyperclip` | schowek (źródło tekstu do CTRL+V) |

> **Usunięto `pyautogui`** (było: wklejanie tekstu). Wciągał pakiet `mouseinfo`
> na licencji **GPLv3** (silny copyleft). Funkcję CTRL+V / typowania przejęła
> biblioteka `keyboard` (MIT, już w tabeli powyżej): `keyboard.send("ctrl+v")`
> oraz `keyboard.write(...)`. Świeża instalacja z `requirements.txt` nie pobiera
> już `pyautogui` ani jego poddrzewa (mouseinfo/pymsgbox/pyscreeze/pytweening/
> pygetwindow/pyrect).

**Pokrycie importów:** wszystkie zewnętrzne importy w `main.py` mają pokrycie
w `requirements.txt`. `import config` to lokalny moduł projektu (`config.py`),
nie zależność zewnętrzna.

**Zależności przechodnie (instalowane automatycznie przez pip):**
- `ctranslate2` (MIT) — silnik wnioskowania (pociągany przez faster-whisper),
- `tokenizers` (Apache-2.0), `huggingface-hub` (Apache-2.0), `onnxruntime`
  (MIT), `tqdm` (MPL-2.0/MIT) — pociągane przez faster-whisper,
- `av` / PyAV (BSD-3-Clause) — pociągany przez faster-whisper; jego koła pip
  **zawierają biblioteki FFmpeg (LGPL-2.1-or-later)** — patrz sekcja 4,
- `PortAudio` (MIT) — natywne wsparcie dla sounddevice.

**Uwaga o przypięciach:** użyto minimalnych wersji (`>=`). Dla maksymalnej
powtarzalności dystrybucji można w przyszłości zamrozić wersje (`pip freeze`),
kosztem braku automatycznych poprawek bezpieczeństwa. Dla aplikacji desktopowej
darmowej minimalne wersje są świadomym, rozsądnym kompromisem.

---

## 3. Biblioteki standardowe Pythona (bez instalacji)

`threading`, `time`, `os`, `sys`, `json`, `datetime`, `ctypes`, `queue`,
`math`, `inspect`, `tkinter`, `winsound`, `platform`, `importlib`, `traceback`.
Wchodzą w skład Pythona (PSF-2.0).

---

## 4. Zależności systemowe / natywne

| Zależność | Wymagana? | Skąd |
|-----------|-----------|------|
| Sterowniki audio Windows (WASAPI/MME przez PortAudio) | tak | wbudowane w Windows |
| Microsoft Visual C++ Runtime | zwykle obecne; wymagane przez koła natywne (ctranslate2) | Windows / Visual Studio Redistributable |
| Sterowniki NVIDIA + CUDA runtime (cuBLAS) | **tylko dla GPU** | `nvidia-cublas-cu12` (pip) + sterownik NVIDIA (użytkownik) |
| FFmpeg (samodzielna instalacja) | **nie jest wymagany** | audio jest przechwytywane jako PCM 16 kHz przez sounddevice i podawane do modelu jako tablica numpy — osobny FFmpeg w PATH nie jest potrzebny |
| FFmpeg (biblioteki w kołach PyAV) | **instalowany pośrednio** | `faster-whisper` twardo wymaga `av` (PyAV), którego koła pip zawierają biblioteki `libav*` (FFmpeg) na licencji LGPL-2.1 — patrz nota poniżej |

> **FFmpeg — dwa różne stwierdzenia, nie mylić ich:**
> 1. **Funkcjonalnie:** WhisperVoice nagrywa bezpośrednio z mikrofonu
>    (PCM float32 → numpy), więc **samodzielny** FFmpeg/`ffmpeg.exe` w PATH
>    nie jest potrzebny, a instalator go nie pobiera.
> 2. **Licencyjnie:** biblioteki FFmpeg i tak **trafiają na dysk** — są wbudowane
>    w koło pip pakietu `av` (PyAV), który jest twardą zależnością
>    `faster-whisper`. Dlatego FFmpeg (LGPL-2.1-or-later) **jest ujęty** w
>    `NOTICE.md` i `THIRD_PARTY_LICENSES`. Jako osobny, wymienialny pakiet pip
>    spełnia warunki LGPL (brak statycznego linkowania).

---

## 5. Licencje — podsumowanie

| Licencja (SPDX) | Komponenty | Typ |
|-----------------|-----------|-----|
| MIT | faster-whisper, CTranslate2, sounddevice, PortAudio, keyboard, onnxruntime, Whisper large-v3 | permisywna |
| BSD-3-Clause | numpy, pyperclip, PyAV (`av`) | permisywna |
| Apache-2.0 | huggingface-hub, tokenizers | permisywna |
| HPND | Pillow | permisywna |
| PSF-2.0 | Python | permisywna |
| MPL-2.0 / MIT | tqdm | słaba copyleft plikowa (bez wpływu na dystrybucję) |
| LGPL-3.0-only | pystray | słaba copyleft (ostrożność — patrz niżej) |
| LGPL-2.1-or-later | FFmpeg (wbudowany w koła PyAV) | słaba copyleft (ostrożność — patrz niżej) |
| NVIDIA EULA | nvidia-cublas-cu12, sterownik NVIDIA | własnościowa (opcjonalna) |

> **Brak GPL/AGPL:** projekt świadomie nie zawiera zależności na licencji
> GPL/AGPL. `pyautogui` usunięto, bo wciągał `mouseinfo` (GPLv3).

### Punkty wymagające ostrożności
- **pystray (LGPL-3.0):** używany jako niemodyfikowana biblioteka (dozwolone).
  Instalowany jako osobny pakiet pip → użytkownik może go wymienić/zaktualizować,
  co spełnia wymóg LGPL. Modyfikacja pystray pociągałaby obowiązek udostępnienia
  zmian na LGPL.
- **NVIDIA:** komponenty własnościowe, instalowane wyłącznie opcjonalnie i za
  zgodą użytkownika; podlegają EULA i polityce prywatności NVIDIA.

---

## 6. Mechanizm pobierania a licencje

| Etap | Co | Licencja | Weryfikacja |
|------|----|----------|-------------|
| Instalator (gdy brak Pythona) | Python 3.12.8 z python.org | PSF-2.0 | suma kontrolna **MD5** (oficjalna z python.org) |
| Instalator | biblioteki z PyPI | MIT/BSD/HPND/LGPL | integralność po stronie pip (HTTPS, hash z PyPI) |
| Instalator (opcjonalnie) | nvidia-cublas-cu12 z PyPI | NVIDIA EULA | integralność po stronie pip |
| 1. uruchomienie aplikacji | model Whisper large-v3 z HuggingFace | MIT | integralność po stronie huggingface-hub |

Wszystkie źródła są publiczne i pobierane po HTTPS. Żaden komponent nie jest
pobierany bez wcześniejszej, jawnej informacji dla użytkownika.
