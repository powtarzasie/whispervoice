# ╔══════════════════════════════════════════════════════════════════╗
# ║            WHISPERVOICE v3.4 — KONFIGURACJA                     ║
# ║            build 15.07.2026                                      ║
# ╚══════════════════════════════════════════════════════════════════╝
#
# Edytuj ten plik, aby dopasować aplikację do swojego sprzętu.
# Po zmianach zrestartuj WhisperVoice.
#
# Profil docelowy:
#   • głównie nagrania 1–2 min, często 2–5 min
#   • rzadziej 5–10 min, okazjonalnie 10–29 min
#   • priorytet: maksymalna jakość polskiego, minimalizacja halucynacji
#
# ── SZYBKI WYBÓR PRESETU ────────────────────────────────────────────
#
#  Laptop  GTX 1660 Ti (6 GB VRAM):
#    MODEL_SIZE   = "large-v3"
#    DEVICE       = "cuda"
#    COMPUTE_TYPE = "int8_float16"   ← mniejsze zużycie VRAM, jakość ≈ float16
#
#  Desktop RTX 3080 / 4080 / 4090 (≥10 GB VRAM):
#    MODEL_SIZE   = "large-v3"
#    DEVICE       = "cuda"
#    COMPUTE_TYPE = "float16"        ← pełna precyzja, najlepsza jakość
#
#  Tylko CPU (bez GPU):
#    MODEL_SIZE   = "medium"
#    DEVICE       = "cpu"
#    COMPUTE_TYPE = "int8"
#
# ────────────────────────────────────────────────────────────────────


# ── MODEL ────────────────────────────────────────────────────────────
# Dostępne rozmiary: tiny | base | small | medium | large-v2 | large-v3
# large-v3 = najlepsza jakość dla polskiego, wymaga GPU z ≥4 GB VRAM
MODEL_SIZE = "large-v3"

# Urządzenie: "cuda" (karta NVIDIA) lub "cpu"
DEVICE = "cuda"

# Typ obliczeń:
#   "float16"      → najlepsza jakość, wymaga ≥8 GB VRAM
#   "int8_float16" → prawie taka sama jakość, ~40% mniej VRAM  ← GTX 1660 Ti
#   "int8"         → tylko CPU
COMPUTE_TYPE = "int8_float16"

# Wątki CPU (używane też gdy DEVICE = "cuda" do pre/post-processingu)
# 0 = auto (faster-whisper sam dobiera liczbę wątków)
CPU_THREADS = 0

# Liczba równoległych workerów — 1 = najstabilniej dla jednej transkrypcji naraz
NUM_WORKERS = 1


# ── JĘZYK ────────────────────────────────────────────────────────────
# "pl"  → wymusza polski, szybciej i mniej angielskich wstawek (zalecane)
# "en"  → angielski
# None  → automatyczne wykrywanie (wolniejsze, ryzyko angielskich wstawek)
LANGUAGE = "pl"

# Zawsze "transcribe" — nigdy "translate" (tłumaczyłoby na angielski)
TASK = "transcribe"

# False = wymuszamy jeden język, nie potrzebujemy multi-lingual trybu
MULTILINGUAL = False

# Używane tylko gdy LANGUAGE = None (awaryjne progi detekcji)
LANGUAGE_DETECTION_THRESHOLD = 0.65
LANGUAGE_DETECTION_SEGMENTS  = 3


# ── HOTKEY ───────────────────────────────────────────────────────────
# Trzymaj hotkey → nagrywanie. Puść → transkrypcja i wklejenie.
# Możliwe formaty: "ctrl+space", "right alt", "f13", "ctrl+shift+r"
HOTKEY = "scroll lock"


# ── AUDIO ────────────────────────────────────────────────────────────
SAMPLE_RATE  = 16000   # Hz — Whisper wymaga 16 kHz, nie zmieniaj
MIN_DURATION = 0.35    # sekundy — krótsze nagrania ignorowane (mniej śmieci)
BLOCK_SIZE   = 1024    # próbki — bufor audio (nie zmieniaj)

