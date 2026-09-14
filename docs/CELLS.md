# The grid: what each cell actually publishes

Everything in [`BENCHMARKS.md`](BENCHMARKS.md) cuts one axis at a time — offering, or motion, or
stage, or industry. This cuts **all three of the first ones at once**, because that is how a
company identifies itself: "early-stage SaaS sold product-led", not "SaaS".

Every cell below carries its own content mix, cadence, format mix, recurring post shapes,
aspect-ratio profile and three named exemplars. **The body of this page is generated**, so it
cannot drift from the corpus:

```bash
python research/classify_posts.py --dump research/findings.json
python research/analyse_cells.py --markdown docs/_cells_body.md   # then paste below the line
python research/analyse_cells.py --grid                           # occupancy, including the holes
```

---

## What "best in cell" can and cannot mean

Every post here is scored against its **own company's median**, because a median pooled across
companies ranks audience size rather than post quality. That is what makes the corpus readable,
and it also means **every company's median is 1.00 by construction.** There is no engagement
ranking of companies to be had from this data. Anyone producing one has either pooled raw
engagement — which ranks follower counts — or invented it.

So each cell names three exemplars on three things the data *can* see:

| | What it measures | Why it is the right question |
|---|---|---|
| **fullest funnel** | share of `requirements` + `consensus` + `validation` | decision-stage content is 3.9% of the whole corpus. Publishing it is the rare act |
| **best format mix** | carousel + video share, minus link share | the largest measured effect on the page, and a production decision rather than a content one |
| **most breakouts** | share of posts at 3x their own median | a feed with hits in it, as distinct from a feed with a high floor |

**They are usually three different companies, and that is the finding.** The company with the
fullest funnel is rarely the one with the biggest hits.

---

## Six things visible only when all three axes are cut at once

### 1. Decision-stage content arrives with the motion, not with the size

The share of `requirements` + `consensus`:

| By stage | | | By motion | |
|---|---:|---|---|---:|
| early | 5.0% | | plg | 2.4% |
| growth | 3.1% | | pls | 2.8% |
| scaled | 4.5% | | slg | 3.1% |
| | | | **enterprise** | **6.4%** |

**There is no stage gradient at all** — growth-stage companies publish *less* decision content
than early-stage ones. There is a clean motion gradient, and enterprise sits at 2.7x PLG.

**You do not grow into publishing buyer's guides. You sell your way into them.** The thing that
produces comparison and business-case content is a committee on the other side of the table, and
that arrives with the motion on the day you start selling that way — not when you hit 500 people.
A growth-stage company moving upmarket needs this content *before* the headcount that usually
accompanies it.

### 2. Proof, unlike decision content, does track scale — inside every motion

Share of `requirements` + `consensus` + `validation`, per cell:

| Cell | early | growth | scaled |
|---|---:|---:|---:|
| saas x plg | 5% | 8% | 10% |
| saas x pls | — | 11% | 16% |
| saas x slg | — | 10% | 15% |
| saas x enterprise | — | 16% | **30%** |
| product x enterprise | — | 20% | 16% |

Every SaaS motion roughly doubles its proof content from its first measured stage to scaled. The
mechanism is not mysterious and it is circular: proof requires customers, and customers arrive
with scale. **The one cell that breaks the pattern is product x enterprise, where growth-stage
robotics companies publish *more* proof than scaled industrial ones** — because a young robotics
company has nothing else to sell with.

### 3. Format discipline gets worse as companies grow

Median across companies, so no single prolific page can move a row:

| Stage | carousel | link post | video |
|---|---:|---:|---:|
| early | **6.5%** | **6.7%** | 26.7% |
| growth | 6.2% | 10.0% | 28.0% |
| scaled | **5.1%** | **12.0%** | **42.0%** |

Scaled companies use **fewer carousels and nearly twice the link posts** — the best format and the
worst one, moving in the wrong directions together. Video doubles, which is a budget story and a
sensible one. The link-post drift is not: it is what happens when a content team with a large blog
starts treating LinkedIn as a distribution channel for it.

And by motion, the same table is sharper still:

| Motion | carousel | link post |
|---|---:|---:|
| plg | 6.7% | 8.0% |
| slg | 6.7% | 9.8% |
| pls | 4.7% | 11.8% |
| **enterprise** | **2.4%** | **12.7%** |

**The enterprise motion has the worst format discipline of any motion measured**, and it is the
motion whose content most needs a carousel: comparisons, trade-offs, business cases. It publishes
them as links.

### 4. Cadence roughly quintuples from early to scaled, and the jump is at the top

