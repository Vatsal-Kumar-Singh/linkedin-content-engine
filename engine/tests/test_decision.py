"""The decision layer: Gate, Lift, Fit, the buying-job classifier, the channel split.

**Most of these check that the scorer REFUSES correctly**, because the failure mode here is
silent. A component that quietly falls back to a default produces a plausible number and nothing
looks wrong. This module ships with no measurements at all, so every refusal is load-bearing.

    cd tests && python -m unittest discover -s . -t .
"""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decision import profile as profile_mod
from decision import channel, scoring
from decision.scoring import (ANGLE_TO_JOB, ANGLE_TO_OTHER_OBJECTIVE, JOB_SERVES, JOB_TO_TIER,
                              classify, fit, gate, lift, recommend, score_slot)

EXAMPLE = profile_mod.load("example-meridian")


# =================================================================================================
# The module carries no data. This is the property the whole design rests on.
# =================================================================================================

class TestNoMeasurementsShip(unittest.TestCase):
    def test_the_module_defines_no_corpus_constants(self):
        """A fallback corpus is one company's audience presented as everybody's."""
        with open(scoring.__file__, encoding="utf-8") as fh:
            src = fh.read()
        for banned in ("LENGTH_BANDS = [", "FORMAT_LIFT", "SATURATION = {"):
            self.assertNotIn(banned, src,
                             "a measured constant is back in the engine: " + banned)

    def test_corpus_returns_none_for_everything_without_a_profile(self):
        c = scoring.corpus({})
        self.assertIsNone(c["length_bands"])
        self.assertIsNone(c["saturation"])
        self.assertEqual(c["measured"], [])

    def test_lift_declines_entirely_without_a_profile(self):
        r = lift({"fmt": "text", "words": 300})
        self.assertIsNone(r["score"])
        self.assertTrue(any("profile" in n for n in r["notes"]))

    def test_lift_scores_once_a_profile_supplies_a_corpus(self):
        r = lift({"fmt": "text", "words": 300}, profile=EXAMPLE)
        self.assertIsNotNone(r["score"])

    def test_two_profiles_produce_different_scores(self):
        """The point of the whole indirection. If this passes trivially it is decorative."""
        other = copy.deepcopy(EXAMPLE)
        other["corpus"]["format_lift"]["clevel"] = {"text": 900.0, "photo album": 100.0}
        mine = lift({"fmt": "text", "words": 300}, profile=EXAMPLE)["components"]["format"]
        theirs = lift({"fmt": "text", "words": 300}, profile=other)["components"]["format"]
        self.assertNotEqual(mine, theirs)
        self.assertEqual(theirs, 1.0)


# =================================================================================================
# Gate. Binary, first, and it is where production and claim rules live.
# =================================================================================================

class TestGate(unittest.TestCase):
    def test_a_proof_tier_above_none_must_name_a_source(self):
        self.assertFalse(gate({"fmt": "text", "proof": "MEASURED"})["pass"])
        self.assertTrue(gate({"fmt": "text", "proof": "MEASURED", "source": "the register"})["pass"])

    def test_an_unknown_proof_tier_is_refused(self):
        self.assertFalse(gate({"fmt": "text", "proof": "PROBABLY"})["pass"])

    def test_a_refusal_always_carries_a_reason(self):
        """A refusal nobody can argue with defeats the point of a human deciding."""
        r = gate({"fmt": "video", "proof": "SPEC"})
        self.assertTrue(r["reasons"] and all(x.strip() for x in r["reasons"]))


# =================================================================================================
# classify. Buying job first, funnel label derived from it.
# =================================================================================================

