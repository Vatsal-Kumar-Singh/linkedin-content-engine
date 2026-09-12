#!/usr/bin/env python3
"""What formats and lengths these companies use, and what the feed rewards.

    python research/classify_posts.py --dump research/findings.json
    python research/analyse_format.py research/findings.json

---

## The one number that would be wrong if this pooled companies

Engagement here is **always a ratio to the post's own company's median**, never a raw count.
Figma's median post outscores a four-person startup's best one, so a pooled median ranks the
audience and says nothing about the post. A ratio of 1.40 means "40% above what this company
normally gets", which is a statement about the post shape and comparable across companies.

**A cell below `--min-n` posts is printed as TOO FEW and never given a median.** Three posts is
an anecdote, and an anecdote with a decimal point on it looks exactly like a measurement.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import Counter, defaultdict

JOBS = ["problem", "exploration", "requirements", "selection", "validation", "consensus"]
OTHER = ["recruitment", "culture", "event", "product-news", "csr"]
BANDS = [(0, 29), (30, 59), (60, 99), (100, 159), (160, 10_000)]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def band_of(w):
    for lo, hi in BANDS:
        if lo <= w <= hi:
            return "%d-%s" % (lo, hi if hi < 10_000 else "+")
    return None


def table(rows, keyfn, title, min_n, extra=None):
    g = defaultdict(list)
    for r in rows:
        k = keyfn(r)
        if k is not None:
            g[k].append(r)
    total = sum(len(v) for v in g.values())
    print("\n=== %s ===" % title)
    print("%-22s %6s %7s %9s %9s" % ("", "n", "share", "median x", "top-decile"))
    order = sorted(g.items(), key=lambda kv: -len(kv[1]))
    for k, rs in order:
        rel = sorted(r["rel"] for r in rs if r.get("rel") is not None)
        if len(rs) < min_n:
            print("%-22s %6d %6.1f%%   TOO FEW (under %d)" % (str(k)[:22], len(rs),
                                                              100.0 * len(rs) / total, min_n))
            continue
        med = statistics.median(rel) if rel else 0
        top = (sum(1 for x in rel if x >= 2.0) / len(rel) * 100) if rel else 0
        print("%-22s %6d %6.1f%% %8.2f %8.0f%%" % (str(k)[:22], len(rs),
                                                   100.0 * len(rs) / total, med, top))
    if extra:
        extra(g)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("findings")
    ap.add_argument("--min-n", type=int, default=15)
    a = ap.parse_args()
    d = json.load(open(a.findings, encoding="utf-8"))
    rows = d["posts"]
    companies = d["companies"]

    print("%d posts across %d companies." % (len(rows), len({r["name"] for r in rows})))
    print("'median x' is the post's engagement against its OWN company's median, so 1.20 means")
    print("20%% better than that company's typical post. 'top-decile' is the share of posts that")
    print("at least doubled their company's median.")

    table(rows, lambda r: r["fmt"], "format: what gets used, and what it earns", a.min_n)
    table(rows, lambda r: band_of(r["words"]), "length in words", a.min_n)
    table(rows, lambda r: r["label"], "by label", a.min_n)
    table(rows, lambda r: r["tier"], "by funnel tier (buying jobs only)", a.min_n)

    # --- format by offering, because hardware and software do not behave the same -------------
    print("\n=== format mix by offering (share of that offering's posts) ===")
    offs = sorted({r["offering"] for r in rows})
    fmts = ["text", "link", "image", "multi-image", "video"]
    print("%-14s %s" % ("", "".join("%13s" % f for f in fmts)))
    for off in offs:
        rs = [r for r in rows if r["offering"] == off]
        c = Counter(r["fmt"] for r in rs)
        print("%-14s %s" % (off, "".join("%12.0f%%" % (100.0 * c[f] / len(rs)) for f in fmts)))

    print("\n=== format mix by motion ===")
    mots = sorted({r["motion"] for r in rows})
    print("%-14s %s" % ("", "".join("%13s" % f for f in fmts)))
    for m in mots:
        rs = [r for r in rows if r["motion"] == m]
        c = Counter(r["fmt"] for r in rs)
        print("%-14s %s" % (m, "".join("%12.0f%%" % (100.0 * c[f] / len(rs)) for f in fmts)))

    # --- the format x job question -------------------------------------------------------------
    print("\n=== which format each buying job gets published in (row = 100%) ===")
    print("%-16s %s" % ("", "".join("%13s" % f for f in fmts)))
    for lab in JOBS + OTHER:
        rs = [r for r in rows if r["label"] == lab]
        if len(rs) < a.min_n:
            continue
        c = Counter(r["fmt"] for r in rs)
        print("%-16s %s" % (lab, "".join("%12.0f%%" % (100.0 * c[f] / len(rs)) for f in fmts)))

    # --- posting volume ------------------------------------------------------------------------
    print("\n=== how much each cohort publishes (originals per company over the window) ===")
    for key in ("offering", "motion", "stage"):
        buckets = defaultdict(list)
        for name, c in companies.items():
            if name in set(d["thin"]):
                continue
            buckets[c[key]].append(c["originals"])
        print("  %s" % key)
        for k, v in sorted(buckets.items()):
            print("     %-14s %d companies, median %.0f originals, range %d-%d"
                  % (k, len(v), statistics.median(v), min(v), max(v)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
