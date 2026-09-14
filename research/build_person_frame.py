#!/usr/bin/env python3
"""Build the sample of named people to set beside the company pages.

    export FIRECRAWL_API_KEY=fc-...
    python research/build_person_frame.py            # report, write nothing
    python research/build_person_frame.py --write    # write research/person-frame.yaml

---

## Why the sample is built in two tiers

**Tier A costs nothing and is chosen by the companies themselves.** When a company page reshares,
the scrape records the original author, so the corpus already names 155 people these pages choose
to amplify. Selecting from that list avoids the usual failure of a person-channel study, which is
that the researcher picks whoever is famous.

**Tier A alone would have answered the wrong question.** The pages that reshare heavily are early
PLG and founder-led companies, so a sample drawn only from Tier A measures *founders at startups*
and would have produced "named people post informally" as a finding about people when it is
really a finding about that cell. Tier B fills the enterprise, service and industrial cells by
looking up a named executive at companies already in the company frame.

**Every person is paired to a company already in the study.** Same market, same window, same
moment — so the person-versus-page comparison is within-company rather than across two unrelated
samples.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
FRAME = HERE / "sample-frame.yaml"
OUT = HERE / "person-frame.yaml"
SEARCH = "https://api.firecrawl.dev/v2/search"

# Companies whose cells Tier A leaves thin. Chosen from the company frame, not invented: the
# point of the pairing is that the page these people sit beside is already measured.
TIER_B = [
    ("Thoughtworks", "thoughtworks"),
    ("Slalom", "slalom-consulting"),
    ("Snowflake", "snowflake-computing"),
    ("Databricks", "databricks"),
    ("Veeva Systems", "veeva-systems"),
    ("Locus Robotics", "locus-robotics"),
    ("Addverb Technologies", "addverb"),
    ("Agility Robotics", "agilityrobotics"),
    ("Cognism", "cognism"),
    ("Gong", "gong-io"),
    ("Prusa Research", "prusa3d"),
    ("Formlabs", "formlabs"),
]

PROFILE_RE = re.compile(r"://(?:[a-z]{2,3}\.)?linkedin\.com/in/([^/?#]+)", re.I)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def companies():
    d = yaml.safe_load(FRAME.read_text(encoding="utf-8"))
    return {c["slug"]: c for c in d["companies"]}


def tier_a(by_slug, min_reshares=2):
    """People the pages themselves amplify, with the company they were reshared by."""
    people = defaultdict(lambda: {"n": 0, "name": None, "by": Counter()})
    for path in glob.glob(str(HERE / "raw" / "*.json")):
        d = json.load(open(path, encoding="utf-8"))
        slug = d["company"]["slug"]
        for p in d.get("posts") or []:
            if not (p.get("header") or {}).get("linkedinUrl"):
                continue
            a = p.get("author") or {}
            if a.get("type") != "profile":
                continue
            pid = a.get("publicIdentifier")
            if not pid:
                continue
            people[pid]["n"] += 1
            people[pid]["name"] = a.get("name")
            people[pid]["by"][slug] += 1
    out = []
    for pid, v in sorted(people.items(), key=lambda kv: -kv[1]["n"]):
        if v["n"] < min_reshares:
            continue
        slug = v["by"].most_common(1)[0][0]
        c = by_slug.get(slug)
        if not c:
            continue
        out.append({"slug": pid, "name": v["name"], "company": c["name"],
                    "company_slug": slug, "tier": "A", "reshares": v["n"],
                    **{k: c[k] for k in ("offering", "motion", "stage", "buyer")}})
    return out


def search(k, query, limit=8):
    req = urllib.request.Request(
        SEARCH, data=json.dumps({"query": query, "limit": limit}).encode("utf-8"),
        headers={"Authorization": "Bearer " + k, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as f:
        d = json.load(f)
    data = d.get("data") or {}
    return (data.get("web") if isinstance(data, dict) else data) or []


def tier_b(by_slug, have, sleep):
    k = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if not k:
        print("\nFIRECRAWL_API_KEY not set; skipping tier B. The sample will be founder-heavy "
              "and the person/page comparison will confound person with stage.")
        return []
    out = []
    print("\nTier B: looking up a named executive at %d companies whose cells tier A misses."
          % len(TIER_B))
    for i, (name, slug) in enumerate(TIER_B):
        c = by_slug.get(slug)
        if not c:
            print("   %-24s not in the company frame, skipped" % name)
            continue
        if i:
            time.sleep(sleep)
        try:
            res = search(k, "%s CEO OR founder OR CTO linkedin profile" % name)
        except urllib.error.HTTPError as e:
            print("   %-24s search failed %s" % (name, e.code))
            if e.code in (402, 429):
                print("   **Firecrawl refused. Stopping tier B here so the gap is visible.**")
                break
            continue
        except Exception as e:
            print("   %-24s search failed %s" % (name, type(e).__name__))
            continue
        picked = None
        for it in res:
            m = PROFILE_RE.search(it.get("url") or "")
            if not m:
                continue
            pid = m.group(1).lower()
            if pid in have or any(o["slug"] == pid for o in out):
                continue
            picked = (pid, (it.get("title") or "").split("-")[0].strip()[:40])
            break
        if not picked:
            print("   %-24s no profile found" % name)
            continue
        print("   %-24s -> %-28s %s" % (name, picked[0], picked[1]))
        out.append({"slug": picked[0], "name": picked[1], "company": c["name"],
                    "company_slug": slug, "tier": "B", "reshares": 0,
                    **{k2: c[k2] for k2 in ("offering", "motion", "stage", "buyer")}})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--min-reshares", type=int, default=2)
    ap.add_argument("--sleep", type=float, default=7.0)
    a = ap.parse_args()

    by_slug = companies()
    A = tier_a(by_slug, a.min_reshares)
    print("Tier A: %d people reshared %d+ times by a page in the company frame."
          % (len(A), a.min_reshares))
    for p in A:
        print("   %-26s %-22s %-22s %s x %s / %s"
              % (p["slug"], (p["name"] or "")[:22], p["company"][:22],
                 p["offering"], p["motion"], p["stage"]))

    have = {p["slug"] for p in A}
    B = tier_b(by_slug, have, a.sleep)
    people = A + B

    print("\n%d people total. Coverage against the company grid:" % len(people))
    for key in ("offering", "motion", "stage"):
        print("   %-10s %s" % (key, dict(Counter(p[key] for p in people))))

    if not a.write:
        print("\nRe-run with --write to save research/person-frame.yaml")
        return 0
    doc = {
        "status": "DRAFT",
        "purpose": "Named people paired to company pages already in sample-frame.yaml, so the "
                   "person-versus-organisation channel split can be measured within company "
                   "rather than across two unrelated samples.",
        "tiers": {
            "A": "chosen by the companies themselves: reshared %d+ times by their own page"
                 % a.min_reshares,
            "B": "looked up to fill the enterprise, service and industrial cells tier A misses, "
                 "because a founder-only sample confounds person with stage",
        },
        "people": people,
    }
    OUT.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print("\nwrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
