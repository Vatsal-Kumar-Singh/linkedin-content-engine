#!/usr/bin/env python3
"""Render the same dark card in each motion mode, so the direction can be
chosen by eye rather than argued about."""
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from postengine.config import load as load_config
from postengine.models import ContentSpec, Draft
from postengine.render.renderer import build_page, card_slots
from postengine.render.backgrounds import wash as compose_wash
from postengine.render.animate import animate_card

cfg = load_config(); geo = cfg.brand["formats"]["CARD"]
out = os.path.join(ROOT, "outputs", "motion"); os.makedirs(out, exist_ok=True)

spec = ContentSpec(id="motion", round=0, pain_point="A1", family="A",
    persona="cfo-procurement", funnel_stage="TOFU", content_type="statement",
    angle="cost-of-inaction", template="CARD", arc="statement",
    working_title="x", value_shown="x", objective="x", metric_label="no-hard-numbers")
draft = Draft(hook="x", body="x",
    creative_headline="Your pipeline broke on Sunday night.",
    creative_supporting_copy="You found out on Tuesday, from a dashboard that was wrong.",
    visual_concept="x")

import sys as _s
if "-h" in _s.argv or "--help" in _s.argv:
    print("usage: python scripts/build_motion_demos.py [modes] [grounds]")
    print("  modes:   sweep,draw,drift,both      (default: sweep,draw)")
    print("  grounds: light,dark                 (default: light,dark)")
    print()
    print("drift and both rotate the whole gradient, so every pixel changes every")
    print("frame and GIF cannot compress it — expect ~27 MB each. Install ffmpeg and")
    print("the MP4 path takes over automatically.")
    _s.exit(0)

MODES = _s.argv[1].split(",") if len(_s.argv) > 1 else ["sweep", "draw"]
GROUNDS = _s.argv[2].split(",") if len(_s.argv) > 2 else ["light", "dark"]

for ground in GROUNDS:
    for mode in MODES:
        slots = card_slots(cfg, draft, spec, "card/wash")
        slots.update(compose_wash(cfg, "motion", geo["width"], geo["height"],
                                  {"wash_dark": ground == "dark",
                                   "wash_motion": mode, "wash_shape": "pencil"}))
        slots["animate"] = True
        tag = "%s_%s" % (ground, mode)
        hp = os.path.join(out, "m_%s.html" % tag)
        io.open(hp, "w", encoding="utf-8").write(
            build_page(cfg, "card/wash", slots, "CARD", ground=ground))
        r = animate_card(hp, out, tag, geo["width"], geo["height"],
                         seconds=7.0, fps=10)
        print("%-12s %s  %5.2f MB  %d frames" % (tag, r["format"], r["bytes"] / 1e6, r["frames"]))
