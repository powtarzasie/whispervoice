# WhisperVoice v3.4 — Rozwiązywanie problemów

Najpierw sprawdź log diagnostyczny:

```
%APPDATA%\WhisperVoice\error.log
%APPDATA%\WhisperVoice\install.log
```

(Wklej `%APPDATA%\WhisperVoice` w pasku adresu Eksploratora plików.)

---

## Instalacja

### Windows pokazuje „Nieznany wydawca” / SmartScreen blokuje plik
Plik instalatora nie jest podpisany certyfikatem Code Signing — to normalne dla
darmowego oprogramowania. Kliknij **Więcej informacji → Uruchom mimo to**.

### „Nie udało się pobrać Pythona”
- Sprawdź połączenie z internetem.
- Firewall/proxy/antywirus może blokować pobieranie z `python.org` — dodaj
  wyjątek lub pobierz Python ręcznie z <https://www.python.org/downloads/>
  (zaznacz **Add Python to PATH**) i uruchom instalator ponownie.

### „Pobrany plik Pythona jest uszkodzony (niezgodna suma kontrolna MD5)”
Pobieranie zostało przerwane lub plik został zmodyfikowany. Uruchom instalator
ponownie — pobierze plik od nowa. Instalator celowo **nie uruchomi** pliku
o niezgodnej sumie kontrolnej.

### „Instalacja bibliotek Python nie powiodła się”
Najczęstsze przyczyny: brak internetu (PyPI), blokada firewall/proxy/antywirus,
brak miejsca na dysku. Szczegóły w `%APPDATA%\WhisperVoice\install.log`.
Po naprawieniu przyczyny uruchom instalator ponownie lub `install.bat`
z folderu aplikacji.

### Instalacja kończy się błędem mimo „prawie gotowe”
To zamierzone: instalator **nie kończy się sukcesem**, jeśli zależności nie
zainstalowały się poprawnie. Zajrzyj do `install.log`, usuń przyczynę i powtórz.

---

## Uruchamianie aplikacji

### Aplikacja nie startuje / okno znika
Uruchom `run.bat` (tryb z konsolą) — zobaczysz komunikaty błędów. Sprawdź też
`error.log`.

### „BRAK PAKIETU …” / „BRAK WYMAGANEGO PAKIETU”
Biblioteki Python nie są zainstalowane. Uruchom `install.bat` z folderu aplikacji.

### „Nie znaleziono Pythona 3.10 lub nowszego”
Uruchom `fix_python_path.bat` z folderu aplikacji (dodaje Python do PATH),
albo zainstaluj Python z <https://www.python.org/downloads/> z opcją
**Add Python to PATH**.

### Ikona w trayu długo jest pomarańczowa
Przy pierwszym uruchomieniu pobierany jest model (~3 GB). Poczekaj — ikona
zmieni kolor na niebieski, gdy model będzie gotowy. **Nie zamykaj aplikacji**
w trakcie pobierania (restart = pobieranie od zera).

### Ikona trayu jest niewidoczna
Kliknij strzałkę **^** na pasku zadań i przeciągnij ikonę **W** na pasek,
albo: *Ustawienia Windows → Personalizacja → Pasek zadań → Ikony w zasobniku*.

---

## Transkrypcja

### Hotkey (Scroll Lock) nie działa
- Sprawdź, czy aplikacja jest uruchomiona (ikona w trayu).
- Niektóre aplikacje uruchomione „jako administrator” przechwytują klawisze —
  uruchom WhisperVoice z tymi samymi uprawnieniami lub zmień hotkey
  (prawy klik na ikonę → Hotkey).
- Zmień hotkey na inny preset, jeśli Scroll Lock koliduje z innym programem.

### Brak dźwięku / nie nagrywa
- Sprawdź, czy mikrofon jest podłączony i ustawiony jako domyślny w Windows.
- *Ustawienia Windows → Prywatność → Mikrofon* — zezwól aplikacjom na dostęp.

### Transkrypcja jest wolna
- Bez karty NVIDIA aplikacja działa na CPU (wolniej). Rozważ mniejszy model
  (menu trayu → Ustawienia → Jakość modelu: `medium` / `small`).
- Z kartą NVIDIA: upewnij się, że zainstalowano komponenty CUDA (opcja w
  instalatorze) i aktualne sterowniki NVIDIA.

### Polskie znaki / tekst trafia do złego okna
Domyślna metoda wklejania to schowek (Ctrl+V) — działa najlepiej z polskimi
znakami. Kliknij w pole docelowe tuż przed puszczeniem hotkey, aby fokus był
ustawiony poprawnie.

---

## Ścieżki ze spacjami i polskimi znakami
Aplikacja i instalator obsługują ścieżki ze spacjami (cudzysłowy w skryptach)
oraz katalog danych w `%APPDATA%`. Jeśli instalujesz w nietypowej lokalizacji
z polskimi znakami i napotkasz problem, zainstaluj w katalogu domyślnym.

---

## Gdzie szukać pomocy
Dołącz zawartość `error.log` i `install.log` przy zgłaszaniu problemu — zawierają
znaczniki czasu i etap, na którym wystąpił błąd. Logi nie zawierają treści
nagrań ani transkrypcji.
