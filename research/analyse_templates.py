#!/usr/bin/env python3
"""Mine the corpus for recurring post shapes, so a template library is derived rather than written.

    python research/classify_posts.py --dump research/findings.json
    python research/analyse_templates.py

The brief this study answers asked for "templates and patterns". Everything else here measures
what companies publish *about*; this asks what shape the posts are, which is the part a writer
actually reuses.

---

## What counts as a shape, and why these four axes

A shape is `job x format x opening move`. All three are machine-read from the post
(`CLASSIFICATION-PROTOCOL.md` covers the one that is not: the job is hand-labelled). Nothing here
is a judgement about quality, so the same corpus scored twice gives the same answer.

**The opening move is the only one that needed defining**, and it is defined narrowly on purpose:
a question mark in the first line, a leading numeral, a first-person-plural opener, a second-person
opener, a named-entity opener, or none of those. A richer taxonomy would be a better description
of writing and a worse instrument, because two readers would disagree about it.

## The rule that keeps this from being astrology

**A shape needs 25 posts before it is named.** Cross three axes and a corpus of three thousand posts
produces hundreds of cells, most of them nearly empty, and the top of a list sorted by median lift
is then just the cells with the fewest posts in them. A fourth axis, length band, was tried and
removed: length had already been measured as barely moving engagement, so all it did was split
every cell below the floor. The threshold is applied before ranking, not
after, and the number of shapes that fail it is reported — it is usually most of them.

**A shape is a description, not a recommendation.** The engagement column says what that shape
earned relative to its own company's median. It says nothing about whether the post did commercial
work, and this corpus has already shown those two ranks to be near-opposites.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
JOBS = ["problem", "exploration", "requirements", "selection", "validation", "consensus"]
OTHER = ["recruitment", "culture", "event", "product-news", "csr"]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def first_line(text):
    for line in (text or "").splitlines():
        if line.strip():
            return line.strip()
    return ""


def opening_move(text):
    """Five mutually exclusive buckets, in priority order. Narrow on purpose: see the docstring.

    An earlier version had a sixth, `named`, meant to catch a post opening on a customer's name.
    Its test was "a capitalised word among the first three", which also matches Today,
    Introducing, Most, and every sentence beginning with a proper noun: 59% of the corpus. A
    bucket holding three posts in five is not a pattern, it is a broken detector, and it was
    crowding every other bucket out of the ranking. There is no cheap honest test for a named
    entity, so the bucket is gone rather than wrong and `declarative` is the residual.
    """
    fl = first_line(text)
    if not fl:
        return "none"
    if "?" in fl:
        return "question"
    if re.match(r"^[^A-Za-z0-9]*[0-9]", fl):
        return "number"
    if re.match(r"^[^A-Za-z0-9]*(we|our|us|i)\b", fl, re.I):
        return "we"
    if re.match(r"^[^A-Za-z0-9]*(you|your|if you|when you|most teams|every)\b", fl, re.I):
        return "you"
    return "declarative"


def band(n):
    if n < 30:
        return "0-29w"
    if n < 60:
        return "30-59w"
    if n < 100:
        return "60-99w"
    if n < 160:
        return "100-159w"
    return "160w+"


def load_text():
    """Post id -> raw text, from raw/ rather than from the batch digests, which are truncated."""
    import glob
    out = {}
    for path in glob.glob(os.path.join(HERE, "raw", "*.json")):
        d = json.load(open(path, encoding="utf-8"))
        for p in d.get("posts") or []:
            pid = str(p.get("id") or "")
            if pid:
                out[pid] = p.get("content") or ""
    return out


def med(vals):
    return statistics.median(vals) if vals else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", default=os.path.join(HERE, "findings.json"))
    ap.add_argument("--min-n", type=int, default=25,
                    help="a shape below this is not named. Applied BEFORE ranking, because a "
                         "list of rare shapes sorted by median is a list of small samples")
    a = ap.parse_args()

    d = json.load(open(a.findings, encoding="utf-8"))
    rows = [r for r in d["posts"] if r.get("rel") is not None]
    texts = load_text()
    for r in rows:
        t = texts.get(r["id"], "")
        r["open"] = opening_move(t)
        r["band"] = band(r["words"])

    print("%d posts, %d companies\n" % (len(rows), len({r["name"] for r in rows})))

    # ------------------------------------------------------------------------------------------
    print("=" * 90)
    print("1. THE OPENING MOVE, ON ITS OWN")
    print("=" * 90)
    print("The first line is the only part most readers see, so it is the part worth naming.\n")
    print("%-12s %7s %8s %10s %12s" % ("opening", "n", "share", "median x", "doubles own"))
    by_open = defaultdict(list)
    for r in rows:
        by_open[r["open"]].append(r)
    for k, rs in sorted(by_open.items(), key=lambda kv: -med([x["rel"] for x in kv[1]])):
        rel = [x["rel"] for x in rs]
        print("%-12s %7d %7.1f%% %10.2f %11.0f%%"
              % (k, len(rs), 100.0 * len(rs) / len(rows), med(rel),
                 100.0 * sum(1 for x in rel if x >= 2) / len(rel)))

    # ------------------------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("2. THE SHAPES THAT RECUR: job x format x opening")
    print("=" * 90)
    shapes = defaultdict(list)
    for r in rows:
        shapes[(r["label"], r["fmt"], r["open"])].append(r)
    named = {k: v for k, v in shapes.items() if len(v) >= a.min_n}
    print("%d distinct shapes exist; %d clear the %d-post floor and carry %d posts (%.0f%% of "
          "the corpus).\nThe rest are real posts and unusable evidence.\n"
          % (len(shapes), len(named), a.min_n, sum(len(v) for v in named.values()),
             100.0 * sum(len(v) for v in named.values()) / len(rows)))
    print("%-14s %-12s %-12s %6s %9s %5s %12s" %
          ("job", "format", "opening", "n", "median x", "cos", "doubles own"))
    ranked = sorted(named.items(), key=lambda kv: -med([x["rel"] for x in kv[1]]))
    for (lab, fmt, op), rs in ranked:
        rel = [x["rel"] for x in rs]
        print("%-14s %-12s %-12s %6d %9.2f %5d %11.0f%%" %
              (lab, fmt, op, len(rs), med(rel), len({x["name"] for x in rs}),
               100.0 * sum(1 for x in rel if x >= 2) / len(rel)))

    # ------------------------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("3. FOR EACH BUYING JOB: THE SHAPE MOST USED, AND THE SHAPE THAT EARNS MOST")
    print("=" * 90)
    print("Where these differ, the gap is the finding: the industry's default shape for that job")
    print("is not the shape that works for it.\n")
    for lab in JOBS + OTHER:
        mine = {k: v for k, v in shapes.items() if k[0] == lab and len(v) >= 10}
        if not mine:
            print("%-14s  no shape reaches ten posts" % lab)
            continue
        most = max(mine.items(), key=lambda kv: len(kv[1]))
        best = max(mine.items(), key=lambda kv: med([x["rel"] for x in kv[1]]))
        fmtk = lambda k: "%s / %s" % (k[1], k[2])
        print("%-14s most used: %-34s n=%-4d %.2fx" %
              (lab, fmtk(most[0]), len(most[1]), med([x["rel"] for x in most[1]])))
        tag = "  <-- same shape" if best[0] == most[0] else ""
        print("%-14s best:      %-34s n=%-4d %.2fx%s" %
              ("", fmtk(best[0]), len(best[1]), med([x["rel"] for x in best[1]]), tag))

    # ------------------------------------------------------------------------------------------
    print("\n" + "=" * 90)
    print("4. WHICH OPENING EACH JOB REACHES FOR, AND WHAT IT EARNS THERE")
    print("=" * 90)
    print("The same opening is not worth the same in every job, which is why a corpus-wide")
    print("'never open on a question' is too blunt to act on.\n")
    opens = ["question", "number", "we", "you", "declarative"]
    print("%-14s %s" % ("", "".join("%-14s" % o for o in opens)))
    for lab in JOBS + OTHER:
        mine = [r for r in rows if r["label"] == lab]
        if len(mine) < 40:
            continue
        cells = []
        for o in opens:
            sub = [r["rel"] for r in mine if r["open"] == o]
            cells.append("%3.0f%% %6s" % (100.0 * len(sub) / len(mine),
                                          ("%.2f" % med(sub)) if len(sub) >= 8 else "-"))
        print("%-14s %s" % (lab, "".join("%-14s" % c for c in cells)))
    print("\nEach cell is: share of that job's posts using that opening, then the median those")
    print("posts earned. A dash means fewer than eight posts, which is not a measurement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
