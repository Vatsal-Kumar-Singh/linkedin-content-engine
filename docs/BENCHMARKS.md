# What B2B companies actually publish on LinkedIn

A measured reference for setting a content split, choosing formats, and shaping a calendar — cut
by **what you sell**, **how you sell it**, **who buys**, and **how big you are**.

**2,020 original posts from 46 companies, every one read and labelled by hand.** Method,
sample and limits are at the bottom; read them before quoting any number.

---

## The finding that should change your calendar

**The content that earns reach and the content that does commercial work are close to
opposites.** Engagement is measured against each company's own median, so 1.59 means "59% above
what that company normally gets":

| What the post does | Share of all posts | Engagement | Doubles the median |
|---|---:|---:|---:|
| `selection` — awards, funding, customer counts, partnerships | 7.7% | **1.59x** | 43% |
| `culture` — team, celebration, humour | 8.7% | **1.32x** | 36% |
| `product-news` — launches and releases | 13.1% | 1.20x | 28% |
| `recruitment` | 3.1% | 1.07x | 21% |
| `event` — booths, webinars, conferences | 18.7% | 1.00x | 13% |
| `validation` — named customer, measured result | 9.5% | 1.00x | 17% |
| `exploration` — how a category or approach works | 21.4% | 0.95x | 11% |
| `consensus` — ROI, security, compliance, procurement | 2.2% | **0.80x** | 7% |
| `problem` — naming a cost the reader is already paying | 9.9% | **0.77x** | 6% |
| `requirements` — comparisons, trade-offs, buyer's guides | 2.9% | **0.68x** | 5% |

Read the bottom three rows again. **Problem framing, buyer's guides and business-case content are
the three worst-performing categories in the corpus**, and they are the three that a buyer in an
active evaluation actually needs. Meanwhile the top of the table — awards, culture, launches — is
mostly content about the company, addressed to people who already follow it.

This is not an argument for publishing less of the bottom three. It is an argument for **never
letting engagement pick your content split**, because a feed-optimised calendar converges on
trophies and team photos. It is also why this repository scores Gate, Lift and Fit
[separately and refuses to blend them](decision/ARCHITECTURE.md): Lift would rank these ten rows
almost perfectly upside down from Fit.

**`requirements` and `consensus` together are 5.1% of everything published.** Whatever else the
grid below says, that is the gap in this industry.

---

## The split, by what you sell

Percentages are of all original posts. "non-buying" is recruitment, culture, event, product news
and CSR combined — real work, just not buying work.

| Offering | n | TOFU | MOFU | BOFU | non-buying |
|---|---:|---:|---:|---:|---:|
| **service** | 269 | **49%** | 13% | 8% | **29%** |
| **saas** | 1089 | 29% | 8% | 11% | 50% |
| **product** | 662 | 27% | 14% | 14% | 44% |

**Service firms sell with ideas and almost nothing else.** Half of everything a consultancy or
agency publishes is problem-framing or category education, and they publish the least non-buying
content of anyone. When the product is judgement, demonstrating judgement *is* the marketing.

**Product companies carry the most BOFU.** Hardware, robotics and devices publish proof at twice
the rate of service firms: a named customer, a measured before-and-after, a deployment. A physical
capital purchase is defended internally with evidence, and the page supplies it.

**SaaS publishes the most non-buying content of the three** — half of it — driven by events and
product news.

## The split, by how you sell

| Motion | n | TOFU | MOFU | BOFU | non-buying |
|---|---:|---:|---:|---:|---:|
| **enterprise** | 763 | 35% | 15% | **15%** | **33%** |
| **slg** | 516 | 37% | 9% | 11% | 42% |
| **pls** | 226 | 29% | 7% | 14% | 50% |
| **plg** | 515 | 21% | 7% | **6%** | **63%** |

**Enterprise motion has the only balanced funnel in the dataset.** It is also the only cohort
where MOFU and BOFU each clear 15%. Long cycles with committees force the content that serves
committees.

