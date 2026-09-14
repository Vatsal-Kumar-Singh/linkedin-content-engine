#!/usr/bin/env python3
"""Pull a stratified sample of the corpus's own images, so design can be looked at rather than asserted.

    python research/classify_posts.py --dump research/findings.json
    python research/sample_creative.py --out <dir>

Every other script here reads text and metadata. Format tells you an image was posted; it tells
you nothing about what was on it. The brief this study answers asked about **design**, and the
only honest way to answer that is to open the files.

---

## The sample is paired, and that is the whole design

For each buying job, the script takes the images from that job's **best-performing** posts and the
images from its **worst-performing** posts, at the same company-normalised scale. Comparing a
strong `validation` creative against a weak `validation` creative holds the content constant, so a
difference that shows up is about the design. Comparing strong creatives against weak ones
*across* jobs would just rediscover that awards outperform buyer's guides, which is already known.

**The sample is committed, on the repository owner's decision, and only while this repository
is private.** It lands in `research/creative_sample/` with a manifest and the coded attributes, so
the design finding can be checked against the images it came from rather than taken on trust.

These are other companies' copyrighted creatives. They are reproduced as a research sample,
attributed by filename and in the manifest, and they are not ours to redistribute further. **If
this repository is ever made public they have to come out of the history, not just the working
tree.** An earlier version of this script refused to write inside the repository at all; that
refusal was a judgement about redistribution, and it was overridden deliberately rather than
worked around. `research/creative_sample/README.md` carries the condition.

The sample is deterministic — same corpus, same pairing rule, same files — so it regenerates for
free from the tracked corpus and needs no scraping key.

## What stops this from being a vibe

The attributes coded from each image are fixed in advance and are countable: does type carry the
message or decorate it, is there a human face, is it a product screenshot, is it a data chart, is
it a photograph, is the brand's own colour system visible, is there text a reader must zoom to
read. Deciding those after seeing the images would make the sample a search for a story.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import urllib.request
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
JOBS = ["problem", "exploration", "requirements", "selection", "validation", "consensus",
        "event", "culture", "product-news"]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def image_urls(with_size=False):
    """post id -> list of image urls (and sizes), from the raw scrape."""
    out = {}
    for path in glob.glob(os.path.join(HERE, "raw", "*.json")):
        d = json.load(open(path, encoding="utf-8"))
        for p in d.get("posts") or []:
            pid = str(p.get("id") or "")
            imgs = p.get("postImages") or []
            urls = []
            for im in imgs:
                if isinstance(im, dict):
                    if im.get("url"):
                        urls.append((im["url"], im.get("width"), im.get("height"))
                                    if with_size else im["url"])
                elif im:
                    urls.append((im, None, None) if with_size else im)
            if pid and urls:
                out[pid] = urls
    return out


def shape_of(w, h):
    """The feed is a fixed-width column, so the only thing that varies is how tall a post is."""
    if not w or not h:
        return None
    r = h / float(w)
    if r < 0.7:
        return "wide 16:9"
    if r < 0.95:
        return "landscape 4:3"
    if r < 1.15:
        return "square 1:1"
    if r < 1.4:
        return "portrait 4:5"
    return "tall 9:16+"


ORDER = ["wide 16:9", "landscape 4:3", "square 1:1", "portrait 4:5", "tall 9:16+"]


def measure_aspect(rows, urls):
    """How much of the feed each post claims, measured on every image post in the corpus.

    This is the one design decision that does not need a human to look at the file, and it turns
    out to be the one that separates the sample most cleanly. Reported before the coded sample
    because it rests on 1,277 posts rather than on 36.
    """
    import statistics
    buckets = defaultdict(list)
    for r in rows:
        got = urls.get(r["id"]) or []
        if not got:
            continue
        _, w, h = got[0]
        s = shape_of(w, h)
        if s:
            buckets[s].append(r)
    total = sum(len(v) for v in buckets.values())
    print("=" * 84)
    print("ASPECT RATIO, MEASURED ON EVERY IMAGE POST IN THE CORPUS (%d posts)" % total)
    print("=" * 84)
    print("The feed is a fixed-width column. A taller image occupies more of the screen for")
    print("longer, and that is a design decision made once, in the template.\n")
    print("%-16s %7s %8s %10s %12s" % ("shape", "n", "share", "median x", "doubles own"))
    for s in ORDER:
        rs = buckets.get(s) or []
        if len(rs) < 20:
            if rs:
                print("%-16s %7d   below 20 posts, reported not counted" % (s, len(rs)))
            continue
        rel = [x["rel"] for x in rs]
        print("%-16s %7d %7.1f%% %10.2f %11.0f%%"
              % (s, len(rs), 100.0 * len(rs) / total, statistics.median(rel),
                 100.0 * sum(1 for x in rel if x >= 2) / len(rel)))
    print()
    # and per job, because a shape ranking can be a content ranking wearing a template
    print("Within each job, so the ranking is not just a content ranking in disguise:")
    print("%-14s %s" % ("", "".join("%-16s" % s for s in ORDER)))
    for job in JOBS:
        mine = [r for r in rows if r["label"] == job and urls.get(r["id"])]
        if len(mine) < 40:
            continue
        cells = []
        for s in ORDER:
            sub = [r["rel"] for r in mine if shape_of(*urls[r["id"]][0][1:]) == s]
            cells.append("%3.0f%% %6s" % (100.0 * len(sub) / len(mine),
                                          ("%.2f" % statistics.median(sub)) if len(sub) >= 8
                                          else "-"))
        print("%-14s %s" % (job, "".join("%-16s" % c for c in cells)))
    print("\nShare of that job's image posts using that shape, then the median they earned.")
    print("A dash is fewer than eight posts, which is not a measurement.\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", default=os.path.join(HERE, "findings.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "creative_sample"),
                    help="where the images go. Defaults to research/creative_sample/")
    ap.add_argument("--measure-only", action="store_true",
                    help="report the corpus-wide aspect-ratio measurement and download nothing")
    ap.add_argument("--per-side", type=int, default=2,
                    help="images per job per side of the pairing. Default 2, so 4 per job")
    a = ap.parse_args()

    if not a.measure_only and not a.out:
        print("--out is required unless --measure-only")
        return 1

    d = json.load(open(a.findings, encoding="utf-8"))
    urls = image_urls(with_size=True)
    rows = [r for r in d["posts"]
            if r.get("rel") is not None and r["id"] in urls and r["fmt"] in ("image", "multi-image")]
    measure_aspect(rows, urls)
    if a.measure_only:
        return 0

    by_job = defaultdict(list)
    for r in rows:
        by_job[r["label"]].append(r)

    os.makedirs(a.out, exist_ok=True)
    manifest = []
    for job in JOBS:
        rs = sorted(by_job.get(job, []), key=lambda r: r["rel"])
        if len(rs) < a.per_side * 2 + 4:
            print("%-14s only %d image posts; skipped" % (job, len(rs)))
            continue
        picks = [("weak", r) for r in rs[:a.per_side]] + [("strong", r) for r in rs[-a.per_side:]]
        for side, r in picks:
            # The post id is in the filename because without it the name is
            # job_side_company_rel, and two posts from one company in one job on one side with
            # the same rounded ratio collide. That happened twice -- Cal.com at 0.25x and
            # Airtable at 0.00x -- and the second download silently overwrote the first, leaving
            # a manifest claiming 36 images beside a directory holding 34.
            name = "%s_%s_%s_%.2fx_%s.jpg" % (job, side, r["name"].replace(" ", "")[:14],
                                              r["rel"], r["id"][-6:])
            path = os.path.join(a.out, name)
            if not os.path.exists(path):
                try:
                    req = urllib.request.Request(urls[r["id"]][0][0],
                                                 headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=60) as f, open(path, "wb") as g:
                        g.write(f.read())
                except Exception as e:
                    print("   failed %s: %s" % (name, e))
                    continue
            manifest.append({"file": name, "job": job, "side": side, "company": r["name"],
                             "rel": round(r["rel"], 2), "fmt": r["fmt"],
                             "cell": r["cell"], "industry": r.get("industry")})
            print("%-14s %-7s %-22s %6.2fx  %s" % (job, side, r["name"], r["rel"], r["fmt"]))

    json.dump(manifest, open(os.path.join(a.out, "manifest.json"), "w", encoding="utf-8"),
              indent=1)

    # A manifest that disagrees with the directory is the failure mode this script already had
    # once, and it is silent: every downstream count reads the manifest. Check, do not assume.
    on_disk = len([f for f in os.listdir(a.out) if f.endswith(".jpg")])
    if on_disk != len(manifest):
        print("\n**%d manifest entries but %d files on disk.** Names are colliding and images "
              "are being overwritten. Do not code this sample until it is fixed."
              % (len(manifest), on_disk))
        return 1
    print("\n%d images in %s, and the manifest agrees with the directory"
          % (len(manifest), a.out))
    print("Read them, code the fixed attribute list in the docstring, and write the attributes to")
    print("coded.tsv. Fixing the list before opening the files is what stops the coding becoming")
    print("a search for a story.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
