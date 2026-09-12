"""Motion variants. The still PNG is the product; the loop is an addition that
must never change what the card says or how it is judged."""
import glob
import io
import math
import os
import shutil
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from helpers import CFG, draft, spec
from postengine.render.backgrounds import _pulse, _visible_arc, compose
from postengine.render.renderer import build_page, card_slots, detect_renderer

# Derived from the filesystem, not hand-listed. The hand-written list held three
# of seven templates, so the CTA guard below was not checking card/wash — the one
# Round 1 actually uses. A mutation that rendered the CTA onto that card passed
# the whole suite. A new template now joins these checks automatically.
TEMPLATES = sorted(
    "card/" + os.path.basename(os.path.dirname(p))
    for p in glob.glob(os.path.join(ROOT, "templates", "card", "*", "template.html"))
)


class TestPulseGeometry(unittest.TestCase):
    """The tracings are cropped on purpose — centres sit off-canvas. A sweep
    around the full circumference is therefore mostly invisible, and the card
    reads as frozen for seconds at a time. These pin the correction."""

    def test_a_fully_visible_circle_returns_the_whole_turn(self):
        self.assertEqual(_visible_arc(600, 600, 100, 1200, 1200), (0.0, 2 * math.pi))

    def test_a_circle_entirely_outside_the_frame_returns_none(self):
        self.assertIsNone(_visible_arc(-5000, -5000, 10, 1200, 1200))

    def test_a_cropped_circle_returns_only_the_on_canvas_run(self):
        # The contrarian card's geometry: centre off the left edge.
        arc = _visible_arc(-168, 240, 552, 1200, 1200)
        self.assertIsNotNone(arc)
        span = arc[1] - arc[0]
        self.assertLess(span, 2 * math.pi * 0.5,
                        "a circle centred off-canvas cannot be half visible")
        self.assertGreater(span, 0.5, "the visible run should not be a sliver")

    def test_the_sweep_is_confined_to_the_visible_run(self):
        """The regression this exists for: with travel set to the full
        circumference, 83 of 84 captured frames were pixel-identical."""
        ctx = compose(CFG, ["geometry"], 1200, 1200,
                      {"geo_cx": -168, "geo_cy": 240, "geo_r": 552})
        travel = abs(ctx["pulse_to"] - ctx["pulse_from"])
        self.assertLess(travel, ctx["geo_c"],
                        "the pulse must not travel the whole circumference")
        self.assertGreater(travel, ctx["pulse_len"],
                           "the pulse must actually move further than its own length")

    def test_both_rings_get_their_own_sweep_range(self):
        ctx = compose(CFG, ["geometry"], 1200, 1200,
                      {"geo_cx": -168, "geo_cy": 240, "geo_r": 552})
        for key in ("pulse_from", "pulse_to", "pulse_from2", "pulse_to2",
                    "geo_c", "geo_c2", "pulse_peak", "pulse_peak2", "pulse_secs"):
            self.assertIn(key, ctx)
        self.assertNotEqual((ctx["pulse_from"], ctx["pulse_to"]),
                            (ctx["pulse_from2"], ctx["pulse_to2"]))
        self.assertLess(ctx["pulse_peak2"], ctx["pulse_peak"],
                        "the inner ring is the duller of the two, by design")