**PLG pages barely sell at all.** Two thirds of a product-led company's posts do no buying job:
they announce releases, run community events and post culture. That is coherent — in PLG the
product does the selling and the page does awareness and retention — but it means **a PLG company
copying PLG benchmarks will never build the evaluation content a committee needs the day it
starts selling upmarket.** The shift from PLG to PLS to enterprise is visible in this table as a
BOFU climb from 6% to 14% to 15%.

## The split, by who buys

This is the sharpest single cut in the whole corpus:

| Buyer | n | TOFU | MOFU | BOFU | non-buying |
|---|---:|---:|---:|---:|---:|
| **procurement** | 136 | 35% | 15% | **17%** | **32%** |
| **exec** | 804 | 35% | 14% | 13% | 36% |
| **manager** | 456 | 36% | 8% | 13% | 43% |
| **practitioner** | 624 | **22%** | 7% | **8%** | **60%** |

**Who signs matters more than what you sell.** A page aimed at practitioners is 60% non-buying
content; a page aimed at procurement is 32%. The gap between those two numbers is bigger than the
gap between any two offerings or any two stages. If your profile declares only one axis, declare
this one.

## The split, by stage

| Stage | n | TOFU | MOFU | BOFU | non-buying |
|---|---:|---:|---:|---:|---:|
| early | 282 | 29% | 14% | 8% | 43% |
| growth | 821 | 27% | 10% | 10% | 52% |
| scaled | 917 | **36%** | 9% | **15%** | 39% |

**Early-stage companies have the least BOFU (8%)** — they have the fewest customers to name, which
is circular and self-reinforcing: no proof, so no proof content, so a harder time earning the
next customer. The one reliably available substitute is the company's own deployment or an
early design partner, which is exactly what the early-stage robotics companies in this sample do.

**Scaled companies swing hardest to TOFU** and carry the most BOFU. They have both the audience
to justify category-level argument and the case studies to prove it.

## Every cell

| Cell | n | TOFU | MOFU | BOFU | non-buying | The shape in one line |
|---|---:|---:|---:|---:|---:|---|
| service x slg | 123 | **50%** | 9% | **2%** | 37% | Pure argument. Almost no proof published at all |
| service x enterprise | 146 | **49%** | 16% | 13% | **22%** | The most buying-dense cell in the dataset |
| saas x slg | 253 | 36% | 9% | 6% | 48% | Category argument plus a heavy event calendar |
| saas x enterprise | 230 | 33% | 13% | **20%** | 33% | The most BOFU-heavy SaaS. Committees demand proof |
| product x enterprise | 387 | 30% | **17%** | 13% | 38% | Spec and comparison content. Engineers are evaluating |
| product x slg | 140 | 29% | 8% | **29%** | 35% | **Proof is the product.** Highest BOFU anywhere |
| saas x pls | 226 | 29% | 7% | 14% | 50% | Self-serve front door, enterprise back end |
| saas x plg | 380 | 23% | 4% | 7% | **61%** | Release notes and community |
| product x plg | 135 | **15%** | 13% | **2%** | **69%** | Effectively a consumer brand page |

`service x plg` is structurally empty and is [documented as such](../research/sample-frame.yaml) —
you cannot self-serve a consultancy.

---

## Format: what gets used, and what the feed rewards

| Format | Share | Engagement | Doubles the median |
|---|---:|---:|---:|
| **multi-image / carousel** | **7.1%** | **1.58x** | **38%** |
| video | 33.6% | 1.13x | 23% |
| single image | 30.5% | 1.00x | 20% |
| text only | 14.9% | 0.78x | 9% |
| link post | 13.9% | **0.75x** | 6% |

**The best-performing format is the least used, by a factor of four.** Multi-image posts earn 58%
above their company's median and more than double it 38% of the time, and they are 7% of what gets
published. **Ten of the 46 companies published none at all.** The companies that do use it are not
the ones you would guess: Addverb (34% of posts), Directive Consulting (29%), Zoho (28%),
Prusa (21%).

