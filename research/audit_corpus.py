#!/usr/bin/env python3
"""Find what in the corpus carries no information, so it can be removed on purpose.

    python research/audit_corpus.py
    python research/audit_corpus.py --prune      # write the exclusion list

---

## The distinction this script exists to hold

**"Carries no information" is not the same as "is bad content."** A four-word post reading
"This is awesome!" is weak content and a real finding: it is how some executives actually use the
channel, and deleting it would flatter the corpus into saying people write essays. It stays.

What goes is data that cannot answer the question asked of it:

- **A post with no text at all.** Nothing to read, nothing to label, nothing to count except a
  format. It inflates `unclear` and tells you only that somebody posted an image.
- **A post outside the window the other corpus covers.** The company pages span one year. Person
  posts reach back to 2014, and LinkedIn in 2014 is not the platform being measured — pre-window
  person posts are 60.5% text-only against 35.2% in-window, so a person/page format comparison
  that includes them is measuring the platform's history, not the channel's nature.
- **An exact duplicate.** The same text posted twice counts twice and is one decision.
- **A post whose engagement is unreadable**, where a ratio cannot be formed.

Each exclusion is written to `research/excluded.json` with its reason, so nothing is silently
dropped and any of it can be put back by changing one flag.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "excluded.json")

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def date_of(p):
    return ((p.get("postedAt") or {}).get("date") or "")[:10]


def eng_of(p):
    e = p.get("engagement") or {}
    if not isinstance(e, dict):
        return None
    return float((e.get("likes") or 0) + (e.get("comments") or 0) + (e.get("shares") or 0))


def norm(text):
    """For duplicate detection: case and whitespace folded, links stripped."""
    t = re.sub(r"https?://\S+|lnkd\.in/\S+", "", (text or "").lower())
    return re.sub(r"[^a-z0-9 ]+", " ", t)


def collapse(text):
    return re.sub(r"\s+", " ", norm(text)).strip()


def load():
    pages, people = [], []
    for path in sorted(glob.glob(os.path.join(HERE, "raw", "*.json"))):
        j = json.load(open(path, encoding="utf-8"))
        for p in j.get("posts") or []:
            if (p.get("header") or {}).get("linkedinUrl"):
                continue
            pages.append({"corpus": "page", "who": j["company"]["slug"], "post": p})
    for path in sorted(glob.glob(os.path.join(HERE, "raw_people", "*.json"))):
        j = json.load(open(path, encoding="utf-8"))
        for p in j.get("posts") or []:
            people.append({"corpus": "person", "who": j["person"]["slug"], "post": p})
    return pages, people


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prune", action="store_true")
    ap.add_argument("--min-words", type=int, default=1,
                    help="posts with fewer words than this carry no readable text. Default 1, "
                         "i.e. only genuinely empty posts go. Raising it starts discarding real "
                         "one-line posts, which are a finding rather than noise")
    a = ap.parse_args()

    pages, people = load()
    rows = pages + people
    print("%d posts in scope: %d page, %d person\n" % (len(rows), len(pages), len(people)))

    # The window the page corpus actually covers. Derived, not hardcoded: the pages are the
    # reference because they were pulled as one recent slice per company.
    pdates = sorted(d for d in (date_of(r["post"]) for r in pages) if d)
    lo, hi = pdates[0], pdates[-1]
    print("page corpus window: %s .. %s\n" % (lo, hi))

    excluded = {}

    def mark(r, reason):
        pid = str(r["post"].get("id") or "")
        if pid and pid not in excluded:
            excluded[pid] = {"corpus": r["corpus"], "who": r["who"], "reason": reason,
                             "date": date_of(r["post"]),
                             "words": len((r["post"].get("content") or "").split())}

    # 1. no readable text ------------------------------------------------------------------------
    for r in rows:
        if len((r["post"].get("content") or "").split()) < a.min_words:
            mark(r, "no text at all")

    # 2. outside the page window (person corpus only; the pages define the window) ----------------
    for r in people:
        d = date_of(r["post"])
        if d and d < lo:
            mark(r, "predates the page corpus window")
        elif not d:
            mark(r, "no timestamp")

    # 3. exact duplicates, within one account ----------------------------------------------------
    seen = defaultdict(list)
    for r in rows:
        txt = collapse(r["post"].get("content") or "")
        if len(txt) < 40:
            continue          # short text collides by chance; not evidence of a repost
        seen[(r["who"], txt)].append(r)
    dupes = 0
    for key, group in seen.items():
        if len(group) > 1:
            group.sort(key=lambda r: date_of(r["post"]))
            for r in group[1:]:
                mark(r, "exact duplicate of an earlier post by the same account")
                dupes += 1

    # 4. people who do not work at the company they are paired to ---------------------------------
    # Tier A selected people by "whose posts does this page reshare", which conflates employees
    # with customers, partners and community figures. The paired comparison asks "does this
    # company's person beat this company's page" and is meaningless for somebody who works
    # elsewhere: an independent creator outscoring a vendor's page is not the finding claimed.
    MISPAIRED = {
        "jeff-geerling-086bb2a": "independent creator; Raspberry Pi reshares him, does not employ him",
        "kenzofong": "founded Rock; reshared by Airtable, not an Airtable employee",
        "melodyskim": "Skim Studio; reshared by Notion, not a Notion employee",
        "stephanie-c-30b12031": "FedEx, which is Dexterity's customer rather than its employer",
    }
    for r in people:
        if r["who"] in MISPAIRED:
            mark(r, "not employed by the paired company: %s" % MISPAIRED[r["who"]])

    # 5. unreadable engagement --------------------------------------------------------------------
    for r in rows:
        if eng_of(r["post"]) is None:
            mark(r, "engagement unreadable")

    # --- report -----------------------------------------------------------------------------------
    by_reason = Counter(v["reason"] for v in excluded.values())
    by_corpus = Counter(v["corpus"] for v in excluded.values())
    print("=== what carries no information ===")
    for reason, n in by_reason.most_common():
        print("   %-52s %4d" % (reason, n))
    print("   %-52s %4d  (%.1f%% of the corpus)"
          % ("TOTAL", len(excluded), 100.0 * len(excluded) / len(rows)))
    print("\n   page corpus loses %d of %d (%.1f%%)"
          % (by_corpus["page"], len(pages), 100.0 * by_corpus["page"] / len(pages)))
    print("   person corpus loses %d of %d (%.1f%%)"
          % (by_corpus["person"], len(people), 100.0 * by_corpus["person"] / len(people)))

    if dupes:
        print("\n=== accounts that posted the same text twice ===")
        who = Counter(v["who"] for v in excluded.values() if "duplicate" in v["reason"])
        for w, n in who.most_common(8):
            print("   %-28s %d repeat%s" % (w, n, "" if n == 1 else "s"))

    # who gets thin --------------------------------------------------------------------------------
    kept = defaultdict(int)
    for r in rows:
        if str(r["post"].get("id") or "") not in excluded:
            kept[(r["corpus"], r["who"])] += 1
    thin = [(c, w, n) for (c, w), n in kept.items() if n < 15]
    print("\n=== accounts that fall under 15 usable posts after pruning ===")
    if not thin:
        print("   none")
    for c, w, n in sorted(thin, key=lambda t: t[2]):
        print("   %-8s %-28s %d" % (c, w, n))

    print("\n**What is deliberately NOT excluded**, because weak content is not absent data:")
    print("   - one-line posts ('This is awesome!'): how some executives really use the channel")
    print("   - zero-engagement posts: a real outcome, and dropping them would flatter every median")
    print("   - memes, culture and off-topic posts: real content decisions with real costs")
    print("   - non-English posts: a finding about who these companies talk to, not noise")

    if a.prune:
        json.dump({"window": {"from": lo, "to": hi}, "excluded": excluded},
                  open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("\nwrote %s (%d ids)" % (OUT, len(excluded)))
    else:
        print("\nRe-run with --prune to write research/excluded.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
