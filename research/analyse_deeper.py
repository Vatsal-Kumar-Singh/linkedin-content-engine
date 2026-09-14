#!/usr/bin/env python3
"""A second pass over the cleaned corpus, looking for what the first pass missed.

    python research/classify_posts.py --dump research/findings.json
    python research/analyse_deeper.py

The first pass asked what companies publish and what the feed rewards. This one asks harder
questions of the same data:

- **Is the headline finding universal or driven by a few accounts?** A corpus-wide median can be
  produced by six outliers. Every claim worth acting on should survive being recomputed
  within each company and counted as a vote.
- **How concentrated is engagement?** If most of it comes from a handful of posts, planning
  around a median is planning around a number nobody experiences.
- **Who is actually active?** A person channel that publishes twice a year is not a channel.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
JOBS = ["problem", "exploration", "requirements", "selection", "validation", "consensus"]
OTHER = ["recruitment", "culture", "event", "product-news", "csr"]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def pct(a, b):
    return (100.0 * a / b) if b else 0.0


def gini(vals):
    """0 = everybody equal, 1 = one post takes everything. On engagement, this says whether a
    feed is a portfolio of steady posts or a lottery with a few winners."""
    v = sorted(x for x in vals if x is not None and x >= 0)
    n = len(v)
    if n < 2 or sum(v) == 0:
        return None
    cum = sum((i + 1) * x for i, x in enumerate(v))
    return (2 * cum) / (n * sum(v)) - (n + 1) / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", default=os.path.join(HERE, "findings.json"))
    ap.add_argument("--min-n", type=int, default=6)
    a = ap.parse_args()
    d = json.load(open(a.findings, encoding="utf-8"))
    rows = d["posts"]
    by_co = defaultdict(list)
    for r in rows:
        by_co[r["name"]].append(r)
    print("%d posts, %d companies\n" % (len(rows), len(by_co)))

    # ----------------------------------------------------------------------------------------
    print("=" * 78)
    print("1. IS THE ENGAGEMENT RANKING UNIVERSAL, OR DRIVEN BY A FEW ACCOUNTS?")
    print("=" * 78)
    print("The corpus-wide table says awards beat buyer's guides. Recomputed inside each company")
    print("and counted as a vote, does that hold? A label is only comparable within a company")
    print("that published at least %d of them.\n" % a.min_n)
    print("%-16s %7s %8s %9s   %s" % ("", "corpus", "companies", "above 1.0", "verdict"))
    for lab in JOBS + OTHER:
        wins = tot = 0
        meds = []
        for co, rs in by_co.items():
            mine = [r["rel"] for r in rs if r["label"] == lab and r.get("rel") is not None]
            if len(mine) < a.min_n:
                continue
            tot += 1
            m = statistics.median(mine)
            meds.append(m)
            if m > 1.0:
                wins += 1
        if tot < 5:
            print("%-16s %7s %8d   too few companies" % (lab, "-", tot))
            continue
        share = pct(wins, tot)
        verdict = ("consistent" if share >= 70 or share <= 30
                   else "MIXED: the corpus number hides disagreement")
        print("%-16s %7.2f %8d %8.0f%%   %s"
              % (lab, statistics.median(meds), tot, share, verdict))

    # ----------------------------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("2. HOW CONCENTRATED IS ENGAGEMENT?")
    print("=" * 78)
    allg = []
    for co, rs in by_co.items():
        e = [r["eng"] for r in rs]
        g = gini(e)
        if g is not None:
            allg.append((g, co, len(rs)))
    allg.sort()
    print("Gini on raw engagement, per company. 0 = every post lands the same, 1 = one post")
    print("takes everything.\n")
    print("   median company: %.2f" % statistics.median(g for g, _, _ in allg))
    print("   most even:   %-24s %.2f" % (allg[0][1], allg[0][0]))
    print("   most lottery:%-24s %.2f" % (allg[-1][1], allg[-1][0]))
    tot_e = sum(r["eng"] for r in rows)
    srt = sorted((r["eng"] for r in rows), reverse=True)
    for frac in (0.01, 0.05, 0.10, 0.20):
        k = max(1, int(len(srt) * frac))
        print("   the top %3.0f%% of posts carry %4.0f%% of all engagement"
              % (frac * 100, pct(sum(srt[:k]), tot_e)))
    print("\n   **A median is the typical post. It is not where the reach is.** Planning to the")
    print("   median optimises the body of the distribution; the tail is what people remember.")

    # ----------------------------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("3. WHAT DO THE BREAKOUT POSTS HAVE IN COMMON?")
    print("=" * 78)
    top = [r for r in rows if (r.get("rel") or 0) >= 3.0]
    rest = [r for r in rows if r.get("rel") is not None and r["rel"] < 3.0]
    print("%d posts tripled their own company's median. Against the other %d:\n"
          % (len(top), len(rest)))
    print("%-16s %9s %9s %8s" % ("", "breakout", "the rest", "lift"))
    for lab in sorted(set(r["label"] for r in rows)):
        x = pct(sum(1 for r in top if r["label"] == lab), len(top))
        y = pct(sum(1 for r in rest if r["label"] == lab), len(rest))
        if x < 1 and y < 1:
            continue
        print("%-16s %8.1f%% %8.1f%% %+7.1f" % (lab, x, y, x - y))
    print()
    for f in ("text", "link", "image", "multi-image", "video"):
        x = pct(sum(1 for r in top if r["fmt"] == f), len(top))
        y = pct(sum(1 for r in rest if r["fmt"] == f), len(rest))
        print("%-16s %8.1f%% %8.1f%% %+7.1f" % (f, x, y, x - y))

    # ----------------------------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("4. DOES THE FORMAT ADVANTAGE HOLD INSIDE EACH JOB?")
    print("=" * 78)
    print("Multi-image earns 1.58x corpus-wide, but it is mostly used for culture. Is the format")
    print("carrying the number, or the content that happens to be published in it?\n")
    print("%-16s %26s %26s" % ("", "multi-image", "same job, other formats"))
    print("%-16s %8s %9s %8s %9s" % ("", "n", "median", "n", "median"))
    for lab in JOBS + OTHER:
        mi = [r["rel"] for r in rows if r["label"] == lab and r["fmt"] == "multi-image"
              and r.get("rel") is not None]
        ot = [r["rel"] for r in rows if r["label"] == lab and r["fmt"] != "multi-image"
              and r.get("rel") is not None]
        if len(mi) < 8:
            continue
        print("%-16s %8d %9.2f %8d %9.2f   %s"
              % (lab, len(mi), statistics.median(mi), len(ot), statistics.median(ot),
                 "format wins" if statistics.median(mi) > statistics.median(ot) else "no gain"))

    # ----------------------------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("5. HOW MUCH OF THE VARIANCE IS BETWEEN COMPANIES, AND HOW MUCH INSIDE ONE?")
    print("=" * 78)
    within = []
    for co, rs in by_co.items():
        rel = [r["rel"] for r in rs if r.get("rel") is not None]
        if len(rel) >= 20:
            within.append((max(rel) / max(0.01, min(rel)), co, statistics.pstdev(rel)))
    within.sort()
    print("Every company's median is 1.00 by construction, so between-company variance in")
    print("*relative* terms is zero. What is left is the spread inside each feed:\n")
    print("   median company's best post is %.0fx its worst"
          % statistics.median(w for w, _, _ in within))
    print("   median within-company standard deviation: %.2f"
          % statistics.median(s for _, _, s in within))
    print("\n   **The decision that matters is not which company to imitate. It is which post to")
    print("   publish next**, because the spread inside one company's own feed is larger than")
    print("   anything measured between companies.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
