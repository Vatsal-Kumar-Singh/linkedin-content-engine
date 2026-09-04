"""Design critic — a separate agent that judges the RENDERED image, not the code.

Same principle as the copy gauntlet: the thing that made the artifact does not
grade it. The critic receives the PNG (and the measured geometry), never the
template source and never the generator's intent.
"""
from __future__ import annotations

import base64
import json
import os
from typing import Any, Callable, Dict, List, Optional

from ..config import Config
from ..models import _loads_lenient
from ..providers import build as build_provider
from ..providers.base import Provider, ProviderError
from .prompts import load_prompt


def _b64(path: str) -> str:
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode("ascii")


def critique(cfg: Config, pngs: List[str], measurements: List[Dict[str, Any]],
             draft, emit: Callable[[str], None] = lambda _s: None,
             fmt: str = "CARD", template: str = "") -> Dict[str, Any]:
    if not pngs:
        return {"status": "skipped", "note": "nothing rendered"}
    try:
        provider, note = build_provider(cfg, "design_critic")
    except ProviderError as exc:
        return {"status": "unavailable", "note": str(exc)}

    if not provider.supports_vision:
        return {"status": "skipped",
                "note": "configured design-critic provider is not vision-capable"}

    m = measurements[0] if measurements else {}
    ctx = {
        "measurements": {
            "smallest_text_px": m.get("smallest_text_px"),
            "overflow": m.get("overflow"),
            "guard_overflows": m.get("guard_overflows"),
            "autofit_adjustments": m.get("adjusted"),
            "canvas_utilization": m.get("canvas_utilization"),
            "type_scale_ratio": m.get("type_scale_ratio"),
            "distinct_type_sizes": m.get("distinct_type_sizes"),
            "largest_text_px": m.get("largest_text_px"),
            "headline_words": len((draft.creative_headline or "").split()),
            # A single-image card must carry the whole hierarchy alone. A
            # carousel cover leads a sequence, so its scale contrast is
            # legitimately shallower.
            "format": fmt,
            "template": template,
        }
    }
    user = (
        "The creative is attached. Supporting geometry measured from the rendered page:\n\n"
        "```json\n%s\n```\n\nJudge what you see."
        % json.dumps(ctx["measurements"], indent=2)
    )
    images = [_b64(p) for p in pngs[:3]] if not provider.is_mock else []

    try:
        raw = provider.complete(load_prompt("design_critic"), user,
                                task="design_critic", images=images, context=ctx)
        data = _loads_lenient(raw) if isinstance(raw, str) else raw
    except Exception as exc:
        return {"status": "error", "error": str(exc)}

    if not isinstance(data, dict):
        return {"status": "error", "error": "design critic returned a non-object"}

    data["status"] = "ok"
    data["critic_model"] = provider.model
    data["mock"] = provider.is_mock
    if note:
        data["note"] = note
    emit("  Design critic: %s%s" % (data.get("verdict", "?"),
                                    " (mock — geometry only)" if provider.is_mock else ""))
    return data
