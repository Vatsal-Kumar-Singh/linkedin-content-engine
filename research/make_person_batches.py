#!/usr/bin/env python3
"""Sample the person corpus into batches a reader can label.

    python research/make_person_batches.py --per-person 15
    python research/make_person_batches.py --check

Same twelve labels and same rules as `research/CLASSIFICATION-PROTOCOL.md`; the company batches
come from `make_batches.py` and land in `labels/`, these land in `labels_people/`.

---

## Why this samples instead of reading everything

The company corpus was read in full because the cells are the unit of analysis and a thin cell
distorts a percentage. Here the unit is the **person**, and people differ enormously in volume:
one wrote 50 posts in the window and another wrote 17. Reading everything would weight the
prolific, so this takes an equal slice from each person and reports what it left out.

**The slice is deterministic, not random.** Posts are sorted by id and taken at an even stride, so
re-running produces the same sample and a second reader can be compared post by post. A seeded
shuffle would do the same job; a stride needs no seed to be remembered.

**A person below the floor is sampled in full** rather than dropped — their whole output is
smaller than the slice would be.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw_people"
BATCHES = HERE / "batches_people"
LABELS = HERE / "labels_people"

HEAD_WORDS = 55
TAIL_WORDS = 16

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def fmt_of(post):
    if post.get("postVideo"):
        return "video"
    n = len(post.get("postImages") or [])
    if n >= 2:
        return "multi-image(%d)" % n
    if n == 1:
        return "image"
    return "link" if re.search(r"https?://|lnkd\.in", post.get("content") or "") else "text"


def digest(text):
    t = re.sub(r"\s+", " ", (text or "").replace("’", "'")).strip()
    w = t.split()
    if len(w) <= HEAD_WORDS + TAIL_WORDS:
        return t
    return " ".join(w[:HEAD_WORDS]) + "  [...]  " + " ".join(w[-TAIL_WORDS:])


def stride_sample(items, k):
    """An even slice across the sorted list. Deterministic, so a second pass is comparable."""
    if k >= len(items):
        return list(items)
    step = len(items) / float(k)
    return [items[int(i * step)] for i in range(k)]


def load(per_person):
    rows, left_out = [], 0
    for path in sorted(glob.glob(str(RAW / "*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        person = d["person"]
        posts = sorted((p for p in (d.get("posts") or []) if p.get("id")),
                       key=lambda p: str(p["id"]))
        take = stride_sample(posts, per_person)
        left_out += len(posts) - len(take)
        for p in take:
            text = p.get("content") or ""
            rows.append({"id": str(p["id"]), "who": person.get("name") or person["slug"],
                         "slug": person["slug"], "fmt": fmt_of(p),
                         "words": len(text.split()), "text": digest(text)})
    rows.sort(key=lambda r: (r["slug"], r["id"]))
    return rows, left_out


def labelled():
    got = {}
    if not LABELS.is_dir():
        return got
    for f in sorted(LABELS.glob("*.tsv")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t") if "\t" in line else line.split(None, 1)
            if len(parts) >= 2:
                got[parts[0].strip()] = parts[1].strip()
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-person", type=int, default=15)
    ap.add_argument("--size", type=int, default=55)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    rows, left_out = load(a.per_person)
    done = labelled()
    if a.check:
        have = sum(1 for r in rows if r["id"] in done)
        print("%d sampled posts, %d labelled, %d to go" % (len(rows), have, len(rows) - have))
        for k, v in Counter(done.values()).most_common():
            print("   %-14s %d" % (k, v))
        return 0

    BATCHES.mkdir(exist_ok=True)
    for f in BATCHES.glob("*.txt"):
        f.unlink()
    n = 0
    for i in range(0, len(rows), a.size):
        chunk = rows[i:i + a.size]
        n += 1
        lines = [
            "# person batch %03d  -  %d posts  -  research/CLASSIFICATION-PROTOCOL.md" % (n, len(chunk)),
            "# labels: problem exploration requirements selection validation consensus",
            "#         recruitment culture event product-news csr unclear",
            "# write research/labels_people/%03d.tsv as: <id><TAB><label>" % n,
            "",
        ]
        for r in chunk:
            lines.append("%s | %s | %s | %dw" % (r["id"], r["who"], r["fmt"], r["words"]))
            lines.append("    %s" % r["text"])
            lines.append("")
        (BATCHES / ("%03d.txt" % n)).write_text("\n".join(lines), encoding="utf-8")
    print("%d posts sampled from %d people -> %d batches of %d in research/batches_people/"
          % (len(rows), len({r["slug"] for r in rows}), n, a.size))
    print("%d posts left unsampled and not read. The sample is even per person so that a "
          "prolific writer does not carry the distribution." % left_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
