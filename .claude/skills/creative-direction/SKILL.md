---
name: creative-direction
description: Develop a visual system for social creatives and iterate it in numbered passes. Use when starting a creative direction from a reference image, adding shape motifs or motion, or preparing a design handoff. Covers measuring a reference instead of eyeballing it, the light/dark inversion, and the defects that only show up when you look at the render.
---

# Creative direction

The method that produced the design system in this repo. It generalises; the
particular shapes do not.

## 0. Know which format you are designing for, and whether it is worth designing

Before any of the craft below, the largest measured effect on a post is its format,
not its execution. From 3,114 hand-read posts in `docs/BENCHMARKS.md`, scored
against each company's own median:

| Format | Share of posts | Engagement |
|---|---:|---:|
| multi-image / carousel | **7.9%** | **1.61x** |
| video | 33.6% | 1.13x |
| single image | 30.5% | 1.00x |
| text only | 14.9% | 0.78x |
| link post | 13.2% | **0.78x** |

Three things follow for a designer.

### Aspect ratio is the design decision nobody makes

Measured on all 1,277 image posts in the corpus, not sampled:

| Shape | Share | Engagement | Doubles the median |
|---|---:|---:|---:|
| **wide 16:9** | **39.0%** | 1.08x | 21% |
| square 1:1 | 32.3% | 1.00x | 20% |
| **portrait 4:5** | 19.0% | **1.16x** | **28%** |
| landscape 4:3 | 8.1% | **1.47x** | 32% |

**The most-used ratio is the one that claims the least screen.** The feed is a
fixed-width column, so 4:5 occupies roughly twice the height of 16:9 for the same
post. 16:9 is where a repurposed asset lands — a blog header, a webinar slide, a
YouTube thumbnail are all 16:9 already. That 39% is not a design decision, it is
the absence of one.

**It is not a blanket rule.** Portrait is the best shape for `selection` (4.18x
against 2.10x for 16:9), `validation` and `event`. It is the *worst* for
`exploration`, `product-news` and `problem`, all three of which do better wide.
Set the ratio per job in the template, not per post.

### What separates a strong creative from a weak one

Eight images were pulled from the corpus and coded, paired strong-against-weak
within the same buying job (`research/sample_creative.py`). Small sample, stated
as one — these are things to try, not benchmarks.

**Evidence beats assertion, by a lot.** The strongest `validation` creative (6.54x)
is a third-party benchmark leaderboard with the vendor at rank one, competitors
named, and the number legible at feed size. The weakest (0.08x) is a quote card:
a customer endorsement in large display type with no number on it. One shows the
thing working; the other shows somebody saying it works.

**A picture of a PDF is a picture of homework.** The weak `requirements` creative
is a 16:9 cover with a rendered mockup of the document floating on it — which is
exactly what a buyer's guide gets published as.

**The weakest creatives carried no brand system at all.** A stock meme template
with visible compression, and a retail-style sale banner with a discount badge.
Both would have looked identical with another company's name on them.

**Type alone is fine, and often better.** The strongest `selection` creative
(16.29x) is a portrait card carrying the logo and the award line and nothing else.

**The best format is the least used, by a factor of four.** Fourteen of 73 companies
published no carousel at all. A carousel is more design work than a card, which is
presumably why — and it is the work with the highest measured return.

**Where carousels exist, they are spent on the wrong content.** Culture posts
(2.38x) dominate carousel usage at 23%; `requirements` — comparisons and buyer's
guides — uses carousels **2%** of the time and link posts **34%** of the time. A
comparison has two states and a trade-off, which is carousel-shaped by nature. It
is being posted as a link to a blog.

**A single image is the baseline, not a win.** It earns exactly 1.00x. Designing a
beautiful card buys you nothing over an ordinary one *at the format level* — the
gain from that work is in comprehension and trust, not reach. Do not let a strong
single-image system become the reason nothing else gets built.

Different offerings behave differently: product companies are the most video-heavy
(37%), service firms use the most carousels (13%) and the most links (22%).

## 0b. On a named person's channel, the answer is often "do not design it"

The same study measured 43 named people against their own company pages:

| | Page | Person |
|---|---:|---:|
| text-only | 14.5% | **36.2%** |
| video | 34.1% | **16.2%** |
| single image | 30.5% | 32.1% |
| multi-image | 7.1% | 5.7% |

**A person's feed is 36% plain text and a page's is 15%.** Video roughly halves.
A page has a design and video pipeline behind it and it uses it; a person types.

For a designer this is a scoping fact, not a taste one. **Creative work aimed at a
founder channel will mostly go unused**, and the pieces that do get used are the
ones a person would plausibly have made or commissioned themselves. The instinct to
give an executive channel the full brand system is the instinct that produces the
0.54x VP row in the benchmarks: a page post with a face on it.

Where design does earn its place on a person channel, it is the same multi-image
gap as everywhere else — 5.8% of person posts, against the 1.61x it earns.

**And the carousel advantage is not a culture-post artefact.** Tested inside each
job, multi-image beats the other formats in five of six: validation 1.38x against
0.97x, event 1.60x against 0.93x, exploration 1.36x against 0.94x. The one
exception is product news (0.88x against 1.24x), which fits — a launch is an
announcement, and a carousel asks the reader to work through it. So a case study
built as a carousel is a materially different post from the same case study posted
as a link, and that is a design decision rather than a copy one.

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
