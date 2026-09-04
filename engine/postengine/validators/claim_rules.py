"""Deterministic claim & policy validation.

Runs BEFORE any model call. Code evaluates objective constraints; the LLM judge
evaluates taste. Every rule here is compiled from config/claim-rules.yaml, so
adding a prohibition is a config edit, not a code change.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..config import Config, load as load_config
from ..models import CheckResult, DeterministicReport, ContentSpec, Draft

_SENTENCE_SPLIT = re.compile(r"[.!?]+(?:\s|$)")


def _sentences(text: str) -> List[str]:
    return [s for s in (p.strip() for p in _SENTENCE_SPLIT.split(text or "")) if s]


def _words(text: str) -> List[str]:
    return [w for w in re.split(r"\s+", (text or "").strip()) if w]


def _snippet(text: str, m: "re.Match", pad: int = 34) -> str:
    a = max(0, m.start() - pad)
    b = min(len(text), m.end() + pad)
    out = text[a:b].replace("\n", " ")
    return ("…" if a else "") + out.strip() + ("…" if b < len(text) else "")


class Validator:
    """Compiles config/claim-rules.yaml once, then validates drafts cheaply."""

    def __init__(self, cfg: Optional[Config] = None) -> None:
        self.cfg = cfg or load_config()
        self.rules = self.cfg.rules
        self.groups: Dict[str, List[str]] = self.rules.get("field_groups") or {}
        self.qualifiers: List[str] = self.rules.get("qualifier_tokens") or []
        self._compiled: Dict[str, "re.Pattern"] = {}
        self._compile_all()

    # ------------------------------------------------------------------
    def _rx(self, pattern: str, case_sensitive: bool = False) -> "re.Pattern":
        key = ("S:" if case_sensitive else "I:") + pattern
        if key not in self._compiled:
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                self._compiled[key] = re.compile(pattern, flags)
            except re.error as exc:
                raise ValueError("bad regex in claim-rules.yaml: %s (%s)" % (pattern, exc))
        return self._compiled[key]

    def _compile_all(self) -> None:
        """Fail loudly at startup rather than mid-run on a bad pattern."""
        for section in ("gates", "binary", "scored_mechanical"):
            for rule in self.rules.get(section) or []:
                for chk in rule.get("checks") or []:
                    for key in ("pattern", "number_pattern", "numerator_pattern"):
                        if chk.get(key):
                            self._rx(chk[key], bool(chk.get("case_sensitive")))
                    for fig in chk.get("figures") or []:
                        self._rx(fig["pattern"])

    # ------------------------------------------------------------------
    def _group_text(self, draft: Draft, group: str) -> List[Tuple[str, str]]:
        """Return [(field_name, text)] for a named field group."""
        fields = self.groups.get(group) or [group]
        return [(f, draft.field_text(f)) for f in fields]

    # Checks that depend only on the content spec, not on any generated text.
    SPEC_LEVEL = ("registry_membership", "blocked_topic", "required_enum")

    # ------------------------------------------------------------------
    def validate_spec(self, spec: ContentSpec) -> DeterministicReport:
        """Pre-flight. Some failures are knowable before a single token is spent
        — a blocked pain point, an unregistered one, a missing metric-labelling
        choice. Generating four drafts for a post that can never ship is waste,
        and it buries the real reason under quality feedback."""
        results: List[CheckResult] = []
        empty = Draft()
        for section in ("gates", "binary"):
            default_sev = "blocking" if section == "gates" else "fail"
            for rule in self.rules.get(section) or []:
                rule_sev = rule.get("severity", default_sev)
                for chk in rule.get("checks") or []:
                    if chk.get("type") not in self.SPEC_LEVEL:
                        continue
                    sev = chk.get("severity", rule_sev)
                    results.extend(self._run_check(chk, rule, sev, empty, spec))
        return DeterministicReport(rules_version=self.cfg.rules_version, results=results)

    # ------------------------------------------------------------------
    def validate(self, draft: Draft, spec: ContentSpec) -> DeterministicReport:
        results: List[CheckResult] = []
        for section in ("gates", "binary", "scored_mechanical"):
            default_sev = {"gates": "blocking", "binary": "fail",
                           "scored_mechanical": "fail"}[section]
            for rule in self.rules.get(section) or []:
                rule_sev = rule.get("severity", default_sev)
                for chk in rule.get("checks") or []:
                    sev = chk.get("severity", rule_sev)
                    results.extend(
                        self._run_check(chk, rule, sev, draft, spec)
                    )
        return DeterministicReport(rules_version=self.cfg.rules_version, results=results)

    # ------------------------------------------------------------------
    def _run_check(self, chk: Dict[str, Any], rule: Dict[str, Any], sev: str,
                   draft: Draft, spec: ContentSpec) -> List[CheckResult]:
        kind = chk.get("type")
        handler: Optional[Callable] = getattr(self, "_c_" + str(kind), None)
        if handler is None:
            return [self._res(chk, rule, "warn", False,
                              message="unknown check type %r in claim-rules.yaml" % kind)]

        # Template scoping — a DOC-only rule is not applicable to a CARD.
        applies = chk.get("applies_to_template")
        if applies and applies != spec.template:
            return []
        return handler(chk, rule, sev, draft, spec)

    def _res(self, chk: Dict[str, Any], rule: Dict[str, Any], sev: str, passed: bool,
             message: str = "", evidence: str = "", field: str = "") -> CheckResult:
        return CheckResult(
            check_id=chk.get("id", "?"),
            gate_id=rule.get("id", "?"),
            title=rule.get("title", ""),
            passed=passed,
            severity=sev,
            message=message or ("" if passed else chk.get("message", "")),
            fix="" if passed else chk.get("fix", ""),
            evidence=evidence,
            field=field,
            rubric_ref=rule.get("rubric_ref", ""),
        )

    # ==================================================================
    # check types
    # ==================================================================
    def _c_forbidden_pattern(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        rx = self._rx(chk["pattern"], bool(chk.get("case_sensitive")))
        for fname, text in self._group_text(draft, chk.get("scope", "all")):
            if not text:
                continue
            m = rx.search(text)
            if m:
                return [self._res(chk, rule, sev, False,
                                  evidence=_snippet(text, m), field=fname)]
        return [self._res(chk, rule, sev, True)]

    def _c_required_pattern(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        """The mirror of forbidden_pattern: the copy must contain this.

        Added for the subject-word rule. A reader scrolling past has two
        seconds; if the product they own is not named where they will actually
        look, the post reads as generic B2B and they scroll on. A category label
        in the corner does not count — the check is scoped to the fields that
        carry the message.
        """
        rx = self._rx(chk["pattern"], bool(chk.get("case_sensitive")))
        fields = [(f, t) for f, t in self._group_text(draft, chk.get("scope", "all"))]
        checked = [(f, t) for f, t in fields if (t or "").strip()]
        if not checked:
            return [self._res(chk, rule, sev, True)]

        if chk.get("in_any"):
            # Satisfied when at least one of the scoped fields carries it.
            for fname, text in checked:
                if rx.search(text):
                    return [self._res(chk, rule, sev, True)]
            return [self._res(chk, rule, sev, False,
                              evidence="not present in: %s"
                                       % ", ".join(f for f, _ in checked),
                              field=checked[0][0])]

        for fname, text in checked:
            if not rx.search(text):
                head = text.replace("\n", " ")[:70]
                return [self._res(chk, rule, sev, False,
                                  evidence="%s: %s%s" % (fname, head,
                                                         "…" if len(text) > 70 else ""),
                                  field=fname)]
        return [self._res(chk, rule, sev, True)]

    def _c_count_max(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        rx = self._rx(chk["pattern"], bool(chk.get("case_sensitive")))
        total, sample, where = 0, "", ""
        for fname, text in self._group_text(draft, chk.get("scope", "all")):
            ms = list(rx.finditer(text or ""))
            if ms and not sample:
                sample, where = _snippet(text, ms[0]), fname
            total += len(ms)
        limit = int(chk.get("max", 0))
        if total > limit:
            return [self._res(chk, rule, sev, False,
                              evidence="%d occurrences (limit %d) — e.g. %s" % (total, limit, sample),
                              field=where)]
        return [self._res(chk, rule, sev, True)]

    def _c_ratio_max(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        rx = self._rx(chk["numerator_pattern"])
        num, den = 0, 0
        for _fname, text in self._group_text(draft, chk.get("scope", "caption")):
            num += len(rx.findall(text or ""))
            den += len(_sentences(text)) if chk.get("denominator") == "sentences" else 1
        if den == 0:
            return [self._res(chk, rule, sev, True)]
        ratio = num / float(den)
        if ratio > float(chk.get("max", 1.0)):
            return [self._res(chk, rule, sev, False,
                              evidence="%d matches across %d sentences (ratio %.2f, limit %.2f)"
                                       % (num, den, ratio, float(chk["max"])))]
        return [self._res(chk, rule, sev, True)]

    def _c_requires_qualifier(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        """A figure must carry a qualifier — and gate A2 requires it in the SAME
        field group, because captions truncate and images get screenshotted."""
        tokens = chk.get("qualifier_override") or self.qualifiers
        qrx = self._rx("|".join(re.escape(t) for t in tokens))
        window = int(chk.get("window", 160))
        per_group = bool(chk.get("per_group"))

        out: List[CheckResult] = []
        group_names = ["caption", "creative"] if per_group else ["all"]
        failed = False
        for gname in group_names:
            gtext = "\n".join(t for _f, t in self._group_text(draft, gname))
            if not gtext:
                continue
            for fig in chk.get("figures") or []:
                frx = self._rx(fig["pattern"])
                for m in frx.finditer(gtext):
                    lo = max(0, m.start() - window)
                    hi = min(len(gtext), m.end() + window)
                    if not qrx.search(gtext[lo:hi]):
                        failed = True
                        out.append(self._res(
                            chk, rule, sev, False,
                            message="%s — %s" % (chk.get("message", ""), fig["name"]),
                            evidence="in %s: %s" % (gname, _snippet(gtext, m)),
                            field=gname))
                        break
        if not failed:
            out.append(self._res(chk, rule, sev, True))
        return out

    def _c_required_enum(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        value = getattr(spec, chk["field"], None) or getattr(draft, chk["field"], None)
        if value in (chk.get("allowed") or []):
            return [self._res(chk, rule, sev, True)]
        return [self._res(chk, rule, sev, False,
                          evidence="%s = %r" % (chk["field"], value), field=chk["field"])]

    def _c_label_consistency(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        if spec.metric_label not in (chk.get("when_label") or []):
            return [self._res(chk, rule, sev, True)]
        rx = self._rx(chk["number_pattern"])
        for fname, text in self._group_text(draft, chk.get("forbid_numbers_in", "creative")):
            m = rx.search(text or "")
            if m:
                return [self._res(chk, rule, sev, False,
                                  evidence="metric_label=%s but creative contains: %s"
                                           % (spec.metric_label, _snippet(text, m)),
                                  field=fname)]
        return [self._res(chk, rule, sev, True)]

    def _c_qualifier_on_creative(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        """Gate A2's second half: the qualifier must live on the creative itself."""
        if spec.metric_label not in (chk.get("when_label") or []):
            return [self._res(chk, rule, sev, True)]
        fields = chk.get("fields") or [chk.get("field", "creative_qualifier")]
        qrx = self._rx("|".join(re.escape(t) for t in self.qualifiers))
        seen = []
        for fname in fields:
            text = draft.field_text(fname).strip()
            seen.append("%s=%r" % (fname, text[:52]))
            if text and qrx.search(text):
                return [self._res(chk, rule, sev, True)]
        return [self._res(chk, rule, sev, False,
                          evidence="metric_label=%s; %s" % (spec.metric_label, "; ".join(seen)),
                          field=fields[0])]

    def _c_registry_membership(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        value = getattr(spec, chk["field"], None)
        registry = self.cfg.registry.get(chk.get("registry", "pain_points")) or {}
        excluded = chk.get("excluded") or []
        if value not in registry:
            return [self._res(chk, rule, sev, False,
                              evidence="%s = %r is not in the register" % (chk["field"], value),
                              field=chk["field"])]
        if value in excluded:
            return [self._res(chk, rule, sev, False,
                              evidence="%s is excluded from LinkedIn" % value, field=chk["field"])]
        entry = registry.get(value) or {}
        if entry.get("excluded_from_linkedin"):
            return [self._res(chk, rule, sev, False,
                              evidence="%s: %s" % (value, entry["excluded_from_linkedin"]),
                              field=chk["field"])]
        return [self._res(chk, rule, sev, True)]

    def _c_blocked_topic(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        blocked = chk.get("blocked") or {}
        reason = blocked.get(spec.pain_point)
        # A pain point may also be marked blocked in the registry itself.
        entry = self.cfg.pain_point(spec.pain_point) or {}
        reason = reason or entry.get("blocked")
        if reason:
            return [self._res(chk, rule, sev, False,
                              evidence="%s: %s" % (spec.pain_point, reason), field="pain_point")]
        return [self._res(chk, rule, sev, True)]

    def _c_length_range(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        text = draft.field_text(chk.get("field", "caption_text"))
        n = len(text) if chk.get("unit", "chars") == "chars" else len(_words(text))
        unit = chk.get("unit", "chars")
        lo, hi = int(chk["min"]), int(chk["max"])
        if lo <= n <= hi:
            return [self._res(chk, rule, sev, True)]
        return [self._res(chk, rule, sev, False,
                          evidence="%d %s (band %d–%d)" % (n, unit, lo, hi),
                          field=chk.get("field", "caption_text"))]

    def _c_word_count(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        n = len(_words(draft.field_text(chk["field"])))
        hi = int(chk.get("max", 10**9))
        warn_above = chk.get("warn_above")
        if n > hi:
            return [self._res(chk, rule, sev, False,
                              evidence="%s is %d words (limit %d)" % (chk["field"], n, hi),
                              field=chk["field"])]
        if warn_above is not None and n > int(warn_above):
            return [self._res(chk, rule, "warn", False,
                              message="%s is %d words. Under %d outperforms longer by ~40%%."
                                      % (chk["field"], n, int(warn_above) + 1),
                              evidence=draft.field_text(chk["field"]), field=chk["field"])]
        return [self._res(chk, rule, sev, True)]

    def _c_slide_count(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        n = len(draft.slides)
        lo, hi = int(chk["min"]), int(chk["max"])
        if lo <= n <= hi:
            return [self._res(chk, rule, sev, True)]
        return [self._res(chk, rule, sev, False,
                          evidence="%d slides (band %d–%d)" % (n, lo, hi), field="slides")]

    def _c_slide_limits(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        problems = []
        for i, s in enumerate(draft.slides, 1):
            hw = len(_words(s.headline))
            if not (int(chk["headline_min_words"]) <= hw <= int(chk["headline_max_words"])):
                problems.append("slide %d headline is %d words (need %s–%s)"
                                % (i, hw, chk["headline_min_words"], chk["headline_max_words"]))
            if len(_sentences(s.body)) > int(chk["max_sentences"]):
                problems.append("slide %d body has %d sentences (max %s)"
                                % (i, len(_sentences(s.body)), chk["max_sentences"]))
            blocks = [b for b in (s.headline, s.body) if b.strip()]
            if len(blocks) > int(chk["max_blocks"]):
                problems.append("slide %d has %d text blocks (max %s)"
                                % (i, len(blocks), chk["max_blocks"]))
        if problems:
            return [self._res(chk, rule, sev, False,
                              evidence="; ".join(problems[:4]), field="slides")]
        return [self._res(chk, rule, sev, True)]

    def _c_cta_present(self, chk, rule, sev, draft, spec) -> List[CheckResult]:
        cta = (draft.cta or "").strip()
        if cta:
            return [self._res(chk, rule, sev, True)]
        return [self._res(chk, rule, sev, False, field="cta")]


def validate(draft: Draft, spec: ContentSpec, cfg: Optional[Config] = None) -> DeterministicReport:
    return Validator(cfg).validate(draft, spec)
