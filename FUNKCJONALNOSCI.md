# FUNKCJONALNOSCI — WhisperVoice (rejestr rozwiązań)

> **Po co ten plik:** AKTUALNY stan aplikacji + POWODY decyzji (nie changelog).
> Kolejna sesja/AI ma tu zobaczyć punkt wyjścia i nie odkrywać/psuć istniejących
> rozwiązań. **PRZED zmianą** czytaj „Mechanizmy nietypowe" i „Ślepe uliczki";
> **PO zmianie** aktualizuj rejestr w tym samym przebiegu co kod.
>
> Wersja: **v3.4** (build 2026-07-15) · Źródło prawdy: `C:\PROJEKTY\aplikacje\WhisperVoice`
> (repo lokalne, bez remote). „Gdzie" = plik/funkcja/id, **nie numery linii** (gniją).
> Kolumna „Zweryfikowano" = data ostatniego świadomego testu.

---

## Architektura w pigułce

| Moduł | Plik / rola | Charakter | Po co osobno |
|---|---|---|---|
| Rdzeń | `main.py` — hotkey, nagrywanie, transkrypcja, wklejanie, tray, overlay | ~2,4 tys. linii, jeden proces | Cała logika czasu rzeczywistego w jednym miejscu |
| Ustawienia | `config.py` — profile transkrypcji, VAD, progi, hotkey | Stałe + profile | Zaawansowana konfiguracja; tray nadpisuje przez `config_user.json` |
| Filtr halucynacji | `hallucinations.py` — wzorce + `filter_hallucinations`, `looks_like_hallucination` | **Czysty moduł (tylko `re`)** | Testowalny offline bez modelu/audio (dev-tools) |
| Testy dev | `dev-tools/test_hallucinations.py` | Offline, exit 0/1 | Regresja filtra; NIE pakowany do dystrybucji |
| Instalator | `final_installer_v3.4.iss` (+ `build_installer.bat`) | Inno Setup, per-user | Pobiera Python/pakiety/CUDA jawnie |

