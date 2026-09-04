"""The gauntlet. Generate → validate deterministically → judge independently → revise."""
from __future__ import annotations

import copy
import datetime as _dt
import os
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .agents import Generator, Judge
from .config import Config, load as load_config
from .models import ContentSpec, DeterministicReport, Draft, DraftError, JudgeReport
from .providers import assert_independent, build as build_provider
from .providers.base import ProviderError
from .store import RunStore
from .validators import Validator

Emit = Callable[[str], None]


def _noop(_: str) -> None:
    pass


# --------------------------------------------------------------------------


@dataclass
class Iteration:
    n: int
    draft: Draft
    deterministic: DeterministicReport
    judge: JudgeReport
    fixes_sent_to_generator: List[Dict[str, Any]] = field(default_factory=list)
    error: str = ""

    def combined_binary(self) -> Dict[str, bool]:
        """Deterministic binary checks and the judge's binary checks, merged.
        A deterministic FAIL always wins — code beats opinion on objective facts."""
        out: Dict[str, bool] = dict(self.judge.binary)
        for r in self.deterministic.results:
            if r.severity != "fail":
                continue
            gid = r.gate_id
            out[gid] = out.get(gid, True) and r.passed
        return out

    def binary_pass_rate(self) -> float:
        b = self.combined_binary()
        return (sum(1 for v in b.values() if v) / float(len(b))) if b else 1.0

    def to_dict(self) -> Dict[str, Any]:
        b = self.combined_binary()
        return {
            "iteration": self.n,
            "error": self.error,
            "draft": self.draft.to_dict() if self.draft else None,
            "draft_seen_by_judge": self.draft.public_dict() if self.draft else None,
            "deterministic": self.deterministic.to_dict() if self.deterministic else None,
            "judge": self.judge.to_dict() if self.judge else None,
            "combined_binary": b,
            "binary_pass_rate": round(self.binary_pass_rate(), 3),
            "scored_total": self.judge.scored_total if self.judge else 0,
            "fixes_sent_to_generator": self.fixes_sent_to_generator,
        }


@dataclass
class RunResult:
    run_id: str
    directory: str
    spec: ContentSpec
    iterations: List[Iteration]
    status: str
    reasons: List[str]
    stamp: Dict[str, Any]
    provider_info: Dict[str, Any]
    creative: Dict[str, Any] = field(default_factory=dict)
    creative_draft: Optional[Draft] = None
    error: str = ""

    @property
    def final(self) -> Optional[Iteration]:
        """The best draft produced, not merely the last one.

        Observed on round1_01: V3 scored a clean 12/12 and V4 came back at
        10/12, so shipping `iterations[-1]` threw away the best writing of the
        run. Iteration is not monotonic — the generator can trade one criterion
        for another — so "last" and "best" are different questions.

        Ranked on: no deterministic failures first, then binary pass rate, then
        scored total, then latest. A draft that fails a gate can never win,
        however well it scores.
        """
        usable = [i for i in self.iterations if i.draft and not i.error]
        if not usable:
            return self.iterations[-1] if self.iterations else None

        def rank(pair):
            idx, it = pair
            det_ok = 1 if (it.deterministic and it.deterministic.ok) else 0
            binary = it.binary_pass_rate()
            scored = it.judge.scored_total if it.judge else 0
            return (det_ok, binary, scored, idx)

        return max(enumerate(usable), key=rank)[1]


# --------------------------------------------------------------------------