And where carousels *are* used, they are used for the wrong thing:

| Multi-image used for | n | Engagement |
|---|---:|---:|
| culture | 41 | **2.38x** |
| selection | 16 | 1.71x |
| event | 36 | 1.55x |
| validation | 11 | 1.38x |
| exploration | 15 | 1.36x |

**The single largest exploitable gap in this dataset**: the format that outperforms everything is
being spent on team photos. `requirements` — comparisons and buyer's guides, the worst-performing
category — is published as a **link post 34% of the time** and as a carousel **2%** of the time.
The comparison table that belongs in a carousel is being posted as a link to a blog.

**Link posts are the worst format in the corpus** and they carry the most decision-stage content.

### Which format each job is published in

| Job | text | link | image | multi | video |
|---|---:|---:|---:|---:|---:|
| validation | 5% | 15% | 22% | 6% | **52%** |
| product-news | 9% | 12% | 27% | 5% | **47%** |
| exploration | 20% | 11% | 25% | 3% | 40% |
| problem | 22% | 19% | 25% | **2%** | 32% |
| **requirements** | 9% | **34%** | 36% | **2%** | 19% |
| **consensus** | 20% | **31%** | 27% | **2%** | 20% |
| selection | 14% | 12% | **43%** | 10% | 21% |
| culture | 21% | 4% | 35% | **23%** | 17% |
| event | 7% | 15% | 40% | 10% | 29% |
| recruitment | **40%** | 23% | 27% | 2% | 8% |

### Format mix by offering and motion

| | text | link | image | multi | video |
|---|---:|---:|---:|---:|---:|
| product | 14% | 9% | 32% | 8% | 37% |
| saas | 17% | 15% | 31% | 5% | 32% |
| service | 10% | **22%** | 24% | **13%** | 32% |
| enterprise | 10% | 15% | 33% | 6% | 36% |
| plg | **21%** | 12% | 29% | 8% | 30% |
| pls | 15% | 20% | 24% | 8% | 32% |
| slg | 16% | 11% | 31% | 8% | 34% |

Service firms lean hardest on links — they are driving to long-form thinking — and also use
carousels most. Product companies are the most video-heavy (37%).

## Length barely matters

| Words | Share | Engagement |
|---|---:|---:|
| 0-29 | 16.4% | 0.91x |
| 30-59 | 26.9% | 0.97x |
| 60-99 | 29.0% | 1.00x |
| 100-159 | 19.4% | 1.06x |
| 160+ | 8.3% | 1.08x |

**The spread from shortest to longest is 0.91 to 1.08.** Against a format spread of 0.75 to 1.58,
length is close to noise. Longer is very slightly better, and anyone optimising word count before
they have fixed their format mix is working on the wrong variable.

## Volume

Every cohort publishes at roughly the same rate — a median of **45 to 48 original posts** in the
window, with no meaningful difference by offering, motion or stage. **Cadence is not where these
companies differentiate.** What varies is what goes in the slots, not how many slots there are.

## When the page is not the channel

Five companies reshare more than 40% of what appears on their page, and three of them reshare so
much that they have almost no original page content at all:

| Company | Reshared | Cell |
|---|---:|---|
| Kalungi | 100% (16 of 16) | service x slg, early |
| PostHog | 77% (37 of 48) | saas x pls, growth |
| Dub | 72% (36 of 50) | saas x plg, early |
| Notion | 47% (23 of 49) | saas x plg, scaled |
| Dexterity | 46% (19 of 41) | product x enterprise, growth |

These are founder-led companies whose page is an **amplifier for named people**, not a publisher.
That is a deliberate channel design and this engine models it directly as
[`kind: person` versus `kind: organisation`](decision/RESEARCH-channel-split.md). It also means
**a page-level benchmark is the wrong benchmark for these companies** — measure the founder's
profile instead. Kalungi, PostHog and Dub fall below this study's 20-original threshold for that
reason and are excluded from every percentage above.

---

## Using this

