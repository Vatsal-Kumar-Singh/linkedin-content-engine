"""Structured content → HTML/CSS → headless Chromium → PNG (+PDF for DOC).

Playwright when it is installed; the local Chrome binary otherwise. Renderer
availability is detected, never assumed — a missing browser degrades the run to
"copy only" with an explicit note, it does not crash it.
"""
from __future__ import annotations

import base64
import glob
import json
import os
import re
import shutil
import subprocess
import tempfile
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..config import Config
from .backgrounds import (accent_rgb, compose as compose_backgrounds,
                          wash as compose_wash)
from .fit import FIT_JS, evaluate as evaluate_fit, precheck
from .mobile import check as check_mobile
from .template import render as render_template, sanitize_inline


class RenderError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# renderer detection
# ---------------------------------------------------------------------------

CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
]


def _playwright_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        return False
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            return bool(p.chromium.executable_path and
                        os.path.exists(p.chromium.executable_path))
    except Exception:
        return False


def _chrome_binary() -> Optional[str]:
    for p in CHROME_PATHS:
        if os.path.exists(p):
            return p
    return shutil.which("google-chrome") or shutil.which("chromium")


def detect_renderer(preference: str = "auto") -> str:
    if preference == "none":
        return "none"
    if preference in ("playwright", "chrome"):
        return preference
    if _playwright_available():
        return "playwright"
    if _chrome_binary():
        return "chrome"
    return "none"


# ---------------------------------------------------------------------------
# page assembly
# ---------------------------------------------------------------------------


def _font_url(cfg: Config, family_key: str, weight: int) -> str:
    typo = cfg.brand["typography"]
    spec = typo[family_key]
    fname = spec["file_pattern"].replace("{w}", str(weight))
    path = os.path.join(cfg.root, typo.get("font_dir", "assets/fonts"), fname)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as fh:
        return "data:font/woff2;base64," + base64.b64encode(fh.read()).decode("ascii")


def _token_ctx(cfg: Config, fmt: str, ground: str = "dark") -> Dict[str, Any]:
    pal = cfg.brand["palette"]
    grounds = cfg.brand["grounds"][ground]
    geo = cfg.brand["formats"][fmt]
    leg = cfg.brand["legibility"]
    ts = cfg.brand.get("type_scale") or {}
    ctx: Dict[str, Any] = {k: v for k, v in pal.items()}
    for name, spec in ts.items():
        ctx["ts_%s" % name] = spec.get("size")
        ctx["ts_%s_tracking" % name] = spec.get("tracking", 0)
        ctx["ts_%s_weight" % name] = spec.get("weight", 400)
    bg = cfg.brand.get("backgrounds") or {}
    ctx.update({
        "glow_opacity": (bg.get("glow") or {}).get("opacity", 0.30),
        "glow_spread": (bg.get("glow") or {}).get("spread", 62),
        "accent_rgb": accent_rgb(cfg, ground),
    })
    ctx.update({
        "ground_bg": pal[grounds["bg"]],
        "ground_fg": pal[grounds["fg"]],
        "ground_muted": pal[grounds["muted"]],
        "ground_accent": pal[grounds["accent"]],
        "ground_structure": pal[grounds.get("structure", "silver_dark")],
        "ground_raised": pal[grounds.get("raised", "navy_raised")],
        "fallback_stack": ", ".join('"%s"' % f if " " in f else f
                                    for f in cfg.brand["typography"]["fallback_stack"]),
        "width": geo["width"], "height": geo["height"],
        "margin": 96 if fmt == "CARD" else 84,
        "min_body_px": leg["min_body_px"], "min_caption_px": leg["min_caption_px"],
        "min_body": leg["min_body_px"], "min_caption": leg["min_caption_px"],
        "font_display_300": _font_url(cfg, "display", 300),
        "font_display_400": _font_url(cfg, "display", 400),
        "font_display_600": _font_url(cfg, "display", 600),
        "font_body_300": _font_url(cfg, "body", 300),
        "font_body_400": _font_url(cfg, "body", 400),
        "font_body_500": _font_url(cfg, "body", 500),
    })
    return ctx


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def build_page(cfg: Config, template_dir: str, slots: Dict[str, Any],
               fmt: str, ground: str = "dark") -> str:
    tokens = _token_ctx(cfg, fmt, ground)
    shared = os.path.join(cfg.root, "templates", "_shared")
    css = render_template(_read(os.path.join(shared, "tokens.css")), tokens, escape=False)
    css += "\n" + render_template(_read(os.path.join(shared, "base.css")), tokens, escape=False)
    css += "\n" + render_template(_read(os.path.join(shared, "backgrounds.css")), tokens,
                                   escape=False)

    tpl_path = os.path.join(cfg.root, "templates", template_dir, "template.html")
    if not os.path.exists(tpl_path):
        raise RenderError("template not found: templates/%s/template.html" % template_dir)

    ctx = dict(tokens)
    ctx.update(slots)
    body = render_template(_read(tpl_path), ctx, partial_dir=shared)
    # Template-local <style> blocks reference the same tokens.
    body = render_template(body, ctx, escape=False, partial_dir=shared)

    return ("<!doctype html><html><head><meta charset='utf-8'>"
            "<style>%s</style></head><body>%s</body></html>" % (css, body))


