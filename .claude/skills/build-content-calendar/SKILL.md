---
name: build-content-calendar
description: Plan what to publish — pains by funnel tier by format, with enough runway not to run dry. Use when building a content calendar, deciding the TOFU/MOFU/BOFU mix, working out how many posts a narrowed message set yields, or matching formats to content.
---

# Building the content calendar

## Generate it, do not write it

The calendar is pains × tiers × formats. Write the script, commit the output, and
regenerate when the register changes. Hand-maintaining the grid guarantees it
drifts from the pain points, and then two documents disagree with nothing saying
which is current.

## The tier rule, stated so it can be enforced

> **TOFU = what is · MOFU = how to · BOFU = how WE**

Apply it to a draft in seconds: if a post labelled TOFU explains how *we* do
something, it is not TOFU.

**TOFU names the problem and stops.** No product, no mechanism, no us. The reason
to hold this line is the 95-5 rule — at any moment roughly 95% of buyers are not
in market. A TOFU post that pitches in its last line spends the 95% to reach the
5% who were going to find you anyway.

This is the rule most likely to slip, because every pain in the register is written
as problem *plus* what we do about it. On TOFU only the left column ships. Nothing
enforces that by default, so make it a gate or a review question.

**Most BOFU is not feed content.** It is sales enablement that happens to live on
LinkedIn — an asset a rep sends in a follow-up, links in a DM, shows on a call. Its
audience is the people in your pipeline, not the feed. Judge it by whether a rep
used it, and make it when sales asks rather than on a schedule.

**The exception, and it is the one that matters.** *The test is not the tier. It is
whether the reader can be reached any other way.* A rep can send a spec sheet to a
contact who asked for it. **Nobody can send anything to the person who blocks the
deal and never takes a vendor call** — the security reviewer, the platform owner,
the safety lead. They are not in your pipeline and never will be.

For that reader the feed is not a second-best channel, it is the only one. Schedule
the consensus artefacts: the objection they will raise, answered for the champion
who has to face them without you in the room. Keep the collateral off the feed.

This was learned the expensive way: a calendar with a documented BOFU bank, every
item deliberately unscheduled, and nothing anywhere that armed a champion against
the person who could stop the project.

## Decide it, do not assume it

`engine/decision/` scores a planned slot three ways and never blends them, because
they fail differently:

| | |
|---|---|
| **Gate** | May we publish this at all. Binary, runs first, holds the claim rules |
| **Lift** | What this treatment is worth, from **your own** measured corpus |
| **Fit** | Is it the right thing to say, given what your content is for |

**It ships with no measurements and refuses rather than guessing.** Without a
profile it returns `None` and names the missing input — because a number computed
from somebody else's audience looks exactly like a real one. `docs/decision/`
covers the profile, the intake and the method for eliciting objectives.

## The mix: start from what your cell actually does

`docs/BENCHMARKS.md` measured 2,020 hand-read posts from 46 companies. Find the row
that matches what the company sells and how it sells, and start there rather than
from a remembered ratio:

| Cell | TOFU | MOFU | BOFU | non-buying |
|---|---:|---:|---:|---:|
| service x slg | 50% | 9% | 2% | 37% |
| service x enterprise | 49% | 16% | 13% | 22% |
| saas x slg | 36% | 9% | 6% | 48% |
| saas x enterprise | 33% | 13% | 20% | 33% |
| product x enterprise | 30% | 17% | 13% | 38% |
| product x slg | 29% | 8% | **29%** | 35% |
| saas x pls | 29% | 7% | 14% | 50% |
| saas x plg | 23% | 4% | 7% | 61% |
| product x plg | 15% | 13% | 2% | 69% |

**Non-buying content is 45% of the whole corpus** — events, launches, culture,
hiring, CSR. If your calendar is 100% buying jobs you have built something no
company in the sample publishes, and the slots you have not planned will get
filled reactively by whoever has a conference next week.

**Who signs splits behaviour harder than what you sell.** Practitioner-buyer pages
are 60% non-buying; procurement-buyer pages are 32%. That gap is wider than the gap
between any two offerings. Read the buyer off the profile before the offering.

**TOFU is still the only tier that reaches non-followers**, which is why small
accounts lean on it harder than the table suggests. Audience size moves you along
the TOFU axis; the cell tells you the shape of what is left.

## Planning a named person's channel

1,785 posts from 43 named people, each paired to a company page in the same study
(`docs/BENCHMARKS.md`). Three things follow for a calendar.

**The topic grid transfers; the execution does not.** A founder's published mix is
nearly identical to their own page's — 28/11/10/44 against 31/10/12/45 on
TOFU/MOFU/BOFU/non-buying. So plan the founder's slots from the same cell table
above. What must not transfer is how it ships: person channels run 40% text-only
against a page's 15%, drop video from 34% to 13%, go long or very short rather than
medium, and carry an explicit CTA in 7% of posts against a page's 21%.

**Which seat, not which person.** Measured against their own page in the same
window, a founder's median post ran **3.06x** and won 19 of 23 pairs. A VP's ran
**0.54x** and won 1 of 4. Individual contributors ran level. The gap between two
person channels is wider than the gap between a person and a page, so "get the
executives posting" is not a plan and "get the founder posting" is. Declare the
seat in the profile: `channels: { founder: { kind: person, seat: founder } }`.