| Cell | early | growth | scaled |
|---|---:|---:|---:|
| saas x plg | 1.9/wk | 4.3/wk | 5.8/wk |
| saas x pls | — | 3.6/wk | 5.4/wk |
| saas x slg | — | 3.7/wk | 5.2/wk |
| saas x enterprise | — | 3.8/wk | **11.2/wk** |
| product x enterprise | — | 2.2/wk | **10.0/wk** |

Growth-stage companies cluster tightly at 3.6–4.3 posts a week regardless of motion. Scaled
enterprise companies publish **three times** that. What a small company lacks is not audience, it
is publishing capacity — and the gap opens at the top of the range, not across it.

### 5. Early-stage product-led SaaS publishes no buyer's guides at all

Four companies, 192 posts, **zero `requirements`.** 69% of the cell is non-buying content: events,
launches, hiring, culture. That is coherent for a product that sells itself, and it is exactly the
cell that most often gets copied by companies whose product does not.

### 6. The fullest funnel in the entire corpus is a regulated enterprise vendor

**Veeva Systems publishes 52% requirements, consensus or validation.** Nothing else in 73
companies comes close. It sells validated systems into life sciences, where every claim is a
regulatory artefact, so the content that survives legal review is the content that carries
evidence. The constraint that looks like a handicap produced the most buyer-useful page measured.

Second is **Abridge at 37%**, also healthcare. Third is **ABB Robotics at 28%**. All three sell
into review processes.

---

## The holes

Fourteen of the 36 cells are below the three-company floor and are **not** reported below. Three
motion-offering pairs are structurally empty and are recorded as such rather than left looking
like an oversight:

- **service x plg** — you cannot self-serve a consultancy.
- **service x pls** — productised services with a self-serve tier exist, mostly design
  subscriptions, and none met this sample's B2B bar.
- **product x pls** — hardware bought on a card that then converts to a contract is a thin band
  between PLG and SLG; no clean example was found.

The remaining gaps are fillable and are listed by `analyse_cells.py --grid`. The largest are
**service x enterprise at early and growth stage** (boutique consultancies), **service x slg at
scale**, and **saas x enterprise at early stage** — companies selling to enterprises from day one.
Filling every fillable cell to three companies needs roughly **31 more pages**, which is about
1,500 more posts to read and about $2.50 of scraping.

---

## saas x plg x early

**192 posts, 4 companies:** Cal.com, Juro, Resend, Trigger.dev

| TOFU | MOFU | BOFU | non-buying | cadence |
|---:|---:|---:|---:|---:|
| 17% | 4% | 5% | 69% | 1.9 posts/week |

**What it publishes**

| Job | n | Share | Engagement |
|---|---:|---:|---:|
| `event` | 52 | 27% | 1.11x |
| `product-news` | 43 | 22% | 0.94x |
| `exploration` | 24 | 12% | 0.91x |
| `recruitment` | 22 | 11% | 0.90x |
| `culture` | 16 | 8% | 1.29x |
| `unclear` | 9 | 5% | 1.25x |
| `problem` | 9 | 5% | 0.86x |
| `selection` | 8 | 4% | 1.00x |
| `validation` | 7 | 4% | - |
| `consensus` | 2 | 1% | - |

**Publishes no `requirements` at all.**

**Format**

| Format | n | Share | Engagement |
|---|---:|---:|---:|
| image | 81 | 42% | 0.86x |
| video | 58 | 30% | 1.25x |
| link | 24 | 12% | 0.91x |
| text | 19 | 10% | 0.86x |
| multi-image | 10 | 5% | 1.81x |

**Shapes that recur in this cell** (8 posts or more)

| Job | Format | Opening | n | Engagement |
|---|---|---|---:|---:|
| `exploration` | video | declarative | 8 | 1.30x |
| `product-news` | video | declarative | 15 | 1.00x |
| `event` | image | declarative | 14 | 0.90x |
| `exploration` | image | declarative | 9 | 0.72x |
| `recruitment` | image | declarative | 15 | 0.67x |

**Design: aspect ratio of image posts**

| Shape | n | Engagement |
|---|---:|---:|
| wide 16:9 | 49 | 0.75x |
| square 1:1 | 23 | 0.95x |
| portrait 4:5 | 12 | 2.00x |
| landscape 4:3 | 7 | - |

**Exemplars**

| | Company | |
|---|---|---|
| fullest funnel | **Trigger.dev** | 10% of posts are requirements, consensus or validation |
| best format mix | **Resend** | 62% carousel or video, 4% link |
| most breakouts | **Resend** | 19% of posts at 3x their own median |

---

## saas x plg x growth

**124 posts, 3 companies:** Linear, Mercury, Supabase