class Gauntlet:
    def __init__(self, cfg: Optional[Config] = None, emit: Emit = _noop) -> None:
        self.cfg = cfg or load_config()
        self.emit = emit
        self.validator = Validator(self.cfg)

        self.gen_provider, gnote = build_provider(self.cfg, "generator")
        self.judge_provider, jnote = build_provider(self.cfg, "judge")
        self.notes = [n for n in (gnote, jnote) if n]

        degraded = assert_independent(self.cfg, self.gen_provider, self.judge_provider)
        self.independence = "DEGRADED" if degraded else "OK"
        if degraded:
            self.notes.append(degraded)

        self.generator = Generator(self.cfg, self.gen_provider)
        self.judge = Judge(self.cfg, self.judge_provider)

    # ------------------------------------------------------------------
    def run(self, spec: ContentSpec, render: bool = True) -> RunResult:
        store = RunStore(self.cfg, spec.id)
        store.write_json("input.json", {
            "spec": spec.to_dict(),
            "stamp": self.cfg.stamp(),
            "providers": self._provider_info(),
            "started": _dt.datetime.now().isoformat(timespec="seconds"),
        })

        # Pre-flight: refuse before spending tokens on a post that cannot ship.
        preflight = self.validator.validate_spec(spec)
        store.write_json("preflight.json", preflight.to_dict())
        if preflight.blocking_failures:
            for r in preflight.blocking_failures:
                self.emit("\n  BLOCKED before generation — %s (%s)" % (r.message, r.check_id))
                if r.evidence:
                    self.emit("    %s" % r.evidence)
                if r.fix:
                    self.emit("    fix: %s" % r.fix)
            result = RunResult(
                run_id=store.run_id, directory=store.dir, spec=spec, iterations=[],
                status="BLOCKED_BEFORE_GENERATION",
                reasons=["%s (%s) — %s%s" % (r.gate_id, r.check_id, r.message,
                                             (" " + r.evidence) if r.evidence else "")
                         for r in preflight.blocking_failures],
                stamp=self.cfg.stamp(), provider_info=self._provider_info())
            self._write_outputs(result, store)
            return result

        band = self.generator._length_band(spec.template)
        iterations: List[Iteration] = []
        draft: Optional[Draft] = None
        fixes: List[Dict[str, Any]] = []
        error = ""

        for n in range(1, self.cfg.max_iterations + 1):
            self.emit("\n  Generating V%d..." % n)
            try:
                draft = (self.generator.generate(spec) if n == 1
                         else self.generator.revise(spec, draft, fixes))
            except (DraftError, ProviderError) as exc:
                error = "generation failed at V%d: %s" % (n, exc)
                self.emit("  ! %s" % error)
                break

            det = self.validator.validate(draft, spec)
            self.emit("  Deterministic checks:  PASS %d  FAIL %d%s" % (
                det.passed_count, det.failed_count,
                ("  WARN %d" % len(det.warnings)) if det.warnings else ""))
            for r in det.blocking_failures:
                self.emit("    BLOCK %s  %s" % (r.check_id, r.message))

            self.emit("  Judge (%s, fresh context)..." % self.judge_provider.model)
            jr = self.judge.evaluate(draft, spec, band)
            if jr.error:
                self.emit("  ! judge error: %s" % jr.error)
            else:
                self.emit("  Judge: %d/12  binary %d/%d  verdict %s" % (
                    jr.scored_total,
                    sum(1 for v in jr.binary.values() if v), len(jr.binary), jr.verdict))

            it = Iteration(n=n, draft=draft, deterministic=det, judge=jr)
            iterations.append(it)

            done, reasons = self._iteration_complete(it)
            if done:
                store.write_json("iteration_%02d.json" % n, it.to_dict())
                self.emit("  → no outstanding fixes")
                break

            fixes = self._compose_fixes(it, spec)
            it.fixes_sent_to_generator = fixes
            store.write_json("iteration_%02d.json" % n, it.to_dict())

            if n < self.cfg.max_iterations:
                self.emit("  → %d fix(es) returned to the generator" % len(fixes))
            else:
                self.emit("  → iteration limit reached (%d)" % self.cfg.max_iterations)

        status, reasons = self._final_status(iterations, error, spec)
        result = RunResult(
            run_id=store.run_id, directory=store.dir, spec=spec, iterations=iterations,
            status=status, reasons=reasons, stamp=self.cfg.stamp(),
            provider_info=self._provider_info(), error=error,
        )

        if render and iterations and not error:
            result.creative = self._render(result, store)

        self._write_outputs(result, store)
        return result

    # ------------------------------------------------------------------
    def _iteration_complete(self, it: Iteration) -> (bool, List[str]):
        """Stop when there is nothing specific left to fix."""
        if it.judge.error:
            return False, ["judge produced no usable evaluation"]
        if it.deterministic.blocking_failures or it.deterministic.binary_failures:
            return False, ["deterministic checks outstanding"]
        pr = self.cfg.pass_rules
        if it.binary_pass_rate() < float(pr["minimum_binary_pass_rate"]):
            return False, ["binary pass rate below threshold"]
        if it.judge.scored_total < int(pr["minimum_quality_score"]):
            return False, ["scored total below threshold"]
        if pr.get("block_on_zero_brand_voice") and it.judge.zero_brand_voice():
            return False, ["brand voice scored 0"]
        if it.judge.verdict == "REVISE" and it.judge.fixes:
            return False, ["judge still asking for revisions"]
        return True, []

    # ------------------------------------------------------------------
    def _compose_fixes(self, it: Iteration, spec: ContentSpec) -> List[Dict[str, Any]]:
        """Structured feedback only. The generator gets problems and replacement
        wording — never the judge's reasoning prose, and never the scores."""
        out: List[Dict[str, Any]] = []
        for r in it.deterministic.results:
            if r.passed or r.severity == "warn":
                continue
            entry: Dict[str, Any] = {
                "source": "deterministic",
                "criterion": r.check_id,
                "gate": r.gate_id,
                "severity": r.severity,
                "problem": r.message,
                "fix": r.fix,
                "evidence": r.evidence,
                "field": r.field,
            }
            band = self._band_for(r.check_id)
            if band:
                entry["target_band"] = band
            out.append(entry)

        for f in it.judge.fixes:
            out.append({
                "source": "judge",
                "criterion": f.criterion,
                "severity": "fail",
                "problem": f.problem,
                "fix": f.fix,
                "replacement": f.replacement,
            })
        for miss in it.judge.unfixed():
            out.append({
                "source": "judge",
                "criterion": miss.criterion,
                "severity": "fail",
                "problem": "the judge marked this down without supplying a specific fix",
                "fix": "Re-examine this criterion against the rubric and improve it.",
                "replacement": "",
            })

        hold = self._passing_criteria(it)
        if hold and out:
            # Without this the loop plays whack-a-mole: the generator rewrites to
            # clear C1 and silently breaks C4 and B3, because nothing told it they
            # were already good. Observed on round1_01 — C1 went 2→2→3 while C4
            # fell 3→3→1 and B3 flipped to fail.
            #
            # Identifiers only. No scores and no judge reasoning, so the generator
            # still cannot argue with a number.
            out.append({
                "source": "engine",
                "criterion": "PRESERVE",
                "severity": "hold",
                "problem": "These criteria already pass. A rewrite that breaks one is "
                           "not an improvement, however well it fixes the rest.",
                "fix": "Change only what the fixes above require. Leave everything "
                       "else as it stands.",
                "preserve": hold,
            })
        return out

    @staticmethod
    def _passing_criteria(it: Iteration) -> List[str]:
        """Criteria the next draft must not regress — identifiers only.

        Scored criteria count only at full marks: a 2 is 'ships after an edit',
        which is not something to freeze in place.
        """
        held: List[str] = []
        j = it.judge
        for cid, score in sorted((j.scores or {}).items()):
            if isinstance(score, int) and score >= 3:
                held.append(cid)
        for bid, ok in sorted((j.binary or {}).items()):
            if ok:
                held.append(bid)
        return held

    def _band_for(self, check_id: str) -> Optional[Dict[str, Any]]:
        for rule in self.cfg.rules.get("binary") or []:
            for chk in rule.get("checks") or []:
                if chk.get("id") == check_id and chk.get("type") == "length_range":
                    return {"unit": chk.get("unit", "chars"),
                            "min": chk.get("min"), "max": chk.get("max")}
        return None

    # ------------------------------------------------------------------
    def _final_status(self, iterations: List[Iteration], error: str,
                      spec: Optional[ContentSpec] = None) -> (str, List[str]):
        """A human always reviews. `enforced` mode decides whether the gauntlet
        cleared the post for that review, not whether it publishes."""
        if error:
            return "ERROR", [error]
        if not iterations:
            return "ERROR", ["no iterations completed"]


        it = iterations[-1]
        reasons: List[str] = []
        pr = self.cfg.pass_rules

        if it.judge.error:
            reasons.append("Judge produced no usable evaluation: %s" % it.judge.error)
        for r in it.deterministic.blocking_failures:
            reasons.append("GATE %s (%s) — %s" % (r.gate_id, r.check_id, r.message))
        for r in it.deterministic.binary_failures:
            reasons.append("CHECK %s (%s) — %s" % (r.gate_id, r.check_id, r.message))

        rate = it.binary_pass_rate()
        if rate < float(pr["minimum_binary_pass_rate"]):
            reasons.append("Binary pass rate %.0f%% is below the configured %.0f%%."
                           % (rate * 100, float(pr["minimum_binary_pass_rate"]) * 100))
        if it.judge.scored_total < int(pr["minimum_quality_score"]):
            reasons.append("Scored total %d/12 is below the configured %d."
                           % (it.judge.scored_total, int(pr["minimum_quality_score"])))
        if pr.get("block_on_zero_brand_voice") and it.judge.zero_brand_voice():
            reasons.append("Brand voice scored 0. A post can otherwise reach 9/12 as 3+3+3+0.")
        if spec is not None and not spec.tier_human_confirmed:
            reasons.append(
                "Intent tier '%s' is unconfirmed. C2 is advisory only — an LLM keyword-matches "
                "here, so a human must confirm the tier before this publishes." % spec.funnel_stage)

        blocking = bool(it.deterministic.blocking_failures) or it.judge.verdict == "BLOCKED"

        if self.cfg.mode == "calibration":
            reasons.insert(0,
                "Mode is CALIBRATION: thresholds are recorded but not binding. The rubric's "
                "80% / 9-of-12 numbers are uncalibrated by their author's own note, so no "
                "post auto-passes on them. Hand-score this post and compare.")
            return ("BLOCKED_HUMAN_REVIEW" if blocking else "HUMAN_REVIEW"), reasons

        if blocking:
            return "BLOCKED", reasons
        if len(reasons) == 0:
            return "PASSED_PENDING_HUMAN", ["Cleared the gauntlet. A human still reviews before publication."]
        return "FAILED_PENDING_HUMAN", reasons

    # ------------------------------------------------------------------
    # Only these fields may be changed by the creative loop. The caption already
    # cleared the copy gauntlet; a design note must not rewrite it.
    CREATIVE_SLOTS = ("creative_headline", "creative_supporting_copy", "creative_qualifier",
                      "eyebrow", "focal", "focal_unit", "alt_text", "visual_concept", "slides")

    def _render(self, result: RunResult, store: RunStore) -> Dict[str, Any]:
        """The creative gauntlet: render → measure → critique → revise → re-render.

        Bounded by creative.max_design_iterations. Any copy the loop changes is
        re-validated against the claim rules before it is accepted — a design
        fix must never be a route around a gate.
        """
        from .render.renderer import render_creative
        ccfg = self.cfg.engine.get("creative") or {}
        max_it = max(1, int(ccfg.get("max_design_iterations", 1)))
        draft = result.final.draft
        history: List[Dict[str, Any]] = []
        creative: Dict[str, Any] = {}

        for k in range(1, max_it + 1):
            try:
                creative = render_creative(self.cfg, result, store, emit=self.emit,
                                           draft=draft, variant=k)
            except Exception as exc:      # rendering must never take the run down
                self.emit("  ! rendering failed: %s" % exc)
                return {"status": "error", "error": str(exc),
                        "traceback": traceback.format_exc(limit=4),
                        "iterations": history}

            problems = self._creative_problems(creative)
            history.append({
                "variant": k,
                "files": creative.get("files"),
                "fit_problems": creative.get("fit_problems"),
                "design_critique": creative.get("design_critique"),
                "problems_found": problems,
                "creative_copy": {f: getattr(draft, f, None) for f in self.CREATIVE_SLOTS
                                  if f != "slides"},
            })
            if not problems:
                break
            if k == max_it:
                self.emit("  → creative iteration limit reached (%d); handing the "
                          "remaining issues to the human" % max_it)
                break

            self.emit("  → %d creative issue(s) returned to the generator" % len(problems))
            revised = self._revise_creative(result.spec, draft, problems)
            if revised is None:
                break
            draft = revised

        # Motion runs once, on the accepted variant only. Animating every
        # attempt would mean ~84 screenshots per rejected draft for a file that
        # gets thrown away, and the design critic grades the still regardless.
        if (ccfg.get("animate", False) and creative.get("status", "").startswith("rendered")
                and result.spec.template == "CARD"):
            from .render.renderer import render_motion
            k = len(history)
            vtag = "" if k <= 1 else "_v%d" % k
            motion = render_motion(
                self.cfg, creative.get("_slots") or {}, creative.get("template") or "",
                result.spec.template, creative.get("renderer") or "",
                store.path(os.path.join("creative_source", "v%d" % k)),
                store, self.cfg.brand["formats"]["CARD"], vtag, self.emit)
            if motion:
                creative["motion"] = motion
                if motion.get("path"):
                    creative.setdefault("files", []).append(motion["path"])
        creative.pop("_slots", None)      # never reaches the run report

        # Every attempt is preserved, but the accepted one also gets the
        # canonical filename — otherwise creative.png is the rejected version.
        accepted = len(history)
        creative["accepted_variant"] = accepted
        if accepted > 1:
            creative["variant_files"] = list(creative.get("files") or [])
            creative["files"] = self._canonicalise(store, creative.get("files") or [], accepted)
        creative["iterations"] = history
        creative["design_iterations"] = len(history)
        creative["final_creative_copy"] = {f: getattr(draft, f, None)
                                           for f in self.CREATIVE_SLOTS if f != "slides"}
        result.creative_draft = draft
        return creative

    # ------------------------------------------------------------------
    @staticmethod
    def _canonicalise(store: RunStore, files: List[str], variant: int) -> List[str]:
        import re as _re
        import shutil as _shutil
        out: List[str] = []
        for rel in files:
            canon = _re.sub(r"_v%d(?=\.|_)" % variant, "", rel)
            canon = _re.sub(r"_v%d_" % variant, "_", canon)
            try:
                _shutil.copyfile(store.path(rel), store.path(canon))
                out.append(canon)
            except OSError:
                out.append(rel)
        return out

    # ------------------------------------------------------------------
    def _creative_problems(self, creative: Dict[str, Any]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for p in creative.get("fit_problems") or []:
            out.append({"source": "fit", "criterion": "DESIGN.FIT", "severity": "fail",
                        "problem": p,
                        "fix": "Shorten the creative copy so it fits the slot. Do not rely "
                               "on the renderer shrinking the type — there is a legibility floor.",
                        "replacement": ""})
        crit = creative.get("design_critique") or {}
        if crit.get("status") == "ok" and crit.get("verdict") == "revise":
            for issue in crit.get("critical_issues") or []:
                out.append({"source": "design_critic", "criterion": "DESIGN.CRITICAL",
                            "severity": "fail", "problem": issue,
                            "fix": "Resolve this before the creative ships.", "replacement": ""})
            for ch in crit.get("changes") or []:
                out.append({"source": "design_critic",
                            "criterion": "DESIGN." + str(ch.get("element", "?")).upper(),
                            "severity": "fail",
                            "problem": str(ch.get("problem", "")),
                            "fix": str(ch.get("fix", "")),
                            "replacement": str(ch.get("replacement", ""))})
        return out

    # ------------------------------------------------------------------
    def _revise_creative(self, spec: ContentSpec, draft: Draft,
                         problems: List[Dict[str, Any]]) -> Optional[Draft]:
        """Take only the creative slots from the revision, then re-validate.

        A design fix must not become a route around a claim gate, and it must
        not quietly rewrite a caption that already cleared the copy gauntlet.
        """
        try:
            proposed = self.generator.revise(spec, draft, problems)
        except (DraftError, ProviderError) as exc:
            self.emit("  ! creative revision failed: %s" % exc)
            return None

        merged = copy.deepcopy(draft)
        for f in self.CREATIVE_SLOTS:
            setattr(merged, f, getattr(proposed, f))

        det = self.validator.validate(merged, spec)
        if det.blocking_failures or det.binary_failures:
            self.emit("  ! creative revision rejected by the claim checks (%s) — "
                      "keeping the previous creative"
                      % ", ".join(r.check_id for r in
                                  (det.blocking_failures + det.binary_failures)[:3]))
            return None
        return merged

    # ------------------------------------------------------------------
    def _provider_info(self) -> Dict[str, Any]:
        return {
            "generator": self.gen_provider.describe(),
            "judge": self.judge_provider.describe(),
            "judge_independence": self.independence,
            "notes": self.notes,
        }

    # ------------------------------------------------------------------
    def _write_outputs(self, result: RunResult, store: RunStore) -> None:
        from .report import post_markdown, run_report
        if result.final and result.final.draft:
            store.write_text("post.md", post_markdown(self.cfg, result))
            store.write_json("judge_report.json", result.final.judge.to_dict())
        store.write_json("run_report.json", run_report(self.cfg, result))
        store.write_json("performance.json", store.performance_skeleton())
