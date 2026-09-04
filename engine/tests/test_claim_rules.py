"""Deterministic claim & policy rules — the layer that must never let a
prohibited claim through, regardless of what a model produced."""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from helpers import CFG, draft, failed_ids, spec
from postengine.validators import Validator

V = Validator(CFG)








class TestNamingCanon(unittest.TestCase):
    """N1 holds your brand's naming rules. The example ships one — a misspelling
    gate — because the shape is what transfers, not the names.

    Whatever your brand book says MUST NOT be written, encode there. A rule
    nobody can break by accident does not need a gate; a rule a tired person
    breaks at 6pm does.
    """

    def test_the_example_misspelling_gate_fires(self):
        r = V.validate(draft(body="We built this on Meridien last year."), spec())
        self.assertIn("N1.1", failed_ids(r))

    def test_the_correct_spelling_passes(self):
        r = V.validate(draft(body="We built this on Meridian last year."), spec())
        self.assertNotIn("N1.1", failed_ids(r))


class TestInternalLeak(unittest.TestCase):
    def test_internal_filenames_block(self):
        r = V.validate(draft(body="See our decisions-log for detail."), spec())
        self.assertIn("L1.1", failed_ids(r))

    def test_governance_language_blocks(self):
        r = V.validate(draft(body="Per ruling 3, this claim is withdrawn."), spec())
        self.assertIn("L1.2", failed_ids(r))

    def test_confidence_markers_block(self):
        r = V.validate(draft(body="This figure is UNVERIFIED."), spec())
        self.assertIn("L1.3", failed_ids(r))


class TestVoiceAndHumanness(unittest.TestCase):
    def test_auto_zero_phrases_fail(self):
        for phrase in ("We are revolutionizing data delivery.",
                       "A genuine game-changer for platform teams.",
                       "Unlock the power of your existing licences.",
                       "In today's fast-paced digital landscape, teams struggle.",
                       "We're excited to announce our new model."):
            r = V.validate(draft(body=phrase), spec())
            self.assertIn("C3.1", failed_ids(r), phrase)

    def test_auto_zero_is_flagged_for_the_brand_voice_rule(self):
        r = V.validate(draft(body="We are revolutionizing delivery."), spec())
        self.assertTrue(r.auto_zero_brand_voice())

    def test_tick_mark_list_fails(self):
        r = V.validate(draft(body="✓ Automated releases ✓ Governed pipeline ✓ Full audit"), spec())
        self.assertIn("C4.1", failed_ids(r))

    def test_not_just_construction_fails(self):
        r = V.validate(draft(body="It's not just faster — it's fundamentally different."), spec())
        self.assertIn("C4.2", failed_ids(r))

    def test_rhetorical_question_answered_immediately_fails(self):
        r = V.validate(draft(body="Who owns the outcome? Nobody. It's the "
                                  "structural problem in the model."), spec())
        self.assertIn("C4.4", failed_ids(r))

    def test_overlong_hook_fails(self):
        r = V.validate(draft(hook="Let us take a moment to consider exactly why change "
                                  "orders have quietly become the biggest problem here"),
                       spec())
        self.assertIn("C1.1", failed_ids(r))

    def test_buzzwords_warn_but_do_not_fail(self):
        r = V.validate(draft(body="A best-in-class, cutting-edge approach."), spec())
        warn_ids = [x.check_id for x in r.warnings]
        self.assertIn("C3.2", warn_ids)
        self.assertNotIn("C3.2", [x.check_id for x in r.binary_failures])



class TestLengthAndStructure(unittest.TestCase):
    def test_text_post_below_band_fails(self):
        r = V.validate(draft(body="Short."), spec(template="TEXT"))
        self.assertIn("B4.1", failed_ids(r))

    def test_doc_slide_count_out_of_range_fails(self):
        d = draft(slides=[{"headline": "One two three", "body": ""}] * 3)
        r = V.validate(d, spec(template="DOC"))
        self.assertIn("B6.1", failed_ids(r))

    def test_doc_per_slide_limits_fail(self):
        slides = [{"headline": "Ok headline here", "body": ""} for _ in range(6)]
        slides[2] = {"headline": "This particular slide headline runs to far too many words indeed",
                     "body": "One. Two. Three."}
        r = V.validate(draft(slides=slides), spec(template="DOC"))
        self.assertIn("B8.1", failed_ids(r))

    def test_missing_cta_fails(self):
        r = V.validate(draft(cta=""), spec())
        self.assertIn("B12.1", failed_ids(r))

    def test_deliberate_no_cta_passes(self):
        r = V.validate(draft(cta="none-by-design"), spec())
        self.assertNotIn("B12.1", failed_ids(r))