| TOFU | MOFU | BOFU | non-buying | cadence |
|---:|---:|---:|---:|---:|
| 20% | 2% | 8% | 69% | 4.3 posts/week |

**What it publishes**

| Job | n | Share | Engagement |
|---|---:|---:|---:|
| `product-news` | 43 | 35% | 1.18x |
| `event` | 29 | 23% | 0.89x |
| `exploration` | 24 | 19% | 0.92x |
| `culture` | 13 | 10% | 0.76x |
| `validation` | 9 | 7% | 1.05x |
| `selection` | 2 | 2% | - |
| `recruitment` | 1 | 1% | - |
| `problem` | 1 | 1% | - |
| `unclear` | 1 | 1% | - |
| `consensus` | 1 | 1% | - |

**Publishes no `requirements` at all.**

**Format**

| Format | n | Share | Engagement |
|---|---:|---:|---:|
| video | 54 | 44% | 1.24x |
| image | 37 | 30% | 0.99x |
| link | 19 | 15% | 0.72x |
| multi-image | 9 | 7% | 1.41x |
| text | 5 | 4% | - |

**Shapes that recur in this cell** (8 posts or more)

| Job | Format | Opening | n | Engagement |
|---|---|---|---:|---:|
| `product-news` | video | declarative | 20 | 1.71x |
| `event` | video | declarative | 13 | 1.20x |
| `exploration` | video | declarative | 9 | 1.05x |
| `product-news` | image | declarative | 11 | 0.92x |

**Design: aspect ratio of image posts**

| Shape | n | Engagement |
|---|---:|---:|
| wide 16:9 | 32 | 0.97x |
| landscape 4:3 | 8 | 1.29x |
| portrait 4:5 | 3 | - |
| square 1:1 | 3 | - |

**Exemplars**

| | Company | |
|---|---|---|
| fullest funnel | **Linear** | 15% of posts are requirements, consensus or validation |
| best format mix | **Mercury** | 60% carousel or video, 10% link |
| most breakouts | **Mercury** | 10% of posts at 3x their own median |

---

## saas x plg x scaled

**172 posts, 5 companies:** Figma, Notion, Postman, Snyk, Zoho

| TOFU | MOFU | BOFU | non-buying | cadence |
|---:|---:|---:|---:|---:|
| 27% | 6% | 7% | 56% | 5.8 posts/week |

**What it publishes**

| Job | n | Share | Engagement |
|---|---:|---:|---:|
| `product-news` | 41 | 24% | 1.60x |
| `exploration` | 38 | 22% | 0.79x |
| `event` | 30 | 17% | 1.00x |
| `culture` | 19 | 11% | 1.70x |
| `problem` | 9 | 5% | 0.67x |
| `validation` | 7 | 4% | - |
| `selection` | 6 | 3% | - |
| `unclear` | 5 | 3% | - |
| `consensus` | 5 | 3% | - |
| `requirements` | 5 | 3% | - |
| `csr` | 4 | 2% | - |
| `recruitment` | 3 | 2% | - |

**Format**

| Format | n | Share | Engagement |
|---|---:|---:|---:|
| text | 57 | 33% | 0.88x |
| video | 51 | 30% | 1.33x |
| image | 37 | 22% | 1.17x |
| multi-image | 14 | 8% | 2.23x |
| link | 13 | 8% | 0.53x |

**Shapes that recur in this cell** (8 posts or more)

| Job | Format | Opening | n | Engagement |
|---|---|---|---:|---:|
| `product-news` | video | declarative | 18 | 2.12x |
| `product-news` | text | declarative | 10 | 1.39x |
| `exploration` | text | declarative | 16 | 0.82x |
| `event` | image | declarative | 14 | 0.62x |
| `exploration` | video | declarative | 10 | 0.53x |

**Design: aspect ratio of image posts**

| Shape | n | Engagement |
|---|---:|---:|
| wide 16:9 | 31 | 1.20x |
| square 1:1 | 8 | 1.50x |
| landscape 4:3 | 6 | - |
| portrait 4:5 | 4 | - |
| tall 9:16+ | 2 | - |

**Exemplars**

| | Company | |
|---|---|---|
| fullest funnel | **Postman** | 22% of posts are requirements, consensus or validation |
| best format mix | **Figma** | 53% carousel or video, 7% link |
| most breakouts | **Zoho** | 40% of posts at 3x their own median |

---

## saas x pls x growth

**179 posts, 4 companies:** Buildertrend, Retool, Vanta, Vercel

| TOFU | MOFU | BOFU | non-buying | cadence |
|---:|---:|---:|---:|---:|
| 26% | 7% | 8% | 55% | 3.6 posts/week |

**What it publishes**

