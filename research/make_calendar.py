#!/usr/bin/env python3
"""Turn the measured corpus into a concrete four-week LinkedIn slot plan for one cell.

    python research/classify_posts.py --dump research/findings.json
    python research/make_calendar.py --cell "saas x enterprise"
    python research/make_calendar.py --cell "saas x plg x early"      # three-axis, see CELLS.md
    python research/make_calendar.py --industry healthcare-lifesci --weeks 8
    python research/make_calendar.py --cell "service x slg" --deviate

Every slot carries the job it does, the format to publish it in, the opening move, and the
aspect ratio — because all four are measured and all four are decisions somebody makes anyway,
usually by accident.

---

## This produces a baseline, and a baseline is not a plan

**The mix comes from what companies in that cell actually publish, which is not what works.**
This repository's single most repeated finding is that the content earning reach and the content
doing commercial work are close to opposites. A calendar that reproduces the corpus exactly
reproduces the corpus's mistakes: 2.4% buyer's guides, 1.5% business case, an event calendar
posted as link previews.

So there are two modes and the difference between them is the point:

- **default** — the cell's measured mix, slot for slot. Use it to see what your peers publish.
- **`--deviate`** — the same cadence, with the decision-stage floor this corpus says the whole
  industry is missing: `requirements` and `consensus` raised to 10% of slots between them, taken
  proportionally out of whatever the cell over-publishes. Use it to build a calendar.

Neither is a recommendation about *your* company. `engine/decision/` exists to make that call from
a profile, and it deliberately returns no multipliers.

## Where the format and shape on each slot come from

Not from the cell — from `analyse_templates.py` and the aspect-ratio measurement, which are
corpus-wide. A cell has too few posts to support a format-by-job-by-opening recommendation, and
inventing one from twelve posts would be worse than borrowing one from three thousand. Where the
corpus has no measured best shape for a job, the slot says so rather than guessing.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
JOBS = ["problem", "exploration", "requirements", "selection", "validation", "consensus"]
OTHER = ["recruitment", "culture", "event", "product-news", "csr"]
DECISION = ["requirements", "consensus"]

# From analyse_templates.py section 3 and sample_creative.py --measure-only. Kept here as a
# table rather than recomputed, because a calendar generator that re-reads every raw file to
# place a slot is a slow way to look up nine rows -- but the source is named on every line so
# the number can be checked.
BEST_SHAPE = {
    # job:           (format,        opening,       aspect,      measured)
    "problem":       ("video",       "you",         "wide 16:9", "1.07x, n=13"),
    "exploration":   ("video",       "a number",    "wide 16:9", "1.39x, n=10"),
    "requirements":  ("video",       "declarative", "wide 16:9", "1.03x, n=11"),
    "selection":     ("image",       "we",          "portrait",  "2.20x, n=21"),
    "validation":    ("video",       "declarative", "portrait",  "1.11x, n=112"),
    "consensus":     (None,          None,          None,        "no shape reaches ten posts"),
    "recruitment":   ("image",       "we",          "square",    "1.53x, n=15"),
    "culture":       ("multi-image", "we",          "square",    "2.38x, n=21"),
    "event":         ("multi-image", "declarative", "portrait",  "1.63x, n=60"),
    "product-news":  ("video",       "declarative", "wide 16:9", "2.19x, n=11"),
    "csr":           ("multi-image", "declarative", "square",    "1.53x, n=9"),
}

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def cadence_of(rows):
    """Posts per week for this cohort, from the span each company's pull actually covers."""
    by_co = defaultdict(list)
    for r in rows:
        if r.get("date"):
            by_co[r["name"]].append(r["date"])
    rates = []
    for co, dates in by_co.items():
        dates.sort()
        if len(dates) < 5:
            continue
        import datetime
        try:
            lo = datetime.date.fromisoformat(dates[0])
            hi = datetime.date.fromisoformat(dates[-1])
        except ValueError:
            continue
        weeks = max(1.0, (hi - lo).days / 7.0)
        rates.append(len(dates) / weeks)
    if not rates:
        return None, 0
    import statistics
    return statistics.median(rates), len(rates)