Dane runtime (config_user.json, error.log, terms_acceptance.json) **wyłącznie** w
`%APPDATA%\WhisperVoice\` — nigdy w katalogu instalacji (może być read-only).

---

## Obszar: Filtr halucynacji Whispera

| Funkcja | Gdzie (plik/funkcja) | Uwagi i decyzje | Zweryfikowano |
|---|---|---|---|
| Warstwa 1 — czyszczenie tekstu | `hallucinations.filter_hallucinations` | Zeruje całość gdy nagrano samą halucynację; ucina „mocną" halucynację doklejoną na końcu; frazy „słabe" tylko przy całości | 2026-07-15 — `dev-tools/test_hallucinations.py`, 22/22 OK |
| Wykrywanie wzorca (Warstwa 2) | `hallucinations.looks_like_hallucination` | Poziomy STRONG/WEAK; `strong_only` do bezpiecznego cięcia ogona | 2026-07-15 — test offline |
| Warstwa 2 — odrzucanie segmentów | `main._transcribe_and_inject` | Odrzuca segment gdy `no_speech_prob ≥ NO_SPEECH_DROP_THRESHOLD` **i** treść pasuje do wzorca | 2026-07-15 — przegląd kodu + test wzorca (bez nagrania na mikrofonie — patrz „do testu ręcznego") |
| Import defensywny | `main.py` (try/except na `from hallucinations`) | Brak modułu → filtr no-op, aplikacja i tak startuje | 2026-07-15 — `py_compile` OK |
| Próg Warstwy 2 | `config.NO_SPEECH_DROP_THRESHOLD` = 0.6 | 1.0 praktycznie wyłącza Warstwę 2 | 2026-07-15 |

**Do testu ręcznego użytkownika:** realne nagranie ciszy/oddechu na mikrofonie i
potwierdzenie, że nic się nie wkleja (test na żywym modelu large-v3 — poza zasięgiem
testu offline).

## Obszar: pozostałe (DO AUDYTU — nieostemplowane)

| Obszar | Gdzie | Status |
|---|---|---|
| Hotkey hold-to-talk | `main._setup_hotkey`, `config.HOTKEY` | Do przejścia w audycie (fizyczne naciśnięcia = test ręczny) |
| Nagrywanie / audio | `main.start_recording`/`stop_recording`, `_audio_callback` | Do audytu |
| Transkrypcja / profile | `main.get_transcribe_kwargs`, `config.TRANSCRIBE_PROFILE_*` | Do audytu |
| Wklejanie tekstu | `main._inject_text` (clipboard/CTRL+V) | Do audytu |
| Overlay wizualny | `main.RecordingOverlay` | Do audytu |
| Tray / menu | `main._build_menu` + `_change_*` | Do audytu |
| Persystencja ustawień | `main._patch_config_file`/`_load_user_config` | Do audytu |

---

## Mechanizmy nietypowe

- **M1 — Dwuwarstwowy filtr halucynacji.** *Problem:* Whisper large-v3 na ciszy/szumie
  „dopowiada" frazy z YouTube (napisy, subskrypcja, „w opisie filmu") z WYSOKĄ pewnością,
  więc wbudowany `no_speech_threshold` (wymaga też niskiego `avg_logprob`) ich nie odrzuca.
  *Rozwiązanie:* W1 = wzorce regex na tekście (`hallucinations.py`) + W2 = odrzucanie
  segmentów po `no_speech_prob` **z** dopasowaniem wzorca. *Dlaczego nie inaczej:* sama
  lista dokładnych fraz gniła (warianty); samo `no_speech_prob` bez wzorca ucinałoby cichą
  prawdziwą mowę → oba warunki naraz.
- **M2 — Import filtra jest defensywny.** Brak `hallucinations.py` (np. częściowa
  instalacja) nie wywala startu — filtr staje się no-opem. Dlatego moduł MUSI być w
  `[Files]` instalatora, inaczej cicho tracimy ochronę.
- **M3 — Transkrypcja w wątku-daemonie + queue, świadomie NIE `ThreadPoolExecutor`.**
  Zawieszenie transkrypcji nie może blokować zamknięcia aplikacji (`main._transcribe_and_inject`).
- **M4 — Profile transkrypcji dobierane po długości nagrania** (SHORT/SHORT_PLUS/DEFAULT/LONG)
  z osobnymi zestawami VAD — `main.get_transcribe_kwargs`.
- **M5 — Kwargs filtrowane po sygnaturze `model.transcribe`** — parametry nieobsługiwane
  przez zainstalowaną wersję faster-whisper są usuwane, żeby nie wywołać błędu.

---

## Ślepe uliczki (NIGDY nie usuwać — tylko dopisywać)

- **Pause/Break jako hotkey** — nienaprawialne: klawisz wysyła press+release razem przy
  wciśnięciu (scancode `E1 1D 45`), więc hold-to-talk dostaje nagranie ~0 s. Usunięty w
  v3.4 + migracja starych configów na Scroll Lock. Nie przywracać.
- **`pyautogui` do wklejania** — wciągał `mouseinfo` na GPLv3 (niezgodne z dystrybucją MIT).
  Zastąpiony `keyboard` (MIT). Nie wracać do pyautogui.
- **Poziom okna `floating`/`screen-saver` (Electron/tk „topmost")** — na Windows nie
  gwarantuje bycia nad oknami systemowymi (to działa na macOS). Nie zakładać, że overlay
  „zawsze na wierzchu" bez pomiaru z-order.
- **Filtrowanie halucynacji samym `no_speech_threshold`** — odrzucone: nie łapie fraz
  generowanych z wysokim `avg_logprob` (patrz M1).

---

## Build / wydanie (skrót)

Bump wersji w `main.py` (`_APP_VERSION`, docstring, „O aplikacji"), `config.py` (nagłówek),
`.iss` (`AppVersion`/`AppBuild`) i `build_installer.bat` — trzymać SPÓJNIE. Każdy nowy
ładowany plik dopisać do `[Files]` w `.iss` (ostatnio: `hallucinations.py`). Build:
`build_installer.bat` → `Output\WhisperVoice_Setup_v3.4.exe`. **Build/wydanie tylko po
wyraźnym „OK" użytkownika.** Repo lokalne — brak drogi CI/GitHub dla tej aplikacji.
