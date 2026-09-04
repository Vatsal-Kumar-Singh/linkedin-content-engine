"""Prompt loading. Prompts are markdown files, not string literals in code."""
from __future__ import annotations

import os
from typing import Dict

from ..config import ROOT

_CACHE: Dict[str, str] = {}


def load_prompt(name: str) -> str:
    if name not in _CACHE:
        path = os.path.join(ROOT, "prompts", name + ".md")
        if not os.path.exists(path):
            raise FileNotFoundError("missing prompt: prompts/%s.md" % name)
        with open(path, "r", encoding="utf-8") as fh:
            _CACHE[name] = fh.read()
    return _CACHE[name]
