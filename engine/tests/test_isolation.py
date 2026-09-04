"""The gauntlet is only real if the judge physically cannot reach the
generator's state. These tests plant canaries and assert they never surface."""
import json
import unittest

from helpers import CFG, StubProvider, draft, spec
from postengine.agents import Generator, Judge
from postengine.agents.judge import ALLOWED_DRAFT_FIELDS, JudgePacket
from postengine.providers import assert_independent
from postengine.providers.base import ProviderError
from postengine.providers.mock import MockProvider

CANARY = "CANARY-GENERATOR-PRIVATE-9f21"


class TestJudgePacket(unittest.TestCase):
    def setUp(self):
        self.spec = spec()
        self.draft = draft(private_reasoning=CANARY,
                           private_self_assessment=CANARY + "-SELF")

    def test_private_reasoning_never_reaches_the_packet(self):
        p = JudgePacket.build(CFG, self.draft, self.spec, "400-1300 chars")
        self.assertNotIn(CANARY, json.dumps(p.to_dict()))
        self.assertNotIn(CANARY, p.render())

    def test_packet_is_an_allowlist_not_a_copy(self):
        d = self.draft
        setattr(d, "smuggled_field", CANARY)          # a field added after the fact
        p = JudgePacket.build(CFG, d, self.spec, "band")
        self.assertNotIn(CANARY, json.dumps(p.to_dict()))
        for key in p.draft:
            self.assertIn(key, ALLOWED_DRAFT_FIELDS)

    def test_packet_is_immutable(self):
        p = JudgePacket.build(CFG, self.draft, self.spec, "band")
        with self.assertRaises(Exception):
            p.objective = "mutated"

    def test_judge_never_sees_the_metric_label_or_internal_constraints(self):
        s = spec(constraints=["INTERNAL-ONLY-NOTE-" + CANARY])
        p = JudgePacket.build(CFG, draft(), s, "band")
        blob = p.render() + json.dumps(p.to_dict())
        self.assertNotIn("INTERNAL-ONLY-NOTE", blob)
        self.assertNotIn("metric_label", blob)

    def test_slides_are_withheld_for_non_document_posts(self):
        p = JudgePacket.build(CFG, draft(slides=[{"headline": "a b c"}]), spec(), "band")
        self.assertNotIn("slides", p.draft)


