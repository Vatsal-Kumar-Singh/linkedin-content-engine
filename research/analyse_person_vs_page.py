#!/usr/bin/env python3
"""Set the named people beside the company pages they sit next to.

    python research/analyse_person_vs_page.py
    python research/analyse_person_vs_page.py --labels     # adds the buying-job split

Needs `research/raw/` and `research/raw_people/` on disk.

---

## What can and cannot be compared

**Composition compares cleanly.** What share of a feed is video, how long the posts are, how the
first line is built — none of that depends on audience size, so a person and a page can be set
side by side directly.

**Raw engagement does not compare across accounts**, because it mostly measures followers. The
one comparison that survives is **paired**: at the same company, in the same window, does the
named person's median post beat the page's? That is confounded by the two accounts' follower
counts and nothing here can remove that. It is still the closest thing to the decision the engine
actually has to make, which is whether a company's reach lives on its page or on its people.

**A person who only reshares is a finding, not a gap.** The scrape keeps both counts.
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

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def fmt_of(post):
    if post.get("postVideo"):
        return "video"
    n = len(post.get("postImages") or [])
    if n >= 2:
        return "multi-image"
    if n == 1:
        return "image"
    return "link" if re.search(r"https?://|lnkd\.in", post.get("content") or "") else "text"


def eng_of(post):
    e = post.get("engagement") or {}
    return float((e.get("likes") or 0) + (e.get("comments") or 0) + (e.get("shares") or 0))


# The headline the actor returns on every post ("Founder & CEO at Dub.co") is enough to tell a
# founder from a staff engineer, which turns out to matter more than person-versus-page does.
SENIORITY = [
    ("founder/CEO", r"\b(founder|co-?founder|chief executive|ceo|president)\b"),
    ("C-suite", r"\b(chief\s+\w+|cto|cmo|cro|cfo|coo|cpo|ciso|cdo)\b"),
    ("VP/Head/Director", r"\b(vp|vice president|head of|director|general manager|gm|partner)\b"),
]


def seniority_of(info):
    s = (info or "").lower()
    for label, pat in SENIORITY:
        if re.search(pat, s):
            return label
    return "individual contributor"


def head_of(text):
    for line in (text or "").splitlines():
        if line.strip():
            return line.strip()
    return (text or "")[:120]


def load_pages():
    out = {}
    for path in sorted(glob.glob(os.path.join(HERE, "raw", "*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        c = d["company"]
        posts = [p for p in (d.get("posts") or [])
                 if not (p.get("header") or {}).get("linkedinUrl")]
        if posts:
            out[c["slug"]] = {"company": c, "posts": posts}
    return out


def load_people():
    out = []
    for path in sorted(glob.glob(os.path.join(HERE, "raw_people", "*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        if not d.get("posts"):
            continue
        info = ""
        for post in d["posts"]:
            info = ((post.get("author") or {}).get("info") or "").strip()
            if info:
                break
        d["person"]["headline"] = info
        d["person"]["seniority"] = seniority_of(info)
        out.append(d)
    return out


def rows_from(posts, meta, kind):
    rows = []
    for p in posts:
        text = p.get("content") or ""
        rows.append({"kind": kind, "who": meta, "fmt": fmt_of(p), "words": len(text.split()),
                     "eng": eng_of(p), "head": head_of(text), "text": text,
                     "date": ((p.get("postedAt") or {}).get("date") or "")[:10]})
    return rows


def pct(a, b):
    return (100.0 * a / b) if b else 0.0


def dist(rows, keyfn, order=None):
    c = Counter(keyfn(r) for r in rows)
    n = len(rows)
    keys = order or sorted(c, key=lambda k: -c[k])
    return {k: pct(c.get(k, 0), n) for k in keys}


def side_by_side(title, left, right, keys, lname="page", rname="person"):
    print("\n=== %s ===" % title)
    print("%-22s %10s %10s %9s" % ("", lname, rname, "diff"))
    for k in keys:
        a, b = left.get(k, 0.0), right.get(k, 0.0)
        print("%-22s %9.1f%% %9.1f%% %+8.1f" % (str(k)[:22], a, b, b - a))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-posts", type=int, default=15)
    a = ap.parse_args()

    pages = load_pages()
    people = load_people()
    if not people:
        sys.exit("no people on disk. Run research/scrape_people.py first")

    prows, qrows = [], []
    for slug, v in pages.items():
        prows += rows_from(v["posts"], v["company"], "page")
    kept_people = [d for d in people if len(d["posts"]) >= a.min_posts]
    for d in kept_people:
        qrows += rows_from(d["posts"], d["person"], "person")

    print("%d pages (%d posts) against %d people (%d posts)."
          % (len(pages), len(prows), len(kept_people), len(qrows)))
    thin = [d for d in people if len(d["posts"]) < a.min_posts]
    if thin:
        print("\n%d people fell below the %d-post threshold and are reported, not counted:"
              % (len(thin), a.min_posts))
        for d in thin:
            print("   %-26s %2d own, %2d reshared   (%s)"
                  % ((d["person"].get("name") or d["person"]["slug"])[:26], d["n"],
                     d.get("n_reshared", 0), d["person"]["company"]))

    fmts = ["text", "link", "image", "multi-image", "video"]
    side_by_side("format mix", dist(prows, lambda r: r["fmt"]),
                 dist(qrows, lambda r: r["fmt"]), fmts)

    def wb(r):
        w = r["words"]
        return ("0-29" if w <= 29 else "30-59" if w <= 59 else "60-99" if w <= 99
                else "100-159" if w <= 159 else "160+")
    side_by_side("body length", dist(prows, wb), dist(qrows, wb),
                 ["0-29", "30-59", "60-99", "100-159", "160+"])

    def hb(r):
        w = len(r["head"].split())
        return "1-6" if w <= 6 else "7-14" if w <= 14 else "15-25" if w <= 25 else "26+"
    side_by_side("first line length", dist(prows, hb), dist(qrows, hb),
                 ["1-6", "7-14", "15-25", "26+"])

    PAT = {
        "opens on a question": lambda r: r["head"].rstrip().endswith("?"),
        "opens on 'we/our'": lambda r: bool(re.match(r"^\W*(we|our)\b", r["head"], re.I)),
        "opens on 'I/my'": lambda r: bool(re.match(r"^\W*(i|i'm|i've|my)\b", r["head"], re.I)),
        "says 'I' anywhere": lambda r: bool(re.search(r"\bI\b|\bmy\b", r["text"])),
        "says 'we' anywhere": lambda r: bool(re.search(r"\bwe\b|\bour\b", r["text"], re.I)),
        "has hashtags": lambda r: bool(re.search(r"(?:^|\s)#\w+", r["text"])),
        "uses emoji": lambda r: bool(re.search(
            r"[\U0001F300-\U0001FAFF☀-➿]", r["text"])),
        "explicit CTA verb": lambda r: bool(re.search(
            r"\b(register|sign up|download|read more|learn more|rsvp|apply|join us)\b",
            r["text"], re.I)),
        "link in comments": lambda r: bool(
            re.search(r"link.{0,12}(in|the).{0,4}comment", r["text"], re.I)),
    }
    print("\n=== how the text is built ===")
    print("%-22s %10s %10s %9s" % ("", "page", "person", "diff"))
    for name, fn in PAT.items():
        x, y = pct(sum(1 for r in prows if fn(r)), len(prows)), \
               pct(sum(1 for r in qrows if fn(r)), len(qrows))
        print("%-22s %9.1f%% %9.1f%% %+8.1f" % (name, x, y, y - x))

    # --- cadence ------------------------------------------------------------------------------
    def cadence(rows_by):
        out = []
        for key, rs in rows_by.items():
            ds = sorted(r["date"] for r in rs if r["date"])
            if len(ds) < 10:
                continue
            d0, d1 = dt.date.fromisoformat(ds[0]), dt.date.fromisoformat(ds[-1])
            out.append(len(ds) / max(1.0, (d1 - d0).days / 7.0))
        return out
    bypage, byperson = defaultdict(list), defaultdict(list)
    for r in prows:
        bypage[r["who"]["slug"]].append(r)
    for r in qrows:
        byperson[r["who"]["slug"]].append(r)
    cp, cq = cadence(bypage), cadence(byperson)
    print("\n=== cadence (posts per week) ===")
    print("   pages   median %.1f   range %.1f-%.1f  (n=%d)"
          % (statistics.median(cp), min(cp), max(cp), len(cp)))
    print("   people  median %.1f   range %.1f-%.1f  (n=%d)"
          % (statistics.median(cq), min(cq), max(cq), len(cq)))

    # --- the paired comparison ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("PAIRED: at the same company, does the person beat the page?")
    print("=" * 78)
    print("Raw engagement, because a ratio to each account's own median would make every account")
    print("1.00 by construction. It is confounded by follower counts and nothing here removes")
    print("that -- read it as a direction, not a multiple.\n")
    pairs = []
    for d in kept_people:
        p = d["person"]
        pg = pages.get(p["company_slug"])
        if not pg:
            continue
        pm = statistics.median(eng_of(x) for x in pg["posts"])
        qm = statistics.median(eng_of(x) for x in d["posts"])
        pairs.append((p, pm, qm))
    pairs.sort(key=lambda t: -(t[2] / t[1] if t[1] else 0))
    print("%-24s %-20s %8s %8s %8s  %s"
          % ("person", "company", "page med", "person", "ratio", "seniority"))
    for p, pm, qm in pairs:
        r = (qm / pm) if pm else float("inf")
        print("%-24s %-20s %8.0f %8.0f %7.2fx  %s"
              % ((p.get("name") or p["slug"])[:24], p["company"][:20], pm, qm, r,
                 p.get("seniority", "?")))
    wins = sum(1 for _, pm, qm in pairs if pm and qm > pm)
    print("\n**the person's median beat the page's in %d of %d pairs (%.0f%%)**"
          % (wins, len(pairs), pct(wins, len(pairs))))
    ratios = sorted((qm / pm) for _, pm, qm in pairs if pm)
    print("median ratio %.2fx  (a person's typical post against their own company's typical post)"
          % statistics.median(ratios))

    print("\n  by seniority -- the split that matters more than person-versus-page does")
    b = defaultdict(list)
    for p, pm, qm in pairs:
        if pm:
            b[p.get("seniority", "?")].append(qm / pm)
    for k, v in sorted(b.items(), key=lambda kv: -statistics.median(kv[1])):
        if len(v) < 3:
            print("     %-24s %2d pairs  TOO FEW" % (k, len(v)))
            continue
        print("     %-24s %2d pairs, median %.2fx, person wins %d of %d"
              % (k, len(v), statistics.median(v), sum(1 for x in v if x > 1), len(v)))

    for key in ("offering", "motion", "stage"):
        print("\n  by %s" % key)
        b = defaultdict(list)
        for p, pm, qm in pairs:
            if pm:
                b[p[key]].append(qm / pm)
        for k, v in sorted(b.items(), key=lambda kv: -statistics.median(kv[1])):
            if len(v) < 3:
                print("     %-14s %d pairs  TOO FEW" % (k, len(v)))
                continue
            print("     %-14s %d pairs, median %.2fx, person wins %d"
                  % (k, len(v), statistics.median(v), sum(1 for x in v if x > 1)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