# Bufor przed/po hotkeyem — chroni początki i końce słów
# ⚠ PRE_ROLL_MS: NIEZAIMPLEMENTOWANE — zmiana tej wartości nie ma efektu (zarezerwowane na v2.1)
PRE_ROLL_MS  = 250     # ms bufora PRZED wciśnięciem hotkey — [NIEZAIMPLEMENTOWANE, nie zmieniaj]
POST_ROLL_MS = 200     # ms bufora PO puszczeniu hotkey — AKTYWNE (dodaje ciszę po zwolnieniu klawisza)

# Normalizacja audio — wyrównuje głośność nagrania
AUDIO_NORMALIZATION = True

# ⚠ NOISE_REDUCTION: NIEZAIMPLEMENTOWANE — zmiana tej wartości nie ma efektu (zarezerwowane na v2.1)
NOISE_REDUCTION = False   # [NIEZAIMPLEMENTOWANE, nie zmieniaj]


# ── TRANSKRYPCJA / JAKOŚĆ ────────────────────────────────────────────
#
# BEAM_SIZE — kompromis między szybkością a dokładnością:
#   5  → standard Whisper
#   8  → bardzo dobry sweet spot
#   10 → top quality (OK dla nagrań 1–5 min na GPU)
BEAM_SIZE = 8

# Dla każdego fragmentu audio próbuje BEST_OF losowych ścieżek przy T>0
BEST_OF  = 5

PATIENCE = 1.0

LENGTH_PENALTY = 1.0

# Kara za powtórzenia — przy naturalnej mowie zostaw 1.0
REPETITION_PENALTY    = 1.0
NO_REPEAT_NGRAM_SIZE  = 0

# Temperatura: 0.0 = deterministycznie; wyższe używane tylko ratunkowo gdy segment wygląda źle
TEMPERATURE = (0.0, 0.2, 0.4, 0.6)

COMPRESSION_RATIO_THRESHOLD = 2.4
LOG_PROB_THRESHOLD           = -1.0
NO_SPEECH_THRESHOLD          = 0.6

# Próg Warstwy 2 filtra halucynacji (main._transcribe_and_inject).
# Segment jest odrzucany TYLKO gdy jednocześnie:
#   (a) no_speech_prob >= NO_SPEECH_DROP_THRESHOLD  (akustycznie to raczej cisza)
#   (b) treść pasuje do wzorca outra/napisów (hallucinations.looks_like_hallucination)
# Oba warunki naraz chronią przed ucięciem prawdziwej, cichej mowy.
# Wyższa wartość = ostrożniej (rzadziej odrzuca). 1.0 praktycznie wyłącza Warstwę 2.
NO_SPEECH_DROP_THRESHOLD     = 0.6

# False = najlepsze dla dyktowania i krótkich/średnich nagrań
# True  = może poprawić spójność długich monologów (>10 min)
CONDITION_ON_PREVIOUS        = False
PROMPT_RESET_ON_TEMPERATURE  = 0.5

# None = bez limitu tokenów (bezpieczne przy długim initial_prompt)
MAX_NEW_TOKENS = None

# Whisper przetwarza okna ~30 s
CHUNK_LENGTH = 30


# ── TIMESTAMPY ───────────────────────────────────────────────────────
# Do dyktowania timestampy niepotrzebne — tylko spowalniają
WITHOUT_TIMESTAMPS              = True
WORD_TIMESTAMPS                 = False
MAX_INITIAL_TIMESTAMP           = 1.0
HALLUCINATION_SILENCE_THRESHOLD = None


# ── VAD — DETEKCJA MOWY / CISZY ──────────────────────────────────────
#
# Trzy zestawy parametrów VAD dopasowane do długości nagrania.
#
VAD_FILTER = True

