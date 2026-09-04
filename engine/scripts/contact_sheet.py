#!/usr/bin/env python3
"""Visual QA sheet — every template family side by side, at full size and at
LinkedIn mobile feed width. Cohesion and variety are judged together."""
import base64, glob, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# outputs/ was reorganised: the pre-wash renders this sheet was built for
# now live under archive/pass-0/, and current cards are in cards/.
OUT = os.path.join(ROOT, "outputs", "cards")

ORDER = ["big_stat", "comparison", "journey", "editorial", "framework", "contrarian"]
TITLES = {"big_stat": "01 · BIG STAT", "comparison": "02 · BEFORE / AFTER",
          "journey": "03 · SYSTEM / JOURNEY", "editorial": "04 · EDITORIAL COVER",
          "framework": "05 · FRAMEWORK MAP", "contrarian": "06 · CONTRARIAN"}


def b64(p):
    with open(p, "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode()


def build(mobile=False):
    cells = []
    for name in ORDER:
        p = os.path.join(OUT, name + ".png")
        if not os.path.exists(p):
            continue
        cells.append("<figure><img src='%s'><figcaption>%s</figcaption></figure>"
                     % (b64(p), TITLES.get(name, name)))
    w = 380 if mobile else 640
    cols = 3
    css = ("""
    body{margin:0;background:#0B1F33;font-family:Inter,-apple-system,sans-serif;padding:46px;}
    h1{color:#F7F9FC;font-size:34px;font-weight:600;letter-spacing:-.01em;margin:0 0 6px;}
    p.lede{color:#8F98A3;font-size:19px;margin:0 0 40px;max-width:900px;line-height:1.5;}
    .g{display:grid;grid-template-columns:repeat(%d,%dpx);gap:38px;}
    figure{margin:0;}
    img{width:100%%;display:block;border:1px solid #1C3A55;}
    figcaption{color:#B8BEC6;font-size:16px;letter-spacing:.14em;padding-top:14px;font-weight:500;}
    """ % (cols, w))
    label = ("Rendered at 380px — LinkedIn mobile feed width" if mobile
             else "Rendered at full size (1200 × 1200)")
    return ("<!doctype html><html><head><meta charset='utf-8'><style>" + css +
            "</style></head><body><h1>the product creative system</h1>"
            "<p class='lede'>" + label + ". Judged together for cohesion (one brand) "
            "and variety (six distinct dominant ideas).</p>"
            "<div class='g'>" + "".join(cells) + "</div></body></html>")


def shoot(html, path, width):
    from playwright.sync_api import sync_playwright
    tmp = os.path.join(OUT, "_sheet.html")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(html)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": 1200})
        pg.goto("file://" + tmp, wait_until="load")
        pg.wait_for_timeout(250)
        pg.screenshot(path=path, full_page=True)
        b.close()
    os.unlink(tmp)
    return path


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print(shoot(build(False), os.path.join(OUT, "contact-sheet.png"), 2200))
    print(shoot(build(True), os.path.join(OUT, "contact-sheet-mobile.png"), 1400))
