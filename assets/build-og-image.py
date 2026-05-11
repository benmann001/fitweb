"""
Build the social-share / Open Graph image for FitWeb.

Output: assets/og-image.jpg, 1200x630, brand-correct.
Idempotent — safe to re-run after copy or palette changes.
"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent
FONTS = ROOT / '.fonts'
FONTS.mkdir(exist_ok=True)

# ── fetch Instrument Serif (regular + italic) from Google Fonts OFL ─────
FONT_URLS = {
    'InstrumentSerif-Regular.ttf':
        'https://github.com/google/fonts/raw/main/ofl/instrumentserif/InstrumentSerif-Regular.ttf',
    'InstrumentSerif-Italic.ttf':
        'https://github.com/google/fonts/raw/main/ofl/instrumentserif/InstrumentSerif-Italic.ttf',
}
for name, url in FONT_URLS.items():
    if not (FONTS / name).exists():
        print(f"Fetching {name} ...")
        urllib.request.urlretrieve(url, FONTS / name)

# ── palette ──────────────────────────────────────────────────────────────
INK     = (15, 15, 14)
CHALK   = (242, 241, 237)
STEEL   = (130, 134, 140)
SIGNAL  = (232, 255, 58)

# ── canvas ───────────────────────────────────────────────────────────────
W, H = 1200, 630
img = Image.new('RGB', (W, H), INK)

# subtle radial Signal glow at upper-right (matches the hero atmosphere)
yy, xx = np.meshgrid(np.arange(H), np.arange(W), indexing='ij')
glow = np.exp(-(((xx - W*0.85) ** 2 + (yy - H*0.25) ** 2) / (2 * (W*0.32) ** 2)))
arr = np.array(img).astype(np.float32) + glow[..., None] * 0.05 * np.array(SIGNAL)

# subtle film grain
np.random.seed(11)
arr += np.random.normal(0, 4.5, arr.shape)
arr = np.clip(arr, 0, 255).astype(np.uint8)
img = Image.fromarray(arr, 'RGB')

draw = ImageDraw.Draw(img)

# ── fonts ────────────────────────────────────────────────────────────────
serif_regular = ImageFont.truetype(str(FONTS / 'InstrumentSerif-Regular.ttf'), 112)
serif_italic  = ImageFont.truetype(str(FONTS / 'InstrumentSerif-Italic.ttf'),  112)

def system_sans(size):
    candidates = [
        '/System/Library/Fonts/HelveticaNeue.ttc',
        '/System/Library/Fonts/Helvetica.ttc',
        '/System/Library/Fonts/Supplemental/Helvetica.ttc',
        '/Library/Fonts/Arial.ttf',
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

mono_eyebrow = system_sans(17)
brand_lg     = system_sans(32)
brand_sm     = system_sans(15)

# ── eyebrow (top-left) ───────────────────────────────────────────────────
EYEBROW = 'EST. 2018  —  FITNESS WEB STUDIO  —  CHRISTCHURCH, AOTEAROA'
draw.text((60, 60), EYEBROW, fill=STEEL, font=mono_eyebrow)

# ── headline: editorial three-line stack ────────────────────────────────
# "Websites for the / fitness brands / that mean it."  (last line italic, signal underline)
LX = 60
LY = 175
LH = 108  # tight line-height

draw.text((LX, LY),         'Websites for the', fill=CHALK, font=serif_regular)
draw.text((LX, LY + LH),    'fitness brands',   fill=CHALK, font=serif_regular)

# italic last line with a thin signal-yellow highlighter at the baseline.
# Use the font's actual ascent metric so the geometry doesn't drift.
italic_text = 'that mean it.'
ix = LX
iy = LY + 2 * LH
italic_bbox = draw.textbbox((ix, iy), italic_text, font=serif_italic)

ascent, _descent = serif_italic.getmetrics()
baseline_y = iy + ascent

# Thin ribbon (12px) sitting mostly below the baseline,
# clipping ~3px into the letter feet for a marker-stroke feel.
strike_top = baseline_y - 3
strike_bot = baseline_y + 9
draw.rectangle(
    [italic_bbox[0] + 4, strike_top, italic_bbox[2] + 8, strike_bot],
    fill=SIGNAL,
)
draw.text((ix, iy), italic_text, fill=CHALK, font=serif_italic)

# ── footer: clean wordmark + url, bottom-left ──────────────────────────
fy = H - 90
draw.text((60, fy), 'fitweb', fill=CHALK, font=brand_lg)
draw.text((60, fy + 44), 'fitweb.co.nz', fill=STEEL, font=brand_sm)

# ── footer: small signal tick + nav cue, bottom-right ──────────────────
nav_text = 'PORTFOLIO  ·  PACKAGES  ·  CONTACT'
nav_w = draw.textlength(nav_text, font=mono_eyebrow)
nav_x = W - 60 - nav_w
draw.text((nav_x, fy + 12), nav_text, fill=STEEL, font=mono_eyebrow)
# signal tick to the LEFT of the nav text
tick_w = 16
draw.rectangle([nav_x - tick_w - 14, fy + 18, nav_x - 14, fy + 20], fill=SIGNAL)

# ── save ────────────────────────────────────────────────────────────────
out = ROOT / 'og-image.jpg'
img.save(out, 'JPEG', quality=90, optimize=True, progressive=True)
print(f"Wrote {out} ({out.stat().st_size // 1024} KB)")