| Job | n | Share | Engagement |
|---|---:|---:|---:|
| `event` | 47 | 26% | 0.92x |
| `product-news` | 30 | 17% | 1.61x |
| `exploration` | 26 | 15% | 0.73x |
| `problem` | 21 | 12% | 0.64x |
| `culture` | 20 | 11% | 1.83x |
| `validation` | 11 | 6% | 0.92x |
| `selection` | 7 | 4% | - |
| `requirements` | 6 | 3% | - |
| `unclear` | 6 | 3% | - |
| `consensus` | 3 | 2% | - |
| `csr` | 1 | 1% | - |
| `recruitment` | 1 | 1% | - |

**Format**

| Format | n | Share | Engagement |
|---|---:|---:|---:|
| video | 50 | 28% | 1.06x |
| link | 48 | 27% | 0.97x |
| text | 34 | 19% | 0.72x |
| image | 32 | 18% | 1.04x |
| multi-image | 15 | 8% | 1.62x |

**Shapes that recur in this cell** (8 posts or more)

| Job | Format | Opening | n | Engagement |
|---|---|---|---:|---:|
| `product-news` | video | declarative | 8 | 1.62x |
| `product-news` | link | declarative | 10 | 1.48x |
| `event` | image | declarative | 11 | 1.46x |
| `event` | video | declarative | 8 | 1.04x |
| `problem` | text | declarative | 9 | 0.50x |

**Design: aspect ratio of image posts**

| Shape | n | Engagement |
|---|---:|---:|
| wide 16:9 | 20 | 0.97x |
| portrait 4:5 | 14 | 1.97x |
| square 1:1 | 9 | 1.15x |
| landscape 4:3 | 3 | - |
| tall 9:16+ | 1 | - |

**Exemplars**

| | Company | |
|---|---|---|
| fullest funnel | **Vercel** | 16% of posts are requirements, consensus or validation |
| best format mix | **Vanta** | 54% carousel or video, 12% link |
| most breakouts | **Buildertrend** | 28% of posts at 3x their own median |

---

## saas x pls x scaled

**321 posts, 8 companies:** 1Password, Airtable, Bluebeam, Clio, Deel, Freshworks, Miro, Stripe

| TOFU | MOFU | BOFU | non-buying | cadence |
|---:|---:|---:|---:|---:|
| 32% | 8% | 14% | 45% | 5.4 posts/week |

**What it publishes**

| Job | n | Share | Engagement |
|---|---:|---:|---:|
| `exploration` | 80 | 25% | 0.99x |
| `event` | 70 | 22% | 1.06x |
| `product-news` | 49 | 15% | 0.98x |
| `validation` | 45 | 14% | 0.87x |
| `selection` | 22 | 7% | 2.77x |
| `problem` | 22 | 7% | 0.66x |
| `culture` | 20 | 6% | 0.85x |
| `csr` | 5 | 2% | - |
| `requirements` | 4 | 1% | - |
| `recruitment` | 2 | 1% | - |
| `consensus` | 1 | 0% | - |
| `unclear` | 1 | 0% | - |

**Format**

| Format | n | Share | Engagement |
|---|---:|---:|---:|
| video | 130 | 40% | 1.08x |
| image | 93 | 29% | 1.00x |
| text | 43 | 13% | 0.71x |
| link | 31 | 10% | 0.86x |
| multi-image | 24 | 7% | 1.32x |

**Shapes that recur in this cell** (8 posts or more)

| Job | Format | Opening | n | Engagement |
|---|---|---|---:|---:|
| `selection` | image | declarative | 9 | 2.94x |
| `event` | multi-image | declarative | 12 | 1.69x |
| `event` | video | declarative | 9 | 1.55x |
| `product-news` | video | declarative | 26 | 1.23x |
| `exploration` | image | declarative | 15 | 1.15x |
| `validation` | image | declarative | 8 | 1.00x |
| `exploration` | video | declarative | 21 | 1.00x |
| `exploration` | text | declarative | 14 | 0.98x |

**Design: aspect ratio of image posts**

| Shape | n | Engagement |
|---|---:|---:|
| wide 16:9 | 50 | 1.14x |
| portrait 4:5 | 31 | 1.71x |
| square 1:1 | 29 | 0.99x |
| landscape 4:3 | 6 | - |
| tall 9:16+ | 1 | - |

**Exemplars**

| | Company | |
|---|---|---|
| fullest funnel | **Deel** | 26% of posts are requirements, consensus or validation |
| best format mix | **Miro** | 72% carousel or video, 6% link |
| most breakouts | **1Password** | 25% of posts at 3x their own median |

---

## saas x slg x growth

