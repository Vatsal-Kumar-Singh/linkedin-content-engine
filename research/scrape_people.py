#!/usr/bin/env python3
"""Pull the posts of every named person in the person frame.

    export APIFY_TOKENS=tok1,tok2,tok3      # never committed; this repo is public
    python research/scrape_people.py --all --batch 4

Companion to `scrape_sample.py`. Same actor family, same guards, one extra filter.

---

## The extra filter, and why it is not the same as the company one

A profile feed contains what the person **posted** and what they **reshared**, and the actor
returns both. For the company scrape, a reshare was excluded because it is not the page's content.
Here the same rule applies for the same reason — but the test is different: a profile's own posts
carry that profile as `author.publicIdentifier`, so anything authored by somebody else is a
reshare regardless of whether a `header` is present.

**Both numbers are kept.** How much of a person's feed is their own writing is the person-side
version of the finding that some company pages are 77% amplifier, and it would be lost if the
reshares were simply dropped.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
FRAME = HERE / "person-frame.yaml"
RAW = HERE / "raw_people"
ACTOR = "harvestapi~linkedin-profile-posts"
RUN_URL = "https://api.apify.com/v2/acts/%s/run-sync-get-dataset-items?token=%s"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def tokens():
    raw = os.environ.get("APIFY_TOKENS") or os.environ.get("APIFY_API_TOKEN") or ""
    out = [t.strip() for t in raw.split(",") if t.strip()]
    if not out:
        sys.exit("set APIFY_TOKENS=tok1,tok2,... in the environment. Nothing is read from disk "
                 "and no key belongs in this repository, which is public.")
    return out


def usage(token):
    try:
        url = "https://api.apify.com/v2/users/me/usage/monthly?token=" + token
        with urllib.request.urlopen(url, timeout=30) as f:
            d = (json.load(f).get("data") or {})
        return float(d.get("totalUsageCreditsUsdAfterVolumeDiscount") or 0.0)
    except Exception:
        return None


def run_batch(token, slugs, max_posts):
    payload = {"profileUrls": ["https://www.linkedin.com/in/%s/" % s for s in slugs],
               "maxPosts": max_posts}
    req = urllib.request.Request(
        RUN_URL % (ACTOR, token),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1800) as f:
        return json.load(f)


def author_of(item):
    a = item.get("author") or {}
    if isinstance(a, dict) and a.get("publicIdentifier"):
        return str(a["publicIdentifier"]).strip().lower()
    return None


def queried_of(item):
    """Whose feed this item came from, when the actor says so."""
    q = (item.get("query") or {})
    for k in ("profileUrl", "profile", "publicIdentifier", "url"):
        v = q.get(k)
        if v:
            return str(v).rstrip("/").split("/")[-1].lower()
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--max-posts", type=int, default=50)
    a = ap.parse_args()

    frame = yaml.safe_load(FRAME.read_text(encoding="utf-8"))
    people = frame["people"]
    if a.probe:
        people = people[:2]
    if not (a.probe or a.all):
        sys.exit("pick --probe or --all")

    RAW.mkdir(exist_ok=True)
    todo = [p for p in people if not (RAW / ("%s.json" % p["slug"])).exists()]
    print("%d people selected, %d already on disk, %d to pull"
          % (len(people), len(people) - len(todo), len(todo)))
    if not todo:
        return 0

    toks, ti = tokens(), 0
    start = usage(toks[ti])
    print("account 1 of %d has spent $%.2f of 5.00\n" % (len(toks), start if start is not None else -1))

    empty, own, reshared = [], 0, 0
    for i in range(0, len(todo), a.batch):
        batch = todo[i:i + a.batch]
        slugs = [p["slug"] for p in batch]
        print("run %d: %s" % (i // a.batch + 1, ", ".join(slugs)))

        items = None
        for _ in range(len(toks)):
            try:
                items = run_batch(toks[ti], slugs, a.max_posts)
                break
            except urllib.error.HTTPError as e:
                body = e.read()[:160].decode("utf-8", "replace")
                print("   token %d refused (%s): %s" % (ti + 1, e.code, body))
                ti = (ti + 1) % len(toks)
                print("   rotating to account %d" % (ti + 1))
                time.sleep(2)
            except Exception as e:
                print("   error: %s: %s" % (type(e).__name__, e))
                break
        if items is None:
            print("   NO ACCOUNT COULD RUN THIS BATCH. Stopping so the gap stays visible.")
            break

        bucket = {s: [] for s in slugs}
        for it in items:
            key = queried_of(it)
            if key not in bucket:
                # Fall back to the author when the query field is absent: a person's own post
                # carries their identifier, which is enough to file it.
                key = author_of(it)
            if key in bucket:
                bucket[key].append(it)

        for p in batch:
            got = bucket.get(p["slug"], [])
            mine = [x for x in got if author_of(x) == p["slug"].lower()]
            theirs = [x for x in got if author_of(x) != p["slug"].lower()]
            (RAW / ("%s.json" % p["slug"])).write_text(
                json.dumps({"person": p, "n": len(mine), "n_reshared": len(theirs),
                            "posts": mine, "reshared": theirs}, ensure_ascii=False),
                encoding="utf-8")
            own += len(mine)
            reshared += len(theirs)
            if not mine:
                empty.append(p)
            print("   %-26s %2d own, %2d reshared%s"
                  % ((p["name"] or p["slug"])[:26], len(mine), len(theirs),
                     "   <-- NO OWN POSTS" if not mine else ""))
        time.sleep(1)

    end = usage(toks[ti])
    print("\n%d own posts, %d reshares, across %d people" % (own, reshared, len(todo) - len(empty)))
    if start is not None and end is not None and end >= start:
        n = max(1, len(todo) - len(empty))
        print("spent $%.3f on this account, about $%.3f per person" % (end - start, (end - start) / n))
    if empty:
        print("\n**%d PEOPLE RETURNED NOTHING OF THEIR OWN.** A private profile, a wrong slug and "
              "somebody who only reshares all look identical here:" % len(empty))
        for p in empty:
            print("   %-26s %s" % ((p["name"] or "")[:26], p["slug"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