class TestJudgePromptContents(unittest.TestCase):
    def test_judge_prompt_carries_no_internal_document_text(self):
        stub = StubProvider({"judge": {"reasoning": "r", "scores": {"C1": 3, "C2": 3, "C3": 3, "C4": 3},
                                       "verdict": "SHIP", "binary": {}}}, family="judge-fam")
        j = Judge(CFG, stub)
        j.evaluate(draft(private_reasoning=CANARY), spec(), "band")
        blob = stub.calls[0]["system"] + stub.calls[0]["user"]
        for forbidden in (CANARY, "decisions-log", "claim-evidence-register",
                          "Ruled by: Leadership", "blocked on Robin"):
            self.assertNotIn(forbidden, blob, forbidden)

    def test_judge_is_not_shown_the_deterministic_findings(self):
        """Anchoring control: the judge forms its own view."""
        stub = StubProvider({"judge": {"reasoning": "r", "scores": {"C1": 3, "C2": 3, "C3": 3, "C4": 3},
                                       "verdict": "SHIP", "binary": {}}}, family="judge-fam")
        Judge(CFG, stub).evaluate(draft(), spec(), "band")
        blob = stub.calls[0]["user"]
        self.assertNotIn("deterministic", blob.lower())
        self.assertNotIn("A1.1", blob)

    def test_generator_revision_never_receives_judge_reasoning_or_scores(self):
        stub = StubProvider({"revise": dict(hook="h", body="b", cta="c",
                                            creative_headline="ch", visual_concept="v")},
                            family="gen-fam")
        g = Generator(CFG, stub)
        fixes = [{"criterion": "C1", "problem": "too long", "fix": "shorten",
                  "replacement": "A better hook."}]
        g.revise(spec(), draft(), fixes)
        blob = stub.calls[0]["user"]
        self.assertIn("A better hook.", blob)
        self.assertNotIn("scored_total", blob)
        self.assertNotIn("verdict", blob.lower())

    def test_composed_fixes_carry_no_judge_reasoning_or_scores(self):
        """The generator gets problems and replacement wording. Handing it a
        score invites arguing with the number instead of fixing the text."""
        from postengine.models import DeterministicReport, Fix, JudgeReport
        from postengine.pipeline import Gauntlet, Iteration
        g = Gauntlet(CFG)
        jr = JudgeReport(reasoning="JUDGE-PRIVATE-REASONING-" + CANARY,
                         scores={"C1": 1, "C2": 3, "C3": 3, "C4": 3},
                         binary={"B11": False}, verdict="REVISE",
                         fixes=[Fix(criterion="C1", problem="p", fix="f", replacement="R"),
                                Fix(criterion="B11", problem="p2", fix="f2")])
        it = Iteration(n=1, draft=draft(),
                       deterministic=DeterministicReport(rules_version="1", results=[]),
                       judge=jr)
        blob = json.dumps(g._compose_fixes(it, spec()))
        self.assertNotIn(CANARY, blob)
        self.assertNotIn("JUDGE-PRIVATE-REASONING", blob)
        self.assertNotIn("C1\": 1", blob)
        self.assertIn("R", blob)


    def test_passing_criteria_are_pinned_against_regression(self):
        """Observed on round1_01: the generator cleared C1 and broke C4 and B3,
        because the fix packet only ever named failures. Passing criteria are now
        listed so a rewrite knows what not to touch — identifiers only, so the
        no-scores rule above still holds."""
        from postengine.models import DeterministicReport, Fix, JudgeReport
        from postengine.pipeline import Gauntlet, Iteration
        g = Gauntlet(CFG)
        jr = JudgeReport(reasoning="r",
                         scores={"C1": 1, "C2": 2, "C3": 3, "C4": 3},
                         binary={"B2": True, "B3": False, "B11": True},
                         verdict="REVISE",
                         fixes=[Fix(criterion="C1", problem="p", fix="f")])
        it = Iteration(n=1, draft=draft(),
                       deterministic=DeterministicReport(rules_version="1", results=[]),
                       judge=jr)
        composed = g._compose_fixes(it, spec())
        hold = [e for e in composed if e.get("criterion") == "PRESERVE"]
        self.assertEqual(len(hold), 1)
        preserve = hold[0]["preserve"]
        self.assertIn("C3", preserve)      # scored 3
        self.assertIn("C4", preserve)
        self.assertIn("B2", preserve)      # binary pass
        self.assertIn("B11", preserve)
        self.assertNotIn("C1", preserve)   # failing
        self.assertNotIn("C2", preserve)   # a 2 is "ships after an edit", not frozen
        self.assertNotIn("B3", preserve)   # binary fail
        self.assertNotIn("3", json.dumps(hold[0]).replace("B3", "").replace("C3", ""))


    def test_the_best_draft_ships_not_the_last(self):
        """Observed on round1_01: V3 scored 12/12, V4 came back at 10/12, and the
        engine rendered V4. Iteration is not monotonic, so last != best."""
        from postengine.models import DeterministicReport, JudgeReport
        from postengine.pipeline import Iteration, RunResult

        def it(n, scored):
            return Iteration(n=n, draft=draft(),
                             deterministic=DeterministicReport(rules_version="1", results=[]),
                             judge=JudgeReport(reasoning="r", scores={"C1": scored},
                                               binary={"B2": True}, verdict="REVISE"))

        r = RunResult(run_id="t", directory="", spec=spec(),
                      iterations=[it(1, 2), it(2, 3), it(3, 1)],
                      status="HUMAN_REVIEW", reasons=[], stamp={}, provider_info={})
        self.assertEqual(r.final.n, 2, "should ship the 3-scoring V2, not the 1-scoring V3")

    def test_a_gate_failure_can_never_win_on_score(self):
        """A draft that trips a deterministic gate is not publishable, however
        well the judge scored it."""
        from postengine.models import CheckResult, DeterministicReport, JudgeReport
        from postengine.pipeline import Iteration, RunResult
        bad = DeterministicReport(rules_version="1", results=[
            CheckResult(check_id="C0.1", gate_id="C0", title="t", severity="fail",
                        passed=False, message="m", fix="f")])
        good = DeterministicReport(rules_version="1", results=[])

        def it(n, det, scored):
            return Iteration(n=n, draft=draft(), deterministic=det,
                             judge=JudgeReport(reasoning="r", scores={"C1": scored},
                                               binary={"B2": True}, verdict="REVISE"))

        r = RunResult(run_id="t", directory="", spec=spec(),
                      iterations=[it(1, bad, 3), it(2, good, 1)],
                      status="HUMAN_REVIEW", reasons=[], stamp={}, provider_info={})
        self.assertEqual(r.final.n, 2, "the clean draft must win over the higher-scoring failure")


class TestFamilyIndependence(unittest.TestCase):
    @staticmethod
    def _cfg(allow):
        # Explicit, so the test does not depend on what the shipped config
        # happens to set. The Claude-only setup turns the override on.
        return type("C", (), {"engine": {"providers": {"allow_same_family": allow}}})()

    def test_same_family_is_refused(self):
        with self.assertRaises(ProviderError):
            assert_independent(self._cfg(False),
                               MockProvider(role="generator", family="same"),
                               MockProvider(role="judge", family="same"))

    def test_different_families_pass(self):
        self.assertIsNone(assert_independent(
            CFG, MockProvider(role="generator", family="a"),
            MockProvider(role="judge", family="b")))

    def test_same_family_same_model_is_degraded(self):
        """The judge is grading its own voice. Worst case."""
        note = assert_independent(self._cfg(True),
                                  MockProvider(model="m1", role="generator", family="same"),
                                  MockProvider(model="m1", role="judge", family="same"))
        self.assertIn("DEGRADED", note)

    def test_same_family_different_model_is_partial(self):
        """The Claude-only setup: opus generates, sonnet judges. Self-preference
        is reduced but not removed, so it must not report as INDEPENDENT."""
        note = assert_independent(self._cfg(True),
                                  MockProvider(model="opus", role="generator", family="anthropic"),
                                  MockProvider(model="sonnet", role="judge", family="anthropic"))
        self.assertIn("PARTIAL", note)
        self.assertNotIn("DEGRADED", note)


if __name__ == "__main__":
    unittest.main()
