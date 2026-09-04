# the product Creative System

**Status:** interim the product sub-brand. The rules do not exist yet (decisions-log
ruling 1), so this is the first draft of the visual language — which is the
pragmatic option design-direction.md §6 already recommended. Every value lives in
`config/brand.yaml`; changing that one file restyles every template.

---

## Tokens

| Group | Values |
|---|---|
| Ground | Deep Navy `#0B1F33` · raised `#12293F` · edge `#1C3A55` |
| Primary | the company Blue `#1780C3` |
| Silver | `#E6E8EB` · `#B8BEC6` · `#8F98A3` · `#626C78` |
| Type | Poppins 300/400/600 (display) · Inter 300/400/500 (body), embedded as woff2 |
| Scale | eyebrow 26 → focal 480. Roughly 1:18, deliberately steep |

Silver carries structure — rules, connectors, tick rails, corner marks, diagram
strokes, secondary type. It is never the dominant colour.

## Background system

Composable layers, fixed stacking order: `ground → texture → geometry → glow →
content`. Parameters in `config/brand.yaml → backgrounds`, geometry computed in
`postengine/render/backgrounds.py`.

| Layer | Use |
|---|---|
| `grid` / `dots` | Near-threshold texture. Structure you feel rather than see |
| `glow` | Restrained directional illumination in brand blue. Never a neon gradient |
| `geometry` | Large concentric rings centred **outside** the canvas, so arcs bleed off two edges — the composition reads as a fragment of a larger system |
| `linework` | Corner marks and a measured tick rail. Makes the creative feel engineered |
| `flow` | Long curves for transformation, workflow, before → after |
| `network` | A small deliberate node lattice for orchestration. Not a constellation |

## Depth

Three layers on every template: background texture → content → foreground detail
(rails, corner marks, the raised bottom band). Depth comes from layering, scale,
opacity, overlap and cropping — not from fake 3D or glassmorphism.

## Template families

| # | Template | Dominant idea | Type-ratio floor |
|---|---|---|---|
| 01 | `card/big_stat` | The figure, ~35% of canvas area, with a data row that visualises it | 8.0 |
| 02 | `card/comparison` | Two worlds either side of a divider; the right side is materially heavier | 3.0 |
| 03 | `card/journey` | The path is the graphic; steps hang off it | 3.0 |
| 04 | `card/editorial` | One massive headline as an object. Carousel cover | 4.0 |
| 05 | `card/framework` | Four blocks on a spine, aggressively simplified | 3.0 |
| 06 | `card/contrarian` | A single sentence; the background system carries the richness | 4.0 |
| — | `document/editorial` | Carousel: editorial cover + body slides + close | 3.5 |

Shared partials: `_shared/backgrounds.html`, `_shared/band.html`,
`_shared/bandstyle.html`. Micro-details (corner marks, tick rows, rails, index
labels, chips) live in `_shared/backgrounds.css`.

## Qualifiers are content, not disclaimers

The bordered "ILLUSTRATIVE FIGURE, NOT AN the company MEASUREMENT" pill is gone. It was
the second-loudest object on the card and drew the eye to the least interesting
words on it.

Gate A2 still requires the qualifier **on the creative** — it is now a labelled
fact in the context strip:

```
CONTRACTUAL TARGET              SCOPE
90 days to first governed       First governed release
go-live                         in production
```

`creative_strip` is a validated draft field, so what the validator scans is
exactly what the renderer draws. `source_label` exists for a genuine citation and
is never populated automatically.

## Measured, not asserted

Every render is measured after layout and the numbers are stored in
`run_report.json`:

| Metric | Meaning |
|---|---|
| `canvas_utilization` | Union bounding box of content ÷ artboard |
| `content_coverage` | Ink coverage sampled on a grid — catches "headline on a coloured rectangle" |
| `type_scale_ratio` | Largest to smallest rendered text |
| `guard_overflows` | Content containers compressed so content renders behind a later block |
| `clipped_elements` | Content cut off by a clipping container |

Text that will not fit is **not** shrunk indefinitely: autofit is bounded, and
below the legibility floor the render fails and the copy goes back to the
generator. Per-template character budgets are in `TEMPLATE_LIMITS`.

Mobile is checked as a ratio, not an absolute: text must be ≥2% of image height,
and anything that has to stop a scroll unaided (a card, or a carousel cover) must
have a dominant element ≥6%.