# ---------------------------------------------------------------------------
# browser drivers
# ---------------------------------------------------------------------------


def _shoot_playwright(pages: List[Tuple[str, str]], width: int, height: int,
                      autofit: Dict[str, Any], floor: float) -> List[Dict[str, Any]]:
    from playwright.sync_api import sync_playwright
    out: List[Dict[str, Any]] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-color-profile=srgb",
                                          "--font-render-hinting=none"])
        page = browser.new_page(viewport={"width": width, "height": height},
                                device_scale_factor=1)
        try:
            for html_path, png_path in pages:
                page.goto("file://" + html_path, wait_until="load")
                try:
                    page.evaluate("document.fonts.ready")
                except Exception:
                    pass
                page.wait_for_timeout(150)
                # Freeze every animation at t=0 before measuring or shooting.
                # Without this a still of an ANIMATED card samples whatever
                # moment the screenshot happened to land on: rendering the same
                # card twice gave two different PNGs, and it was the design
                # critic's input and the run's stored artefact that varied. Only
                # the animated variants were affected, which is why it went
                # unnoticed — the static light cards were byte-identical.
                try:
                    page.evaluate("""() => {
                        for (const a of document.getAnimations()) {
                            a.pause();
                            a.currentTime = 0;
                        }
                    }""")
                except Exception:
                    pass
                measure = page.evaluate(FIT_JS, {
                    "ratio": float(autofit.get("step_ratio", 0.94)),
                    "maxSteps": int(autofit.get("max_steps", 6)),
                    "floor": floor, "width": width, "height": height,
                    "clipTolerance": 14,
                })
                page.screenshot(path=png_path, clip={"x": 0, "y": 0,
                                                     "width": width, "height": height})
                out.append({"png": png_path, "measure": measure})
        finally:
            browser.close()
    return out


def _shoot_chrome(pages: List[Tuple[str, str]], width: int, height: int,
                  binary: str) -> List[Dict[str, Any]]:
    """Fallback path. Chrome's CLI cannot return measurements, so the fit script
    is inlined into the page and writes its result into the title attribute,
    which we cannot read back either — so this path reports fit as unmeasured."""
    out: List[Dict[str, Any]] = []
    for html_path, png_path in pages:
        cmd = [binary, "--headless=new", "--disable-gpu", "--hide-scrollbars",
               "--force-color-profile=srgb",
               "--virtual-time-budget=3000",
               "--window-size=%d,%d" % (width, height),
               "--screenshot=%s" % png_path, "file://" + html_path]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              timeout=90)
        if not os.path.exists(png_path):
            raise RenderError("chrome failed to produce %s: %s"
                              % (png_path, proc.stderr.decode("utf-8", "replace")[:400]))
        out.append({"png": png_path,
                    "measure": {"unmeasured": True,
                                "note": "chrome CLI fallback cannot return geometry; "
                                        "install playwright for measured fit validation"}})
    return out


