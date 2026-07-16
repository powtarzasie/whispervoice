# NOTICE — WhisperVoice v3.4

WhisperVoice
Copyright (c) 2026 Mariusz Świerguła
Licencja: MIT (zobacz plik `LICENSE`)

---

Ten produkt zawiera oraz pobiera oprogramowanie firm trzecich. Poniżej skrócone
noty atrybucyjne. Pełny wykaz wersji, licencji i źródeł znajduje się w plikach
`THIRD_PARTY_LICENSES.md` oraz `DEPENDENCIES_AND_LICENSES_v3.0.md`.

## Atrybucje

- **Python** — Copyright (c) Python Software Foundation. Licencja PSF-2.0.
- **faster-whisper** — Copyright (c) SYSTRAN. Licencja MIT.
- **CTranslate2** — Copyright (c) OpenNMT / SYSTRAN. Licencja MIT.
- **sounddevice** — Copyright (c) Matthias Geier. Licencja MIT.
- **PortAudio** — Copyright (c) Ross Bencina, Phil Burk. Licencja MIT.
- **numpy** — Copyright (c) NumPy Developers. Licencja BSD-3-Clause.
- **keyboard** — Copyright (c) BoppreH. Licencja MIT. (globalny hotkey oraz
  wysyłanie CTRL+V / typowanie tekstu).
- **pystray** — Copyright (c) Moses Palmér. Licencja LGPL-3.0-only.
- **Pillow** — Copyright (c) Jeffrey A. Clark i kontrybutorzy. Licencja HPND.
- **pyperclip** — Copyright (c) Al Sweigart. Licencja BSD-3-Clause.
- **Whisper large-v3 (wagi modelu)** — Copyright (c) OpenAI. Licencja MIT.

### Zależności pośrednie (pobierane automatycznie przez pip wraz z faster-whisper)

- **huggingface-hub** — Copyright (c) Hugging Face. Licencja Apache-2.0.
- **tokenizers** — Copyright (c) Hugging Face. Licencja Apache-2.0.
- **onnxruntime** — Copyright (c) Microsoft. Licencja MIT.
- **tqdm** — Copyright (c) tqdm developers. Licencja MPL-2.0 oraz MIT.
- **PyAV (`av`)** — Copyright (c) PyAV authors. Licencja BSD-3-Clause.
  Koła (wheels) PyAV z PyPI **zawierają biblioteki FFmpeg** (libavcodec,
  libavformat, libavutil, libswresample i in.).
- **FFmpeg** (wbudowany w koła PyAV) — Copyright (c) FFmpeg authors.
  Licencja **LGPL-2.1-or-later** (kompilacja LGPL używana przez PyAV).
  Dostarczany jako osobny, wymienialny pakiet pip — nie jest statycznie
  wkompilowany w kod WhisperVoice, więc warunki LGPL są spełnione.

## Komponenty opcjonalne (GPU NVIDIA)

- **nvidia-cublas-cu12** — Copyright (c) NVIDIA Corporation.
  NVIDIA Software License Agreement. Instalowany wyłącznie opcjonalnie,
  przy wykrytej karcie NVIDIA i za zgodą użytkownika.

## Uwagi

- WhisperVoice nie modyfikuje powyższych komponentów — używa ich jako
  bibliotek. Komponenty na licencjach copyleft (pystray — LGPL-3.0; FFmpeg
  wewnątrz PyAV — LGPL-2.1) są instalowane jako osobne, wymienialne pakiety pip,
  co spełnia warunki LGPL (możliwość podmiany/aktualizacji biblioteki).
- WhisperVoice **nie** zawiera biblioteki `pyautogui`. Do wklejania (CTRL+V)
  i typowania tekstu używa biblioteki `keyboard` (MIT). Dzięki temu projekt nie
  pobiera zależności `pyautogui → mouseinfo`, która jest na licencji **GPLv3**
  (silny copyleft, niezgodny z permisywną dystrybucją MIT).
- WhisperVoice **nie** instaluje ani **nie** aktualizuje sterowników NVIDIA
  ani oprogramowania NVIDIA GeForce Experience.
- Sama aplikacja nie zbiera, nie przesyła ani nie przechowuje danych osobowych.
