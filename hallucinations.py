"""
WhisperVoice — filtr halucynacji modelu Whisper.

DLACZEGO TO ISTNIEJE
────────────────────
Whisper (zwłaszcza large-v3) był trenowany na ogromnej ilości materiałów z
YouTube wraz z napisami. Na fragmentach CISZY, oddechu lub cichego szumu model
zamiast napisać „nic" generuje najczęstsze frazy z danych treningowych — końcówki
filmów i podpisy napisów, np. „Napisy przygotowane przez…", „Wszystkie informacje
znajdziecie w opisie filmu", „Subskrybuj kanał", „Dziękuję za oglądanie". To nie
jest błąd nagrania — to halucynacja samego modelu. Klasyk faster-whisper / OpenAI
Whisper (patrz: liczne zgłoszenia „Amara.org", „napisy społeczności").

Ten moduł jest CZYSTY — zależy wyłącznie od `re`. Dzięki temu skrypt testowy
`dev-tools/test_hallucinations.py` importuje go bez ładowania faster-whisper,
sounddevice ani modelu (test odpala się w ułamku sekundy, offline).

DWA POZIOMY PEWNOŚCI
────────────────────
  • STRONG — frazy praktycznie nieobecne w prawdziwym dyktowaniu (napisy /
    subskrypcja / „w opisie filmu"). Można je wycinać nawet z KOŃCA realnej
    wypowiedzi.
  • WEAK — frazy, które MOGĄ paść naturalnie (np. „dziękuję za uwagę" w mailu).
    Usuwamy je tylko z dodatkowym sygnałem: albo cały tekst jest halucynacją,
    albo segment został akustycznie rozpoznany jako cisza (wysokie no_speech_prob
    — patrz `main._transcribe_and_inject`, Warstwa 2).

Filtr działa DWUWARSTWOWO razem z main.py:
  Warstwa 1 (tu, `filter_hallucinations`) — czyszczenie tekstu po sklejeniu.
  Warstwa 2 (main.py) — odrzucanie całych SEGMENTÓW o wysokim no_speech_prob,
            jeśli ich treść pasuje do `looks_like_hallucination`.
"""

import re

# ── Frazy „mocne" — YouTube-owe, nie występują w normalnym dyktowaniu ────────
_STRONG_PATTERNS = [re.compile(p, re.IGNORECASE) for p in (
    # „Napisy … przygotowane / stworzone / dostarczone / tłumaczone przez …"
    # (opcjonalna końcówka „…przez X" domyka pełny podpis, np. „przez społeczność Amara")
    r"napis(?:y|ów|ami)?\b[^.?!]{0,45}\b(?:przygotow\w*|stworz\w*|dostarcz\w*|"
    r"wykona\w*|zrobi\w*|opracow\w*|t[łl]umacz\w*|autorstw\w*)"
    r"(?:\s+przez\b[^.?!]{0,40})?",
    r"amara(?:\.?\s*org)?",                                # sygnatura „Amara.org" — klasyk halucynacji
    r"\bnapisy\s+dla\s+was\b",
    r"\bnapisy\s*[:\-]",                                   # „Napisy: Jan Kowalski"
    # „(Wszystkie) informacje … w opisie" / „w opisie filmu / kanału"
    r"\b(?:wszystkie\s+)?informacj\w*\b[^.?!]{0,45}\bw\s+opisie\b",
    r"\bw\s+opisie\s+(?:filmu|kana[łl]u|wideo|odcinka|nagrania|materia[łl]u)\b",
    r"\b(?:znajdzie\w*|znajd[źz]\w*|sprawd[źz]\w*|klik\w*)\b[^.?!]{0,30}\bw\s+opisie\b",
    r"\blink\w*\s+w\s+opisie\b",
    # Subskrypcja / reakcje
    r"\b(?:za)?subskrybuj\w*\b",
    r"\bsubskrypcj\w*\b",
    r"\bzostaw\s+(?:like'?a?|[łl]apk\w*|suba|suba)\b",
    r"\b[łl]apk\w*\s+w\s+g[óo]r[ęe]\b",
    r"\bkliknij\s+(?:w\s+)?(?:link|dzwonek)\b",
    # Angielskie (Whisper potrafi halucynować po angielsku nawet przy LANGUAGE=pl)
    r"\bthanks?\s+for\s+watching\b",
    r"\b(?:please\s+|don'?t\s+forget\s+to\s+)?subscribe\b",
    r"\bsubtitles?\s+by\b",
    r"\bcaptions?\s+by\b",
    r"\bsee\s+you\s+(?:next\s+time|in\s+the\s+next)\b",
)]

