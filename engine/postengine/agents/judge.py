"""Judge agent — and the context firewall that makes the gauntlet real.

The requirement is that the generator does not grade its own work. That is only
true if the judge physically cannot reach the generator's state. `JudgePacket`
is the enforcement: it is a frozen dataclass with a fixed field set, it is the
only thing the judge prompt is built from, and it is constructed by an explicit
allowlist rather than by copying a draft object.

Specifically the judge never receives:
  · the generator's private reasoning or self-assessment
  · the generator's system prompt or brief
  · its own previous scores, verdicts or reasoning  (fresh context every pass)
  · the deterministic validator's findings          (avoids anchoring)
  · constraints/decisions-log.md or claim-evidence-register.md  (internal)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional

from ..config import Config
from ..models import ContentSpec, Draft, DraftError, JudgeReport
from ..providers.base import Provider, ProviderError, TransientProviderError, with_retry
from .prompts import load_prompt

# The complete set of draft fields the judge may see. Anything not on this list
# cannot reach the judge, whatever the generator puts in the draft object.
ALLOWED_DRAFT_FIELDS = (
    "hook", "hook_alternatives", "body", "cta",
    "creative_headline", "creative_supporting_copy", "creative_qualifier",
    "creative_strip", "source_label", "comparison_rows", "steps",
    "left_label", "right_label", "prop_label_a", "prop_label_b", "frag_note", "counter",
    "eyebrow", "focal", "focal_unit", "visual_concept", "alt_text",
    "first_comment", "slides", "claims_used", "claim_qualifiers", "sources_used",
)


@dataclass(frozen=True)
class JudgePacket:
    """Everything the judge is allowed to know. Frozen on purpose."""
    draft: Dict[str, Any]
    objective: str
    declared_tier: str
    template: str
    pain_point_id: str
    pain_point_summary: str
    length_band: str
    rubric_version: str

    @staticmethod
    def build(cfg: Config, draft: Draft, spec: ContentSpec, length_band: str) -> "JudgePacket":
        public = draft.public_dict()
        safe = {k: public[k] for k in ALLOWED_DRAFT_FIELDS if k in public}
        if spec.template != "DOC":
            safe.pop("slides", None)
        pp = cfg.pain_point(spec.pain_point) or {}
        return JudgePacket(
            draft=safe,
            objective=spec.objective,
            declared_tier=spec.funnel_stage,
            template=spec.template,
            pain_point_id=spec.pain_point,
            pain_point_summary=str(pp.get("title", "")),
            length_band=length_band,
            rubric_version=cfg.rubric_version,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def render(self) -> str:
        return "\n\n".join([
            "## Content objective",
            self.objective,
            "## Declared classification (assess it, do not assume it)",
            "- Intent tier: **%s**\n- Template: **%s**\n- Pain point: **%s** — %s"
            % (self.declared_tier, self.template, self.pain_point_id, self.pain_point_summary),
            "## Length band for this format",
            "%s. Length is capped here and earns nothing beyond it." % self.length_band,
            "## The draft",
            "```json\n%s\n```" % json.dumps(self.draft, indent=2, ensure_ascii=False),
        ])


class Judge:
    def __init__(self, cfg: Config, provider: Provider) -> None:
        self.cfg = cfg
        self.provider = provider
        self.system = load_prompt("judge")

    def evaluate(self, draft: Draft, spec: ContentSpec, length_band: str) -> JudgeReport:
        """One evaluation, in a fresh context. No history is carried between passes."""
        packet = JudgePacket.build(self.cfg, draft, spec, length_band)
        raw = self._call(packet)
        try:
            report = JudgeReport.from_model_json(
                raw, rubric_version=self.cfg.rubric_version, judge_model=self.provider.model)
        except DraftError as exc:
            # A judge that cannot produce a usable verdict must not silently
            # become a pass. It becomes an explicit, recorded failure.
            report = JudgeReport(
                reasoning="", verdict="BLOCKED",
                scores={k: 0 for k in JudgeReport.SCORED},
                error="judge output unusable: %s" % exc,
                raw=str(raw)[:4000],
                rubric_version=self.cfg.rubric_version, judge_model=self.provider.model)
        return report

    def packet_for(self, draft: Draft, spec: ContentSpec, length_band: str) -> JudgePacket:
        return JudgePacket.build(self.cfg, draft, spec, length_band)

    # ------------------------------------------------------------------
    def _call(self, packet: JudgePacket) -> str:
        r = self.cfg.engine.get("retry") or {}
        retry_on = set((r.get("retry_on") or []))

        def once() -> str:
            out = self.provider.complete(
                self.system, packet.render(), task="judge",
                # Only fields that are already rendered into the prompt above.
                context={"draft": packet.draft, "objective": packet.objective,
                         "declared_tier": packet.declared_tier,
                         "template": packet.template,
                         "pain_point_id": packet.pain_point_id})
            if not (out or "").strip():
                raise TransientProviderError("judge returned an empty response")
            if "malformed_json" in retry_on:
                # A malformed response is worth one more attempt before it is
                # recorded as a failure — models recover from this often.
                try:
                    JudgeReport.from_model_json(
                        out, rubric_version=self.cfg.rubric_version,
                        judge_model=self.provider.model)
                except DraftError as exc:
                    raise TransientProviderError("malformed judge JSON: %s" % exc)
            return out

        try:
            return with_retry(once, int(r.get("attempts", 3)),
                              list(r.get("backoff_seconds") or [2, 6]))
        except ProviderError as exc:
            return json.dumps({"reasoning": "", "verdict": "BLOCKED",
                               "scores": {}, "error": str(exc)})