# ---------------------------------------------------------------------------
# slot mapping — draft fields → template slots
# ---------------------------------------------------------------------------

TAGLINE = "AI-Native · Secure by Design · Outcomes Delivered"

# A symbolic unit (%, %+, ×) rides the figure inline; a word unit sits beneath it.
_SYMBOLIC_UNIT = re.compile(r"^[%×x+°]{1,3}$")

_SPLIT_UNIT = re.compile(
    r"^\s*([\d.,%+×x–\-]+|\S{1,14})\s*(months?|days?|hours?|hrs?|weeks?|%|x|×)?\s*$",
    re.IGNORECASE)


def _focal_parts(draft) -> Tuple[str, str, str]:
    """Return (figure, inline_symbol, word_unit).

    '60%'        -> ('60', '%',  '')
    '9–14 months'-> ('9–14', '', 'months')
    'No ceiling' -> ('No ceiling', '', '')

    A symbol rides the figure inline; a word sits underneath. That is the only
    way a long unit cannot squeeze the figure off the artboard.
    """
    focal = str(getattr(draft, "focal", "") or "").strip()
    unit = str(getattr(draft, "focal_unit", "") or "").strip()
    raw = (draft.creative_headline or "").strip()
    if not focal:
        m = _SPLIT_UNIT.match(raw)
        if m and m.group(2):
            focal, unit = m.group(1), m.group(2)
        else:
            focal = raw
    # A trailing symbol already inside the figure gets split out for styling.
    m = re.match(r"^(.*?)([%×x])$", focal)
    if m and m.group(1).strip():
        return m.group(1).strip(), m.group(2), unit
    if unit and _SYMBOLIC_UNIT.match(unit):
        return focal, unit, ""
    return focal, "", unit


def _strip_cells(draft) -> List[Dict[str, str]]:
    """The context strip. Gate A2 still requires the qualifier on the creative —
    it now appears as a labelled fact rather than a bordered disclaimer, which
    drew the eye to the least interesting words on the card.

    Rendered verbatim from the fields the validator scanned. The renderer never
    invents or rewrites this text, or what ships would differ from what was
    checked."""
    cells = [{"k": (c.get("label") or "").upper(), "v": _emphasise(c.get("value") or "")}
             for c in (draft.creative_strip or []) if (c.get("value") or "").strip()]
    if not cells and (draft.creative_qualifier or "").strip():
        cells = [{"k": "NOTE", "v": _emphasise(draft.creative_qualifier)}]
    return cells[:3]


_EMPH = re.compile(r"\*([^*]{1,60})\*")


def _emphasise(text: str) -> str:
    """`*word*` becomes an accent-coloured word. Escaped first, so generated
    copy can never inject structure into the page."""
    return _EMPH.sub(r"<em>\1</em>", sanitize_inline(text or ""))


# Per-template content limits. When copy exceeds these the answer is to
# shorten the copy or change template — never to keep shrinking the type.
TEMPLATE_LIMITS: Dict[str, Dict[str, int]] = {
    "card/big_stat":    {"focal": 14, "deck": 130, "eyebrow": 26, "strip_value": 54},
    "card/comparison":  {"headline": 62, "row": 46, "eyebrow": 26},
    "card/journey":     {"headline": 60, "step": 30, "step_body": 52, "eyebrow": 26},
    "card/editorial":   {"headline": 74, "sub": 130, "eyebrow": 26},
    "card/framework":   {"headline": 60, "node": 26, "node_body": 68, "eyebrow": 26},
    "card/contrarian":  {"statement": 78, "sub": 150, "eyebrow": 26},
    "document/editorial": {"headline": 74, "copy": 200, "eyebrow": 24},
}