# ── Frazy „słabe" — bywają naturalne; usuwamy tylko z dodatkowym sygnałem ─────
_WEAK_PATTERNS = [re.compile(p, re.IGNORECASE) for p in (
    r"\bdzięk\w*\s+(?:za\s+)?(?:ogl[ąa]dani\w*|obejrzeni\w*|uwag\w*)\b",
    r"\bdzięki\s+za\s+ogl[ąa]dani\w*",
    r"\bdo\s+zobaczeni\w*\b[^.?!]{0,25}(?:nast[ęe]pn\w*|kolejn\w*|razem|odcinku)\b",
    r"\bdo\s+nast[ęe]pnego\b",
    r"\bmi[łl]ego\s+dnia\b",
    r"\bdobrego\s+dnia\b",
    r"\bzapraszam\s+(?:do\s+)?(?:subskryb\w*|ogl[ąa]dani\w*|obejrzeni\w*)\b",
    r"\bwitaj\w*\s+w\s+(?:kolejn\w*|nast[ęe]pn\w*)\b",
    r"\bgoodbye\b",
    r"\bgood\s+night\b",
)]

# Wszystko, co nie jest literą/cyfrą (z polskimi znakami) — do liczenia „realnej treści".
_NON_ALNUM = re.compile(r"[^0-9A-Za-ząćęłńóśźżĄĆĘŁŃÓŚŹŻ]+")


def _any(patterns, text: str) -> bool:
    return any(p.search(text) for p in patterns)


def looks_like_hallucination(text: str, strong_only: bool = False) -> bool:
    """
    Czy fragment pasuje do znanego wzorca halucynacji Whispera.

    strong_only=True → sprawdza tylko frazy „mocne" (bezpieczne do wycięcia
    nawet z prawdziwej wypowiedzi).
    """
    if not text:
        return False
    if _any(_STRONG_PATTERNS, text):
        return True
    if not strong_only and _any(_WEAK_PATTERNS, text):
        return True
    return False


def _merged_spans(text: str, patterns) -> list[tuple[int, int]]:
    """Scala zachodzące na siebie dopasowania w rozłączne przedziały (posortowane)."""
    spans: list[tuple[int, int]] = []
    for p in patterns:
        for m in p.finditer(text):
            if m.end() > m.start():
                spans.append((m.start(), m.end()))
    if not spans:
        return []
    spans.sort()
    merged = [spans[0]]
    for s, e in spans[1:]:
        cs, ce = merged[-1]
        if s <= ce:
            merged[-1] = (cs, max(ce, e))
        else:
            merged.append((s, e))
    return merged


def _remove_spans(text: str, spans) -> str:
    if not spans:
        return text
    out, prev = [], 0
    for s, e in spans:
        out.append(text[prev:s])
        prev = e
    out.append(text[prev:])
    return "".join(out)


def filter_hallucinations(text: str) -> str:
    """
    WARSTWA 1 — czyści sklejoną transkrypcję z halucynacji.

    Kroki:
      1) Jeśli CAŁY (krótki) tekst to praktycznie sama halucynacja → zwraca ""
         (typowo: nagrano ciszę / przypadkowe muśnięcie hotkeya).
      2) Wycina „mocną" halucynację DOKLEJONĄ NA KOŃCU realnej wypowiedzi,
         o ile przed nią zostaje sensowna treść.

    Nie modyfikuje środka prawdziwej wypowiedzi. Frazy „słabe" wycina wyłącznie
    w kroku 1 (całość-halucynacja), nigdy z ogona (bo mogą być naturalne).
    """
    if not text:
        return text
    text = text.strip()
    if not text:
        return ""

    # ── Krok 1: cały (krótki) tekst = halucynacja ────────────────────────────
    if len(text) <= 160 and looks_like_hallucination(text):
        merged = _merged_spans(text, _STRONG_PATTERNS + _WEAK_PATTERNS)
        covered = sum(e - s for s, e in merged)
        frac = covered / max(len(text), 1)
        uncovered_alnum = len(_NON_ALNUM.sub("", _remove_spans(text, merged)))
        # Zeruj gdy halucynacja pokrywa większość tekstu LUB poza nią zostają
        # jedynie krótkie wypełniacze (np. „mój kanał", „i tyle").
        if frac >= 0.65 or uncovered_alnum <= 6:
            return ""

    # ── Krok 2: „mocna" halucynacja doklejona na końcu ───────────────────────
    starts = []
    for p in _STRONG_PATTERNS:
        m = p.search(text)
        if m:
            starts.append(m.start())
    if starts:
        cut_at = min(starts)
        before = text[:cut_at].strip()
        if len(_NON_ALNUM.sub("", before)) >= 4:   # przed halucynacją jest realna treść
            return before.rstrip(" ,.!?;:—-––—")

    return text
