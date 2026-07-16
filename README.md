# WhisperVoice v3.4

**Build: 02.06.2026 · Platforma docelowa: Windows 11 (Windows 10 64-bit kompatybilny)**

Darmowa aplikacja desktopowa udostępniana nieodpłatnie do użytku własnego.
Udostępniana **bez gwarancji** poprawnego działania (zobacz sekcję
*Odpowiedzialność* i plik `LICENSE`).

---

## Opis

WhisperVoice działa lokalnie na komputerze użytkownika i służy do transkrypcji mowy na tekst w czasie rzeczywistym. Przytrzymaj klawisz **Scroll Lock** → mów → puść → transkrybowany tekst zostaje wklejony do aktywnego pola tekstowego.

Hotkey można w każdej chwili zmienić z menu trayu — bez edycji plików konfiguracyjnych. Dostępnych jest siedem presetów (Scroll Lock, Prawy Alt, Prawy Ctrl, F12, F13, Ctrl+Space, Ctrl+Shift+R) oraz opcja **Własny…**, która otwiera okno przechwytujące dowolną kombinację klawiszy.

Aplikacja korzysta z modelu **Whisper large-v3** (OpenAI) uruchomionego przez bibliotekę **faster-whisper** (SYSTRAN) na silniku CTranslate2. Oznacza to identyczną jakość transkrypcji jak oryginalny Whisper, przy 3–5× niższym zużyciu pamięci GPU i znacznie krótszym czasie przetwarzania. Aplikacja działa w pełni offline po pierwszym uruchomieniu (model jest pobierany tylko raz, ~3 GB).

---

## Wymagania systemowe

- **Windows 11** (64-bit) — platforma docelowa; Windows 10 (64-bit) kompatybilny
- Python 3.10 lub nowszy (instalator pobierze Python 3.12.8, jeśli go brak)
- Mikrofon
- Połączenie z internetem przy pierwszym uruchomieniu (pobieranie modelu ~3 GB)
- Opcjonalnie: karta NVIDIA z minimum 4 GB VRAM (znacznie szybsza transkrypcja)

---

## Uruchomienie

- `run_silent.vbs` — uruchamia aplikację bez okna terminala (zalecane)
- `run.bat` — uruchamia z oknem konsoli (tryb debug / diagnostyka)

Aplikacja pojawia się jako ikona w zasobniku systemowym (tray). Kliknij prawym przyciskiem myszy na ikonę, aby zobaczyć menu.

---

## Konfiguracja

### Menu trayu (bez restartu aplikacji)

Klik prawym na ikonę WhisperVoice w trayu → **Ustawienia**:

- **Jakość modelu** — `tiny` / `base` / `small` / `medium` / `large-v2` / `large-v3`
- **Precyzja transkrypcji** — beam_size: 1, 5, 8, 10
- **Język rozpoznawania** — `pl`, `en`, auto-detekcja
- **Hotkey** — 7 popularnych presetów (Scroll Lock, Prawy Alt, Prawy Ctrl, F12, F13, Ctrl+Space, Ctrl+Shift+R) + pozycja **Własny…** otwierająca okno do przechwycenia dowolnej kombinacji klawiszy

Wszystkie zmiany są walidowane (np. odrzucenie kombinacji zarezerwowanej przez Windows) i zapisywane do `%APPDATA%\WhisperVoice\config_user.json`. Zachowują się między restartami aplikacji.

### Plik `config.py` (zaawansowane)

Plik `config.py` w folderze instalacji zawiera dodatkowe parametry, które nie są dostępne z trayu:

- `MODEL_SIZE`, `DEVICE`, `COMPUTE_TYPE` — domyślny model i urządzenie (zmiany z trayu mają wyższy priorytet)
- `HOTKEY` — wartość startowa (nadpisywana przez ustawienie z trayu w `config_user.json`)
- `LANGUAGE`, `BEAM_SIZE` — analogicznie
- `INITIAL_PROMPT`, `HOTWORDS` — kontekst i słowa kluczowe dla modelu
- profile VAD (`SHORT_VAD_PARAMETERS`, `DEFAULT_VAD_PARAMETERS`, `LONG_VAD_PARAMETERS`) — szczegóły detekcji mowy/ciszy

