#!/usr/bin/env python3
"""Join the hand-read labels to the scrape metadata and report what the corpus shows.

    python research/classify_posts.py
    python research/classify_posts.py --by offering --by motion
    python research/classify_posts.py --min-posts 20 --dump findings.json

`research/CLASSIFICATION-PROTOCOL.md` defines the labels and why they are read rather than
pattern-matched. This script does no classifying of its own.

---

## Three rules this enforces, each from something that went wrong

**A company below `--min-posts` originals does not vote.** A page with sixteen posts and a page
with fifty do not carry the same weight, and averaging them as equals lets the quietest company
swing a cell it barely occupies. Thin companies are reported by name and excluded from every
percentage; they are not deleted, because *why* a company is thin is itself a finding.

**A repost is not the page's content, and the ratio is a finding.** Posts carrying
`header.linkedinUrl` are the page resharing somebody else's post — usually its own founder's.
They are excluded from the job distribution, and the excluded fraction is reported per company,
because a page that is 77% reshares is running a **person-led channel with an organisation-shaped
amplifier**, which is a strategy, not an absence of one.

**Engagement is normalised per company, always.** Figma has two million followers and a
four-person startup has four thousand. A median pooled across them measures audience, not method,
so every post is scored against its own company's median before anything is aggregated.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
LABELS = os.path.join(HERE, "labels")

JOBS = ["problem", "exploration", "requirements", "selection", "validation", "consensus"]
OTHER = ["recruitment", "culture", "event", "product-news", "csr"]
VALID = set(JOBS) | set(OTHER) | {"unclear"}
TIER = {"problem": "TOFU", "exploration": "TOFU",
        "requirements": "MOFU", "selection": "MOFU",
        "validation": "BOFU", "consensus": "BOFU"}

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def read_labels():
    got, bad = {}, []
    for path in sorted(glob.glob(os.path.join(LABELS, "*.tsv"))):
        for line in open(path, encoding="utf-8"):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 2:
                parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            pid, lab = parts[0].strip(), parts[1].strip()
            if lab not in VALID:
                bad.append((os.path.basename(path), pid, lab))
                continue
            got[pid] = lab
    return got, bad


def fmt_of(post):
    if post.get("postVideo"):
        return "video"
    n = len(post.get("postImages") or [])
    if n >= 2:
        return "multi-image"
    if n == 1:
        return "image"
    return "link" if re.search(r"https?://|lnkd\.in", post.get("content") or "") else "text"


def engagement_of(post):
    e = post.get("engagement") or {}
    return float((e.get("likes") or 0) + (e.get("comments") or 0) + (e.get("shares") or 0))


def load(labels):
    rows, companies = [], {}
    for path in sorted(glob.glob(os.path.join(HERE, "raw", "*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        c = d["company"]
        posts = d.get("posts") or []
        reshares = [p for p in posts if (p.get("header") or {}).get("linkedinUrl")]
        originals = [p for p in posts if not (p.get("header") or {}).get("linkedinUrl")]
        companies[c["name"]] = {
            "slug": c["slug"], "raw": len(posts), "originals": len(originals),
            "reshares": len(reshares),
            **{k: c[k] for k in ("offering", "motion", "stage", "buyer", "market", "regulated")},
        }
        for p in originals:
            pid = str(p.get("id") or "")
            lab = labels.get(pid)
            if not lab:
                continue
            text = p.get("content") or ""
            rows.append({
                "id": pid, "name": c["name"],
                **{k: c[k] for k in ("offering", "motion", "stage", "buyer", "market",
                                     "regulated")},
                "cell": "%s x %s" % (c["offering"], c["motion"]),
                "label": lab,
                "job": lab if lab in JOBS else None,
                "tier": TIER.get(lab),
                "fmt": fmt_of(p), "words": len(text.split()), "eng": engagement_of(p),
                "date": ((p.get("postedAt") or {}).get("date") or "")[:10],
            })
    return rows, companies


def normalise(rows):
    """Score each post against its OWN company's median. Pooling measures audience, not method."""
    by = defaultdict(list)
    for r in rows:
        by[r["name"]].append(r["eng"])
    med = {k: statistics.median(v) for k, v in by.items() if v}
    for r in rows:
        m = med.get(r["name"]) or 0
        r["rel"] = (r["eng"] / m) if m > 0 else None
    return rows, med


def pct(part, whole):
    return (100.0 * part / whole) if whole else 0.0