def largest_remainder(shares, total):
    """Allocate `total` whole slots across `shares` without the rounding losing or inventing one."""
    raw = {k: v * total for k, v in shares.items()}
    out = {k: int(math.floor(v)) for k, v in raw.items()}
    short = total - sum(out.values())
    for k, _ in sorted(raw.items(), key=lambda kv: -(kv[1] - math.floor(kv[1])))[:short]:
        out[k] += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", default=os.path.join(HERE, "findings.json"))
    ap.add_argument("--cell",
                    help='"saas x enterprise", or "saas x plg x early" for the three-axis cut')
    ap.add_argument("--industry", help="e.g. healthcare-lifesci")
    ap.add_argument("--weeks", type=int, default=4)
    ap.add_argument("--per-week", type=float,
                    help="override the measured cadence for this cohort")
    ap.add_argument("--deviate", action="store_true",
                    help="raise requirements+consensus to 10%% of slots, out of what the cell "
                         "over-publishes. See the docstring")
    a = ap.parse_args()

    if not (a.cell or a.industry):
        sys.exit("pick --cell or --industry")

    d = json.load(open(a.findings, encoding="utf-8"))
    rows = d["posts"]
    if a.cell:
        # two parts is offering x motion; three is offering x motion x stage, which is how a
        # company actually identifies itself and the cut docs/CELLS.md uses
        parts = [x.strip() for x in a.cell.split("x")]
        if len(parts) == 3:
            o, m, s = parts
            rows = [r for r in rows
                    if r.get("offering") == o and r.get("motion") == m and r.get("stage") == s]
        elif len(parts) == 2:
            rows = [r for r in rows if r.get("cell") == a.cell]
        else:
            sys.exit('--cell takes "offering x motion" or "offering x motion x stage"')
        label = a.cell
    else:
        rows = [r for r in rows if r.get("industry") == a.industry]
        label = a.industry
    if not rows:
        sys.exit("no posts for %r. Try one of: %s"
                 % (label, ", ".join(sorted({str(r.get("cell")) for r in d["posts"]}))))

    companies = {r["name"] for r in rows}
    if len(companies) < 3:
        print("**%d companies in this cohort.** Below the three-company floor this study uses "
              "everywhere else, so what follows describes those companies rather than the "
              "cohort. Read it as an example, not a benchmark.\n" % len(companies))

    rate, n_co = cadence_of(rows)
    per_week = a.per_week or (rate or 3.0)
    total = max(1, int(round(per_week * a.weeks)))

    counts = Counter(r["label"] for r in rows if r["label"] != "unclear")
    n = sum(counts.values())
    shares = {k: v / n for k, v in counts.items()}

    print("=" * 78)
    print("%s  -  %d weeks, %d slots" % (label.upper(), a.weeks, total))
    print("=" * 78)
    print("%d posts from %d companies. Measured cadence %.1f posts/week (from %d companies "
          "with a readable span)." % (n, len(companies), per_week, n_co))
    if a.deviate:
        floor = 0.10
        have = sum(shares.get(k, 0.0) for k in DECISION)
        if have < floor:
            need = floor - have
            donors = {k: v for k, v in shares.items() if k not in DECISION}
            pool = sum(donors.values())
            shares = {k: (v - need * (v / pool) if k in donors else v) for k, v in shares.items()}
            for k in DECISION:
                shares[k] = shares.get(k, 0.0) + need * (
                    0.5 if all(shares.get(j, 0) == 0 for j in DECISION) else
                    (shares.get(k, 0.0) / have if have else 0.5))
            # normalise: the proportional top-up above can drift by a fraction of a percent
            s = sum(shares.values())
            shares = {k: v / s for k, v in shares.items()}
            print("**--deviate**: requirements + consensus raised from %.1f%% to %.0f%% of "
                  "slots, taken proportionally from everything else. Whole slots round up, so a "
                  "short calendar can land a point or two above the floor."
                  % (100 * have, 100 * floor))
        else:
            print("**--deviate**: this cohort already publishes %.1f%% decision-stage content, "
                  "above the 10%% floor. Mix unchanged." % (100 * have))
    print()

    alloc = largest_remainder(shares, total)
    alloc = {k: v for k, v in alloc.items() if v > 0}

    print("%-14s %6s %8s   %-12s %-12s %-11s %s"
          % ("job", "slots", "share", "format", "opening", "aspect", "measured at"))
    print("-" * 92)
    for k in JOBS + OTHER:
        if k not in alloc:
            continue
        fmt, op, asp, note = BEST_SHAPE.get(k, (None, None, None, ""))
        print("%-14s %6d %7.0f%%   %-12s %-12s %-11s %s"
              % (k, alloc[k], 100.0 * alloc[k] / total,
                 fmt or "-", op or "-", asp or "-", note))
    print("-" * 92)
    print("%-14s %6d" % ("TOTAL", sum(alloc.values())))

    # --- the schedule --------------------------------------------------------------------------
    print("\nOne way to lay that out. Slots are spread so no two of the same job land adjacent;")
    print("the days carry no measured effect (Mon-Thu 1.00-1.04, Fri 0.94) and are only a shape.\n")
    queue = []
    for k in sorted(alloc, key=lambda x: -alloc[x]):
        queue.extend([k] * alloc[k])
    # interleave: take from the largest remaining pile each time
    spread, piles = [], Counter(queue)
    last = None
    while sum(piles.values()):
        pick = max((k for k in piles if piles[k] and k != last), key=lambda k: piles[k],
                   default=None)
        if pick is None:
            pick = max(piles, key=lambda k: piles[k])
        spread.append(pick)
        piles[pick] -= 1
        if piles[pick] == 0:
            del piles[pick]
        last = pick

    i = 0
    for w in range(a.weeks):
        this_week = spread[i:i + int(round(total / float(a.weeks)))]
        i += len(this_week)
        if not this_week:
            continue
        print("week %d" % (w + 1))
        for j, job in enumerate(this_week):
            fmt, op, asp, _ = BEST_SHAPE.get(job, (None, None, None, ""))
            # a cohort publishing more than five times a week doubles up on a day rather than
            # inventing a sixth one; saying so beats printing Mon twice and looking like a bug
            day = DAYS[j % len(DAYS)] + ("" if j < len(DAYS) else "*")
            print("   %-5s %-14s %-12s %s" % (day, job, fmt or "-", asp or ""))
        if len(this_week) > len(DAYS):
            print("   * second post that day -- this cohort publishes %.1f times a week"
                  % per_week)
        print()

    print("**What this does not decide.** Which pain each slot argues, whether the claim in it can")
    print("be published, and whether the post should exist at all. That is what a profile and")
    print("`engine/decision/` are for; this only fixes how many of each kind and in what shape.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