def _eyebrow_for(cfg: Config, draft, spec) -> str:
    """The small label above the headline.

    Reads the dedicated `eyebrows` map rather than slicing the family sentence.
    Slicing produced "THE COMMERCIAL MODEL" and "CONTINUITY AND ACCOUNTABIL" —
    the first is banned consultant language, the second is a truncation. Neither
    could be caught by a gate, because this text is composed at render time and
    never passes through the validator.
    """
    eb = (cfg.registry.get("eyebrows") or {}).get(spec.family, "")
    fam = (cfg.registry.get("families") or {}).get(spec.family, "")
    return (str(getattr(draft, "eyebrow", "") or "").strip()
            or eb
            or fam.split("—")[0].strip()
            or ("Family " + spec.family))[:26].upper()


def _wordmark_html(cfg) -> str:
    """The wordmark, with one letter in the accent colour.

    It used to be hard-coded in three templates as literal markup, which meant a
    different company could not use the design without editing HTML. Now it is a
    slot: set `wordmark` in registry.yaml and every template follows.
    """
    name = str(cfg.registry.get("wordmark") or "")
    if len(name) < 3:
        return name
    i = len(name) // 2 - 1 if len(name) > 3 else 1
    return "%s<span>%s</span>%s" % (name[:i], name[i], name[i + 1:])


def _brand_ctx(cfg: Config, draft, spec, index: int = 1) -> Dict[str, Any]:
    return {
        "eyebrow": _eyebrow_for(cfg, draft, spec),
        "index": "%02d" % index,
        "meta_label": (cfg.registry.get("meta_label") or ""),
        "brandline": (cfg.registry.get("brandline") or ""),
        "wordmark_html": _wordmark_html(cfg),
        "source_label": (draft.source_label or "").strip(),
        "tagline": TAGLINE,
        "strip": bool(_strip_cells(draft)),
        "strip_cells": _strip_cells(draft),
        "strip_gap": 46,
    }


def _wash_seed(spec) -> str:
    """What the wash geometry is derived from.

    The post id, so a card keeps its shape, colours and angle across every
    re-render in a run. Falls back to the pain point when a spec carries no id,
    which keeps previews stable too.
    """
    return str(getattr(spec, "id", "") or getattr(spec, "pain_point", "") or "x")


