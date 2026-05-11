"""
Retreat Ben's portrait into the FitWeb brand:
  - Editorial monochrome duotone (warm Ink -> warm Chalk)
  - Background normalised to deep ink (kills the original blue cast)
  - Chest logo suppressed (faded into shirt-dark)
  - Subtle film grain to match brand atmosphere
"""

from PIL import Image, ImageFilter
import numpy as np
from pathlib import Path

SRC = Path('/Users/Ben/Desktop/ben-mann-portrait.png')
OUT_DIR = Path('/Users/Ben/Desktop/fitweb-site/assets')
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Slightly warm versions of the brand neutrals — keeps the skin reading human
INK   = np.array([0x12, 0x11, 0x0E]) / 255.0
CHALK = np.array([0xF4, 0xF0, 0xE6]) / 255.0

src = Image.open(SRC).convert('RGB')
print(f"Source: {src.size}")

arr = np.array(src).astype(np.float32) / 255.0
R, G, B = arr[..., 0], arr[..., 1], arr[..., 2]
L = 0.2126 * R + 0.7152 * G + 0.0722 * B

# ── 1. tonal adjustment ─────────────────────────────────────────────────
# lift shadows slightly, gentle midtone gamma, keep highlight rolloff
L2 = np.clip((L - 0.05) / 0.88, 0, 1)
L2 = np.power(L2, 0.93)

# ── 2. duotone (warm ink -> warm chalk) ─────────────────────────────────
duo = INK + (CHALK - INK) * L2[..., None]

# ── 3. force deep shadows to pure ink (kills any colour residue) ────────
deep = L2 < 0.06
duo[deep] = INK

# ── 4. suppress the chest logo ──────────────────────────────────────────
# Auto-locate the logo by finding the bright green-dominant blob
# in the lower half of the frame.
H, W = arr.shape[:2]
y_grad = np.linspace(0, 1, H)[:, None]
in_lower = (y_grad > 0.70).astype(np.float32)
# threshold tuned to the actual logo brightness/saturation in this shot
green_hot = ((G > R * 1.20) & (G > B * 1.60) & (L > 0.40)).astype(np.float32)
hot = green_hot * in_lower

ys_idx, xs_idx = np.where(hot > 0.5)

if len(ys_idx) >= 100:
    cy_px = ys_idx.mean()
    cx_px = xs_idx.mean()
    half_h = (ys_idx.max() - ys_idx.min()) / 2
    half_w = (xs_idx.max() - xs_idx.min()) / 2
    span_y = (ys_idx.max() - ys_idx.min()) / H
    span_x = (xs_idx.max() - xs_idx.min()) / W
    if span_y < 0.12 and span_x < 0.12:
        cx, cy = cx_px / W, cy_px / H
        rx = max((half_w / W) * 2.6, 0.110)
        ry = max((half_h / H) * 2.6, 0.090)
        print(f"Logo auto-detected at ({cx:.3f}, {cy:.3f}), radius ({rx:.3f}, {ry:.3f})")
    else:
        cx, cy, rx, ry = 0.700, 0.810, 0.080, 0.062
        print(f"Auto-detect spread too wide; using known coords")
else:
    cx, cy, rx, ry = 0.700, 0.810, 0.080, 0.062
    print(f"Logo not detected; using known coords")

xs = np.linspace(0, 1, W)[None, :]
ys = np.linspace(0, 1, H)[:, None]
ellipse = ((xs - cx) / rx) ** 2 + ((ys - cy) / ry) ** 2
logo_mask = np.clip(1.5 - ellipse, 0, 1).astype(np.float32)

# soft blur the edges
lm = Image.fromarray((logo_mask * 255).astype(np.uint8), 'L')
lm = lm.filter(ImageFilter.GaussianBlur(radius=24))
logo_mask = np.array(lm).astype(np.float32) / 255.0

# paint with shirt-ink
SHIRT = np.array([0x09, 0x09, 0x09]) / 255.0
duo = duo * (1 - logo_mask[..., None]) + SHIRT * logo_mask[..., None]

# ── 5. resize to web target ─────────────────────────────────────────────
out_img = Image.fromarray(np.clip(duo * 255, 0, 255).astype(np.uint8), 'RGB')
target_w = 1400
out_img = out_img.resize((target_w, int(out_img.height * target_w / out_img.width)), Image.LANCZOS)

# ── 6. subtle film grain ────────────────────────────────────────────────
np.random.seed(7)
grain = np.random.normal(0, 4.5, out_img.size[::-1] + (3,))
final = np.clip(np.array(out_img).astype(np.float32) + grain, 0, 255).astype(np.uint8)
out_img = Image.fromarray(final, 'RGB')

# ── 7. gentle sharpen ───────────────────────────────────────────────────
out_img = out_img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=70, threshold=2))

out_jpg = OUT_DIR / 'founder.jpg'
out_img.save(out_jpg, 'JPEG', quality=88, optimize=True, progressive=True)
print(f"Wrote: {out_jpg} ({out_jpg.stat().st_size // 1024} KB)")
