"""Pass/fail logic, iteration control, and failure handling."""
import atexit
import copy
import json
import shutil
import tempfile
import unittest

from helpers import CFG, StubProvider, draft, spec
from postengine.config import Config, ConfigError
from postengine.models import (DeterministicReport, Draft, DraftError, Fix,
                             JudgeReport, CheckResult)
from postengine.pipeline import Gauntlet, Iteration
from postengine.providers.mock import MockProvider


# Tests must never write into the user's runs/ directory.
_TEST_RUNS = tempfile.mkdtemp(prefix="postengine-tests-")
atexit.register(lambda: shutil.rmtree(_TEST_RUNS, ignore_errors=True))


def cfg_copy(**engine_over):
    c = copy.deepcopy(CFG)
    c.engine.setdefault("paths", {})["runs"] = _TEST_RUNS
    c.root = c.root  # runs path is absolute, so root is not consulted
    for k, v in engine_over.items():
        if k == "pass_rules":
            c.engine["pass_rules"].update(v)
        else:
            c.engine[k] = v
    return c


def det(results=None):
    return DeterministicReport(rules_version="1.0.0", results=results or [])


def check(cid, gid, passed, sev):
    return CheckResult(check_id=cid, gate_id=gid, title="t", passed=passed, severity=sev)


def judge(total=12, binary=None, verdict="SHIP", c3=None, fixes=None, error=""):
    each = total // 4
    scores = {"C1": each, "C2": each, "C3": each if c3 is None else c3, "C4": total - 3 * each}
    return JudgeReport(reasoning="r", scores=scores, binary=binary or {"B2": True},
                       verdict=verdict, fixes=fixes or [], error=error)


class TestJudgeReportParsing(unittest.TestCase):
    def test_missing_reasoning_is_rejected(self):
        with self.assertRaises(DraftError):
            JudgeReport.from_model_json({"scores": {"C1": 3, "C2": 3, "C3": 3, "C4": 3},
                                         "verdict": "SHIP"})

    def test_out_of_range_score_is_rejected(self):
        with self.assertRaises(DraftError):
            JudgeReport.from_model_json({"reasoning": "r", "verdict": "SHIP",
                                         "scores": {"C1": 7, "C2": 3, "C3": 3, "C4": 3}})

    def test_non_numeric_score_is_rejected(self):
        with self.assertRaises(DraftError):
            JudgeReport.from_model_json({"reasoning": "r", "verdict": "SHIP",
                                         "scores": {"C1": "great", "C2": 3, "C3": 3, "C4": 3}})

    def test_omitted_criterion_is_rejected(self):
        with self.assertRaises(DraftError):
            JudgeReport.from_model_json({"reasoning": "r", "verdict": "SHIP",
                                         "scores": {"C1": 3, "C2": 3}})

    def test_unknown_verdict_degrades_to_revise_not_to_ship(self):
        r = JudgeReport.from_model_json({"reasoning": "r", "verdict": "looks fine to me",
                                         "scores": {"C1": 3, "C2": 3, "C3": 3, "C4": 3}})
        self.assertEqual(r.verdict, "REVISE")

    def test_prose_wrapped_json_is_recovered(self):
        raw = ('Sure! Here is my evaluation:\n```json\n'
               '{"reasoning":"r","verdict":"SHIP","scores":{"C1":3,"C2":3,"C3":3,"C4":3}}\n```')
        self.assertEqual(JudgeReport.from_model_json(raw).scored_total, 12)

    def test_scoring_arithmetic(self):
        r = JudgeReport.from_model_json({"reasoning": "r", "verdict": "REVISE",
                                         "scores": {"C1": 2, "C2": 3, "C3": 0, "C4": 1},
                                         "binary": {"B2": True, "B3": False, "B11": False}})
        self.assertEqual(r.scored_total, 6)
        self.assertAlmostEqual(r.binary_pass_rate, 1 / 3.0, places=3)
        self.assertTrue(r.zero_brand_voice())

    def test_sub_three_scores_without_a_fix_are_reported(self):
        r = JudgeReport.from_model_json({"reasoning": "r", "verdict": "REVISE",
                                         "scores": {"C1": 1, "C2": 3, "C3": 3, "C4": 3},
                                         "binary": {"B11": False}})
        self.assertEqual(sorted(f.criterion for f in r.unfixed()), ["B11", "C1"])


