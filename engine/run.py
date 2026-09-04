#!/usr/bin/env python3
"""the product LinkedIn Content & Creative Engine.

    python run.py --list
    python run.py --post round1_01
    python run.py --round 1
"""
import sys, os

# Windows consoles default to cp1252, which cannot encode the box-drawing and
# typographic characters the CLI prints. Without this, `--list` dies on a
# UnicodeEncodeError before printing a single row.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # non-reconfigurable stream
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from postengine.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
