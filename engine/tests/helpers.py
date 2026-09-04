"""Shared test fixtures."""
from __future__ import annotations

import os as _os
# Tests never hit a live provider. Without this, having ANTHROPIC_API_KEY set
# or the claude CLI on PATH turns unit tests into live calls.
_os.environ.setdefault("ENGINE_FORCE_MOCK", "1")

import json
import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from postengine.config import load as load_config          # noqa: E402
from postengine.models import ContentSpec, Draft           # noqa: E402
from postengine.providers.base import Provider             # noqa: E402

CFG = load_config()

BASE_SPEC = {
    "id": "test_spec", "pain_point": "A1", "family": "A", "persona": "cfo-procurement",
    "funnel_stage": "TOFU", "template": "CARD", "arc": "single stat",
    "content_type": "stat-creative", "angle": "cost-of-inaction",
    "working_title": "t", "value_shown": "v", "objective": "o",
    "metric_label": "no-hard-numbers", "constraints": [],
}

CLEAN_BODY = (
    "A pipeline stopped on Sunday night. Nobody was paged, because nothing was "
    "watching it. On Monday the dashboards still rendered, using Saturday's "
    "numbers."
    "\n\n"
    "On Tuesday someone in finance asked why the weekly report looked flat, and "
    "that was how the team found out. Two days of decisions had already been "
    "made on the old numbers."
    "\n\n"
    "The gap between a break and the discovery of it is the part nobody measures. "
    "It is also the part that decides whether anyone trusts the dashboard."
)


CLEAN_DRAFT = {
    # A draft that passes every shipped gate. It exists so a test can assert the
    # ABSENCE of a failure and mean it — if the baseline itself trips something,
    # every such test becomes noise.
    "hook": "Your pipeline broke on Sunday night.",
    "body": CLEAN_BODY,
    "cta": "How long would it take you to notice a pipeline had stopped?",
    "creative_headline": "Your pipeline broke on Sunday night",
    "creative_supporting_copy": "You found out on Tuesday, from a dashboard that was wrong.",
    "creative_qualifier": "",
    "focal": "Two days", "focal_unit": "", "eyebrow": "WHEN IT BREAKS",
    "visual_concept": "Statement card.",
    "alt_text": "Your pipeline broke on Sunday and you found out on Tuesday.",
}


def spec(**over: Any) -> ContentSpec:
    d = dict(BASE_SPEC)
    d.update(over)
    return ContentSpec.from_dict(d)


def draft(**over: Any) -> Draft:
    d = dict(CLEAN_DRAFT)
    d.update(over)
    s = over.pop("_spec", None)
    return Draft.from_model_json(d, s)


def failed_ids(report) -> List[str]:
    return [r.check_id for r in report.results if not r.passed]


class StubProvider(Provider):
    """A provider that returns exactly what a test tells it to."""
    is_mock = True
    supports_vision = True

    def __init__(self, responses: Dict[str, Any], family: str = "stub",
                 model: str = "stub-1") -> None:
        super().__init__(model)
        self.family = family
        self.name = "stub"
        self.responses = responses
        self.calls: List[Dict[str, Any]] = []

    def complete(self, system: str, user: str, *, task: str = "",
                 images: Optional[List[str]] = None,
                 context: Optional[Dict[str, Any]] = None) -> str:
        self.calls.append({"task": task, "system": system, "user": user})
        r = self.responses.get(task)
        if callable(r):
            r = r(len([c for c in self.calls if c["task"] == task]))
        if isinstance(r, str):
            return r
        return json.dumps(r)