**380 posts, 9 companies:** 6sense, Clari, Cognism, Ironclad, Lattice, Modern Treasury, Persefoni, Ramp, Watershed

| TOFU | MOFU | BOFU | non-buying | cadence |
|---:|---:|---:|---:|---:|
| 32% | 9% | 8% | 48% | 3.7 posts/week |

**What it publishes**

| Job | n | Share | Engagement |
|---|---:|---:|---:|
| `exploration` | 94 | 25% | 0.81x |
| `event` | 70 | 18% | 1.01x |
| `culture` | 61 | 16% | 1.14x |
| `product-news` | 41 | 11% | 1.00x |
| `problem` | 29 | 8% | 0.77x |
| `selection` | 28 | 7% | 2.15x |
| `validation` | 27 | 7% | 1.19x |
| `recruitment` | 10 | 3% | 0.66x |
| `unclear` | 8 | 2% | 1.25x |
| `requirements` | 8 | 2% | 1.03x |
| `consensus` | 3 | 1% | - |
| `csr` | 1 | 0% | - |

**Format**

| Format | n | Share | Engagement |
|---|---:|---:|---:|
| image | 163 | 43% | 1.00x |
| video | 102 | 27% | 1.19x |
| text | 50 | 13% | 0.73x |
| link | 43 | 11% | 0.81x |
| multi-image | 22 | 6% | 2.07x |

**Shapes that recur in this cell** (8 posts or more)

| Job | Format | Opening | n | Engagement |
|---|---|---|---:|---:|
| `selection` | image | declarative | 13 | 4.00x |
| `product-news` | image | declarative | 14 | 1.61x |
| `validation` | video | declarative | 9 | 1.43x |
| `validation` | image | declarative | 9 | 1.19x |
| `event` | video | declarative | 12 | 1.17x |
| `exploration` | video | declarative | 14 | 1.14x |
| `product-news` | video | declarative | 12 | 1.13x |
| `culture` | text | declarative | 8 | 1.12x |

**Design: aspect ratio of image posts**

| Shape | n | Engagement |
|---|---:|---:|
| portrait 4:5 | 74 | 0.92x |
| wide 16:9 | 65 | 1.05x |
| square 1:1 | 31 | 1.26x |
| landscape 4:3 | 12 | 1.17x |
| tall 9:16+ | 3 | - |

**Exemplars**

| | Company | |
|---|---|---|
| fullest funnel | **Modern Treasury** | 19% of posts are requirements, consensus or validation |
| best format mix | **Ramp** | 73% carousel or video, 5% link |
| most breakouts | **6sense** | 16% of posts at 3x their own median |

---

## saas x slg x scaled

**206 posts, 5 companies:** Gong, Outreach, Personio, Procore, Rippling

| TOFU | MOFU | BOFU | non-buying | cadence |
|---:|---:|---:|---:|---:|
| 21% | 8% | 13% | 56% | 5.2 posts/week |

**What it publishes**

| Job | n | Share | Engagement |
|---|---:|---:|---:|
| `culture` | 47 | 23% | 1.33x |
| `event` | 34 | 17% | 0.77x |
| `exploration` | 29 | 14% | 0.97x |
| `product-news` | 24 | 12% | 1.73x |
| `validation` | 21 | 10% | 0.91x |
| `problem` | 14 | 7% | 1.00x |
| `selection` | 13 | 6% | 1.33x |
| `recruitment` | 10 | 5% | 1.00x |
| `consensus` | 6 | 3% | - |
| `requirements` | 4 | 2% | - |
| `unclear` | 4 | 2% | - |

**Format**

| Format | n | Share | Engagement |
|---|---:|---:|---:|
| video | 79 | 38% | 1.13x |
| image | 48 | 23% | 0.90x |
| link | 37 | 18% | 0.80x |
| text | 24 | 12% | 1.00x |
| multi-image | 18 | 9% | 2.39x |

**Shapes that recur in this cell** (8 posts or more)

| Job | Format | Opening | n | Engagement |
|---|---|---|---:|---:|
| `product-news` | video | declarative | 8 | 2.67x |
| `culture` | multi-image | declarative | 11 | 2.18x |
| `exploration` | text | declarative | 8 | 1.15x |
| `culture` | video | declarative | 12 | 1.14x |
| `culture` | image | declarative | 8 | 1.00x |
| `culture` | video | question | 9 | 1.00x |
| `exploration` | video | declarative | 8 | 0.88x |

**Design: aspect ratio of image posts**

| Shape | n | Engagement |
|---|---:|---:|
| square 1:1 | 29 | 0.87x |
| portrait 4:5 | 17 | 0.93x |
| wide 16:9 | 12 | 2.05x |
| landscape 4:3 | 7 | - |
| tall 9:16+ | 1 | - |