Po zmianach w `config.py` zrestartuj aplikację.

### Automatyczny dobór profilu transkrypcji

Profil transkrypcji jest wybierany automatycznie na podstawie długości nagrania:

| Długość nagrania | Profil       |
| ---------------: | :----------- |
| do 30 s          | SHORT        |
| 30–90 s          | SHORT\_PLUS  |
| 90 s – 10 min    | DEFAULT      |
| 10–29 min        | LONG         |

---

## Instalacja

**Zalecane — instalator graficzny:** uruchom `WhisperVoice_Setup_v3.4.exe`
i przejdź przez kreator. Instalator działa **per-użytkownik (bez administratora)**,
pokazuje **jawną listę** wszystkich pobieranych komponentów (Python, biblioteki,
opcjonalnie CUDA) z paskiem postępu, weryfikuje pobrany Python sumą kontrolną
i **nie instaluje niczego po cichu**. Szczegóły: `INSTALL.md`.

**Alternatywnie — ręcznie (gdy masz już Pythona):**

```
install.bat
```

Skrypt instaluje wszystkie wymagane pakiety Python. Przy pierwszym uruchomieniu
aplikacja pobierze model Whisper large-v3 (~3 GB) — wymagane połączenie z internetem.

Aby włączyć autostart z systemem Windows (opcjonalnie), uruchom:

```
autostart_install.bat
```

Pełna dokumentacja: `INSTALL.md` (instalacja), `TROUBLESHOOTING.md` (problemy),
`THIRD_PARTY_LICENSES.md` i `DEPENDENCIES_AND_LICENSES_v3.0.md` (zależności
i licencje), `CHANGELOG.md` (historia zmian).

---

## Brak zbierania danych

Aplikacja nie zbiera, nie przesyła ani nie przechowuje danych osobowych użytkownika.

Aplikacja działa w całości lokalnie na komputerze użytkownika. Nie posiada kont użytkowników, panelu logowania, systemu płatności ani mechanizmów śledzenia.

Niektóre komponenty zewnętrzne, w szczególności oprogramowanie NVIDIA, mogą działać zgodnie z własnymi zasadami licencyjnymi i politykami prywatności dostawcy.

---

## Odpowiedzialność

Aplikacja jest udostępniana bezpłatnie, w stanie „takim, jaki jest" („as is"), bez gwarancji poprawnego działania, przydatności do konkretnego celu, nieprzerwanego działania lub braku błędów.

Użytkownik korzysta z aplikacji na własną odpowiedzialność. Autor nie ponosi odpowiedzialności za szkody wynikające z użycia, modyfikacji lub nieprawidłowej konfiguracji aplikacji.

Powyższe ograniczenie odpowiedzialności obowiązuje w najszerszym zakresie dozwolonym przez obowiązujące prawo.

---

## Komponenty zewnętrzne

Aplikacja wykorzystuje komponenty open-source oraz opcjonalne komponenty NVIDIA wymagane do obsługi GPU.

Pełna lista licencji zamieszczona jest w plikach `THIRD_PARTY_LICENSES.md`
(kanoniczny), `THIRD_PARTY_LICENSES.txt` oraz `DEPENDENCIES_AND_LICENSES_v3.0.md`.

---

## Licencja

MIT License — Copyright (c) 2026 Mariusz Świerguła

Pełna treść licencji: plik `LICENSE`.

---

## Historia wersji

### WhisperVoice 1.0

Pierwsza publiczna wersja aplikacji. Wymagała bardziej technicznego podejścia do instalacji i konfiguracji — skierowana była przede wszystkim do użytkowników obeznanych z terminalem i Pythonem.

#### Funkcje v1.0