def card_slots(cfg: Config, draft, spec, template_dir: str) -> Dict[str, Any]:
    """Route a draft into the slots of whichever card template was selected."""
    ts = cfg.brand.get("type_scale") or {}
    geo = cfg.brand["formats"]["CARD"]
    W, H = geo["width"], geo["height"]
    slots: Dict[str, Any] = dict(_brand_ctx(cfg, draft, spec))
    slots.update({"width": W, "height": H})

    if template_dir == "card/big_stat":
        focal, symbol, unit = _focal_parts(draft)
        is_word = not re.match(r"^[\d.,%+×x–\-]+$", focal)
        # When the figure is a share, visualise it. A proportion bar reinforces
        # the focal point instead of competing with it; anything else gets a
        # system fragment so the right column is never empty.
        pct = None
        if symbol.startswith("%"):
            m = re.match(r"^(\d{1,3})", focal)
            if m and 0 < int(m.group(1)) <= 100:
                pct = int(m.group(1))
        slots.update(compose_wash(cfg, _wash_seed(spec), W, H))
        slots.update({
            "focal": focal, "focal_symbol": symbol, "focal_unit": unit.upper(),
            "focal_class": "focal--word" if is_word else "",
            "focal_size": ts.get("focal_word", {}).get("size", 190) if is_word
                          else ts.get("focal", {}).get("size", 460),
            "focal_word_size": ts.get("focal_word", {}).get("size", 190),
            "focal_size_max": ts.get("focal_word", {}).get("size", 190) if is_word
                              else ts.get("focal", {}).get("size", 460),
            "focal_size_min": 140 if is_word else 240,
            "deck_html": _emphasise(draft.creative_supporting_copy or draft.alt_text),
            "deck_size": ts.get("deck", {}).get("size", 60),
            "deck_min": 42, "deck_measure": 24,
            "stat_top": 34 if is_word else 6,
            "deck_top": 30, "data_bottom": 26,
            "proportion": pct is not None,
            "prop_pct": pct or 0, "prop_h": 430,
            "prop_label_a": (draft.prop_label_a or "Repeat work").strip()[:22],
            "prop_label_b": (draft.prop_label_b or "Everything else").strip()[:22],
            "frag_note": (draft.frag_note or "").strip()[:88],
        })
        return slots

    hl = ts.get("headline", {}).get("size", 108)

    if template_dir == "card/comparison":
        slots.update(compose_wash(cfg, _wash_seed(spec), W, H))
        left, right = _comparison_rows(draft)
        slots.update({
            "headline_html": _emphasise(draft.creative_headline or draft.creative_supporting_copy),
            "left_label": (draft.left_label or "TODAY").upper(),
            "right_label": (draft.right_label or cfg.registry.get("brandline") or "").upper(),
            "rows_left": left, "rows_right": right,
            "row_count": max(len(left), len(right)),
            "headline_size": 78, "row_size": 36 if max(len(left), len(right)) > 3 else 42,
        })
        return slots

    if template_dir == "card/journey":
        steps = _journey_steps(draft)
        slots.update(compose_wash(cfg, _wash_seed(spec), W, H))
        slots.update({
            "headline_html": _emphasise(draft.creative_headline or ""),
            "sub_html": "", "sub": "",
            "steps": steps, "step_count": len(steps),
            "headline_size": 76,
            "step_size": 42 if len(steps) > 3 else 50,
            "step_gap": 30 if len(steps) > 3 else 46,
        })
        return slots

    if template_dir == "card/editorial":
        slots.update(compose_wash(cfg, _wash_seed(spec), W, H))
        slots.update({
            "headline_html": _emphasise(draft.creative_headline or ""),
            "sub_html": _emphasise(draft.creative_supporting_copy or ""),
            "sub": draft.creative_supporting_copy or "",
            "counter": draft.counter or "",
            "headline_size": 132, "headline_measure": 13,
        })
        return slots

    if template_dir == "card/framework":
        nodes = _framework_nodes(draft)
        slots.update(compose_wash(cfg, _wash_seed(spec), W, H))
        slots.update({
            "headline_html": _emphasise(draft.creative_headline or ""),
            "sub_html": _emphasise(draft.creative_supporting_copy or ""),
            "sub": draft.creative_supporting_copy or "",
            "nodes": nodes,
            "headline_size": 74, "node_size": 37,
        })
        return slots

    if template_dir == "card/wash":
        slots.update(compose_wash(cfg, _wash_seed(spec), W, H))
        statement = draft.creative_headline or draft.creative_supporting_copy
        slots.update({
            "statement_html": _emphasise(statement),
            "sub_html": _emphasise(draft.creative_supporting_copy) if draft.creative_headline else "",
            "sub": draft.creative_supporting_copy if draft.creative_headline else "",
            "statement_size": 148, "statement_measure": 16,
        })
        return slots

    # card/contrarian — the default for a statement-led card
    slots.update(compose_wash(cfg, _wash_seed(spec), W, H))
    statement = draft.creative_headline or draft.creative_supporting_copy
    slots.update({
        "statement_html": _emphasise(statement),
        "sub_html": _emphasise(draft.creative_supporting_copy) if draft.creative_headline else "",
        "sub": draft.creative_supporting_copy if draft.creative_headline else "",
        "statement_size": 148, "statement_measure": 16, "quote_top": 204,
    })
    return slots


def _comparison_rows(draft):
    """Two-column rows. The generator supplies them; otherwise derive nothing —
    an empty comparison is a template-routing error, not something to invent."""
    rows = getattr(draft, "comparison_rows", None) or []
    left, right = [], []
    for r in rows[:5]:
        if isinstance(r, dict):
            left.append(_emphasise(r.get("old") or r.get("left") or ""))
            right.append(_emphasise(r.get("new") or r.get("right") or ""))
    return left, right