class TestJudgeFailureHandling(unittest.TestCase):
    def test_unusable_judge_output_becomes_blocked_never_a_pass(self):
        from postengine.agents import Judge
        stub = StubProvider({"judge": "this is not json at all"}, family="j")
        r = Judge(CFG, stub).evaluate(draft(), spec(), "band")
        self.assertEqual(r.verdict, "BLOCKED")
        self.assertTrue(r.error)
        self.assertEqual(r.scored_total, 0)

    def test_empty_judge_response_is_retried_then_blocked(self):
        from postengine.agents import Judge
        c = cfg_copy()
        c.engine["retry"] = {"attempts": 2, "backoff_seconds": [0], "retry_on": ["malformed_json"]}
        stub = StubProvider({"judge": ""}, family="j")
        r = Judge(c, stub).evaluate(draft(), spec(), "band")
        self.assertEqual(r.verdict, "BLOCKED")
        self.assertGreaterEqual(len(stub.calls), 2, "an empty response should be retried")


class TestCombinedBinary(unittest.TestCase):
    def test_a_deterministic_fail_overrides_a_judge_pass(self):
        it = Iteration(n=1, draft=draft(),
                       deterministic=det([check("B4.1", "B4", False, "fail")]),
                       judge=judge(binary={"B4": True, "B2": True}))
        self.assertFalse(it.combined_binary()["B4"])

    def test_warnings_do_not_affect_the_pass_rate(self):
        it = Iteration(n=1, draft=draft(),
                       deterministic=det([check("C3.2", "C3", False, "warn")]),
                       judge=judge(binary={"B2": True}))
        self.assertEqual(it.binary_pass_rate(), 1.0)