- **Transkrypcja mowy na tekst** — model Whisper large-v3 (GPU) lub medium (CPU), wybierany automatycznie
- **Hotkey: wyłącznie Scroll Lock** — stały, niezmienialny z poziomu interfejsu; zmiana wymagała edycji `config.py`
- **Ikona w zasobniku systemowym** z czterema kolorami: pomarańczowy (ładowanie), niebieski (gotowy), czerwony (nagrywa), fioletowy (przetwarza)
- **Konfiguracja wyłącznie przez `config.py`** — brak menu ustawień w trayu
- **Uruchamianie przez `run.bat`** — zawsze z oknem konsoli, bez trybu cichego
- **Automatyczne przełączanie GPU/CPU** — jeśli nie wykryto karty NVIDIA, aplikacja przechodziła na CPU z modelem medium

#### Instalacja v1.0 (ręczna, 5 kroków)

W przeciwieństwie do v2.0 instalacja wymagała ręcznego wykonania każdego kroku w terminalu:

1. **Instalacja Pythona** — pobranie z `python.org` i zainstalowanie z ręcznym zaznaczeniem opcji „Add Python to PATH" (bez tego nic nie działało)
2. **Uruchomienie `install.bat`** — instalacja bibliotek (3–5 minut)
3. **Instalacja CUDA ręcznie w terminalu** — wymagana dla kart NVIDIA:
   ```
   pip install nvidia-cublas-cu12
   ```
   (~550 MB; bez tego krok GPU nie działał)
4. **Pierwsze uruchomienie przez `run.bat`** — pobranie modelu Whisper large-v3 (~3 GB); oczekiwanie na komunikat `[WhisperVoice] Model gotowy!`
5. **Test w Notatniku** — weryfikacja działania hotkeyem Scroll Lock

Instalacja nie posiadała kreatora — każdy krok użytkownik wykonywał samodzielnie.

#### Konfiguracja v1.0 (`config.py`)

Wszystkie ustawienia znajdowały się w pliku `config.py`, edytowanym ręcznie w Notatniku. Po każdej zmianie wymagany był restart aplikacji.

| Parametr | Przykładowa wartość | Opis |
| --- | --- | --- |
| `MODEL_SIZE` | `"large-v3"` | Rozmiar modelu. `large-v3` = najlepsza jakość; `medium` dla słabszego GPU |
| `DEVICE` | `"cuda"` | Urządzenie: `"cuda"` = karta NVIDIA, `"cpu"` = procesor |
| `COMPUTE_TYPE` | `"int8_float16"` | Precyzja obliczeń. GTX 1660 Ti → `int8_float16`; RTX 3080+ → `float16`; CPU → `int8` |
| `LANGUAGE` | `"pl"` | Język: `"pl"` = polski, `"en"` = angielski, `None` = auto-wykrywanie |
| `HOTKEY` | `"scroll lock"` | Klawisz nagrywania (zmiana tylko tutaj, nie z GUI) |
| `BEAM_SIZE` | `5` | Jakość vs szybkość (zakres 1–10; wyżej = dokładniej i wolniej) |
| `MIN_DURATION` | `0.4` | Minimalna długość nagrania w sekundach; krótsze są ignorowane |
| `INJECT_METHOD` | `"clipboard"` | Sposób wklejania: `"clipboard"` = Ctrl+V (zalecane dla polskich znaków) |

Predefiniowane profile sprzętowe (wklejane ręcznie do `config.py`):

```python
# GTX 1660 Ti (6 GB VRAM) — laptop
MODEL_SIZE   = "large-v3"
DEVICE       = "cuda"
COMPUTE_TYPE = "int8_float16"

# RTX 3080 / 4080 / 4090 (10+ GB VRAM) — desktop
MODEL_SIZE   = "large-v3"
DEVICE       = "cuda"
COMPUTE_TYPE = "float16"

# Tylko CPU (brak karty NVIDIA)
MODEL_SIZE   = "medium"
DEVICE       = "cpu"
COMPUTE_TYPE = "int8"
```

---

## Historia zmian