class TestAnimationIsOptIn(unittest.TestCase):
    """A static PNG must render identically whether or not motion exists."""

    def test_backgrounds_default_to_static(self):
        self.assertFalse(compose(CFG, ["geometry"], 1200, 1200, {})["animate"])

    def test_no_pulse_markup_without_the_flag(self):
        for t in TEMPLATES:
            slots = card_slots(CFG, draft(), spec(), t)
            self.assertNotIn("class=\"pulse", build_page(CFG, t, slots, "CARD"), t)

    def test_motion_markup_appears_with_the_flag(self):
        """Cards now carry the wash ground, so motion lives on its strokes. The
        ring comet it replaced still exists for the carousel, which is a
        separate pass and still includes the backgrounds partial."""
        slots = card_slots(CFG, draft(), spec(), "card/wash")
        slots["animate"] = True
        slots["wash_motion"] = "sweep"
        html = build_page(CFG, "card/wash", slots, "CARD", ground="dark")
        self.assertIn("wash--anim", html)
        self.assertIn("wash--sweep", html)
        self.assertIn('pathLength="1000"', html)

    def test_each_motion_mode_reaches_the_markup(self):
        """Four modes exist so the direction can be chosen by eye. Each has to
        actually reach the page — a mode that silently falls back to another
        would make the comparison meaningless."""
        for mode in ("sweep", "drift", "both", "draw"):
            slots = card_slots(CFG, draft(), spec(), "card/wash")
            slots["animate"] = True
            slots["wash_motion"] = mode
            html = build_page(CFG, "card/wash", slots, "CARD", ground="dark")
            self.assertIn("wash--" + mode, html, mode)

    def test_path_length_is_declared_on_every_stroke(self):
        """The motifs differ in real arc length by an order of magnitude — a
        spiral against a straight moire line — so one set of dash numbers only
        works if every path declares the same nominal length."""
        from postengine.render.backgrounds import SHAPES
        for shape in sorted(SHAPES):
            slots = card_slots(CFG, draft(), spec(), "card/wash")
            slots.update(compose(CFG, ["geometry"], 1200, 1200, {}))
            slots["animate"] = True
            slots["wash_shape"] = shape
            html = build_page(CFG, "card/wash", slots, "CARD", ground="dark")
            n_paths = html.count("<path pathLength=")
            self.assertGreater(n_paths, 0, shape)

    def test_the_shape_dims_through_the_type_rather_than_being_cut_by_it(self):
        """Every motif crosses the left-aligned type column sooner or later."""
        slots = card_slots(CFG, draft(), spec(), "card/wash")
        self.assertIn('mask="url(#washmask)"',
                      build_page(CFG, "card/wash", slots, "CARD", ground="light"))

    def test_every_layer_of_a_ring_shares_one_dash_period(self):
        """The bug this exists for. Gaps were originally the full circumference,
        giving the streak a period of `length + C` and the head a period of `C`.
        They wrapped at different points, so the head drifted a full streak-length
        off the front by the end of the sweep — measured at exactly 340px."""
        ctx = compose(CFG, ["geometry"], 1200, 1200,
                      {"geo_cx": -168, "geo_cy": 240, "geo_r": 552})
        for suffix in ("", "2"):
            circ = ctx["geo_c" + suffix]
            self.assertAlmostEqual(ctx["pulse_len" + suffix] + ctx["pulse_gap" + suffix],
                                   circ, delta=0.2, msg="streak period, ring " + suffix)
            self.assertAlmostEqual(0.01 + ctx["head_gap" + suffix],
                                   circ, delta=0.2, msg="head period, ring " + suffix)

    def test_the_dash_seam_is_rotated_away_from_the_visible_arc(self):
        """A dash straddling the path's start point is drawn as two pieces. That
        point is at (cx+r, cy) — (384, 240) on the contrarian card, inside the
        frame and directly under the sweep — so the streak tore in half as it
        crossed. Each ring is rotated to put the seam opposite the visible run."""
        cx, cy, r, w, h = -168, 240, 552, 1200, 1200
        ctx = compose(CFG, ["geometry"], w, h,
                      {"geo_cx": cx, "geo_cy": cy, "geo_r": r})
        arc = _visible_arc(cx, cy, r, w, h)
        for suffix, radius in (("", r), ("2", r * 0.70)):
            seam = math.radians(ctx["pulse_rot" + suffix])
            x, y = cx + radius * math.cos(seam), cy + radius * math.sin(seam)
            self.assertFalse(0 <= x <= w and 0 <= y <= h,
                             "the seam must not sit inside the frame (ring %s)" % suffix)
        # And the visible run ends up centred on pi, as far from the seam as
        # the geometry allows.
        span = arc[1] - arc[0]
        self.assertAlmostEqual(-ctx["pulse_from"] + ctx["pulse_len"],
                               r * (math.pi - span / 2), delta=1.0)

    def test_the_band_is_lifted_only_on_motion_variants(self):
        """LinkedIn paints scrub bar and sound toggle over the bottom of a video.
        That is exactly where the brandmark sits."""
        slots = card_slots(CFG, draft(), spec(), "card/contrarian")
        self.assertNotIn("padding-bottom:92px", build_page(CFG, "card/contrarian", slots, "CARD"))
        slots["animate"] = True
        self.assertIn("padding-bottom:92px", build_page(CFG, "card/contrarian", slots, "CARD"))