**Exemplars**

| | Company | |
|---|---|---|
| fullest funnel | **Procore** | 26% of posts are requirements, consensus or validation |
| best format mix | **Rippling** | 67% carousel or video, 18% link |
| most breakouts | **Procore** | 18% of posts at 3x their own median |

---

## saas x enterprise x growth

**224 posts, 5 companies:** Abridge, Cohere Health, Komodo Health, Wiz, project44

| TOFU | MOFU | BOFU | non-buying | cadence |
|---:|---:|---:|---:|---:|
| 30% | 12% | 12% | 46% | 3.8 posts/week |

**What it publishes**

| Job | n | Share | Engagement |
|---|---:|---:|---:|
| `exploration` | 57 | 25% | 0.85x |
| `event` | 46 | 21% | 0.98x |
| `culture` | 28 | 12% | 1.33x |
| `validation` | 26 | 12% | 0.97x |
| `selection` | 17 | 8% | 2.25x |
| `product-news` | 14 | 6% | 1.38x |
| `recruitment` | 12 | 5% | 0.85x |
| `problem` | 11 | 5% | 0.69x |
| `requirements` | 10 | 4% | 0.77x |
| `csr` | 3 | 1% | - |

**Publishes no `consensus` at all.**

**Format**

| Format | n | Share | Engagement |
|---|---:|---:|---:|
| image | 124 | 55% | 1.00x |
| video | 53 | 24% | 1.22x |
| multi-image | 23 | 10% | 1.29x |
| link | 12 | 5% | 0.51x |
| text | 12 | 5% | 0.70x |

**Shapes that recur in this cell** (8 posts or more)

| Job | Format | Opening | n | Engagement |
|---|---|---|---:|---:|
| `selection` | image | declarative | 11 | 2.25x |
| `product-news` | image | declarative | 8 | 1.49x |
| `culture` | image | declarative | 11 | 1.44x |
| `event` | multi-image | declarative | 11 | 1.31x |
| `exploration` | video | declarative | 19 | 1.14x |
| `validation` | image | declarative | 11 | 1.14x |
| `validation` | video | declarative | 10 | 0.95x |
| `exploration` | image | declarative | 19 | 0.90x |

**Design: aspect ratio of image posts**

| Shape | n | Engagement |
|---|---:|---:|
| square 1:1 | 95 | 0.95x |
| wide 16:9 | 35 | 1.05x |
| landscape 4:3 | 9 | 1.56x |
| portrait 4:5 | 6 | - |
| tall 9:16+ | 2 | - |

**Exemplars**

| | Company | |
|---|---|---|
| fullest funnel | **Abridge** | 37% of posts are requirements, consensus or validation |
| best format mix | **Abridge** | 63% carousel or video, 7% link |
| most breakouts | **Wiz** | 10% of posts at 3x their own median |

---

## saas x enterprise x scaled

**184 posts, 4 companies:** Databricks, Snowflake, UiPath, Veeva Systems

| TOFU | MOFU | BOFU | non-buying | cadence |
|---:|---:|---:|---:|---:|
| 33% | 10% | 26% | 32% | 11.2 posts/week |

**What it publishes**

| Job | n | Share | Engagement |
|---|---:|---:|---:|
| `exploration` | 43 | 23% | 0.94x |
| `validation` | 39 | 21% | 0.92x |
| `event` | 29 | 16% | 1.00x |
| `product-news` | 25 | 14% | 1.65x |
| `problem` | 18 | 10% | 0.63x |
| `selection` | 10 | 5% | 2.32x |
| `consensus` | 8 | 4% | 1.21x |
| `requirements` | 8 | 4% | 0.67x |
| `culture` | 2 | 1% | - |
| `recruitment` | 2 | 1% | - |

**Format**

| Format | n | Share | Engagement |
|---|---:|---:|---:|
| video | 76 | 41% | 1.05x |
| image | 57 | 31% | 1.11x |
| link | 38 | 21% | 0.71x |
| text | 10 | 5% | 0.92x |
| multi-image | 3 | 2% | - |

**Shapes that recur in this cell** (8 posts or more)

| Job | Format | Opening | n | Engagement |
|---|---|---|---:|---:|
| `product-news` | video | declarative | 17 | 1.68x |
| `validation` | video | declarative | 16 | 1.01x |
| `validation` | image | declarative | 9 | 0.94x |
| `exploration` | image | declarative | 11 | 0.92x |
| `exploration` | video | declarative | 13 | 0.89x |
| `event` | video | declarative | 8 | 0.61x |

**Design: aspect ratio of image posts**