def _journey_steps(draft):
    out = []
    for i, s in enumerate(getattr(draft, "steps", None) or [], 1):
        if isinstance(s, dict):
            out.append({"n": "%02d" % i,
                        "title": (s.get("title") or "").upper(),
                        "body": s.get("body") or ""})
    return out[:4]


def _framework_nodes(draft):
    out = []
    for i, s in enumerate(getattr(draft, "steps", None) or [], 1):
        if isinstance(s, dict):
            out.append({"n": "%02d" % i,
                        "title": (s.get("title") or "").upper(),
                        "body": s.get("body") or ""})
    return out[:4]


def doc_slots(cfg: Config, draft, spec, index: int, total: int, slide) -> Dict[str, Any]:
    kind = (slide.kind or "point").lower()
    geo = cfg.brand["formats"]["DOC"]
    # The cover is pure editorial: a massive headline and nothing competing with
    # it. Context belongs on the closing slide, where the reader has arrived.
    cells = _strip_cells(draft) if kind in ("cover", "close") else []
    bg = compose_backgrounds(
        cfg, ["grid", "glow"] + (["geometry"] if kind == "cover" else []),
        geo["width"], geo["height"],
        {"glow_x": 78, "glow_y": 16, "glow_opacity": 0.22,
         "geo_cx": geo["width"] * 1.14, "geo_cy": geo["height"] * 0.30,
         "geo_r": geo["width"] * 0.44, "arc_from": 132, "arc_to": 208})
    out = dict(bg)
    out.update({
        "kind_class": "cover" if kind == "cover" else "body-slide",
        "is_cover": kind == "cover",
        "tag": (str(getattr(draft, "eyebrow", "") or spec.family))[:24],
        "index": "%02d" % index, "total": "%02d" % total,
        "step": "%02d" % index,
        "headline": slide.headline,
        "sub": draft.creative_supporting_copy if kind == "cover" else "",
        "copy": slide.body,
        "cover_size": 112, "headline_size": 82, "body_size": 34,
        "strip": bool(cells), "strip_cells": cells, "strip_gap": 40,
        "brandline": (cfg.registry.get("brandline") or ""),
        "source_label": (draft.source_label or "").strip(),
        "tagline": TAGLINE,
        "headline_html": _emphasise(slide.headline),
        "sub_html": _emphasise(draft.creative_supporting_copy if kind == "cover" else ""),
        "copy_html": _emphasise(slide.body),
    })
    return out


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------


def render_motion(cfg: Config, slots: Dict[str, Any], template_dir: str, fmt: str,
                  renderer: str, src_dir: str, store, geo: Dict[str, Any],
                  vtag: str, emit: Callable[[str], None] = lambda _s: None
                  ) -> Optional[Dict[str, Any]]:
    """Emit a looping motion asset for an already-rendered card.

    The animated page is built from the *same slots* as the still, with only
    the pulse layers switched on, so the motion cannot drift from the frame the
    critic actually approved.

    CARD only: a carousel is swiped and LinkedIn renders document posts as
    stills, so motion there is bytes nobody sees.
    """
    if fmt != "CARD":
        return {"status": "not_applicable",
                "note": "motion is for single cards; carousels are swiped, not played."}
    if renderer != "playwright":
        return {"status": "unavailable",
                "note": "frame capture needs playwright; the still PNG is unaffected."}
    try:
        from .animate import DEFAULT_FPS, animate_card
        aslots = dict(slots)
        aslots["animate"] = True
        secs = float(aslots.get("pulse_secs") or 7.0)
        ahp = os.path.join(src_dir, "creative_animated.html")
        with open(ahp, "w", encoding="utf-8") as fh:
            fh.write(build_page(cfg, template_dir, aslots, fmt))
        emit("  Rendering motion loop (%.1fs @ %dfps)..." % (secs, DEFAULT_FPS))
        motion = animate_card(ahp, store.dir, "creative%s_motion" % vtag,
                              geo["width"], geo["height"], seconds=secs)
        motion["path"] = os.path.relpath(motion["path"], store.dir)
        motion["status"] = "rendered"
        emit("  Motion: %s, %d frames, %.1f MB"
             % (motion["format"], motion["frames"], motion["bytes"] / 1e6))
        return motion
    except Exception as exc:
        # A failed animation must never sink a run whose copy and still are both
        # fine. The loop is the optional half of the deliverable.
        emit("  ! motion render failed: %s" % exc)
        return {"status": "failed", "error": str(exc)}


