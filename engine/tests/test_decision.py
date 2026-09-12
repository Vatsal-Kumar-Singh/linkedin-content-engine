"""The decision layer: Gate, Lift, Fit, the buying-job classifier, the channel split.

**Most of these check that the scorer REFUSES correctly**, because the failure mode here is
silent. A component that quietly falls back to a default produces a plausible number and nothing
looks wrong. This module ships with no measurements at all, so every refusal is load-bearing.

    cd tests && python -m unittest discover -s . -t .
"""
import copy
import os
import statistics
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decision import profile as profile_mod
from decision import channel, scoring
from decision.channel import recommend_channels
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
        r = lift({"fmt": "text", "words": 300}, "founder")
        self.assertIsNone(r["score"])
        self.assertTrue(any("profile" in n for n in r["notes"]))

    def test_lift_scores_once_a_profile_supplies_a_corpus(self):
        r = lift({"fmt": "text", "words": 300}, "founder", profile=EXAMPLE)
        self.assertIsNotNone(r["score"])

    def test_two_profiles_produce_different_scores(self):
        """The point of the whole indirection. If this passes trivially it is decorative."""
        other = copy.deepcopy(EXAMPLE)
        other["corpus"]["format_lift"]["founder"] = {"text": 900.0, "photo album": 100.0}
        mine = lift({"fmt": "text", "words": 300}, "founder", EXAMPLE)["components"]["format"]
        theirs = lift({"fmt": "text", "words": 300}, "founder", other)["components"]["format"]
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

# Channels are declared, never assumed, so every fixture has to say what this company has.
TWO_CHANNELS = {"founder": {"kind": "person"}, "page": {"kind": "organisation"}}


def _strat(viable="partial", awareness="emerging", exposure="low", channels=None):
    return {"channels": dict(TWO_CHANNELS if channels is None else channels),
            "channel_strategy": {"founder_network": {"viable": viable, "evidence": "x"},
                                 "category_awareness": awareness,
                                 "named_person_exposure": exposure}}


class TestChannelSplit(unittest.TestCase):
    def test_it_refuses_without_the_intake_answers(self):
        """Four things now, because which channels exist is also the profile's to say."""
        r = channel.recommend_channels({})
        self.assertIsNone(r["applies"])
        self.assertEqual(len(r["missing"]), 4)
        self.assertTrue(any("channels" in m for m in r["missing"]))

    def test_yaml_booleans_are_accepted_as_the_words_somebody_typed(self):
        """`viable: yes` arrives from YAML as True. Rejecting it punishes the obvious spelling."""
        self.assertTrue(channel.recommend_channels(_strat(viable=True))["applies"])
        self.assertFalse(channel.recommend_channels(_strat(viable=False))["applies"])

    def test_no_usable_network_means_the_split_does_not_apply(self):
        r = channel.recommend_channels(_strat(viable="no"))
        self.assertFalse(r["applies"])
        self.assertEqual(set(r["channels"]), {"page"})

    def test_mofu_sits_on_both_channels(self):
        r = channel.recommend_channels(_strat())
        both = set(r["channels"]["founder"]["carries"]) & set(r["channels"]["page"]["carries"])
        self.assertTrue(both)
        self.assertTrue(all(JOB_TO_TIER[j] == "MOFU" for j in both))

    def test_an_established_category_inverts_which_channel_is_funded_first(self):
        self.assertEqual(channel.recommend_channels(_strat(awareness="emerging"))["primary"],
                         "founder")
        self.assertEqual(channel.recommend_channels(_strat(awareness="established"))["primary"],
                         "page")

    def test_high_exposure_moves_claim_bearing_work_to_the_page(self):
        self.assertTrue(any("WHO CARRIES THE RISK" in c
                            for c in channel.recommend_channels(_strat(exposure="high"))["cautions"]))


# =================================================================================================
# recommend(). Gate before Lift, in that order.
# =================================================================================================

class TestRecommend(unittest.TestCase):
    def test_it_never_offers_a_gate_blocked_format(self):
        r = recommend({"fmt": "text", "words": 250, "who": "founder", "proof": "NONE"},
                      "founder", EXAMPLE)
        self.assertNotIn("video", {o["fmt"] for o in r["options"]})
        self.assertNotIn("carousel", {o["fmt"] for o in r["options"]})

    def test_every_option_carries_the_precondition_lift_cannot_check(self):
        r = recommend({"fmt": "text", "words": 250, "proof": "NONE"}, "page", EXAMPLE)
        self.assertTrue(all(o["needs"] for o in r["options"]))

    def test_it_declines_a_word_target_with_no_measured_bands(self):
        r = recommend({"fmt": "text", "words": 250, "proof": "NONE"}, "founder")
        self.assertIsNone(r["words"]["in_best_band"])


