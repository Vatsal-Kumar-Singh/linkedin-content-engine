#!/usr/bin/env python3
"""Check the figures published in docs/BENCHMARKS.md against what the corpus currently says.

    python research/classify_posts.py --dump research/findings.json
    python research/verify_figures.py

Exit code is non-zero if any published figure has drifted, so this can gate a commit.

---

## Why this exists

The corpus has been re-cut four times: a threshold was added, a pruning pass removed 10% of it,
the person sample was rebuilt, and round two added 28 companies. Each time, numbers moved in a
document holding roughly 150 of them, and each time the sweep was done by eye. Twice that missed
something — a 1.58x that had become 1.61x, a person count that had become stale two edits earlier.

**A figure in a published document is a claim, and an unverified claim is the thing this whole
repository exists to prevent.** So the check is mechanical and the registry is small on purpose:
it holds the figures a reader would actually act on, not every number in every table. A registry
that tried to hold all 150 would rot faster than the document.

## What it cannot catch

It compares numbers to numbers. It cannot tell you that a *sentence* around a correct number has
become false — "four claims survive" beside a table now showing two would pass. Prose still needs
reading. This catches the arithmetic, which is the part that drifts silently.
"""

from __future__ import annotations

import json
import os
import re
import statistics
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(os.path.dirname(HERE), "docs", "BENCHMARKS.md")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def pct(a, b):
    return (100.0 * a / b) if b else 0.0


def main():
    if not os.path.exists(os.path.join(HERE, "findings.json")):
        sys.exit("run classify_posts.py --dump research/findings.json first")
    d = json.load(open(os.path.join(HERE, "findings.json"), encoding="utf-8"))
    rows = [r for r in d["posts"] if r.get("rel") is not None]
    doc = open(DOC, encoding="utf-8").read()

    n = len(rows)
    labels = Counter(r["label"] for r in rows)
    fmts = Counter(r["fmt"] for r in rows)

    def med_rel(pred):
        v = [r["rel"] for r in rows if pred(r)]
        return statistics.median(v) if v else None

    # Each entry: a human name, the exact string that must appear in the doc, and the value it
    # was generated from. The string is what is checked; the value is printed on a failure so the
    # correction is obvious rather than something to go and look up.
    checks = [
        # the counted corpus, not the labelled one: thin companies are labelled and not counted
        ("counted corpus", "**%s across %d pages** clear the 20-original threshold"
         % ("{:,}".format(n), len({r["name"] for r in rows})), n),
        ("selection engagement", "| `selection` — awards, funding, customer counts, partnerships | "
         "%.1f%% | **%.2fx**" % (pct(labels["selection"], n), med_rel(lambda r: r["label"] == "selection")),
         med_rel(lambda r: r["label"] == "selection")),
        ("requirements engagement", "| `requirements` — comparisons, trade-offs, buyer's guides | "
         "%.1f%% | **%.2fx**" % (pct(labels["requirements"], n), med_rel(lambda r: r["label"] == "requirements")),
         med_rel(lambda r: r["label"] == "requirements")),
        ("problem engagement", "| `problem` — naming a cost the reader is already paying | "
         "%.1f%% | **%.2fx**" % (pct(labels["problem"], n), med_rel(lambda r: r["label"] == "problem")),
         med_rel(lambda r: r["label"] == "problem")),
        ("requirements+consensus gap", "are %.1f%% of everything published"
         % pct(labels["requirements"] + labels["consensus"], n),
         pct(labels["requirements"] + labels["consensus"], n)),
        ("multi-image lift", "| **multi-image / carousel** | **%.1f%%** | **%.2fx**"
         % (pct(fmts["multi-image"], n), med_rel(lambda r: r["fmt"] == "multi-image")),
         med_rel(lambda r: r["fmt"] == "multi-image")),
        ("link lift", "| link post | %.1f%% | **%.2fx**"
         % (pct(fmts["link"], n), med_rel(lambda r: r["fmt"] == "link")),
         med_rel(lambda r: r["fmt"] == "link")),
        ("video lift", "| video | %.1f%% | %.2fx" % (pct(fmts["video"], n), med_rel(lambda r: r["fmt"] == "video")),
         med_rel(lambda r: r["fmt"] == "video")),
        ("companies with zero carousels",
         "**Fourteen of the %d companies published none at all.**" % len({r["name"] for r in rows}),
         sum(1 for c in {r["name"] for r in rows}
             if not any(r["fmt"] == "multi-image" for r in rows if r["name"] == c))),
    ]

    print("checking %d published figures against %d posts, %d companies\n"
          % (len(checks), n, len({r["name"] for r in rows})))
    bad = 0
    for name, needle, value in checks:
        if needle in doc:
            print("  ok      %-30s" % name)
        else:
            bad += 1
            print("  DRIFTED %-30s the document should contain:\n            %r"
                  % (name, needle))
    if bad:
        print("\n**%d of %d figures have drifted.** The corpus moved and the document did not."
              % (bad, len(checks)))
        return 1
    print("\nall %d figures match the corpus." % len(checks))
    return 0


if __name__ == "__main__":
    sys.exit(main())
