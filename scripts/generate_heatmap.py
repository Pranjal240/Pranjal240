#!/usr/bin/env python3
"""Fetch GitHub contributions and generate animated heatmap SVGs."""
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
USER = "Pranjal240"


def fetch():
    """Fetch contribution data from GitHub HTML page."""
    try:
        import requests
        from bs4 import BeautifulSoup
        resp = requests.get(f"https://github.com/users/{USER}/contributions", timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        days = []
        for td in soup.select("td.ContributionCalendar-day"):
            date = td.get("data-date")
            level = td.get("data-level", "0")
            if date:
                days.append({"date": date, "level": int(level)})
        if days:
            days.sort(key=lambda d: d["date"])
            DATA.parent.mkdir(exist_ok=True)
            DATA.write_text(json.dumps(days, indent=2))
            print(f"Fetched {len(days)} days")
            return days
    except Exception as e:
        print(f"Fetch failed: {e}")

    if DATA.exists():
        print("Using cached data")
        return json.loads(DATA.read_text())

    print("Generating sample data")
    days = []
    today = datetime.now()
    for i in range(365):
        d = today - timedelta(days=364 - i)
        lvl = random.choices([0, 1, 2, 3, 4], weights=[40, 25, 20, 10, 5])[0]
        days.append({"date": d.strftime("%Y-%m-%d"), "level": lvl})
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps(days, indent=2))
    return days


def github_dow(d):
    return (d.weekday() + 1) % 7


def render(days, bg, chrome_bg, colors, label_clr, filename):
    cell, gap = 11, 3
    step = cell + gap
    pl, pt = 50, 24
    chrome_h = 34

    date_lvl = {d["date"]: d["level"] for d in days}
    dates = sorted(date_lvl.keys())
    if not dates:
        return

    first = datetime.strptime(dates[0], "%Y-%m-%d")
    last = datetime.strptime(dates[-1], "%Y-%m-%d")
    start = first - timedelta(days=github_dow(first))

    cells = []
    cur = start
    while cur <= last:
        wk = (cur - start).days // 7
        dow = github_dow(cur)
        ds = cur.strftime("%Y-%m-%d")
        cells.append({"w": wk, "d": dow, "l": date_lvl.get(ds, -1), "date": ds})
        cur += timedelta(days=1)

    nw = max(c["w"] for c in cells) + 1 if cells else 53
    content_w = pl + nw * step + 14
    content_h = pt + 7 * step + 14
    sw = content_w
    sh = content_h + chrome_h
    dur = 1.5

    mn = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {sw} {sh}" width="{sw}" height="{sh}">']
    p.append("<style>")
    p.append(".cl{opacity:0}")
    p.append("@keyframes pp{to{opacity:1}}")
    p.append(f'.lb{{font-family:"Courier New",monospace;font-size:10px;fill:{label_clr}}}')
    p.append("</style>")

    p.append(f'<rect width="100%" height="100%" fill="{bg}" rx="8"/>')
    p.append(f'<rect width="{sw}" height="{chrome_h}" fill="{chrome_bg}" rx="8"/>')
    p.append(f'<rect y="{chrome_h - 8}" width="{sw}" height="8" fill="{chrome_bg}"/>')
    for i, c in enumerate(["#FF5F57", "#FFBD2E", "#27C93F"]):
        p.append(f'<circle cx="{18 + i * 20}" cy="{chrome_h // 2}" r="5" fill="{c}"/>')
    p.append(f'<text x="{sw // 2}" y="{chrome_h // 2 + 4}" text-anchor="middle"'
             f' font-family="Courier New,monospace" font-size="11" fill="{label_clr}"'
             f' opacity="0.7">$ cat contributions.log</text>')

    oy = chrome_h + 8

    # day labels
    for dow, lab in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        p.append(f'<text x="4" y="{oy + pt + dow * step + cell - 1}" class="lb">{lab}</text>')

    # month labels
    seen = set()
    for c in cells:
        d = datetime.strptime(c["date"], "%Y-%m-%d")
        if d.day <= 7:
            k = f"{d.year}-{d.month}"
            if k not in seen:
                seen.add(k)
                p.append(f'<text x="{pl + c["w"] * step}" y="{oy + pt - 6}" class="lb">{mn[d.month - 1]}</text>')

    # cells
    for c in cells:
        if c["l"] < 0:
            continue
        x = pl + c["w"] * step
        y = oy + pt + c["d"] * step
        clr = colors[min(c["l"], len(colors) - 1)]
        delay = ((c["w"] + c["d"]) / (nw + 7)) * dur
        p.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2"'
                 f' fill="{clr}" class="cl"'
                 f' style="animation:pp .05s {delay:.3f}s forwards"/>')

    p.append("</svg>")
    out = ROOT / filename
    out.write_text("\n".join(p))
    print(f"Generated: {out}")


def main():
    days = fetch()
    render(days, "#0D1117", "#161B22",
           ["#161B22", "#4B5563", "#7C3AED", "#A78BFA", "#22D3EE"],
           "#8B949E", "contrib-heatmap-dark.svg")
    render(days, "#FFFFFF", "#F6F8FA",
           ["#EBEDF0", "#9CA3AF", "#8B5CF6", "#7C3AED", "#0891B2"],
           "#57606A", "contrib-heatmap-light.svg")


if __name__ == "__main__":
    main()