class TestStatusLogic(unittest.TestCase):
    def _status(self, cfg, iterations, spec_=None):
        g = Gauntlet(cfg)
        return g._final_status(iterations, "", spec_ or spec())

    def test_calibration_never_auto_passes(self):
        c = cfg_copy(mode="calibration")
        it = Iteration(n=1, draft=draft(), deterministic=det(), judge=judge(12))
        status, reasons = self._status(c, [it], spec(tier_human_confirmed=True))
        self.assertEqual(status, "HUMAN_REVIEW")
        self.assertIn("CALIBRATION", reasons[0])

    def test_calibration_still_marks_a_gate_failure(self):
        c = cfg_copy(mode="calibration")
        it = Iteration(n=1, draft=draft(),
                       deterministic=det([check("A1.1", "A1", False, "blocking")]),
                       judge=judge(12))
        status, _ = self._status(c, [it])
        self.assertEqual(status, "BLOCKED_HUMAN_REVIEW")

    def test_enforced_clears_a_clean_post_for_human_review(self):
        c = cfg_copy(mode="enforced")
        it = Iteration(n=1, draft=draft(), deterministic=det(), judge=judge(12))
        status, reasons = self._status(c, [it], spec(tier_human_confirmed=True))
        self.assertEqual(status, "PASSED_PENDING_HUMAN")
        self.assertIn("human still reviews", reasons[0])

    def test_enforced_never_publishes_without_a_human(self):
        c = cfg_copy(mode="enforced")
        it = Iteration(n=1, draft=draft(), deterministic=det(), judge=judge(12))
        status, _ = self._status(c, [it], spec(tier_human_confirmed=True))
        self.assertIn("PENDING_HUMAN", status)

    def test_unconfirmed_intent_tier_is_always_flagged(self):
        c = cfg_copy(mode="enforced")
        it = Iteration(n=1, draft=draft(), deterministic=det(), judge=judge(12))
        status, reasons = self._status(c, [it], spec(tier_human_confirmed=False))
        self.assertEqual(status, "FAILED_PENDING_HUMAN")
        self.assertTrue(any("tier" in r for r in reasons))

    def test_zero_brand_voice_blocks_even_at_nine_of_twelve(self):
        """3+3+3+0 reaches the 9/12 threshold. It must not pass."""
        c = cfg_copy(mode="enforced", pass_rules={"block_on_zero_brand_voice": True})
        jr = JudgeReport(reasoning="r", scores={"C1": 3, "C2": 3, "C3": 0, "C4": 3},
                         binary={"B2": True}, verdict="SHIP")
        it = Iteration(n=1, draft=draft(), deterministic=det(), judge=jr)
        self.assertEqual(jr.scored_total, 9)
        status, reasons = self._status(c, [it], spec(tier_human_confirmed=True))
        self.assertEqual(status, "FAILED_PENDING_HUMAN")
        self.assertTrue(any("Brand voice scored 0" in r for r in reasons))

    def test_below_threshold_binary_rate_fails_in_enforced_mode(self):
        c = cfg_copy(mode="enforced")
        it = Iteration(n=1, draft=draft(), deterministic=det(),
                       judge=judge(12, binary={"B2": True, "B3": False, "B11": False}))
        status, _ = self._status(c, [it], spec(tier_human_confirmed=True))
        self.assertEqual(status, "FAILED_PENDING_HUMAN")

    def test_no_iterations_is_an_error(self):
        status, _ = self._status(cfg_copy(), [])
        self.assertEqual(status, "ERROR")


class TestIterationControl(unittest.TestCase):
    def test_max_iterations_is_respected(self):
        c = cfg_copy(pass_rules={"maximum_iterations": 2})
        c.engine["creative"]["enabled"] = False
        gen = StubProvider({"generate": dict(hook="Here is a very long descriptive hook that goes on",
                                             body="b" * 500, cta="c",
                                             creative_headline="ch", visual_concept="v"),
                            "revise": dict(hook="Here is a very long descriptive hook that goes on",
                                           body="b" * 500, cta="c",
                                           creative_headline="ch", visual_concept="v")},
                           family="gen")
        jud = StubProvider({"judge": {"reasoning": "r", "verdict": "REVISE",
                                      "scores": {"C1": 1, "C2": 3, "C3": 3, "C4": 3},
                                      "binary": {"B2": True},
                                      "fixes": [{"criterion": "C1", "problem": "p",
                                                 "fix": "f", "replacement": "x"}]}},
                           family="jud")
        g = Gauntlet(c)
        g.gen_provider, g.judge_provider = gen, jud
        from postengine.agents import Generator, Judge
        g.generator, g.judge = Generator(c, gen), Judge(c, jud)
        result = g.run(spec(), render=False)
        self.assertEqual(len(result.iterations), 2)
        self.assertEqual(len([c_ for c_ in gen.calls if c_["task"] == "generate"]), 1)
        self.assertEqual(len([c_ for c_ in gen.calls if c_["task"] == "revise"]), 1)

    def test_a_clean_first_pass_stops_after_one_iteration(self):
        c = cfg_copy()
        c.engine["creative"]["enabled"] = False
        g = Gauntlet(c)
        result = g.run(spec(pain_point="A1"), render=False)
        self.assertGreaterEqual(len(result.iterations), 1)
        self.assertLessEqual(len(result.iterations), c.max_iterations)

    def test_generation_failure_is_recorded_not_swallowed(self):
        c = cfg_copy()
        c.engine["creative"]["enabled"] = False
        c.engine["retry"] = {"attempts": 1, "backoff_seconds": [0], "retry_on": []}
        gen = StubProvider({"generate": {"hook": "only a hook"}}, family="gen")
        jud = StubProvider({"judge": {"reasoning": "r", "verdict": "SHIP",
                                      "scores": {"C1": 3, "C2": 3, "C3": 3, "C4": 3}}},
                           family="jud")
        g = Gauntlet(c)
        from postengine.agents import Generator, Judge
        g.gen_provider, g.judge_provider = gen, jud
        g.generator, g.judge = Generator(c, gen), Judge(c, jud)
        result = g.run(spec(), render=False)
        self.assertEqual(result.status, "ERROR")
        self.assertIn("missing required field", result.error)