class TestClassify(unittest.TestCase):
    def test_a_declared_job_beats_the_angle(self):
        c = classify({"angle": "hiring", "job": "validation"})
        self.assertEqual((c["job"], c["label"], c["source"]), ("validation", "BOFU", "declared"))

    def test_a_job_outside_the_six_is_refused_rather_than_coerced(self):
        self.assertIsNone(classify({"angle": "explainer", "job": "vibes"})["job"])

    def test_an_angle_serving_no_buying_job_names_what_it_does_serve(self):
        self.assertEqual(classify({"angle": "hiring"})["objective"], "recruitment")

    def test_an_unmapped_angle_says_so_instead_of_guessing(self):
        c = classify({"angle": "no-such-angle"})
        self.assertIsNone(c["label"])
        self.assertIn("no job mapping", c["note"])

    def test_the_three_job_tables_cover_the_same_six_jobs(self):
        self.assertEqual(set(JOB_TO_TIER), set(JOB_SERVES))
        self.assertLessEqual(set(ANGLE_TO_JOB.values()), set(JOB_TO_TIER))

    def test_no_angle_is_in_both_mappings(self):
        self.assertFalse(set(ANGLE_TO_JOB) & set(ANGLE_TO_OTHER_OBJECTIVE))


# =================================================================================================
# Fit. The refusals matter more than the numbers.
# =================================================================================================

class TestFit(unittest.TestCase):
    def test_fit_withholds_without_objective_weights(self):
        r = fit({"angle": "measured-scale", "proof": "MEASURED"}, profile={})
        self.assertIsNone(r["score"])
        self.assertTrue(any("objective weights" in m for m in r["missing"]))

    def test_fit_does_not_substitute_a_default_when_it_withholds(self):
        r = fit({"angle": "measured-scale", "proof": "MEASURED"}, profile={})
        self.assertNotIn("alignment", r["components"])

    def test_openness_degrades_rather_than_blocking(self):
        """Themes outside the measured set are normal. Withholding them all would be worse."""
        r = fit({"angle": "measured-scale", "theme": None, "proof": "NONE"}, EXAMPLE)
        self.assertIsNotNone(r["score"])
        self.assertEqual(r["basis"], ["alignment", "proof"])

    def test_an_emptier_theme_scores_more_open(self):
        thin = fit({"angle": "measured-scale", "theme": "pipeline reliability",
                    "proof": "NONE"}, EXAMPLE)["components"]["openness"]
        thick = fit({"angle": "measured-scale", "theme": "observability tooling",
                     "proof": "NONE"}, EXAMPLE)["components"]["openness"]
        self.assertGreater(thin, thick)

    def test_capture_weighting_favours_late_jobs_and_create_favours_early(self):
        late = fit({"angle": "objection-handling", "proof": "NONE"}, EXAMPLE)
        early = fit({"angle": "problem-reframe", "proof": "NONE"}, EXAMPLE)
        self.assertGreater(late["by_kind"]["capture"], early["by_kind"]["capture"])
        self.assertGreater(early["by_kind"]["create"], late["by_kind"]["create"])


# =================================================================================================
# The profile loader refuses what the engine cannot interpret.
# =================================================================================================

class TestProfileLoader(unittest.TestCase):
    def _write(self, body):
        import tempfile
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "t.md"), "w", encoding="utf-8") as fh:
            fh.write("# t\n\n```yaml\n" + body + "\n```\n")
        return d

    def _load(self, body):
        d = self._write(body)
        old = profile_mod.PROFILES
        profile_mod.PROFILES = __import__("pathlib").Path(d)
        try:
            return profile_mod.load("t")
        finally:
            profile_mod.PROFILES = old

    def test_a_weight_without_a_kind_is_refused(self):
        with self.assertRaises(ValueError):
            self._load("objectives:\n  weights:\n    growth: 100\n")

    def test_weights_that_do_not_sum_to_100_are_refused(self):
        with self.assertRaises(ValueError):
            self._load("objectives:\n  weights:\n    a: 60\n    b: 20\n"
                       "  kinds:\n    a: capture\n    b: create\n")

    def test_no_weights_at_all_is_a_legitimate_state(self):
        self.assertEqual(self._load("company: x\n")["company"], "x")

    def test_two_yaml_blocks_are_refused(self):
        import tempfile, pathlib
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "t.md"), "w", encoding="utf-8") as fh:
            fh.write("```yaml\na: 1\n```\n\n```yaml\na: 2\n```\n")
        old = profile_mod.PROFILES
        profile_mod.PROFILES = pathlib.Path(d)
        try:
            with self.assertRaises(ValueError):
                profile_mod.load("t")
        finally:
            profile_mod.PROFILES = old