class TestScoreSlot(unittest.TestCase):
    def test_every_result_carries_a_line_a_human_can_argue_with(self):
        for prof in ({}, EXAMPLE):
            r = score_slot({"fmt": "text", "words": 250, "proof": "NONE",
                            "angle": "explainer"}, prof, "founder")
            self.assertTrue(r["why"] and isinstance(r["why"], str))


if __name__ == "__main__":
    unittest.main()


# =================================================================================================
# measure_corpus.py — the tool that fills a profile's `corpus:` block.
#
# **Tested by planting a structure and checking it comes back**, because a measurement script that
# runs cleanly and reports the wrong numbers is the exact silent failure this repo keeps hitting.
# =================================================================================================

class TestMeasureCorpus(unittest.TestCase):
    @staticmethod
    def _rows():
        """Two authors, a 6x audience gap, and a known length and format effect planted in."""
        import random
        rng = random.Random(7)
        rows = []
        for author, scale in (("small", 40.0), ("large", 320.0)):
            for _ in range(60):
                words = rng.choice([rng.randint(20, 49), rng.randint(50, 99),
                                    rng.randint(100, 179), rng.randint(180, 400)])
                fmt = rng.choice(["text", "single image", "photo album", "photo album"])
                length_effect = 0.5 if words < 100 else (1.0 if words < 180 else 1.8)
                fmt_effect = {"text": 0.6, "single image": 1.0, "photo album": 1.7}[fmt]
                rows.append({"author": author, "channel": "c", "words": words, "format": fmt,
                             "eng": scale * length_effect * fmt_effect * rng.uniform(0.7, 1.3)})
        return rows

    def _module(self):
        import importlib.util
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "scripts", "measure_corpus.py")
        spec = importlib.util.spec_from_file_location("measure_corpus", path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_normalisation_removes_the_audience_gap(self):
        """The whole point. One author earns 8x the other and it says nothing about post shape."""
        m = self._module()
        rows, medians, _ = m.normalise(self._rows())
        self.assertGreater(max(medians.values()) / min(medians.values()), 4,
                           "the fixture should contain a large audience gap")
        for author in medians:
            rel = statistics.median([r["rel"] for r in rows if r["author"] == author])
            self.assertAlmostEqual(rel, 1.0, delta=0.15,
                                   msg="after normalising, each author centres on 1.0")

    def test_the_planted_length_effect_comes_back_in_order(self):
        m = self._module()
        rows, _, _ = m.normalise(self._rows())
        meds = []
        for band in m.DEFAULT_BANDS:
            vals = [r["rel"] for r in rows if m.band_of(r["words"], m.DEFAULT_BANDS) == band]
            meds.append(statistics.median(vals))
        self.assertEqual(meds, sorted(meds, reverse=True),
                         "longer bands were planted as stronger and must come back that way")

    def test_the_planted_format_effect_comes_back_in_order(self):
        m = self._module()
        rows, _, _ = m.normalise(self._rows())
        got = {f: statistics.median([r["rel"] for r in rows if r["format"] == f])
               for f in ("text", "single image", "photo album")}
        self.assertLess(got["text"], got["single image"])
        self.assertLess(got["single image"], got["photo album"])

    def test_an_author_with_no_engagement_is_dropped_not_divided_by(self):
        m = self._module()
        rows = self._rows() + [{"author": "silent", "channel": "c", "words": 200,
                                "format": "text", "eng": 0.0}]
        kept, _, dropped = m.normalise(rows)
        self.assertEqual(len(dropped), 1)
        self.assertNotIn("silent", {r["author"] for r in kept})


# =================================================================================================
# gen_calendar.py — the seam between the decision layer and the pipeline.
#
# **The integration test that matters**: what this emits must be something `run.py` can load
# without any change downstream. If that stops being true, the two halves have come apart.
# =================================================================================================

class TestCalendarGenerator(unittest.TestCase):
    def _gen(self):
        import importlib.util
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "scripts", "gen_calendar.py")
        spec = importlib.util.spec_from_file_location("gen_calendar", path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def _slots(self, channel="founder"):
        m = self._gen()
        from decision.channel import recommend_channels
        carried = set(recommend_channels(EXAMPLE)["channels"][channel]["carries"])
        kind = recommend_channels(EXAMPLE)["channels"][channel]["kind"]
        return m, m.candidates(m.load_registry(), carried, "a buyer", channel, kind)

    def test_what_it_emits_loads_as_a_content_spec(self):
        """The whole claim of seamlessness, asserted rather than hoped for."""
        from postengine.models import ContentSpec
        m, slots = self._slots()
        self.assertTrue(slots)
        for i, s in enumerate(slots[:5], 1):
            ContentSpec.from_dict(m.to_spec(s, i, "t"))     # raises SpecError if it would not

    def test_a_channel_only_gets_the_jobs_it_carries(self):
        from decision.channel import recommend_channels
        rec = recommend_channels(EXAMPLE)
        for ch in ("founder", "page"):
            _, slots = self._slots(ch)
            carried = set(rec["channels"][ch]["carries"])
            self.assertTrue(slots, ch)
            self.assertTrue({s["job"] for s in slots} <= carried, ch)

    def test_the_two_channels_produce_different_work(self):
        """If they came back the same, the channel split would be decoration."""
        _, cl = self._slots("founder")
        _, co = self._slots("page")
        self.assertNotEqual({s["job"] for s in cl}, {s["job"] for s in co})

    def test_an_executive_slot_is_marked_so_the_carousel_ban_applies(self):
        """Gate reads `who`. Without it the scorer recommends a designed carousel for every
        executive slot, because carousel tops most corpora and nothing was stopping it."""
        m, cl = self._slots("founder")
        _, co = self._slots("page")
        self.assertTrue(all(s.get("who") for s in cl))
        self.assertFalse(any(s.get("who") for s in co))
        blocked = m.recommend(dict(cl[0], fmt="carousel"), "founder", EXAMPLE)
        self.assertNotIn("carousel", {o["fmt"] for o in blocked["options"]})

    def test_no_slot_serves_an_objective_funded_separately(self):
        """Recruitment has its own budget. It must not compete for calendar slots."""
        _, slots = self._slots()
        self.assertFalse(any(s["angle"] in ("hiring", "career-arc") for s in slots))


# =================================================================================================
# Format -> template. The last seam: what the corpus says wins, translated into what renders.
# =================================================================================================

class TestFormatDrivesTemplate(unittest.TestCase):
    def test_every_known_format_maps_to_a_template_the_router_understands(self):
        """A format mapping to a template the engine has no router entry for renders nothing."""
        import yaml
        from decision.scoring import FORMAT_PRODUCTION
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "config", "engine.yaml")
        with open(path, encoding="utf-8") as fh:
            router = (yaml.safe_load(fh) or {}).get("template_router") or {}
        known = set((router.get("default") or {}))
        for fmt, spec in FORMAT_PRODUCTION.items():
            self.assertIn(spec["template"], known, fmt)

    def test_a_format_this_engine_cannot_render_ships_on_text(self):
        """A photo album is photographs. Claiming a CARD for one is claiming a creative that
        nobody will make, and the post then ships late or without art."""
        from decision.scoring import FORMAT_PRODUCTION
        for fmt, spec in FORMAT_PRODUCTION.items():
            if not spec["rendered"]:
                self.assertEqual(spec["template"], "TEXT", fmt)

    def test_recommend_reports_the_template_and_who_makes_the_creative(self):
        r = recommend({"fmt": "text", "words": 250, "proof": "NONE"}, "page", EXAMPLE)
        self.assertIsNotNone(r["template"])
        self.assertIsInstance(r["rendered"], bool)

    def test_the_two_channels_choose_different_templates_from_one_profile(self):
        """The reason format lift is measured per channel, asserted end to end."""
        exec_slot = {"fmt": "text", "words": 250, "who": "x", "proof": "NONE"}
        page_slot = {"fmt": "text", "words": 250, "proof": "NONE"}
        a = recommend(exec_slot, "founder", EXAMPLE)
        b = recommend(page_slot, "page", EXAMPLE)
        self.assertNotEqual(a["template"], b["template"])
        self.assertFalse(a["rendered"])     # profile rewards photographs
        self.assertTrue(b["rendered"])      # page rewards designed work

    def test_the_generated_spec_carries_the_recommended_template(self):
        """If the spec ignored the recommendation the wiring would be decorative."""
        import importlib.util
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "scripts", "gen_calendar.py")
        spec_ = importlib.util.spec_from_file_location("gen_calendar", path)
        m = importlib.util.module_from_spec(spec_)
        spec_.loader.exec_module(m)
        from decision.channel import recommend_channels
        for ch in ("founder", "page"):
            carried = set(recommend_channels(EXAMPLE)["channels"][ch]["carries"])
            kind = recommend_channels(EXAMPLE)["channels"][ch]["kind"]
            slot = m.candidates(m.load_registry(), carried, "a buyer", ch, kind)[0]
            rec = recommend(slot, ch, EXAMPLE)
            out = m.to_spec(slot, 1, "t", rec)
            self.assertEqual(out["template"], rec["template"], ch)
            self.assertEqual(out["creative_format"], rec["format"], ch)


