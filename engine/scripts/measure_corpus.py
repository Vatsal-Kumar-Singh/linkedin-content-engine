#!/usr/bin/env python3
"""Measure a company's own published posts into the `corpus:` block a profile needs.

`engine/decision/` ships with no measurements and declines to score until a profile supplies
them. **This is how the profile gets them**, and phase 1 of `docs/PLAYBOOK.md` is where it
belongs in the sequence.

    python scripts/measure_corpus.py posts.csv
    python scripts/measure_corpus.py posts.csv --channel clevel --min-n 8

Input is a CSV with one row per published post:

    author,channel,words,format,engagement,original
    ada,clevel,312,photo album,180,true
    ada,clevel,88,text,41,true
    grace,company,240,single image,96,true

| Column | Required | Notes |
|---|---|---|
| `author` | yes | **The normalisation key.** One row per post, the person or page that published it |
| `channel` | yes | Free text. Measured separately and never pooled |
| `words` | yes | Word count of the post body. Or supply `text` and it is counted for you |
| `format` | yes | Your own vocabulary: text, single image, photo album, carousel, video |
| `engagement` | yes | One number. Reactions, or reactions plus comments; be consistent |
| `original` | no | `false` excludes the row. Shares and reposts belong to somebody else |

---

## The two traps this script exists to enforce

**Cross-author medians rank the author, not the method.** One company's executives can outscore
another's six to one on employee base and network density alone, and pooling them tells you who
has the biggest following rather than which post shape works. **Every post is scored against its
own author's median before anything is aggregated.** The output is therefore a ratio, not a like
count, which is also what the scorer wants.

**A channel's medians never transfer to another channel.** A company page and a personal profile
are different products with different audiences. This measures one channel per run and refuses to
pool them.

**And a third, quieter one: a band with three posts in it is an anecdote.** Any band below
`--min-n` is reported and left out of the emitted YAML rather than shipped as a measurement.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import defaultdict

# Word bands. Fixed rather than derived, so two companies can be compared and so the boundaries
# are somebody's stated judgement rather than an artefact of one dataset's shape. Override with
# --bands if your channel behaves differently; the engine only needs them ordered best-first.
DEFAULT_BANDS = [(180, 10_000), (100, 179), (50, 99), (1, 49)]

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def read_rows(path, channel=None):
    out, skipped = [], defaultdict(int)
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for i, r in enumerate(csv.DictReader(fh), start=2):
            if (r.get("original") or "true").strip().lower() in ("false", "0", "no"):
                skipped["not original"] += 1
                continue
            if channel and (r.get("channel") or "").strip() != channel:
                skipped["other channel"] += 1
                continue
            try:
                words = int(r["words"]) if r.get("words") else len((r.get("text") or "").split())
                eng = float(r["engagement"])
            except (KeyError, ValueError):
                skipped["unreadable row"] += 1
                continue
            if words <= 0:
                skipped["no word count"] += 1
                continue
            out.append({"author": (r.get("author") or "").strip() or "unknown",
                        "channel": (r.get("channel") or "").strip(),
                        "words": words, "format": (r.get("format") or "").strip().lower(),
                        "eng": eng})
    return out, skipped


def normalise(rows):
    """Score every post against its OWN author's median. See the trap above.

    Returns rows with `rel`, and the per-author medians so the report can show its working. An
    author whose median is zero is dropped: dividing by it is undefined, and an author with no
    engagement at all tells you nothing about post shape.
    """
    by_author = defaultdict(list)
    for r in rows:
        by_author[r["author"]].append(r["eng"])
    medians = {a: statistics.median(v) for a, v in by_author.items()}
    kept, dropped = [], []
    for r in rows:
        m = medians[r["author"]]
        if m <= 0:
            dropped.append(r)
            continue
        kept.append(dict(r, rel=r["eng"] / m))
    return kept, medians, dropped


def band_of(words, bands):
    for lo, hi in bands:
        if lo <= words <= hi:
            return (lo, hi)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path")
    ap.add_argument("--channel", help="measure only this channel. Without it, every channel "
                                      "present is listed and you are asked to pick one")
    ap.add_argument("--min-n", type=int, default=5,
                    help="a band or format below this many posts is reported, not emitted")
    ap.add_argument("--bands", help="e.g. 200-9999,100-199,1-99")
    a = ap.parse_args()

    bands = DEFAULT_BANDS
    if a.bands:
        bands = []
        for part in a.bands.split(","):
            lo, hi = part.split("-")
            bands.append((int(lo), int(hi)))

    rows, skipped = read_rows(a.csv_path, a.channel)
    if not rows:
        sys.exit("no usable rows. Skipped: %s" % dict(skipped) or "file was empty")

    channels = sorted({r["channel"] for r in rows if r["channel"]})
    if not a.channel and len(channels) > 1:
        print("This file holds %d channels: %s" % (len(channels), ", ".join(channels)))
        print("\n**A channel's medians never transfer to another channel.** Re-run with")
        print("--channel <name>, once per channel, and put each result under its own key.")
        return 1

    rows, author_medians, no_baseline = normalise(rows)
    if not rows:
        sys.exit("every author had a median of zero. Nothing can be normalised against that")

    print("%d posts, %d authors, channel %r"
          % (len(rows), len(author_medians), a.channel or (channels[0] if channels else "?")))
    for k, v in sorted(skipped.items()):
        print("  skipped %-16s %d" % (k, v))
    if no_baseline:
        print("  skipped %-16s %d (author median was zero)" % ("no baseline", len(no_baseline)))

    print("\n=== each author against their own median ===")
    print("  Raw medians differ by an order of magnitude between authors and that is about")
    print("  audience, not about posts. Everything below is a ratio to the author's own median.")
    for author, m in sorted(author_medians.items(), key=lambda kv: -kv[1]):
        n = sum(1 for r in rows if r["author"] == author)
        print("    %-22s n=%-4d own median %.0f" % (author, n, m))

    # --- length ------------------------------------------------------------------------------
    print("\n=== by word band ===")
    by_band, emitted_bands = defaultdict(list), []
    for r in rows:
        b = band_of(r["words"], bands)
        if b:
            by_band[b].append(r["rel"])
    for b in bands:
        vals = by_band.get(b, [])
        label = "%d-%s" % (b[0], b[1] if b[1] < 10_000 else "+")
        if len(vals) < a.min_n:
            print("    %-10s n=%-4d TOO FEW, not emitted" % (label, len(vals)))
            continue
        med = statistics.median(vals)
        print("    %-10s n=%-4d %.2fx the author's own median" % (label, len(vals), med))
        emitted_bands.append((b[0], b[1], round(med, 3)))

    # --- format ------------------------------------------------------------------------------
    print("\n=== by format ===")
    by_fmt = defaultdict(list)
    for r in rows:
        if r["format"]:
            by_fmt[r["format"]].append(r["rel"])
    emitted_fmt = {}
    for f, vals in sorted(by_fmt.items(), key=lambda kv: -statistics.median(kv[1])):
        if len(vals) < a.min_n:
            print("    %-16s n=%-4d TOO FEW, not emitted" % (f, len(vals)))
            continue
        med = statistics.median(vals)
        print("    %-16s n=%-4d %.2fx" % (f, len(vals), med))
        emitted_fmt[f] = round(med, 3)

    # --- the block -----------------------------------------------------------------------------
    chan = a.channel or (channels[0] if channels else "clevel")
    print("\n=== paste into the profile, under `corpus:` ===\n")
    if emitted_bands:
        print("  length_bands:              # [min_words, max_words, median relative to author]")
        for lo, hi, med in emitted_bands:
            print("    - [%d, %d, %s]" % (lo, hi, med))
    else:
        print("  # no band cleared --min-n. Length is not measurable from this corpus yet.")
    print("  format_lift:")
    if emitted_fmt:
        print("    %s: {%s}" % (chan, ", ".join("%s: %s" % (k, v) for k, v in emitted_fmt.items())))
    else:
        print("    %s: null                 # nothing cleared --min-n" % chan)

    thin = [f for f, v in by_fmt.items() if len(v) < a.min_n]
    if thin or len(emitted_bands) < len(bands):
        print("\n**What was left out is worth reading.** A format or band below %d posts is an"
              % a.min_n)
        print("anecdote, and the engine would rather score nothing than score that. Publish more")
        print("in the thin ones on purpose, and re-measure; that is a real experiment.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
