#!/usr/bin/env python3
"""Render one worked example of every card template, in both grounds.

Copy is matched to the SHAPE of each template, not assigned at random. A stat
card needs a pain that has a number; a comparison needs two states; a journey
needs an escalation. Putting one pain through all seven would have forced the
same mismatch that moved Round 1 off stat cards in the first place.

On the stat card specifically: the number describes the READER's situation, not
our performance. The claim register rates 33 of 62 claims unsubstantiated and
records that the deck's own 70% figure is contradicted two slides earlier, so no
performance number belongs on a card. "Four companies" is a description of how
their estate is staffed — recognisable, checkable by the reader, and not a claim
about us.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from postengine.config import load as load_config
from postengine.models import ContentSpec, Draft
from postengine.render.renderer import build_page, card_slots, _shoot_playwright

# template -> (pain, copy). Every headline names the subject word (C0.1), carries a
# concrete noun that is not the brand name (C0.3), and no question opens on a
# yes/no auxiliary (C0.4).
EXAMPLES = [
    dict(
        key="big_stat", template="card/big_stat", pain="A2", family="A",
        headline="4", focal="4", focal_label="teams touch this pipeline",
        sub="Ingestion, transformation, the warehouse, the dashboard. Ask who "
            "owns it when the number is wrong.",
        note="A number describing the reader's own setup, not our performance.",
    ),
    dict(
        key="comparison", template="card/comparison", pain="A1", family="A",
        headline="Finding out on Sunday, or finding out on Tuesday",
        sub="The same broken pipeline. Two very different Mondays.",
        left_label="Nothing watching", right_label="Watched",
        rows=[("You hear it from a colleague", "You hear it from an alert"),
              ("Monday's numbers are Saturday's", "Monday's numbers are Monday's"),
              ("Someone reruns it by hand", "It reruns and tells you"),
              ("Two days of wrong decisions", "Twenty minutes")],
        note="Two states side by side — the shape this template exists for.",
    ),
    dict(
        key="journey", template="card/journey", pain="C1", family="C",
        headline="How a number stops being trustworthy",
        sub="Nobody decides to stop trusting a dashboard. It just happens.",
        steps=[("A job fails quietly", "No alert, because nothing was watching it."),
               ("The dashboard still renders", "Using whatever it loaded last."),
               ("Someone notices it looks odd", "But cannot say why, so says nothing."),
               ("Now nobody quotes that number", "The dashboard is still up. It is just ignored.")],
        note="An escalation in four beats — the problem-spiral shape.",
    ),
    dict(
        key="framework", template="card/framework", pain="A2", family="A",
        headline="What owning a pipeline actually means",
        sub="Four jobs. Usually four different people, and no name against the last one.",
        nodes=[("Move the data", "Ingestion and scheduling."),
               ("Shape it", "Transformations and tests."),
               ("Serve it", "The warehouse and the dashboard."),
               ("Answer for it", "When the number is wrong, who replies.")],
        note="A structure the reader can hold — the framework shape.",
    ),
    dict(
        key="editorial", template="card/editorial", pain="B1", family="B",
        headline="Your analysts start every morning checking last night's jobs",
        sub="Not modelling. Not answering questions. Checking whether the machines "
            "did what they were told.",
        eyebrow="THE MORNING CHECK",
        note="Headline-dominant, nothing competing. Doubles as a carousel cover.",
    ),
    dict(
        key="contrarian", template="card/contrarian", pain="C1", family="C",
        headline="Nobody can tell you where that number came from",
        sub="Three people will guess. That is not the same as knowing.",
        note="One sentence carrying the argument.",
    ),
    dict(
        key="wash", template="card/wash", pain="A1", family="A",
        headline="Your pipeline broke on Sunday night",
        sub="You found out on Tuesday, from a dashboard that was already wrong.",
        note="The statement card on the standard ground.",
    ),
]



def _spec(ex):
    return ContentSpec(
        id=ex["key"], round=0, pain_point=ex["pain"], family=ex["family"],
        persona="cfo-procurement", funnel_stage="TOFU", content_type="statement",
        angle="cost-of-inaction", template="CARD", arc="statement",
        working_title=ex["headline"], value_shown="example", objective="example",
        metric_label="no-hard-numbers")


def _draft(ex):
    d = Draft(hook=ex["headline"], body=ex["sub"],
              creative_headline=ex["headline"],
              creative_supporting_copy=ex["sub"],
              visual_concept="example")
    for field, attr in (("focal", "focal"), ("focal_label", "focal_unit"),
                        ("eyebrow", "eyebrow"),
                        ("left_label", "left_label"), ("right_label", "right_label")):
        if ex.get(field):
            setattr(d, attr, ex[field])
    if ex.get("rows"):
        d.comparison_rows = [{"left": a, "right": b} for a, b in ex["rows"]]
    # The journey and framework templates read `title` and `body`, not `label`.
    for src in ("steps", "nodes"):
        if ex.get(src) and not d.steps:
            d.steps = [{"title": s[0], "body": s[1]} if isinstance(s, tuple)
                       else {"title": s, "body": ""} for s in ex[src]]
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "outputs", "cards"))
    ap.add_argument("--motion", default="sweep",
                    help="dark-card motion mode: sweep | drift | both | draw")
    a = ap.parse_args()
    # Playwright resolves file:// against the process working directory, so a
    # relative --out silently fails to load the page it just wrote.
    a.out = os.path.abspath(a.out)
    os.makedirs(a.out, exist_ok=True)

    cfg = load_config()
    geo = cfg.brand["formats"]["CARD"]
    leg = cfg.brand["legibility"]
    pages = []

    for ex in EXAMPLES:
        spec, draft = _spec(ex), _draft(ex)
        for ground in ("light", "dark"):
            slots = card_slots(cfg, draft, spec, ex["template"])
            if ground == "dark":
                # Recompose the ground in the dark colourway and switch motion on.
                from postengine.render.backgrounds import wash as compose_wash
                slots.update(compose_wash(cfg, ex["key"], geo["width"], geo["height"],
                                          {"wash_dark": True, "wash_motion": a.motion}))
                slots["animate"] = True
            html = build_page(cfg, ex["template"], slots, "CARD", ground=ground)
            hp = os.path.join(a.out, "%s_%s.html" % (ex["key"], ground))
            with open(hp, "w", encoding="utf-8") as fh:
                fh.write(html)
            pages.append((hp, os.path.join(a.out, "%s_%s.png" % (ex["key"], ground))))

    _shoot_playwright(pages, geo["width"], geo["height"],
                      (cfg.engine.get("creative") or {}).get("autofit") or {},
                      float(leg["min_caption_px"]))
    print("rendered %d cards -> %s" % (len(pages), a.out))


if __name__ == "__main__":
    main()
