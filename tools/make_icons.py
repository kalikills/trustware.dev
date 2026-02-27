from __future__ import annotations
from pathlib import Path
from PIL import Image

SITE_ROOT = Path(__file__).resolve().parents[1]
SRC = SITE_ROOT / "assets" / "logo" / "trustware-logo.png"
OUT = SITE_ROOT / "assets" / "icons"

SIZES = [512, 256, 180, 128, 64, 32, 16]

def trim_alpha(im: Image.Image) -> Image.Image:
    im = im.convert("RGBA")
    alpha = im.split()[-1]
    bbox = alpha.getbbox()
    if not bbox:
        return im
    return im.crop(bbox)

def to_square(im: Image.Image, pad=0) -> Image.Image:
    w, h = im.size
    side = max(w, h) + pad * 2
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    x = (side - w) // 2
    y = (side - h) // 2
    canvas.paste(im, (x, y), im)
    return canvas

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    im = Image.open(SRC)
    im = trim_alpha(im)
    im = to_square(im, pad=20)

    # PNG icons
    for s in SIZES:
        resized = im.resize((s, s), Image.LANCZOS)
        if s == 180:
            resized.save(OUT / "apple-touch-icon.png")
        else:
            resized.save(OUT / f"icon-{s}.png")

    # favicon.ico (multi-size)
    ico_sizes = [(16,16), (32,32), (48,48)]
    im_ico = im.resize((256,256), Image.LANCZOS)
    im_ico.save(OUT / "favicon.ico", sizes=ico_sizes)

    print("Wrote icons to:", OUT)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())