"""Template robustness. A template that overflows, clips, or shrinks text below
the mobile floor must fail loudly rather than ship an unreadable creative."""
import os
import shutil
import tempfile
import unittest

from helpers import CFG, draft, spec
from postengine.render.fit import BUDGETS, evaluate, precheck
from postengine.render.renderer import (build_page, card_slots, detect_renderer,
                                      doc_slots, _focal_parts)
from postengine.render.template import render


class TestMustacheLite(unittest.TestCase):
    def test_variables_sections_and_inversions(self):
        self.assertEqual(render("{{a}}", {"a": "x"}), "x")
        self.assertEqual(render("{{#a}}Y{{/a}}", {"a": True}), "Y")
        self.assertEqual(render("{{#a}}Y{{/a}}", {"a": ""}), "")
        self.assertEqual(render("{{^a}}N{{/a}}", {"a": ""}), "N")
        self.assertEqual(render("{{#xs}}[{{.}}]{{/xs}}", {"xs": ["a", "b"]}), "[a][b]")

    def test_content_is_escaped_so_copy_cannot_inject_markup(self):
        out = render("{{a}}", {"a": "<script>alert(1)</script>"})
        self.assertNotIn("<script>", out)

    def test_missing_variable_renders_empty_not_literal(self):
        self.assertEqual(render("x{{nope}}y", {}), "xy")


class TestFocalParsing(unittest.TestCase):
    def test_symbol_rides_the_figure_inline(self):
        d = draft(focal="60", focal_unit="%")
        self.assertEqual(_focal_parts(d), ("60", "%", ""))

    def test_multi_character_symbol_stays_inline(self):
        d = draft(focal="40", focal_unit="%+")
        self.assertEqual(_focal_parts(d), ("40", "%+", ""))

    def test_word_unit_sits_beneath(self):
        d = draft(focal="9–14", focal_unit="months")
        self.assertEqual(_focal_parts(d), ("9–14", "", "months"))

    def test_phrase_focal_has_no_unit(self):
        d = draft(focal="No ceiling", focal_unit="")
        self.assertEqual(_focal_parts(d), ("No ceiling", "", ""))

    def test_falls_back_to_parsing_the_headline(self):
        d = draft(focal="", focal_unit="", creative_headline="9–14 months")
        self.assertEqual(_focal_parts(d), ("9–14", "", "months"))


class TestPrecheck(unittest.TestCase):
    def test_absurdly_long_slot_is_rejected_before_a_browser_starts(self):
        problems = precheck({"focal": "x" * 200})
        self.assertTrue(problems)
        self.assertIn("focal", problems[0])

    def test_reasonable_slots_pass(self):
        self.assertEqual(precheck({"focal": "60", "deck": "A short line."}), [])

    def test_every_budget_is_a_sane_band(self):
        for name, (lo, hi) in BUDGETS.items():
            self.assertLess(lo, hi, name)


class TestFitEvaluation(unittest.TestCase):
    def test_overflow_is_reported(self):
        p = evaluate({"overflow": True, "overflowing_elements": ["deck"],
                      "smallest_text_px": 40, "adjusted": []}, 30, 24, True)
        self.assertTrue(any("clipped" in x for x in p))

    def test_text_below_the_mobile_floor_is_reported(self):
        p = evaluate({"overflow": False, "smallest_text_px": 18, "adjusted": []}, 30, 24, True)
        self.assertTrue(any("below the 24px caption floor" in x for x in p))

    def test_autofit_shrinking_past_the_body_floor_is_reported(self):
        p = evaluate({"overflow": False, "smallest_text_px": 40,
                      "adjusted": [{"selector": "deck", "from": 60, "to": 21, "steps": 6}]},
                     30, 24, True)
        self.assertTrue(any("too long for the slot" in x for x in p))

    def test_a_clean_render_reports_nothing(self):
        self.assertEqual(evaluate({"overflow": False, "smallest_text_px": 26,
                                   "adjusted": []}, 30, 24, True), [])


