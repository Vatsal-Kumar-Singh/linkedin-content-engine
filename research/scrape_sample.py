#!/usr/bin/env python3
"""Pull the LinkedIn posts of every company in the sample frame.

**Measured first.** What these companies actually published is the evidence; published advice
about what they ought to publish is gathered separately and graded. `research/sample-frame.yaml`
is the study design and names why each company stands for its cell.

    export APIFY_TOKENS=tok1,tok2,tok3          # never committed; this repo is public
    python research/scrape_sample.py --probe    # 2 companies, reports the real cost per company
    python research/scrape_sample.py --all
    python research/scrape_sample.py --cell "product x enterprise"

---

## Three things this guards, each from a failure that has happened

**A wrong slug returns an empty dataset, not an error.** So does a run past the actor's free-tier
cap. Both look exactly like "this company posts nothing", which is a finding, and it would be a
fabricated one. Every company that comes back empty is reported by name at the end, and the raw
file records the attempt either way.

**Cost is measured before it is committed.** `--probe` runs two companies and reports dollars per
company from the account's own usage figures, so the full run is a decision with a number behind
it rather than a hope.

**Raw is written before anything is interpreted.** Classification is re-runnable from disk; a
change to the classifier must never mean paying to scrape again.
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
FRAME = HERE / "sample-frame.yaml"
RAW = HERE / "raw"
ACTOR = "harvestapi~linkedin-company-posts"
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
    """Dollars spent this cycle on one account, from the account itself."""
    try:
        url = "https://api.apify.com/v2/users/me/usage/monthly?token=" + token
        with urllib.request.urlopen(url, timeout=30) as f:
            d = (json.load(f).get("data") or {})
        return float(d.get("totalUsageCreditsUsdAfterVolumeDiscount") or 0.0)
    except Exception:
        return None


def url_of(company):
    """The page to pull. A frame entry may override it, and some genuinely need to.

    **A division of a conglomerate is often a LinkedIn *showcase* page, not a company page.**
    ABB Robotics is: /company/abb-robotics/ returns nothing and /showcase/abbrobotics/ returns
    its posts. Without the override that reads as "ABB Robotics does not publish", which is the
    opposite of true and would have been a finding about industrial robotics content.
    """
    return company.get("url") or ("https://www.linkedin.com/company/%s/" % company["slug"])


def run_batch(token, urls, max_posts):
    """One run, many companies. Returns the raw items or raises."""
    payload = {"companyUrls": list(urls), "maxPosts": max_posts}
    req = urllib.request.Request(
        RUN_URL % (ACTOR, token),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1800) as f:
        return json.load(f)


def company_of(item):
    """Which company a returned post belongs to.

    `author.universalName` is the slug and it is checked first. The fallback reads the input URL
    back out of `query`, which matters when a post comes back with a thin author block: without
    it the post is silently dropped and the company reads as empty, which is indistinguishable
    from a wrong slug.
    """
    author = item.get("author") or {}
    if isinstance(author, dict) and author.get("universalName"):
        return str(author["universalName"]).strip().lower()
    q = (item.get("query") or {}).get("companyUniversalName") or ""
    if q:
        return q.rstrip("/").split("/")[-1].lower()
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true", help="two companies, report cost per company")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--cell", help='e.g. "product x enterprise"')
    ap.add_argument("--batch", type=int, default=8, help="companies per run")
    ap.add_argument("--max-posts", type=int, default=50)
    a = ap.parse_args()

    frame = yaml.safe_load(FRAME.read_text(encoding="utf-8"))
    companies = frame["companies"]
    if a.cell:
        off, mot = [x.strip() for x in a.cell.lower().split("x")]
        companies = [c for c in companies if c["offering"] == off and c["motion"] == mot]
    if a.probe:
        companies = companies[:2]
    if not (a.probe or a.all or a.cell):
        sys.exit("pick --probe, --cell or --all")

    RAW.mkdir(exist_ok=True)
    todo = [c for c in companies if not (RAW / ("%s.json" % c["slug"])).exists()]
    done = len(companies) - len(todo)
    print("%d companies selected, %d already on disk, %d to pull"
          % (len(companies), done, len(todo)))
    if not todo:
        return 0

    toks, ti = tokens(), 0
    start_usd = usage(toks[ti])
    print("account 1 of %d has spent $%.2f of 5.00 this cycle\n"
          % (len(toks), start_usd if start_usd is not None else -1))

    empty, pulled = [], 0
    for i in range(0, len(todo), a.batch):
        batch = todo[i:i + a.batch]
        urls = [url_of(c) for c in batch]
        print("run %d: %s" % (i // a.batch + 1, ", ".join(c["slug"] for c in batch)))

        items = None
        for attempt in range(len(toks)):
            try:
                items = run_batch(toks[ti], urls, a.max_posts)
                break
            except urllib.error.HTTPError as e:
                body = e.read()[:200].decode("utf-8", "replace")
                print("   token %d refused (%s): %s" % (ti + 1, e.code, body))
                # Budget or rate refusal: rotate rather than stopping. The cap is per account.
                ti = (ti + 1) % len(toks)
                print("   rotating to account %d" % (ti + 1))
                time.sleep(2)
            except Exception as e:
                print("   error: %s: %s" % (type(e).__name__, e))
                break
        if items is None:
            print("   NO ACCOUNT COULD RUN THIS BATCH. Stopping so the gap is visible.")
            break

        by_slug = {}
        for it in items:
            key = company_of(it)
            if key:
                by_slug.setdefault(key, []).append(it)

        for c in batch:
            got = by_slug.get(c["slug"].lower()) or []
            (RAW / ("%s.json" % c["slug"])).write_text(
                json.dumps({"company": c, "n": len(got), "posts": got}, ensure_ascii=False),
                encoding="utf-8")
            if got:
                pulled += len(got)
            else:
                empty.append(c)
            print("   %-24s %d posts%s" % (c["name"], len(got), "  <-- EMPTY" if not got else ""))
        time.sleep(1)

    end_usd = usage(toks[ti])
    print("\n%d posts across %d companies" % (pulled, len(todo) - len(empty)))
    if start_usd is not None and end_usd is not None and end_usd >= start_usd:
        spent = end_usd - start_usd
        per = spent / max(1, len(todo) - len(empty))
        print("spent $%.3f on this account, about $%.3f per company" % (spent, per))

    if empty:
        print("\n**%d COMPANIES RETURNED NOTHING.** An empty dataset is what a wrong slug and an\n"
              "exhausted actor cap both look like, and neither is the finding 'they post nothing':"
              % len(empty))
        for c in empty:
            print("   %-24s slug %r" % (c["name"], c["slug"]))
        print("Check the slug by opening linkedin.com/company/<slug>/ before concluding anything.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
