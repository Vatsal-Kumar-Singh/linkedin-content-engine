#!/usr/bin/env python3
"""Rhythm and shape: how often these companies post, when, and how the text is built.

    python research/classify_posts.py --dump research/findings.json
    python research/analyse_cadence.py

Reads `research/raw/` for text and timestamps and `findings.json` for the labels, so it needs the
scrape on disk. Costs nothing to re-run.

---

## Why cadence is measurable at all from a capped scrape

Each company was pulled to a cap of 50 posts, so the **span** of those posts is the measurement:
a company posting five times a week fills 50 slots in ten weeks, one posting weekly takes a year.
Posts per week is therefore `n / weeks_spanned`, and it is comparable across companies even though
the post counts are not.

**A company that did not reach the cap is a different measurement** and is marked. Its span is its
whole visible history rather than a recent window, so a long quiet stretch drags its rate down in
a way the capped companies' rates cannot show.

## Why "best day to post" is not in this file

It would be easy to print, and it would be close to meaningless: day-of-week effects are
confounded with what gets published on which day. Companies put events on Mondays and Fridays and
long-form on Tuesdays, so a day ranking is mostly a content ranking wearing a calendar. The
day table below is printed **with the label mix beside it** for that reason.
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


# ==================================================================================================
# Text shape. Each of these is a structural fact about the post, not a judgement about it, so it
# can be counted rather than read. Anything that needed reading is already in the labels.
# ==================================================================================================
PATTERNS = {
    "opens on a question": lambda h, t: h.rstrip().endswith("?"),
    "opens on a number": lambda h, t: bool(re.match(r"^\W*\d", h)) or bool(
        re.search(r"\b\d+(\.\d+)?\s?(%|x\b|percent)", h, re.I)),
    "opens on 'we'": lambda h, t: bool(re.match(r"^\W*(we|our)\b", h, re.I)),
    "opens on 'you/your'": lambda h, t: bool(re.match(r"^\W*(you|your)\b", h, re.I)),
    "addresses 'you' anywhere": lambda h, t: bool(re.search(r"\byou\b|\byour\b", t, re.I)),
    "has a stat in the body": lambda h, t: bool(
        re.search(r"\b\d+(\.\d+)?\s?(%|x\b)|\b\d[\d,]{2,}\b", t)),
    "names a company (Cap Case)": lambda h, t: bool(
        re.search(r"\b[A-Z][a-z]+\s(?:[A-Z][a-z]+|[A-Z]{2,})\b", t)),
    "link in comments": lambda h, t: bool(re.search(r"link.{0,12}(in|the).{0,4}comment", t, re.I)),
    "explicit CTA verb": lambda h, t: bool(re.search(
        r"\b(register|sign up|save your (seat|spot)|download|read more|learn more|book|rsvp|"
        r"apply|watch|join us|get your|try it)\b", t, re.I)),
    "bulleted or listed": lambda h, t: len(re.findall(r"(?m)^\s*[•▪→➡\-✓✅▶⭐\U0001F539]", t)) >= 2,
    "uses emoji": lambda h, t: bool(re.search(
        r"[\U0001F300-\U0001FAFF☀-➿⬀-⯿]", t)),
    "has hashtags": lambda h, t: bool(re.search(r"(?:^|\s)#\w+", t)),
    "quotes somebody": lambda h, t: bool(re.search(r"[“\"][^”\"]{25,}[”\"]", t)),
}


def head_of(text):
    """The first line, which is all most readers see before the fold."""
    for line in (text or "").splitlines():
        if line.strip():
            return line.strip()
    return (text or "")[:120]


def load():
    by_id = {}
    for path in sorted(glob.glob(os.path.join(HERE, "raw", "*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        for p in d.get("posts") or []:
            if (p.get("header") or {}).get("linkedinUrl"):
                continue
            pid = str(p.get("id") or "")
            if pid:
                by_id[pid] = (d["company"], p)
    return by_id


def pct(a, b):
    return (100.0 * a / b) if b else 0.0


def band_table(rows, keyfn, title, min_n):
    g = defaultdict(list)
    for r in rows:
        k = keyfn(r)
        if k is not None:
            g[k].append(r)
    tot = sum(len(v) for v in g.values())
    print("\n=== %s ===" % title)
    print("%-30s %6s %7s %9s" % ("", "n", "share", "median x"))
    for k, rs in sorted(g.items(), key=lambda kv: -len(kv[1])):
        rel = [r["rel"] for r in rs if r.get("rel") is not None]
        if len(rs) < min_n:
            print("%-30s %6d %6.1f%%   TOO FEW" % (str(k)[:30], len(rs), pct(len(rs), tot)))
            continue
        print("%-30s %6d %6.1f%% %8.2f"
              % (str(k)[:30], len(rs), pct(len(rs), tot),
                 statistics.median(rel) if rel else 0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", default=os.path.join(HERE, "findings.json"))
    ap.add_argument("--min-n", type=int, default=25)
    a = ap.parse_args()

    f = json.load(open(a.findings, encoding="utf-8"))
    raw = load()
    thin = set(f["thin"])
    rows = []
    for r in f["posts"]:
        got = raw.get(r["id"])
        if not got:
            continue
        _, post = got
        text = post.get("content") or ""
        rows.append(dict(r, text=text, head=head_of(text)))
    print("%d labelled posts matched to their text." % len(rows))

    # --- cadence ------------------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("HOW OFTEN THEY PUBLISH")
    print("=" * 78)
    spans = {}
    for path in sorted(glob.glob(os.path.join(HERE, "raw", "*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        c = d["company"]
        if c["name"] in thin:
            continue
        ds = sorted(((p.get("postedAt") or {}).get("date") or "")[:10]
                    for p in d.get("posts") or [] if (p.get("postedAt") or {}).get("date"))
        ds = [x for x in ds if x]
        if len(ds) < 10:
            continue
        d0 = dt.date.fromisoformat(ds[0])
        d1 = dt.date.fromisoformat(ds[-1])
        weeks = max(1.0, (d1 - d0).days / 7.0)
        spans[c["name"]] = {"n": len(ds), "weeks": weeks, "per_week": len(ds) / weeks,
                            "capped": len(d.get("posts") or []) >= 50,
                            **{k: c[k] for k in ("offering", "motion", "stage", "buyer")}}

    capped = [v for v in spans.values() if v["capped"]]
    print("\n%d companies, %d of them hit the 50-post cap (their span is a true recent window)."
          % (len(spans), len(capped)))
    allr = sorted(v["per_week"] for v in spans.values())
    print("posts per week across all of them: median %.1f, range %.1f to %.1f"
          % (statistics.median(allr), allr[0], allr[-1]))

    for key in ("offering", "motion", "stage", "buyer"):
        print("\n  by %s" % key)
        b = defaultdict(list)
        for v in spans.values():
            b[v[key]].append(v["per_week"])
        for k, v in sorted(b.items(), key=lambda kv: -statistics.median(kv[1])):
            print("     %-14s %2d companies, median %4.1f posts/week  (range %.1f-%.1f)"
                  % (k, len(v), statistics.median(v), min(v), max(v)))

    fastest = sorted(spans.items(), key=lambda kv: -kv[1]["per_week"])
    print("\n  fastest five")
    for n, v in fastest[:5]:
        print("     %-24s %4.1f/week  (%d posts over %.0f weeks)" % (n, v["per_week"], v["n"], v["weeks"]))
    print("  slowest five")
    for n, v in fastest[-5:]:
        print("     %-24s %4.1f/week  (%d posts over %.0f weeks)" % (n, v["per_week"], v["n"], v["weeks"]))

    # --- does posting more cost you per-post engagement? ---------------------------------------
    print("\n  Does publishing more cost engagement per post?")
    print("  Each company's own median is 1.00 by construction, so this cannot be answered by")
    print("  comparing medians. What CAN be asked is whether high-cadence companies have a")
    print("  flatter spread -- fewer posts that break out well above their own baseline:")
    by_name = defaultdict(list)
    for r in rows:
        if r.get("rel") is not None:
            by_name[r["name"]].append(r["rel"])
    fast = [n for n, v in spans.items() if v["per_week"] >= statistics.median(allr)]
    slow = [n for n, v in spans.items() if v["per_week"] < statistics.median(allr)]
    for label, names in (("above median cadence", fast), ("below median cadence", slow)):
        vals = [x for n in names for x in by_name.get(n, [])]
        if not vals:
            continue
        breakout = pct(sum(1 for x in vals if x >= 2.0), len(vals))
        print("     %-22s %d companies, %d posts, %.0f%% of posts doubled their own median"
              % (label, len(names), len(vals), breakout))

    # --- day of week --------------------------------------------------------------------------
    print("\n  By day of week, with the label mix beside it, because a day ranking is mostly a")
    print("  content ranking wearing a calendar:")
    byday = defaultdict(list)
    for r in rows:
        try:
            byday[dt.date.fromisoformat(r["date"]).weekday()].append(r)
        except Exception:
            pass
    print("     %-5s %6s %9s   %s" % ("day", "n", "median x", "most published that day"))
    for i in range(7):
        rs = byday.get(i, [])
        if len(rs) < a.min_n:
            print("     %-5s %6d   TOO FEW" % (DOW[i], len(rs)))
            continue
        rel = [r["rel"] for r in rs if r.get("rel") is not None]
        top = Counter(r["label"] for r in rs).most_common(2)
        print("     %-5s %6d %8.2f    %s"
              % (DOW[i], len(rs), statistics.median(rel),
                 ", ".join("%s %.0f%%" % (k, pct(v, len(rs))) for k, v in top)))

    # --- text shape ---------------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("HOW THE TEXT IS BUILT")
    print("=" * 78)
    print("\nEach row is a structural fact counted from the post, not a judgement about it.")
    print("%-32s %6s %7s %9s %9s" % ("", "n", "share", "median x", "vs rest"))
    base = {r["id"]: r["rel"] for r in rows if r.get("rel") is not None}
    allvals = sorted(base.values())
    for name, fn in PATTERNS.items():
        hit = [r for r in rows if fn(r["head"], r["text"])]
        miss = [r for r in rows if r not in hit] if False else None
        hv = [r["rel"] for r in hit if r.get("rel") is not None]
        ids = {r["id"] for r in hit}
        mv = [v for k, v in base.items() if k not in ids]
        if len(hv) < a.min_n:
            print("%-32s %6d %6.1f%%   TOO FEW" % (name, len(hit), pct(len(hit), len(rows))))
            continue
        hm, mm = statistics.median(hv), (statistics.median(mv) if mv else 0)
        print("%-32s %6d %6.1f%% %8.2f %8s"
              % (name, len(hit), pct(len(hit), len(rows)), hm,
                 ("%+.0f%%" % (100 * (hm - mm) / mm)) if mm else "-"))

    # --- opening line length -------------------------------------------------------------------
    def hb(r):
        w = len(r["head"].split())
        return "hook 1-6 words" if w <= 6 else ("hook 7-14" if w <= 14 else
                                                ("hook 15-25" if w <= 25 else "hook 26+"))
    band_table(rows, hb, "first line length (all most readers see)", a.min_n)

    # --- hashtags -------------------------------------------------------------------------------
    def hc(r):
        n = len(re.findall(r"(?:^|\s)#\w+", r["text"]))
        return "0 hashtags" if n == 0 else ("1-3" if n <= 3 else ("4-7" if n <= 7 else "8+"))
    band_table(rows, hc, "hashtag count", a.min_n)

    # --- structure by job --------------------------------------------------------------------
    print("\n=== which patterns each buying job uses (share of that job's posts) ===")
    picks = ["opens on a question", "opens on a number", "has a stat in the body",
             "addresses 'you' anywhere", "bulleted or listed", "link in comments"]
    print("%-16s %s" % ("", "".join("%14s" % p[:13] for p in picks)))
    for lab in ["problem", "exploration", "requirements", "selection", "validation", "consensus"]:
        rs = [r for r in rows if r["label"] == lab]
        if len(rs) < a.min_n:
            continue
        print("%-16s %s" % (lab, "".join(
            "%13.0f%%" % pct(sum(1 for r in rs if PATTERNS[p](r["head"], r["text"])), len(rs))
            for p in picks)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
