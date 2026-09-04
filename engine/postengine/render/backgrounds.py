"""Procedural background layers.

Every parameter comes from `config/brand.yaml -> backgrounds`. Templates
declare which layers they want; this module computes the geometry. Keeping the
maths here means a template stays a layout, not a pile of hand-tuned SVG.
"""
from __future__ import annotations

import math
import re
import random
from typing import Any, Dict, List, Optional


def _hex_to_rgb(h: str) -> str:
    h = h.lstrip("#")
    return "%d,%d,%d" % (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def compose(cfg, layers: List[str], width: int, height: int,
            options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return the template context for the requested background layers."""
    b = cfg.brand.get("backgrounds") or {}
    o = options or {}
    ctx: Dict[str, Any] = {
        "width": width, "height": height,
        "bg_grid": False, "bg_dots": False, "bg_glow": False,
        "bg_geometry": False, "bg_linework": False, "bg_flow": False,
        # Motion is opt-in. A static PNG must render identically every
        # time; a running animation would sample a random frame.
        "animate": False,
        "bg_network": False,
    }

    if "grid" in layers:
        g = b.get("grid", {})
        ctx.update(bg_grid=True, grid_size=g.get("size", 48),
                   grid_opacity=g.get("opacity", 0.055))

    if "dots" in layers:
        d = b.get("dot_grid", {})
        ctx.update(bg_dots=True, dot_size=d.get("size", 34),
                   dot_radius=d.get("radius", 1.4),
                   dot_opacity=d.get("opacity", 0.085))

    if "glow" in layers:
        g = b.get("glow", {})
        ctx.update(bg_glow=True,
                   glow_opacity=o.get("glow_opacity", g.get("opacity", 0.30)),
                   glow_spread=g.get("spread", 62),
                   glow_x=o.get("glow_x", 76), glow_y=o.get("glow_y", 14))

    if "geometry" in layers:
        g = b.get("geometry", {})
        # Concentric rings whose centre sits OUTSIDE the canvas, so the arcs
        # bleed off two edges. The composition then reads as a fragment of
        # something larger rather than an object floating in a rectangle.
        cx = o.get("geo_cx", width * 1.06)
        cy = o.get("geo_cy", height * 0.80)
        r = o.get("geo_r", width * 0.46)
        ctx.update(bg_geometry=True,
                   geometry_opacity=g.get("opacity", 0.16),
                   geo_cx=round(cx, 1), geo_cy=round(cy, 1),
                   geo_r=round(r, 1), geo_r2=round(r * 0.70, 1),
                   geo_r3=round(r * 1.34, 1),
                   geo_arc=_arc(cx, cy, r, o.get("arc_from", 172),
                                o.get("arc_to", 232)),
                   geo_dot_x=round(cx + r * math.cos(math.radians(o.get("arc_to", 232))), 1),
                   geo_dot_y=round(cy + r * math.sin(math.radians(o.get("arc_to", 232))), 1),
                   **_pulse(cx, cy, r, width, height, g, o))

    if "linework" in layers:
        lw = b.get("linework", {})
        m = o.get("mark_inset", 46)
        arm = o.get("mark_arm", 42)
        ctx.update(bg_linework=True,
                   linework_opacity=lw.get("opacity", 0.20),
                   tick_opacity=lw.get("opacity", 0.20) * 0.9,
                   m=m, m_t=m + arm, m_x=m + arm,
                   m_r=width - m - arm, m_rr=width - m,
                   m_b=height - m - arm, m_bb=height - m,
                   ticks=_ticks(width, height, m, o))

    if "flow" in layers:
        f = b.get("flow", {})
        ctx.update(bg_flow=True,
                   flow_opacity=f.get("opacity", 0.30),
                   flow_path=o.get("flow_path") or _flow(width, height, 0),
                   flow_path_2=o.get("flow_path_2") or _flow(width, height, 1))

    if "network" in layers:
        n = b.get("network", {})
        nodes, edges = _network(width, height, o)
        ctx.update(bg_network=True,
                   network_opacity=n.get("opacity", 0.22),
                   network_node_opacity=min(1.0, n.get("opacity", 0.22) * 2.4),
                   net_nodes=nodes, net_edges=edges)

    return ctx


# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# WASH + PENCIL — the light creative direction.
#
# Every number below was measured off the reference rather than chosen:
#   · 9 strokes, 2.55% ink coverage, mean darkening 50 against the ground
#   · colour poles at saturation 29-41%, value 89-100% — a tint, never a fill
#   · a visible knot the curves pass through, fanning wider on one side
#
# The reference's two poles are 89 degrees apart in hue (blue 199, magenta 288).
# The brand palette cannot reach that: tinting each colour into the band above
# and reading it back, only ai_cyan and brand_blue survive — deep_navy lands at
# 8-11% saturation and silver_mid at 4%, which is grey, not pale. So the wash
# runs cyan against blue, 11 degrees apart, and gets its life from value rather
# than hue. signal_green is the only real hue contrast in the palette and
# carries a 10% area cap, so it is never a full-bleed pole.
# ---------------------------------------------------------------------------

WASH_POLES = [("ai_cyan", "brand_blue"), ("brand_blue", "ai_cyan")]


def _tint(hexcol: str, amount: float) -> str:
    """Mix toward white. 0 leaves the colour alone, 1 is white."""
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(
        int(round(c + (255 - c) * amount)) for c in (r, g, b))


def _pencil_paths(fx: float, fy: float, w: float, h: float, n: int = 9,
                  rot_deg: float = 0.0, spread_out: float = 62.0,
                  spread_in: float = 30.0, knot_deg: float = 13.0,
                  tang: float = 0.30, ease: float = 0.45,
                  reach: float = 1.25) -> List[str]:
    """A pencil of open curves passing exactly through one knot.

    Each curve is two cubics meeting at the focus, because placing both
    endpoints and hoping the curve passes near it does not work: with different
    spreads on the two sides the vertical components never cancel and the
    extreme curves miss by ~150px, which dissolves the knot into a set of
    parallel S-curves. Meeting at the focus makes passage structural, and the
    shared tangent through it keeps the join invisible.
    """
    F = (fx * w, fy * h)
    L = reach * max(w, h)
    rot = math.radians(rot_deg)

    def rotate(pt):
        dx, dy = pt[0] - F[0], pt[1] - F[1]
        return (F[0] + dx * math.cos(rot) - dy * math.sin(rot),
                F[1] + dx * math.sin(rot) + dy * math.cos(rot))

    def at(deg, dist):
        a = math.radians(deg)
        return (F[0] + math.cos(a) * dist, F[1] + math.sin(a) * dist)

    def lerp(a, b, k):
        return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)

    out: List[str] = []
    for i in range(n):
        frac = (i / (n - 1.0)) - 0.5
        tau = frac * knot_deg                       # tangent at the knot
        p0 = at(180 + frac * spread_in, L)
        p3 = at(frac * spread_out, L)
        c2a = at(180 + tau, L * tang)
        c1b = at(tau, L * tang)
        c1a = lerp(p0, F, ease)
        c2b = lerp(p3, F, ease)
        p0, c1a, c2a, Fr, c1b, c2b, p3 = map(
            rotate, (p0, c1a, c2a, F, c1b, c2b, p3))
        out.append(
            "M%.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f C%.1f %.1f %.1f %.1f %.1f %.1f"
            % (p0[0], p0[1], c1a[0], c1a[1], c2a[0], c2a[1], Fr[0], Fr[1],
               c1b[0], c1b[1], c2b[0], c2b[1], p3[0], p3[1]))
    return out



# ---------------------------------------------------------------------------
# THE OPEN-SHAPE FAMILY
#
# Five motifs, one grammar. Every one is: thin open strokes (never a closed
# outline, never a fill), bleeding past the frame so the card reads as a crop of
# something larger, placed off-centre and rotated. They differ in what the eye
# is asked to follow — a crossing, a nesting, a weave, a winding, an
# interference — which is enough variety to keep 84 posts from looking stamped
# without inventing a second visual language.
# ---------------------------------------------------------------------------


def _rot_fn(F, rot_deg):
    rot = math.radians(rot_deg)
    cos_r, sin_r = math.cos(rot), math.sin(rot)

    def rotate(pt):
        dx, dy = pt[0] - F[0], pt[1] - F[1]
        return (F[0] + dx * cos_r - dy * sin_r, F[1] + dx * sin_r + dy * cos_r)
    return rotate


def _path(points: List[Any], closed: bool = False) -> str:
    """A smooth open path through points, via Catmull-Rom converted to cubics.

    Sampling a curve and joining the samples with straight segments is visible
    at hairline weights — the polygon shows. Converting to cubics keeps the
    stroke genuinely curved at any zoom.
    """
    if len(points) < 2:
        return ""
    d = "M%.1f %.1f" % points[0]
    for i in range(len(points) - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1, p2 = points[i], points[i + 1]
        p3 = points[i + 2] if i + 2 < len(points) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d += " C%.1f %.1f %.1f %.1f %.1f %.1f" % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    return d


def _shape_contour(F, w, h, rnd, rot_deg):
    """Nested open arcs, like elevation lines round a peak that is off-frame.

    Each ring is perturbed by its own slow wobble rather than being a true
    circle — concentric circles read as a target, which is a different and much
    more corporate idea.
    """
    rotate = _rot_fn(F, rot_deg)
    n = rnd.randint(7, 10)
    base = max(w, h) * rnd.uniform(0.16, 0.24)
    step = max(w, h) * rnd.uniform(0.055, 0.085)
    wob = rnd.uniform(0.05, 0.11)
    phase = rnd.uniform(0, 6.28)
    # Spans of 210-320 degrees drew near-complete rings, and a set of concentric
    # rings is a bullseye — a closed figure with a centre, which is the opposite
    # of an open shape. Arcs of 110-190 degrees stay open, and drifting each
    # one's start angle stops them nesting tidily.
    a_drift = rnd.uniform(-26, 26)
    out = []
    for i in range(n):
        r = base + step * i
        a0 = rnd.uniform(-40, 30) + a_drift * i
        span = rnd.uniform(110, 190)
        pts = []
        for k in range(45):
            t = a0 + span * k / 44.0
            a = math.radians(t)
            rr = r * (1 + wob * math.sin(a * 2.0 + phase + i * 0.35))
            pts.append(rotate((F[0] + math.cos(a) * rr, F[1] + math.sin(a) * rr)))
        out.append(_path(pts))
    return out


def _shape_braid(F, w, h, rnd, rot_deg):
    """Strands weaving around a common axis, crossing repeatedly.

    Phase offsets rather than a shared envelope: strands that swell together
    read as a ribbon, which closes the shape. Crossing is the point.
    """
    rotate = _rot_fn(F, rot_deg)
    n = rnd.randint(4, 6)
    L = max(w, h) * 1.5
    amp = max(w, h) * rnd.uniform(0.07, 0.13)
    # Under about 1.6 cycles the strands cross once or twice and read as a
    # weave; above it they wrap repeatedly and the figure becomes a double
    # helix, which is a science-stock cliche and not what this is for. The
    # envelope taper also stops it looking like a uniform rope.
    cycles = rnd.uniform(0.9, 1.55)
    taper = rnd.uniform(0.35, 0.7)
    out = []
    for i in range(n):
        ph = 6.28 * i / float(n)
        drift = (i - (n - 1) / 2.0) * max(w, h) * 0.012
        pts = []
        for k in range(70):
            t = k / 69.0
            x = F[0] - L / 2 + L * t
            env = 1.0 - taper * abs(2 * t - 1) ** 1.6
            y = F[1] + drift + amp * env * math.sin(6.28 * cycles * t + ph)
            pts.append(rotate((x, y)))
        out.append(_path(pts))
    return out


def _shape_spiral(F, w, h, rnd, rot_deg):
    """One winding open spiral, sometimes doubled.

    Archimedean, so the gap between turns stays even — a logarithmic spiral
    accelerates and reads as a shell or a galaxy, which is decoration with a
    subject of its own.
    """
    rotate = _rot_fn(F, rot_deg)
    # Two or three arms as the norm. A single thin spiral disappeared once the
    # per-stroke depth variation started thinning strokes — one stroke has
    # nothing to be varied against, so it simply got fainter.
    arms = rnd.choice([2, 2, 3])
    turns = rnd.uniform(2.4, 3.6)
    # Sized so the OUTERMOST turn lands near the frame edge. At the previous
    # rate the spiral reached ~2200px on a 1200px card, so everything after the
    # first turn was off-frame and the motif read as a single stray arc.
    growth = (max(w, h) * rnd.uniform(0.42, 0.58)) / (6.283 * turns)
    out = []
    for arm in range(arms):
        off = 6.28 * arm / float(arms)
        pts = []
        steps = int(90 * turns)
        for k in range(steps):
            a = 6.28 * turns * k / float(steps - 1)
            r = growth * a
            pts.append(rotate((F[0] + math.cos(a + off) * r,
                               F[1] + math.sin(a + off) * r)))
        out.append(_path(pts))
    return out


def _shape_moire(F, w, h, rnd, rot_deg):
    """Two families of near-parallel curves crossing at a shallow angle.

    The interference between them is the subject, so the crossing angle stays
    small — past about 15 degrees they stop interfering and read as a grid.
    """
    rotate = _rot_fn(F, rot_deg)
    L = max(w, h) * 1.6
    out = []
    for fam, tilt in ((0, 0.0), (1, rnd.uniform(5.0, 13.0))):
        n = rnd.randint(9, 13)
        gap = max(w, h) * rnd.uniform(0.055, 0.08)
        bow = max(w, h) * rnd.uniform(0.05, 0.10) * (1 if fam == 0 else -1)
        for i in range(n):
            off = (i - (n - 1) / 2.0) * gap
            pts = []
            for k in range(40):
                t = k / 39.0
                x = -L / 2 + L * t
                y = off + bow * math.sin(math.pi * t)
                a = math.radians(tilt)
                pts.append(rotate((F[0] + x * math.cos(a) - y * math.sin(a),
                                   F[1] + x * math.sin(a) + y * math.cos(a))))
            out.append(_path(pts))
    return out



def _shape_deflect(F, w, h, rnd, rot_deg):
    """Streamlines bending around an object that is not drawn.

    Distinct from the other motifs because most of the figure is calm: the
    disturbance is local, and the eye goes to the thing causing it, which is
    absent. The others all put their event in the middle of a busy field.
    """
    rotate = _rot_fn(F, rot_deg)
    n = rnd.randint(10, 14)
    L = max(w, h) * 1.55
    gap = max(w, h) * rnd.uniform(0.048, 0.07)
    radius = max(w, h) * rnd.uniform(0.16, 0.24)
    out = []
    for i in range(n):
        off = (i - (n - 1) / 2.0) * gap
        pts = []
        for k in range(64):
            t = k / 63.0
            x = -L / 2 + L * t
            # Displacement falls off with distance from the axis and with
            # distance along it, so lines far out stay straight.
            d = math.hypot(x, off) / radius
            push = math.exp(-d * d * 0.9) * radius * 0.62
            sign = 1.0 if off >= 0 else -1.0
            pts.append(rotate((F[0] + x, F[1] + off + push * sign)))
        out.append(_path(pts))
    return out


def _shape_ripple(F, w, h, rnd, rot_deg):
    """Wavefronts travelling out from a source off the frame.

    Not circles: each front carries a wave along its own length, so they read as
    something propagating rather than as rings sitting still. That is what keeps
    it apart from contour.
    """
    rotate = _rot_fn(F, rot_deg)
    n = rnd.randint(8, 12)
    base = max(w, h) * rnd.uniform(0.18, 0.28)
    step = max(w, h) * rnd.uniform(0.06, 0.09)
    amp = rnd.uniform(0.035, 0.075)
    freq = rnd.uniform(2.5, 4.5)
    span = rnd.uniform(90, 150)
    a0 = rnd.uniform(-60, 20)
    out = []
    for i in range(n):
        r = base + step * i
        pts = []
        for k in range(46):
            t = k / 45.0
            a = math.radians(a0 + span * t)
            rr = r * (1 + amp * math.sin(freq * math.pi * t + i * 0.8))
            pts.append(rotate((F[0] + math.cos(a) * rr, F[1] + math.sin(a) * rr)))
        out.append(_path(pts))
    return out


def _shape_pencil(F, w, h, rnd, rot_deg):
    """The original: curves spreading either side of one tight knot."""
    spread = rnd.uniform(52, 74)
    return _pencil_paths(
        F[0] / float(w), F[1] / float(h), w, h, n=9, rot_deg=rot_deg,
        spread_out=spread, spread_in=spread * rnd.uniform(0.34, 0.52),
        knot_deg=rnd.uniform(8, 18))


SHAPES = {
    "pencil": _shape_pencil,
    "deflect": _shape_deflect,
    "ripple": _shape_ripple,
    "contour": _shape_contour,
    "braid": _shape_braid,
    "spiral": _shape_spiral,
    "moire": _shape_moire,
}


def _shade(hexcol: str, amount: float) -> str:
    """Mix toward black. The dark colourway's mirror of _tint."""
    h = hexcol.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % tuple(int(round(c * (1 - amount))) for c in (r, g, b))


def _accent_on(paths: List[str]) -> Optional[Any]:
    """A point that actually sits on the figure.

    The construction focus is the wrong place for contour, ripple and moire:
    those are built AROUND a centre the strokes never touch, so an accent there
    floats in empty space and reads as a stray dot. Taking a coordinate off the
    middle stroke puts the accent on the figure for every motif, without each
    one having to declare its own.
    """
    if not paths:
        return None
    d = paths[len(paths) // 2]
    nums = re.findall(r"-?\d+\.?\d*", d)
    if len(nums) < 2:
        return None
    # Coordinates come in pairs; take the pair nearest the middle of the path.
    pairs = [(float(nums[i]), float(nums[i + 1])) for i in range(0, len(nums) - 1, 2)]
    return pairs[len(pairs) // 2]


def _dress(paths: List[str], rnd, base_w: float, dark: bool) -> List[Dict[str, Any]]:
    """Give each stroke its own weight and opacity.

    Pass 1 drew every stroke in a bundle identically, which is why the figures
    read as flat diagrams rather than as something with depth. Varying the two
    together — a thinner stroke is also a fainter one — is how distance reads
    to the eye, and it is the difference between a bundle of wires and a form.

    The variation is smooth across the bundle rather than random per stroke:
    noise makes it look like a rendering fault, a gradient makes it look lit.
    """
    out: List[Dict[str, Any]] = []
    n = max(1, len(paths))
    phase = rnd.uniform(0, 6.283)
    depth = rnd.uniform(0.30, 0.55)
    for i, d in enumerate(paths):
        t = i / float(n) if n > 1 else 0.5
        lift = 0.5 + 0.5 * math.sin(6.283 * t + phase)      # 0..1 across the bundle
        w = base_w * (1.0 - depth * 0.55 * (1 - lift))
        o = 1.0 - depth * (1 - lift)
        out.append({"d": d,
                    "sw": round(max(0.55, w), 2),
                    "so": round(max(0.22, o), 3)})
    return out


def wash(cfg, seed: str, width: int, height: int,
         o: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """One deterministic wash-and-pencil variant.

    Seeded by the post id, never by the clock: the gauntlet re-renders a post
    several times across a run and every render has to be the same image, so
    "random" here means "fixed by which post this is".
    """
    o = o or {}
    pal = cfg.brand["palette"]
    rnd = random.Random("wash:" + str(seed))

    a_name, b_name = rnd.choice(WASH_POLES)
    dark = bool((o or {}).get("wash_dark"))

    if dark:
        # The light version runs its poles pale against a white core. On navy
        # that inverts: the poles are the brand colours pushed DOWN toward the
        # ground, and the core is the ground itself rather than white. Reusing
        # the light tints on navy produced pastel smears floating on a dark
        # card — the two colourways need opposite operations, not one with a
        # swapped background.
        pole_a = _shade(pal[a_name], rnd.uniform(0.52, 0.64))
        pole_b = _shade(pal[b_name], rnd.uniform(0.62, 0.74))
        core = pal["deep_navy"]
    else:
        # 0.54-0.62 is the tint window that lands inside the reference's
        # measured saturation band. Outside it the colour either shouts or
        # disappears.
        pole_a = _tint(pal[a_name], rnd.uniform(0.54, 0.62))
        pole_b = _tint(pal[b_name], rnd.uniform(0.54, 0.62))
        core = "#FFFFFF"

    ang = rnd.choice([18, 32, 48, 132, 148, 205, 218, 232, 322, 338])
    a = math.radians(ang)
    cx, cy = width / 2.0, height / 2.0
    r = max(width, height) * 0.72

    # The type column is left-aligned and runs the height of the card, so the
    # knot is biased right. Placing it under the words was legible in isolation
    # and not once real copy went on top.
    fx = o.get("wash_fx", rnd.uniform(0.56, 0.86))
    fy = o.get("wash_fy", rnd.choice([rnd.uniform(0.13, 0.29),
                                      rnd.uniform(0.66, 0.86)]))
    # Which motif this post gets. Seeded, so a post keeps its shape across
    # re-renders — the family varies across the calendar, never within a post.
    shape_name = o.get("wash_shape") or rnd.choice(sorted(SHAPES))
    _shape_paths = SHAPES[shape_name]((fx * width, fy * height), width, height,
                                      rnd, rnd.uniform(0, 360))
    _accent = _accent_on(_shape_paths) or (fx * width, fy * height)

    return {
        "bg_wash": True,
        "wash_a": pole_a, "wash_b": pole_b, "wash_core": core,
        "wash_dark": dark,
        "wash_motion": (o or {}).get("wash_motion", "sweep"),
        # The ground rect is oversized and centred so the drift rotation never
        # swings a corner into frame.
        "wash_over_w": round(max(width, height) * 1.62, 1),
        "wash_over_x": round((width - max(width, height) * 1.62) / 2.0, 1),
        "wash_over_y": round((height - max(width, height) * 1.62) / 2.0, 1),
        # Ink is the brand colour at full strength. The measured reference
        # darkens its ground by ~50 on average; a tinted stroke managed 16 and
        # read as a smudge. The wash is what gets tinted, never the line.
        "wash_ink_a": pal[a_name] if not dark else _tint(pal[a_name], 0.30),
        "wash_ink_mid": _tint(pal["brand_blue"], 0.18) if not dark else pal["silver"],
        "wash_ink_b": pal[b_name] if not dark else _tint(pal[b_name], 0.30),
        "wash_x1": round(cx - math.cos(a) * r, 1),
        "wash_y1": round(cy - math.sin(a) * r, 1),
        "wash_x2": round(cx + math.cos(a) * r, 1),
        "wash_y2": round(cy + math.sin(a) * r, 1),
        "wash_shape": shape_name,
        "wash_paths": _dress(_shape_paths, rnd, o.get("wash_stroke", 1.4), dark),
        # A single accent at the figure's focus. The old geometry layer carried
        # one and retiring it left the compositions without a point of rest —
        # every figure was all travel and no arrival.
        "wash_dot_x": round(_accent[0], 1),
        "wash_dot_y": round(_accent[1], 1),
        "wash_dot_r": 7,
        # The travelling highlight. On navy it is lighter than the strokes; on
        # the pale wash a lighter highlight is invisible, so there it is the
        # brand colour at full strength and the base strokes are the ones held
        # back. Same mechanism, opposite contrast direction.
        "wash_hi": pal["silver_light"] if dark else pal["brand_blue"],
        "wash_hi_w": round(o.get("wash_stroke", 1.4) * (2.1 if dark else 2.4), 2),
        "wash_stroke": o.get("wash_stroke", 1.4),
        "wash_opacity": o.get("wash_opacity", 0.85 if not dark else 0.72),
    }


def _visible_arc(cx: float, cy: float, r: float, w: float, h: float):
    """The longest run of a circle that actually falls inside the frame.

    The geometry is deliberately cropped — centres sit off-canvas so the card
    reads as a fragment of something larger. That is right for a still and
    wrong for motion: a highlight travelling the full circumference spends most
    of the loop outside the frame, so the card looks static for seconds at a
    time. Confining the sweep to the visible run is what turns the effect from
    an intermittent flicker into a continuous shimmer.

    Returns (theta_start, theta_end) in radians measured the way SVG draws a
    circle: 0 at (cx+r, cy), increasing clockwise. None when the circle never
    enters the frame.
    """
    steps = 720
    inside = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        x = cx + r * math.cos(t)
        y = cy + r * math.sin(t)
        inside.append(0 <= x <= w and 0 <= y <= h)
    if not any(inside):
        return None
    if all(inside):
        return (0.0, 2 * math.pi)

    # Rotate so the scan starts on a gap; the visible run is then contiguous
    # and does not need wrap-around handling.
    start = next(i for i in range(steps) if inside[i] and not inside[i - 1])
    length = 0
    while length < steps and inside[(start + length) % steps]:
        length += 1
    return (2 * math.pi * start / steps,
            2 * math.pi * (start + length) / steps)


def _pulse(cx: float, cy: float, r: float, w: float, h: float,
           g: Dict[str, Any], o: Dict[str, Any]) -> Dict[str, Any]:
    """Dash geometry for the travelling silver comet on each tracing.

    Each ring carries three stacked dashes rather than one, because a single
    hairline stroke reads as a rendering artefact rather than as light:

      halo    a wide, blurred, dim dash — the glow the streak sits in
      streak  the visible silver tail
      head    a near-zero-length dash with a round linecap, which renders as a
              dot, parked at the leading edge of the streak

    The head is the accent dot from the static card, taken off its fixed
    position on the arc and put on the front of the sweep. It rides the same
    dashoffset animation as the streak, offset by exactly the streak's own
    length, so the two cannot drift apart — no second animation to keep in
    sync, and no motion-path maths.

    Two things make that actually hold, and both were bugs before they were
    rules:

    Every layer's dash pattern must sum to exactly one circumference. Gaps were
    originally the full circumference, which gave the streak a period of
    `length + C` and the head a period of `C` — so they wrapped at different
    points and the head drifted a full streak-length off the front by the end
    of the sweep.

    Each ring is rotated so the path's start point — where a dash straddling it
    is drawn as two pieces — sits opposite the visible arc. The contrarian
    card's outer ring starts at (384, 240), inside the frame and directly under
    the sweep, so the streak visibly tore in half as it crossed.
    """
    out: Dict[str, Any] = {
        "pulse_secs": g.get("pulse_secs", 6.0),
        # Peak brightness as a token. The first pass ran at 0.55/0.28 and went
        # unnoticed in the feed — on a navy card, silver at half opacity behind
        # a 148px headline is simply not competing. Turn it up until it looks
        # wrong, then come back one notch.
        "pulse_peak": g.get("pulse_peak", 0.92),
        "pulse_peak2": g.get("pulse_peak2", 0.55),
        # Long enough to read as a streak of light. A short dash reads as a tick
        # mark sliding along a line, which looks like a progress indicator.
        "pulse_len": o.get("pulse_len", 340),
        "pulse_len2": o.get("pulse_len2", 250),
        "pulse_head_r": o.get("pulse_head_r", 7),
        "pulse_head_r2": o.get("pulse_head_r2", 5),
    }
    # A dash this short renders as nothing but its own round linecap: a dot.
    head_dash = 0.01

    # The tracings pass under the type — on a card whose headline fills the
    # middle third, every ring does. Left alone the comet is hard-chopped by the
    # letterforms and its glow smears around them, which reads as a rendering
    # fault rather than as light behind glass. This band tells the comet where
    # the words are so it can dim through them instead. Fractions of height, so
    # a template overrides it only if its content sits somewhere unusual.
    # Gradient stop offsets are always 0-1 fractions of the gradient vector,
    # never user-space pixels, so these stay fractional.
    out["pulse_mask_y0"] = round(o.get("pulse_mask_from", 0.19), 3)
    out["pulse_mask_y1"] = round(o.get("pulse_mask_to", 0.30), 3)
    out["pulse_mask_y2"] = round(o.get("pulse_mask_from2", 0.62), 3)
    out["pulse_mask_y3"] = round(o.get("pulse_mask_to2", 0.73), 3)
    # How far the comet dims behind type. Not to zero: a highlight that vanishes
    # entirely looks like a bug, and a faint one behind glass looks deliberate.
    out["pulse_mask_dim"] = o.get("pulse_mask_dim", 0.26)

    for suffix, radius, dash in (("", r, out["pulse_len"]),
                                 ("2", r * 0.70, out["pulse_len2"])):
        circ = 2 * math.pi * radius
        arc = _visible_arc(cx, cy, radius, w, h)
        if arc is None:
            # Off-frame entirely: park the dash and let it sit at zero opacity
            # rather than emitting an animation that can never be seen.
            rotation, a0, a1 = 0.0, 0.0, 0.0
        else:
            span = min(arc[1] - arc[0], 2 * math.pi)
            # Put the seam diametrically opposite the middle of the visible run.
            # In the rotated frame the visible arc then sits centred on pi, as
            # far from the seam as the geometry allows.
            rotation = math.degrees((arc[0] + arc[1]) / 2 + math.pi)
            a0, a1 = math.pi - span / 2, math.pi + span / 2

        s0 = radius * a0 - dash          # enters just before the frame edge
        s1 = radius * a1 + dash          # and clears it on the way out

        out["geo_c" + suffix] = round(circ, 1)
        out["pulse_rot" + suffix] = round(rotation, 2)
        # Patterns that tile the circle exactly once, so every layer shares one
        # period and no layer can drift against another.
        out["pulse_gap" + suffix] = round(max(circ - dash, 1.0), 1)
        out["head_gap" + suffix] = round(circ - head_dash, 1)
        # Negative dashoffset advances the dash along the path.
        out["pulse_from" + suffix] = round(-s0, 1)
        out["pulse_to" + suffix] = round(-s1, 1)
        # The head sits one streak-length further along the same path.
        out["head_from" + suffix] = round(-(s0 + dash), 1)
        out["head_to" + suffix] = round(-(s1 + dash), 1)
    return out


def _arc(cx: float, cy: float, r: float, a0: float, a1: float) -> str:
    x0 = cx + r * math.cos(math.radians(a0))
    y0 = cy + r * math.sin(math.radians(a0))
    x1 = cx + r * math.cos(math.radians(a1))
    y1 = cy + r * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    return "M%.1f %.1f A%.1f %.1f 0 %d 1 %.1f %.1f" % (x0, y0, r, r, large, x1, y1)


def _ticks(width: int, height: int, m: int, o: Dict[str, Any]) -> List[str]:
    """A measured tick rail down one edge. Reads as an engineering drawing."""
    out: List[str] = []
    top = o.get("tick_top", int(height * 0.30))
    bottom = o.get("tick_bottom", int(height * 0.72))
    step = o.get("tick_step", 26)
    x = o.get("tick_x", m)
    i = 0
    y = top
    while y <= bottom:
        length = 16 if i % 4 == 0 else 8
        out.append("M%d %d L%d %d" % (x, y, x + length, y))
        y += step
        i += 1
    return out


def _flow(width: int, height: int, variant: int) -> str:
    """A single long curve crossing the canvas. Transformation, not decoration."""
    if variant == 0:
        return ("M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f S %.0f %.0f, %.0f %.0f"
                % (-40, height * 0.74,
                   width * 0.22, height * 0.74,
                   width * 0.30, height * 0.40,
                   width * 0.55, height * 0.42,
                   width * 0.86, height * 0.44,
                   width + 40, height * 0.16))
    return ("M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f"
            % (-40, height * 0.86,
               width * 0.36, height * 0.86,
               width * 0.52, height * 0.56,
               width + 40, height * 0.34))


def _network(width: int, height: int, o: Dict[str, Any]):
    """A small, deliberate node lattice — not a crypto constellation."""
    pts = o.get("net_points") or [
        (0.09, 0.16), (0.30, 0.09), (0.52, 0.20), (0.19, 0.34),
        (0.41, 0.40), (0.68, 0.33), (0.88, 0.22), (0.78, 0.52),
    ]
    nodes = [{"cx": round(x * width, 1), "cy": round(y * height, 1),
              "r": 4.0 if i % 3 == 0 else 2.6}
             for i, (x, y) in enumerate(pts)]
    links = o.get("net_links") or [(0, 1), (1, 2), (0, 3), (3, 4), (2, 4),
                                   (2, 5), (5, 6), (5, 7)]
    edges = ["M%.1f %.1f L%.1f %.1f" % (nodes[a]["cx"], nodes[a]["cy"],
                                        nodes[b]["cx"], nodes[b]["cy"])
             for a, b in links if a < len(nodes) and b < len(nodes)]
    return nodes, edges


def accent_rgb(cfg, ground: str = "dark") -> str:
    grounds = cfg.brand["grounds"][ground]
    return _hex_to_rgb(cfg.brand["palette"][grounds["accent"]])
