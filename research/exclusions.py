#!/usr/bin/env python3
"""The one place that says which posts are out, and why.

`audit_corpus.py --prune` writes `excluded.json`; every analysis reads it through here so the
corpus one script sees is the corpus the others see. Nothing is deleted from `raw/`: the exclusion
is a view, and removing the file restores the full corpus.

**Weak content is not excluded content.** One-line posts, zero-engagement posts, memes and
non-English posts all stay, because each is a real decision somebody made. What goes is data that
cannot answer the question: empty posts, exact duplicates, posts outside the window the other
corpus covers, and people who do not work at the company they are paired to.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_PATH = os.path.join(HERE, "excluded.json")


def excluded_ids():
    if not os.path.isfile(_PATH):
        return set(), {}
    d = json.load(open(_PATH, encoding="utf-8"))
    return set(d.get("excluded") or {}), (d.get("window") or {})


def banner():
    ids, win = excluded_ids()
    if not ids:
        return "no exclusion list found; running on the full corpus"
    return ("%d posts excluded by research/audit_corpus.py (window %s..%s). "
            "Weak content is kept; only data that cannot answer the question is dropped."
            % (len(ids), win.get("from", "?"), win.get("to", "?")))