class TestCtaStaysOffTheCreative(unittest.TestCase):
    """The CTA belongs in the LinkedIn caption, not burned into the image.

    Three reasons, and all three still hold for the motion variant: an in-image
    CTA cannot be clicked; it dates the asset the moment the offer changes; and
    on a video post LinkedIn's own player chrome covers the bottom strip where
    a CTA would naturally sit. Nothing enforced this before — it was true only
    because no template happened to reference the field."""

    def test_no_card_template_renders_the_cta(self):
        d = draft(cta="CTA-CANARY-BOOK-A-CALL")
        for t in TEMPLATES:
            for animate in (False, True):
                slots = card_slots(CFG, d, spec(), t)
                slots["animate"] = animate
                self.assertNotIn("CTA-CANARY", build_page(CFG, t, slots, "CARD"),
                                 "%s (animate=%s)" % (t, animate))

    def test_no_template_source_mentions_the_cta_field(self):
        """The rendered-output check above is weaker than its name suggests.

        `cta` is never placed in the slots, so a template referencing {{cta}}
        renders EMPTY and the output check passes — for the wrong reason. A
        mutation adding {{cta}} to a card survived the whole suite. The day
        someone adds cta to the slots for an unrelated reason, that dormant
        reference starts printing a CTA onto the creative.

        So guard the source as well as the output.
        """
        import glob
        import re
        offenders = []
        pattern = re.compile(r"\{\{\{?\s*(#|\^)?\s*cta\s*\}?\}\}")
        for path in (glob.glob(os.path.join(ROOT, "templates", "*", "*", "template.html"))
                     + glob.glob(os.path.join(ROOT, "templates", "_shared", "*.html"))):
            src = io.open(path, encoding="utf-8").read()
            if pattern.search(src):
                offenders.append(os.path.relpath(path, ROOT))
        self.assertFalse(offenders,
                         "these templates reference the cta field; the CTA belongs "
                         "in the LinkedIn caption, never burned into the image: %s"
                         % offenders)

    def test_the_cta_is_not_even_placed_in_the_slots(self):
        slots = card_slots(CFG, draft(cta="CTA-CANARY-BOOK-A-CALL"), spec(), "card/contrarian")
        self.assertNotIn("CTA-CANARY", repr(slots))