# Profil VAD dla nagrań do 30 s
SHORT_VAD_PARAMETERS = {
    "threshold":                      0.42,
    "neg_threshold":                  None,
    "min_speech_duration_ms":         80,
    "max_speech_duration_s":          29.5,
    "min_silence_duration_ms":        600,
    "speech_pad_ms":                  500,
    "min_silence_at_max_speech":      98,
    "use_max_poss_sil_at_max_speech": True,
}

# Profil VAD dla nagrań 30 s – 10 min
DEFAULT_VAD_PARAMETERS = {
    "threshold":                      0.45,
    "neg_threshold":                  None,
    "min_speech_duration_ms":         120,
    "max_speech_duration_s":          29.5,
    "min_silence_duration_ms":        750,
    "speech_pad_ms":                  450,
    "min_silence_at_max_speech":      98,
    "use_max_poss_sil_at_max_speech": True,
}

# Alias dla kompatybilności wstecznej
VAD_PARAMETERS = DEFAULT_VAD_PARAMETERS

# Profil VAD dla nagrań 10–29 min
LONG_VAD_PARAMETERS = {
    "threshold":                      0.45,
    "neg_threshold":                  None,
    "min_speech_duration_ms":         120,
    "max_speech_duration_s":          29.5,
    "min_silence_duration_ms":        900,
    "speech_pad_ms":                  500,
    "min_silence_at_max_speech":      98,
    "use_max_poss_sil_at_max_speech": True,
}

# Profil VAD dla nagrań 30–90 s (przejście SHORT→DEFAULT)
SHORT_PLUS_VAD_PARAMETERS = {
    "threshold":                      0.43,
    "neg_threshold":                  None,
    "min_speech_duration_ms":         100,
    "max_speech_duration_s":          29.5,
    "min_silence_duration_ms":        650,
    "speech_pad_ms":                  470,
    "min_silence_at_max_speech":      98,
    "use_max_poss_sil_at_max_speech": True,
}

# Zachowany dla kompatybilności — VAD_PARAMETERS ma pierwszeństwo
VAD_MIN_SILENCE_MS = 750


# ── PROMPT STARTOWY ──────────────────────────────────────────────────
#
# Krótki, konkretny prompt domenowy.
# Nie używaj pangramów ani egzotycznych zdań — mogą biasować model.
# Możesz dopisać własne słowa kluczowe z Twojej dziedziny.
#
INITIAL_PROMPT_DEFAULT = (
    "To jest dokładna transkrypcja wypowiedzi w języku polskim. "
    "Nie tłumacz na język angielski. Zachowuj polskie znaki, naturalną interpunkcję "
    "i poprawną pisownię. Typowe słowa: że, się, już, też, więc, żeby, ponieważ, "
    "właściwie, później, również, będzie, można, trzeba, chciałbym, chciałabym. "
    "Wypowiedź może zawierać słowa techniczne, angielskie nazwy własne i skróty."
)

# Alias dla kompatybilności wstecznej
INITIAL_PROMPT = INITIAL_PROMPT_DEFAULT

# Krótki prompt dla nagrań do 30 s — nie biasuje modelu zbędnym kontekstem
INITIAL_PROMPT_SHORT = (
    "To jest krótka transkrypcja wypowiedzi w języku polskim. "
    "Nie tłumacz na angielski. Zachowaj polskie znaki i poprawną pisownię."
)


# ── HOTWORDS / SŁOWA KLUCZOWE ────────────────────────────────────────
#
# Słowa trudne do rozpoznania lub ważne domenowo.
# Optymalnie: 20–60 słów. Nie przesadzaj z długością.
#
HOTWORDS = (
    "WhisperVoice, Whisper, faster-whisper, OpenAI, ChatGPT, prompt, aplikacja, "
    "transkrypcja, dyktowanie, konfiguracja, model large-v3, "
    "trening, hipertrofia, redukcja, masa mięśniowa, kalorie, białko, minicut, "
    "feedback, klient, plan treningowy, dieta, regeneracja"
)