**1. Find your row, then look at what it is missing.** The tables describe what companies like
yours *do*, not what works. `requirements` and `consensus` are 5.1% of the entire corpus, so
almost every row understates them. Treat the grid as a baseline to deviate from deliberately.

**2. Set the split from Fit, never from Lift.** The ten-row table at the top is the reason. If you
let engagement choose, you will publish awards and team photos, because that is what the feed
pays for.

**3. Fix format before you touch anything else.** It is the largest measured effect. Specifically:
move comparison and business-case content out of link posts and into carousels. That is a
0.68x-to-1.58x move on the two categories that matter most at the decision stage, and almost
nobody in this sample is doing it.

**4. Declare your buyer.** It splits behaviour harder than offering, motion or stage. A profile
that declares `buyer: practitioner` and one that declares `buyer: procurement` should not get the
same calendar.

**5. Check whether the page is even your channel.** If your founder outperforms the page, the page
is an amplifier and the benchmarks above do not apply to it.

`engine/decision/company_type.py` turns the offering and motion declarations into constraints and
cautions. **It deliberately returns no score multipliers** — the numbers above are a description
of an industry, and an industry is not a target.

---

## Method, and what it cannot tell you

**Sample.** 49 companies chosen to populate an offering x motion x stage grid, defined in
[`research/sample-frame.yaml`](../research/sample-frame.yaml) with a stated reason for every
company. 46 cleared the threshold. Pulled September 2026 via Apify, up to 50 posts each,
2,298 posts. Raw JSON is kept so classification can be re-run without paying to scrape again.

**Labelling.** Every post was **read** and assigned exactly one of twelve labels defined in
[`research/CLASSIFICATION-PROTOCOL.md`](../research/CLASSIFICATION-PROTOCOL.md). An earlier
regex pass left 95% of the corpus unclassified and was abandoned: buying jobs are semantic, and
patterns only find the posts that announce themselves, which biases the result toward companies
with a house style of labelling their own content. **1.6% of posts ended as `unclear`**, against a
15% ceiling above which this project treats a distribution as a statement about the instrument
rather than the corpus.

**Thresholds.** A company with fewer than 20 labelled originals is reported by name and excluded
from every percentage. Reposts (`header.linkedinUrl`) are excluded from the distributions and
reported separately as a channel finding.

**Engagement is normalised per company, always.** Every post is scored against its own company's
median, so the output is a ratio and comparisons are about post shape rather than audience size.

### Four things this cannot tell you

**Engagement is not pipeline.** Reactions, comments and shares are the only outcome signal in
this data. Nothing here observed a deal. The top table is a reach ranking, and the whole point of
the first section is that reach and commercial value diverge sharply.

**A carousel cannot be told apart from a photo album.** Both arrive as `postImages` with several
entries. Everything said about "multi-image" covers both, and a claim specifically about document
carousels is not supported.

**One window, no seasonality.** These are recent posts pulled at one moment. A company mid-launch
or mid-conference-season is over-represented on those categories.

**One reader.** Every label is one person's judgement applied consistently. The protocol exists so
a second reader can label the same batches independently and the two files can be compared post by
post — which is the only way to find out whether these labels are stable or one reader's opinion.
That pass has not been run.

### Reproducing it

```bash
export APIFY_TOKENS=tok1,tok2      # never committed; this repo is public
export FIRECRAWL_API_KEY=fc-...
python research/scrape_sample.py --all --batch 5
python research/resolve_slugs.py --write     # anything that came back empty
python research/make_batches.py              # then read and label into research/labels/
python research/classify_posts.py --dump research/findings.json
python research/analyse_format.py research/findings.json
```

**An empty dataset is what a wrong slug and an exhausted actor quota both look like**, and neither
is the finding "they post nothing". 14 of the first 47 companies came back empty and every one was
a bad slug or a flaky run: Retool is `tryretool`, Outreach is `outreach-saas`, and ABB Robotics
publishes from a LinkedIn **showcase** page that `/company/` does not reach. Resolve before
concluding.
