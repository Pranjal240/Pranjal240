#!/usr/bin/env python3
"""Convert background-removed profile photo to animated ASCII portrait SVGs."""
from pathlib import Path
import html as H
import numpy as np
from PIL import Image
import cv2

ROOT = Path(__file__).resolve().parent.parent
RAMP = " .:-=+*#%@"


def prep_photo():
    img = Image.open(ROOT / "assets" / "profile-nobg.webp").convert("RGBA")
    r, g, b, a = img.split()
    gray = np.array(img.convert("L"))
    alpha = np.array(a)

    # CLAHE for better internal detail on the subject
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    detail = clahe.apply(gray)

    # transparent/white background → white (255), keep subject detail
    result = np.where(alpha > 128, detail, 255).astype(np.uint8)

    out = ROOT / "assets" / "prepped.png"
    Image.fromarray(result).save(out)
    print(f"Prepped: {out} ({result.shape[1]}x{result.shape[0]})")
    return out


def to_ascii(img_path, cols=70):
    img = Image.open(img_path).convert("L")
    w, h = img.size
    cw = w / cols
    rows = int(h / (cw * 2.0))
    small = np.array(img.resize((cols, rows)))

    lines = []
    for r in range(rows):
        row = ""
        for c in range(cols):
            v = int(small[r, c])
            if v > 220:
                row += " "
            else:
                idx = int((255 - v) / 255 * (len(RAMP) - 1))
                row += RAMP[max(0, min(len(RAMP) - 1, idx))]
        lines.append(row)

    # rows >85% spaces → fully blank
    cleaned = []
    for line in lines:
        pct = line.count(" ") / len(line) if line else 1
        cleaned.append(" " * len(line) if pct > 0.85 else line)

    # trim blank rows top/bottom
    while cleaned and cleaned[0].strip() == "":
        cleaned.pop(0)
    while cleaned and cleaned[-1].strip() == "":
        cleaned.pop()

    return cleaned


def render_svg(lines, bg, chrome_bg, fg, cursor_clr, label_clr, filename):
    fs = 7
    cw, ch = 4.2, 8.0
    pad = 12
    chrome_h = 34
    ncols = max(len(l) for l in lines)
    nrows = len(lines)
    sw = int(ncols * cw + pad * 2)
    sh = int(nrows * ch + pad * 2 + chrome_h + 14)
    dur = 2.5

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sw} {sh}" width="{sw}" height="{sh}">']
    p.append("<style>")
    p.append(f'.r{{font-family:"Courier New",monospace;font-size:{fs}px;fill:{fg};opacity:0;white-space:pre}}')
    for i in range(nrows):
        d = (i / nrows) * dur
        p.append(f".r{i}{{animation:a .04s {d:.3f}s forwards}}")
    p.append("@keyframes a{to{opacity:1}}")
    p.append(f".cur{{fill:{cursor_clr};opacity:0;animation:bk 1s step-end infinite {dur+.1:.1f}s}}")
    p.append("@keyframes bk{0%,100%{opacity:1}50%{opacity:0}}")
    p.append("</style>")

    p.append(f'<rect width="100%" height="100%" fill="{bg}" rx="8"/>')
    p.append(f'<rect width="{sw}" height="{chrome_h}" fill="{chrome_bg}" rx="8"/>')
    p.append(f'<rect y="{chrome_h - 8}" width="{sw}" height="8" fill="{chrome_bg}"/>')
    for i, c in enumerate(["#FF5F57", "#FFBD2E", "#27C93F"]):
        p.append(f'<circle cx="{18 + i * 20}" cy="{chrome_h // 2}" r="5" fill="{c}"/>')
    p.append(f'<text x="{sw // 2}" y="{chrome_h // 2 + 4}" text-anchor="middle"'
             f' font-family="Courier New,monospace" font-size="11" fill="{label_clr}"'
             f' opacity="0.7">portrait.txt</text>')

    cy0 = chrome_h + 8
    for i, line in enumerate(lines):
        y = cy0 + pad + (i + 1) * ch
        p.append(f'<text x="{pad}" y="{y:.1f}" class="r r{i}" xml:space="preserve">{H.escape(line)}</text>')

    cur_y = cy0 + pad + nrows * ch + 6
    p.append(f'<rect x="{pad}" y="{cur_y}" width="{cw * 1.2:.1f}" height="2" class="cur" rx="1"/>')
    p.append("</svg>")

    out = ROOT / filename
    out.write_text("\n".join(p))
    print(f"Generated: {out}")


def main():
    prepped = prep_photo()
    lines = to_ascii(prepped)
    print(f"ASCII: {len(lines)} rows x {max(len(l) for l in lines)} cols")
    render_svg(lines, "#0D1117", "#161B22", "#A78BFA", "#22D3EE", "#8B949E",
               "pranjal-ascii-dark.svg")
    render_svg(lines, "#F8FAFC", "#F0F0F0", "#5B21B6", "#0891B2", "#6B7280",
               "pranjal-ascii-light.svg")


if __name__ == "__main__":
    main()
