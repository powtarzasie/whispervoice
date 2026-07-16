"""
WhisperVoice v3.4 — lokalny voice-to-text dla Windows 11
build 15.07.2026
Przytrzymaj Scroll Lock → mów → puść → tekst pojawia się w aktywnym polu.

Wymaga: pip install faster-whisper sounddevice keyboard pystray pillow pyperclip
"""

import threading
import time
import os
import sys
import json
import datetime
import ctypes
import queue
import math
import inspect
import re

# ── Wymuś UTF-8 dla stdout/stderr ────────────────────────────────────────────
# Windows domyślnie używa cp1250/cp1252 — print() z polskimi znakami może padać
# UnicodeEncodeError. Reconfigure działa od Python 3.7+.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# ── Wczesne logowanie błędów importu ─────────────────────────────────────────
# Jeśli pakiet nie jest zainstalowany, błąd trafia do error.log zamiast
# zniknąć razem z oknem konsoli.
_APP_DIR_EARLY  = os.path.dirname(os.path.abspath(__file__))
# Katalog danych użytkownika — zawsze zapisywalny (nie wymaga uprawnień admina)
# Ważne: gdy app jest w Program Files, _APP_DIR_EARLY jest tylko do odczytu!
_DATA_DIR_EARLY = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "WhisperVoice")
try:
    os.makedirs(_DATA_DIR_EARLY, exist_ok=True)
except Exception:
    _DATA_DIR_EARLY = _APP_DIR_EARLY   # fallback: katalog instalacji
_LOG_EARLY      = os.path.join(_DATA_DIR_EARLY, "error.log")

_APP_VERSION = "3.4"
_BUILD_DATE  = "15.07.2026"


def _log(msg: str, level: str = "INFO") -> None:
    """
    Zapisuje wpis do error.log z timestamp.
    Bezpieczna nawet przy braku uprawnień do pliku — nigdy nie rzuca wyjątku.
    Używana przez cały main.py do śledzenia każdego etapu pracy aplikacji.
    """
    ts   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    line = f"[{ts}] [{level}] {msg}\n"
    print(line, end="")
    try:
        with open(_LOG_EARLY, "a", encoding="utf-8") as _f:
            _f.write(line)
    except Exception:
        pass


# ── Wpis startowy — widoczny od pierwszej linii logu ─────────────────────────
try:
    import platform as _plt
    _log(f"=== WhisperVoice v{_APP_VERSION} (build {_BUILD_DATE}) START ===")
    _log(f"Python {sys.version.split()[0]} | OS: {_plt.platform()} | PID: {os.getpid()}")
    _log(f"Log: {_LOG_EARLY}")
except Exception:
    pass


def _import_or_die(module_name: str, pip_name: str = ""):
    import importlib
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        msg = (
            f"[WhisperVoice] BRAK PAKIETU: {module_name}\n"
            f"  Błąd: {e}\n"
            f"  Rozwiązanie: pip install {pip_name or module_name}\n"
            f"  lub uruchom install.bat\n"
        )
        print(msg, file=sys.stderr)
        try:
            with open(_LOG_EARLY, "a", encoding="utf-8") as _f:
                _f.write(f"\n[{datetime.datetime.now()}]\n" + msg)
        except Exception:
            pass
        input("Nacisnij Enter aby zamknac...")
        sys.exit(1)
# ─────────────────────────────────────────────────────────────────────────────

try:
    import numpy as np
except ImportError as _e:
    _msg = (
        f"[WhisperVoice] BRAK PAKIETU: numpy\n"
        f"  Błąd: {_e}\n"
        f"  Rozwiązanie: uruchom install.bat z folderu aplikacji.\n"
    )
    print(_msg, file=sys.stderr)
    try:
        with open(_LOG_EARLY, "a", encoding="utf-8") as _f:
            _f.write(f"\n[{datetime.datetime.now()}]\n" + _msg)
    except Exception:
        pass
    try:
        ctypes.windll.user32.MessageBoxW(0, _msg, "WhisperVoice — brak pakietu", 0x10)
    except Exception:
        pass
    input("Naciśnij Enter aby zamknąć...")
    sys.exit(1)


def _add_nvidia_dll_paths():
    """Dodaje ścieżki DLL z pakietów nvidia (pip) do PATH i wyszukiwania Windows."""
    import sys
    added = []
    for base in sys.path:
        nvidia_dir = os.path.join(base, 'nvidia')
        if os.path.isdir(nvidia_dir):
            for pkg in os.listdir(nvidia_dir):
                bin_path = os.path.join(nvidia_dir, pkg, 'bin')
                if os.path.isdir(bin_path) and bin_path not in added:
                    added.append(bin_path)
                    # Dodaj do PATH (główna metoda dla CTranslate2)
                    os.environ['PATH'] = bin_path + os.pathsep + os.environ.get('PATH', '')
                    # Dodaj też przez add_dll_directory (Python 3.8+)
                    try:
                        os.add_dll_directory(bin_path)
                    except Exception:
                        pass

_add_nvidia_dll_paths()

try:
    import sounddevice as sd
    import keyboard
    import pyperclip
    import pystray
    from PIL import Image, ImageDraw
    from faster_whisper import WhisperModel
    import config
except ImportError as _e:
    _missing_msg = (
        f"[WhisperVoice] BRAK WYMAGANEGO PAKIETU\n\n"
        f"Błąd: {_e}\n\n"
        f"Rozwiązanie:\n"
        f"  Uruchom install.bat z folderu aplikacji.\n"
        f"  (instaluje wszystkie wymagane pakiety Python)\n\n"
        f"Szczegóły w pliku: {_LOG_EARLY}"
    )
    print(_missing_msg, file=sys.stderr)
    try:
        with open(_LOG_EARLY, "a", encoding="utf-8") as _f:
            _f.write(f"\n[{datetime.datetime.now()}]\n" + _missing_msg)
    except Exception:
        pass
    try:
        ctypes.windll.user32.MessageBoxW(
            0, _missing_msg, "WhisperVoice — brak pakietu", 0x10
        )
    except Exception:
        pass
    input("Naciśnij Enter aby zamknąć...")
    sys.exit(1)


# ── Filtr halucynacji (Warstwa 1) — czysty moduł, import defensywny ──────────
# Jeśli plik hallucinations.py nie doszedł (np. częściowa/stara instalacja),
# aplikacja nadal wystartuje — filtr staje się wtedy no-opem zamiast wywalać start.
try:
    from hallucinations import filter_hallucinations, looks_like_hallucination
except ImportError as _hall_err:
    print(f"[WhisperVoice] Uwaga: brak modułu hallucinations.py ({_hall_err}) — "
          f"filtr halucynacji wyłączony.")

    def filter_hallucinations(text):                         # type: ignore[misc]
        return text

    def looks_like_hallucination(text, strong_only=False):   # type: ignore[misc]
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Warunki korzystania — akceptacja przy pierwszym uruchomieniu
# ─────────────────────────────────────────────────────────────────────────────

_APP_DIR  = os.path.dirname(os.path.abspath(__file__))   # katalog instalacji (może być read-only)
_DATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "WhisperVoice")
os.makedirs(_DATA_DIR, exist_ok=True)

# Pliki zapisywalne — wszystkie idą do %APPDATA%\WhisperVoice\
_TERMS_FILE       = os.path.join(_DATA_DIR, "terms_acceptance.json")
_CONFIG_USER_FILE = os.path.join(_DATA_DIR, "config_user.json")   # ustawienia zmienione z tray

_TERMS_VERSION = "3.0"

def get_transcribe_kwargs(duration_seconds: float) -> tuple[dict, str]:
    """
    Zwraca (kwargs, nazwa_profilu) na podstawie długości nagrania.

    Progi:
      ≤ 30 s   → SHORT      (krótki prompt, VAD z niższym progiem ciszy)
      ≤ 90 s   → SHORT_PLUS (przejście, pełny prompt, łagodny VAD)
      ≤ 600 s  → DEFAULT    (główny profil dyktowania)
      > 600 s  → LONG       (łagodniejszy VAD, beam_size=8)

    Język i zadanie zawsze brane z config, żeby uwzględniać zmiany z trayu.
    """
    if duration_seconds <= 30:
        kwargs = dict(config.TRANSCRIBE_PROFILE_SHORT)
        profile_name = "SHORT"
    elif duration_seconds <= 90:
        kwargs = dict(config.TRANSCRIBE_PROFILE_SHORT_PLUS)
        profile_name = "SHORT_PLUS"
    elif duration_seconds <= 600:
        kwargs = dict(config.TRANSCRIBE_PROFILE_DEFAULT)
        profile_name = "DEFAULT"
    else:
        kwargs = dict(config.TRANSCRIBE_PROFILE_LONG)
        profile_name = "LONG"

    # Respektuj zmiany języka/zadania/precyzji z menu trayu
    kwargs["language"] = config.LANGUAGE
    kwargs["task"] = config.TASK
    kwargs["beam_size"] = config.BEAM_SIZE   # nadpisuje hardcoded wartość profilu

    return kwargs, profile_name


