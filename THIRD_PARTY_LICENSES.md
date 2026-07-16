# Third-Party Licenses — WhisperVoice v3.4

build 15.07.2026 · Copyright (c) 2026 Mariusz Świerguła

Aplikacja korzysta z komponentów firm trzecich. Każdy komponent pozostaje
objęty własną licencją i własnością odpowiednich autorów/licencjodawców.
Autor aplikacji nie rości sobie praw do komponentów zewnętrznych.

> **Uwaga prawna:** to jest techniczny audyt licencyjny, **nie** porada prawna.

---

## Komponenty open-source (dołączane lub pobierane)

| # | Komponent | Wersja | Licencja (SPDX) | Źródło | Dołączenie | Funkcja |
|---|-----------|--------|-----------------|--------|------------|---------|
| 1 | Python | 3.12.x | PSF-2.0 | https://www.python.org/ | Pobierany przez instalator (gdy brak) | Środowisko uruchomieniowe |
| 2 | faster-whisper | ≥1.0.0 | MIT | https://github.com/SYSTRAN/faster-whisper | Pobierany przez pip | Silnik transkrypcji (Whisper na CTranslate2) |
| 3 | CTranslate2 | (zależność faster-whisper) | MIT | https://github.com/OpenNMT/CTranslate2 | Pobierany przez pip (pośrednio) | Silnik wnioskowania |
| 4 | sounddevice | ≥0.4.6 | MIT | https://github.com/spatialaudio/python-sounddevice | Pobierany przez pip | Nagrywanie dźwięku |
| 5 | PortAudio | (zależność sounddevice) | MIT | http://www.portaudio.com/ | Pobierany pośrednio | Wejście/wyjście audio |
| 6 | numpy | ≥1.24.0 | BSD-3-Clause | https://numpy.org/ | Pobierany przez pip | Obliczenia numeryczne audio |
| 7 | keyboard | ≥0.13.5 | MIT | https://github.com/boppreh/keyboard | Pobierany przez pip | Globalny hotkey + wklejanie (CTRL+V) i typowanie tekstu |
| 8 | pystray | ≥0.19.5 | LGPL-3.0-only | https://github.com/moses-palmer/pystray | Pobierany przez pip | Ikona/menu w trayu |
| 9 | Pillow | ≥10.0.0 | HPND | https://python-pillow.org/ | Pobierany przez pip | Grafika ikony trayu |
| 10 | pyperclip | ≥1.8.2 | BSD-3-Clause | https://github.com/asweigart/pyperclip | Pobierany przez pip | Schowek systemowy (źródło tekstu do CTRL+V) |
| 11 | Whisper large-v3 (wagi modelu) | large-v3 | MIT | https://huggingface.co/Systran/faster-whisper-large-v3 | Pobierany przy 1. uruchomieniu | Model rozpoznawania mowy |

> **Zmiana licencyjna (audyt):** wcześniejsze wersje używały `pyautogui`
> (BSD-3-Clause) do wklejania tekstu. `pyautogui` został **usunięty**, ponieważ
> jako twardą zależność wciągał pakiet `mouseinfo` na licencji **GPLv3** (silny
> copyleft, niezgodny z permisywną dystrybucją MIT). Jego funkcję (CTRL+V,
> typowanie) przejęła biblioteka `keyboard` (MIT), już obecna w projekcie.

### Zależności pośrednie (instalowane automatycznie przez pip z faster-whisper)

| # | Komponent | Licencja (SPDX) | Źródło | Funkcja |
|---|-----------|-----------------|--------|---------|
| T1 | huggingface-hub | Apache-2.0 | https://github.com/huggingface/huggingface_hub | Pobieranie modelu |
| T2 | tokenizers | Apache-2.0 | https://github.com/huggingface/tokenizers | Tokenizacja |
| T3 | onnxruntime | MIT | https://github.com/microsoft/onnxruntime | Model VAD (Silero) |
| T4 | tqdm | MPL-2.0 AND MIT | https://github.com/tqdm/tqdm | Pasek postępu pobierania |
| T5 | PyAV (`av`) | BSD-3-Clause | https://github.com/PyAV-Org/PyAV | Wiązania do FFmpeg (dekodowanie audio) |
| T6 | FFmpeg (w kołach PyAV) | **LGPL-2.1-or-later** | https://ffmpeg.org/ | Biblioteki libav* dołączone w kołach PyAV |

