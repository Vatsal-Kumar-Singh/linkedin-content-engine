#!/usr/bin/env python3
"""Turn the scraped corpus into batches a reader can label.

    python research/make_batches.py                 # default 80 posts a batch
    python research/make_batches.py --size 60
    python research/make_batches.py --check         # what is labelled, what is left
    python research/make_batches.py --remaining     # only the unlabelled, into batches_todo/

`research/CLASSIFICATION-PROTOCOL.md` defines the labels. This script only prepares the reading
and never decides anything.

---

## What it does and does not include

**Reposts are dropped.** A post carrying `header.linkedinUrl` is somebody else's content appearing
on this page, and counting it would credit the reposter with the original's shape and engagement.

**The text is truncated, and the truncation is the risk.** A buying job is usually established in
the opening lines, but a post that turns at the end — a teaching post closing with a customer
result — can be misread from its head alone. So the tail is included as well when a post is long,
marked with an ellipsis, and the word count is always shown so the reader knows what was cut.

**Order is deterministic**: by company slug, then by post id. Re-running produces identical
batches, which is what makes a second independent labelling pass comparable to the first.

**`--remaining` is for growing the corpus, and writes somewhere else on purpose.** Adding
companies renumbers every batch, because the ordering is by slug and a new slug interleaves. A
reader handed the regenerated set would be handed everything already read. `--remaining` writes
only unlabelled posts, to `batches_todo/`, and leaves `batches/` alone so the full pass stays
reproducible.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
BATCHES = HERE / "batches"
TODO = HERE / "batches_todo"
LABELS = HERE / "labels"

HEAD_WORDS = 60
TAIL_WORDS = 18

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def fmt_of(post):
    """Format from metadata. See the protocol: carousels and photo albums are one bucket."""
    if post.get("postVideo"):
        return "video"
    n = len(post.get("postImages") or [])
    if n >= 2:
        return "multi-image(%d)" % n
    if n == 1:
        return "image"
    return "link" if re.search(r"https?://|lnkd\.in", post.get("content") or "") else "text"


def is_repost(post):
    h = post.get("header") or {}
    return bool(isinstance(h, dict) and h.get("linkedinUrl"))


def digest(text):
    """Readable, short, and honest about what it cut."""
    t = re.sub(r"\s+", " ", (text or "").replace("’", "'")).strip()
    w = t.split()
    if len(w) <= HEAD_WORDS + TAIL_WORDS:
        return t
    return " ".join(w[:HEAD_WORDS]) + "  [...]  " + " ".join(w[-TAIL_WORDS:])


def load_posts():
    out = []
    for path in sorted(glob.glob(str(RAW / "*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        c = d["company"]
        for p in d.get("posts") or []:
            if is_repost(p):
                continue
            pid = str(p.get("id") or "")
            if not pid:
                continue
            out.append({"id": pid, "slug": c["slug"], "name": c["name"],
                        "fmt": fmt_of(p), "words": len((p.get("content") or "").split()),
                        "text": digest(p.get("content") or "")})
    out.sort(key=lambda r: (r["slug"], r["id"]))
    return out


def labelled_ids():
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
    ap.add_argument("--size", type=int, default=80)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--remaining", action="store_true",
                    help="write only unlabelled posts, to batches_todo/, leaving batches/ intact")
    a = ap.parse_args()

    posts = load_posts()
    if not posts:
        sys.exit("no posts in research/raw. Run scrape_sample.py first")
    done = labelled_ids()

    if a.check:
        ids = [p["id"] for p in posts]
        have = sum(1 for i in ids if i in done)
        print("%d original posts, %d labelled, %d to go" % (len(ids), have, len(ids) - have))
        stray = set(done) - set(ids)
        if stray:
            print("**%d labels do not match any post on disk.** A label file has drifted from the "
                  "corpus, or the corpus was re-scraped." % len(stray))
        from collections import Counter
        for k, v in Counter(done.values()).most_common():
            print("   %-14s %d" % (k, v))
        missing = [p for p in posts if p["id"] not in done]
        if missing:
            first = sorted({BATCHES / ("%03d.txt" % (i // a.size + 1))
                            for i, p in enumerate(posts) if p["id"] not in done})
            print("unfinished batches: %s" % ", ".join(f.name for f in sorted(first)[:12]))
        return 0

    out_dir = TODO if a.remaining else BATCHES
    if a.remaining:
        posts = [x for x in posts if x["id"] not in done]
        if not posts:
            print("nothing left to label")
            return 0
        print("%d unlabelled posts -> %s/" % (len(posts), out_dir.name))
    out_dir.mkdir(exist_ok=True)
    for f in out_dir.glob("*.txt"):
        f.unlink()
    n = 0
    for i in range(0, len(posts), a.size):
        chunk = posts[i:i + a.size]
        n += 1
        stem = ("r2_%03d" % n) if a.remaining else ("%03d" % n)
        lines = [
            "# batch %03d  -  %d posts  -  label per research/CLASSIFICATION-PROTOCOL.md" % (n, len(chunk)),
            "# labels: problem exploration requirements selection validation consensus",
            "#         recruitment culture event product-news csr unclear",
            "# write research/labels/%s.tsv as: <id><TAB><label>" % stem,
            "",
        ]
        for p in chunk:
            lines.append("%s | %s | %s | %dw" % (p["id"], p["name"], p["fmt"], p["words"]))
            lines.append("    %s" % p["text"])
            lines.append("")
        (out_dir / ("%s.txt" % stem)).write_text("\n".join(lines), encoding="utf-8")
    print("%d posts -> %d batches of %d in research/%s/" % (len(posts), n, a.size, out_dir.name))
    print("%d already labelled" % sum(1 for p in posts if p["id"] in done))
    return 0


if __name__ == "__main__":
    sys.exit(main())
