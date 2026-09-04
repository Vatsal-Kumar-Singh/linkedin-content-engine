"""Generator agent. Writes V1, then revises against structured feedback."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from ..config import Config
from ..models import ContentSpec, Draft, DraftError
from ..providers.base import Provider, ProviderError, TransientProviderError, with_retry
from .prompts import load_prompt


class Generator:
    def __init__(self, cfg: Config, provider: Provider) -> None:
        self.cfg = cfg
        self.provider = provider
        self.system = load_prompt("generator")

    # ------------------------------------------------------------------
    def generate(self, spec: ContentSpec) -> Draft:
        user = self._brief(spec)
        ctx = {"spec": spec.to_dict()}
        raw = self._call(self.system, user, task="generate", context=ctx)
        return Draft.from_model_json(raw, spec)

    # ------------------------------------------------------------------
    def revise(self, spec: ContentSpec, previous: Draft,
               fixes: List[Dict[str, Any]]) -> Draft:
        """The generator sees ONLY: its previous draft, the structured feedback,
        and the constraints. It never sees the judge's reasoning prose or scores —
        a score invites arguing with the number instead of fixing the text."""
        system = self.system + "\n\n---\n\n" + load_prompt("generator_revision")
        user = "\n\n".join([
            self._brief(spec),
            "## Your previous draft\n\n```json\n%s\n```"
            % json.dumps(previous.public_dict(), indent=2, ensure_ascii=False),
            "## Required fixes\n\n```json\n%s\n```"
            % json.dumps(fixes, indent=2, ensure_ascii=False),
        ])
        ctx = {"spec": spec.to_dict(), "previous_draft": previous.to_dict(), "fixes": fixes}
        raw = self._call(system, user, task="revise", context=ctx)
        return Draft.from_model_json(raw, spec)

    # ------------------------------------------------------------------
    def _brief(self, spec: ContentSpec) -> str:
        reg = self.cfg.registry
        pp = self.cfg.pain_point(spec.pain_point) or {}
        band = self._length_band(spec.template)
        lines = [
            "## This post",
            "",
            "| | |",
            "|---|---|",
            "| Pain point | **%s** — %s |" % (spec.pain_point, pp.get("title", "")),
            "| The value we provide | %s |" % pp.get("value", spec.value_shown),
            "| Family | %s — %s |" % (spec.family, (reg.get("families") or {}).get(spec.family, "")),
            "| Persona | %s |" % (reg.get("personas") or {}).get(spec.persona, spec.persona),
            "| Funnel stage | **%s** — %s |" % (
                spec.funnel_stage, (reg.get("funnel_stages") or {}).get(spec.funnel_stage, "")),
            "| Content type | %s |" % spec.content_type,
            "| Angle | %s |" % spec.angle,
            "| Template | **%s** |" % spec.template,
            "| Arc | %s — %s |" % (spec.arc, (reg.get("arcs") or {}).get(spec.arc, "")),
            "| Length band | %s |" % band,
            "| Metric labelling | **%s** |" % spec.metric_label,
            "",
            "**Working title (a direction, not a line to reuse):** %s" % spec.working_title,
            "",
            "**Objective:** %s" % spec.objective,
        ]
        if pp.get("constraint"):
            lines += ["", "**Pain-point constraint:** %s" % pp["constraint"]]
        if spec.constraints:
            lines += ["", "**Constraints for this specific post:**"]
            lines += ["- %s" % c for c in spec.constraints]
        if spec.metric_label in ("no-hard-numbers", "n/a"):
            lines += ["", "**The metric-labelling choice for this post is `%s`, so the creative "
                          "must carry no hard numbers at all.** Use a short phrase as the focal "
                          "element instead of a figure." % spec.metric_label]
        elif spec.metric_label == "illustrative":
            lines += ["", "**Metric labelling is `illustrative`.** Any figure must be visibly "
                          "labelled as an estimate or industry figure, not as our measured result."]
        elif spec.metric_label == "modelled-from-target-SLA":
            lines += ["", "**Metric labelling is `modelled-from-target-SLA`.** Any outcome figure "
                          "must be labelled a contractual target, on the creative as well as in "
                          "the caption."]
        return "\n".join(lines)

    def _length_band(self, template: str) -> str:
        for rule in self.cfg.rules.get("binary") or []:
            for chk in rule.get("checks") or []:
                if chk.get("type") == "length_range" and chk.get("applies_to_template") == template:
                    return "%s–%s %s (hook + body + CTA combined)" % (
                        chk["min"], chk["max"], chk.get("unit", "chars"))
        return "no band configured"

    # ------------------------------------------------------------------
    def _call(self, system: str, user: str, task: str, context: Dict[str, Any]) -> str:
        r = self.cfg.engine.get("retry") or {}

        def once() -> str:
            out = self.provider.complete(system, user, task=task, context=context)
            if not (out or "").strip():
                raise TransientProviderError("generator returned an empty response")
            return out

        return with_retry(once, int(r.get("attempts", 3)), list(r.get("backoff_seconds") or [2, 6]))