Biblioteki standardowe Pythona (`tkinter`, `ctypes`, `winsound`, `threading`
itd.) są częścią Pythona (PSF-2.0) i nie są wymieniane osobno.

---

## Komponenty własnościowe (opcjonalne, tylko dla GPU NVIDIA)

| # | Komponent | Licencja | Źródło | Kiedy |
|---|-----------|----------|--------|-------|
| 1 | nvidia-cublas-cu12 | NVIDIA Software License Agreement | https://pypi.org/project/nvidia-cublas-cu12/ | Instalowany przez pip **tylko** gdy wykryto kartę NVIDIA **i** użytkownik zaznaczył opcję GPU |
| 2 | NVIDIA Display Driver | NVIDIA EULA | https://www.nvidia.com/drivers | **Nie** instalowany przez aplikację — użytkownik instaluje go samodzielnie |

Pełna treść EULA NVIDIA: <https://docs.nvidia.com/cuda/eula/>.

> **Sprostowanie względem v2.0:** wcześniejsza dokumentacja wymieniała
> `winget` oraz `NVIDIA GeForce Experience` jako komponenty „używane podczas
> instalacji”. **Kod aplikacji ani instalatora ich nie wywołuje.** Zostały
> usunięte z listy. Aplikacja **nie pobiera, nie instaluje i nie aktualizuje**
> sterowników NVIDIA ani GeForce Experience.

---

## Uwagi licencyjne i ryzyka

- **MIT / BSD-3-Clause / HPND / PSF-2.0** — licencje permisywne. Wymagają
  zachowania informacji o prawach autorskich i treści licencji. Dopuszczają
  użytek prywatny i komercyjny. Brak obowiązku udostępniania własnego kodu.
- **pystray (LGPL-3.0-only)** — wymaga ostrożności. WhisperVoice **używa**
  pystray jako niemodyfikowanej biblioteki (dynamiczny import), co LGPL
  dopuszcza bez obowiązku udostępniania kodu aplikacji. Gdyby pystray został
  **zmodyfikowany**, zmiany należałoby udostępnić na LGPL-3.0. Należy zapewnić
  użytkownikowi możliwość podmiany/aktualizacji biblioteki (spełnione: pystray
  instalowany jest jako osobny pakiet pip, który można zaktualizować).
- **FFmpeg w kołach PyAV (LGPL-2.1-or-later)** — analogicznie do pystray:
  biblioteki FFmpeg są dostarczane wewnątrz osobnego, wymienialnego pakietu pip
  (`av`), nie są statycznie wkompilowane w kod WhisperVoice ani w jeden plik
  wykonywalny. Warunek LGPL (możliwość podmiany biblioteki) jest spełniony.
  ⚠ **Gdyby w przyszłości** aplikacja była pakowana przez PyInstaller/„one-file"
  exe, statyczne wbudowanie LGPL (pystray, FFmpeg) wymagałoby dodatkowych kroków
  (dostarczenie obiektów do relinkowania lub linkowanie dynamiczne) — obecny
  model dystrybucji (pip) tego problemu nie ma.
- **Brak komponentów GPL** — projekt świadomie **nie** zawiera zależności na
  licencji GPL/AGPL. Usunięto `pyautogui`, bo wciągał `mouseinfo` (GPLv3).
- **nvidia-cublas-cu12 (NVIDIA EULA)** — własnościowa. Można używać i
  redystrybuować zgodnie z warunkami NVIDIA; nie wolno modyfikować ani
  sprzedawać jako osobnego produktu. Instalowana wyłącznie opcjonalnie.
- **Wagi modelu Whisper (MIT, OpenAI)** — dopuszczają użytek prywatny i
  komercyjny; model działa lokalnie, bez połączenia z serwerami OpenAI.

Aplikacja jest darmowa, niekomercyjna i może być udostępniana nieodpłatnie.
Nie zwalnia to z obowiązków licencyjnych powyższych komponentów (zachowanie
not o prawach autorskich i treści licencji) — niniejszy plik je realizuje.

---

## Wyłączenie odpowiedzialności

Aplikacja jest dostarczana bezpłatnie i „w stanie takim, jaki jest” (AS IS),
bez gwarancji jakiegokolwiek rodzaju. Sama aplikacja nie zbiera, nie przesyła
ani nie przechowuje danych osobowych. Oprogramowanie firm trzecich (w tym
NVIDIA) może działać zgodnie z własnymi politykami; jest to poza kontrolą
WhisperVoice. Autor nie odpowiada za komponenty firm trzecich.