def report_split(rows, keys, title=None):
    groups = defaultdict(list)
    for r in rows:
        groups[tuple(str(r[k]) for k in keys)].append(r)
    print("\n%-30s %5s %6s %6s %6s %7s %7s" %
          (title or " x ".join(keys), "n", "TOFU", "MOFU", "BOFU", "non-buy", "unclear"))
    print("-" * 76)
    for g, rs in sorted(groups.items()):
        n = len(rs)
        t = Counter(r["tier"] for r in rs if r["tier"])
        oth = sum(1 for r in rs if r["label"] in OTHER)
        unc = sum(1 for r in rs if r["label"] == "unclear")
        print("%-30s %5d %5.0f%% %5.0f%% %5.0f%% %6.0f%% %6.0f%%"
              % (" / ".join(g)[:30], n, pct(t["TOFU"], n), pct(t["MOFU"], n),
                 pct(t["BOFU"], n), pct(oth, n), pct(unc, n)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--by", action="append", default=None)
    ap.add_argument("--min-posts", type=int, default=20,
                    help="a company with fewer labelled originals than this is reported but "
                         "excluded from every percentage. Default 20")
    ap.add_argument("--dump")
    a = ap.parse_args()

    labels, bad = read_labels()
    if bad:
        print("**%d labels are not in the protocol's vocabulary and were dropped:**" % len(bad))
        for f, pid, lab in bad[:10]:
            print("   %s  %s  %r" % (f, pid, lab))
    rows, companies = load(labels)
    if not rows:
        sys.exit("no labelled posts. See CLASSIFICATION-PROTOCOL.md")

    # --- the threshold -------------------------------------------------------------------------
    labelled = Counter(r["name"] for r in rows)
    thin = {n for n in companies if labelled.get(n, 0) < a.min_posts}
    kept = [r for r in rows if r["name"] not in thin]
    kept, medians = normalise(kept)

    print("\n%d companies scraped, %d posts pulled, %d originals labelled"
          % (len(companies), sum(c["raw"] for c in companies.values()), len(rows)))
    print("%d companies clear the %d-original threshold and carry the percentages below; "
          "%d do not" % (len(companies) - len(thin), a.min_posts, len(thin)))

    if thin:
        print("\n**BELOW THRESHOLD — reported, not counted.** A page with a handful of originals")
        print("cannot stand for a cell, and the reason it is thin is usually the finding:")
        print("   %-24s %6s %6s %9s  %s" % ("company", "pulled", "orig", "reshare%", "cell"))
        for n in sorted(thin, key=lambda x: companies[x]["originals"]):
            c = companies[n]
            print("   %-24s %6d %6d %8.0f%%  %s x %s"
                  % (n, c["raw"], c["originals"], pct(c["reshares"], c["raw"]),
                     c["offering"], c["motion"]))

    # --- the reshare finding -------------------------------------------------------------------
    heavy = sorted((c for c in companies.items() if c[1]["raw"] and
                    pct(c[1]["reshares"], c[1]["raw"]) >= 40),
                   key=lambda kv: -pct(kv[1]["reshares"], kv[1]["raw"]))
    if heavy:
        print("\n**PAGES THAT MOSTLY RESHARE.** Not an absence of strategy: the page is an")
        print("amplifier for named people, which is a channel decision this engine models as")
        print("`kind: person` versus `kind: organisation`. Reshares are excluded from the")
        print("distributions below, so for these companies the page's own voice is what is left:")
        for n, c in heavy:
            print("   %-24s %3d of %3d reshared (%.0f%%)  %s x %s / %s"
                  % (n, c["reshares"], c["raw"], pct(c["reshares"], c["raw"]),
                     c["offering"], c["motion"], c["stage"]))

    # --- the honesty gate ----------------------------------------------------------------------
    n = len(kept)
    unc = sum(1 for r in kept if r["label"] == "unclear")
    print("\n%d posts across %d companies carry every number below." % (n, len(medians)))
    print("unclear: %d (%.1f%%)" % (unc, pct(unc, n)))
    if pct(unc, n) > 15:
        print("\n**ABOVE THE 15% HONESTY THRESHOLD.** Past this the instrument is reporting on")
        print("itself rather than on the corpus. Do not quote the percentages as findings.")
    else:
        print("Below the 15%% gate, so the distributions are about the corpus. (%.1f%%)"
              % pct(unc, n))

    print("\n=== what the whole corpus does ===")
    for k, v in Counter(r["label"] for r in kept).most_common():
        bucket = "buying job" if k in JOBS else ("unclear" if k == "unclear" else "other")
        print("   %-14s %5d %5.1f%%   %s" % (k, v, pct(v, n), bucket))

    for keys in (a.by and [a.by] or [["offering"], ["motion"], ["stage"], ["cell"]]):
        report_split(kept, keys)

    if a.dump:
        json.dump({"posts": kept, "companies": companies, "thin": sorted(thin)},
                  open(a.dump, "w", encoding="utf-8"), ensure_ascii=False)
        print("\nwrote %s" % a.dump)
    return 0


if __name__ == "__main__":
    sys.exit(main())