def render_creative(cfg: Config, result, store, emit: Callable[[str], None] = lambda _s: None,
                    draft=None, variant: int = 1,
                    animate: Optional[bool] = None) -> Dict[str, Any]:
    """Render one variant. `variant` prefixes the output files so every attempt
    in the creative loop is preserved rather than overwritten.

    `animate` additionally emits a looping GIF/MP4 of the same card. It only
    applies to CARD: a carousel is swiped, and LinkedIn renders document
    posts as stills, so motion there is wasted bytes. None reads the config.
    The still PNG is always produced — the animation is an extra asset, not
    a replacement, so nothing downstream (critic, fit checks) changes."""
    ccfg = cfg.engine.get("creative") or {}
    spec = result.spec
    draft = draft if draft is not None else result.final.draft
    vtag = "" if variant <= 1 else "_v%d" % variant

    if not ccfg.get("enabled", True):
        return {"status": "disabled"}
    if spec.template == "TEXT":
        return {"status": "not_applicable",
                "note": "TEXT posts carry no creative by design — zero design cost."}

    template_dir = cfg.template_dir(spec.template, spec.arc)
    if not template_dir:
        return {"status": "no_template",
                "note": "no template routed for %s/%s" % (spec.template, spec.arc)}

    renderer = detect_renderer(str(ccfg.get("renderer", "auto")))
    if renderer == "none":
        return {"status": "unavailable", "template": template_dir,
                "note": "no headless browser found. `python -m playwright install chromium` "
                        "or install Google Chrome. Copy pipeline is unaffected."}

    fmt = spec.template
    geo = cfg.brand["formats"][fmt]
    leg = cfg.brand["legibility"]
    src_dir = store.path(os.path.join("creative_source", "v%d" % variant))
    os.makedirs(src_dir, exist_ok=True)

    # ---- build the page(s) -------------------------------------------
    pages: List[Tuple[str, str]] = []
    slot_sets: List[Dict[str, Any]] = []
    if fmt == "CARD":
        slots = card_slots(cfg, draft, spec, template_dir)
        slot_sets.append(slots)
        html = build_page(cfg, template_dir, slots, fmt)
        hp = os.path.join(src_dir, "creative.html")
        with open(hp, "w", encoding="utf-8") as fh:
            fh.write(html)
        pages.append((hp, store.path("creative%s.png" % vtag)))
    else:
        total = len(draft.slides)
        if total == 0:
            return {"status": "no_slides",
                    "note": "DOC template routed but the draft carries no slides"}
        for i, slide in enumerate(draft.slides, 1):
            slots = doc_slots(cfg, draft, spec, i, total, slide)
            slot_sets.append(slots)
            html = build_page(cfg, template_dir, slots, fmt)
            hp = os.path.join(src_dir, "slide_%02d.html" % i)
            with open(hp, "w", encoding="utf-8") as fh:
                fh.write(html)
            pages.append((hp, store.path("slide%s_%02d.png" % (vtag, i))))

    # ---- cheap pre-render budget check --------------------------------
    pre: List[str] = []
    for s in slot_sets:
        pre.extend(precheck(s))
    if pre:
        emit("  Creative pre-check: %d slot problem(s)" % len(pre))

    # ---- shoot --------------------------------------------------------
    emit("  Rendering creative (%s, %s, %dx%d)..."
         % (template_dir, renderer, geo["width"], geo["height"]))
    if renderer == "playwright":
        shots = _shoot_playwright(pages, geo["width"], geo["height"],
                                  ccfg.get("autofit") or {},
                                  float(leg["min_caption_px"]))
    else:
        shots = _shoot_chrome(pages, geo["width"], geo["height"], _chrome_binary())

    # ---- animated variant ---------------------------------------------
    motion = None
    want_motion = ccfg.get("animate", False) if animate is None else animate
    if want_motion:
        motion = render_motion(cfg, slot_sets[0], template_dir, fmt, renderer,
                               src_dir, store, geo, vtag, emit)

    # ---- measured fit validation --------------------------------------
    fit_problems: List[str] = list(pre)
    for i, s in enumerate(shots, 1):
        m = s.get("measure") or {}
        if m.get("unmeasured"):
            continue
        for p in evaluate_fit(m, float(leg["min_body_px"]), float(leg["min_caption_px"]),
                              bool(ccfg.get("fail_on_overflow", True))):
            fit_problems.append("page %d: %s" % (i, p))
        # Only a card, or a carousel cover, has to stop a scroll unaided.
        for p in check_mobile(m, geo["height"],
                              int(leg.get("mobile_reference_width", 430)), geo["width"],
                              require_focal=(fmt == "CARD" or i == 1)):
            fit_problems.append("page %d (mobile): %s" % (i, p))

    files = [os.path.relpath(s["png"], store.dir) for s in shots]

    # ---- PDF for carousels --------------------------------------------
    pdf = None
    if fmt == "DOC" and renderer == "playwright":
        try:
            pdf = _pdf_from_pngs([s["png"] for s in shots], store.path("carousel%s.pdf" % vtag),
                                 geo["width"], geo["height"])
            if pdf:
                files.append(os.path.relpath(pdf, store.dir))
        except Exception as exc:
            emit("  ! PDF assembly failed: %s" % exc)

    out: Dict[str, Any] = {
        "status": "rendered" if not fit_problems else "rendered_with_problems",
        "variant": variant,
        "renderer": renderer,
        "template": template_dir,
        "dimensions": "%dx%d" % (geo["width"], geo["height"]),
        "files": files,
        "fit_problems": fit_problems,
        "measurements": [s.get("measure") for s in shots],
        "brand_status": cfg.brand.get("status"),
        # Private, and popped by the caller before the report is written. The
        # motion pass reuses the accepted card's exact slots so the loop cannot
        # drift from the still; recomputing them there would risk exactly that.
        "_slots": slot_sets[0],
    }
    if motion:
        out["motion"] = motion
        if motion.get("path"):
            out["files"].append(motion["path"])
    if fit_problems:
        emit("  ! fit problems: %s" % fit_problems[0])
    else:
        emit("  Creative fit: OK (measured, smallest text %s px)"
             % (shots[0].get("measure") or {}).get("smallest_text_px"))

    # ---- design critic -------------------------------------------------
    if ccfg.get("design_critic_enabled", True):
        from ..agents.design_critic import critique
        out["design_critique"] = critique(cfg, [s["png"] for s in shots],
                                          [s.get("measure") or {} for s in shots],
                                          draft, emit=emit, fmt=fmt, template=template_dir)
    return out


def _pdf_from_pngs(pngs: List[str], out_path: str, width: int, height: int) -> Optional[str]:
    """One slide per page, no margins — how LinkedIn wants a document post."""
    from playwright.sync_api import sync_playwright
    imgs = []
    for p in pngs:
        with open(p, "rb") as fh:
            imgs.append("data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii"))
    html = ("<!doctype html><html><head><style>"
            "@page{size:%dpx %dpx;margin:0}html,body{margin:0;padding:0}"
            "img{display:block;width:%dpx;height:%dpx;page-break-after:always}"
            "img:last-child{page-break-after:auto}</style></head><body>%s</body></html>"
            % (width, height, width, height,
               "".join('<img src="%s">' % s for s in imgs)))
    tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8")
    tmp.write(html)
    tmp.close()
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        page.goto("file://" + tmp.name, wait_until="load")
        page.pdf(path=out_path, width="%dpx" % width, height="%dpx" % height,
                 print_background=True, margin={"top": "0", "bottom": "0",
                                                "left": "0", "right": "0"})
        b.close()
    os.unlink(tmp.name)
    return out_path if os.path.exists(out_path) else None
