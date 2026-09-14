# What B2B companies actually publish on LinkedIn

A measured reference for setting a content split, choosing formats, shaping a calendar and
briefing a designer — cut by **what you sell**, **how you sell it**, **who buys**, **how big you
are**, and **which industry you sell into**.

**3,141 original posts from 77 company pages, every one read and labelled by hand** — of which
**3,114 across 73 pages** clear the 20-original threshold and carry every number here. Plus
**1,289 posts from 33 named people** paired to those same companies. An audit removed 506 posts
(10.1%) that could not answer the question asked of them — the reasons are in
[Pruning](#what-was-removed-from-the-corpus-and-what-was-deliberately-kept).

**This was measured in two rounds, and the second one matters for how you read the first.** Round
one covered 49 companies across offering, motion and stage. Those 49 turned out to be, without
anybody choosing it, almost entirely developer tooling, robotics, industrial hardware, revenue
software and consulting — so every conclusion was a conclusion about *those* industries and
nothing said so. Round two added 28 companies across eight absent verticals (fintech, security,
supply chain, legal, HR, healthcare, climate, construction) and an `industry` axis to carry them.
Several headline numbers moved. Where a round-one claim did not survive, it is marked rather than
quietly replaced.

Method, sample and limits are at the bottom; read them before quoting any number.

---

## The finding that should change your calendar

**The content that earns reach and the content that does commercial work are close to
opposites.** Engagement is measured against each company's own median, so 1.59 means "59% above
what that company normally gets":

| What the post does | Share of all posts | Engagement | Doubles the median |
|---|---:|---:|---:|
| `selection` — awards, funding, customer counts, partnerships | 7.1% | **1.84x** | 48% |
| `culture` — team, celebration, humour | 11.0% | **1.35x** | 32% |
| `product-news` — launches and releases | 12.4% | 1.23x | 30% |
| `recruitment` | 3.0% | 1.00x | 18% |
| `event` — booths, webinars, conferences | 20.1% | 0.98x | 13% |
| `validation` — named customer, measured result | 10.1% | 0.97x | 15% |
| `exploration` — how a category or approach works | 22.2% | 0.92x | 11% |
| `csr` | 1.2% | 0.89x | 13% |
| `consensus` — ROI, security, compliance, procurement | 1.5% | **0.82x** | 6% |
| `problem` — naming a cost the reader is already paying | 7.4% | **0.75x** | 6% |
| `requirements` — comparisons, trade-offs, buyer's guides | 2.4% | **0.70x** | 4% |

Read the bottom three rows again. **Problem framing, buyer's guides and business-case content are
the three worst-performing categories in the corpus**, and they are the three that a buyer in an
active evaluation actually needs. Meanwhile the top of the table — awards, culture, launches — is
mostly content about the company, addressed to people who already follow it.

This is not an argument for publishing less of the bottom three. It is an argument for **never
letting engagement pick your content split**, because a feed-optimised calendar converges on
trophies and team photos. It is also why this repository scores Gate, Lift and Fit
[separately and refuses to blend them](decision/ARCHITECTURE.md): Lift would rank these ten rows
almost perfectly upside down from Fit.

**`requirements` and `consensus` together are 3.9% of everything published**, down from 5.0%
when the corpus was 46 companies. Adding 28 companies across eight new verticals did not find the
missing decision-stage content; it found more companies not publishing it. Whatever else the grid
below says, that is the gap in this industry — and it is scarce enough that the 0.70x and 0.82x
above still cannot be confirmed company by company. See
[the second pass](#the-engagement-ranking-is-only-partly-universal).

---

## The split, by what you sell

Percentages are of all original posts. "non-buying" is recruitment, culture, event, product news
and CSR combined — real work, just not buying work.

| Offering | n | TOFU | MOFU | BOFU | non-buying |
|---|---:|---:|---:|---:|---:|
| **service** | 393 | **47%** | 10% | 9% | **34%** |
| **saas** | 2024 | 28% | 8% | 11% | 51% |
| **product** | 697 | 25% | 14% | 14% | 45% |

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
| **enterprise** | 973 | 34% | 14% | **15%** | **37%** |
| **slg** | 1018 | 31% | 8% | 12% | 47% |
| **pls** | 500 | 30% | 8% | 12% | 49% |
| **plg** | 623 | 20% | 6% | **5%** | **66%** |

**Enterprise motion has the only balanced funnel in the dataset.** It is also the only cohort
where MOFU and BOFU each clear 15%. Long cycles with committees force the content that serves
committees.

**PLG pages barely sell at all.** Two thirds of a product-led company's posts do no buying job:
they announce releases, run community events and post culture. That is coherent — in PLG the
product does the selling and the page does awareness and retention — but it means **a PLG company
copying PLG benchmarks will never build the evaluation content a committee needs the day it
starts selling upmarket.** The shift from PLG to PLS to enterprise is visible in this table as a
BOFU climb from 5% to 12% to 15%.

*(Round two more than doubled the PLS cell, from 226 posts to 500, by adding Stripe, Vanta,
1Password, Clio, Deel, Buildertrend and Bluebeam. The shape held.)*

## The split, by who buys

This is the sharpest single cut in the whole corpus:

| Buyer | n | TOFU | MOFU | BOFU | non-buying |
|---|---:|---:|---:|---:|---:|
| **procurement** | 128 | 31% | **16%** | **18%** | **34%** |
| **exec** | 1356 | 33% | 11% | 12% | 42% |
| **manager** | 804 | 30% | 7% | 13% | 49% |
| **practitioner** | 826 | **24%** | 8% | **8%** | **58%** |

**Who signs matters more than what you sell.** A page aimed at practitioners is 58% non-buying
content; a page aimed at procurement is 34%. The gap between those two numbers is bigger than the
gap between any two offerings or any two stages. If your profile declares only one axis, declare
this one.

**Procurement is three companies and stays a signal rather than a result.** It is the only level
of any axis in this study that never reached the three-company floor comfortably, and round two
did not fix it: the verticals added buy through legal and security review rather than through a
procurement function that owns the decision.

## The split, by stage

| Stage | n | TOFU | MOFU | BOFU | non-buying |
|---|---:|---:|---:|---:|---:|
| early | 402 | 24% | 11% | 9% | 53% |
| growth | 1411 | 29% | 9% | 10% | 50% |
| scaled | 1301 | **32%** | 10% | **14%** | 43% |

**Early-stage companies have the least BOFU (9%)** — they have the fewest customers to name, which
is circular and self-reinforcing: no proof, so no proof content, so a harder time earning the
next customer. The one reliably available substitute is the company's own deployment or an
early design partner, which is exactly what the early-stage robotics companies in this sample do.

**Scaled companies swing hardest to TOFU** and carry the most BOFU. They have both the audience
to justify category-level argument and the case studies to prove it.

## Every cell

| Cell | n | TOFU | MOFU | BOFU | non-buying | The shape in one line |
|---|---:|---:|---:|---:|---:|---|
| service x enterprise | 190 | **49%** | 14% | 10% | **26%** | The most buying-dense cell in the dataset |
| service x slg | 203 | **44%** | 6% | 7% | 41% | Pure argument. Very little proof published |
| saas x enterprise | 408 | 32% | 11% | **18%** | 39% | The most BOFU-heavy SaaS. Committees demand proof |
| saas x pls | 500 | 30% | 8% | 12% | 49% | Self-serve front door, enterprise back end |
| product x enterprise | 375 | 29% | **17%** | 14% | 39% | Spec and comparison content. Engineers are evaluating |
| saas x slg | 628 | 29% | 9% | 10% | 51% | Category argument plus a heavy event calendar |
| product x slg | 187 | 26% | 9% | **25%** | 41% | **Proof is the product.** Highest BOFU anywhere |
| saas x plg | 488 | 22% | 4% | 6% | **65%** | Release notes and community |
| product x plg | 135 | **15%** | 13% | **2%** | **69%** | Effectively a consumer brand page |

`service x plg` is structurally empty and is [documented as such](../research/sample-frame.yaml) —
you cannot self-serve a consultancy.

**These nine cells are offering x motion. The third axis is cut separately in
[`CELLS.md`](CELLS.md)**, which reports offering x motion x stage — how a company actually
identifies itself — with named exemplars, recurring post shapes and an aspect-ratio profile per
cell. Thirteen of the 36 three-axis cells currently clear the three-company floor; the rest are
listed there with what each still needs.

---

## The split, by industry

**This axis did not exist in round one, and its absence was the biggest hole in this study.** The
first 49 companies were all developer tooling, robotics, industrial hardware, revenue software or
consulting. Round two added 28 companies across eight verticals chosen for being missing rather
than for being interesting. A vertical needs three companies before it gets a row.

| Industry | n | TOFU | MOFU | BOFU | non-buying |
|---|---:|---:|---:|---:|---:|
| **prof-services** | 349 | **46%** | 10% | 10% | 33% |
| **revops-martech** | 206 | 38% | 11% | **6%** | 44% |
| supply-chain | 139 | 37% | 13% | **6%** | 43% |
| climate-energy | 137 | 36% | 10% | 12% | 42% |
| data-ai | 144 | 36% | 12% | **19%** | **33%** |
| cybersecurity | 170 | 34% | 8% | **5%** | 50% |
| work-productivity | 252 | 31% | **4%** | 9% | 50% |
| robotics-automation | 329 | 29% | **19%** | 15% | 35% |
| hr-people | 156 | 24% | 6% | 12% | 55% |
| construction-proptech | 140 | 24% | 7% | 16% | 54% |
| industrial-hardware | 321 | 22% | 10% | 14% | 53% |
| **healthcare-lifesci** | 166 | 22% | 10% | **24%** | 43% |
| fintech-payments | 125 | 21% | 7% | 9% | 58% |
| dev-infra | 277 | **19%** | **5%** | 9% | **68%** |
| **legal-compliance** | 130 | **12%** | **5%** | 8% | **73%** |

`business-suite` has two companies and is reported, not counted.

**The spread by industry is wider than the spread by anything else measured.** TOFU runs from 12%
to 46% — a range no offering, motion, stage or buyer cut comes close to. **Industry is the axis
this study was missing, and it is now the one with the most signal in it.**

**Healthcare and life sciences publish the most proof of any vertical, by a distance.** 24% BOFU
against a corpus average of 11%. When a claim has to survive a regulator, a named deployment with
a measured result is the only safe thing to say — and the page ends up more useful to a buyer than
almost anyone else's.

**Security publishes the least proof of any vertical: 5% BOFU.** That is the finding most worth
arguing with. Security vendors publish prolifically — original threat research, vulnerability
disclosures, conference programmes — and almost none of it is a named customer with a measured
outcome. The category talks about attacks and rarely about what the product did about one at a
named company. `revops-martech` and `supply-chain` sit at the same 6%, which is the same shape:
sell advice, prove little.

**Legal and compliance is the strangest row in the study** and worth reading twice. 73% non-buying,
12% TOFU, the lowest of both. It is driven by two things this corpus had not seen before: an
extremely heavy event calendar, and **vendors running job boards for their own audience** — Juro
posted other companies' legal vacancies weekly, which is a quarter of its feed. It is real
audience-building and it does no buying work at all.

**Developer infrastructure is 68% non-buying** — release notes and community, with 19% TOFU. It is
the PLG shape in its purest form and it is the shape most content advice is unconsciously written
about, because it is the corner of B2B that writes the most about content.

**Robotics has the most MOFU of any vertical (19%).** Long capex cycles with engineering review
produce comparison and specification content that nobody else publishes.

---


## Format: what gets used, and what the feed rewards

| Format | Share | Engagement | Doubles the median |
|---|---:|---:|---:|
| **multi-image / carousel** | **7.9%** | **1.61x** | **37%** |
| video | 33.4% | 1.10x | 22% |
| single image | 33.1% | 1.00x | 19% |
| text only | 12.4% | 0.78x | 9% |
| link post | 13.2% | **0.78x** | 8% |

**The best-performing format is the least used, by a factor of four.** Multi-image posts earn 61%
above their company's median and more than double it 37% of the time, and they are 8% of what gets
published. **Fourteen of the 73 companies published none at all.** The companies that do use it
are not the ones you would guess: Addverb (34% of posts), Mercury (30%), Directive Consulting
(29%), Zoho (28%), Wiz (24%), Buildertrend (23%).

This held across a doubled corpus and eight new verticals, which is more than can be said for
several other findings on this page.

And where carousels *are* used, they are used for the wrong thing:

| Multi-image used for | n | Engagement |
|---|---:|---:|
| culture | 73 | **2.10x** |
| selection | 19 | 1.83x |
| event | 80 | 1.60x |
| csr | 9 | 1.53x |
| validation | 12 | 1.36x |
| exploration | 29 | 1.36x |

**The single largest exploitable gap in this dataset**: the format that outperforms everything is
being spent on team photos. `requirements` — comparisons and buyer's guides, the worst-performing
category — is published as a **link post 30% of the time** and as a carousel **3%** of the time.
The comparison table that belongs in a carousel is being posted as a link to a blog.

**Link posts are the worst format in the corpus** and they carry the most decision-stage content.

### Which format each job is published in

| Job | text | link | image | multi | video |
|---|---:|---:|---:|---:|---:|
| product-news | 9% | 11% | 27% | 4% | **49%** |
| validation | 4% | 18% | 28% | 4% | **46%** |
| exploration | 16% | 12% | 29% | 4% | 39% |
| problem | 23% | 18% | 26% | **1%** | 32% |
| **requirements** | 9% | **30%** | 36% | **3%** | 22% |
| **consensus** | 19% | **30%** | 28% | **2%** | 21% |
| selection | 13% | 12% | **48%** | 9% | 19% |
| culture | 15% | 5% | 29% | **21%** | 30% |
| event | 9% | 12% | 42% | 13% | 24% |
| recruitment | 9% | 26% | **48%** | 5% | 13% |
| csr | 13% | 11% | 34% | **24%** | 18% |

### Format mix by offering and motion

| | text | link | image | multi | video |
|---|---:|---:|---:|---:|---:|
| product | 12% | 9% | 32% | 9% | **38%** |
| saas | 13% | 13% | 35% | 7% | 32% |
| service | 11% | **21%** | 26% | **12%** | 30% |
| enterprise | **8%** | 14% | 36% | 7% | 35% |
| plg | **19%** | 11% | 33% | 9% | 28% |
| pls | 15% | 16% | 25% | 8% | 36% |
| slg | 11% | 13% | 34% | 8% | 34% |

Service firms lean hardest on links — they are driving to long-form thinking — and also use
carousels most. Product companies are the most video-heavy (38%).

## Length barely matters

| Words | Share | Engagement |
|---|---:|---:|
| 0-29 | 14.0% | 1.00x |
| 30-59 | 24.8% | 0.97x |
| 60-99 | 30.3% | 1.00x |
| 100-159 | 22.0% | 1.02x |
| 160+ | 8.9% | 1.08x |

**The spread from shortest to longest is 0.97 to 1.08.** Against a format spread of 0.78 to 1.61,
length is not close to noise, it *is* noise. Doubling the corpus flattened this further: the
0.91x that very short posts earned in round one was a small-sample artefact and is now 1.00x.
Anyone optimising word count before they have fixed their format mix is working on the wrong
variable.

## The person channel: it is not person versus page, it is founder versus everyone else

**1,289 posts from 33 named people, each paired to a company page already in this study** —
same company, same twelve-month window. The pairing is what makes it readable: raw engagement
mostly measures followers, so the only honest comparison is within a company.

At the same company, the named person's median post beat the page's in **23 of 31 pairs (74%)**,
median ratio **1.92x**. But that number hides the finding:

| Who is posting | Pairs | Median vs their own page | Person wins |
|---|---:|---:|---:|
| **founder / CEO** | 19 | **3.17x** | 16 of 19 |
| C-suite | 3 | 1.91x | 2 of 3 |
| individual contributor | 6 | 1.03x | 4 of 6 |
| VP / Head / Director | 3 | 0.77x | 1 of 3 |

**A founder's typical post is worth three of their company page's.** "Get your executives
posting" is not the finding; the effect is concentrated almost entirely in the founder and CEO
seat. Below it the advantage disappears — individual contributors run level with the page and the
three VPs measured came in under it, though three people is a signal to check rather than a result
to plan around.

Veeva Systems is an accidental control: four of its people are in the sample, and they span
**45.86x to 0.25x** against the same page in the same window. Within-company variance dwarfs
every between-company difference measured anywhere in this study.

*(Peter Gassner's 45.86x is the largest ratio here and should be read carefully: Veeva's page
median is 36, which is very low for a company of that size, so the ratio is as much a weak page
as a strong person. Ratios like these are a direction, not a multiple.)*

### Where the person channel matters most

| | Pairs | Median ratio | Person wins |
|---|---:|---:|---:|
| **enterprise motion** | 8 | **3.44x** | 6 |
| plg | 6 | 2.91x | 5 |
| slg | 10 | 2.26x | 8 |
| pls | 7 | 1.01x | 4 |
| saas | 22 | 2.71x | 18 |
| service | 3 | 1.91x | 2 |
| product | 6 | 1.24x | 3 |

**The person channel pays most exactly where committees buy.** Enterprise motion is the highest
ratio measured, which is the empirical version of a rule this engine already carried on judgement
alone: when a buyer is deciding whether they want *these specific people* in their business, an
organisation page cannot answer the question.

### What a person publishes, and how it differs

| | Page | Person | Difference |
|---|---:|---:|---:|
| **says "I" anywhere** | 3.2% | **43.2%** | **+40.0** |
| **text-only posts** | 14.5% | **36.2%** | **+21.7** |
| body 160+ words | 8.3% | 27.9% | +19.6 |
| opens on "I/my" | 0.3% | 8.7% | +8.4 |
| first line 26+ words | 20.9% | 27.3% | +6.4 |
| body 0-29 words | 16.6% | 21.6% | +5.0 |
| says "we" anywhere | 52.9% | 54.1% | +1.3 |
| has hashtags | 23.1% | 20.7% | -2.4 |
| uses emoji | 35.6% | 26.3% | -9.3 |
| **explicit CTA verb** | 20.6% | **7.3%** | **-13.3** |
| body 60-99 words | 29.0% | 14.4% | -14.5 |
| **video** | 34.1% | **16.2%** | **-17.9** |

**These are two different products, not one voice in two registers.**

**People write; pages produce.** Text-only is 36% of a person's feed and 15% of a page's; video
is 34% of a page's and 16% of a person's. A page has a design and video pipeline behind it and uses
it. A person types.

*(An earlier version of this page put person text-only at 40% and video at 13%. Those figures
included person posts going back to 2014, against a page corpus covering twelve months, and
pre-window person posts are 60.5% text-only. The gap is real; it was overstated by measuring
LinkedIn's history rather than the channel's nature.)*

**Length goes bimodal on a person's feed.** People post the very short (21.6% under 30 words) and
the very long (27.9% over 160) and largely skip the middle, where pages cluster. A page's 60-99
word post — the single most common company shape — is 14% of a person's output.

**"I" is the whole difference in voice.** 43% against 3.2%, the starkest single gap in this study.
Note what does *not* change: "we" appears in 53% of both. A person says *I and we*; a page can only
say *we*. **That is the capability the page structurally does not have**, and it is why reposting
a founder's post onto the page is not the same as the page saying it.

**People barely ask for anything.** An explicit CTA appears in 20.6% of page posts and 7.3% of
person posts.

**Pages publish two and a half times as often**: 4.0 posts a week against 1.6. Combined with the
paired ratio, a founder posting weekly is doing roughly the work of a page posting two or three
times — and the founder's cadence is the one companies treat as optional.

**And most of these channels are not running.** Counting only the twelve months the pages cover,
**10 of 43 people (23%) published fewer than 15 posts in a year** and four published fewer than
five. Several are CEOs: Slalom's published once, Veeva's VP of Safety once. A person channel that
posts twice a year is not a channel, and a plan that assumes an executive will post is planning
around the thing that most often does not happen.

### What a founder publishes about: almost exactly what the page publishes about

447 of the person posts were read and labelled with the same twelve labels as the company corpus,
sampled evenly per person so a prolific writer could not carry the distribution. The expectation
going in was that people would publish different *content*. They do not:

| | Page | Person | Difference |
|---|---:|---:|---:|
| TOFU | 30.8% | 33.6% | +2.8 |
| MOFU | 10.5% | 8.3% | -2.2 |
| **BOFU** | 11.7% | **7.6%** | **-4.1** |
| non-buying | 45.6% | 44.5% | -1.1 |
| unclear | 1.4% | 6.0% | +4.7 |

And by seat, the founder row is the one that matters — because it is the page's row:

| Who | n | TOFU | MOFU | BOFU | non-buying |
|---|---:|---:|---:|---:|---:|
| **company page** | 2026 | 31% | 10% | **12%** | 46% |
| **founder / CEO** | 251 | **29%** | **10%** | **12%** | **42%** |
| C-suite | 49 | 63% | 12% | 2% | 22% |
| VP / Head / Director | 58 | 40% | 5% | 7% | 45% |
| individual contributor | 89 | 27% | 3% | **0%** | 63% |

**A founder publishes almost exactly the same mix as their own company page — and outperforms it
three to one.** Put the two halves of this study together and the conclusion is unusually clean:

> The difference between a founder channel and a page channel is **not what gets said. It is how,
> and by whom.**

Same topics, same funnel shape, roughly the same share of non-buying content. What changes is that
the founder writes in first person (43% versus 3.2%), types instead of producing video (40%
text-only versus 15%), runs long or very short rather than medium, asks for almost nothing (7.4%
CTA versus 20.6%), and posts a third as often.

Two qualifications, and both matter:

**BOFU halves on a person's channel — but not on a founder's.** Overall the drop is 11.7% to
7.6%. Split by seat it disappears at the top: **founders carry 12% BOFU, exactly what the page
carries.** The whole of the decline sits below them, at 7% for VPs and **0% for individual
contributors**. So the common advice to keep proof off personal channels is measuring the wrong
people; the founders in this sample publish proof at the page's own rate.

**Below the founder seat the funnel collapses.** Individual contributors published **no BOFU at
all** in the sampled slice and 3% MOFU against 63% non-buying. That is a personal brand, which is
a perfectly good thing to run and is not a sales channel. The VP row is closer but still thin.
**Only the founder seat reproduces the page's shape**, on every one of the four measures.

*(The C-suite row at 63% TOFU is the most buying-dense in the table and also the smallest — 49
posts from 3 people. Treat it as a lead worth checking, not a finding.)*

Where the two differ is inside the non-buying half, and it is one substitution:

| | Page | Founder |
|---|---:|---:|
| culture | 8.9% | **16.7%** |
| event | 18.6% | **10.0%** |
| product news | 13.8% | 12.4% |

**The page runs the event calendar; the founder tells the stories.** Conference booths, webinars
and registration drives are page work — a founder doing that is spending the most valuable channel
a company has on logistics.

### What this means for the channel decision

This repository already models channels as
[`kind: person` or `kind: organisation`](decision/RESEARCH-channel-split.md) and makes the company
declare which. The measurement supports the distinction and sharpens it:

1. **Declare the seat, not just the channel.** A founder channel and a VP channel are not the same
   instrument. The measured difference between them is larger than the difference between a
   person and a page.
2. **Do not pool a person's corpus with a page's** when measuring format lift. Their format mixes
   differ by 25 points on text alone, so a pooled median describes neither.
3. **A person is not a distribution channel for page content — but the topic list transfers.**
   A founder publishes almost the same mix the page does, so the planning grid in this document
   applies to both. What must not transfer is the execution: strip the CTA, drop the video, let it
   run long or very short, and let the writer say "I". A page post with a face on it is what the
   0.77x VP row looks like from the inside.
4. **Do not strip proof out of a founder's channel.** BOFU halves across person channels overall,
   but founders carry exactly the page's 12% — the decline is entirely below that seat, reaching
   0% for individual contributors. Plan proof onto a founder and off an IC.
5. **Measure your own pair before deciding.** 8 of 31 people lost to their own page, including
   three founders. The spread within one company reached 45.86x to 0.25x.
6. **Check the channel is running before planning on it.** Nearly a quarter of the executives in
   this sample published fewer than fifteen posts in a year.

---

## How the text is built

Structural facts counted from the post — no judgement involved, so these are as reliable as the
format numbers. "vs rest" compares posts with the trait against posts without it.

| Trait | Share of posts | Engagement | vs rest |
|---|---:|---:|---:|
| opens on "we" or "our" | 9.4% | **1.19x** | **+19%** |
| quotes somebody | 9.1% | **1.10x** | **+10%** |
| "link in comments" | 4.8% | 1.08x | +8% |
| has a stat in the body | 26.8% | 1.04x | +4% |
| opens on a number | 4.6% | 1.00x | 0% |
| explicit CTA verb | 29.3% | 1.00x | 0% |
| addresses "you" anywhere | 49.3% | 1.00x | -1% |
| uses emoji | 42.9% | 1.00x | 0% |
| has hashtags | 20.2% | 1.00x | 0% |
| bulleted or listed | 11.8% | 0.97x | -3% |
| **opens on "you" or "your"** | 2.8% | **0.89x** | **-11%** |
| **opens on a question** | 6.5% | **0.81x** | **-19%** |

**Five of these contradict advice you will have been given, and the two strongest are about
pronouns.**

**Opening on a question is the worst-performing trait measured.** It is the single most commonly
recommended LinkedIn hook and it runs 19% below posts that do not use it. A question asks the
reader for work before giving them anything.

**Opening on "you" is the second worst, at 0.89x.** Round one measured only whether a post
*contained* "you" anywhere, found it level, and concluded the second-person advice was neutral.
Round two separated the opener from the body, and the opener is negative: 0.89x, and only 10% of
those posts double their company's median. Meanwhile opening on **"we" or "our" runs 1.19x**, the
best-performing trait in the table.

**So the most repeated rule in LinkedIn advice — lead with the reader, never with yourself —
is backwards in this corpus.** Mentioning the reader in the body is fine and does nothing either
way (1.00x across 49% of posts). Opening on them costs you.

**Hashtags do nothing, until you use too many.** Zero, one to three and four to seven all sit at
0.96 to 1.05. **79.8% of this corpus uses none.** The one real signal is at the top: **eight or
more hashtags runs 0.69x**, the worst band of any trait measured. That band is only 0.8% of posts,
so it is a small sample and a large penalty.

**Emoji do nothing either** — 43% of posts use them, at 1.00x.

Two things that do work and are barely used: **quoting somebody** (+10%, in 9.1% of posts) and
putting the **link in the comments** (+8%, in 4.8%). The second is worth noting alongside the
format table, where link posts are the worst format at 0.78x — the penalty is on the link *in the
post*, and moving it to the comments appears to recover part of it. Both effects roughly halved
when the corpus doubled, which is the normal fate of a finding from a small sample; the direction
held, the size did not.

### The first line is the lever

| First line | Share | Engagement |
|---|---:|---:|
| **1-6 words** | 11.1% | **1.19x** |
| 7-14 words | 37.3% | 1.00x |
| 15-25 words | 30.3% | 0.98x |
| 26+ words | 21.2% | 1.00x |

**A very short opening line is worth more than anything else in this table, and only 11% of posts
use one.** This is one of the few numbers on this page that did not move at all when the corpus
doubled. Note the shape: it is not "shorter is better" — 7-14, 15-25 and 26+ are identical. It is
a cliff at about six words. Everything past that is the same.

Combined with the body-length finding, the picture is clear: **the first line matters and the rest
of the length does not.**

### Which patterns each buying job uses

| Job | opens on ? | opens on a number | stat in body | says "you" | bulleted | link in comments |
|---|---:|---:|---:|---:|---:|---:|
| problem | 10% | 13% | 34% | 50% | 11% | 4% |
| exploration | 8% | 5% | 25% | 47% | 12% | 4% |
| requirements | **12%** | 4% | 16% | **55%** | 18% | 7% |
| selection | **2%** | 8% | **48%** | 27% | 5% | 3% |
| validation | 8% | 8% | 39% | 27% | 12% | 4% |
| consensus | 11% | 2% | 26% | 43% | 21% | 2% |

`requirements` — already the worst-performing category at 0.70x — uses the worst-performing hook
(question openers) more than any other job, addresses the reader as "you" more than any other job,
and ships as a link post 30% of the time. Every one of those is a measured penalty in this corpus.
**It is not that buyer's guides cannot travel; it is that nobody publishes them in a shape that
travels.**

Compare `selection`, the best-performing job at 1.84x: it opens on a question 2% of the time,
carries a stat in the body 48% of the time, and barely addresses the reader at all. The
highest-performing content in this corpus is the least reader-centred content in it.

## Cadence varies thirty-fold

**An earlier version of this page said cadence does not differentiate these companies. That was
wrong, and the way it was wrong is worth keeping.** The scrape caps at 50 posts per company, so
*post counts* came out at a median of 45-48 for every cohort — and uniformity produced by a
ceiling looks exactly like uniformity produced by behaviour. The cap was the finding.

The measurable thing is the **span**: a company posting five times a week fills 50 slots in ten
weeks, one posting weekly takes a year. On that measure:

**Median 4.6 posts per week, range 0.7 to 20.6.** Rockwell Automation filled the 50-post cap in
**two weeks**; RightHand Robotics took 41 weeks to publish 27.

| | Median posts/week | Range |
|---|---:|---|
| **saas** | 5.4 | 1.2 - 15.9 |
| product | 3.6 | 0.7 - 20.6 |
| **service** | 2.8 | 0.7 - 9.2 |
| **enterprise motion** | 5.9 | 0.7 - 20.6 |
| plg | 5.3 | 1.0 - 15.6 |
| pls | 4.9 | 3.4 - 11.4 |
| **slg** | 3.9 | 0.7 - 9.8 |
| **scaled** | 6.3 | 1.0 - 20.6 |
| growth | 3.8 | 0.7 - 11.4 |
| **early** | 2.2 | 0.9 - 12.2 |

**Scaled companies publish nearly three times as often as early-stage ones** (6.3 against 2.2),
and SaaS twice as often as service firms. Service firms publish least and, from the split tables
above, publish the most buying-dense content when they do — fewer, heavier posts.

Round two sharpened the stage gradient rather than flattening it: with 12 early-stage companies
instead of 8, early cadence fell from 2.8 to **2.2 posts a week**. The thing a small company has
least of is not audience, it is publishing capacity.

**Publishing more does not appear to dilute.** Splitting the sample at the median cadence, both
halves break out (double their own median) on exactly **19%** of posts. High-cadence companies are
not paying for volume with flatter performance. That is a null result on one year of one sample,
not a licence to post twenty times a week, but the dilution effect people assume is not visible
here.

**Day of week is close to noise**: Monday to Thursday runs 1.00 to 1.04, Friday 0.94. Weekend
volume is tiny and Sunday the only day below 0.90. Day tables are usually content tables wearing a calendar —
Monday is 21% events here — so a day ranking mostly tells you what people schedule when.

## When the page is not the channel

Seven companies reshare more than 40% of what appears on their page, and three of them reshare so
much that they have almost no original page content at all:

| Company | Reshared | Cell |
|---|---:|---|
| Kalungi | 100% (16 of 16) | service x slg, early |
| PostHog | 77% (37 of 48) | saas x pls, growth |
| Dub | 72% (36 of 50) | saas x plg, early |
| Notion | 47% (23 of 49) | saas x plg, scaled |
| Dexterity | 46% (19 of 41) | product x enterprise, growth |
| Stripe | 44% (21 of 48) | saas x pls, scaled |
| Mercury | 40% (20 of 50) | saas x plg, growth |

These are founder-led companies whose page is an **amplifier for named people**, not a publisher.
That is a deliberate channel design and this engine models it directly as
[`kind: person` versus `kind: organisation`](decision/RESEARCH-channel-split.md). It also means
**a page-level benchmark is the wrong benchmark for these companies** — measure the founder's
profile instead. Kalungi, PostHog and Dub fall below this study's 20-original threshold for that
reason and are excluded from every percentage above. So does Velocity Partners, for a different
reason worth recording: a B2B content agency that published **two posts in eleven months** on its
own page.

---

## What a second pass found

The first pass asked what gets published and what the feed rewards. A second pass asked harder
questions of the same data, and four of the answers change how the rest of this page should be
read.

### Engagement is far more concentrated than a median suggests

| | Share of all engagement |
|---|---:|
| the top **1%** of posts | **26%** |
| the top 5% | 47% |
| the top 10% | 59% |
| the top 20% | 73% |

Median company Gini on raw engagement is **0.42** (Miro the most even at 0.24, Zoho the most
lottery-like at 0.67). Person channels are slightly more concentrated than pages, 0.47 against
0.42.

**Every ratio on this page is a median, and a median is the typical post, not where the reach
is.** A calendar tuned to raise the median optimises the body of a distribution whose top 1%
carries a third of everything. Both matter and they are different jobs: the median is what your
followers experience week to week, the tail is what reaches anybody else.

### The spread inside one company dwarfs the spread between companies

**The median company's best post outscores its own worst by 43x**, with a within-company standard
deviation of 1.34 on the normalised scale. Since every company's median is 1.00 by construction,
there is no between-company variance left in relative terms at all.

**So the decision that matters is not which company to imitate. It is which post to publish
next.** This document is most useful for spotting what you are not doing at all — the empty
formats, the missing jobs — and least useful as a target to converge on.

### The engagement ranking is only partly universal

The headline table says awards beat buyer's guides. Recomputed *inside* each company and counted
as a vote — one company, one vote, only where it published at least six posts with that label:

| Label | Corpus median | Companies testable | Share above 1.0 | Verdict |
|---|---:|---:|---:|---|
| `selection` | 1.98 | 13 | **92%** | consistent |
| `product-news` | 1.35 | 23 | 70% | **mixed** |
| `culture` | 1.33 | 26 | 69% | **mixed** |
| `event` | 1.00 | 43 | 49% | **mixed** |
| `validation` | 0.99 | 20 | 50% | **mixed** |
| `recruitment` | 0.78 | 6 | 33% | **mixed** |
| `exploration` | 0.90 | 49 | 31% | **mixed** |
| `problem` | 0.69 | 17 | **12%** | consistent (reliably *under*) |
| `requirements` | — | **1** | — | **cannot be tested** |
| `consensus` | — | **0** | — | **cannot be tested** |

**Round one ran this test on 46 companies and found four claims consistent. Round two ran it on 73
and found two.** `product-news` and `culture` both crossed back over the line — 70% and 69%, where
the test asks for 70% or better. They did not reverse; they stopped being reliable. That is what a
larger sample usually does to a finding at the boundary, and it is the reason to report the vote
rather than the median.

**Two claims survive.** `selection` beats a company's own median at 12 of the 13 companies that
published enough of it, and `problem` loses to it at 15 of 17. Those two are safe to act on
anywhere. Everything else on this page is a corpus median that hides real disagreement between
companies.

**`validation` splits exactly 50/50 across 20 companies.** "Case studies perform" is not a
generalisation this data supports. At half the companies measured, the case study is the weakest
thing on the page.

**And the two scarcest labels still cannot be validated at all, on a corpus of 73 companies.**
Exactly one company published six or more `requirements` posts and none published six `consensus`
posts. Adding 28 companies across eight verticals moved those counts from 1 and 0 to 1 and 0.

So the 0.70x and 0.82x quoted earlier rest on posts scattered thinly across many companies rather
than on any company's own experience. They are the best available estimate and they are not a
robust one. **The scarcity that makes decision-stage content the industry's biggest gap is the
same scarcity that makes it impossible to measure properly** — and that is itself the most
reliable thing this study can say about it.

### The carousel advantage is real, not an artefact of what gets published in it

The obvious objection to "multi-image earns 1.61x" is that carousels are mostly culture posts, and
culture performs well anyway. Tested inside each job, the format wins on its own:

| Job | Multi-image | Same job, other formats | |
|---|---:|---:|---|
| culture | **2.10x** (n=73) | 1.18x | format wins |
| event | **1.60x** (n=80) | 0.89x | format wins |
| csr | **1.53x** (n=9) | 0.83x | format wins |
| validation | **1.36x** (n=12) | 0.96x | format wins |
| exploration | **1.36x** (n=29) | 0.90x | format wins |
| selection | 1.83x (n=19) | 1.85x | no gain |
| product-news | 0.95x (n=14) | 1.24x | no gain |

**Within `validation` a carousel earns 1.36x where every other format earns 0.96x.** The case
study that becomes a carousel is a different post from the case study that becomes a link. Within
`event` the gap is wider still: 1.60x against 0.89x, on 80 carousels.

Two jobs show no benefit. Product news fits — a launch is an announcement and a carousel asks the
reader to work through it. `selection` is the interesting one: it was a format win in round one and
is now a dead heat, because an awards post is already the best-performing thing on the page and
the carousel has nothing left to add.

### What breakout posts are made of

298 posts tripled their own company's median. Against the other 2,816:

| | Breakouts | Everything else | |
|---|---:|---:|---:|
| `selection` | 21.5% | 5.6% | **+15.9** |
| `culture` | 24.2% | 9.7% | **+14.5** |
| `product-news` | 19.8% | 11.6% | +8.2 |
| `recruitment` | 3.0% | 3.0% | 0.0 |
| `validation` | 6.0% | 10.6% | -4.5 |
| `problem` | **0.3%** | 8.2% | **-7.8** |
| `event` | 12.1% | 21.0% | -8.9 |
| `exploration` | 8.7% | 23.6% | **-14.9** |
| **`requirements`** | **0.0%** | 2.7% | -2.7 |
| **`consensus`** | **0.3%** | 1.6% | -1.3 |
| video | 39.3% | 32.7% | +6.5 |
| multi-image | **16.8%** | 7.0% | **+9.8** |
| text | 5.4% | 13.1% | -7.8 |
| link | 6.4% | 14.0% | -7.6 |

**Not one of the 298 breakout posts was a buyer's guide.** One was a business case and one was
problem framing. On a corpus 55% larger than round one's, the decision-stage categories stayed at
zero. If
breakout reach is the goal, the decision-stage content is the wrong instrument — which is another
way of saying the same thing as the first table on this page, stated in the tail rather than the
median.

The formats tell the useful half: **breakouts are video and carousels; text and link posts are
half as likely to appear** as their share of the corpus would predict.

---

---

## The shapes that recur, and the ones that work

Everything above measures what companies publish *about*. This measures what shape the post is,
which is the part a writer actually reuses. A shape is `job x format x opening move`, all three
machine-read (`research/analyse_templates.py`). **209 shapes exist in the corpus; 31 carry at
least 25 posts** and those 31 cover two thirds of everything published.

### The opening move

| Opening | Share | Engagement | Doubles the median |
|---|---:|---:|---:|
| **"We…" / "Our…"** | 9.4% | **1.21x** | **28%** |
| declarative (everything else) | 71.6% | 1.00x | 20% |
| opens on a number | 2.3% | 0.99x | 20% |
| **"You…" / "Your…"** | 4.6% | 0.96x | **10%** |
| **a question** | 12.1% | **0.81x** | 11% |

The two moves LinkedIn advice recommends most — open on a question, open on the reader — are the
two worst. The move it warns against is the best.

### The thirteen shapes worth naming

Every shape below is at least 25 posts across at least ten companies, so none of them is one
company's house style:

| Job | Format | Opening | n | Engagement | Companies |
|---|---|---|---:|---:|---:|
| culture | multi-image | declarative | 48 | **2.14x** | 20 |
| **selection** | **image** | **declarative** | **79** | **2.10x** | **42** |
| selection | video | declarative | 28 | 2.08x | 20 |
| **event** | **multi-image** | declarative | 60 | **1.63x** | 33 |
| product-news | video | declarative | 151 | 1.54x | 38 |
| culture | image | declarative | 70 | 1.41x | 32 |
| event | video | declarative | 102 | 1.13x | 41 |
| validation | video | declarative | 112 | 1.11x | 37 |
| exploration | video | declarative | 183 | 1.00x | 54 |
| **event** | **image** | declarative | **181** | **0.92x** | 49 |
| problem | image | declarative | 45 | 0.77x | 24 |
| **problem** | **text** | declarative | 34 | **0.74x** | 17 |
| **event** | **link** | declarative | 47 | **0.58x** | 25 |

**The single most-published shape in B2B LinkedIn is an event post as a static image with a
declarative opening — 181 posts across 49 companies — and it earns 0.92x.** The same job as a
carousel earns 1.63x. That is one substitution, available to every company in the study, and
almost nobody makes it.

**The worst-performing shape that recurs is an event as a link post: 0.58x across 25 companies.**
A registration link posted as a link preview is the cheapest thing to make and the least
rewarded thing in the corpus.

**`problem` as a plain text post doubles its company's median 0% of the time.** Not rarely —
never, across 34 posts and 17 companies. If you are going to name a cost the reader is paying,
this data says do not do it as a text post.

### For each job: the shape most used, and the shape that earns most

Where these differ, the gap is the finding.

| Job | Most used | | Best | |
|---|---|---:|---|---:|
| problem | image / declarative (n=45) | 0.77x | video / "you" (n=13) | **1.07x** |
| exploration | video / declarative (n=183) | 1.00x | video / number (n=10) | **1.39x** |
| requirements | image / declarative (n=21) | **0.55x** | video / declarative (n=11) | **1.03x** |
| selection | image / declarative (n=79) | 2.10x | image / "we" (n=21) | 2.20x |
| validation | video / declarative (n=112) | 1.11x | *the same shape* | 1.11x |
| event | image / declarative (n=181) | 0.92x | multi-image / declarative (n=60) | **1.63x** |
| product-news | video / declarative (n=151) | 1.54x | video / question (n=11) | **2.19x** |
| culture | image / declarative (n=70) | 1.41x | multi-image / "we" (n=21) | **2.38x** |
| recruitment | image / declarative (n=27) | 0.86x | image / "we" (n=15) | **1.53x** |

**`validation` is the only job where the industry's default shape is also its best.** Everywhere
else the most-published shape is beaten by a shape sitting in the same corpus.

**`requirements` has the worst default of all: a static image with a declarative opening, at
0.55x.** The buyer's guide is not just the worst-performing job on this page, it is published in
the worst-performing shape available to it.

Two cautions. These are descriptions, not instructions: the engagement column says nothing about
whether the post did commercial work, and this page has already shown those two ranks to be near
opposites. And the "best" column is often a small sample — ten to twenty posts — so treat it as a
thing to try rather than a thing to believe.

---

## Design: what is actually on the image

Format tells you an image was posted. It says nothing about what was on it, and the brief this
study answers asked about design. Two things are measurable here, and they are measurable to very
different standards.

### Aspect ratio, measured on all 1,277 image posts

The feed is a fixed-width column, so the only thing a creative controls is how much vertical space
it claims. This is in the scrape metadata, so it is measured on everything rather than sampled:

| Shape | Share | Engagement | Doubles the median |
|---|---:|---:|---:|
| **wide 16:9** | **39.0%** | 1.08x | 21% |
| square 1:1 | 32.3% | 1.00x | 20% |
| **portrait 4:5** | 19.0% | **1.16x** | **28%** |
| landscape 4:3 | 8.1% | **1.47x** | 32% |
| tall 9:16+ | 1.6% | 1.31x | 15% |

**The most-used aspect ratio is 16:9, and it is the one that claims the least screen.** Portrait
4:5 occupies roughly twice the vertical space of 16:9 in the same column, earns 1.16x against
1.08x, and doubles its company's median 28% of the time against 21%.

The per-job table is where it gets sharper:

| Job | 16:9 | 1:1 | 4:5 |
|---|---|---|---|
| **selection** | 33% at **2.10x** | 42% at 1.45x | 17% at **4.18x** |
| validation | 33% at 1.00x | 40% at 1.00x | 19% at **1.33x** |
| event | 37% at 1.00x | 37% at 0.82x | 18% at **1.28x** |
| culture | 30% at 2.45x | 26% at 1.42x | 29% at 1.39x |
| exploration | 50% at 0.95x | 24% at 0.96x | 18% at 0.90x |
| product-news | 50% at 1.16x | 35% at 1.02x | 10% at 0.89x |
| problem | 32% at **0.88x** | 29% at 0.66x | 27% at 0.67x |

**An awards post in portrait earns 4.18x; the same post in 16:9 earns 2.10x**, and only 17% of
them are portrait. For `selection`, `validation` and `event`, portrait is the best shape and the
least used. For `exploration`, `product-news` and `problem` it is not — those three do better wide,
which is worth knowing before anyone issues a blanket "always post portrait".

**16:9 is where a repurposed asset lands.** A blog header, a webinar slide, a YouTube thumbnail
are all 16:9 already. The 39% share is not a design decision; it is the absence of one.

### What is on the strong creatives and what is on the weak ones

The rest of design cannot be measured from metadata, so it was sampled and looked at. The sample
is paired: for each job, the images from that job's best-performing posts against the images from
its worst-performing posts, at the same company-normalised scale, so content is held roughly
constant and what differs is the design (`research/sample_creative.py`). **36 images were pulled;
eight were coded, across four jobs.** That is a small sample and is reported as one — it generates
hypotheses to test against your own feed, not benchmarks.

**Evidence beats assertion, and the gap is enormous.** The strongest `validation` creative in the
sample (6.54x) is a screenshot of a third-party benchmark leaderboard with the vendor at rank one,
competitors named and visible, and the number — 90.9% — legible at feed size without zooming. The
weakest (0.08x) is a quote card: a customer's endorsement set in large display type, correctly
attributed, with no number on it at all. One shows the thing working. The other shows somebody
saying it works.

**The asset cover is the weakest recurring creative.** The weak `requirements` example (0.34x) is
a 16:9 dark cover with a rendered mockup of the PDF floating on it. A picture of a document is a
picture of homework, and it is exactly what a buyer's guide gets published as.

**The strongest creatives carry the brand system; the weakest carry none.** The two weakest images
in the sample were a stock meme template with white caption text and visible compression artefacts,
and a retail-style sale banner with a discount badge and a deadline. Neither used the company's
own colour system, type or logo in any load-bearing way. Both would have looked identical with
another company's name on them.

**Type on its own is fine, and often better.** The strongest `selection` creative (16.29x) is a
portrait card carrying the logo and the award line and nothing else: no photograph, no product, no
mockup. The message *is* the image. This runs against the instinct to add a visual; where the claim
is short and strong, setting it large and getting out of the way outperformed every decorated
alternative in the sample.

**A person at scale works where a document does not.** The strong `requirements` creative (2.20x)
was a full-bleed cut-out of one named employee, treated like a sports card. Round one's format
table already showed video and carousels beating static images; this sample suggests part of what
those formats buy is a human being at a size the feed cannot ignore.

---

## What was removed from the corpus, and what was deliberately kept

An audit removes **506 posts, 10.1% of the corpus** (`research/audit_corpus.py`, exclusions
listed in `research/excluded.json`, nothing deleted from `raw/`).

| Reason | Posts |
|---|---:|
| predates the window the page corpus covers | 366 |
| person not employed by the company they were paired to | 58 |
| no text at all | 44 |
| exact duplicate of an earlier post by the same account | 24 |
| generated by LinkedIn's job widget, not written by the company | 14 |

The page corpus loses **1.2%**. The person corpus loses **25.7%**, and the count of usable people
fell from 43 to 33. Three of those reasons were defects in how this study was built:

**The two corpora did not cover the same window.** Company pages were pulled as one recent slice
and span twelve months. Person feeds were pulled to the same post cap and reach back to **2014**.
LinkedIn in 2014 is not the platform being measured, and it shows: pre-window person posts are
**60.5% text-only against 35.2% in-window**. Every person-versus-page composition number in the
first version of this page was inflated by it.

**Selecting people by "whose posts does this page reshare" conflates employees with everybody
else.** A page reshares its customers, its partners and the community figures it likes. Four
people in the sample did not work at the company they were paired to — an independent creator
reshared by Raspberry Pi, a founder of a different company reshared by Airtable, a designer
reshared by Notion, and a FedEx executive reshared by a FedEx *supplier*. A paired comparison
asking "does this company's person beat this company's page" is meaningless for them.

**A post LinkedIn wrote is not a post the company wrote.** Cognism's feed carries 14 posts in the
format "We're #hiring a new {title} in {city}. Apply today or share this post with your network."
— **28% of its feed**. LinkedIn's job widget renders those from a requisition; nobody at the
company chose a word of them. They are short, they open on "we", they carry a CTA verb and a
hashtag, and every one of those is a trait this study reports on. That a page gives a third of its
feed to them is a real finding and stays in; the text is not evidence about how the company writes
and leaves the analysis.

**The pruning strengthened the main finding rather than weakening it.** Founders went from 3.06x
to **3.17x** and the overall win rate from 69% to 74%, because some of what was removed was
historic posts from people who have since stopped posting.

### What was deliberately kept

**"Carries no information" is not the same as "is bad content."** These all stayed:

- **One-line posts** — "This is awesome!", "Great to see!". Weak content, and a real finding: it
  is how several executives in this sample actually use the channel. Removing them would flatter
  the corpus into reporting that people write essays.
- **Zero-engagement posts.** A real outcome. Dropping them would raise every median in this
  document by hiding the failures.
- **Memes, in-jokes and off-topic posts.** Real decisions with real opportunity costs.
- **Non-English posts.** A finding about who these companies are talking to.
- **Repeated posts that are not identical.** Zebra Technologies published the *same* newsletter
  blurb **ten times** — a fifth of its feed. Nine of those are excluded as duplicates, and the
  repetition itself is one of the more striking content-operation findings here.

## Using this

**0. Read the median and the tail as two different jobs.** The top 1% of posts carry 26% of all
engagement, and the spread inside one company's own feed is larger than anything measured between
companies. Nothing on this page is a target to converge on; it is a map of what your cell does and
does not do.

**1. Find your industry row first, then your cell.** Industry has the widest spread of any axis
here — 12% to 46% TOFU — and it was the axis this study was missing for its entire first round.
The cell tables are still useful; they are just not the first cut any more.

**2. Look at what your row is missing, not what it has.** The tables describe what companies like
yours *do*, not what works. `requirements` and `consensus` are 3.9% of the entire corpus, so
almost every row understates them. Treat the grid as a baseline to deviate from deliberately.

**3. Set the split from Fit, never from Lift.** The eleven-row table at the top is the reason. If
you let engagement choose, you will publish awards and team photos, because that is what the feed
pays for.

**4. Fix format and shape before you touch the words.** It is the largest measured effect.
Specifically: move comparison and business-case content out of link posts and into carousels
(0.70x to 1.61x), move event posts out of static images and into carousels (0.92x to 1.63x), and
stop shipping creatives at 16:9 by default. Every one of those is a decision made once, in a
template, not per post.

**5. Declare your buyer.** It splits behaviour harder than offering, motion or stage. A profile
that declares `buyer: practitioner` and one that declares `buyer: procurement` should not get the
same calendar.

**6. Check whether the page is even your channel.** If your founder outperforms the page, the page
is an amplifier and the benchmarks above do not apply to it.

**7. Believe two findings and test the rest.** Recomputed company by company, only `selection`
beats a company's own median reliably and only `problem` loses to it reliably. Everything else on
this page is a corpus median hiding disagreement between companies, including yours.

`engine/decision/company_type.py` turns the offering and motion declarations into constraints and
cautions. **It deliberately returns no score multipliers** — the numbers above are a description
of an industry, and an industry is not a target. That is truer after round two than before it: the
one thing a doubled corpus reliably did was demote findings from "consistent" to "mixed".

---

## Method, and what it cannot tell you

**The person sample.** 47 named people, each paired to a company already in the frame, defined in
[`research/person-frame.yaml`](../research/person-frame.yaml). Two tiers. **Tier A cost nothing
and was chosen by the companies themselves**: when a page reshares, the scrape records the
original author, so the corpus already named 155 people these pages choose to amplify. **Tier A
alone would have answered the wrong question** — the pages that reshare heavily are early PLG and
founder-led companies, so a sample drawn only from it measures founders at startups and would have
reported "named people post informally" as a fact about people rather than about that cell. Tier B
filled the enterprise, service and industrial cells. **33 people clear a 15-post floor after the
audit; the 14 below it are named in the output**, and the floor counts usable posts rather than
pulled ones -- counting the raw pull let an account whose every post was excluded still appear in
the headcount while contributing nothing. Seniority is read off the LinkedIn headline the scrape returns
on every post.

**Sample, round one.** 49 companies chosen to populate an offering x motion x stage grid,
defined in [`research/sample-frame.yaml`](../research/sample-frame.yaml) with a stated reason for
every company. Pulled September 2026 via Apify, up to 50 posts each, 2,298 posts.

**Sample, round two.** 28 further companies, chosen on one rule stated before any credit was
spent: **a company enters because its vertical is missing, not because its content is good.**
Picking well-known good publishers would have produced a flattering corpus and a useless one — the
question is what a vertical does, not what its best account does. Where a vertical offered a
choice, the tie went to whatever also thickened a thin cell: service, early stage and PLS. 1,299
further posts, $2.00 of Apify credit. **10 of the 28 came back empty on the first pull and every
one was a wrong slug** — Mercury is `mercuryhq`, project44 is `project-44`, Bluebeam is
`bluebeam-software`. Same failure mode as round one, same fix.

**73 of the 77 companies clear the 20-original threshold**, and the four that do not are named in
the output. Raw JSON is kept so classification can be re-run without paying to scrape again, and
company attributes are joined from the frame at analysis time rather than from the scrape
snapshot — otherwise adding an axis silently gives every previously-scraped company a null for it.

**Labelling.** Every post was **read** and assigned exactly one of twelve labels defined in
[`research/CLASSIFICATION-PROTOCOL.md`](../research/CLASSIFICATION-PROTOCOL.md). An earlier
regex pass left 95% of the corpus unclassified and was abandoned: buying jobs are semantic, and
patterns only find the posts that announce themselves, which biases the result toward companies
with a house style of labelling their own content. **1.4% of posts ended as `unclear`**, against a
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

**The paired ratio is confounded by follower counts, and nothing here removes that.** A founder
with 80,000 followers beating a page with 12,000 is not evidence about post shape. The pairing
controls for company, market and window; it does not control for audience size, which is the
variable most likely to be driving the result. Read every ratio in the person section as a
direction. It is the right direction for a channel decision — reach is reach, whatever produces
it — but it is not a claim that the same words do better under a face.

**Seniority is read off a self-written headline.** "Founder & CEO at X" is reliable; a headline
reading "Building the future of work" is not, and lands in individual contributor. The bands are
also small: 19 founder pairs, but only 3 C-suite and 3 VP. **The VP row at 0.77x is three people**
and should be treated as a signal to check rather than a finding to act on.

**The person labels are a sample, not a census, and the pruning made it smaller.** 447 usable
labelled person posts against a company corpus read in full. That is comfortable for the headline
splits and thin everywhere else: `requirements` is 1.1% of it, which is five posts, and the
C-suite row is 49 posts from three people.

**The design section is 8 coded images.** The aspect-ratio table rests on all 1,277 image posts
and is as solid as anything here. Everything after it in that section rests on eight images across
four jobs, paired strong against weak within the same job. It is a hypothesis generator. It is
written as one and should be read as one.

**Two labelling decisions in round two are judgement calls worth disclosing.** Deel ran a
recruitment campaign for a customer's job — a real, paid, advertised role — as a product
demonstration of borderless hiring; those posts are labelled `validation` where they make the
product point and `culture` where they are pure stunt, not `recruitment`, because nobody was being
recruited to Deel. Juro's weekly listings of *other companies'* legal vacancies are labelled
`recruitment`, because they are job listings, even though Juro is not hiring. A different reader
could defend the opposite on either. Both are large enough to move their company's row.

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
is the finding "they post nothing". 14 of the first 47 companies came back empty, and 10 of the
next 28; every one was a bad slug or a flaky run. Retool is `tryretool`, Outreach is
`outreach-saas`, Ironclad is `ironclad-inc-`, Sylvera is `sylveracarbon`, and ABB Robotics
publishes from a LinkedIn **showcase** page that `/company/` does not reach. **Roughly a third of
slugs guessed from a company name are wrong**, across two independent rounds. Resolve before
concluding.

For the two parts of this page that are newer than the rest:

```bash
python research/analyse_templates.py          # the shape library
python research/sample_creative.py --measure-only   # aspect ratio, all image posts
python research/sample_creative.py --out <scratch dir outside the repo>
```

The creative sampler refuses to write inside the repository. The images are other companies'
copyrighted work; the coded attributes are the deliverable and the files are not kept.