| Shape | n | Engagement |
|---|---:|---:|
| square 1:1 | 33 | 1.06x |
| wide 16:9 | 24 | 1.11x |
| landscape 4:3 | 2 | - |
| portrait 4:5 | 1 | - |

**Exemplars**

| | Company | |
|---|---|---|
| fullest funnel | **Veeva Systems** | 52% of posts are requirements, consensus or validation |
| best format mix | **Veeva Systems** | 48% carousel or video, 8% link |
| most breakouts | **UiPath** | 16% of posts at 3x their own median |

---

## product x enterprise x growth

**141 posts, 4 companies:** Addverb Technologies, Dexterity, Locus Robotics, RightHand Robotics

| TOFU | MOFU | BOFU | non-buying | cadence |
|---:|---:|---:|---:|---:|
| 16% | 16% | 15% | 54% | 2.2 posts/week |

**What it publishes**

| Job | n | Share | Engagement |
|---|---:|---:|---:|
| `event` | 48 | 34% | 0.76x |
| `validation` | 21 | 15% | 1.64x |
| `culture` | 16 | 11% | 1.19x |
| `exploration` | 15 | 11% | 1.20x |
| `selection` | 15 | 11% | 1.63x |
| `product-news` | 8 | 6% | 1.14x |
| `requirements` | 7 | 5% | - |
| `problem` | 7 | 5% | - |
| `csr` | 4 | 3% | - |

**Publishes no `consensus` at all.**

**Format**

| Format | n | Share | Engagement |
|---|---:|---:|---:|
| image | 54 | 38% | 0.94x |
| video | 46 | 33% | 1.33x |
| multi-image | 19 | 13% | 1.36x |
| text | 11 | 8% | 0.63x |
| link | 11 | 8% | 0.57x |

**Shapes that recur in this cell** (8 posts or more)

| Job | Format | Opening | n | Engagement |
|---|---|---|---:|---:|
| `validation` | video | declarative | 9 | 2.38x |
| `event` | image | declarative | 24 | 0.74x |

**Design: aspect ratio of image posts**

| Shape | n | Engagement |
|---|---:|---:|
| portrait 4:5 | 26 | 0.96x |
| wide 16:9 | 21 | 1.01x |
| landscape 4:3 | 12 | 1.34x |
| square 1:1 | 9 | 0.60x |
| tall 9:16+ | 5 | - |

**Exemplars**

| | Company | |
|---|---|---|
| fullest funnel | **Locus Robotics** | 25% of posts are requirements, consensus or validation |
| best format mix | **Addverb Technologies** | 66% carousel or video, 0% link |
| most breakouts | **RightHand Robotics** | 8% of posts at 3x their own median |

---

## product x enterprise x scaled

**141 posts, 3 companies:** ABB Robotics, Rockwell Automation, Zebra Technologies

| TOFU | MOFU | BOFU | non-buying | cadence |
|---:|---:|---:|---:|---:|
| 38% | 12% | 15% | 35% | 10.0 posts/week |

**What it publishes**

| Job | n | Share | Engagement |
|---|---:|---:|---:|
| `exploration` | 40 | 28% | 0.99x |
| `event` | 35 | 25% | 1.08x |
| `selection` | 15 | 11% | 1.53x |
| `validation` | 14 | 10% | 0.86x |
| `problem` | 13 | 9% | 0.79x |
| `consensus` | 7 | 5% | - |
| `culture` | 5 | 4% | - |
| `product-news` | 5 | 4% | - |
| `csr` | 4 | 3% | - |
| `requirements` | 2 | 1% | - |
| `unclear` | 1 | 1% | - |

**Format**

| Format | n | Share | Engagement |
|---|---:|---:|---:|
| video | 86 | 61% | 1.03x |
| text | 21 | 15% | 0.79x |
| link | 19 | 13% | 0.94x |
| image | 13 | 9% | 1.28x |
| multi-image | 2 | 1% | - |

**Shapes that recur in this cell** (8 posts or more)

| Job | Format | Opening | n | Engagement |
|---|---|---|---:|---:|
| `event` | video | declarative | 15 | 1.06x |
| `exploration` | video | declarative | 20 | 1.03x |

**Design: aspect ratio of image posts**

| Shape | n | Engagement |
|---|---:|---:|
| wide 16:9 | 7 | - |
| square 1:1 | 4 | - |
| tall 9:16+ | 2 | - |
| portrait 4:5 | 2 | - |

**Exemplars**

| | Company | |
|---|---|---|
| fullest funnel | **ABB Robotics** | 28% of posts are requirements, consensus or validation |
| best format mix | **Zebra Technologies** | 64% carousel or video, 0% link |
| most breakouts | **Zebra Technologies** | 7% of posts at 3x their own median |

