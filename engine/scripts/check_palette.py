#!/usr/bin/env python3
"""Measure whether a palette can actually do the jobs the renderer asks of it.

`config/brand.yaml` tells you to run this before choosing wash poles. It was never shipped, so
until now the instruction pointed at nothing and the pole choice in `render/backgrounds.py` was
inherited from a palette nobody here uses.

Three questions, all answered by measurement rather than by eye:

1. **Can a colour reach the pale band?** The wash tints its poles toward white and runs them at
   saturation 29-41%, value 89-100% -- measured off the reference, see backgrounds.py. A colour
   that lands outside that band after tinting is not pale, it is grey, and the wash goes flat.

2. **Are the poles far enough apart in hue?** The reference sits 89 degrees apart. Anything under
   about 10 degrees gets its separation from value alone, which is a weaker effect and worth
   knowing you are choosing.

3. **Does type survive on every ground?** WCAG contrast for each ground's foreground, muted and
   accent roles. 4.5:1 for body, 3.0:1 for large display type, and structure colours are exempt
   because they draw hairlines rather than letters.

    python scripts/check_palette.py
    python scripts/check_palette.py --poles          # rank every pair as a wash candidate
"""

from __future__ import annotations

import argparse
import colorsys
import itertools
import os
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The pale band, measured off the reference in render/backgrounds.py.
SAT_BAND = (0.29, 0.41)
VAL_BAND = (0.89, 1.00)
# Tint amounts the wash actually uses when it mixes a pole toward white.
TINT_STEPS = (0.55, 0.62, 0.70, 0.78)


def rgb(hexcol: str):
    h = hexcol.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def tint(hexcol: str, amount: float) -> str:
    r, g, b = (int(hexcol.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(int(round(c + (255 - c) * amount)) for c in (r, g, b))


def hsv(hexcol: str):
    return colorsys.rgb_to_hsv(*rgb(hexcol))


def luminance(hexcol: str) -> float:
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in rgb(hexcol))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def pale_reach(hexcol: str):
    """Best tint amount for this colour, and whether it lands inside the pale band."""
    best = None
    for amt in TINT_STEPS:
        h, s, v = hsv(tint(hexcol, amt))
        inside = SAT_BAND[0] <= s <= SAT_BAND[1] and VAL_BAND[0] <= v <= VAL_BAND[1]
        score = (0 if inside else 1, abs(s - sum(SAT_BAND) / 2))
        if best is None or score < best[0]:
            best = (score, amt, s, v, inside)
    _, amt, s, v, inside = best
    return amt, s, v, inside


def hue_gap(a: str, b: str) -> float:
    d = abs(hsv(a)[0] - hsv(b)[0]) * 360.0
    return min(d, 360.0 - d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", default=os.path.join(ROOT, "config", "brand.yaml"))
    ap.add_argument("--poles", action="store_true", help="rank every pair as a wash candidate")
    a = ap.parse_args()

    with open(a.brand, "r", encoding="utf-8") as fh:
        brand = yaml.safe_load(fh)
    pal = brand["palette"]
    grounds = brand.get("grounds") or {}

    print("\n  PALE BAND  (wash poles need saturation %.0f-%.0f%%, value %.0f-%.0f%% after tinting)"
          % (SAT_BAND[0] * 100, SAT_BAND[1] * 100, VAL_BAND[0] * 100, VAL_BAND[1] * 100))
    reach = {}
    for name, hexcol in sorted(pal.items()):
        amt, s, v, ok = pale_reach(hexcol)
        reach[name] = ok
        print(f"    {'PALE' if ok else '  --'}  {name:16s} {hexcol}  tint {amt:.2f} -> "
              f"sat {s * 100:5.1f}%  val {v * 100:5.1f}%")

    usable = [n for n, ok in reach.items() if ok]
    print(f"\n    {len(usable)} of {len(pal)} colours reach the pale band: "
          f"{', '.join(usable) if usable else 'NONE'}")
    if len(usable) < 2:
        print("    WARNING: a wash needs two poles. With fewer than two, use a flat or")
        print("    patterned ground (grid, dot_grid, linework) instead of the wash template.")

    if a.poles or len(usable) >= 2:
        print("\n  POLE PAIRS  (reference sits 89 degrees apart; under 10 means value, not hue)")
        pairs = sorted(itertools.combinations(usable, 2),
                       key=lambda p: -hue_gap(pal[p[0]], pal[p[1]]))
        for x, y in pairs[:8]:
            g = hue_gap(pal[x], pal[y])
            note = "hue contrast" if g >= 30 else "value contrast only" if g < 10 else "narrow"
            print(f"    {g:5.1f} deg  {x:16s} x {y:16s}  {note}")
        if not pairs:
            print("    none")

    print("\n  CONTRAST  (body needs 4.5:1, display type 3.0:1; structure roles are exempt)")
    worst = 0
    for gname, roles in grounds.items():
        bg = pal[roles["bg"]]
        print(f"    ground {gname:6s} bg {roles['bg']} {bg}")
        for role in ("fg", "muted", "accent"):
            if role not in roles:
                continue
            c = contrast(bg, pal[roles[role]])
            floor = 4.5 if role in ("fg", "muted") else 3.0
            flag = "ok  " if c >= floor else "FAIL"
            if c < floor:
                worst += 1
            print(f"      {flag} {role:7s} {roles[role]:16s} {pal[roles[role]]}  {c:5.2f}:1"
                  f"   (needs {floor})")

    print()
    if worst:
        print(f"  {worst} contrast failure(s). Fix the ground map in brand.yaml before rendering.\n")
        return 1
    print("  No contrast failures.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