@unittest.skipIf(detect_renderer("auto") != "playwright", "needs playwright")
class TestLiveMotion(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _page(self):
        slots = card_slots(CFG, draft(), spec(), "card/contrarian")
        slots["animate"] = True
        path = os.path.join(self.tmp, "a.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(build_page(CFG, "card/contrarian", slots, "CARD"))
        return path

    def test_frames_are_reproducible(self):
        """Frames are seeked, not sampled from the wall clock. Two captures of
        the same frame index must be byte-identical or the gauntlet loses its
        determinism the moment motion is switched on."""
        from postengine.render.animate import capture_frames
        p = self._page()
        a = capture_frames(p, os.path.join(self.tmp, "a"), 300, 300, seconds=7.0, fps=2)
        b = capture_frames(p, os.path.join(self.tmp, "b"), 300, 300, seconds=7.0, fps=2)
        self.assertEqual(len(a), len(b))
        for x, y in zip(a, b):
            with open(x, "rb") as fx, open(y, "rb") as fy:
                self.assertEqual(fx.read(), fy.read(), os.path.basename(x))

    def test_the_card_actually_moves_across_the_loop(self):
        """The bug this catches: a sweep that spends the cycle off-canvas still
        produces a valid GIF, it just produces a still one."""
        from PIL import Image, ImageChops
        from postengine.render.animate import capture_frames
        frames = capture_frames(self._page(), os.path.join(self.tmp, "f"),
                                1200, 1200, seconds=7.0, fps=4)
        base = Image.open(frames[0]).convert("RGB")
        moving = 0
        for f in frames[1:]:
            with Image.open(f) as im:
                d = ImageChops.difference(base, im.convert("RGB")).convert("L")
                if max(d.getextrema()) >= 8:
                    moving += 1
        self.assertGreaterEqual(moving, len(frames) - 2,
                                "the loop must not sit still for most of its length")


if __name__ == "__main__":
    unittest.main()


class TestPassTwoRefinements(unittest.TestCase):
    """Depth, the accent, and a highlight that works on both grounds."""

    def test_strokes_carry_their_own_weight_and_opacity(self):
        """Pass 1 drew every stroke in a bundle identically, which is why the
        figures read as flat diagrams. Variation across the bundle is what makes
        it a form."""
        ctx = compose(CFG, ["geometry"], 1200, 1200, {})
        from postengine.render.backgrounds import wash
        c = wash(CFG, "depth", 1200, 1200, {"wash_shape": "pencil"})
        widths = {p["sw"] for p in c["wash_paths"]}
        opac = {p["so"] for p in c["wash_paths"]}
        self.assertGreater(len(widths), 1, "every stroke has the same width")
        self.assertGreater(len(opac), 1, "every stroke has the same opacity")
        for p in c["wash_paths"]:
            self.assertGreaterEqual(p["sw"], 0.55)
            self.assertGreaterEqual(p["so"], 0.22)

    def test_the_accent_lands_on_the_figure(self):
        """The construction focus is the wrong place for contour, ripple and
        moire — those are built around a centre their strokes never touch, so an
        accent there floats in empty space."""
        import re
        from postengine.render.backgrounds import SHAPES, wash
        for shape in sorted(SHAPES):
            c = wash(CFG, "acc-" + shape, 1200, 1200, {"wash_shape": shape})
            dot = (c["wash_dot_x"], c["wash_dot_y"])
            pts = []
            for p in c["wash_paths"]:
                nums = [float(x) for x in re.findall(r"-?\d+\.?\d*", p["d"])]
                pts += [(nums[i], nums[i + 1]) for i in range(0, len(nums) - 1, 2)]
            near = min(math.hypot(dot[0] - x, dot[1] - y) for x, y in pts)
            self.assertLess(near, 2.0,
                            "%s: accent is %.0fpx off the figure" % (shape, near))

    def test_the_highlight_is_a_separate_layer_with_ground_aware_colour(self):
        """One brightening sweep cannot serve both grounds — on a pale wash it is
        invisible. The highlight is its own layer, lighter than the strokes on
        navy and darker than them on light."""
        from postengine.render.backgrounds import wash
        light = wash(CFG, "hi", 1200, 1200, {})
        dark = wash(CFG, "hi", 1200, 1200, {"wash_dark": True})
        self.assertNotEqual(light["wash_hi"], dark["wash_hi"])
        # Both sweeps must come from the palette rather than a literal in the code, and they
        # must differ. **Naming the two colours here would pin the test to one brand**, which is
        # what the previous version did and why it failed the moment the palette changed. The
        # claim being tested is "ground-aware, from config", and that is exactly what is asserted.
        colours = set(CFG.brand["palette"].values())
        self.assertIn(dark["wash_hi"], colours)
        self.assertIn(light["wash_hi"], colours)

    def test_motion_reaches_both_grounds(self):
        for ground, is_dark in (("light", False), ("dark", True)):
            slots = card_slots(CFG, draft(), spec(), "card/wash")
            from postengine.render.backgrounds import wash
            slots.update(wash(CFG, "m", 1200, 1200,
                              {"wash_dark": is_dark, "wash_motion": "sweep"}))
            slots["animate"] = True
            html = build_page(CFG, "card/wash", slots, "CARD", ground=ground)
            self.assertIn("wash-hi", html, ground)
            self.assertIn("wash--sweep", html, ground)


@unittest.skipIf(detect_renderer("auto") != "playwright", "needs playwright")
class TestAnimatedStillsAreDeterministic(unittest.TestCase):
    """Found by cloning the repo and comparing renders: all seven static cards
    came back byte-identical and all seven animated ones differed.

    A still of an animated card was sampling whatever moment the screenshot
    landed on, because the shooter never paused CSS animations. That made the
    design critic's input and the run's stored artefact vary between renders of
    the same card — while looking fine, which is why it survived two passes."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_the_same_animated_card_renders_the_same_bytes_twice(self):
        import hashlib
        from postengine.render.backgrounds import wash
        from postengine.render.renderer import _shoot_playwright

        slots = card_slots(CFG, draft(), spec(), "card/wash")
        slots.update(wash(CFG, "det", 1200, 1200,
                          {"wash_dark": True, "wash_motion": "sweep"}))
        slots["animate"] = True
        hp = os.path.join(self.tmp, "a.html")
        with open(hp, "w", encoding="utf-8") as fh:
            fh.write(build_page(CFG, "card/wash", slots, "CARD", ground="dark"))

        digests = []
        for i in range(2):
            png = os.path.join(self.tmp, "s%d.png" % i)
            _shoot_playwright([(hp, png)], 1200, 1200, {}, 24.0)
            with open(png, "rb") as fh:
                digests.append(hashlib.sha256(fh.read()).hexdigest())
        self.assertEqual(digests[0], digests[1],
                         "an animated card renders different bytes each time")


class TestStillsAreFrozen(unittest.TestCase):
    """The rule CLAUDE.md states and nothing enforced.

    `scripts/mutation_check.py` carries a mutant that resumes every animation after seeking to
    zero. It survived every run, because the freeze script was inline in the render loop and no
    test could see it. A still of an animated card would then sample whatever moment the
    screenshot landed on, and the same card would render two different files.
    """

    def test_the_freeze_script_pauses_seeks_and_never_resumes(self):
        from postengine.render.renderer import FREEZE_STILL_JS
        self.assertIn("a.pause()", FREEZE_STILL_JS)
        self.assertIn("a.currentTime = 0", FREEZE_STILL_JS)
        self.assertNotIn(".play()", FREEZE_STILL_JS,
                         "a still that resumes its animations is not reproducible")

    def test_the_frame_capture_seeks_by_index_rather_than_waiting(self):
        """The animated path has the same requirement for the same reason."""
        import inspect
        from postengine.render import animate
        src = inspect.getsource(animate._freeze_and_seek)
        self.assertIn("a.pause()", src)
        self.assertNotIn(".play()", src)
