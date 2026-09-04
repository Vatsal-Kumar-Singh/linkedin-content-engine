---
name: creative-direction
description: Develop a visual system for social creatives and iterate it in numbered passes. Use when starting a creative direction from a reference image, adding shape motifs or motion, or preparing a design handoff. Covers measuring a reference instead of eyeballing it, the light/dark inversion, and the defects that only show up when you look at the render.
---

# Creative direction

The method that produced the design system in this repo. It generalises; the
particular shapes do not.

## 1. Measure the reference, do not eyeball it

Given a reference image, extract numbers before forming an opinion: the colour at
each corner, the hue and saturation of each pole, how much of the frame is ink,
and how far the strokes darken the ground beneath them (compare each pixel to a
blurred copy of itself — a uniform filter at about 21px works).

On the original reference that produced: **9 strokes, 2.55% ink coverage, poles at
29–41% saturation and 89–100% value, strokes darkening their ground by ~50 on
average.** Every one of those became a parameter.

The first attempt, judged by eye, was three times too faint. "Too faint" is
arguable until you have the number.

## 2. Check the palette can actually reach it

Tint each brand colour toward the reference's measured band and read the result
back. On the original project only two of the palette's colours survived — the
others landed at 4–11% saturation, which is grey, not pale.

That is a finding to report, not a problem to hide. It is also an argument for
extending the palette, which is a decision someone else owns.

## 3. Open shapes, and what "open" means

Thin strokes, never a closed outline, never a fill, bleeding past the frame so the
card reads as a crop of something larger. Build a family — the one here has seven:
crossing, nesting, weaving, winding, interference, deflection, propagation.

Two things separate a family from wallpaper.

**Vary weight and opacity across the bundle**, smoothly rather than randomly.
Random per-stroke noise looks like a rendering fault; a gradient looks lit. Every
stroke identical is why a figure reads as a flat diagram.

**Give it a point of rest** — one accent, placed *on* the figure. Reading a
coordinate off a middle stroke works for every motif; the construction centre does
not, because several motifs are built around a point their strokes never touch,
and an accent there floats in empty space.

Seed the choice from the post id, never the clock. A post re-rendered mid-run must
be the same image.

## 4. Light and dark are opposite operations, not one with a swapped background

Poles are tinted **toward white** on a pale ground and shaded **toward the ground**
on a dark one. Reusing the light tints on navy produced pastel smears floating on a
dark card.

The same inversion governs motion. A *brightening* sweep is invisible on a pale
ground. Make the highlight its own layer over the strokes: on dark it is lighter
than them, on light it is darker. One set of keyframes then serves both, and the
only thing that changes is which side of the strokes the highlight sits on.

## 5. Motion

Drive `stroke-dashoffset` against a declared `pathLength`. A nominal length is what
lets one set of dash numbers work for a spiral and a straight line, whose real arc
lengths differ by an order of magnitude.

- **Only the background moves.** A card whose headline flies in is a template pack.
- **Seek frames, do not sample them.** Pause every animation and set its
  `currentTime` per frame, or two renders of one card differ.
- **Rest, but not too much.** A highlight that never stops is a loading spinner;
  one that rests half the loop leaves the card visibly dead.
- **Watch the file size.** Anything changing every pixel every frame — a rotating
  full-frame gradient — cannot be compressed by GIF. Two such modes came to 27 MB
  each against 2 MB for the others. Install ffmpeg and the MP4 path takes over.

## 6. Look at the render. Every time.

These all passed the test suite and were caught only by opening the image:

- a comet head that detached from its tail — two dash patterns with different
  periods, so they wrapped at different points
- a figure that tore in half — the dash seam sat inside the frame
- a "bullseye" that was technically a set of open arcs
- a scrim correct on the pale ground and a glaring band on the dark one
- a single spiral that vanished once depth variation started thinning strokes,
  because one stroke has nothing to be varied against
- curves running straight through the headline: legible in isolation, and not once
  real copy went on top

Render it, open it, look at it. Then look at it again with the actual copy on it.

## 7. Work in numbered passes

Tag each one in git. Keep a `DESIGN-PASSES.md` recording what changed, what it
fixed, and what is still open; the tag lets anyone render or diff a previous pass.

Start a pass by asking about scope rather than assuming — which templates, which
grounds, what content, what motion. Both passes on the original project began with
four questions and both were better for it.

End a pass by writing down its known limits. The next pass starts there.
