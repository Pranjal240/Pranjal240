#!/usr/bin/env python3
"""Generate neofetch-style animated info card SVGs (dark + light)."""
from pathlib import Path
import html as H

ROOT = Path(__file__).resolve().parent.parent

TITLE = "pranjal240@github"
SEP = "─" * 30

ITEMS = [
    ("sep",),
    ("Name", "Pranjal Mishra"),
    ("Role", "Full-Stack Dev | IoT Enthusiast"),
    ("Origin", "India"),
    ("Education", "ECE Student"),
    ("Status", "Building & Innovating"),
    ("sep",),
    ("Languages", "C++ · JS · TS · Python · PHP"),
    ("Frontend", "React · Angular · Next.js"),
    ("Backend", "Node.js · Express · FastAPI"),
    ("Database", "MongoDB · Firebase"),
    ("Cloud", "AWS · Azure · GCP · Vercel"),
    ("AI/ML", "TensorFlow"),
    ("sep",),
    ("Email", "pranjalwork2602@gmail.com"),
    ("LinkedIn", "pranjal-mishra-3a7256291"),
    ("Instagram", "pranjal.__.mishra"),
]

PALETTE = ["#A78BFA", "#7C3AED", "#22D3EE", "#0891B2", "#10B981", "#059669", "#F97316", "#EF4444"]


def render(bg, chrome_bg, title_clr, key_clr, val_clr, sep_clr, label_clr, filename):
    w = 520
    lh = 20
    fs = 13
    px = 24
    chrome_h = 34
    dur = 2.0

    n_lines = 1 + len(ITEMS) + 2
    h = chrome_h + n_lines * lh + 50

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">']
    p.append("<style>")
    p.append(f'.t{{font-family:"Courier New",monospace;font-size:{fs}px;opacity:0}}')
    total = 1 + len(ITEMS) + 1
    for i in range(total):
        d = (i / total) * dur
        p.append(f".l{i}{{animation:fi .06s {d:.3f}s forwards}}")
    p.append("@keyframes fi{to{opacity:1}}")
    p.append("</style>")

    # frame
    p.append(f'<rect width="{w}" height="{h}" fill="{bg}" rx="8"/>')
    p.append(f'<rect width="{w}" height="{chrome_h}" fill="{chrome_bg}" rx="8"/>')
    p.append(f'<rect y="{chrome_h - 8}" width="{w}" height="8" fill="{chrome_bg}"/>')
    for i, c in enumerate(["#FF5F57", "#FFBD2E", "#27C93F"]):
        p.append(f'<circle cx="{18 + i * 20}" cy="{chrome_h // 2}" r="5" fill="{c}"/>')
    p.append(f'<text x="{w // 2}" y="{chrome_h // 2 + 4}" text-anchor="middle"'
             f' font-family="Courier New,monospace" font-size="11" fill="{label_clr}"'
             f' opacity="0.7">pranjal@github ~ $ neofetch</text>')

    y = chrome_h + 28
    idx = 0
    val_x = px + 135

    # title
    p.append(f'<text x="{px}" y="{y}" class="t l{idx}" fill="{title_clr}"'
             f' font-weight="bold">{TITLE}</text>')
    idx += 1
    y += lh

    for item in ITEMS:
        if item[0] == "sep":
            p.append(f'<text x="{px}" y="{y}" class="t l{idx}" fill="{sep_clr}">{SEP}</text>')
        else:
            key, val = item
            ek = H.escape(key + ":")
            ev = H.escape(val)
            p.append(f'<text y="{y}" class="t l{idx}">'
                     f'<tspan x="{px}" fill="{key_clr}">{ek}</tspan>'
                     f'<tspan x="{val_x}" fill="{val_clr}">{ev}</tspan>'
                     f'</text>')
        idx += 1
        y += lh

    # color palette
    y += 10
    for i, c in enumerate(PALETTE):
        bx = px + i * 28
        p.append(f'<rect x="{bx}" y="{y - 12}" width="20" height="20" rx="3"'
                 f' fill="{c}" class="t l{idx}"/>')
    idx += 1

    p.append("</svg>")
    out = ROOT / filename
    out.write_text("\n".join(p))
    print(f"Generated: {out}")


def main():
    render("#0D1117", "#161B22", "#A78BFA", "#22D3EE", "#CBD5E1", "#30363D",
           "#8B949E", "info-card-dark.svg")
    render("#FFFFFF", "#F6F8FA", "#7C3AED", "#0891B2", "#374151", "#D1D5DB",
           "#6B7280", "info-card-light.svg")


if __name__ == "__main__":
    main()
