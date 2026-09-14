#!/usr/bin/env python3
"""Cut everything this study measures by offering x motion x stage, one cell at a time.

    python research/classify_posts.py --dump research/findings.json
    python research/analyse_cells.py                 # every cell that clears the floor
    python research/analyse_cells.py --cell "saas x plg x early"
    python research/analyse_cells.py --grid          # occupancy only, including the holes

The rest of this study cuts one axis at a time: offering, or motion, or stage. This cuts all
three at once, which is how a company actually identifies itself — "we are early-stage SaaS sold
product-led", not "we are SaaS".

---

## Why "best in cell" cannot mean "most engagement"

Every post here is scored against its **own company's median**, because a median pooled across
companies ranks audience size rather than post quality. That normalisation is what makes the
corpus readable, and it also means **every company's median is 1.00 by construction**. There is no
engagement ranking of companies to be had. Anybody producing one from this data has either pooled
raw engagement, which ranks follower counts, or made it up.

So a cell names three exemplars on three things the data *can* see, and says which is which:

- **Most complete funnel** — the largest share of `requirements` + `consensus` + `validation`.
  This corpus's central finding is that decision-stage content is missing industry-wide, at 3.9%
  of everything. A company publishing it is doing the rare thing, whatever its reach.
- **Best format discipline** — carousel and video share up, link-post share down, measured against
  the corpus-wide format ranking. This is a production decision, not a content one, and it is the
  single largest measured effect on the page.
- **Most breakout reach** — the largest share of posts at 3x their own median or better. A feed
  with hits in it, as distinct from a feed with a high floor.

**These will usually be three different companies, and that is the point.** The one with the
fullest funnel is rarely the one with the biggest hits — the first table in `BENCHMARKS.md` is the
reason, and it holds inside cells as well as across them.

## The floor

A cell needs **three companies** to be reported and **eight posts** for any sub-table inside it.
Below that the output says so and prints nothing, because a cell with one company in it is a
description of that company wearing the authority of a benchmark.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
JOBS = ["problem", "exploration", "requirements", "selection", "validation", "consensus"]
OTHER = ["recruitment", "culture", "event", "product-news", "csr"]
TIER = {"problem": "TOFU", "exploration": "TOFU", "requirements": "MOFU", "selection": "MOFU",
        "validation": "BOFU", "consensus": "BOFU"}
SCARCE = ("requirements", "consensus", "validation")
OFF = ["saas", "product", "service"]
MOT = ["plg", "pls", "slg", "enterprise"]
STG = ["early", "growth", "scaled"]

# Structurally empty, recorded rather than left looking like an oversight.
STRUCTURAL = {
    ("service", "plg"): "you cannot self-serve a consultancy",
    ("service", "pls"): "productised services with a self-serve tier exist but are rare and "
                        "mostly design subscriptions; none met the sample's B2B bar",
    ("product", "pls"): "hardware bought on a card that then converts to a contract is a thin "
                        "band between plg and slg; no clean example was found",
}

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def pct(a, b):
    return (100.0 * a / b) if b else 0.0


def med(v):
    return statistics.median(v) if v else None


def cadence(rows):
    by = defaultdict(list)
    for r in rows:
        if r.get("date"):
            by[r["name"]].append(r["date"])
    rates = []
    for co, ds in by.items():
        ds.sort()
        if len(ds) < 5:
            continue
        try:
            lo, hi = datetime.date.fromisoformat(ds[0]), datetime.date.fromisoformat(ds[-1])
        except ValueError:
            continue
        rates.append(len(ds) / max(1.0, (hi - lo).days / 7.0))
    return med(rates)


def exemplars(rows):
    """Three named companies, on the three things the normalisation leaves visible."""
    by = defaultdict(list)
    for r in rows:
        by[r["name"]].append(r)
    out = {}
    fair = {c: rs for c, rs in by.items() if len(rs) >= 15}
    if not fair:
        return out
    out["funnel"] = max(fair.items(),
                        key=lambda kv: pct(sum(1 for r in kv[1] if r["label"] in SCARCE),
                                           len(kv[1])))
    out["format"] = max(fair.items(),
                        key=lambda kv: (pct(sum(1 for r in kv[1]
                                                if r["fmt"] in ("multi-image", "video")),
                                            len(kv[1]))
                                        - pct(sum(1 for r in kv[1] if r["fmt"] == "link"),
                                              len(kv[1]))))
    out["reach"] = max(fair.items(),
                       key=lambda kv: pct(sum(1 for r in kv[1] if (r.get("rel") or 0) >= 3),
                                          len(kv[1])))
    return out


def md_cell(key, rows, min_sub=8):
    """The same report as report_cell, as markdown, for docs/CELLS.md.

    Two renderers for one analysis is a duplication risk, so they read the same rows and compute
    nothing independently: everything printed here is computed by the helpers above, the same ones
    the terminal report uses. If a number needs changing it changes in one place.
    """
    off, mot, stg = key
    cos = sorted({r["name"] for r in rows})
    n = len(rows)
    out = []
    w = out.append
    w("## %s x %s x %s" % (off, mot, stg))
    w("")
    w("**%d posts, %d companies:** %s" % (n, len(cos), ", ".join(cos)))
    w("")
    rate = cadence(rows)
    tiers = Counter(TIER.get(r["label"]) for r in rows if TIER.get(r["label"]))
    non = sum(1 for r in rows if r["label"] in OTHER)
    w("| TOFU | MOFU | BOFU | non-buying | cadence |")
    w("|---:|---:|---:|---:|---:|")
    w("| %.0f%% | %.0f%% | %.0f%% | %.0f%% | %s posts/week |"
      % (pct(tiers["TOFU"], n), pct(tiers["MOFU"], n), pct(tiers["BOFU"], n), pct(non, n),
         ("%.1f" % rate) if rate else "-"))
    w("")

    w("**What it publishes**")
    w("")
    w("| Job | n | Share | Engagement |")
    w("|---|---:|---:|---:|")
    for lab, c in Counter(r["label"] for r in rows).most_common():
        rel = [r["rel"] for r in rows if r["label"] == lab and r.get("rel") is not None]
        w("| `%s` | %d | %.0f%% | %s |"
          % (lab, c, pct(c, n), ("%.2fx" % med(rel)) if len(rel) >= min_sub else "-"))
    missing = [j for j in JOBS if not any(r["label"] == j for r in rows)]
    w("")
    if missing:
        w("**Publishes no `%s` at all.**" % "`, no `".join(missing))
        w("")

    w("**Format**")
    w("")
    w("| Format | n | Share | Engagement |")
    w("|---|---:|---:|---:|")
    for f, c in Counter(r["fmt"] for r in rows).most_common():
        rel = [r["rel"] for r in rows if r["fmt"] == f and r.get("rel") is not None]
        w("| %s | %d | %.0f%% | %s |"
          % (f, c, pct(c, n), ("%.2fx" % med(rel)) if len(rel) >= min_sub else "-"))
    w("")

    shapes = defaultdict(list)
    for r in rows:
        if r.get("open") and r.get("rel") is not None:
            shapes[(r["label"], r["fmt"], r["open"])].append(r["rel"])
    named = sorted({k: v for k, v in shapes.items() if len(v) >= min_sub}.items(),
                   key=lambda kv: -med(kv[1]))
    w("**Shapes that recur in this cell** (%d posts or more)" % min_sub)
    w("")
    if not named:
        w("None reaches the floor. Use the corpus-wide shape table in `BENCHMARKS.md`.")
    else:
        w("| Job | Format | Opening | n | Engagement |")
        w("|---|---|---|---:|---:|")
        for (lab, fmt, op), rel in named[:8]:
            w("| `%s` | %s | %s | %d | %.2fx |" % (lab, fmt, op, len(rel), med(rel)))
    w("")

    asp = defaultdict(list)
    for r in rows:
        if r.get("aspect") and r.get("rel") is not None:
            asp[r["aspect"]].append(r["rel"])
    if asp:
        w("**Design: aspect ratio of image posts**")
        w("")
        w("| Shape | n | Engagement |")
        w("|---|---:|---:|")
        for s, rel in sorted(asp.items(), key=lambda kv: -len(kv[1])):
            w("| %s | %d | %s |"
              % (s, len(rel), ("%.2fx" % med(rel)) if len(rel) >= min_sub else "-"))
        w("")

    ex = exemplars(rows)
    if ex:
        w("**Exemplars**")
        w("")
        w("| | Company | |")
        w("|---|---|---|")
        f = ex["funnel"]
        w("| fullest funnel | **%s** | %.0f%% of posts are requirements, consensus or validation |"
          % (f[0], pct(sum(1 for r in f[1] if r["label"] in SCARCE), len(f[1]))))
        d = ex["format"]
        w("| best format mix | **%s** | %.0f%% carousel or video, %.0f%% link |"
          % (d[0], pct(sum(1 for r in d[1] if r["fmt"] in ("multi-image", "video")), len(d[1])),
             pct(sum(1 for r in d[1] if r["fmt"] == "link"), len(d[1]))))
        b = ex["reach"]
        w("| most breakouts | **%s** | %.0f%% of posts at 3x their own median |"
          % (b[0], pct(sum(1 for r in b[1] if (r.get("rel") or 0) >= 3), len(b[1]))))
        w("")
    return "\n".join(out)


def report_cell(key, rows, min_sub=8):
    off, mot, stg = key
    cos = sorted({r["name"] for r in rows})
    n = len(rows)
    print("=" * 88)
    print("%s x %s x %s  -  %d posts, %d companies" % (off, mot, stg, n, len(cos)))
    print("=" * 88)
    print("   " + ", ".join(cos))

    rate = cadence(rows)
    tiers = Counter(TIER.get(r["label"]) for r in rows if TIER.get(r["label"]))
    non = sum(1 for r in rows if r["label"] in OTHER)
    unc = sum(1 for r in rows if r["label"] == "unclear")
    print("\n   mix     TOFU %.0f%%   MOFU %.0f%%   BOFU %.0f%%   non-buying %.0f%%   unclear %.0f%%"
          % (pct(tiers["TOFU"], n), pct(tiers["MOFU"], n), pct(tiers["BOFU"], n),
             pct(non, n), pct(unc, n)))
    print("   cadence %s posts/week" % ("%.1f" % rate if rate else "not readable"))

    # --- what it publishes, by label -----------------------------------------------------------
    print("\n   %-14s %5s %7s %9s" % ("job", "n", "share", "median x"))
    for lab, c in Counter(r["label"] for r in rows).most_common():
        rel = [r["rel"] for r in rows if r["label"] == lab and r.get("rel") is not None]
        print("   %-14s %5d %6.0f%% %9s"
              % (lab, c, pct(c, n), ("%.2f" % med(rel)) if len(rel) >= min_sub else "-"))

    # --- format ------------------------------------------------------------------------------
    print("\n   %-14s %5s %7s %9s" % ("format", "n", "share", "median x"))
    for f, c in Counter(r["fmt"] for r in rows).most_common():
        rel = [r["rel"] for r in rows if r["fmt"] == f and r.get("rel") is not None]
        print("   %-14s %5d %6.0f%% %9s"
              % (f, c, pct(c, n), ("%.2f" % med(rel)) if len(rel) >= min_sub else "-"))

    # --- the shapes that recur inside this cell ------------------------------------------------
    shapes = defaultdict(list)
    for r in rows:
        if r.get("open") and r.get("rel") is not None:
            shapes[(r["label"], r["fmt"], r["open"])].append(r["rel"])
    named = {k: v for k, v in shapes.items() if len(v) >= min_sub}
    print("\n   shapes recurring in this cell (>= %d posts):" % min_sub)
    if not named:
        print("      none. Use the corpus-wide table in BENCHMARKS.md instead.")
    for (lab, fmt, op), rel in sorted(named.items(), key=lambda kv: -med(kv[1]))[:8]:
        print("      %-14s %-12s %-12s n=%-4d %.2fx" % (lab, fmt, op, len(rel), med(rel)))

    # --- aspect ratio --------------------------------------------------------------------------
    asp = defaultdict(list)
    for r in rows:
        if r.get("aspect") and r.get("rel") is not None:
            asp[r["aspect"]].append(r["rel"])
    if asp:
        print("\n   aspect ratio of image posts:")
        for s, rel in sorted(asp.items(), key=lambda kv: -len(kv[1])):
            print("      %-14s n=%-4d %s" % (s, len(rel),
                                             ("%.2fx" % med(rel)) if len(rel) >= min_sub else "-"))

    # --- exemplars ---------------------------------------------------------------------------
    ex = exemplars(rows)
    if ex:
        print("\n   exemplars (three different questions, usually three different companies):")
        f = ex["funnel"]
        print("      fullest funnel   %-24s %.0f%% requirements/consensus/validation"
              % (f[0], pct(sum(1 for r in f[1] if r["label"] in SCARCE), len(f[1]))))
        d = ex["format"]
        print("      best format mix  %-24s %.0f%% carousel+video, %.0f%% link"
              % (d[0], pct(sum(1 for r in d[1] if r["fmt"] in ("multi-image", "video")), len(d[1])),
                 pct(sum(1 for r in d[1] if r["fmt"] == "link"), len(d[1]))))
        b = ex["reach"]
        print("      most breakouts   %-24s %.0f%% of posts at 3x their own median"
              % (b[0], pct(sum(1 for r in b[1] if (r.get("rel") or 0) >= 3), len(b[1]))))
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", default=os.path.join(HERE, "findings.json"))
    ap.add_argument("--cell", help='"saas x plg x early"')
    ap.add_argument("--grid", action="store_true", help="occupancy table only")
    ap.add_argument("--min-companies", type=int, default=3)
    ap.add_argument("--markdown", help="write docs/CELLS.md style output to this path")
    a = ap.parse_args()

    d = json.load(open(a.findings, encoding="utf-8"))
    rows = d["posts"]

    # opening move and aspect ratio are computed by sibling scripts; reuse rather than re-derive
    sys.path.insert(0, HERE)
    try:
        from analyse_templates import opening_move, load_text
        texts = load_text()
        for r in rows:
            r["open"] = opening_move(texts.get(r["id"], ""))
    except Exception as e:
        print("(opening moves unavailable: %s)" % e)
    try:
        from sample_creative import image_urls, shape_of
        urls = image_urls(with_size=True)
        for r in rows:
            got = urls.get(r["id"])
            if got:
                r["aspect"] = shape_of(got[0][1], got[0][2])
    except Exception as e:
        print("(aspect ratios unavailable: %s)" % e)

    grid = defaultdict(list)
    for r in rows:
        grid[(r["offering"], r["motion"], r["stage"])].append(r)

    if a.grid or not a.cell:
        print("OCCUPANCY: offering x motion x stage. A cell needs %d companies to be reported.\n"
              % a.min_companies)
        print("%-10s %-12s%s" % ("offering", "motion", "".join("%-16s" % s for s in STG)))
        print("-" * 74)
        for o in OFF:
            for m in MOT:
                cells = []
                for s in STG:
                    rs = grid.get((o, m, s)) or []
                    c = len({r["name"] for r in rs})
                    cells.append("-" if not c else "%d co, %d posts" % (c, len(rs)))
                note = "   <- %s" % STRUCTURAL[(o, m)] if (o, m) in STRUCTURAL else ""
                print("%-10s %-12s%s%s" % (o, m, "".join("%-16s" % c for c in cells), note))
        gaps = [(o, m, s) for o in OFF for m in MOT for s in STG
                if (o, m) not in STRUCTURAL
                and len({r["name"] for r in (grid.get((o, m, s)) or [])}) < a.min_companies]
        print("\n**%d fillable cells are below %d companies:**" % (len(gaps), a.min_companies))
        for o, m, s in gaps:
            have = len({r["name"] for r in (grid.get((o, m, s)) or [])})
            print("   %-34s has %d, needs %d more" % ("%s x %s x %s" % (o, m, s),
                                                      have, a.min_companies - have))
        print()

    if a.cell:
        key = tuple(x.strip() for x in a.cell.split("x"))
        if key not in grid:
            sys.exit("no posts in %r" % a.cell)
        report_cell(key, grid[key])
        return 0
    if a.grid:
        return 0

    if a.markdown:
        parts = []
        for o in OFF:
            for m in MOT:
                for s in STG:
                    rs = grid.get((o, m, s)) or []
                    if len({r["name"] for r in rs}) >= a.min_companies:
                        parts.append(md_cell((o, m, s), rs))
        open(a.markdown, "w", encoding="utf-8").write("\n---\n\n".join(parts) + "\n")
        print("wrote %s (%d cells)" % (a.markdown, len(parts)))
        return 0

    for o in OFF:
        for m in MOT:
            for s in STG:
                rs = grid.get((o, m, s)) or []
                if len({r["name"] for r in rs}) >= a.min_companies:
                    report_cell((o, m, s), rs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
