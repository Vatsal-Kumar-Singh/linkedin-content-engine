#!/usr/bin/env python3
"""Find the real LinkedIn slug for companies whose scrape came back empty.

**An empty dataset and a wrong slug are the same observation**, and the difference between them
is the difference between "this company does not post" and "we looked in the wrong place". The
first pull of this sample returned nothing for 14 of 47 companies, which is far too many for the
first explanation, so this checks the second before anything is concluded.

    export FIRECRAWL_API_KEY=fc-...            # never committed; this repo is public
    python research/resolve_slugs.py           # report what it finds, change nothing
    python research/resolve_slugs.py --write    # update the frame, drop the empty raw files

Then re-run `scrape_sample.py --all`, which only pulls what is missing from disk.

---

## Why a search rather than a guess

The bad slugs were all guessed from the company name, and the guess is right often enough to be
dangerous. Retool is `tryretool`. Nothing about the name says so, and `retool` is a real page
belonging to somebody else, so the wrong guess fails silently rather than loudly.

**The slug is still not trusted after this runs.** A search can return a regional page, a careers
page, or a same-named company in another industry. The proof that a slug is right is that it
returns posts, which is the next script's job, and this one only narrows the candidates.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
FRAME = HERE / "sample-frame.yaml"
RAW = HERE / "raw"
SEARCH = "https://api.firecrawl.dev/v2/search"

# Sub-pages of a company page. The slug sits before these, and a naive "first /company/ URL"
# picks up ".../jobs" as though it were the identity.
SUBPAGES = {"jobs", "life", "people", "about", "posts", "videos", "insights", "mycompany"}

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def key():
    k = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if not k:
        sys.exit("set FIRECRAWL_API_KEY in the environment. Nothing is read from this repo, "
                 "which is public.")
    return k


def search(k, query, limit=8):
    req = urllib.request.Request(
        SEARCH, data=json.dumps({"query": query, "limit": limit}).encode("utf-8"),
        headers={"Authorization": "Bearer " + k, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as f:
        d = json.load(f)
    data = d.get("data") or {}
    return (data.get("web") if isinstance(data, dict) else data) or []


SLUG_RE = re.compile(r"://(?:[a-z]{2,3}\.)?linkedin\.com/company/([^/?#]+)", re.I)


def slugs_in(results):
    """Every company slug the search turned up, in order, deduplicated."""
    out = []
    for it in results:
        m = SLUG_RE.search(it.get("url") or "")
        if not m:
            continue
        s = m.group(1).strip().lower()
        if s in SUBPAGES or s in out:
            continue
        out.append(s)
    return out


def tokens_of(name):
    """Words that carry identity. Drops the suffixes every company shares."""
    stop = {"inc", "ltd", "limited", "llc", "corp", "co", "the", "technologies", "technology",
            "group", "labs", "software", "systems", "solutions", "company"}
    return [w for w in re.findall(r"[a-z0-9]+", name.lower()) if w not in stop]


def score(slug, name):
    """How much a slug looks like this company. Higher is better; 0 means unrelated.

    The point is to rank candidates, not to decide. `cohere-health` and `cohere` both contain
    "cohere" and are different companies, so the head token matching is necessary but the full
    name matching is what separates them.
    """
    flat = re.sub(r"[^a-z0-9]", "", slug.lower())
    toks = tokens_of(name)
    if not toks:
        return 0
    joined = "".join(toks)
    if flat == joined:
        return 100
    hits = sum(1 for t in toks if t in flat)
    if hits == len(toks):
        return 80
    if toks[0] in flat:
        return 40 + 10 * hits
    return 10 * hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--only", help="comma-separated slugs, to retry a few")
    ap.add_argument("--sleep", type=float, default=6.0,
                    help="seconds between searches. The API allows about 10 a minute "
                         "and answers a burst with 429, which is indistinguishable "
                         "from an unresolvable company unless you slow down")
    a = ap.parse_args()

    frame = yaml.safe_load(FRAME.read_text(encoding="utf-8"))
    want = {s.strip() for s in a.only.split(",")} if a.only else None
    empty = []
    for c in frame["companies"]:
        if want and c["slug"] not in want:
            continue
        f = RAW / ("%s.json" % c["slug"])
        if f.is_file() and (json.loads(f.read_text(encoding="utf-8")).get("n") or 0) == 0:
            empty.append(c)

    if not empty:
        print("Nothing to resolve: no company on disk came back empty.")
        return 0
    print("%d companies returned nothing. Searching for the real slug of each.\n" % len(empty))

    k, found, unresolved = key(), {}, []
    for i, c in enumerate(empty):
        if i:
            time.sleep(a.sleep)
        try:
            res = search(k, '%s company linkedin' % c["name"])
        except urllib.error.HTTPError as e:
            body = e.read()[:200].decode("utf-8", "replace")
            print("   %-26s SEARCH FAILED %s %s" % (c["name"], e.code, body))
            if e.code in (402, 429):
                print("\n**Firecrawl is out of credits or rate limited.** Stopping here so the\n"
                      "gap stays visible. Rotate the key and re-run; resolved slugs are kept.")
                break
            unresolved.append(c)
            continue
        except Exception as e:
            print("   %-26s SEARCH FAILED %s: %s" % (c["name"], type(e).__name__, e))
            unresolved.append(c)
            continue

        ranked = sorted(((score(s, c["name"]), s) for s in slugs_in(res)), reverse=True)
        ranked = [(sc, s) for sc, s in ranked if sc >= 40]
        if not ranked:
            print("   %-26s %-26s -> NOTHING PLAUSIBLE" % (c["name"], c["slug"]))
            unresolved.append(c)
            continue
        best_score, best = ranked[0]
        others = ", ".join(s for _, s in ranked[1:4])
        mark = "same" if best == c["slug"] else "NEW"
        print("   %-26s %-26s -> %-26s %-4s score %d%s"
              % (c["name"], c["slug"], best, mark, best_score,
                 ("   also: " + others) if others else ""))
        if best != c["slug"]:
            found[c["slug"]] = best

    print("\n%d slug corrections, %d still unresolved" % (len(found), len(unresolved)))
    if unresolved:
        print("**Unresolved companies are not evidence of anything.** Either replace them in the")
        print("frame with a company that stands for the same cell, or record the cell as thin:")
        for c in unresolved:
            print("   %-26s %s x %s" % (c["name"], c["offering"], c["motion"]))
    if not found:
        return 0
    if not a.write:
        print("\nRe-run with --write to apply, then `scrape_sample.py --all` to pull them.")
        return 0

    text = FRAME.read_text(encoding="utf-8")
    for old, new in found.items():
        before = text
        text = re.sub(r"(slug:\s*)%s\b" % re.escape(old), r"\g<1>%s" % new, text)
        if text == before:
            print("   WARNING: %r not found in the frame text; not rewritten" % old)
    FRAME.write_text(text, encoding="utf-8")
    for old in found:
        (RAW / ("%s.json" % old)).unlink(missing_ok=True)
    print("\nframe updated, %d empty raw files removed. Now run scrape_sample.py --all" % len(found))
    return 0


if __name__ == "__main__":
    sys.exit(main())