**Build 02.06.2026 (v3.2)** — niezależny audyt końcowy. Spójna ikona aplikacji
(`whispervoice.ico`) na każdym etapie: instalator, skróty i tray. W instalatorze
dodano wyraźną rekomendację CUDA (mocno zalecane dla NVIDIA — duże przyspieszenie;
opcja domyślnie zaznaczona dla wykrytych kart). Zaktualizowano dokumenty Word
(instrukcja, słowniczek) do stanu v3.x. Szczegóły: `AUDIT_REPORT_v3.2.md`, `CHANGELOG.md`.

**Build 01.06.2026 (v3.1)** — faza stabilizacji. Pełne testy funkcjonalne i
stabilnościowe (rzeczywista transkrypcja polskiej mowy na GPU, scenariusze
błędne, logi). Poprawki: (1) odporność na uszkodzony `config_user.json`
(samonaprawa zamiast cichej odmowy zapisu ustawień); (2) wątek transkrypcji
przepisany na **daemon + queue** — zawieszona transkrypcja nie blokuje już
zamknięcia aplikacji. Wszystkie testy zaliczone. Szczegóły:
`STABILITY_TEST_REPORT_v3.1.md`, `CHANGELOG.md`.

**Build 01.06.2026 (v3.0)** — uporządkowanie projektu i instalatora. Nowy,
kompletny `final_installer_v3.0.iss` (Inno Setup): instalacja per-użytkownik bez
administratora, jawny ekran komponentów przed pobieraniem, automatyczne pobranie
Pythona z weryfikacją sumy kontrolnej MD5, instalacja bibliotek pip **bez okna
terminala** z paskiem postępu, brak „fałszywego sukcesu” przy błędzie zależności,
opcjonalny autostart (domyślnie wyłączony), deinstalator pytający o dane użytkownika.
Pełna dokumentacja i audyt licencji. Skorygowano listę komponentów NVIDIA
(usunięto nieużywane `winget`/GeForce Experience). Szczegóły: `CHANGELOG.md`.

**Build 17.05.2026** — submenu **Hotkey** w menu trayu z 7 popularnymi presetami i opcją **Własny…** (okno przechwytujące dowolny klawisz). Walidacja kandydata przed zapisem (odrzucenie klawiszy zarezerwowanych przez Windows). Zmiana hotkey nie wymaga restartu aplikacji ani edycji `config.py`.

**Build 16.05.2026** — 8 poprawek z audytu III: komunikat o pobieraniu modelu, weryfikacja sumy kontrolnej Pythona, sprawdzenie miejsca na dysku, fallback `pip --user`, walidacja DEVICE/MODEL_SIZE, logowanie stderr przy `run_silent.vbs`, detekcja Pythona do 3.16, `cuda_check.tmp` w `%APPDATA%`.

---

## FAQ

Poniższe pytania i odpowiedzi mają pomóc rozwiać wątpliwości dotyczące legalności, prywatności oraz zastosowanych technologii. Sekcja jest przeznaczona zarówno dla użytkowników bez wiedzy technicznej, jak i dla osób chcących dokładnie zrozumieć, z czego zbudowana jest aplikacja.

---

### Instalacja i pierwsze uruchomienie

**Czym jest plik `WhisperVoice_Setup_v3.4.exe`?**

To instalator aplikacji — plik uruchamiający proces instalacji na Twoim komputerze. Rozszerzenie `.exe` oznacza program wykonywalny systemu Windows. Nie musisz nic rozumieć z technikaliów — wystarczy na niego kliknąć dwa razy, tak samo jak instaluje się każdy inny program (np. przeglądarkę czy komunikator).

**Czy instalacja jest skomplikowana? Czy muszę umieć programować?**

Nie. Instalacja prowadzona jest przez kreator — czyli serię ekranów z przyciskami „Dalej" i „Zakończ". Wystarczy klikać zgodnie z instrukcjami na ekranie. Nie trzeba wpisywać żadnych komend, znać Pythona ani mieć doświadczenia technicznego.

**Co dokładnie robi instalator? Czy instaluje coś bez mojej wiedzy?**