class TestConfigValidation(unittest.TestCase):
    def test_bad_mode_is_rejected(self):
        c = copy.deepcopy(CFG)
        c.engine["mode"] = "yolo"
        with self.assertRaises(ConfigError):
            c._validate()

    def test_out_of_range_threshold_is_rejected(self):
        c = copy.deepcopy(CFG)
        c.engine["pass_rules"]["minimum_quality_score"] = 99
        with self.assertRaises(ConfigError):
            c._validate()

    def test_rubric_is_hashed_for_provenance(self):
        self.assertTrue(CFG.stamp()["rubric_sha256"])
        self.assertEqual(len(CFG.stamp()["rubric_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()


class TestInputHardening(unittest.TestCase):
    """Found during hostile review: three ways a bad model response caused a
    problem downstream rather than being rejected at the boundary."""

    def test_runaway_draft_is_rejected_before_it_becomes_a_judge_prompt(self):
        from postengine.models import MAX_DRAFT_CHARS
        with self.assertRaises(DraftError) as cm:
            Draft.from_model_json({"hook": "h", "body": "x" * (MAX_DRAFT_CHARS + 10),
                                   "creative_headline": "c", "visual_concept": "v"})
        self.assertIn("hard cap", str(cm.exception))

    def test_control_characters_are_stripped(self):
        d = Draft.from_model_json({"hook": "a\x00b", "body": "c\x1fd",
                                   "creative_headline": "e\x07f", "visual_concept": "v"})
        for value in (d.hook, d.body, d.creative_headline):
            self.assertNotIn("\x00", value)
            self.assertNotIn("\x1f", value)
            self.assertNotIn("\x07", value)

    def test_newlines_and_tabs_survive(self):
        d = Draft.from_model_json({"hook": "h", "body": "a\n\nb\tc",
                                   "creative_headline": "c", "visual_concept": "v"})
        self.assertIn("\n\n", d.body)

    def test_fractional_score_is_malformed_not_rounded_up(self):
        """2.6 rounding to 3 would quietly turn a REVISE into a SHIP."""
        with self.assertRaises(DraftError):
            JudgeReport.from_model_json({"reasoning": "r", "verdict": "SHIP",
                                         "scores": {"C1": 2.6, "C2": 3, "C3": 3, "C4": 3}})

    def test_integral_float_is_accepted(self):
        r = JudgeReport.from_model_json({"reasoning": "r", "verdict": "SHIP",
                                         "scores": {"C1": 3.0, "C2": 3, "C3": 3, "C4": 3}})
        self.assertEqual(r.scored_total, 12)


class TestCreativeGauntlet(unittest.TestCase):
    """The creative loop must be bounded, must re-validate anything it changes,
    and must never let a design fix rewrite the caption."""

    def test_a_design_revision_may_not_touch_the_caption(self):
        c = cfg_copy()
        g = Gauntlet(c)
        original = draft()
        proposed = draft(body="A COMPLETELY DIFFERENT BODY that never faced the judge.",
                         hook="A different hook.",
                         creative_supporting_copy="Shorter line.")

        class OneShot:
            def revise(self_inner, spec_, prev, fixes):
                return proposed
        g.generator = OneShot()
        merged = g._revise_creative(spec(), original, [{"criterion": "DESIGN.FIT"}])
        self.assertIsNotNone(merged)
        self.assertEqual(merged.body, original.body, "the caption must survive untouched")
        self.assertEqual(merged.hook, original.hook)
        self.assertEqual(merged.creative_supporting_copy, "Shorter line.")

    def test_a_design_revision_that_breaks_a_gate_is_rejected(self):
        """A design fix must not be a route around a claim gate."""
        c = cfg_copy()
        g = Gauntlet(c)
        bad = draft(creative_supporting_copy="Industry-leading pipeline monitoring.")

        class OneShot:
            def revise(self_inner, spec_, prev, fixes):
                return bad
        g.generator = OneShot()
        self.assertIsNone(g._revise_creative(spec(), draft(), [{"criterion": "DESIGN.FIT"}]))

    def test_fit_problems_become_structured_design_fixes(self):
        g = Gauntlet(cfg_copy())
        problems = g._creative_problems({
            "fit_problems": ["slot `deck` is 665 characters; the template holds 120."],
            "design_critique": {"status": "ok", "verdict": "revise",
                                "critical_issues": ["Text overflows."],
                                "changes": [{"element": "headline", "problem": "Too long",
                                             "fix": "Cut to 7 words",
                                             "replacement": "A shorter headline."}]}})
        crits = [p["criterion"] for p in problems]
        self.assertIn("DESIGN.FIT", crits)
        self.assertIn("DESIGN.CRITICAL", crits)
        self.assertIn("DESIGN.HEADLINE", crits)
        self.assertTrue(all(p.get("fix") for p in problems))

    def test_an_approving_critic_produces_no_design_fixes(self):
        g = Gauntlet(cfg_copy())
        self.assertEqual(g._creative_problems({
            "fit_problems": [],
            "design_critique": {"status": "ok", "verdict": "approve",
                                "critical_issues": [], "changes": []}}), [])


class TestPreflight(unittest.TestCase):
    """Some failures are knowable from the spec alone. Spending four drafting
    rounds on a post that can never ship is waste, and it buries the real
    reason under quality feedback."""

    def _run(self, s):
        c = cfg_copy()
        c.engine["creative"]["enabled"] = False
        return Gauntlet(c).run(s, render=False)

    def test_blocked_pain_point_never_reaches_the_generator(self):
        r = self._run(spec(pain_point="E3"))
        self.assertEqual(r.status, "BLOCKED_BEFORE_GENERATION")
        self.assertEqual(r.iterations, [])
        self.assertTrue(any("E3" in x for x in r.reasons))

    def test_pain_point_excluded_from_linkedin_never_reaches_the_generator(self):
        r = self._run(spec(pain_point="F4"))
        self.assertEqual(r.status, "BLOCKED_BEFORE_GENERATION")
        self.assertEqual(r.iterations, [])

    def test_unregistered_pain_point_is_caught_before_generation(self):
        r = self._run(spec(pain_point="Z9"))
        self.assertEqual(r.status, "BLOCKED_BEFORE_GENERATION")

    def test_missing_metric_label_choice_is_caught_before_generation(self):
        """Gate A4: someone must actively choose, before drafting."""
        r = self._run(spec(metric_label="unset"))
        self.assertEqual(r.status, "BLOCKED_BEFORE_GENERATION")

    def test_a_valid_spec_passes_preflight(self):
        r = self._run(spec(pain_point="A1"))
        self.assertNotEqual(r.status, "BLOCKED_BEFORE_GENERATION")
        self.assertTrue(r.iterations)

    def test_the_blocking_reason_is_recorded_on_disk(self):
        r = self._run(spec(pain_point="E3"))
        import json as _json
        import os as _os
        pf = _json.load(open(_os.path.join(r.directory, "preflight.json")))
        self.assertIn("S1.2", pf["blocking_failures"])