class TestBlindHeadlineGate(unittest.TestCase):
    """C0.3 exists to catch a headline that means nothing on its own.

    It was inert. C0.1 requires every headline to name the subject word, and `the subject word`
    was in C0.3's own list of concrete nouns — so C0.3 was satisfied by the thing
    another gate already mandated, and could never fire. "Meridian: no ceiling"
    reached a rendered card through that hole, and the gate's own fix text names
    "No ceiling" as the canonical failure it was meant to stop.
    """

    @staticmethod
    def _pattern():
        import re
        import yaml
        with open(os.path.join(ROOT, "config", "claim-rules.yaml"), encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)

        def find(node):
            if isinstance(node, dict):
                if node.get("id") == "C0.3":
                    return node
                for v in node.values():
                    hit = find(v)
                    if hit:
                        return hit
            if isinstance(node, list):
                for v in node:
                    hit = find(v)
                    if hit:
                        return hit
            return None

        return re.compile(find(doc)["pattern"])

    def test_naming_the_subject_alone_does_not_satisfy_the_gate(self):
        pat = self._pattern()
        for blind in ("Meridian: no ceiling",
                      "the subject word, unlocked",
                      "The the subject word ceiling",
                      "Rethinking the subject word"):
            self.assertIsNone(pat.search(blind),
                              "%r should be caught as a blind headline" % blind)

    def test_a_concrete_headline_passes(self):
        pat = self._pattern()
        for good in ("Every the subject word change is another invoice",
                     "Nobody can tell you next year's the subject word bill",
                     "Your analysts are stuck checking jobs"):
            self.assertIsNotNone(pat.search(good), good)


class TestClosedQuestionGate(unittest.TestCase):
    """A question headline is often stronger than a statement — the reader has to
    answer it themselves rather than accept or reject a claim. But only if they
    cannot answer it in one word. "Is your the subject word bill too high?" passed every
    gate we had: it names the subject word (C0.1) and carries a concrete noun (C0.3).
    Nothing checked whether the reader could dismiss it."""

    @staticmethod
    def _pattern(rule_id):
        import re
        import yaml
        with open(os.path.join(ROOT, "config", "claim-rules.yaml"), encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)

        def find(node):
            if isinstance(node, dict):
                if node.get("id") == rule_id:
                    return node
                for v in node.values():
                    hit = find(v)
                    if hit:
                        return hit
            if isinstance(node, list):
                for v in node:
                    hit = find(v)
                    if hit:
                        return hit
            return None

        return re.compile(find(doc)["pattern"])

    def test_yes_no_questions_are_refused(self):
        pat = self._pattern("C0.4")
        for closed in ("Is your the subject word bill too high?",
                       "Are you happy with your the subject word partner?",
                       "Can the subject word changes ship faster?",
                       "Do your the subject word admins spend the week on tickets?"):
            self.assertIsNotNone(pat.search(closed),
                                 "%r is answerable in one word" % closed)

    def test_open_questions_and_statements_pass(self):
        pat = self._pattern("C0.4")
        for good in ("What will the subject word cost you next year?",
                     "What is the subject word going to cost you next year?",
                     "How many the subject word tickets did your admin close this week?",
                     "Ask for one the subject word field. Get a quote.",
                     "Every the subject word change is another invoice"):
            self.assertIsNone(pat.search(good), good)


class TestSubjectWordIsActuallyRequired(unittest.TestCase):
    """C0.1 is the load-bearing gate — every other content rule assumes the word
    is there, and the algorithm's topic classification depends on it too.

    It had no test. A mutation replacing its pattern with one that matches any
    single letter passed the entire suite: the gate could have been silently
    neutered and nothing would have said so. Every other gate we have added since
    was tested; the oldest and most important one was not.
    """

    @staticmethod
    def _rule(rule_id):
        import yaml
        with open(os.path.join(ROOT, "config", "claim-rules.yaml"), encoding="utf-8") as fh:
            doc = yaml.safe_load(fh)

        def find(node):
            if isinstance(node, dict):
                if node.get("id") == rule_id:
                    return node
                for v in node.values():
                    hit = find(v)
                    if hit:
                        return hit
            if isinstance(node, list):
                for v in node:
                    hit = find(v)
                    if hit:
                        return hit
            return None

        return find(doc)

    def test_c01_exists_and_targets_the_frontline_fields(self):
        r = self._rule("C0.1")
        self.assertIsNotNone(r, "C0.1 has been removed")
        self.assertEqual(r["type"], "required_pattern")
        self.assertEqual(r["scope"], "frontline")
        self.assertTrue(r.get("in_any"), "C0.1 must pass when ANY frontline field names the subject word")
        self.assertEqual(r["severity"], "fail")

    def test_c01_matches_the_subject_word_and_nothing_else(self):
        """The mutation that survived replaced the pattern with one matching any
        letter. Assert the pattern is specific, not merely present."""
        import re
        pat = re.compile(self._rule("C0.1")["pattern"])
        for names in ("We watch your Meridian pipelines", "data pipeline alerts", "PIPELINE"):
            self.assertIsNotNone(pat.search(names), names)
        for doesnt in ("We watch your dashboards", "One price a month",
                       "a", "pipe line", "line"):
            self.assertIsNone(pat.search(doesnt),
                              "%r must not satisfy the subject-word requirement" % doesnt)


# NOTE ON WHAT IS NOT HERE
#
# The original project had six gate classes testing claim-specific rules —
# withdrawn competitor claims, an unsourced executive quote, a figure the source
# deck contradicted two slides later. Those gates and their tests were entirely
# client-specific and are not shipped.
#
# The SHAPE transfers. When you write your own claim gates in the marked block in
# claim-rules.yaml, test each one against strings that should pass AND strings
# that should fail, then break it and confirm scripts/mutation_check.py notices.
# A gate nobody has tried to evade is a gate nobody knows works.
