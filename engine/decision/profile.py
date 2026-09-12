#!/usr/bin/env python3
"""Read a company profile.

**One file per company, one home per fact.** A profile is markdown for a person and a single
fenced YAML block for the machine. The prose carries the reasoning and the block carries the
data, and neither restates the other, so they cannot drift apart. Splitting them into two files
would give one fact two homes, which is the failure `docs/03-integration.md` exists to avoid.

The loader is deliberately strict about one thing: **a profile that declares objective weights
without declaring each objective's `kind` is rejected.** The engine cannot know what a "qualified
plant conversation" is, and must not guess. `kind` is the translation layer, and a weight the
engine cannot interpret is worse than no weight, because it would silently fall through to a
default.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

# Profiles sit beside this module. The path was `parent.parent` in the layout this came
# from, where the loader lived one level deeper; moving the package without moving the
# path pointed it at a directory that does not exist.
PROFILES = Path(__file__).resolve().parent / "profiles"

# What the engine understands, and all it understands, about an objective.
#
#   capture   moves a buyer who has already identified themselves. Demand capture
#   create    builds standing among people who are not in market yet. Demand creation
#
# The distinction is from the demand-creation literature graded in `research/01-models-in-use.md`,
# and it is the only company-agnostic vocabulary that survived. Everything else about an
# objective is the company's own business.
KINDS = {"capture", "create"}

_BLOCK = re.compile(r"```yaml\n(.*?)\n```", re.S)


def load(name: str) -> dict:
    """Load `profiles/<name>.md` and return the YAML block as a dict."""
    p = PROFILES / (name if name.endswith(".md") else name + ".md")
    if not p.is_file():
        raise FileNotFoundError(f"no profile at {p}")
    blocks = _BLOCK.findall(p.read_text(encoding="utf-8"))
    if not blocks:
        raise ValueError(f"{p.name} has no fenced yaml block, so there is nothing to read")
    if len(blocks) > 1:
        raise ValueError(f"{p.name} has {len(blocks)} yaml blocks. One file, one home for a fact")
    prof = yaml.safe_load(blocks[0]) or {}
    _validate(prof, p.name)
    return prof


def _validate(prof: dict, who: str) -> None:
    obj = prof.get("objectives") or {}
    weights = obj.get("weights") or {}
    if not weights:
        return                      # no weights is a legitimate state. Fit withholds and says so
    kinds = obj.get("kinds") or {}
    missing = [k for k in weights if k not in kinds]
    if missing:
        raise ValueError(
            f"{who}: objectives {missing} carry a weight and no `kind`. The engine cannot "
            f"interpret a company-specific objective without one, and guessing would put a "
            f"default behind a number somebody agreed to. Add kind: capture or create")
    bad = {k: v for k, v in kinds.items() if v not in KINDS}
    if bad:
        raise ValueError(f"{who}: unknown objective kinds {bad}. Allowed: {sorted(KINDS)}")
    total = sum(weights.values())
    if abs(total - 100) > 1:
        raise ValueError(f"{who}: weights sum to {total}, not 100. If a budget was split out, "
                         f"renormalise it in the file and say so, rather than leaving the "
                         f"arithmetic implicit")


def weights_by_kind(prof: dict) -> dict:
    """Collapse company-specific objectives into the two the engine understands."""
    obj = (prof or {}).get("objectives") or {}
    weights, kinds = obj.get("weights") or {}, obj.get("kinds") or {}
    out = {k: 0.0 for k in KINDS}
    for name, w in weights.items():
        out[kinds[name]] += w / 100.0
    return out


def separate_budget(prof: dict, objective: str) -> dict | None:
    """An objective funded outside the 100 points. Scored, but never ranked against them."""
    return ((prof or {}).get("objectives") or {}).get("separate_budgets", {}).get(objective)


if __name__ == "__main__":
    import json
    import sys
    p = load(sys.argv[1] if len(sys.argv) > 1 else "example-meridian")
    print(json.dumps({"weights_by_kind": weights_by_kind(p),
                      "recruitment_budget": separate_budget(p, "recruitment")}, indent=1))