Instalator informuje Cię na każdym kroku, co zostanie zainstalowane. Na ekranie powitalnym zobaczysz pełną listę: Python (środowisko uruchomieniowe), biblioteki do transkrypcji i obsługi dźwięku, oraz opcjonalnie komponenty NVIDIA jeśli masz kartę graficzną tej firmy. Model AI (~3 GB) jest pobierany osobno przy pierwszym uruchomieniu aplikacji — instalator też Cię o tym uprzedzi.

**Czy potrzebuję połączenia z internetem do instalacji?**

Tak, ale tylko raz — przy pierwszej instalacji i pierwszym uruchomieniu. Instalator pobiera Python (~28 MB, jeśli nie masz go zainstalowanego) oraz biblioteki (~150–550 MB). Przy pierwszym starcie aplikacja pobiera model Whisper (~3 GB). Po tym wszystkim aplikacja działa w pełni offline — bez internetu, bez konta, bez logowania.

**Czy muszę mieć uprawnienia administratora?**

Nie. Instalator działa w trybie „tylko dla mnie" — instaluje wszystko w przestrzeni Twojego konta użytkownika, bez potrzeby uprawnień administratora.

**Co jeśli instalacja się zatrzyma lub coś pójdzie nie tak?**

Instalator jest zaprojektowany tak, aby radzić sobie z typowymi problemami automatycznie (np. brak Pythona → pobierze go sam, błąd uprawnień pip → spróbuje alternatywnej metody). Jeśli mimo to coś nie zadziała, w folderze `%APPDATA%\WhisperVoice\` pojawią się pliki `error.log` i `install.log` z opisem problemu.

---

### Legalność

**Co oznaczają licencje wymienione przy komponentach (MIT, PSF, BSD, LGPL, HPND)?**

Licencje open-source określają, na jakich zasadach można używać, kopiować i modyfikować dane oprogramowanie. Poniżej krótkie wyjaśnienie każdej z nich, w kolejności od najbardziej do najmniej permisywnej:

| Licencja | Skrót od | Co oznacza w praktyce |
|---|---|---|
| **MIT** | Massachusetts Institute of Technology | Najbardziej liberalna. Możesz robić z kodem co chcesz — używać, modyfikować, sprzedawać — pod warunkiem zachowania informacji o autorze. Brak wymogu udostępniania własnych zmian. |
| **PSF** | Python Software Foundation | Licencja Pythona. Równie liberalna jak MIT — swobodne użycie komercyjne i prywatne. Wymaga zachowania nagłówka z informacją o licencji. |
| **BSD-3-Clause** | Berkeley Software Distribution (3 klauzule) | Podobna do MIT. Dodaje zakaz używania nazwy twórców do promocji produktów pochodnych bez zgody. W praktyce identyczna swoboda jak MIT. |
| **HPND** | Historical Permission Notice and Disclaimer | Historyczna licencja permisywna, poprzedniczka BSD. Identyczna swoboda użycia jak MIT — można używać komercyjnie i prywatnie bez ograniczeń. |
| **LGPL-3.0** | GNU Lesser General Public License v3 | Bardziej restrykcyjna. Jeśli *modyfikujesz* bibliotekę objętą LGPL, zmiany muszą być udostępnione na tej samej licencji. Jeśli jedynie *używasz* biblioteki jako komponentu (jak WhisperVoice używa pystray) — bez obowiązku udostępniania własnego kodu. |
| **NVIDIA EULA** | End User License Agreement | Własnościowa licencja. Zamknięty kod, nie ma możliwości modyfikacji ani redystrybucji. Użytek dozwolony zgodnie z warunkami NVIDIA — bezpłatnie, ale tylko na warunkach producenta. |

Wszystkie komponenty WhisperVoice (poza opcjonalnymi bibliotekami NVIDIA) korzystają z licencji permisywnych, które dopuszczają użytek prywatny i komercyjny bez dodatkowych formalności.

---

**Czy mogę legalnie korzystać z WhisperVoice?**

Tak. WhisperVoice jest udostępniany bezpłatnie na licencji MIT, która pozwala na swobodne używanie, kopiowanie i modyfikowanie oprogramowania — zarówno prywatnie, jak i w środowisku zawodowym. Pełna treść licencji znajduje się w pliku `LICENSE`.

**Czy aplikacja korzysta z czegoś, co wymaga osobnej zgody lub opłaty?**

Wszystkie kluczowe komponenty (Python, faster-whisper, CTranslate2, model Whisper large-v3) są opublikowane na licencji MIT lub równoważnie permisywnych licencjach open-source i mogą być używane bezpłatnie. Jedynym wyjątkiem są opcjonalne komponenty NVIDIA (sterowniki, biblioteka cuBLAS) — są one własnościowe i wymagają akceptacji warunków licencyjnych NVIDIA. Są one jednak instalowane wyłącznie gdy wykryto kartę graficzną NVIDIA i wyłącznie na potrzeby przyspieszenia GPU; bez karty NVIDIA nie są pobierane ani instalowane.

**Czy model AI (Whisper) jest legalny w użyciu komercyjnym?**

Tak. Model Whisper large-v3 opublikowany przez OpenAI jest dostępny na licencji MIT, która dopuszcza użytek zarówno prywatny, jak i komercyjny. WhisperVoice uruchamia ten model lokalnie — bez żadnego połączenia z serwerami OpenAI.

**Kto jest autorem i właścicielem aplikacji?**

Autorem i właścicielem aplikacji WhisperVoice jest Mariusz Świerguła (Copyright © 2026). Komponenty zewnętrzne pozostają własnością ich twórców — szczegóły w pliku `THIRD_PARTY_LICENSES.txt`.

---

### Prywatność i dane

**Czy aplikacja przesyła moje nagrania lub transkrypcje gdziekolwiek?**

Nie. WhisperVoice działa w całości lokalnie na Twoim komputerze. Audio jest przechwytywane przez mikrofon, przetwarzane na miejscu przez model Whisper uruchomiony lokalnie i wklejane bezpośrednio do aktywnego pola tekstowego. Żadne nagrania ani transkrypcje nie są przesyłane do internetu ani do jakichkolwiek zewnętrznych serwerów.

**Czy aplikacja zbiera dane o mnie lub moim sposobie użytkowania?**

Nie. Aplikacja nie posiada żadnych mechanizmów zbierania danych, telemetrii, kont użytkowników ani systemu śledzenia. Nie przesyła żadnych informacji — ani o użytkowniku, ani o urządzeniu.

**Gdzie są przechowywane moje ustawienia?**

Ustawienia (hotkey, model, język, precyzja) są przechowywane wyłącznie lokalnie w pliku `%APPDATA%\WhisperVoice\config_user.json` na Twoim komputerze. Plik ten nie jest w żaden sposób synchronizowany ani wysyłany poza urządzenie.

**Co z NVIDIA i prywatnością?**

Sama aplikacja WhisperVoice nie zbiera żadnych danych. Jednak opcjonalne oprogramowanie NVIDIA (w szczególności GeForce Experience, instalowane jedynie jako fallback podczas aktualizacji sterownika) może zbierać dane diagnostyczne lub telemetryczne zgodnie z własną polityką prywatności NVIDIA. Taka ewentualna transmisja danych jest całkowicie poza kontrolą WhisperVoice i leży wyłącznie po stronie NVIDIA.

**Czy WhisperVoice jest zgodny z RODO?**

Sama aplikacja nie przetwarza, nie przechowuje ani nie przesyła żadnych danych osobowych — co do zasady nie wchodzi więc w zakres obowiązków wynikających z RODO. Jeśli jednak używasz jej w środowisku, gdzie transkrybujesz wypowiedzi innych osób (np. nagrania spotkań), obowiązek zapewnienia zgodności z RODO spoczywa na użytkowniku, a nie na aplikacji.

---

### Użyte technologie i modele AI

**Jakiego modelu AI używa WhisperVoice?**

WhisperVoice korzysta z modelu **Whisper large-v3** opracowanego przez OpenAI. Jest to model rozpoznawania mowy (ASR — Automatic Speech Recognition) wytrenowany na obszernym zbiorze danych audio z publicznie dostępnych źródeł internetowych. Model obsługuje ponad 90 języków i jest szczególnie skuteczny w języku polskim i angielskim.

**Co to jest faster-whisper i czym różni się od oryginalnego Whispera?**

faster-whisper to reimplementacja oryginalnego modelu Whisper stworzona przez firmę SYSTRAN. Korzysta z silnika wnioskowania CTranslate2, który optymalizuje obliczenia tak, aby model działał 3–5 razy szybciej i zużywał znacznie mniej pamięci niż oryginalna implementacja OpenAI — przy identycznej jakości transkrypcji. WhisperVoice używa tych samych wag modelu (plików z parametrami sieci neuronowej), jedynie uruchamia je przez wydajniejszy silnik.

**Czy model AI uczy się na moich nagraniach lub je wysyła do twórców?**

Nie. Model jest pobrany lokalnie i działa wyłącznie na Twoim komputerze. Nie ma żadnego mechanizmu doskonalenia modelu na podstawie danych użytkowników — ani po stronie WhisperVoice, ani po stronie faster-whisper. Wagi modelu są statyczne i nie zmieniają się w trakcie użytkowania.

**Jakie biblioteki open-source zostały użyte do budowy aplikacji?**

WhisperVoice używa następujących komponentów open-source:

| Komponent | Licencja | Zastosowanie |
|---|---|---|
| Python 3.12 | PSF | Środowisko uruchomieniowe |
| faster-whisper | MIT | Transkrypcja mowy na tekst |
| CTranslate2 | MIT | Silnik wnioskowania dla modelu |
| sounddevice / PortAudio | MIT | Rejestrowanie dźwięku z mikrofonu |
| numpy | BSD-3-Clause | Przetwarzanie danych audio |
| keyboard | MIT | Globalne skróty + wklejanie (CTRL+V) i typowanie tekstu |
| pystray | LGPL-3.0 | Ikona i menu w zasobniku systemowym |
| Pillow | HPND | Obsługa obrazu ikony trayu |
| pyperclip | BSD-3-Clause | Dostęp do schowka systemowego |
| PyAV (`av`) + FFmpeg | BSD-3-Clause + LGPL-2.1 | Zależność pośrednia faster-whisper (biblioteki audio) |
| huggingface-hub, tokenizers | Apache-2.0 | Zależności pośrednie (pobieranie/tokenizacja) |
| onnxruntime | MIT | Zależność pośrednia (model VAD) |

> **Bez GPL/AGPL.** Projekt celowo nie zawiera zależności na licencji
> GPL/AGPL. Do wklejania używamy `keyboard` (MIT), a **nie** `pyautogui` —
> ten ostatni wciągał pakiet `mouseinfo` na licencji GPLv3.

Pełna lista z odnośnikami do repozytoriów i treści licencji znajduje się w plikach `THIRD_PARTY_LICENSES.md` / `THIRD_PARTY_LICENSES.txt` oraz `NOTICE.md`.

**Czy WhisperVoice wymaga połączenia z internetem do działania?**

Jedynie przy pierwszym uruchomieniu — do pobrania modelu Whisper large-v3 (~3 GB). Po pobraniu aplikacja działa w pełni offline. Połączenie z internetem nie jest wymagane do żadnej funkcji transkrypcji.

**Czy mogę używać mniejszego modelu, jeśli mam słabszy komputer?**

Tak. W menu trayu (Ustawienia → Jakość modelu) możesz wybrać lżejszy wariant: `tiny`, `base`, `small`, `medium`, `large-v2` lub `large-v3`. Mniejsze modele działają szybciej i wymagają mniej zasobów, kosztem nieco niższej dokładności transkrypcji. Każda zmiana modelu powoduje jednorazowe pobranie nowego wariantu (~70 MB – 3 GB zależnie od rozmiaru).