# =================================================================================================
# Company type. Two axes: what you sell, and how it gets bought.
#
# It sat in the profile and nothing read it, which made it a note rather than a decision. These
# check that it now changes answers, and that an undeclared type is not silently treated as the
# case most published advice assumes.
# =================================================================================================

class TestCompanyType(unittest.TestCase):
    def _ct(self):
        from decision import company_type
        return company_type

    def test_an_undeclared_type_is_not_quietly_defaulted(self):
        """Most content advice assumes SaaS sold PLG. Defaulting to it hides the mismatch."""
        imp = self._ct().implications({})
        self.assertFalse(imp["declared"])
        self.assertEqual(imp["load_bearing"], [])
        self.assertTrue(imp["missing"])

    def test_every_rule_table_key_is_an_allowed_value(self):
        ct = self._ct()
        self.assertEqual(set(ct.MOTION_RULES), ct.MOTION)
        self.assertEqual(set(ct.OFFERING_RULES), ct.OFFERING)

    def test_every_named_job_is_a_real_buying_job(self):
        """A typo here silently stops a load-bearing job from ever being checked for."""
        ct = self._ct()
        for m, rules in ct.MOTION_RULES.items():
            for job in rules["load_bearing"] + rules["discounted"]:
                self.assertIn(job, JOB_TO_TIER, "%s names a job that does not exist" % m)

    def test_plg_discounts_consensus_and_slg_turns_on_it(self):
        """The single most useful distinction: in PLG the reader is the buyer; in SLG a messenger."""
        ct = self._ct()
        plg = ct.implications({"company_type": {"offering": "saas", "motion": "plg"}})
        slg = ct.implications({"company_type": {"offering": "saas", "motion": "slg"}})
        self.assertIn("consensus creation", plg["discounted"])
        self.assertIn("consensus creation", slg["load_bearing"])

    def test_selling_a_service_makes_the_named_channel_primary(self):
        """Awareness funds the page first for most companies. A service sale is a bet on people,
        and an organisation page cannot answer whether you want these specific humans."""
        base = {"channels": dict(TWO_CHANNELS),
                "channel_strategy": {"founder_network": {"viable": "yes", "evidence": "x"},
                                     "category_awareness": "established",
                                     "named_person_exposure": "low"}}
        saas = dict(base, company_type={"offering": "saas", "motion": "plg"})
        svc = dict(base, company_type={"offering": "service", "motion": "slg"})
        self.assertEqual(channel.recommend_channels(saas)["primary"], "page")
        self.assertEqual(channel.recommend_channels(svc)["primary"], "founder")

    def test_an_undeclared_type_is_flagged_on_the_channel_recommendation(self):
        base = {"channels": dict(TWO_CHANNELS),
                "channel_strategy": {"founder_network": {"viable": "yes", "evidence": "x"},
                                     "category_awareness": "emerging",
                                     "named_person_exposure": "low"}}
        self.assertTrue(any("company_type is not declared" in c
                            for c in channel.recommend_channels(base)["cautions"]))

    def test_the_check_does_not_demand_what_a_channel_cannot_carry(self):
        """**A warning that cannot be satisfied trains people to ignore the ones that can be.**

        An executive profile carries no consensus-creation work by construction, so demanding it
        there is noise. It is still reported, as a pointer to the channel that does carry it.
        """
        ct = self._ct()
        prof = {"company_type": {"offering": "saas", "motion": "slg"}}
        carried = {"problem identification", "solution exploration"}
        out = ct.check_calendar(prof, carried, carried)
        self.assertTrue(all("not carried by this channel" in f for f in out), out)

    def test_the_check_still_flags_a_gap_the_channel_could_have_filled(self):
        ct = self._ct()
        prof = {"company_type": {"offering": "saas", "motion": "slg"}}
        carried = {"consensus creation", "validation", "supplier selection"}
        out = ct.check_calendar(prof, {"validation"}, carried)
        self.assertTrue(any(f.startswith("NO consensus creation") for f in out), out)

    def test_it_returns_no_score_multipliers(self):
        """Constraints and cautions only. A scorer that refuses to invent a length band must not
        invent a weighting because a document implied one mattered."""
        imp = self._ct().implications({"company_type": {"offering": "product",
                                                        "motion": "enterprise"}})
        for v in imp.values():
            self.assertNotIsInstance(v, float)
