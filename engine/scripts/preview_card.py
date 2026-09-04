#!/usr/bin/env python3
"""Render one card from literal copy — no LLM, no gauntlet.

Design iteration needs a fast loop. Going through the full pipeline to look at
a border radius costs a generation, a judge pass and a critic pass; this hands
the template the copy directly and shoots it. It is a QA tool, so it renders
only what it is given and asserts nothing about the copy's quality.

  python scripts/preview_card.py --statement "..." --sub "..." [--animate]
"""
import argparse, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from postengine.config import load as load_config
from postengine.models import ContentSpec, Draft
from postengine.render.renderer import (build_page, card_slots, detect_renderer,
                                      _shoot_playwright)


SEED = "preview"


def _spec(template_dir):
    return ContentSpec(id=SEED, round=0, pain_point="A1", family="A",
                       persona="cfo-procurement", funnel_stage="TOFU",
                       content_type="statement", angle="cost-of-inaction",
                       template="CARD", arc="statement",
                       working_title="preview", value_shown="preview", objective="preview",
                       metric_label="no-hard-numbers")


def _draft(statement, sub):
    """The real Draft, so the preview cannot drift from what the engine renders."""
    return Draft(hook=statement, body=sub, creative_headline=statement,
                 creative_supporting_copy=sub, visual_concept="preview")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--statement", required=True)
    ap.add_argument("--sub", default="")
    ap.add_argument("--template", default="card/contrarian")
    ap.add_argument("--animate", action="store_true")
    ap.add_argument("--ground", default="dark")
    ap.add_argument("--seed", default="preview",
                    help="post id the wash geometry is derived from")
    ap.add_argument("--out", default=os.path.join(ROOT, "outputs", "preview"))
    a = ap.parse_args()

    global SEED
    SEED = a.seed
    # Playwright resolves file:// against the process working directory, so a
    # relative --out silently fails to load the page it just wrote.
    a.out = os.path.abspath(a.out)
    os.makedirs(a.out, exist_ok=True)
    cfg = load_config()
    geo = cfg.brand["formats"]["CARD"]
    draft = _draft(a.statement, a.sub)

    slots = card_slots(cfg, draft, _spec(a.template), a.template)
    slots["animate"] = bool(a.animate)
    html = build_page(cfg, a.template, slots, "CARD", ground=a.ground)
    hp = os.path.join(a.out, "preview.html")
    with open(hp, "w", encoding="utf-8") as fh:
        fh.write(html)

    png = os.path.join(a.out, "preview.png")
    _shoot_playwright([(hp, png)], geo["width"], geo["height"],
                      (cfg.engine.get("creative") or {}).get("autofit") or {},
                      float(cfg.brand["legibility"]["min_caption_px"]))
    print("still :", png)

    if a.animate:
        from postengine.render.animate import animate_card
        m = animate_card(hp, a.out, "preview_motion", geo["width"], geo["height"],
                         seconds=float(slots.get("pulse_secs") or 7.0),
                         keep_frames=True)   # the preview exists to be eyeballed
        print("motion:", m["path"], "|", m["format"], m["frames"], "frames",
              "| %.2f MB" % (m["bytes"] / 1e6))


if __name__ == "__main__":
    main()
