"""Run persistence. The iteration history is the product — nothing is overwritten."""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
from typing import Any, Dict, List, Optional

from .config import Config


def _now() -> _dt.datetime:
    return _dt.datetime.now()


class RunStore:
    def __init__(self, cfg: Config, spec_id: str, run_id: Optional[str] = None) -> None:
        self.cfg = cfg
        self.spec_id = spec_id
        configured = (cfg.engine.get("paths") or {}).get("runs", "runs")
        base = configured if os.path.isabs(configured) else os.path.join(cfg.root, configured)
        os.makedirs(base, exist_ok=True)
        self.run_id = run_id or self._allocate(base)
        self.dir = os.path.join(base, self.run_id)
        os.makedirs(self.dir, exist_ok=True)
        self.started = _now()

    def _allocate(self, base: str) -> str:
        day = _now().strftime("%Y-%m-%d")
        n = 1
        for name in os.listdir(base):
            m = re.match(r"^%s-(\d{3})" % re.escape(day), name)
            if m:
                n = max(n, int(m.group(1)) + 1)
        return "%s-%03d-%s" % (day, n, self.spec_id)

    # ------------------------------------------------------------------
    def path(self, *parts: str) -> str:
        return os.path.join(self.dir, *parts)

    def write_json(self, name: str, obj: Any) -> str:
        p = self.path(name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, ensure_ascii=False)
        return p

    def write_text(self, name: str, text: str) -> str:
        p = self.path(name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
        return p

    # ------------------------------------------------------------------
    def performance_skeleton(self) -> Dict[str, Any]:
        """The outer loop. Null until a real number is pasted in — never seeded
        with hypothetical data."""
        return {
            "run_id": self.run_id,
            "spec_id": self.spec_id,
            "published_at": None,
            "post_url": None,
            "metrics": {
                "impressions": None, "likes": None, "comments": None, "shares": None,
                "saves": None, "engagement_rate": None, "clicks": None,
                "qualified_conversations": None, "leads": None,
            },
            "benchmarks": dict(self.cfg.registry.get("benchmarks") or {}),
            "qualitative": {"this_is_us_comments": None, "notes": ""},
            "note": "Populate after publication. Comparison across runs is by "
                    "pain_point x angle x hook x template x funnel_stage, recorded in run_report.json.",
        }
