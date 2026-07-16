# Changelog — WhisperVoice

Wszystkie istotne zmiany w projekcie. Format zgodny z duchem
[Keep a Changelog](https://keepachangelog.com/); wersjonowanie semantyczne.

---

## [3.4] — 2026-06-14 · finalizacja builda 2026-07-15

### Naprawione — halucynacje Whispera i spójność wersji (2026-07-15)

- **Halucynacje modelu na ciszy/szumie — nowy, dwuwarstwowy filtr.** Whisper
  large-v3 na fragmentach ciszy (m.in. ogon nagrania po puszczeniu hotkeya,
  przypadkowe muśnięcia klawisza, oddech) „dopowiadał" gotowe frazy z danych
  treningowych YouTube — np. „Wszystkie informacje … w opisie filmu",
  „Napisy … przygotowane przez … Amara.org", „Subskrybuj". Wbudowany
  `no_speech_threshold` ich nie odrzucał, bo model generuje je z WYSOKĄ pewnością
  (`avg_logprob`), a poprzedni filtr porównywał tylko dokładne podłańcuchy z
  niekompletnej listy fraz.
  - **Warstwa 1** — wydzielony, czysty moduł `hallucinations.py`: wzorce (regex)
    odporne na warianty + zerowanie całości, gdy nagrano samą halucynację.
  - **Warstwa 2** — w `main.py` odrzucanie całych segmentów o wysokim
    `no_speech_prob`, których treść pasuje do wzorca (oba warunki naraz →
    minimalne ryzyko ucięcia cichej, prawdziwej mowy). Próg konfigurowalny:
    `NO_SPEECH_DROP_THRESHOLD` w `config.py`.
  - Testy regresyjne offline (bez modelu): `dev-tools/test_hallucinations.py`.
  (`hallucinations.py`, `main.py`, `config.py`, `dev-tools/`)
- **Ujednolicono numer wersji na 3.4 w całym kodzie.** `main.py` raportował
  wewnętrznie `3.3` (nagłówek, log startowy, okno „O aplikacji") mimo instalatora
  i dokumentacji 3.4. Zsynchronizowano `_APP_VERSION`, docstring i „O aplikacji"
  oraz nagłówek `config.py`; datę builda ustawiono na 2026-07-15.
  (`main.py`, `config.py`, `final_installer_v3.4.iss`, `build_installer.bat`)
- **Domknięcie spójności wersji i pisowni nazwiska przed publikacją na GitHub
  (2026-07-16).** Pozostałe nagłówki skryptów i licencji (`run.bat`,
  `run_silent.vbs`, `install.bat`, `autostart_install.bat`, `requirements.txt`,
  `LICENSE`, `NOTICE.md`, `THIRD_PARTY_LICENSES.txt/.md`) miały jeszcze
  „v3.2 | build 02.06.2026" — ujednolicono do „v3.4 | build 15.07.2026" (spójnie
  z `AppBuild` w `.iss`). Skorygowano pisownię nazwiska autora na **„Mariusz
  Świerguła"** we wszystkich plikach bieżących (LICENSE, NOTICE, README,
  THIRD_PARTY, `.iss`, landing `docs/index.html`). Wpis historyczny w sekcji
  [3.0] pozostaje bez zmian.

### Naprawione

- **Usunięto `Pause / Break` jako hotkey — był nieużywalny dla trybu
  „trzymaj-by-nagrywać".** Na Windows klawisz Pause/Break dostarcza kod
  naciśnięcia i puszczenia **razem, w jednej serii, już przy fizycznym
  wciśnięciu** (sekwencja scancode `E1 1D 45`); przy puszczeniu nie wysyła nic.
  W modelu press=start / release=stop oznaczało to, że nagrywanie zatrzymywało
  się natychmiast po starcie → nagranie miało ~0 długości i było odrzucane przez
  `MIN_DURATION` → hotkey „nic nie robił". Tego nie da się naprawić w kodzie —
  to zachowanie samego klawisza. (`main.py`)
  - Usunięto preset `Pause / Break` z menu traya.
  - Dialog „Własny…" odrzuca teraz Pause/Break z wyjaśnieniem.
  - Migracja przy starcie: zapisany w configu `pause` jest automatycznie
    podmieniany na działający `Scroll Lock` (zamiast martwego hotkeya).
  - Poprawiono komunikat walidacji, który wcześniej błędnie zalecał Pause/Break.

### Zmienione

- **Zalecany hotkey wraca na `Scroll Lock`** — sprawdzony, domyślny od wcześniejszych
  wersji, obecny na każdej klawiaturze (uwaga: gdy włączony, w Excelu strzałki
  przewijają arkusz — patrz TROUBLESHOOTING). Nowa kolejność presetów:
  Scroll Lock *(zalecane)*, Prawy Ctrl, Prawy Alt, F13, Ctrl+Space, Własny…
  (`main.py`)

---

## [3.3] — 2026-06-07 (uzupełnione 2026-06-12)

### Naprawione

- **Audyt licencyjny (12.06): usunięto `pyautogui`** — wciągał zależność
  `mouseinfo` na licencji **GPLv3** (silny copyleft, niezgodny z dystrybucją MIT).
  Wklejanie (CTRL+V) i typowanie przejęła biblioteka `keyboard` (MIT):
  `keyboard.send("ctrl+v")`, `keyboard.write(...)`. Zaktualizowano
  requirements.txt, install.bat, instalator (.iss), NOTICE i THIRD_PARTY_LICENSES.
  (`main.py`, `requirements.txt`, `install.bat`, `final_installer_v3.3.iss`)
- **Walidacja własnego hotkeya (12.06):** dialog „Własny…" odrzuca teraz
  pojedyncze klawisze piszące/nawigacyjne (litery, cyfry, spacja, Enter, Tab,
  strzałki itp.) — taki hotkey byłby rejestrowany z `suppress=True` i blokowałby
  klawisz we WSZYSTKICH aplikacjach w systemie. (`main.py`)
- **Instalator pakuje aktualną instrukcję** `WhisperVoice_Instrukcja_v3.3.docx`
  (wcześniej starą `_UPDATED.docx`) + skrót „Instrukcja użytkownika (Word)"
  w Menu Start. (`final_installer_v3.3.iss`)
- **Instrukcja (docx):** naprawiono pomieszany akapit „NOWE w v3.3", dodano wpis
  v3.3 do historii zmian (i poprawiono datę buildu v3.2), dodano sekcję
  „11. Licencja i zastrzeżenia" (MIT, AS IS, odesłanie do NOTICE).

- **Hotkey z modyfikatorem (np. Ctrl+Space) nie blokuje już CTRL+C / CTRL+V / CTRL+Z.**
  Poprzednio `keyboard.add_hotkey(..., suppress=True)` instalował globalny hook,
  który przy hotkeyach zawierających modyfikator (Ctrl, Alt, Shift) blokował
  powiązane kombinacje w innych aplikacjach. Naprawiono: `suppress=False` gdy
  hotkey zawiera modyfikator. (`main.py`)
- **Prawy Alt jako hotkey nie blokuje już polskich znaków (AltGr: ą ę ó ź ż).**
  Poprzednio `on_press_key("right alt", ..., suppress=True)` przechwytywał każde
  wciśnięcie prawego Alt zanim dotarło do systemu, uniemożliwiając wpisywanie
  polskich znaków przez AltGr. Naprawiono: `suppress=False` dla wszystkich
  gołych modyfikatorów (right alt, right ctrl). (`main.py`)
- **Prawy Ctrl i Prawy Alt nie wyzwalają już aplikacji przy lewostronnych skrótach (Lewy Ctrl+V itp.)**
  `keyboard.on_press_key("right ctrl")` normalizowało nazwę klawisza i dopasowywało
  również lewy Ctrl, przez co Lewy Ctrl+V wywoływał nagrywanie. Przepisano na
  `keyboard.hook()` z jawnym porównaniem `event.name == "right ctrl"` —
  rozróżniana jest teraz dokładna strona klawiatury. (`main.py`)

### Zmienione

- **Zaktualizowano presety hotkey w menu traya:**
  - Usunięto: `F12` (otwiera DevTools w Chrome / debugger VS Code),
    `Ctrl+Shift+R` (hard refresh w przeglądarkach).
  - Dodano: `Pause / Break` — klawisz obecny na każdej standardowej klawiaturze,
    nieużywany przez żadną nowoczesną aplikację biurową. **Nowe zalecane.**
  - Przywrócono: `Prawy Alt` (bezpieczny po naprawie suppress).
  - Dodano ostrzeżenie przy `Scroll Lock`: blokuje tryb przewijania w Excelu
    (strzałki przewijają arkusz zamiast przenosić zaznaczenie komórki).
  - Nowa kolejność: Scroll Lock, Pause/Break *(zalecane)*, Prawy Alt,
    Prawy Ctrl, F13, Ctrl+Space, Własny…

---

## [3.2] — 2026-06-03

Niezależny audyt końcowy (jakość, instalator, licencje, stabilność) po wersjach
3.0 i 3.1, plus konkretne usprawnienia zgłoszone przez użytkownika.

### Dodane
- **Przełącznik zwrotów grzecznościowych w menu tray.** Nowa opcja
  `Tray → Pisownia → Zwroty grzecznościowe [wł] / [wył]` pozwala włączać
  i wyłączać automatyczną kapitalizację polskich form grzecznościowych
  **bez restartu aplikacji i bez edycji `config.py`**. Ustawienie jest
  zapisywane w `config_user.json` i zachowywane między sesjami.
  Objęte formy: Pan/Pani/Państwo (wszystkie przypadki), Ty/Cię/Ciebie/Ci/
  Tobie/Tobą, Twój/Twoja/Twoje (wszystkie przypadki), Wy/Was/Wam/Wami,
  Wasz/Wasza/Wasze (wszystkie przypadki). Domyślnie: **włączone**.
- **Spójna ikona aplikacji** `whispervoice.ico` (niebieskie koło z literą „W”),
  generowana z tej samej geometrii co ikona w zasobniku (tray) — zob.
  `make_icon.py`. Używana JEDNOCZEŚNIE przez: plik `Setup.exe` (`SetupIconFile`),
  skróty po instalacji (`IconFilename` na skrótach Menu Start / pulpit / autostart)
  oraz pozycję w „Programy i funkcje” (`UninstallDisplayIcon`). Dzięki temu ikona
  wygląda **identycznie na każdym etapie**: instalacja → zainstalowana aplikacja → tray.
- **Wyraźna rekomendacja CUDA w instalatorze.** Na ekranie komponentów i w opisie
  zadania dodano informację, że komponenty GPU NVIDIA CUDA są **mocno zalecane**
  (transkrypcja nawet kilkanaście razy szybsza niż na CPU). Gdy wykryto kartę
  NVIDIA, zadanie CUDA jest **domyślnie zaznaczone** (pojawia się tylko dla NVIDIA).
- `final_installer_v3.2.iss` (zalecany do kompilacji). `build_installer.bat`
  wskazuje na 3.2. Zachowano `final_installer_v3.0.iss` i `final_installer_v3.1.iss`.
- `make_icon.py` — reprodukowalny generator ikony (narzędzie deweloperskie,
  niedołączane do instalowanej aplikacji).
- `AUDIT_REPORT_v3.2.md` — niezależny audyt końcowy.

### Zmienione
- **Zaktualizowano dokumenty Word** `WhisperVoice_Instrukcja_UPDATED.docx` oraz
  `Slowniczek_Techniczny.docx` do stanu v3.x. Skorygowano nieaktualne treści z
  wersji 2.0: instalacja per-użytkownik w `%LOCALAPPDATA%` (nie Program Files),
  **brak czarnego okna terminala** podczas instalacji, weryfikacja **MD5**
  (zamiast SHA256), Python 3.12.8, nazwy plików instalatora v3.2, mocna
  rekomendacja CUDA, sekcja o spójnej ikonie, opis przełącznika zwrotów
  grzecznościowych.
- Oznaczenie wersji podniesione do **3.2 (build 03.06.2026)** w kodzie,
  skryptach, instalatorze i dokumentacji. Wersja warunków korzystania pozostaje
  `3.0` (treść bez zmian — brak wymuszania ponownej akceptacji).

### Uwagi
- Brak zmian w logice transkrypcji względem 3.1 — testy funkcjonalne i
  stabilnościowe powtórzono (bez regresji).

---

## [3.1] — 2026-06-01

Faza stabilizacji: rzeczywiste testy funkcjonalne i stabilnościowe aplikacji
(nie tylko sprawdzenie obecności plików). Przetestowano m.in. prawdziwą
transkrypcję polskiej mowy na GPU, scenariusze błędne, logowanie i odporność
na zawieszenia. Wykryte błędy zostały poprawione i ponownie przetestowane.

### Naprawione
- **Odporność na uszkodzony `config_user.json`.** Wcześniej, jeśli plik ustawień
  uległ uszkodzeniu (np. przerwany zapis), `_patch_config_file` próbował go
  odczytać, zgłaszał wyjątek i **już nigdy nie zapisywał ustawień** (cicha
  awaria). Teraz uszkodzony plik jest wykrywany i **odtwarzany od nowa**, więc
  zapisywanie ustawień zawsze działa. (`main.py`)
- **Wątek transkrypcji nie blokuje już zamknięcia aplikacji.** Wcześniejsza
  implementacja używała `ThreadPoolExecutor` z `shutdown(wait=False)` z błędnym
  założeniem, że wątek roboczy jest daemonem. W rzeczywistości
  `concurrent.futures` rejestruje atexit-hook dołączający wątki — zawieszona
  transkrypcja mogła blokować zamknięcie procesu. Przepisano na **wątek-daemon
  + `queue.Queue`** z tym samym mechanizmem timeoutu; zawieszona transkrypcja
  nie blokuje wyjścia z aplikacji. (`main.py`)

### Dodane
- `final_installer_v3.1.iss` (zalecany do kompilacji; `final_installer_v3.0.iss`
  zachowany). `build_installer.bat` wskazuje teraz na wersję 3.1.
- Raporty: `STABILITY_TEST_REPORT_v3.1.md`, `AUDIT_REPORT_v3.1.md`,
  `INSTALLER_TEST_REPORT_v3.1.md`.

### Zmienione
- Oznaczenie wersji podniesione do **3.1** w kodzie, skryptach, instalatorze i
  dokumentacji.
- **Uwaga:** wersja warunków korzystania pozostaje `3.0` (treść warunków się nie
  zmieniła) — użytkownicy nie muszą ponownie akceptować warunków po aktualizacji.

### Uwagi z testów (bez zmian w kodzie — z założenia)
- Aplikacja jest narzędziem **dyktowania na żywo** (mikrofon → hotkey → wklejenie),
  a **nie** narzędziem wsadowym do plików. Scenariusze „plik w nieobsługiwanym
  formacie / pusty / uszkodzony / z polskimi znakami w nazwie” **nie dotyczą**
  aplikacji, bo nie przyjmuje ona plików wejściowych. Opisano w raporcie.

---

## [3.0] — 2026-06-01

Wersja porządkująca projekt i instalator. Skupia się na transparentności
instalacji, kompletności zależności oraz dokumentacji i licencjach.

### Dodane
- **`final_installer_v3.0.iss`** — kompletny, gotowy do kompilacji skrypt
  Inno Setup 6. Zastępuje brakujący/utracony `WhisperVoice_Setup.iss`.
  - instalacja **per-użytkownik, bez uprawnień administratora**;
  - **jawny ekran komponentów** przed pobieraniem (nazwa, wersja, źródło,
    cel, licencja, lokalizacja każdego pobieranego elementu);
  - **automatyczne pobieranie Pythona** (gdy brak) z paskiem postępu,
    obsługą anulowania i obsługą braku internetu;
  - **weryfikacja integralności** pobranego Pythona sumą kontrolną MD5
    publikowaną oficjalnie przez python.org;
  - instalacja bibliotek `pip` **bez okna terminala**, z widocznym paskiem
    postępu w kreatorze (rozwiązuje „czarny terminal” z wcześniejszych wersji);
  - instalacja kończy się błędem, jeśli zależności nie zostały poprawnie
    zainstalowane (brak „fałszywego sukcesu”);
  - opcjonalny skrót na pulpicie i opcjonalny autostart (**domyślnie wyłączony**);
  - deinstalator **nie usuwa** logów ani ustawień bez pytania użytkownika.
- Pełny zestaw dokumentacji: `INSTALL.md`, `TROUBLESHOOTING.md`,
  `THIRD_PARTY_LICENSES.md`, `NOTICE.md`, `CHANGELOG.md`,
  `DEPENDENCIES_AND_LICENSES_v3.0.md`.
- Raporty: `AUDIT_REPORT_v3.0.md`, `INSTALLER_TEST_REPORT_v3.0.md`.
- Plik `.gitignore` wykluczający artefakty runtime (logi, cache, `__pycache__`,
  pliki użytkownika) z repozytorium i dystrybucji.

### Zmienione
- Ujednolicono oznaczenie wersji na **3.0 (build 01.06.2026)** we wszystkich
  plikach kodu, skryptów i dokumentacji.
- `THIRD_PARTY_LICENSES` skorygowano do **rzeczywistego** zachowania aplikacji:
  usunięto wpisy o `winget` i `NVIDIA GeForce Experience` jako komponentach
  „używanych podczas instalacji” — kod ich nie wywołuje. Doprecyzowano, że
  aplikacja **nie instaluje ani nie aktualizuje** sterowników NVIDIA; instaluje
  jedynie opcjonalny pakiet `nvidia-cublas-cu12` przy wykrytej karcie NVIDIA.
- Poprawiono pisownię nazwiska autora w pliku `LICENSE` na spójne
  „Mariusz Świergula” (zgodnie z pozostałymi plikami).

### Naprawione
- Usunięto rozbieżność: dokumentacja wspominała o „weryfikacji SHA256 Pythona”,
  której nie było w kodzie. Integralność pobieranego Pythona jest teraz
  faktycznie weryfikowana (MD5 z python.org) w instalatorze `.iss`.

### Usunięte (porządki)
- `__pycache__/` i pliki `.pyc` (regenerowane automatycznie).
- `_syntax_test.py` (plik pomocniczy, oznaczony jako bezpieczny do usunięcia).
- `error.log` z katalogu projektu (artefakt runtime; aplikacja zapisuje logi
  do `%APPDATA%\WhisperVoice\`).
- `terms_acceptance.json` z katalogu projektu (stan runtime; tworzony w
  `%APPDATA%\WhisperVoice\` przy pierwszym uruchomieniu).

---

## [2.0] — build 17.05.2026

- Menu trayu z 7 presetami hotkey + opcja **Własny…** (przechwytywanie klawisza),
  bez restartu aplikacji i bez edycji `config.py`.
- Walidacja kandydata na hotkey (odrzucenie klawiszy zarezerwowanych przez Windows).
- Komunikat o pobieraniu modelu przy pierwszym uruchomieniu, sprawdzanie miejsca
  na dysku, fallback `pip --user`, detekcja Pythona do 3.16,
  `cuda_check.tmp` w `%APPDATA%`, wzmocnione logowanie do `error.log`.
- Tryb cichy `run_silent.vbs`, automatyczne przełączanie GPU/CPU.

## [1.0]

- Pierwsza publiczna wersja. Instalacja i konfiguracja ręczna (terminal),
  hotkey wyłącznie Scroll Lock, konfiguracja przez `config.py`.