class TestPageAssembly(unittest.TestCase):
    def test_brand_tokens_come_from_config_not_the_template(self):
        html = build_page(CFG, "card/big_stat",
                          card_slots(CFG, draft(), spec(), "card/big_stat"), "CARD")
        self.assertIn(CFG.brand["palette"]["deep_navy"], html)
        self.assertIn(CFG.brand["palette"]["brand_blue"], html)

    def test_fonts_are_embedded_so_the_render_never_depends_on_a_network(self):
        html = build_page(CFG, "card/big_stat",
                          card_slots(CFG, draft(), spec(), "card/big_stat"), "CARD")
        self.assertIn("data:font/woff2;base64,", html)
        self.assertNotIn("fonts.googleapis.com", html)

    def test_no_unresolved_placeholders_remain(self):
        html = build_page(CFG, "card/big_stat",
                          card_slots(CFG, draft(), spec(), "card/big_stat"), "CARD")
        self.assertNotIn("{{", html)

    def test_document_template_assembles_for_every_slide_kind(self):
        for kind in ("cover", "point", "turn", "close"):
            slide = type("S", (), {"kind": kind, "headline": "Three word headline",
                                   "body": "Some body."})()
            html = build_page(CFG, "document/editorial",
                              doc_slots(CFG, draft(), spec(template="DOC"), 1, 8, slide), "DOC")
            self.assertNotIn("{{", html)

    def test_the_approved_tagline_is_never_reworded(self):
        """Creatives now carry the positioning line rather than the corporate
        tagline — brand presence is restrained, and the product is not governed by
        Brand Book v1.4 (ruling 1). Where the tagline DOES appear it must be the
        approved string exactly: that is the one string the Brand Book locks."""
        html = build_page(CFG, "card/big_stat",
                          card_slots(CFG, draft(), spec(), "card/big_stat"), "CARD")
        self.assertNotIn("Outcomes-Delivered", html)
        if "AI-Native" in html:
            self.assertIn("AI-Native · Secure by Design · Outcomes Delivered", html)


@unittest.skipIf(detect_renderer("auto") == "none", "no headless browser available")
class TestLiveRender(unittest.TestCase):
    """The real thing: long copy must be caught by measurement, not by hope."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _measure(self, slots):
        from playwright.sync_api import sync_playwright
        from postengine.render.fit import FIT_JS
        html = build_page(CFG, "card/big_stat", slots, "CARD")
        path = os.path.join(self.tmp, "t.html")
        open(path, "w", encoding="utf-8").write(html)
        geo = CFG.brand["formats"]["CARD"]
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": geo["width"], "height": geo["height"]})
            pg.goto("file://" + path, wait_until="load")
            pg.wait_for_timeout(120)
            m = pg.evaluate(FIT_JS, {"ratio": 0.94, "maxSteps": 6, "floor": 24,
                                     "clipTolerance": 14,
                                     "width": geo["width"], "height": geo["height"]})
            b.close()
        return m

    def test_the_design_survives_at_mobile_feed_size(self):
        """A LinkedIn creative is judged at roughly 430pt wide."""
        from postengine.render.mobile import check as check_mobile
        m = self._measure(card_slots(
            CFG, draft(focal="60", focal_unit="%", creative_headline="60%"),
            spec(), "card/big_stat"))
        geo = CFG.brand["formats"]["CARD"]
        self.assertEqual(check_mobile(m, geo["height"], 430, geo["width"]), [])

    def test_the_composition_occupies_the_canvas(self):
        """The old system floated content in a coloured rectangle."""
        m = self._measure(card_slots(
            CFG, draft(focal="60", focal_unit="%", creative_headline="60%"),
            spec(), "card/big_stat"))
        self.assertGreaterEqual(m["canvas_utilization"], 0.70,
                                "composition does not occupy the page")
        self.assertGreaterEqual(m["type_scale_ratio"], 6.0,
                                "type-scale contrast too weak — no entry point")

    def test_normal_copy_renders_within_the_legibility_floors(self):
        m = self._measure(card_slots(CFG, draft(), spec(), "card/big_stat"))
        problems = evaluate(m, CFG.brand["legibility"]["min_body_px"],
                            CFG.brand["legibility"]["min_caption_px"], True)
        self.assertEqual(problems, [], problems)

    def test_grossly_overlong_copy_is_caught_by_measurement(self):
        slots = card_slots(CFG, draft(
            creative_supporting_copy=("This supporting line is far longer than the slot "
                                      "was ever designed to hold and keeps going well past "
                                      "any reasonable limit for a single card. ") * 6,
            creative_qualifier="A qualifier that is also much longer than it should be, "
                               "repeated for effect, repeated for effect, again."),
            spec(), "card/big_stat")
        m = self._measure(slots)
        problems = evaluate(m, CFG.brand["legibility"]["min_body_px"],
                            CFG.brand["legibility"]["min_caption_px"], True)
        self.assertTrue(problems, "overlong copy must be detected, not silently clipped")

    def test_nothing_is_ever_clipped_silently(self):
        m = self._measure(card_slots(CFG, draft(), spec(), "card/big_stat"))
        self.assertFalse(m["overflow"])
        self.assertIsNotNone(m["smallest_text_px"])


if __name__ == "__main__":
    unittest.main()