**Keep the proof on the page.** BOFU halves on a person's channel (11.6% to 6.0%)
and named-customer validation nearly halves (9.4% to 4.7%). That is coherent — a
case study is a company asset with a company's approvals behind it — and it means
**the two channels are not substitutes.** A buyer mid-evaluation is served by the
page.

**And do not put the event calendar on the founder.** The one real substitution
between the two is `culture` (8.9% page, 17.7% founder) against `event` (18.5%
page, 10.7% founder). The page runs booths, webinars and registration drives; the
founder tells the stories. A founder posting booth logistics is spending the most
valuable channel a company has on the cheapest work it has.

## Do not let engagement set the mix

The same corpus, scored against each company's own median:

| | Engagement | |
|---|---:|---|
| selection — awards, funding, customer counts | **1.59x** | |
| culture | 1.32x | |
| product news | 1.20x | |
| validation | 1.00x | |
| exploration | 0.95x | |
| consensus — ROI, security, procurement | **0.80x** | |
| problem | **0.77x** | |
| requirements — comparisons, buyer's guides | **0.68x** | |

**The three worst-performing categories are the three an active evaluation needs.**
A calendar tuned on engagement converges on trophies and team photos. This is
exactly why Gate, Lift and Fit are scored separately and never blended — Lift ranks
that table almost perfectly upside down from Fit.

And note what is scarce: **requirements and consensus together are 5.1% of
everything those 46 companies published.** The middle and the end of the funnel are
an industry-wide hole. Do not aim at the median there.

## Narrowing the message means MORE posts per pain, not fewer

The arithmetic that surprises people:

| Pains kept | At one post per tier | Runway at 2/week |
|---|---|---|
| 2 | 6 | 3 weeks |
| 3 | 9 | **4.5 weeks** |
| 4 | 12 | 6 weeks |

What fills the gap is **angles** — the same pain, a different way in: cost of
inaction, contrarian take, myth-bust, customer story, how it actually works, the
hidden version nobody names. Three pains × six angles is eighteen TOFU posts
before you touch MOFU.

Organise by **pain cluster, not by tier**. Each pain gets a ladder, you publish
TOFU-weighted and interleave the rest. Not "TOFU month, then MOFU month".

## Match the format to the shape of the content

A stat card needs a pain that has a number. A comparison needs two states. A
journey needs an escalation. Putting one pain through every template forces
mismatches — a statement with no number in a big-stat layout is a chart of
nothing.

Check what your pains actually contain before assigning formats. On the original
project only two of six pains had a figure, which moved an entire test round onto
statement cards.

## Watch the format distribution

Count how many posts each template family actually serves before investing in it.
On the original project six of seven card layouts served 19% of the calendar while
the carousel — 74% — ran on two slide layouts. A seventh card layout would have
changed two or three posts; a second carousel slide type changes sixty.

**And check what you are not using at all.** In the measured corpus, multi-image
posts earn **1.58x** their company's median — the best of any format — and are
**7.1%** of what gets published. Ten of the 46 companies published none. Where
carousels do get used they carry team photos (2.38x), while `requirements`, the
worst-performing category, ships as a **link post 34%** of the time and a carousel
**2%** of the time.

**The comparison table that belongs in a carousel is being posted as a link to a
blog.** Link posts are the worst-performing format in the dataset (0.75x). If a
calendar puts decision-stage content behind a link, that is the first thing to fix.

Length is close to noise by comparison: 0.91x to 1.08x across every word band.

## A caveat worth carrying

The funnel is a poor fit for LinkedIn organic. Buyers do not move through tidy
stages, and one post reaches all three at once — someone binges your case studies
on Monday and forgets you exist by Friday.

The tiers are still useful as a discipline on what a given post is allowed to do.
Treat them as constraints on the draft, not a journey the reader is on.

**Better: classify by the buying JOB, and keep the funnel word as a label.** The
research the funnel is usually justified with does not describe stages at all — it
describes jobs a buying group revisits in loops and in parallel: identifying the
problem, exploring solutions, building requirements, selecting a supplier,
validating, and building internal consensus. Ask which job a post does, then let
the tier follow from it. The vocabulary survives and the classification stops
being a guess.

`engine/decision/` does this, and will tell you when it cannot: an angle with no
job mapping reports as unclassified rather than defaulting to a tier. **Watch the
unclassified rate.** Above roughly 15% the taxonomy does not describe your corpus,
and a tidy distribution computed from it is worse than no distribution. A first
run on a real calendar reported zero BOFU anywhere, which looked like a strategy
finding and was a coverage artefact: two thirds of one channel's angles were
unmapped, and the unmapped set happened to contain every late-stage angle there
was.

## And do not confuse a calendar with a test

If you plan to A/B test messages, hold everything except the message constant, and
work out first whether you have the audience to resolve anything. Detecting a
realistic difference between message arms needs tens of thousands of impressions.
Below a few thousand followers, organic LinkedIn is a qualitative instrument —
read the comments, not the counts.
