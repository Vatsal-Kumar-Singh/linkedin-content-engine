# What B2B companies actually publish on LinkedIn

A measured reference for setting a content split, choosing formats, and shaping a calendar — cut
by **what you sell**, **how you sell it**, **who buys**, and **how big you are**.

**2,026 original posts from 46 company pages, every one read and labelled by hand**, plus
**1,289 posts from 33 named people** paired to those same companies. A later audit removed 487
posts (12.6%) that could not answer the question asked of them — the reasons are in
[Pruning](#what-was-removed-from-the-corpus-and-what-was-deliberately-kept), and the person count
fell hardest. Method, sample and limits are at the bottom; read them before quoting any number.

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

**`requirements` and `consensus` together are 5.0% of everything published.** Whatever else the
grid below says, that is the gap in this industry — and it is scarce enough that the 0.68x and
0.80x above could not be confirmed company by company. See
[the second pass](#the-engagement-ranking-is-only-partly-universal).

---

## The split, by what you sell

Percentages are of all original posts. "non-buying" is recruitment, culture, event, product news
and CSR combined — real work, just not buying work.

| Offering | n | TOFU | MOFU | BOFU | non-buying |
|---|---:|---:|---:|---:|---:|
| **service** | 269 | **49%** | 13% | 8% | **29%** |
| **saas** | 1082 | 30% | 8% | 11% | 50% |
| **product** | 650 | 26% | 14% | 15% | 44% |

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
| saas x slg | 250 | 36% | 10% | 6% | 48% | Category argument plus a heavy event calendar |
| saas x enterprise | 230 | 33% | 13% | **20%** | 33% | The most BOFU-heavy SaaS. Committees demand proof |
| product x enterprise | 375 | 29% | **17%** | 14% | 39% | Spec and comparison content. Engineers are evaluating |
| product x slg | 140 | 29% | 8% | **29%** | 35% | **Proof is the product.** Highest BOFU anywhere |
| saas x pls | 226 | 29% | 7% | 14% | 50% | Self-serve front door, enterprise back end |
| saas x plg | 376 | 23% | 5% | 7% | **61%** | Release notes and community |
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
| quotes somebody | 8.6% | **1.18x** | **+18%** |
| "link in comments" | 4.6% | **1.16x** | **+16%** |
| opens on "we" or "our" | 10.3% | **1.13x** | **+13%** |
| has a stat in the body | 24.8% | 1.05x | +5% |
| explicit CTA verb | 27.4% | 1.03x | +3% |
| addresses "you" anywhere | 48.8% | 1.00x | 0% |
| uses emoji | 36.0% | 1.00x | 0% |
| has hashtags | 23.4% | 1.00x | 0% |
| bulleted or listed | 11.8% | 0.98x | -2% |
| **opens on a question** | 7.3% | **0.82x** | **-18%** |

**Four of these contradict advice you will have been given.**

**Opening on a question is the worst-performing trait measured.** It is the single most commonly
recommended LinkedIn hook and it runs 18% below posts that do not use it. A question asks the
reader for work before giving them anything.

**Hashtags do nothing. At all.** Zero hashtags, one to three, four to seven — every band sits at
exactly 1.00x. **76.6% of this corpus uses none**, and the quarter that does gets nothing for it.

**Emoji do nothing either** — 36% of posts use them, at 1.00x.

**Talking about yourself is fine.** Posts opening on "we" or "our" run 13% *above* the rest, and
posts addressing "you" run exactly level. The advice to write in second person and never lead with
yourself is not visible in this data.

Two things that do work and are barely used: **quoting somebody** (+18%, in 8.6% of posts) and
putting the **link in the comments** (+16%, in 4.6%). The second is worth noting alongside the
format table, where link posts are the worst format at 0.75x — the penalty is on the link *in the
post*, and moving it to the comments appears to recover it.

### The first line is the lever

| First line | Share | Engagement |
|---|---:|---:|
| **1-6 words** | 12.2% | **1.19x** |
| 7-14 words | 36.9% | 1.00x |
| 15-25 words | 29.6% | 0.99x |
| 26+ words | 21.3% | 1.00x |

**A very short opening line is worth more than anything else in this table, and only 12% of posts
use one.** Note the shape: it is not "shorter is better" — 7-14, 15-25 and 26+ are identical. It is
a cliff at about six words. Everything past that is the same.

Combined with the body-length finding, the picture is clear: **the first line matters and the rest
of the length does not.**

### Which patterns each buying job uses

| Job | opens on ? | opens on a number | stat in body | says "you" | bulleted | link in comments |
|---|---:|---:|---:|---:|---:|---:|
| problem | 11% | 14% | 33% | 50% | 12% | 5% |
| exploration | 10% | 4% | 17% | 46% | 11% | 5% |
| requirements | **16%** | 3% | 14% | **62%** | 21% | 7% |
| selection | 3% | 8% | **45%** | 27% | 5% | 3% |
| validation | 8% | 7% | 41% | 21% | 13% | 3% |
| consensus | 11% | 2% | 24% | 40% | 20% | 2% |

`requirements` — already the worst-performing category at 0.68x — uses the worst-performing hook
(question openers, 16%) more than any other job. It is being written in the least effective way
available, on top of shipping as a link post a third of the time.

## Cadence varies thirty-fold

**An earlier version of this page said cadence does not differentiate these companies. That was
wrong, and the way it was wrong is worth keeping.** The scrape caps at 50 posts per company, so
*post counts* came out at a median of 45-48 for every cohort — and uniformity produced by a
ceiling looks exactly like uniformity produced by behaviour. The cap was the finding.

The measurable thing is the **span**: a company posting five times a week fills 50 slots in ten
weeks, one posting weekly takes a year. On that measure:

**Median 4.5 posts per week, range 0.7 to 20.6.** Rockwell Automation filled the 50-post cap in
**two weeks**; RightHand Robotics took 41 weeks to publish 27.

| | Median posts/week | Range |
|---|---:|---|
| **saas** | 6.0 | 1.2 - 15.9 |
| product | 3.4 | 0.7 - 20.6 |
| **service** | 2.5 | 0.7 - 9.2 |
| **enterprise motion** | 6.0 | 0.7 - 20.6 |
| plg | 4.9 | 1.0 - 15.6 |
| pls | 4.5 | 3.6 - 9.0 |
| **slg** | 3.1 | 0.7 - 9.8 |
| **scaled** | 6.6 | 1.0 - 20.6 |
| growth | 3.0 | 0.7 - 9.8 |
| early | 2.8 | 1.0 - 12.2 |

**Scaled companies publish more than twice as often as growth-stage ones**, and SaaS more than
twice as often as service firms. Service firms publish least and, from the split tables above,
publish the most buying-dense content when they do — fewer, heavier posts.

**Publishing more does not appear to dilute.** Splitting the sample at the median cadence, both
halves break out (double their own median) on exactly **19%** of posts. High-cadence companies are
not paying for volume with flatter performance. That is a null result on one year of one sample,
not a licence to post twenty times a week, but the dilution effect people assume is not visible
here.

**Day of week is close to noise**: Monday to Friday runs 0.98 to 1.02. Weekend volume is tiny and
Sunday is the only day below 0.90. Day tables are usually content tables wearing a calendar —
Monday is 21% events here — so a day ranking mostly tells you what people schedule when.

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

## What a second pass found

The first pass asked what gets published and what the feed rewards. A second pass asked harder
questions of the same data, and four of the answers change how the rest of this page should be
read.

### Engagement is far more concentrated than a median suggests

| | Share of all engagement |
|---|---:|
| the top **1%** of posts | **30%** |
| the top 5% | 50% |
| the top 10% | 61% |
| the top 20% | 74% |

Median company Gini on raw engagement is **0.42** (Miro the most even at 0.24, Zoho the most
lottery-like at 0.67). Person channels are slightly more concentrated than pages, 0.47 against
0.42.

**Every ratio on this page is a median, and a median is the typical post, not where the reach
is.** A calendar tuned to raise the median optimises the body of a distribution whose top 1%
carries a third of everything. Both matter and they are different jobs: the median is what your
followers experience week to week, the tail is what reaches anybody else.

### The spread inside one company dwarfs the spread between companies

**The median company's best post outscores its own worst by 36x**, with a within-company standard
deviation of 1.33 on the normalised scale. Since every company's median is 1.00 by construction,
there is no between-company variance left in relative terms at all.

**So the decision that matters is not which company to imitate. It is which post to publish
next.** This document is most useful for spotting what you are not doing at all — the empty
formats, the missing jobs — and least useful as a target to converge on.

### The engagement ranking is only partly universal

The headline table says awards beat buyer's guides. Recomputed *inside* each company and counted
as a vote — one company, one vote, only where it published at least six posts with that label:

| Label | Corpus median | Companies testable | Share above 1.0 | Verdict |
|---|---:|---:|---:|---|
| `selection` | 1.82 | 10 | **90%** | consistent |
| `product-news` | 1.39 | 16 | 75% | consistent |
| `culture` | 1.33 | 14 | 71% | consistent |
| `problem` | 0.69 | 17 | **18%** | consistent (reliably *under*) |
| `event` | 1.01 | 25 | 56% | **mixed** |
| `validation` | 1.06 | 11 | 55% | **mixed** |
| `exploration` | 0.93 | 31 | 32% | **mixed** |
| `requirements` | — | **1** | — | **cannot be tested** |
| `consensus` | — | **0** | — | **cannot be tested** |

Four claims survive the stricter test: awards, launches and culture reliably beat a company's own
median, and problem framing reliably loses to it. **Three do not.** `validation` splits almost
evenly — a case study is a strong post at some companies and a weak one at others, so "case
studies perform" is not a safe generalisation and is worth testing on your own feed.

**And the two scarcest labels cannot be validated at all.** Exactly one company published six or
more `requirements` posts and none published six `consensus` posts, so the 0.68x and 0.80x
figures quoted earlier rest on posts scattered thinly across many companies rather than on any
company's own experience. They are the best available estimate and they are not a robust one.
The scarcity that makes them the industry's biggest gap is the same scarcity that makes them hard
to measure.

### The carousel advantage is real, not an artefact of what gets published in it

The obvious objection to "multi-image earns 1.58x" is that carousels are mostly culture posts, and
culture performs well anyway. Tested inside each job, the format wins on its own:

| Job | Multi-image | Same job, other formats | |
|---|---:|---:|---|
| culture | **2.38x** (n=41) | 1.12x | format wins |
| selection | **1.71x** (n=16) | 1.50x | format wins |
| event | **1.60x** (n=36) | 0.93x | format wins |
| validation | **1.38x** (n=11) | 0.97x | format wins |
| exploration | **1.36x** (n=15) | 0.94x | format wins |
| product-news | 0.88x (n=13) | 1.24x | no gain |

**Within `validation` a carousel earns 1.38x where every other format earns 0.97x.** The case
study that becomes a carousel is a different post from the case study that becomes a link. Only
product news shows no benefit, which fits — a launch is an announcement and a carousel asks the
reader to work through it.

### What breakout posts are made of

174 posts tripled their own company's median. Against the other 1,827:

| | Breakouts | Everything else | |
|---|---:|---:|---:|
| `culture` | 23.0% | 7.4% | **+15.5** |
| `selection` | 20.7% | 6.5% | **+14.2** |
| `product-news` | 23.0% | 12.3% | +10.7 |
| `validation` | 5.2% | 10.0% | -4.8 |
| `event` | 10.9% | 19.6% | -8.7 |
| `problem` | **0.6%** | 10.8% | **-10.3** |
| `exploration` | 9.2% | 22.3% | -13.1 |
| **`requirements`** | **0.0%** | 3.1% | -3.1 |
| video | 42.5% | 33.0% | +9.5 |
| multi-image | **15.5%** | 6.3% | **+9.2** |
| text | 5.7% | 15.3% | -9.5 |
| link | 5.7% | 14.8% | -9.1 |

**Not one of the 174 breakout posts was a buyer's guide, and one was problem framing.** If
breakout reach is the goal, the decision-stage content is the wrong instrument — which is another
way of saying the same thing as the first table on this page, stated in the tail rather than the
median.

The formats tell the useful half: **breakouts are video and carousels; text and link posts are
half as likely to appear** as their share of the corpus would predict.

---

## What was removed from the corpus, and what was deliberately kept

An audit after the first analysis removed **487 posts, 12.6% of the corpus**
(`research/audit_corpus.py`, exclusions listed in `research/excluded.json`, nothing deleted from
`raw/`).

| Reason | Posts |
|---|---:|
| predates the window the page corpus covers | 366 |
| person not employed by the company they were paired to | 58 |
| no text at all | 41 |
| exact duplicate of an earlier post by the same account | 22 |

The page corpus lost **0.9%**. The person corpus lost **22.5%**, and the count of usable people
fell from 43 to 33. Two of those reasons were defects in how this study was built:

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

**0. Read the median and the tail as two different jobs.** The top 1% of posts carry 30% of all
engagement, and the spread inside one company's own feed is larger than anything measured between
companies. Nothing on this page is a target to converge on; it is a map of what your cell does and
does not do.

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

**The person sample.** 47 named people, each paired to a company already in the frame, defined in
[`research/person-frame.yaml`](../research/person-frame.yaml). Two tiers. **Tier A cost nothing
and was chosen by the companies themselves**: when a page reshares, the scrape records the
original author, so the corpus already named 155 people these pages choose to amplify. **Tier A
alone would have answered the wrong question** — the pages that reshare heavily are early PLG and
founder-led companies, so a sample drawn only from it measures founders at startups and would have
reported "named people post informally" as a fact about people rather than about that cell. Tier B
filled the enterprise, service and industrial cells. 43 people cleared a 15-post floor; the four
below it are named in the output. Seniority is read off the LinkedIn headline the scrape returns
on every post.

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
