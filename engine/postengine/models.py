"""Schemas for everything that crosses a boundary.

Plain dataclasses rather than pydantic: the only validation we need is
"did the model return the fields we asked for", and doing that by hand keeps
the failure messages specific enough to feed back to the generator.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

# --------------------------------------------------------------------------
# Content spec — the engine's input
# --------------------------------------------------------------------------


@dataclass
class ContentSpec:
    id: str
    pain_point: str
    family: str
    persona: str
    funnel_stage: str
    template: str
    arc: str
    content_type: str
    angle: str
    working_title: str
    value_shown: str
    objective: str
    metric_label: str
    constraints: List[str] = field(default_factory=list)
    backlog_id: Optional[str] = None
    round: Optional[int] = None
    tier_human_confirmed: bool = False
    performance_tracking: bool = True

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ContentSpec":
        known = {f for f in cls.__dataclass_fields__}
        missing = [
            k for k in ("id", "pain_point", "funnel_stage", "template", "objective")
            if not d.get(k)
        ]
        if missing:
            raise SpecError("content spec is missing required field(s): %s" % ", ".join(missing))
        clean = {k: v for k, v in d.items() if k in known}
        clean.setdefault("family", str(d.get("pain_point", "?"))[0])
        for k in ("working_title", "value_shown", "objective"):
            if isinstance(clean.get(k), str):
                clean[k] = " ".join(clean[k].split())
        return cls(**clean)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# A model that returns a runaway response must not become a runaway prompt to
# the next agent. Well past any legitimate LinkedIn post, but a hard stop.
MAX_DRAFT_CHARS = 60000

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _clean(text: str) -> str:
    """Strip control characters. They survive JSON, break HTML rendering, and
    can hide content from a regex that a reader would still see."""
    return _CONTROL.sub("", text or "")


class SpecError(ValueError):
    """A content spec could not be loaded."""


class DraftError(ValueError):
    """A model returned something that is not a usable draft."""


# --------------------------------------------------------------------------
# Draft — the generator's output. This is the contract with the judge.
# --------------------------------------------------------------------------

DRAFT_PUBLIC_FIELDS = (
    "pain_point", "persona", "funnel_stage", "content_type", "angle",
    "hook", "body", "cta", "creative_headline", "creative_supporting_copy",
    "creative_qualifier", "creative_strip", "source_label",
    "comparison_rows", "steps", "left_label", "right_label",
    "prop_label_a", "prop_label_b", "frag_note", "counter",
    "eyebrow", "focal", "focal_unit",
    "visual_concept", "claims_used", "claim_qualifiers", "sources_used",
    "metric_label", "alt_text", "slides", "first_comment",
)

# `cta` is deliberately NOT required at the schema layer. An absent CTA is a
# content decision the rubric has an opinion about (binary B12), so it must reach
# the validator as a named, fixable failure rather than dying as a parse error.
REQUIRED_DRAFT_FIELDS = (
    "hook", "body", "creative_headline", "visual_concept",
)


@dataclass
class Slide:
    headline: str
    body: str = ""
    kind: str = "point"          # cover | point | turn | close

    @classmethod
    def from_any(cls, v: Any) -> "Slide":
        if isinstance(v, str):
            return cls(headline=_clean(v).strip())
        if isinstance(v, dict):
            return cls(
                headline=_clean(str(v.get("headline") or v.get("title") or "")).strip(),
                body=_clean(str(v.get("body") or v.get("text") or "")).strip(),
                kind=str(v.get("kind") or "point"),
            )
        raise DraftError("slide is neither a string nor an object: %r" % (v,))


@dataclass
class Draft:
    """One version of a post. Every field here is publishable-facing.

    Anything the generator thinks privately lives in `private_reasoning` and is
    never included in `public_dict()` — which is the only thing the judge sees.
    """
    hook: str = ""
    body: str = ""
    cta: str = ""
    creative_headline: str = ""
    creative_supporting_copy: str = ""
    # Gate A2 requires the qualifier to be ON the creative. It is an explicit
    # field so that what the validator scans is exactly what the renderer draws.
    creative_qualifier: str = ""
    # A designed context strip on the creative — label/value cells. This is
    # where a qualifier lives now: as a labelled fact, not a disclaimer pill.
    creative_strip: List[Dict[str, str]] = field(default_factory=list)
    source_label: str = ""
    # Structured creative content for the comparison / journey / framework
    # templates. Absent for a stat or statement card.
    comparison_rows: List[Dict[str, str]] = field(default_factory=list)
    steps: List[Dict[str, str]] = field(default_factory=list)
    left_label: str = ""
    right_label: str = ""
    # Labels for the proportion bar on a share-based stat card, and the note
    # beside the system fragment when the figure is not a share.
    prop_label_a: str = ""
    prop_label_b: str = ""
    frag_note: str = ""
    counter: str = ""     # carousel slide indicator on an editorial cover
    eyebrow: str = ""
    focal: str = ""
    focal_unit: str = ""
    visual_concept: str = ""
    alt_text: str = ""
    first_comment: str = ""
    pain_point: str = ""
    persona: str = ""
    funnel_stage: str = ""
    content_type: str = ""
    angle: str = ""
    metric_label: str = ""
    claims_used: List[str] = field(default_factory=list)
    claim_qualifiers: List[str] = field(default_factory=list)
    sources_used: List[str] = field(default_factory=list)
    slides: List[Slide] = field(default_factory=list)
    hook_alternatives: List[str] = field(default_factory=list)

    # --- generator-private. NEVER crosses to the judge. --------------------
    private_reasoning: str = ""
    private_self_assessment: str = ""

    # ----------------------------------------------------------------------
    @classmethod
    def from_model_json(cls, raw: Any, spec: Optional[ContentSpec] = None) -> "Draft":
        if isinstance(raw, str):
            raw = _loads_lenient(raw)
        if not isinstance(raw, dict):
            raise DraftError("generator returned %s, not a JSON object" % type(raw).__name__)

        size = len(json.dumps(raw, default=str))
        if size > MAX_DRAFT_CHARS:
            raise DraftError(
                "draft is %d characters, over the %d hard cap. Something has run away — "
                "it is not being sent on to the judge." % (size, MAX_DRAFT_CHARS))

        missing = [f for f in REQUIRED_DRAFT_FIELDS if not str(raw.get(f) or "").strip()]
        if missing:
            raise DraftError("draft is missing required field(s): %s" % ", ".join(missing))

        def s(k: str) -> str:
            return _clean(str(raw.get(k) or "")).strip()

        def lst(k: str) -> List[str]:
            v = raw.get(k) or []
            if isinstance(v, str):
                v = [v]
            if not isinstance(v, list):
                return []
            return [_clean(str(x)).strip() for x in v if str(x).strip()]

        slides = [Slide.from_any(x) for x in (raw.get("slides") or [])]

        d = cls(
            hook=s("hook"), body=s("body"), cta=s("cta"),
            creative_headline=s("creative_headline"),
            creative_supporting_copy=s("creative_supporting_copy"),
            creative_qualifier=s("creative_qualifier"),
            creative_strip=_strip(raw.get("creative_strip")),
            source_label=s("source_label"),
            comparison_rows=_pairs(raw.get("comparison_rows"), ("old", "new")),
            steps=_pairs(raw.get("steps"), ("title", "body")),
            left_label=s("left_label"), right_label=s("right_label"),
            prop_label_a=s("prop_label_a"), prop_label_b=s("prop_label_b"),
            frag_note=s("frag_note"), counter=s("counter"),
            eyebrow=s("eyebrow"), focal=s("focal"), focal_unit=s("focal_unit"),
            visual_concept=s("visual_concept"), alt_text=s("alt_text"),
            first_comment=s("first_comment"),
            pain_point=s("pain_point"), persona=s("persona"),
            funnel_stage=s("funnel_stage"), content_type=s("content_type"),
            angle=s("angle"), metric_label=s("metric_label"),
            claims_used=lst("claims_used"), claim_qualifiers=lst("claim_qualifiers"),
            sources_used=lst("sources_used"), slides=slides,
            hook_alternatives=lst("hook_alternatives"),
            private_reasoning=str(raw.get("private_reasoning") or ""),
            private_self_assessment=str(raw.get("private_self_assessment") or ""),
        )
        # The spec is authoritative for the matrix cell and the A4 label. A model
        # is not permitted to reclassify its own post or relabel its own metrics.
        if spec is not None:
            d.pain_point = spec.pain_point
            d.persona = spec.persona
            d.funnel_stage = spec.funnel_stage
            d.content_type = spec.content_type
            d.angle = spec.angle
            d.metric_label = spec.metric_label
        return d

    # ----------------------------------------------------------------------
    def public_dict(self) -> Dict[str, Any]:
        """Exactly what may leave the generator. The judge sees this and nothing else."""
        out: Dict[str, Any] = {}
        for k in DRAFT_PUBLIC_FIELDS:
            v = getattr(self, k, None)
            if k == "slides":
                out[k] = [asdict(s) for s in self.slides]
            else:
                out[k] = v
        return out

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["slides"] = [asdict(s) for s in self.slides]
        return d

    # --- convenience views used by the validator --------------------------
    def caption_text(self) -> str:
        return "\n\n".join(x for x in (self.hook, self.body, self.cta) if x).strip()

    def field_text(self, name: str) -> str:
        if name == "slides":
            return "\n".join((s.headline + " " + s.body).strip() for s in self.slides)
        if name == "creative_strip":
            return "\n".join("%s %s" % (c.get("label", ""), c.get("value", ""))
                              for c in self.creative_strip)
        if name in ("comparison_rows", "steps"):
            return "\n".join(" ".join(str(x) for x in c.values())
                              for c in getattr(self, name))
        if name == "caption_text":
            return self.caption_text()
        value = getattr(self, name, "")
        if isinstance(value, (list, tuple)):
            return "\n".join(str(v) for v in value)
        return str(value or "")


def _strip(v: Any) -> List[Dict[str, str]]:
    """Normalise the creative context strip to [{label, value}]."""
    out: List[Dict[str, str]] = []
    if not isinstance(v, list):
        return out
    for item in v[:4]:
        if isinstance(item, dict):
            label = _clean(str(item.get("label") or item.get("k") or "")).strip()
            value = _clean(str(item.get("value") or item.get("v") or "")).strip()
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            label, value = _clean(str(item[0])).strip(), _clean(str(item[1])).strip()
        else:
            continue
        if value:
            out.append({"label": label, "value": value})
    return out


def _pairs(v: Any, keys: tuple) -> List[Dict[str, str]]:
    """Normalise structured creative content to a list of two-key dicts."""
    out: List[Dict[str, str]] = []
    if not isinstance(v, list):
        return out
    a, b = keys
    alias = {"old": ("old", "left", "before"), "new": ("new", "right", "after"),
             "title": ("title", "headline", "label"), "body": ("body", "text", "detail")}
    for item in v[:6]:
        if isinstance(item, dict):
            av = next((item[k] for k in alias.get(a, (a,)) if item.get(k)), "")
            bv = next((item[k] for k in alias.get(b, (b,)) if item.get(k)), "")
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            av, bv = item[0], item[1]
        else:
            continue
        av, bv = _clean(str(av)).strip(), _clean(str(bv)).strip()
        if av or bv:
            out.append({a: av, b: bv})
    return out


def _loads_lenient(text: str) -> Any:
    """Parse JSON from a model that may have wrapped it in prose or a fence."""
    text = (text or "").strip()
    if not text:
        raise DraftError("model returned an empty response")
    try:
        return json.loads(text)
    except Exception:
        pass
    # fenced block
    if "```" in text:
        parts = text.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("json"):
                p = p[4:].strip()
            if p.startswith("{") or p.startswith("["):
                try:
                    return json.loads(p)
                except Exception:
                    continue
    # first balanced object
    start = text.find("{")
    if start != -1:
        depth, in_str, esc = 0, False, False
        for i in range(start, len(text)):
            c = text[i]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
                continue
            if c == '"':
                in_str = True
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except Exception:
                        break
    raise DraftError("could not parse JSON from model response (%d chars)" % len(text))


# --------------------------------------------------------------------------
# Deterministic validation results
# --------------------------------------------------------------------------


@dataclass
class CheckResult:
    check_id: str
    gate_id: str
    title: str
    passed: bool
    severity: str                 # blocking | fail | warn
    message: str = ""
    fix: str = ""
    evidence: str = ""
    field: str = ""
    rubric_ref: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class DeterministicReport:
    rules_version: str
    results: List[CheckResult] = field(default_factory=list)

    @property
    def blocking_failures(self) -> List[CheckResult]:
        return [r for r in self.results if not r.passed and r.severity == "blocking"]

    @property
    def binary_failures(self) -> List[CheckResult]:
        return [r for r in self.results if not r.passed and r.severity == "fail"]

    @property
    def warnings(self) -> List[CheckResult]:
        return [r for r in self.results if not r.passed and r.severity == "warn"]

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed_count(self) -> int:
        return sum(1 for r in self.results if not r.passed and r.severity != "warn")

    @property
    def ok(self) -> bool:
        return not self.blocking_failures and not self.binary_failures

    def auto_zero_brand_voice(self) -> bool:
        return any(r.gate_id == "C3" and not r.passed and r.severity == "fail"
                   for r in self.results)

    def fixes(self) -> List[Dict[str, str]]:
        return [
            {"id": r.check_id, "severity": r.severity, "problem": r.message,
             "fix": r.fix, "evidence": r.evidence, "field": r.field}
            for r in self.results if not r.passed
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rules_version": self.rules_version,
            "passed": self.passed_count,
            "failed": self.failed_count,
            "warnings": len(self.warnings),
            "blocking_failures": [r.check_id for r in self.blocking_failures],
            "ok": self.ok,
            "results": [r.to_dict() for r in self.results],
        }


# --------------------------------------------------------------------------
# Judge output
# --------------------------------------------------------------------------

VALID_VERDICTS = ("SHIP", "REVISE", "BLOCKED")


@dataclass
class Fix:
    criterion: str
    problem: str
    fix: str
    replacement: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class JudgeReport:
    reasoning: str = ""
    binary: Dict[str, bool] = field(default_factory=dict)
    scores: Dict[str, int] = field(default_factory=dict)
    verdict: str = "REVISE"
    fixes: List[Fix] = field(default_factory=list)
    human_flags: List[str] = field(default_factory=list)
    raw: str = ""
    error: str = ""
    rubric_version: str = ""
    judge_model: str = ""

    SCORED = ("C1", "C2", "C3", "C4")

    @classmethod
    def from_model_json(cls, raw: Any, rubric_version: str = "", judge_model: str = "") -> "JudgeReport":
        original = raw if isinstance(raw, str) else json.dumps(raw)
        if isinstance(raw, str):
            raw = _loads_lenient(raw)
        if not isinstance(raw, dict):
            raise DraftError("judge returned %s, not a JSON object" % type(raw).__name__)

        reasoning = str(raw.get("reasoning") or "").strip()
        if not reasoning:
            raise DraftError("judge returned no reasoning — reason-before-score is mandatory")

        binary: Dict[str, bool] = {}
        for k, v in (raw.get("binary") or {}).items():
            key = str(k).strip().upper()
            if isinstance(v, bool):
                binary[key] = v
            elif isinstance(v, str):
                binary[key] = v.strip().lower() in ("true", "pass", "yes", "y", "✓")

        scores: Dict[str, int] = {}
        for k in cls.SCORED:
            v = (raw.get("scores") or {}).get(k)
            if v is None:
                continue
            try:
                f = float(v)
            except (TypeError, ValueError):
                raise DraftError("judge score for %s is not a number: %r" % (k, v))
            # The scale is 0–3 integers. A fractional score is a malformed
            # response, not a nuance — rounding 2.6 up to 3 would quietly turn a
            # REVISE into a SHIP.
            if abs(f - round(f)) > 1e-9:
                raise DraftError(
                    "judge score for %s is fractional (%r). The scale is 0-3 integers." % (k, v))
            n = int(round(f))
            if not 0 <= n <= 3:
                raise DraftError("judge score for %s is out of the 0–3 range: %r" % (k, v))
            scores[k] = n
        missing = [k for k in cls.SCORED if k not in scores]
        if missing:
            raise DraftError("judge omitted score(s): %s" % ", ".join(missing))

        verdict = str(raw.get("verdict") or "").strip().upper()
        if verdict not in VALID_VERDICTS:
            verdict = "REVISE"

        fixes = []
        for f in (raw.get("fixes") or []):
            if isinstance(f, str):
                fixes.append(Fix(criterion="?", problem=f, fix=f))
            elif isinstance(f, dict):
                fixes.append(Fix(
                    criterion=str(f.get("criterion") or f.get("id") or "?"),
                    problem=str(f.get("problem") or ""),
                    fix=str(f.get("fix") or ""),
                    replacement=str(f.get("replacement") or ""),
                ))

        hf = raw.get("human_flags") or []
        if isinstance(hf, str):
            hf = [hf]

        return cls(
            reasoning=reasoning, binary=binary, scores=scores, verdict=verdict,
            fixes=fixes, human_flags=[str(x) for x in hf], raw=original,
            rubric_version=rubric_version, judge_model=judge_model,
        )

    # ----------------------------------------------------------------------
    @property
    def scored_total(self) -> int:
        return sum(self.scores.get(k, 0) for k in self.SCORED)

    @property
    def binary_pass_rate(self) -> float:
        if not self.binary:
            return 1.0
        return sum(1 for v in self.binary.values() if v) / float(len(self.binary))

    def zero_brand_voice(self) -> bool:
        return self.scores.get("C3", 3) == 0

    def unfixed(self) -> List[Fix]:
        """Sub-3 criteria and failed binaries must each carry a specific fix."""
        need = {k for k, v in self.scores.items() if v < 3}
        need |= {k for k, v in self.binary.items() if not v}
        have = {f.criterion for f in self.fixes}
        return [Fix(criterion=c, problem="no specific fix supplied by the judge",
                    fix="") for c in sorted(need - have)]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rubric_version": self.rubric_version,
            "judge_model": self.judge_model,
            "reasoning": self.reasoning,
            "binary": self.binary,
            "binary_pass_rate": round(self.binary_pass_rate, 3),
            "scores": self.scores,
            "scored_total": self.scored_total,
            "verdict": self.verdict,
            "fixes": [f.to_dict() for f in self.fixes],
            "human_flags": self.human_flags,
            "error": self.error,
        }
