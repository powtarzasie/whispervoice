"""
make_icon.py — generator pliku whispervoice.ico (narzędzie deweloperskie).

Tworzy ikonę aplikacji w jednym, spójnym wyglądzie używanym JEDNOCZEŚNIE przez:
  • instalator (ikona pliku Setup.exe),
  • skróty po instalacji (Menu Start / pulpit / autostart),
  • ikonę w zasobniku systemowym (tray) — stan IDLE.

Wygląd (litera "W" na niebieskim kole) jest identyczny jak ikona trayu rysowana
w main.py (_draw_icon, ICON_STYLE="letter", kolor COLOR_IDLE). Aby zachować
jedno źródło prawdy, kolor pobierany jest z config.COLOR_IDLE.

Użycie:  python make_icon.py
Wymaga:  Pillow (już w requirements.txt).
"""
import os
from PIL import Image, ImageDraw

try:
    import config
    COLOR_IDLE = tuple(config.COLOR_IDLE)
except Exception:
    COLOR_IDLE = (30, 91, 191)  # fallback — zgodny z config.py

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whispervoice.ico")


def draw_w(size: int) -> Image.Image:
    """Rysuje literę W na kole — geometria jak w main._draw_icon, skalowana do 'size'."""
    s = size / 64.0
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r, g, b = COLOR_IDLE
    d.ellipse([0, 0, size - 1, size - 1], fill=(r, g, b, 255))
    w = (255, 255, 255, 230)
    width = max(2, round(5 * s))
    pts = [
        [(13, 12), (22, 48)],
        [(22, 48), (32, 28)],
        [(32, 28), (42, 48)],
        [(42, 48), (51, 12)],
    ]
    for (x1, y1), (x2, y2) in pts:
        d.line([x1 * s, y1 * s, x2 * s, y2 * s], fill=w, width=width)
    return img


def main():
    sizes = [256, 128, 64, 48, 32, 24, 16]
    base = draw_w(256)
    imgs = [base] + [draw_w(sz) for sz in sizes if sz != 256]
    # Pillow zapisuje wielorozmiarowe ICO na podstawie listy 'sizes'
    base.save(OUT, format="ICO", sizes=[(sz, sz) for sz in sizes])
    print(f"[make_icon] Zapisano: {OUT}")
    print(f"[make_icon] Rozmiary: {sizes} | kolor IDLE: {COLOR_IDLE}")


if __name__ == "__main__":
    main()