def postprocess_transcript(text: str) -> str:
    """
    Prosty post-processing transkrypcji: normalizacja spacji i interpunkcji.
    Nie przepisuje treści — tylko czyści format.
    """
    text = text.strip()
    text = " ".join(text.split())

    replacements = {
        " ,": ",",
        " .": ".",
        " !": "!",
        " ?": "?",
        " :": ":",
        " ;": ";",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = _capitalize_polite_forms(text)

    return text


# ── Kapitalizacja zwrotów grzecznościowych ────────────────────────────────────
_POLITE_FORMS = re.compile(
    r'\b('
    # Pan/Pani/Państwo i odmiana
    r'pan|pana|panu|panem|panie|pani'
    r'|państwo|państwa|państwu|państwem'
    # Ty i odmiana — zaimek osobowy (2. os. l. poj.)
    r'|ty|cię|ciebie|ci|tobie|tobą'
    # Twój i odmiana — zaimek dzierżawczy (2. os. l. poj.)
    r'|twój|twoja|twoje|twojego|twojej|twojemu|twoją|twoim|twoi|twoich|twoimi'
    # Wy i odmiana — zaimek osobowy (2. os. l. mn.)
    r'|wy|was|wam|wami'
    # Wasz i odmiana — zaimek dzierżawczy (2. os. l. mn.)
    r'|wasz|wasza|wasze|waszego|waszej|waszemu|waszą|waszym|wasi|waszych|waszymi'
    r')\b',
    flags=re.IGNORECASE,
)


def _capitalize_polite_forms(text: str) -> str:
    """Zamienia zwroty grzecznościowe na wersję z wielką literą (jeśli włączone)."""
    if not getattr(config, "POLITE_FORMS_ENABLED", True):
        return text
    def _cap(m: re.Match) -> str:
        w = m.group(1)
        return w[0].upper() + w[1:]
    return _POLITE_FORMS.sub(_cap, text)


# ── Filtr halucynacji ─────────────────────────────────────────────────────────
# Logika wykrywania i usuwania halucynacji Whispera została wydzielona do czystego
# modułu `hallucinations.py` (Warstwa 1) — importowanego na górze pliku. Dzięki
# temu można ją testować w izolacji (dev-tools/test_hallucinations.py) bez
# ładowania modelu, audio ani sterowników. Warstwa 2 (odrzucanie całych segmentów
# o wysokim no_speech_prob) znajduje się niżej, w _transcribe_and_inject.


def _check_terms_accepted() -> bool:
    """
    Sprawdza czy użytkownik zaakceptował warunki korzystania.
    Jeśli nie — pokazuje okno dialogowe (tkinter).
    Zwraca True jeśli zaakceptowano, False jeśli anulowano.
    """
    # Sprawdź zapis z poprzedniej akceptacji
    if os.path.exists(_TERMS_FILE):
        try:
            with open(_TERMS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("termsAccepted") and data.get("termsVersion") == _TERMS_VERSION:
                return True  # już zaakceptowane — nie pokazuj ponownie
        except Exception:
            pass

    # Pokaż okno dialogowe z warunkami
    import tkinter as tk

    accepted = [False]

    root = tk.Tk()
    root.title("WhisperVoice — Warunki korzystania")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    # Wyśrodkuj okno — wystarczająca wysokość żeby zmieścić tekst + przyciski
    w, h = 530, 460
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")
    root.configure(bg="#f0f0f0")

    def on_accept():
        accepted[0] = True
        root.destroy()

    def on_cancel():
        accepted[0] = False
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_cancel)

    # ── Przyciski zakotwiczone NA DOLE (pack przed treścią = zawsze widoczne)
    tk.Frame(root, height=1, bg="#cccccc").pack(side="bottom", fill="x")
    btn_frame = tk.Frame(root, pady=12, bg="#f0f0f0")
    btn_frame.pack(side="bottom", fill="x")

    tk.Button(
        btn_frame, text="Anuluj", width=12,
        font=("Segoe UI", 10), command=on_cancel,
        relief="groove"
    ).pack(side="right", padx=(8, 20))

    tk.Button(
        btn_frame, text="Akceptuję  ✓", width=14,
        font=("Segoe UI", 10, "bold"),
        bg="#0078d4", fg="white", activebackground="#005a9e",
        activeforeground="white", relief="flat", command=on_accept
    ).pack(side="right", padx=4)

    # ── Nagłówek ──────────────────────────────────────────────────────
    tk.Label(
        root, text="Warunki korzystania",
        font=("Segoe UI", 13, "bold"), pady=10, bg="#f0f0f0"
    ).pack(side="top", fill="x")
    tk.Frame(root, height=1, bg="#cccccc").pack(side="top", fill="x")

    # ── Treść — wypełnia przestrzeń między nagłówkiem a przyciskami ───
    terms_text = (
        "Ta aplikacja jest darmowa, działa lokalnie\n"
        "i nie zbiera danych osobowych.\n"
        "\n"
        "Aplikacja jest udostępniana w stanie „takim, jaki jest”,\n"
        "bez gwarancji poprawnego działania, przydatności\n"
        "do konkretnego celu lub braku błędów.\n"
        "\n"
        "Korzystasz z aplikacji na własną odpowiedzialność.\n"
        "\n"
        "Aplikacja wykorzystuje komponenty open-source oraz\n"
        "opcjonalne komponenty NVIDIA wymagane do obsługi GPU.\n"
        "Komponenty zewnętrzne podlegają własnym licencjom.\n"
        "\n"
        "Niektóre komponenty zewnętrzne, w szczególności\n"
        "oprogramowanie NVIDIA, mogą działać zgodnie z własnymi\n"
        "zasadami licencyjnymi i politykami prywatności dostawcy.\n"
        "\n"
        "Klikając Akceptuję, potwierdzasz, że rozumiesz\n"
        "powyższe warunki."
    )
    tk.Label(
        root, text=terms_text,
        font=("Segoe UI", 10), justify="left",
        anchor="nw", padx=24, pady=12, bg="#ffffff"
    ).pack(side="top", fill="both", expand=True)

    root.mainloop()

    if accepted[0]:
        # Zapisz akceptację lokalnie
        try:
            with open(_TERMS_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "termsAccepted": True,
                    "termsVersion": _TERMS_VERSION,
                    "termsAcceptedAt": datetime.date.today().isoformat(),
                }, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        return True
    else:
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Zapis ustawień do config.py
# ─────────────────────────────────────────────────────────────────────────────

def _patch_config_file(key: str, value) -> None:
    """
    Zapisuje zmienione ustawienie do %APPDATA%\\WhisperVoice\\config_user.json.
    Zastąpiło wcześniejszy zapis bezpośrednio do config.py, który wymagał
    uprawnień zapisu do katalogu instalacji (Program Files).
    """
    # Wczytaj istniejące ustawienia — ale NIE pozwól, by uszkodzony plik
    # (np. po przerwanym zapisie) zablokował zapis nowych ustawień na zawsze.
    # W takim wypadku odtwarzamy plik od zera zamiast cicho odmawiać zapisu.
    data: dict = {}
    if os.path.exists(_CONFIG_USER_FILE):
        try:
            with open(_CONFIG_USER_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = {}
        except Exception as exc:
            print(f"[WhisperVoice] Uszkodzony config_user.json ({exc}) — "
                  f"odtwarzam plik od nowa.")
            data = {}
    try:
        data[key] = value
        with open(_CONFIG_USER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        print(f"[WhisperVoice] Błąd zapisu ustawień ({key}): {exc}")


def _load_user_config() -> None:
    """
    Wczytuje ustawienia zmienione przez użytkownika z config_user.json
    i nadpisuje nimi wartości z config.py (które są domyślnymi).
    Wywoływana raz przy starcie aplikacji, przed ładowaniem modelu.

    Walidacja sanity: jeśli auto-detekcja wymusiła CPU, blokujemy
    zapis large-* z user_config — ładowanie large-v3 na CPU jest
    skrajnie wolne i typowo padnie z OOM przy małych RAM-ach.
    """
    if not os.path.exists(_CONFIG_USER_FILE):
        return
    try:
        with open(_CONFIG_USER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Czy CUDA jest realnie dostępne (do walidacji DEVICE z user_config)?
        try:
            import ctranslate2
            _cuda_available = ctranslate2.get_cuda_device_count() > 0
        except Exception:
            _cuda_available = False

        applied = []
        for key, value in data.items():
            # Sanity guard 1: nie pozwól nadpisać DEVICE='cuda' gdy brak GPU
            if key == "DEVICE" and value == "cuda" and not _cuda_available:
                print(f"[WhisperVoice] Pominięto user_config['DEVICE']='cuda' "
                      f"— brak GPU, wymuszam '{config.DEVICE}'.")
                continue
            # Sanity guard 2: nie pozwól nadpisać medium → large-* gdy DEVICE=cpu
            if (key == "MODEL_SIZE"
                    and isinstance(value, str) and value.startswith("large")
                    and getattr(config, "DEVICE", "cpu") == "cpu"):
                print(f"[WhisperVoice] Pominięto user_config['MODEL_SIZE']={value!r} "
                      f"— tryb CPU, wymuszam '{config.MODEL_SIZE}'.")
                continue
            if hasattr(config, key):
                setattr(config, key, value)
                applied.append(key)
        if applied:
            print(f"[WhisperVoice] Wczytano ustawienia użytkownika: {', '.join(applied)}")
    except Exception as exc:
        print(f"[WhisperVoice] Błąd wczytywania ustawień użytkownika: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# Auto-detekcja GPU / CPU
# ─────────────────────────────────────────────────────────────────────────────

def _auto_detect_device() -> None:
    """
    Sprawdza dostepnosc CUDA. Jesli brak karty NVIDIA — automatycznie
    przelacza config na tryb CPU (nadpisuje w pamieci, nie rusza pliku).
    """
    try:
        import ctranslate2
        cuda_count = ctranslate2.get_cuda_device_count()
    except Exception:
        cuda_count = 0

    if cuda_count > 0 and config.DEVICE == "cuda":
        print(f"[WhisperVoice] Wykryto {cuda_count} GPU NVIDIA — tryb CUDA aktywny.")
        print(f"[WhisperVoice] Model: {config.MODEL_SIZE} | compute: {config.COMPUTE_TYPE}")
    else:
        if config.DEVICE == "cuda":
            print("[WhisperVoice] Brak karty NVIDIA lub sterowniki CUDA niedostepne.")
            print("[WhisperVoice] Przelaczam automatycznie na tryb CPU.")
            print("[WhisperVoice] UWAGA: transkrypcja bedzie wolniejsza niz na GPU.")
            config.DEVICE = "cpu"
            config.COMPUTE_TYPE = "int8"
            config.MODEL_SIZE = "medium"
        print(f"[WhisperVoice] Tryb CPU | model: {config.MODEL_SIZE} | compute: {config.COMPUTE_TYPE}")

_auto_detect_device()


# ─────────────────────────────────────────────────────────────────────────────
# Weryfikacja uprawnień do globalnych hotkeys
# ─────────────────────────────────────────────────────────────────────────────

def _check_keyboard_permissions() -> bool:
    """
    Sprawdza czy aplikacja może rejestrować globalny hotkey systemowy.
    Na kontach bez admina lub przy restrykcyjnych politykach GPO (środowiska
    korporacyjne) biblioteka keyboard może nie działać — bez tej weryfikacji
    aplikacja startuje normalnie, ale Scroll Lock nie reaguje.
    Zwraca True jeśli hotkey jest możliwy do zarejestrowania.
    """
    try:
        # Używamy suppress=True (tak samo jak _setup_hotkey poniżej) — żeby test
        # odzwierciedlał faktyczny tryb rejestracji. Wcześniej był suppress=False
        # i test mógł przejść mimo że pełna rejestracja by padła.
        _tid = keyboard.add_hotkey("f24", lambda: None, suppress=True)
        try:
            keyboard.remove_hotkey(_tid)
        except Exception:
            # remove_hotkey może rzucić jeśli handle nie jest rozpoznawane przez
            # daną wersję biblioteki — nie pozwól żeby cleanup zepsuł sam test
            pass
        return True
    except Exception as exc:
        msg = (
            "WhisperVoice nie ma uprawnień do globalnych skrótów klawiszowych.\n\n"
            f"Hotkey ({config.HOTKEY.upper()}) nie zostanie zarejestrowany.\n\n"
            "Możliwe przyczyny:\n"
            "  • Konto bez uprawnień administratora\n"
            "  • Polityki GPO blokujące keyboard hooks\n"
            "  • Antywirus/EDR blokujący Raw Input\n\n"
            "Spróbuj uruchomić aplikację jako Administrator.\n\n"
            f"Szczegóły błędu: {exc}"
        )
        print(f"[WhisperVoice] ⚠ Brak uprawnień do hotkey: {exc}")
        ctypes.windll.user32.MessageBoxW(0, msg, "WhisperVoice — błąd uprawnień", 0x30)
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Dźwięki potwierdzenia (winsound — wbudowane w Windows, zero zależności)
# ─────────────────────────────────────────────────────────────────────────────
#
# UWAGA: winsound.Beep() używa starego API PC-speakera i na nowoczesnym
# sprzęcie (laptopy, USB audio) bywa niesłyszalny lub zupełnie cichy.
# Zamiast tego używamy winsound.PlaySound() z systemowymi aliasami Windows
# (te same dźwięki co w powiadomieniach, Eksploratorze itp.) — zawsze słyszalne.
#
# Dostępne aliasy systemowe Windows:
#   "SystemAsterisk"    → informacja / gotowość
#   "SystemExclamation" → ostrzeżenie
#   "SystemHand"        → błąd / krytyczny
#   "SystemNotification"→ powiadomienie (Windows 10+)
#   "SystemDefault"     → dźwięk domyślny

def _play_beep(alias: str = "SystemAsterisk") -> None:
    """
    Odtwarza systemowy dźwięk Windows asynchronicznie przez winsound.PlaySound.
    Używa aliasów dźwięków Windows (nie Beep — ten jest często niesłyszalny).
    Działa tylko gdy config.SOUND_FEEDBACK = True.
    """
    if not getattr(config, "SOUND_FEEDBACK", True):
        return

    def _worker():
        try:
            import winsound
            winsound.PlaySound(alias, winsound.SND_ALIAS)
        except Exception:
            # Ostatni fallback: stary Beep na wypadek braku dźwięków systemowych
            try:
                import winsound as _ws
                _ws.Beep(880, 200)
            except Exception:
                pass

    threading.Thread(target=_worker, daemon=True, name="beep").start()


def _show_toast(message: str, duration_ms: int = 2800) -> None:
    """
    Mały popup-toast w prawym dolnym rogu ekranu na duration_ms milisekund.
    Używany gdy model się ładuje a użytkownik wciśnie hotkey — wyraźny,
    widoczny feedback bez blokowania czegokolwiek.
    """
    def _run():
        import tkinter as tk
        try:
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            root.configure(bg="#1e293b")

            w, h = 300, 54
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            root.geometry(f"{w}x{h}+{sw - w - 16}+{sh - h - 60}")

            try:
                root.attributes("-alpha", 0.93)
            except Exception:
                pass

            tk.Label(
                root, text=message,
                font=("Segoe UI", 10), fg="#f8fafc", bg="#1e293b",
                padx=14, pady=16, anchor="w",
            ).pack(fill="both", expand=True)

            root.after(duration_ms, root.destroy)
            root.mainloop()
        except Exception:
            pass

    threading.Thread(target=_run, daemon=True, name="toast").start()


# ─────────────────────────────────────────────────────────────────────────────
# Ikona trayu
# ─────────────────────────────────────────────────────────────────────────────

def _draw_icon(color_rgb: tuple, show_dot: bool = False) -> Image.Image:
    """
    Rysuje ikonę trayu 64×64 RGBA.
    Styl wybierany z config.ICON_STYLE:
      "letter" → litera W (domyślne — nie myli się z systemową ikoną mikrofonu)
      "mic"    → mikrofon (styl klasyczny)
      "wave"   → paski equalizera (fale dźwiękowe)
    show_dot=True → biały punkt zamiast symbolu (tryb nagrywania, wspólny dla wszystkich stylów)
    """
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Tło — koło
    r, g, b = color_rgb
    d.ellipse([0, 0, size - 1, size - 1], fill=(r, g, b, 255))

    w = (255, 255, 255, 230)  # biały półprzezroczysty

    if show_dot:
        # Pulsujący punkt — tryb nagrywania (wspólny dla wszystkich stylów)
        d.ellipse([20, 20, 44, 44], fill=w)
        return img

    style = getattr(config, "ICON_STYLE", "letter")

    if style == "letter":
        # ── Litera W rysowana ręcznie przez linie (nie wymaga zewnętrznego fontu) ──
        # Proporcje: góra na y=12, dolne rogi na y=48, środkowe wcięcie na y=30
        # Lewa noga zewnętrzna
        d.line([13, 12, 22, 48], fill=w, width=5)
        # Lewa noga wewnętrzna
        d.line([22, 48, 32, 28], fill=w, width=5)
        # Prawa noga wewnętrzna
        d.line([32, 28, 42, 48], fill=w, width=5)
        # Prawa noga zewnętrzna
        d.line([42, 48, 51, 12], fill=w, width=5)

    elif style == "wave":
        # ── Trzy paski equalizera — różne wysokości ──
        # Lewy słupek
        d.rectangle([16, 22, 23, 50], fill=w)
        # Środkowy (najwyższy)
        d.rectangle([28, 13, 35, 50], fill=w)
        # Prawy
        d.rectangle([40, 28, 47, 50], fill=w)

    else:
        # ── "mic" — mikrofon: kapsuła + podstawka ──
        d.rounded_rectangle([24, 8, 40, 34], radius=8, fill=w)
        # Łuk podstawki (dolna półelipsa)
        d.arc([17, 28, 47, 50], start=0, end=180, fill=w, width=3)
        # Pionowy trzon
        d.line([32, 50, 32, 57], fill=w, width=3)
        # Podstawa pozioma
        d.line([25, 57, 39, 57], fill=w, width=3)

    return img



# ─────────────────────────────────────────────────────────────────────────────
# Nakładka wizualna (floating overlay)
# ─────────────────────────────────────────────────────────────────────────────


# Tabela RTF (ile razy szybciej od czasu rzeczywistego dziala dany model/device/compute).
# Klucz: (model_size, device, compute_type)
# Wartosc: RTF — im wyzszy, tym szybciej przetwarza wzgledem dlugosci audio.
#
# Uwaga: Whisper zawsze przetwarza pelne okno ~30 s, nawet dla krotkich nagran.
# Dlatego _MIN_EFFECTIVE_DURATION_S zapobiega zanizonemu szacowaniu dla krotkich klipow.
_RTF_TABLE = {
    # ── CUDA ──────────────────────────────────────────────────────────
    ("large-v3", "cuda", "float16"):        8.0,
    ("large-v3", "cuda", "int8_float16"):   5.0,   # np. GTX 1660 Ti, beam_size=10
    ("large-v3", "cuda", "int8"):           4.5,
    ("large-v2", "cuda", "float16"):        8.0,
    ("large-v2", "cuda", "int8_float16"):   5.0,
    ("large-v2", "cuda", "int8"):           4.5,
    ("medium",   "cuda", "float16"):       15.0,
    ("medium",   "cuda", "int8_float16"):  10.0,
    ("medium",   "cuda", "int8"):           8.0,
    ("small",    "cuda", "float16"):       22.0,
    ("small",    "cuda", "int8_float16"):  16.0,
    ("small",    "cuda", "int8"):          13.0,
    ("base",     "cuda", "float16"):       32.0,
    ("base",     "cuda", "int8_float16"):  25.0,
    ("base",     "cuda", "int8"):          20.0,
    ("tiny",     "cuda", "float16"):       45.0,
    ("tiny",     "cuda", "int8_float16"):  35.0,
    ("tiny",     "cuda", "int8"):          28.0,
    # ── CPU (compute_type = int8) ──────────────────────────────────────
    ("large-v3", "cpu",  "int8"):           0.4,
    ("large-v2", "cpu",  "int8"):           0.4,
    ("medium",   "cpu",  "int8"):           1.5,
    ("small",    "cpu",  "int8"):           3.0,
    ("base",     "cpu",  "int8"):           5.5,
    ("tiny",     "cpu",  "int8"):           9.0,
}
_OVERHEAD_S = 1.0              # staly narzut startowy (s)
_MIN_EFFECTIVE_DURATION_S = 28.0  # Whisper przetwarza min. okno ~30 s — nawet dla 3-sekundowego klipu


class RecordingOverlay:
    """
    Slim Pill overlay — 282×52 px.
    Nagrywanie : czerwona ikona mikrofonu + animowana fala.
    Przetwarzanie : fioletowy spinner + pasek postępu + timer.
    Kształt kapsułki uzyskiwany przez transparentcolor (Win10 i Win11).
    """

    _W, _H  = 282, 52
    _BG     = "#111827"   # tło kapsułki
    _TRANS  = "#000001"   # kolor kluczowy przezroczystości (nie pojawia się w UI)

    _C = {
        "rec_ring":  "#2a1616",   # tło koła — nagrywanie
        "rec":       "#f87171",   # akcent czerwony (ikona, fala)
        "proc_ring": "#1c1c38",   # tło koła — przetwarzanie
        "proc":      "#818cf8",   # akcent fioletowy (spinner)
        "label":     "#e2e8f0",   # tekst główny
        "timer":     "#4b5563",   # tekst drugorzędny
        "pct":       "#6366f1",   # procenty
        "track":     "#1d2235",   # tło paska postępu
        "fill_r":    "#ef4444",   # pasek — nagrywanie
        "fill_p":    "#6366f1",   # pasek — przetwarzanie
        "shimmer":   "#a5b4fc",   # shimmer na pasku
    }

    def __init__(self):
        self._q: queue.Queue          = queue.Queue()
        self._thread: threading.Thread | None = None
        self._root  = None
        self._cv    = None
        self._state = "hidden"
        self._frame = 0
        self._anim_id = None

        # IDs elementów canvas
        self._circle_id = None
        self._mic_items: list[tuple] = []   # (canvas_id, "fill"|"arc"|"line")
        self._spin_id   = None
        self._lbl_id    = None
        self._sub_id    = None
        self._pct_id    = None
        self._bar_ids:  list = []
        self._pb_track  = None
        self._pb_fill   = None
        self._pb_shim   = None

        # timing
        self._start_time    = 0.0
        self._estimated_dur = 4.0

    # ── Public API (thread-safe) ──────────────────────────────────────────────

    def show_recording(self):
        self._send("recording")

    def show_processing(self, audio_duration: float = 0.0):
        rtf = _RTF_TABLE.get(
            (config.MODEL_SIZE, config.DEVICE, config.COMPUTE_TYPE), 5.0
        )
        effective_dur = max(audio_duration, _MIN_EFFECTIVE_DURATION_S)
        self._estimated_dur = _OVERHEAD_S + effective_dur / rtf
        self._start_time    = time.time()
        self._send("processing")

    def hide(self):
        self._send("hidden")

    def _send(self, state: str):
        self._q.put(state)
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(
                target=self._run, daemon=True, name="overlay-tk"
            )
            self._thread.start()

    # ── Wątek tkinter ─────────────────────────────────────────────────────────

    def _run(self):
        import tkinter as tk

        root = tk.Tk()
        self._root = root

        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.0)
        root.configure(bg=self._TRANS)
        root.resizable(False, False)

        sw = root.winfo_screenwidth()
        x  = (sw - self._W) // 2
        root.geometry(f"{self._W}x{self._H}+{x}+16")

        # True pill shape — przezroczystość przez kolor kluczowy (Win10 i Win11)
        try:
            root.attributes("-transparentcolor", self._TRANS)
        except Exception:
            pass

        # Zaokrąglenia Win11 (dodatkowy fallback)
        try:
            hwnd = root.winfo_id()
            pref = ctypes.c_int(2)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 33, ctypes.byref(pref), ctypes.sizeof(pref)
            )
        except Exception:
            pass

        cv = tk.Canvas(
            root, width=self._W, height=self._H,
            bg=self._TRANS, highlightthickness=0
        )
        cv.pack()
        self._cv = cv

        W, H = self._W, self._H
        r    = H // 2   # 26 — promień kapsułki

        # ── Kapsułka tło (dwie półkule + prostokąt środkowy) ─────────────────
        kw = {"fill": self._BG, "outline": ""}
        cv.create_oval(0, 0, r * 2, H, **kw)
        cv.create_oval(W - r * 2, 0, W, H, **kw)
        cv.create_rectangle(r, 0, W - r, H, **kw)

        # ── Koło ikony — 28×28 px, lewy margines 10 px ───────────────────────
        self._circle_id = cv.create_oval(
            10, 12, 38, 40, fill=self._C["proc_ring"], outline=""
        )

        # ── Mikrofon (w kole, centrum ≈ 24,26) ───────────────────────────────
        # Głowa: kapsułka 8×15 px (oval 20,12 → 28,27)
        # Uchwyt: łuk U poniżej głowy
        # Trzon + podstawa
        def _mi(item_id, kind):   # helper do rejestracji
            self._mic_items.append((item_id, kind))

        c = self._C["proc"]   # kolor startowy (nadpisywany przez _apply)
        _mi(cv.create_oval(20, 12, 28, 27, fill=c, outline=""),             "fill")
        _mi(cv.create_arc(17, 22, 31, 32,
                          start=0, extent=-180,
                          style="arc", outline=c, width=2),                 "arc")
        _mi(cv.create_line(24, 32, 24, 38, fill=c, width=2),               "line")
        _mi(cv.create_line(20, 38, 28, 38, fill=c, width=2),               "line")

        # ── Spinner (przetwarzanie) — obracający się łuk 270°  ────────────────
        self._spin_id = cv.create_arc(
            15, 17, 33, 35,
            start=0, extent=270,
            style="arc", outline=self._C["proc"], width=2,
            state="hidden"
        )

        # ── Tekst główny ──────────────────────────────────────────────────────
        self._lbl_id = cv.create_text(
            46, 19,
            text="Słucham…",
            fill=self._C["label"],
            font=("Segoe UI", 10, "bold"),
            anchor="w"
        )

        # ── Tekst drugorzędny (timer) ─────────────────────────────────────────
        self._sub_id = cv.create_text(
            46, 35,
            text="",
            fill=self._C["timer"],
            font=("Segoe UI", 8),
            anchor="w",
            state="hidden"
        )

        # ── Procenty ─────────────────────────────────────────────────────────
        self._pct_id = cv.create_text(
            274, 26,
            text="",
            fill=self._C["pct"],
            font=("Segoe UI", 9, "bold"),
            anchor="e",
            state="hidden"
        )

        # ── Fala dźwiękowa — 7 cienkich słupków (nagrywanie) ─────────────────
        bx, bw, bg_gap = 46, 3, 2
        my = 35
        for i in range(7):
            x0 = bx + i * (bw + bg_gap)
            bid = cv.create_rectangle(
                x0, my - 3, x0 + bw, my + 3,
                fill=self._C["rec"], outline="", state="hidden"
            )
            self._bar_ids.append(bid)

        # ── Pasek postępu — 3 px, w płaskiej części kapsułki ─────────────────
        pb_x0, pb_x1 = r + 4, W - r - 4   # 30 … 252
        pb_y0, pb_y1 = H - 8, H - 5       # 44 … 47
        self._pb_track = cv.create_rectangle(
            pb_x0, pb_y0, pb_x1, pb_y1,
            fill=self._C["track"], outline="", state="hidden"
        )
        self._pb_fill = cv.create_rectangle(
            pb_x0, pb_y0, pb_x0, pb_y1,
            fill=self._C["fill_p"], outline="", state="hidden"
        )
        self._pb_shim = cv.create_rectangle(
            pb_x0, pb_y0, pb_x0 + 20, pb_y1,
            fill=self._C["shimmer"], outline="", state="hidden"
        )

        root.withdraw()
        self._poll()
        root.mainloop()

    # ── Polling kolejki ───────────────────────────────────────────────────────

    def _poll(self):
        try:
            while True:
                state = self._q.get_nowait()
                self._apply(state)
        except queue.Empty:
            pass
        if self._root:
            self._root.after(40, self._poll)

    # ── Pomocnicze: kolor i widoczność ikon mikrofonu ─────────────────────────

    def _set_mic_color(self, color: str) -> None:
        cv = self._cv
        for item_id, kind in self._mic_items:
            if kind == "fill":
                cv.itemconfig(item_id, fill=color)
            elif kind == "arc":
                cv.itemconfig(item_id, outline=color)
            else:                           # "line"
                cv.itemconfig(item_id, fill=color)

    def _set_mic_state(self, state: str) -> None:
        for item_id, _ in self._mic_items:
            self._cv.itemconfig(item_id, state=state)

    # ── Aplikowanie stanu ─────────────────────────────────────────────────────

    def _apply(self, state: str):
        self._state = state
        root = self._root
        cv   = self._cv

        if state == "hidden":
            if self._anim_id:
                root.after_cancel(self._anim_id)
                self._anim_id = None
            self._fade_out()
            return

        root.deiconify()
        self._frame = 0

        if state == "recording":
            cv.itemconfig(self._circle_id, fill=self._C["rec_ring"])
            self._set_mic_color(self._C["rec"])
            self._set_mic_state("normal")
            cv.itemconfig(self._spin_id,  state="hidden")

            cv.itemconfig(self._lbl_id,   text="Słucham…")
            cv.itemconfig(self._sub_id,   state="hidden")
            cv.itemconfig(self._pct_id,   state="hidden")

            for bid in self._bar_ids:
                cv.itemconfig(bid, state="normal")
            cv.itemconfig(self._pb_track, state="hidden")
            cv.itemconfig(self._pb_fill,  state="hidden")
            cv.itemconfig(self._pb_shim,  state="hidden")

        elif state == "processing":
            cv.itemconfig(self._circle_id, fill=self._C["proc_ring"])
            self._set_mic_state("hidden")
            cv.itemconfig(self._spin_id,  outline=self._C["proc"], state="normal")

            cv.itemconfig(self._lbl_id,   text="Przetwarza…")
            cv.itemconfig(self._sub_id,   text="", state="normal")
            cv.itemconfig(self._pct_id,   text="0%", state="normal")

            for bid in self._bar_ids:
                cv.itemconfig(bid, state="hidden")

            pb_x0 = self._H // 2 + 4
            cv.itemconfig(self._pb_track, state="normal")
            cv.itemconfig(self._pb_fill,  fill=self._C["fill_p"], state="normal")
            cv.itemconfig(self._pb_shim,  state="normal")
            cv.coords(self._pb_fill, pb_x0, self._H - 8, pb_x0,      self._H - 5)
            cv.coords(self._pb_shim, pb_x0, self._H - 8, pb_x0 + 20, self._H - 5)

        if self._anim_id:
            root.after_cancel(self._anim_id)
        self._animate()
        self._fade_in()

    # ── Animacje ──────────────────────────────────────────────────────────────

    def _animate(self):
        if self._state == "hidden" or not self._root:
            self._anim_id = None
            return

        cv = self._cv
        self._frame += 1
        t  = self._frame

        if self._state == "recording":
            bx, bw, bg_gap = 46, 3, 2
            my = 35
            n  = len(self._bar_ids)
            for i, bid in enumerate(self._bar_ids):
                phase = i * (math.pi * 2 / n)
                h = max(2.0, abs(math.sin(t * 0.30 + phase)) * 10)
                x0 = bx + i * (bw + bg_gap)
                cv.coords(bid, x0, my - h, x0 + bw, my + h)

        elif self._state == "processing":
            # Obracający się spinner
            spin_angle = (t * 9) % 360
            cv.itemconfig(self._spin_id, start=spin_angle)

            # Pasek postępu
            elapsed   = time.time() - self._start_time
            estimated = self._estimated_dur
            progress  = min(elapsed / estimated, 0.92) if estimated > 0 else 0.0

            pb_x0 = self._H // 2 + 4      # 30
            pb_x1 = self._W - self._H // 2 - 4  # 252
            pb_y0, pb_y1 = self._H - 8, self._H - 5

            fill_x = pb_x0 + progress * (pb_x1 - pb_x0)
            cv.coords(self._pb_fill, pb_x0, pb_y0, fill_x, pb_y1)

            # Shimmer
            shim_w    = 20
            fill_span = fill_x - pb_x0
            if fill_span > shim_w:
                pos    = 0.5 + 0.45 * math.sin(t * 0.18)
                shim_x = pb_x0 + pos * (fill_span - shim_w)
                cv.coords(self._pb_shim, shim_x, pb_y0, shim_x + shim_w, pb_y1)
                cv.itemconfig(self._pb_shim, state="normal")
            else:
                cv.itemconfig(self._pb_shim, state="hidden")

            # Aktualizuj tekst
            cv.itemconfig(self._sub_id, text=f"{elapsed:.1f}s / ~{estimated:.1f}s")
            cv.itemconfig(self._pct_id, text=f"{int(progress * 100)}%")

        self._anim_id = self._root.after(45, self._animate)

    def _fade_in(self, alpha: float = 0.0):
        if not self._root or self._state == "hidden":
            return
        alpha = min(alpha + 0.12, 0.95)
        self._root.attributes("-alpha", alpha)
        if alpha < 0.95:
            self._root.after(18, self._fade_in, alpha)

    def _fade_out(self, alpha: float = 0.95):
        if not self._root:
            return
        if alpha <= 0.0:
            self._root.withdraw()
            self._root.attributes("-alpha", 0.95)
            return
        self._root.attributes("-alpha", alpha)
        self._root.after(18, self._fade_out, alpha - 0.12)

# ─────────────────────────────────────────────────────────────────────────────
# Pomocnicza: wątek daemon z pełnym logowaniem wyjątków
# ─────────────────────────────────────────────────────────────────────────────

def _logged_thread(fn, name: str, *args, **kwargs) -> threading.Thread:
    """
    Uruchamia fn w wątku daemon z pełnym logowaniem nieobsłużonych wyjątków.
    Bez tego wrapper'a wyjątek w daemon thread ginie bezśladowo — nie trafia
    do error.log i nie widać go w konsoli gdy app działa przez run_silent.vbs.
    """
    import traceback as _tbmod

    def _target():
        try:
            fn(*args, **kwargs)
        except Exception:
            _log(
                f"[{name}] NIEOBSŁUGIWANY WYJĄTEK:\n{_tbmod.format_exc()}",
                level="ERROR",
            )

    t = threading.Thread(target=_target, daemon=True, name=name)
    t.start()
    return t


# ─────────────────────────────────────────────────────────────────────────────
# Klawisze-modyfikatory — keyboard.add_hotkey() NIE odpala się dla samego
# modyfikatora (czeka na "prawdziwy" klawisz po +). Dla tych hotkeyów musimy
# użyć keyboard.on_press_key()/on_release_key() zamiast add_hotkey().
# Dotyczy m.in. "right ctrl", "right alt" w menu trayu.
# ─────────────────────────────────────────────────────────────────────────────
_MODIFIER_KEYS = frozenset({
    "ctrl", "control",
    "shift",
    "alt",
    "win", "windows", "cmd", "command",
    "left ctrl",  "right ctrl",
    "left shift", "right shift",
    "left alt",   "right alt", "alt gr", "altgr",
    "left win",   "right win", "left windows", "right windows",
})


# ─────────────────────────────────────────────────────────────────────────────
# Klawisze NIEUŻYWALNE jako hotkey „trzymaj-by-nagrywać".
# Pause/Break: na Windows klawisz dostarcza kod naciśnięcia (make) ORAZ puszczenia
# (break) razem, w jednej serii, już przy fizycznym WCIŚNIĘCIU (sekwencja scancode
# E1 1D 45). Przy fizycznym puszczeniu nie wysyła nic. Dla modelu hold-to-talk
# (press=start, release=stop) oznacza to, że stop_recording odpala się natychmiast
# po start_recording → nagranie ma ~0 długości i jest odrzucane przez MIN_DURATION.
# Efekt: hotkey „nic nie robi". Tego nie da się naprawić w kodzie — to zachowanie
# samego klawisza. Blokujemy go w menu, w dialogu „Własny…" i przy starcie.
# ─────────────────────────────────────────────────────────────────────────────
_BLOCKED_HOTKEYS = frozenset({"pause", "pause break"})


# ─────────────────────────────────────────────────────────────────────────────
# Klasa główna
# ─────────────────────────────────────────────────────────────────────────────

class WhisperVoice:
    def __init__(self):
        self.model: WhisperModel | None = None
        self.icon: pystray.Icon | None = None

        # Stan nagrywania
        self._recording = False
        self._audio_chunks: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()

        # Handles hooków klawiatury — śledzimy własne rejestracje, żeby
        # _change_hotkey mógł je punktowo zdjąć (zamiast unhook_all, które
        # niszczy też hooki innych komponentów, np. capture w dialogu Własny).
        self._hotkey_handle  = None   # handle z keyboard.add_hotkey
        self._press_handle   = None   # handle z keyboard.on_press_key (bare modifier)
        self._release_handle = None   # handle z keyboard.on_release / on_release_key
        self._hotkey_state   = {"active": False}

        # Nakładka wizualna
        self.overlay = RecordingOverlay()

        # Uchwyt okna aktywnego przed nagrywaniem — przywracamy fokus przed CTRL+V
        # żeby tekst trafił do właściwego pola a nie do losowego okna w tle.
        self._focus_hwnd: int = 0

    # ── Ładowanie modelu ─────────────────────────────────────────────

    def load_model(self) -> None:
        """Ładuje model Whisper w tle; aktualizuje ikonę po zakończeniu."""
        _log(f"load_model START — model: {config.MODEL_SIZE}, device: {config.DEVICE}, "
             f"compute: {config.COMPUTE_TYPE}")
        self._set_icon(config.COLOR_LOADING, tip="WhisperVoice — ładowanie modelu…")
        _cache = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
        print(f"[WhisperVoice] Ładuję model: {config.MODEL_SIZE} "
              f"({config.DEVICE}, {config.COMPUTE_TYPE})…")
        print(f"[WhisperVoice] Cache modeli: {_cache}  "
              f"(large-v3 ≈ 3 GB przy pierwszym pobraniu)")

        # ── Pierwsze uruchomienie: komunikat o pobieraniu modelu ────────
        # Przy uruchomieniu przez run_silent.vbs konsola jest ukryta, więc
        # tqdm progress bar faster-whisper trafia donikąd. MsgBox informuje
        # użytkownika ŻE i ILE się pobiera, zanim ikona zacznie wisieć 30 min.
        _model_dir = os.path.join(_cache, f"models--Systran--faster-whisper-{config.MODEL_SIZE}")
        if not os.path.exists(_model_dir):
            _size_estimate = {
                "tiny":     "~75 MB",
                "base":     "~145 MB",
                "small":    "~480 MB",
                "medium":   "~1,5 GB",
                "large-v2": "~3 GB",
                "large-v3": "~3 GB",
            }.get(config.MODEL_SIZE, "~1,5 GB")
            _first_run_msg = (
                f"WhisperVoice — PIERWSZE URUCHOMIENIE\n\n"
                f"Aplikacja zaraz pobierze model Whisper AI z serwerów HuggingFace.\n\n"
                f"  Model:    {config.MODEL_SIZE}\n"
                f"  Rozmiar:  {_size_estimate}\n"
                f"  Źródło:   huggingface.co/Systran/faster-whisper-{config.MODEL_SIZE}\n"
                f"  Cel:      {_cache}\n\n"
                f"Pobieranie może potrwać od kilku do kilkudziesięciu minut\n"
                f"w zależności od prędkości łącza internetowego.\n\n"
                f"WAŻNE:\n"
                f"  • Nie zamykaj aplikacji — restart oznacza pobieranie od 0%.\n"
                f"  • Pobieranie odbywa się raz. Kolejne uruchomienia są offline.\n"
                f"  • Aplikacja będzie gotowa, gdy ikona w trayu zmieni kolor\n"
                f"    z pomarańczowego na NIEBIESKI.\n\n"
                f"Kliknij OK i poczekaj cierpliwie."
            )
            try:
                ctypes.windll.user32.MessageBoxW(0, _first_run_msg,
                    "WhisperVoice — pobieranie modelu AI", 0x40)  # MB_ICONINFORMATION
            except Exception:
                pass
            print(f"[WhisperVoice] Pobieranie modelu {config.MODEL_SIZE} ({_size_estimate})…")

        try:
            self.model = WhisperModel(
                config.MODEL_SIZE,
                device=config.DEVICE,
                compute_type=config.COMPUTE_TYPE,
                num_workers=config.NUM_WORKERS,
                cpu_threads=config.CPU_THREADS,
            )
            print("[WhisperVoice] Model gotowy!")
            _log(f"load_model OK — model: {config.MODEL_SIZE} na {config.DEVICE.upper()} gotowy")
            _play_beep("SystemAsterisk")   # standardowy dźwięk informacji Windows
            self._set_icon(config.COLOR_IDLE,
                           tip=f"WhisperVoice — {config.HOTKEY.upper()} aby nagrać")
            # Powiadomienie balonowe "gotowy" — raz po załadowaniu
            if self.icon:
                try:
                    self.icon.notify(
                        f"WhisperVoice gotowy!\nPrzytrzymaj {config.HOTKEY.upper()} i mów.",
                        "WhisperVoice"
                    )
                except Exception:
                    pass
        except Exception as exc:
            import traceback as _tb_load
            _log(f"load_model BŁĄD: {exc}\n{_tb_load.format_exc()}", level="ERROR")
            print(f"[WhisperVoice] Błąd ładowania modelu: {exc}")
            print("             Sprawdź DEVICE i COMPUTE_TYPE w config.py")
            self._set_icon((150, 150, 150),
                           tip="WhisperVoice — błąd modelu, sprawdź konsolę")

    # ── Nagrywanie ───────────────────────────────────────────────────

    def _audio_callback(self, indata: np.ndarray, frames: int, t, status) -> None:
        with self._lock:
            if self._recording:
                self._audio_chunks.append(indata.copy())

    def start_recording(self) -> None:
        _log("start_recording wywołane")
        if self.model is None:
            print("[WhisperVoice] Model jeszcze się ładuje…")
            # Daj użytkownikowi wyraźny feedback zamiast cichego zignorowania hotkey
            _play_beep("SystemExclamation")              # dźwięk ostrzeżenia Windows
            _show_toast("⏳  Model AI się ładuje — poczekaj kilka sekund…")
            self._set_icon(config.COLOR_LOADING,
                           tip="WhisperVoice ⏳ — model się ładuje, poczekaj…")
            return

        with self._lock:
            if self._recording:
                return
            self._recording = True
            self._audio_chunks = []

        # Zapamiętaj aktywne okno PRZED nagrywaniem — do przywrócenia fokusu przy wklejaniu
        try:
            self._focus_hwnd = ctypes.windll.user32.GetForegroundWindow()
            _log(f"start_recording — zapamiętano HWND fokusu: {self._focus_hwnd}")
        except Exception as _e:
            self._focus_hwnd = 0
            _log(f"start_recording — nie udało się pobrać HWND: {_e}", level="WARN")

        print("[WhisperVoice] 🎙 Nagrywanie…")
        _log("start_recording — mikrofon otwarty, nagrywanie aktywne")
        self._set_icon(config.COLOR_RECORD, dot=True,
                       tip="WhisperVoice — NAGRYWA…")
        self.overlay.show_recording()

        try:
            self._stream = sd.InputStream(
                samplerate=config.SAMPLE_RATE,
                channels=1,
                dtype="float32",
                blocksize=config.BLOCK_SIZE,
                callback=self._audio_callback,
            )
            self._stream.start()
        except Exception as exc:
            import traceback as _tb_mic
            _log(f"start_recording BŁĄD mikrofonu: {exc}\n{_tb_mic.format_exc()}", level="ERROR")
            print(f"[WhisperVoice] Błąd mikrofonu: {exc}")
            # Cleanup: jeśli InputStream powstał ale .start() padł, zamknij go
            # ręcznie — inaczej deskryptor mikrofonu wisi do końca procesu.
            if self._stream is not None:
                try:
                    self._stream.close()
                except Exception:
                    pass
                self._stream = None
            with self._lock:
                self._recording = False
            self.overlay.hide()
            self._set_icon(config.COLOR_IDLE,
                           tip=f"WhisperVoice — {config.HOTKEY.upper()} aby nagrać")

    def stop_recording(self) -> None:
        # Wstępne sprawdzenie — bez modyfikacji stanu
        with self._lock:
            if not self._recording:
                return

        # Post-roll: kontynuuj nagrywanie przez chwilę po puszczeniu hotkey,
        # żeby nie obcinać ostatniej sylaby / końca słowa.
        post_roll_s = getattr(config, "POST_ROLL_MS", 0) / 1000.0
        if post_roll_s > 0:
            time.sleep(post_roll_s)

        with self._lock:
            if not self._recording:
                return
            self._recording = False
            chunks = list(self._audio_chunks)
            self._audio_chunks = []

        # Oblicz długość nagrania do szacowania czasu transkrypcji
        _total_samples = sum(c.shape[0] for c in chunks)
        _audio_dur = _total_samples / config.SAMPLE_RATE

        # Pusty bufor — nie pokazujemy overlay processing, od razu ukrywamy
        if _total_samples == 0:
            self.overlay.hide()
            self._set_icon(config.COLOR_IDLE,
                           tip=f"WhisperVoice — {config.HOTKEY.upper()} aby nagrać")
            if self._stream:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception:
                    pass
                self._stream = None
            return

        print("[WhisperVoice] ⏹ Zatrzymano, przetwarzam…")
        _log(f"stop_recording — długość audio: {_audio_dur:.2f}s, próbki: {_total_samples}")
        self._set_icon(config.COLOR_PROCESS,
                       tip="WhisperVoice — transkrypcja…")
        self.overlay.show_processing(_audio_dur)

        if self._stream:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None

        # Transkrypcja w osobnym wątku — _logged_thread przechwytuje każdy wyjątek do logu
        _logged_thread(self._transcribe_and_inject, "transcribe", chunks)

    # ── Transkrypcja ─────────────────────────────────────────────────

    def _transcribe_and_inject(self, chunks: list[np.ndarray]) -> None:
        _log(f"_transcribe_and_inject WEJŚCIE — chunków: {len(chunks)}")
        if not chunks:
            _log("_transcribe_and_inject — brak chunków audio, powrót do IDLE")
            self.overlay.hide()
            self._set_icon(config.COLOR_IDLE,
                           tip=f"WhisperVoice — {config.HOTKEY.upper()} aby nagrać")
            return

        audio = np.concatenate(chunks, axis=0).flatten()
        duration = len(audio) / config.SAMPLE_RATE

        # Normalizacja głośności — wyrównuje nagrania ciche i głośne.
        # Ograniczamy wzmocnienie do 10× żeby nie amplifikować szumu w nagraniach
        # praktycznie pustych (peak ~ 0.001 dawał ~950× gain i podbijał szum tła).
        if config.AUDIO_NORMALIZATION:
            peak = float(np.max(np.abs(audio)))
            if peak > 1e-3:
                gain = min(0.95 / peak, 10.0)
                audio = audio * gain

        if duration < config.MIN_DURATION:
            print(f"[WhisperVoice] Za krótkie ({duration:.2f}s) — ignoruję.")
            self.overlay.hide()
            self._set_icon(config.COLOR_IDLE,
                           tip=f"WhisperVoice — {config.HOTKEY.upper()} aby nagrać")
            return

        # Dobór profilu na podstawie długości nagrania
        # (inspect zaimportowany na poziomie modułu — bez per-call overhead)
        _inspect = inspect
        _kwargs, _profile_name = get_transcribe_kwargs(duration)

        # Dodaj parametry nieobsługiwane przez starsze wersje biblioteki
        _kwargs.setdefault("multilingual",                  config.MULTILINGUAL)
        _kwargs.setdefault("max_initial_timestamp",         config.MAX_INITIAL_TIMESTAMP)
        _kwargs.setdefault("prepend_punctuations",          config.PREPEND_PUNCTUATIONS)
        _kwargs.setdefault("append_punctuations",           config.APPEND_PUNCTUATIONS)
        _kwargs.setdefault("language_detection_threshold",  config.LANGUAGE_DETECTION_THRESHOLD)
        _kwargs.setdefault("language_detection_segments",   config.LANGUAGE_DETECTION_SEGMENTS)

        # Usuń parametry nieobsługiwane przez zainstalowaną wersję biblioteki
        _supported = set(_inspect.signature(self.model.transcribe).parameters)
        _kwargs = {k: v for k, v in _kwargs.items() if k in _supported}

        # Usuń opcjonalne parametry z wartością None — niektóre wersje faster-whisper
        # nie akceptują None jawnie (oczekują braku parametru lub wartości domyślnej)
        for _opt in ("clip_timestamps", "prefix", "hallucination_silence_threshold"):
            if _kwargs.get(_opt) is None:
                _kwargs.pop(_opt, None)

        # Filtruj też vad_parameters — usuń klucze nieobsługiwane przez VadOptions
        # w zainstalowanej wersji (np. min_silence_at_max_speech, use_max_poss_sil_at_max_speech)
        if isinstance(_kwargs.get("vad_parameters"), dict):
            try:
                from faster_whisper.vad import VadOptions
                _vad_supported = set(
                    _inspect.signature(VadOptions.__init__).parameters
                ) - {"self"}
                _kwargs["vad_parameters"] = {
                    k: v for k, v in _kwargs["vad_parameters"].items()
                    if k in _vad_supported
                }
            except Exception:
                pass

        print(f"[WhisperVoice] Profil: {_profile_name} | Długość audio: {duration:.2f}s")

        # Timeout dynamiczny: CPU = max(duration * 8, 90s); GPU = max(duration * 2, 30s)
        # Chroni przed deadlockiem gdy faster-whisper zawiesi się na materializacji generatora.
        if config.DEVICE == "cpu":
            _timeout_s = max(duration * 8, 90.0)
        else:
            _timeout_s = max(duration * 2, 30.0)

        _log(f"_transcribe START — profil: {_profile_name}, "
             f"długość: {duration:.2f}s, timeout: {_timeout_s:.0f}s, "
             f"device: {config.DEVICE}, model: {config.MODEL_SIZE}")

        # Wątek transkrypcji jako DAEMON + queue do przekazania wyniku.
        # Świadomie NIE używamy ThreadPoolExecutor: jego wątki robocze nie są
        # daemonami, a concurrent.futures rejestruje atexit-hook, który dołącza
        # (join) wątki przy zamykaniu procesu. Gdyby transkrypcja realnie zawisła,
        # zamknięcie aplikacji blokowałoby się na takim wątku. Daemon-thread nie
        # blokuje wyjścia z procesu — to chroni przed "wiszącą" aplikacją.
        _result_q: queue.Queue = queue.Queue(maxsize=1)

        def _do_transcribe():
            try:
                # list() materializuje generator — tu może wisieć bez timeout'u
                _segs, _inf = self.model.transcribe(audio, **_kwargs)
                _result_q.put(("ok", (list(_segs), _inf)))
            except Exception as _e:
                _result_q.put(("err", _e))

        _worker = threading.Thread(
            target=_do_transcribe, name="whisper-transcr", daemon=True
        )
        _worker.start()
        _t_start = time.time()

        # Jeden zewnętrzny try/except/finally gwarantuje że overlay.hide()
        # i _set_icon() ZAWSZE zostają wywołane — nawet przy Timeout lub innym wyjątku.
        try:
            # ── Oczekiwanie na wynik z timeoutem ──────────────────────────────
            try:
                _status, _payload = _result_q.get(timeout=_timeout_s)
            except queue.Empty:
                # Timeout — wątek (daemon) wisi w tle, ale NIE blokuje zamknięcia.
                _t_elapsed = time.time() - _t_start
                _log(
                    f"_transcribe TIMEOUT po {_t_elapsed:.1f}s "
                    f"(limit: {_timeout_s:.0f}s) — powrót do IDLE",
                    level="ERROR",
                )
                raise RuntimeError(
                    f"Timeout transkrypcji ({_timeout_s:.0f}s). "
                    f"Spróbuj krótszego nagrania lub modelu 'medium' na CPU."
                )

            if _status == "err":
                raise _payload          # wyjątek z wątku — obsłużony niżej
            segments, info = _payload

            _t_elapsed = time.time() - _t_start

            print(f"[WhisperVoice] Czas transkrypcji: {_t_elapsed:.2f}s | "
                  f"Segmentow: {len(segments)} | "
                  f"Jezyk: {info.language} (p={info.language_probability:.2f})")
            _log(f"_transcribe OK — czas: {_t_elapsed:.2f}s, "
                 f"segmentów: {len(segments)}, "
                 f"język: {info.language} (p={info.language_probability:.2f})")

            # ── Post-processing i wklejanie ───────────────────────────────────
            for _i, _seg in enumerate(segments, 1):
                _tok_count = len(_seg.tokens) if hasattr(_seg, "tokens") and _seg.tokens else 0
                _temp = getattr(_seg, "temperature", "?")
                print(
                    f"  [seg {_i:02d}]"
                    f"  {_seg.start:6.2f}s-{_seg.end:6.2f}s"
                    f"  logp={_seg.avg_logprob:.3f}"
                    f"  compr={_seg.compression_ratio:.2f}"
                    f"  no_speech={_seg.no_speech_prob:.3f}"
                    f"  temp={_temp}"
                    f"  tok={_tok_count}"
                )

            # ── Warstwa 2 filtra halucynacji: odrzuć całe SEGMENTY, które są
            #    akustycznie ciszą (wysokie no_speech_prob) A JEDNOCZEŚNIE ich
            #    treść pasuje do znanego wzorca outra/napisów. Oba warunki naraz
            #    minimalizują ryzyko ucięcia prawdziwej, cichej mowy.
            _nsp_drop = getattr(config, "NO_SPEECH_DROP_THRESHOLD", 0.6)
            _kept_parts: list[str] = []
            for seg in segments:
                _t = (seg.text or "").strip()
                if not _t:
                    continue
                _nsp = float(getattr(seg, "no_speech_prob", 0.0) or 0.0)
                if _nsp >= _nsp_drop and looks_like_hallucination(_t):
                    _log(f"_transcribe — odrzucono segment-halucynację "
                         f"(no_speech={_nsp:.2f}): '{_t[:60]}'", level="WARN")
                    print(f"[WhisperVoice] ⚠ Segment-halucynacja odrzucona "
                          f"(no_speech={_nsp:.2f}): '{_t[:60]}'")
                    continue
                _kept_parts.append(_t)

            text = " ".join(_kept_parts)
            text = postprocess_transcript(text)   # normalizacja spacji/interpunkcji
            text = filter_hallucinations(text)     # Warstwa 1: wzorce + całość-halucynacja

            if text:
                print(f"[WhisperVoice] Tekst: {text}")
                _log(f"_inject START — tekst: {text[:80]}{'…' if len(text) > 80 else ''}")
                self._inject_text(text)
            else:
                print("[WhisperVoice] Brak mowy / zbyt cicho.")
                _log("_transcribe — brak mowy lub zbyt cicho (pusty tekst)")

        except Exception as exc:
            import traceback as _tb_tr
            _log(f"_transcribe BŁĄD: {exc}\n{_tb_tr.format_exc()}", level="ERROR")
            print(f"[WhisperVoice] Blad transkrypcji: {exc}")

        finally:
            # Gwarantowane wykonanie niezależnie od wyniku (OK / błąd / timeout)
            _log("_transcribe_and_inject KONIEC — powrót do IDLE")
            self.overlay.hide()
            self._set_icon(config.COLOR_IDLE,
                           tip=f"WhisperVoice - {config.HOTKEY.upper()} aby nagrac")

    # -- Wklejanie tekstu ------------------------------------------------

    def _inject_text(self, text: str) -> None:
        """Wkleja tekst w aktywne pole tekstowe przez schowek (CTRL+V)."""
        _log(f"_inject_text START — metoda: {config.INJECT_METHOD}, znaków: {len(text)}")

        # Przywróć fokus do okna które było aktywne przed nagrywaniem.
        # SetForegroundWindow może zawieść gdy app jest w tle (Windows ogranicza
        # to do procesów na pierwszym planie) — dlatego próba jest w try/except.
        _hwnd = getattr(self, "_focus_hwnd", 0)
        if _hwnd:
            try:
                ctypes.windll.user32.SetForegroundWindow(_hwnd)
                time.sleep(0.06)   # krótka pauza na stabilizację fokusu
                _log(f"_inject_text — fokus przywrócony do HWND: {_hwnd}")
            except Exception as _fe:
                _log(f"_inject_text — SetForegroundWindow({_hwnd}) nie powiodło się: {_fe}",
                     level="WARN")

        time.sleep(config.INJECT_DELAY)

        if config.INJECT_METHOD == "clipboard":
            old_clip = ""
            try:
                old_clip = pyperclip.paste() or ""
            except Exception:
                pass

            try:
                pyperclip.copy(text)
            except Exception as exc:
                print(f"[WhisperVoice] Blad schowka (copy): {exc}")
                return
            time.sleep(0.05)
            try:
                # CTRL+V przez bibliotekę keyboard (MIT) — wcześniej pyautogui,
                # usunięty bo wciągał zależność na licencji GPLv3 (mouseinfo).
                keyboard.send("ctrl+v")
                _log("_inject_text — CTRL+V wysłane")
            except Exception as exc:
                _log(f"_inject_text BŁĄD CTRL+V: {exc}", level="ERROR")
                print(f"[WhisperVoice] Blad symulacji CTRL+V: {exc}")

            time.sleep(0.25)

            if old_clip:
                try:
                    pyperclip.copy(old_clip)
                except Exception:
                    pass

            _log("_inject_text KONIEC")

        else:
            # Metoda typing przez keyboard.write (MIT) — wcześniej pyautogui.write.
            _log("_inject_text — metoda typing (keyboard.write)")
            keyboard.write(text, delay=0.01)
            _log("_inject_text KONIEC")

    # -- Hotkey ----------------------------------------------------------

    def _cleanup_hotkey_hooks(self) -> None:
        h = self._hotkey_handle
        if h is not None:
            try:
                keyboard.remove_hotkey(h)
            except Exception as exc:
                print(f"[WhisperVoice] remove_hotkey: {exc}")
        h = self._press_handle
        if h is not None:
            try:
                keyboard.unhook(h)
            except Exception as exc:
                print(f"[WhisperVoice] unhook(press): {exc}")
        h = self._release_handle
        if h is not None:
            try:
                keyboard.unhook(h)
            except Exception as exc:
                print(f"[WhisperVoice] unhook(release): {exc}")
        self._hotkey_handle  = None
        self._press_handle   = None
        self._release_handle = None

    def _setup_hotkey(self) -> None:
        if not _check_keyboard_permissions():
            print("[WhisperVoice] Hotkey nie zostanie zarejestrowany - brak uprawnien.")
            self._set_icon((150, 80, 80), tip="WhisperVoice - blad uprawnien hotkey")
            return

        self._cleanup_hotkey_hooks()
        self._hotkey_state["active"] = False

        hotkey_lower = (config.HOTKEY or "").strip().lower()

        # Migracja: Pause/Break był zalecanym presetem w v3.3, ale jest nieużywalny
        # dla hold-to-talk (patrz _BLOCKED_HOTKEYS). Jeśli użytkownik ma go zapisanego
        # w configu, podmieniamy na działający Scroll Lock, zamiast zostawiać martwy
        # hotkey, który cicho nic nie nagrywa.
        if hotkey_lower in _BLOCKED_HOTKEYS:
            _fallback = "scroll lock"
            print(f"[WhisperVoice] Hotkey '{hotkey_lower}' jest nieuzywalny "
                  f"(Pause/Break) - przelaczam na '{_fallback}'.")
            config.HOTKEY = _fallback
            try:
                _patch_config_file("HOTKEY", _fallback)
            except Exception as exc:
                print(f"[WhisperVoice] Nie udalo sie zapisac fallbacku hotkey: {exc}")
            hotkey_lower = _fallback

        hotkey_keys  = [k.strip().lower() for k in hotkey_lower.split("+") if k.strip()]
        if not hotkey_keys:
            print(f"[WhisperVoice] Pusty hotkey w config.HOTKEY - pomijam rejestracje.")
            return

        is_bare_modifier = ("+" not in hotkey_lower) and (hotkey_lower in _MODIFIER_KEYS)

        def on_press(_event=None):
            if self._hotkey_state["active"] or self._recording:
                return
            self._hotkey_state["active"] = True
            _logged_thread(self.start_recording, "hotkey-press")

        def on_release(event: keyboard.KeyboardEvent) -> None:
            key = (getattr(event, "name", "") or "").lower()
            if not self._hotkey_state["active"]:
                return
            if is_bare_modifier or key in hotkey_keys:
                self._hotkey_state["active"] = False
                _logged_thread(self.stop_recording, "hotkey-release")

        try:
            if is_bare_modifier:
                # Używamy keyboard.hook() zamiast on_press_key/on_release_key,
                # bo on_press_key("right ctrl") może dopasowywać również "ctrl"
                # (lewy Ctrl), przez co Lewy Ctrl+V wywoływałby aplikację.
                # hook() daje nam surowe zdarzenia — filtrujemy po DOKŁADNEJ nazwie,
                # co gwarantuje rozróżnienie lewej i prawej strony klawiatury.
                # suppress=False — nie blokujemy klawisza dla innych aplikacji
                # (suppress=True dla "right alt" blokowałoby AltGr: ą ę ó ź ż).
                _hotkey_pressed = {"v": False}

                def _bare_hook(event, _hl=hotkey_lower, _s=_hotkey_pressed):
                    name = (getattr(event, "name", "") or "").lower()
                    if name != _hl:
                        return
                    if event.event_type == keyboard.KEY_DOWN and not _s["v"]:
                        _s["v"] = True
                        on_press(event)
                    elif event.event_type == keyboard.KEY_UP and _s["v"]:
                        _s["v"] = False
                        on_release(event)

                self._press_handle   = keyboard.hook(_bare_hook, suppress=False)
                self._release_handle = None   # hook obsługuje press+release razem
            else:
                # suppress=True dla klawiszy bez modyfikatora (np. F12) działa OK.
                # Dla hotkey z modyfikatorem (ctrl+space, alt+x itp.) suppress=True
                # powoduje że globalny hook blokuje WSZYSTKIE zdarzenia CTRL, przez co
                # CTRL+C / CTRL+V przestają działać w innych aplikacjach.
                # Rozwiązanie: suppress=False gdy hotkey zawiera modyfikator.
                has_modifier = any(k in _MODIFIER_KEYS for k in hotkey_keys)
                self._hotkey_handle  = keyboard.add_hotkey(
                    config.HOTKEY, on_press, suppress=not has_modifier,
                )
                self._release_handle = keyboard.on_release(on_release)
        except Exception as exc:
            print(f"[WhisperVoice] Blad rejestracji hotkey '{config.HOTKEY}': {exc}")
            self._set_icon((150, 80, 80), tip=f"WhisperVoice - blad hotkey: {exc}")

    # -- Tray ------------------------------------------------------------

    def _set_icon(self, color: tuple, dot: bool = False, tip: str = "") -> None:
        if self.icon:
            self.icon.icon = _draw_icon(color, show_dot=dot)
            if tip:
                self.icon.title = tip

    # -- Pomocnicze factory methods dla menu -----------------------------

    def _menu_action(self, callback, val):
        def action(icon, item):
            _logged_thread(callback, "menu-action", val)
        return action

    @staticmethod
    def _menu_checked(get_fn, val):
        def checked(item):
            return get_fn() == val
        return checked

    def _build_menu(self) -> pystray.Menu:
        # -- Podmenu: Jakosc modelu
        model_sizes = [
            ("tiny",     "tiny     - najszybszy, CPU"),
            ("base",     "base     - szybki, CPU"),
            ("small",    "small    - balans CPU"),
            ("medium",   "medium   - dobry, CPU/GPU"),
            ("large-v2", "large-v2 - bardzo dobry, GPU"),
            ("large-v3", "large-v3 - najlepszy, GPU"),
        ]
        model_menu = pystray.Menu(*[
            pystray.MenuItem(
                label,
                self._menu_action(self._change_model_size, size),
                checked=self._menu_checked(lambda: config.MODEL_SIZE, size),
            )
            for size, label in model_sizes
        ])

        # -- Podmenu: Precyzja (beam_size)
        beam_options = [
            (1,  "1  - blyskaiwczny (mniejsza dokladnosc)"),
            (5,  "5  - standardowy"),
            (8,  "8  - zalecany dla GPU"),
            (10, "10 - maksymalnie dokladny (wolniejszy)"),
        ]
        beam_menu = pystray.Menu(*[
            pystray.MenuItem(
                label,
                self._menu_action(self._change_beam_size, beam),
                checked=self._menu_checked(lambda: config.BEAM_SIZE, beam),
            )
            for beam, label in beam_options
        ])

        # -- Podmenu: Jezyk
        lang_options = [
            ("pl",   "Polski (pl)"),
            ("en",   "Angielski (en)"),
            (None,   "Auto-detekcja"),
        ]
        lang_menu = pystray.Menu(*[
            pystray.MenuItem(
                label,
                self._menu_action(self._change_language, lang),
                checked=self._menu_checked(lambda: config.LANGUAGE, lang),
            )
            for lang, label in lang_options
        ])

        # -- Podmenu: Hotkey
        hotkey_presets = [
            ("scroll lock",  "Scroll Lock  (zalecane)"),
            ("right ctrl",   "Prawy Ctrl"),
            ("right alt",    "Prawy Alt"),
            ("f13",          "F13  (rozszerzone klawiatury)"),
            ("ctrl+space",   "Ctrl+Space"),
        ]
        hotkey_menu = pystray.Menu(
            *[
                pystray.MenuItem(
                    label,
                    self._menu_action(self._change_hotkey, hk),
                    checked=self._menu_checked(
                        lambda: (config.HOTKEY or "").strip().lower(), hk
                    ),
                )
                for hk, label in hotkey_presets
            ],
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Wlasny...",
                lambda icon, item: _logged_thread(
                    self._open_hotkey_capture_dialog, "hotkey-dialog"
                ),
            ),
        )

        # -- Podmenu: Styl ikony
        icon_styles = [
            ("letter", "W  - litera (zalecane)"),
            ("wave",   "== - fale / equalizer"),
            ("mic",    "o  - mikrofon (styl klasyczny)"),
        ]
        icon_style_menu = pystray.Menu(*[
            pystray.MenuItem(
                label,
                self._menu_action(self._change_icon_style, s),
                checked=self._menu_checked(
                    lambda: getattr(config, "ICON_STYLE", "letter"), s
                ),
            )
            for s, label in icon_styles
        ])

        # -- Podmenu: Dzwieki
        _snd = getattr(config, "SOUND_FEEDBACK", True)
        sound_label = f"Dzwieki potwierdzenia  {'[wl]' if _snd else '[wyl]'}"
        sound_menu = pystray.Menu(
            pystray.MenuItem(
                sound_label,
                lambda icon, item: _logged_thread(self._toggle_sound_feedback, "menu-sound"),
            ),
        )

        # -- Podmenu: Zwroty grzecznosciowe
        _pf = getattr(config, "POLITE_FORMS_ENABLED", True)
        polite_label = f"Zwroty grzecznosciowe  {'[wl]' if _pf else '[wyl]'}"
        polite_menu = pystray.Menu(
            pystray.MenuItem(
                polite_label,
                lambda icon, item: _logged_thread(self._toggle_polite_forms, "menu-polite"),
            ),
        )

        # -- Menu glowne
        _device_label = "GPU" if config.DEVICE == "cuda" else "CPU"
        model_label = f"Model: {config.MODEL_SIZE}  |  {_device_label}"
        return pystray.Menu(
            pystray.MenuItem(config.APP_NAME, None, enabled=False),
            pystray.MenuItem(model_label, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Ustawienia", pystray.Menu(
                pystray.MenuItem("Jakosc modelu", model_menu),
                pystray.MenuItem("Dokladnosc / szybkosc", beam_menu),
                pystray.MenuItem("Jezyk rozpoznawania", lang_menu),
                pystray.MenuItem("Hotkey", hotkey_menu),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Styl ikony", icon_style_menu),
                pystray.MenuItem("Dzwieki", sound_menu),
                pystray.MenuItem("Pisownia", polite_menu),
            )),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "O aplikacji",
                lambda icon, item: _logged_thread(self._show_about, "menu-about")
            ),
            pystray.MenuItem(
                "Licencje (third-party)",
                lambda icon, item: _logged_thread(self._open_licenses, "menu-licenses")
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Zakoncz", self._quit),
        )

    def _quit(self, icon=None, item=None) -> None:
        print("[WhisperVoice] Zamykanie...")
        if self.icon:
            self.icon.stop()

    # -- O aplikacji / Licencje -----------------------------------------

    def _show_about(self) -> None:
        msg = (
            f"WhisperVoice  v3.4  |  build 15.07.2026\n\n"
            f"Lokalny voice-to-text oparty na Whisper AI (OpenAI).\n"
            f"Dziala offline po pierwszym uruchomieniu.\n\n"
            f"Autor:    Mariusz Swiergula\n"
            f"Licencja: MIT\n\n"
            f"Konfiguracja:\n"
            f"  Model:   {config.MODEL_SIZE}\n"
            f"  Device:  {config.DEVICE.upper()}\n"
            f"  Compute: {config.COMPUTE_TYPE}\n"
            f"  Hotkey:  {config.HOTKEY.upper()}\n"
            f"  Ikona:   {getattr(config, 'ICON_STYLE', 'letter')}\n\n"
            f"Lista licencji komponentow zewnetrznych:\n"
            f"  Menu tray -> Licencje (third-party)"
        )
        ctypes.windll.user32.MessageBoxW(
            0, msg, "O aplikacji - WhisperVoice", 0x40
        )

    def _open_licenses(self) -> None:
        lic_path = os.path.join(_APP_DIR, "THIRD_PARTY_LICENSES.txt")
        if os.path.exists(lic_path):
            os.startfile(lic_path)
        else:
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Nie znaleziono pliku:\n{lic_path}",
                "WhisperVoice - Licencje",
                0x30
            )

    # -- Zmiana ustawien z trayu ----------------------------------------

    def _change_model_size(self, size: str) -> None:
        if config.MODEL_SIZE == size:
            return
        config.MODEL_SIZE = size
        _patch_config_file("MODEL_SIZE", size)
        self.model = None
        if self.icon:
            self.icon.menu = self._build_menu()
        self.load_model()
        if self.icon:
            self.icon.menu = self._build_menu()

    def _change_beam_size(self, beam: int) -> None:
        config.BEAM_SIZE = beam
        _patch_config_file("BEAM_SIZE", beam)
        print(f"[WhisperVoice] Precyzja transkrypcji: beam_size={beam}")
        if self.icon:
            self.icon.menu = self._build_menu()

    def _change_language(self, lang) -> None:
        config.LANGUAGE = lang
        _patch_config_file("LANGUAGE", lang)
        label = lang if lang else "auto"
        print(f"[WhisperVoice] Jezyk: {label}")
        if self.icon:
            self.icon.menu = self._build_menu()

    def _change_icon_style(self, style: str) -> None:
        """Zmienia styl ikony trayu - bez restartu."""
        config.ICON_STYLE = style
        _patch_config_file("ICON_STYLE", style)
        print(f"[WhisperVoice] Styl ikony: {style}")
        current_color = (
            config.COLOR_RECORD   if self._recording
            else config.COLOR_IDLE if self.model
            else config.COLOR_LOADING
        )
        self._set_icon(current_color)
        if self.icon:
            self.icon.menu = self._build_menu()

    def _toggle_sound_feedback(self) -> None:
        """Wlacza/wylacza dzwieki potwierdzenia."""
        config.SOUND_FEEDBACK = not getattr(config, "SOUND_FEEDBACK", True)
        _patch_config_file("SOUND_FEEDBACK", config.SOUND_FEEDBACK)
        state = "wlaczone" if config.SOUND_FEEDBACK else "wylaczone"
        print(f"[WhisperVoice] Dzwieki potwierdzenia: {state}")
        if config.SOUND_FEEDBACK:
            _play_beep("SystemAsterisk")
        if self.icon:
            self.icon.menu = self._build_menu()

    def _toggle_polite_forms(self) -> None:
        """Wlacza/wylacza kapitalizacje zwrotow grzecznosciowych."""
        config.POLITE_FORMS_ENABLED = not getattr(config, "POLITE_FORMS_ENABLED", True)
        _patch_config_file("POLITE_FORMS_ENABLED", config.POLITE_FORMS_ENABLED)
        state = "wlaczone" if config.POLITE_FORMS_ENABLED else "wylaczone"
        print(f"[WhisperVoice] Zwroty grzecznosciowe: {state}")
        if self.icon:
            self.icon.menu = self._build_menu()

    # -- Hotkey ----------------------------------------------------------

    @staticmethod
    def _validate_hotkey(candidate: str) -> tuple[bool, str]:
        candidate_lower = (candidate or "").strip().lower()
        is_bare_modifier = ("+" not in candidate_lower) and (candidate_lower in _MODIFIER_KEYS)
        try:
            if is_bare_modifier:
                h = keyboard.on_press_key(candidate_lower, lambda e: None, suppress=True)
                try:
                    keyboard.unhook(h)
                except Exception:
                    pass
            else:
                h = keyboard.add_hotkey(candidate, lambda: None, suppress=True)
                try:
                    keyboard.remove_hotkey(h)
                except Exception:
                    pass
        except Exception as exc:
            return False, str(exc)
        return True, ""

    def _change_hotkey(self, new_hotkey: str) -> None:
        if not new_hotkey:
            return
        new_hotkey = new_hotkey.strip().lower()
        if not new_hotkey:
            return

        if new_hotkey == (config.HOTKEY or "").strip().lower():
            return

        if new_hotkey == "esc" or new_hotkey == "escape":
            ctypes.windll.user32.MessageBoxW(
                0,
                "ESC jest zarezerwowany do anulowania - wybierz inny klawisz.",
                "WhisperVoice - niedozwolony klawisz",
                0x30,
            )
            return

        if new_hotkey in _BLOCKED_HOTKEYS:
            ctypes.windll.user32.MessageBoxW(
                0,
                "Klawisza Pause/Break nie mozna uzyc jako hotkey.\n\n"
                "Na Windows ten klawisz zglasza nacisniecie i puszczenie\n"
                "rownoczesnie - nagrywanie zatrzymywaloby sie natychmiast\n"
                "po starcie, wiec nic nie zostaloby nagrane.\n\n"
                "Wybierz np. Scroll Lock, Prawy Ctrl, F13 albo kombinacje\n"
                "z modyfikatorem (Ctrl/Alt/Shift + klawisz).",
                "WhisperVoice - niedozwolony klawisz",
                0x30,
            )
            return

        # Hotkey bez modyfikatora rejestrowany jest z suppress=True (patrz
        # _setup_hotkey) — klawisz piszący/nawigacyjny zostałby zablokowany
        # dla WSZYSTKICH aplikacji w systemie (np. litera "A" lub spacja).
        _hk_keys = [k.strip() for k in new_hotkey.split("+") if k.strip()]
        _has_mod = any(k in _MODIFIER_KEYS for k in _hk_keys)
        _DANGEROUS_BARE = {
            "space", "spacebar", "enter", "return", "tab", "backspace",
            "delete", "del", "insert", "left", "right", "up", "down",
            "home", "end", "page up", "page down",
        }
        if not _has_mod and any(
            len(k) == 1 or k in _DANGEROUS_BARE for k in _hk_keys
        ):
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Klawisza {new_hotkey.upper()} nie mozna uzyc jako hotkey.\n\n"
                "Pojedynczy klawisz piszacy lub nawigacyjny zostalby\n"
                "przechwycony GLOBALNIE i przestalby dzialac we wszystkich\n"
                "aplikacjach, dopoki WhisperVoice jest uruchomiony.\n\n"
                "Wybierz np. Scroll Lock, Prawy Ctrl, F13 albo kombinacje\n"
                "z modyfikatorem (Ctrl/Alt/Shift + klawisz).",
                "WhisperVoice - niedozwolony klawisz",
                0x30,
            )
            return

        ok, exc_msg = self._validate_hotkey(new_hotkey)
        if not ok:
            msg = (
                f"Tego klawisza ({new_hotkey.upper()}) nie mozna uzyc.\n\n"
                f"Szczegoly: {exc_msg}\n\n"
                "Wybierz inny - moze byc zarezerwowany przez Windows "
                "(np. Win+L) lub uzywany przez inna aplikacje."
            )
            ctypes.windll.user32.MessageBoxW(
                0, msg, "WhisperVoice - blad hotkey", 0x30,
            )
            return

        if self._recording:
            try:
                self.stop_recording()
            except Exception as exc:
                print(f"[WhisperVoice] stop_recording przed zmiana hotkey: {exc}")
            time.sleep(0.05)

        self._cleanup_hotkey_hooks()

        old_hotkey = config.HOTKEY
        config.HOTKEY = new_hotkey
        _patch_config_file("HOTKEY", new_hotkey)
        print(f"[WhisperVoice] Hotkey zmieniony: {old_hotkey!r} -> {new_hotkey!r}")

        self._setup_hotkey()

        if self.icon:
            self.icon.menu = self._build_menu()
        self._set_icon(
            config.COLOR_IDLE,
            tip=f"WhisperVoice - {config.HOTKEY.upper()} aby nagrac",
        )

    def _open_hotkey_capture_dialog(self) -> None:
        import tkinter as tk

        captured  = {"value": ""}
        cancelled = {"flag": False}

        root = tk.Tk()
        root.title("WhisperVoice - wlasny hotkey")
        root.resizable(False, False)

        W, H = 420, 180
        try:
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            x  = (sw - W) // 2
            y  = (sh - H) // 2
            root.geometry(f"{W}x{H}+{x}+{y}")
        except Exception:
            root.geometry(f"{W}x{H}")

        try:
            root.attributes("-topmost", True)
        except Exception:
            pass

        info = tk.Label(
            root,
            text=(
                "Nacisnij klawisz lub kombinacje, ktora chcesz uzywac "
                "jako hotkey.\nAplikacja sprawdzi, czy klawisz da sie "
                "zarejestrowac w systemie."
            ),
            wraplength=400,
            justify="left",
            anchor="w",
        )
        info.pack(padx=12, pady=(12, 6), fill="x")

        detected_var = tk.StringVar(value="Wykryty klawisz: <jeszcze nic>")
        detected = tk.Label(
            root,
            textvariable=detected_var,
            font=("Segoe UI", 10, "bold"),
        )
        detected.pack(padx=12, pady=(4, 8))

        btn_frame = tk.Frame(root)
        btn_frame.pack(side="bottom", pady=(0, 14))

        save_btn   = tk.Button(btn_frame, text="Zapisz", width=10, state="disabled")
        cancel_btn = tk.Button(btn_frame, text="Anuluj", width=10)
        save_btn.pack(side="left", padx=8)
        cancel_btn.pack(side="left", padx=8)

        def on_save():
            val = captured["value"]
            cancelled["flag"] = True
            try:
                root.destroy()
            except Exception:
                pass
            if val:
                _logged_thread(self._change_hotkey, "hotkey-change", val)

        def on_cancel():
            cancelled["flag"] = True
            try:
                root.destroy()
            except Exception:
                pass

        save_btn.config(command=on_save)
        cancel_btn.config(command=on_cancel)
        root.protocol("WM_DELETE_WINDOW", on_cancel)

        def apply_captured(value: str):
            if cancelled["flag"]:
                return
            value = (value or "").strip().lower()
            if not value:
                detected_var.set("Wykryty klawisz: <nic nie wykryto>")
                return
            captured["value"] = value
            detected_var.set(f"Wykryty klawisz: {value.upper()}")
            try:
                save_btn.config(state="normal")
            except Exception:
                pass

        def on_timeout():
            if cancelled["flag"] or captured["value"]:
                return
            detected_var.set(
                "Nie wykryto klawisza - zamknij i sprobuj ponownie."
            )

        def capture_worker():
            try:
                result = keyboard.read_hotkey(suppress=False)
            except Exception as exc:
                print(f"[WhisperVoice] capture_worker error: {exc}")
                result = ""
            try:
                root.after(0, lambda r=result: apply_captured(r))
            except Exception:
                pass

        threading.Thread(
            target=capture_worker, daemon=True, name="hotkey-capture",
        ).start()

        try:
            root.after(30000, on_timeout)
        except Exception:
            pass

        root.mainloop()

    # -- Start -----------------------------------------------------------

    def _show_tray_pin_hint(self) -> None:
        """
        Jednorazowa podpowiedz (balloon notification) jak przypiąc ikone
        do widocznego obszaru paska zadan. Sledzone przez flage
        'tray_pin_hint_shown' w config_user.json - nie powtarza sie.
        """
        shown = False
        try:
            if os.path.exists(_CONFIG_USER_FILE):
                with open(_CONFIG_USER_FILE, "r", encoding="utf-8") as f:
                    shown = json.load(f).get("tray_pin_hint_shown", False)
        except Exception:
            pass
        if shown:
            return

        time.sleep(1.2)
        try:
            if self.icon:
                self.icon.notify(
                    "Aby ikona byla zawsze widoczna:\n"
                    "Kliknij ^ na pasku -> przeciagnij ikone W na pasek.\n"
                    "Lub: Ustawienia Windows -> Pasek zadan -> Ikony w zasobniku.",
                    "WhisperVoice - wskazowka"
                )
        except Exception:
            pass

        try:
            _patch_config_file("tray_pin_hint_shown", True)
        except Exception:
            pass


    def run(self) -> None:
        print("=" * 60)
        print(f"  {config.APP_NAME} - lokalny voice-to-text (Whisper)")
        print("=" * 60)
        print(f"[WhisperVoice] Dane aplikacji: {_DATA_DIR}")

        _load_user_config()

        _logged_thread(self.load_model, "load-model")
        self._setup_hotkey()

        self.icon = pystray.Icon(
            config.APP_NAME,
            _draw_icon(config.COLOR_LOADING),
            f"{config.APP_NAME} - ladowanie modelu AI (prosze czekac)...",
            self._build_menu(),
        )

        threading.Thread(target=self._show_tray_pin_hint, daemon=True,
                         name="tray-pin-hint").start()

        print("[WhisperVoice] Ikona w trayu aktywna.")
        print(f"[WhisperVoice] Przytrzymaj {config.HOTKEY.upper()} aby nagrywa.")
        print(f"[WhisperVoice] Styl ikony: {getattr(config, 'ICON_STYLE', 'letter')}")
        self.icon.run()


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        if not _check_terms_accepted():
            print("[WhisperVoice] Warunki nie zostaly zaakceptowane. Zamykam.")
            sys.exit(0)

        app = WhisperVoice()
        app.run()

    except KeyboardInterrupt:
        print("\n[WhisperVoice] Przerwano przez uzytkownika.")

    except Exception:
        import traceback as _tb
        err = _tb.format_exc()
        print(f"\n[WhisperVoice] BLAD KRYTYCZNY:\n{err}")
        try:
            _err_log = os.path.join(_DATA_DIR, "error.log")
            with open(_err_log, "a", encoding="utf-8") as _f:
                _f.write(f"\n[{datetime.datetime.now()}] BLAD KRYTYCZNY:\n{err}")
            print(f"[WhisperVoice] Szczegoly w: {_err_log}")
        except Exception:
            pass
        _log(f"__main__ BLAD KRYTYCZNY, szczegoly w: {_LOG_EARLY}", level="ERROR")
        input("Nacisnij Enter aby zamknac...")