# ── INTERPUNKCJA / TOKENY ────────────────────────────────────────────
SUPPRESS_BLANK        = True
SUPPRESS_TOKENS       = [-1]
PREPEND_PUNCTUATIONS  = '\'"\u00bf([{-'
APPEND_PUNCTUATIONS   = '\'\".\u3002,\uff0c!\uff01?\uff1f:\uff1a)]}\u3001'


# ── PROFILE TRANSKRYPCJI ─────────────────────────────────────────────
#
# Trzy pełne profile — wybierane automatycznie na podstawie długości nagrania:
#   SHORT   → do 30 s     (krótki prompt, łagodniejszy VAD, wyższy próg ciszy)
#   DEFAULT → 30 s – 10 min (główny profil dyktowania)
#   LONG    → 10–29 min   (łagodniejszy VAD, beam_size jak DEFAULT)
#
TRANSCRIBE_PROFILE_SHORT = {
    "language":                     "pl",
    "task":                         "transcribe",

    "beam_size":                    10,
    "best_of":                      5,
    "patience":                     1.0,
    "length_penalty":               1.0,

    "repetition_penalty":           1.0,
    "no_repeat_ngram_size":         0,

    "temperature":                  (0.0, 0.2, 0.4),

    "compression_ratio_threshold":  2.4,
    "log_prob_threshold":           -1.0,
    "no_speech_threshold":          0.75,

    "condition_on_previous_text":   False,
    "prompt_reset_on_temperature":  0.5,

    "initial_prompt":               INITIAL_PROMPT_SHORT,
    "prefix":                       None,

    "suppress_blank":               True,
    "suppress_tokens":              [-1],

    "without_timestamps":           True,
    "word_timestamps":              False,

    "vad_filter":                   True,
    "vad_parameters":               SHORT_VAD_PARAMETERS,

    "max_new_tokens":               None,
    "chunk_length":                 30,
    "clip_timestamps":              None,

    "hallucination_silence_threshold": None,
    "hotwords":                     HOTWORDS,
}


TRANSCRIBE_PROFILE_SHORT_PLUS = {
    "language":                     "pl",
    "task":                         "transcribe",

    "beam_size":                    10,
    "best_of":                      5,
    "patience":                     1.0,
    "length_penalty":               1.0,

    "repetition_penalty":           1.0,
    "no_repeat_ngram_size":         0,

    "temperature":                  (0.0, 0.2, 0.4),

    "compression_ratio_threshold":  2.4,
    "log_prob_threshold":           -1.0,
    "no_speech_threshold":          0.55,

    "condition_on_previous_text":   False,
    "prompt_reset_on_temperature":  0.5,

    "initial_prompt":               INITIAL_PROMPT_DEFAULT,
    "prefix":                       None,

    "suppress_blank":               True,
    "suppress_tokens":              [-1],

    "without_timestamps":           True,
    "word_timestamps":              False,

    "vad_filter":                   True,
    "vad_parameters":               SHORT_PLUS_VAD_PARAMETERS,

    "max_new_tokens":               None,
    "chunk_length":                 30,
    "clip_timestamps":              None,

    "hallucination_silence_threshold": None,
    "hotwords":                     HOTWORDS,
}

TRANSCRIBE_PROFILE_DEFAULT = {
    "language":                     "pl",
    "task":                         "transcribe",

    "beam_size":                    8,
    "best_of":                      5,
    "patience":                     1.0,
    "length_penalty":               1.0,

    "repetition_penalty":           1.0,
    "no_repeat_ngram_size":         0,

    "temperature":                  (0.0, 0.2, 0.4),

    "compression_ratio_threshold":  2.4,
    "log_prob_threshold":           -1.0,
    "no_speech_threshold":          0.55,

    "condition_on_previous_text":   False,
    "prompt_reset_on_temperature":  0.5,

    "initial_prompt":               INITIAL_PROMPT_DEFAULT,
    "prefix":                       None,

    "suppress_blank":               True,
    "suppress_tokens":              [-1],

    "without_timestamps":           True,
    "word_timestamps":              False,

    "vad_filter":                   True,
    "vad_parameters":               DEFAULT_VAD_PARAMETERS,

    "max_new_tokens":               None,
    "chunk_length":                 30,
    "clip_timestamps":              None,

    "hallucination_silence_threshold": None,
    "hotwords":                     HOTWORDS,
}