# =================================================================================================
# The channel split, which is conditional and must be able to say no.
# =================================================================================================

def _strat(viable="partial", awareness="emerging", exposure="low"):
    return {"channel_strategy": {"founder_network": {"viable": viable, "evidence": "x"},
                                 "category_awareness": awareness,
                                 "named_person_exposure": exposure}}


class TestChannelSplit(unittest.TestCase):
    def test_it_refuses_without_the_intake_answers(self):
        r = channel.recommend_channels({})
        self.assertIsNone(r["applies"])
        self.assertEqual(len(r["missing"]), 3)

    def test_yaml_booleans_are_accepted_as_the_words_somebody_typed(self):
        """`viable: yes` arrives from YAML as True. Rejecting it punishes the obvious spelling."""
        self.assertTrue(channel.recommend_channels(_strat(viable=True))["applies"])
        self.assertFalse(channel.recommend_channels(_strat(viable=False))["applies"])

    def test_no_usable_network_means_the_split_does_not_apply(self):
        r = channel.recommend_channels(_strat(viable="no"))
        self.assertFalse(r["applies"])
        self.assertEqual(set(r["channels"]), {"company"})

    def test_mofu_sits_on_both_channels(self):
        r = channel.recommend_channels(_strat())
        both = set(r["channels"]["clevel"]["carries"]) & set(r["channels"]["company"]["carries"])
        self.assertTrue(both)
        self.assertTrue(all(JOB_TO_TIER[j] == "MOFU" for j in both))

    def test_an_established_category_inverts_which_channel_is_funded_first(self):
        self.assertEqual(channel.recommend_channels(_strat(awareness="emerging"))["primary"],
                         "clevel")
        self.assertEqual(channel.recommend_channels(_strat(awareness="established"))["primary"],
                         "company")

    def test_high_exposure_moves_claim_bearing_work_to_the_page(self):
        self.assertTrue(any("WHO CARRIES THE RISK" in c
                            for c in channel.recommend_channels(_strat(exposure="high"))["cautions"]))


# =================================================================================================
# recommend(). Gate before Lift, in that order.
# =================================================================================================

class TestRecommend(unittest.TestCase):
    def test_it_never_offers_a_gate_blocked_format(self):
        r = recommend({"fmt": "text", "words": 250, "who": "founder", "proof": "NONE"},
                      profile=EXAMPLE)
        self.assertNotIn("video", {o["fmt"] for o in r["options"]})
        self.assertNotIn("carousel", {o["fmt"] for o in r["options"]})

    def test_every_option_carries_the_precondition_lift_cannot_check(self):
        r = recommend({"fmt": "text", "words": 250, "proof": "NONE"}, profile=EXAMPLE)
        self.assertTrue(all(o["needs"] for o in r["options"]))

    def test_it_declines_a_word_target_with_no_measured_bands(self):
        r = recommend({"fmt": "text", "words": 250, "proof": "NONE"})
        self.assertIsNone(r["words"]["in_best_band"])


class TestScoreSlot(unittest.TestCase):
    def test_every_result_carries_a_line_a_human_can_argue_with(self):
        for prof in ({}, EXAMPLE):
            r = score_slot({"fmt": "text", "words": 250, "proof": "NONE",
                            "angle": "explainer"}, prof, "clevel")
            self.assertTrue(r["why"] and isinstance(r["why"], str))


if __name__ == "__main__":
    unittest.main()