---

## service x slg x growth

**173 posts, 4 companies:** Directive Consulting, Netguru, New Breed, Refine Labs

| TOFU | MOFU | BOFU | non-buying | cadence |
|---:|---:|---:|---:|---:|
| 51% | 8% | 7% | 33% | 2.4 posts/week |

**What it publishes**

| Job | n | Share | Engagement |
|---|---:|---:|---:|
| `exploration` | 58 | 34% | 0.86x |
| `problem` | 30 | 17% | 0.82x |
| `event` | 28 | 16% | 1.22x |
| `culture` | 22 | 13% | 1.96x |
| `validation` | 11 | 6% | 1.00x |
| `selection` | 8 | 5% | 1.69x |
| `recruitment` | 6 | 3% | - |
| `requirements` | 5 | 3% | - |
| `unclear` | 3 | 2% | - |
| `csr` | 1 | 1% | - |
| `consensus` | 1 | 1% | - |

**Format**

| Format | n | Share | Engagement |
|---|---:|---:|---:|
| video | 62 | 36% | 0.89x |
| image | 41 | 24% | 1.15x |
| link | 25 | 14% | 0.83x |
| multi-image | 23 | 13% | 1.77x |
| text | 22 | 13% | 0.86x |

**Shapes that recur in this cell** (8 posts or more)

| Job | Format | Opening | n | Engagement |
|---|---|---|---:|---:|
| `culture` | multi-image | we | 10 | 1.96x |
| `event` | image | declarative | 10 | 1.12x |
| `exploration` | video | declarative | 12 | 0.85x |
| `exploration` | text | declarative | 9 | 0.71x |
| `problem` | video | declarative | 11 | 0.69x |

**Design: aspect ratio of image posts**

| Shape | n | Engagement |
|---|---:|---:|
| square 1:1 | 30 | 1.37x |
| wide 16:9 | 19 | 1.50x |
| portrait 4:5 | 11 | 1.00x |
| tall 9:16+ | 2 | - |
| landscape 4:3 | 2 | - |

**Exemplars**

| | Company | |
|---|---|---|
| fullest funnel | **New Breed** | 21% of posts are requirements, consensus or validation |
| best format mix | **Directive Consulting** | 75% carousel or video, 0% link |
| most breakouts | **Netguru** | 22% of posts at 3x their own median |

---

## service x enterprise x scaled

**190 posts, 4 companies:** Accenture Song, Flexport, Slalom, Thoughtworks

| TOFU | MOFU | BOFU | non-buying | cadence |
|---:|---:|---:|---:|---:|
| 49% | 14% | 10% | 26% | 5.0 posts/week |

**What it publishes**

| Job | n | Share | Engagement |
|---|---:|---:|---:|
| `exploration` | 60 | 32% | 0.82x |
| `problem` | 34 | 18% | 0.78x |
| `event` | 26 | 14% | 1.02x |
| `selection` | 22 | 12% | 1.71x |
| `validation` | 17 | 9% | 1.00x |
| `culture` | 15 | 8% | 4.16x |
| `requirements` | 5 | 3% | - |
| `product-news` | 4 | 2% | - |
| `csr` | 4 | 2% | - |
| `consensus` | 2 | 1% | - |
| `recruitment` | 1 | 1% | - |

**Format**

| Format | n | Share | Engagement |
|---|---:|---:|---:|
| image | 54 | 28% | 0.87x |
| link | 53 | 28% | 0.75x |
| video | 47 | 25% | 1.24x |
| multi-image | 20 | 11% | 2.59x |
| text | 16 | 8% | 0.70x |

**Shapes that recur in this cell** (8 posts or more)

| Job | Format | Opening | n | Engagement |
|---|---|---|---:|---:|
| `exploration` | video | declarative | 13 | 1.00x |
| `event` | image | declarative | 10 | 0.79x |
| `exploration` | link | declarative | 21 | 0.75x |
| `exploration` | image | declarative | 8 | 0.69x |
| `problem` | link | declarative | 8 | 0.66x |

**Design: aspect ratio of image posts**

| Shape | n | Engagement |
|---|---:|---:|
| portrait 4:5 | 22 | 0.78x |
| square 1:1 | 22 | 0.79x |
| wide 16:9 | 21 | 2.46x |
| landscape 4:3 | 9 | 2.43x |

**Exemplars**

| | Company | |
|---|---|---|
| fullest funnel | **Accenture Song** | 17% of posts are requirements, consensus or validation |
| best format mix | **Thoughtworks** | 42% carousel or video, 20% link |
| most breakouts | **Flexport** | 23% of posts at 3x their own median |