TRANSCRIBE_PROFILE_LONG = {
    **TRANSCRIBE_PROFILE_DEFAULT,

    "vad_parameters":               LONG_VAD_PARAMETERS,

    # condition_on_previous_text pozostaje False — ogranicza ryzyko przenoszenia błędów
    "condition_on_previous_text":   False,
}

# Mapowanie do wyboru profilu w kodzie głównym
DURATION_PROFILES = {
    "SHORT":       TRANSCRIBE_PROFILE_SHORT,      # ≤ 30 s
    "SHORT_PLUS":  TRANSCRIBE_PROFILE_SHORT_PLUS, # 30–90 s
    "DEFAULT":     TRANSCRIBE_PROFILE_DEFAULT,    # 90 s – 10 min
    "LONG":        TRANSCRIBE_PROFILE_LONG,       # 10–29 min
}


# ── WKLEJANIE TEKSTU ─────────────────────────────────────────────────
# "clipboard" → CTRL+V (szybkie, działa wszędzie, zalecane)
# "typing"    → symulacja klawiatury (wolne, może nie działać z polskimi znakami)
INJECT_METHOD = "clipboard"
INJECT_DELAY  = 0.10   # sekundy przed wklejeniem (nie zmniejszaj poniżej 0.05)


# ── TRAY / WYGLĄD ────────────────────────────────────────────
APP_NAME = "WhisperVoice"

# Styl ikony w zasobniku systemowym:
#   "letter" → litera W w kole (zalecane — nie myli się z systemową ikoną mikrofonu)
#   "mic"    → mikrofon (styl z v1)
#   "wave"   → pasek equalizera (fale dźwiękowe)
ICON_STYLE = "letter"

# Dźwięki potwierdzenia przez winsound (wbudowane w Windows, zero dodatkowych zależności):
#   True  → krótki beep przy starcie nagrywania, stopie i gdy model jest gotowy
#   False → cisza
SOUND_FEEDBACK = True

# Kapitalizacja zwrotów grzecznościowych po transkrypcji:
#   True  → automatyczna wielka litera | False → tekst bez zmian
#
#   Objęte formy:
#     Pan/Pani/Państwo  →  Pan, Pana, Panu, Panem, Panie, Pani,
#                          Państwo, Państwa, Państwu, Państwem
#     Ty (os. l.poj.)   →  Ty, Cię, Ciebie, Ci, Tobie, Tobą
#     Twój (dz. l.poj.) →  Twój, Twoja, Twoje, Twojego, Twojej,
#                          Twojemu, Twoją, Twoim, Twoi, Twoich, Twoimi
#     Wy (os. l.mn.)    →  Wy, Was, Wam, Wami
#     Wasz (dz. l.mn.)  →  Wasz, Wasza, Wasze, Waszego, Waszej,
#                          Waszemu, Waszą, Waszym, Wasi, Waszych, Waszymi
POLITE_FORMS_ENABLED = True

# Kolory ikony trayu (RGB)
COLOR_IDLE    = (30,  91, 191)   # niebieski    — gotowy do nagrywania
COLOR_RECORD  = (200, 30,  30)   # czerwony     — nagrywa
COLOR_PROCESS = (107, 33, 168)   # fioletowy    — przetwarza
COLOR_LOADING = (200, 120,  0)   # pomarańczowy — ładowanie modelu
