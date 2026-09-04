---
name: linkedin-post
description: Write a LinkedIn post for the product — hook, caption, on-image copy, hashtags and distribution. Use when drafting or reviewing any LinkedIn post, choosing a TOFU/MOFU/BOFU tier, deciding what goes on the creative versus in the caption, or setting hashtags. Carries the 2026 platform mechanics that decide whether a post travels.
---

# Writing a LinkedIn post

Work through these in order. Each step has a reference file with the evidence
and the detail; the rules here are the short version.

The single most important thing to know before writing anything: **hashtags no
longer distribute your post, the words in the copy do.** LinkedIn retired
hashtag following in 2024, and posts without hashtags now outperform posts with
them by 5–10%. What replaced them is Topic Authority — the platform reads your
full copy and builds a topic fingerprint from it. See `references/distribution.md`.

---

## 1. Fix the tier before you write a word

TOFU, MOFU and BOFU are not tones, they are three different jobs. The fastest
check, and the one that catches most misclassification in seconds:

| Tier | Is | If your draft… |
|---|---|---|
| **TOFU** | *what is* | …explains how **we** do something, it is not TOFU |
| **MOFU** | *how to* | …names no alternative to us, it is probably still TOFU |
| **BOFU** | *how WE* | …avoids specifics on scope or price, it is not yet BOFU |

**TOFU names the problem and stops.** No product, no mechanism, no us. Its job
is recognition — "that's my Tuesday". A TOFU post that pitches in the last line
converts nobody and costs the reader who was not in market yet.

Full detail, including why the funnel framing is a poor fit for LinkedIn and
what to do about it: `references/tiers.md`.

## 2. Write the first two lines as though they are the whole post

For most readers they are: **65% never click "see more"**. Keep the first line
under ten words and make it do two jobs at once — stop the scroll, and signal
who the post is for.

The explicit hook formulas ("Unpopular opinion:", "Here's what nobody tells
you") are saturated in 2026 and now read as a tell. Use the underlying lever,
not the announcement of it. `references/hooks.md`.

## 3. Repeat the topic words on purpose

This is the part that replaced hashtags. The algorithm classifies your post from
its copy, so the subject has to be unmistakable in the text itself — not implied,
not in a corner label, not in a tag at the bottom.

For us that means **the subject word appears in the headline and early in the caption**,
every time. This is already a hard gate (C0.1) for copy reasons; it is also how
the post gets distributed. The two reasons happen to agree.

Topic Authority rewards a narrow, consistent subject. Posting across scattered
topics dilutes the fingerprint and the whole account travels worse — which is a
distribution argument for the narrow pain-point focus, not just an editorial one.

## 4. Split the copy between the image and the caption

They are not the same words twice, and they are not unrelated either.

- **The image carries the argument.** It has to work with the caption collapsed,
  because that is how most people meet it.
- **The caption opens by mirroring the image's hook**, then goes somewhere the
  image cannot — the detail, the example, the qualification.
- **A qualifier belongs wherever the claim is.** If a number is on the creative,
  its qualifier is on the creative. Captions truncate; the image does not.

`references/creative-copy.md` has the slot-by-slot rules, carousel cover specs
and the length targets.

## 5. Set hashtags last, and set few

Default **0–3**. Four or five only for an event or campaign. **Ten or more
carries a 30–50% visibility penalty.** They are a lightweight topic signal now,
not a reach driver — so they should restate the subject already in the copy, not
reach for a wider audience.

Never `#AI`, `#Innovation`, `#DigitalTransformation` or anything else that
describes a category rather than this post.

## 6. Before it ships

Run the six-question test in `kb/ad-craft.md` §5, then check:

- [ ] Cover the caption. Does the image still mean something on its own?
- [ ] Is *the subject word* in the first line?
- [ ] First line under ten words?
- [ ] Does the tier match what the post actually does — *what is* / *how to* / *how WE*?
- [ ] Three hashtags or fewer, all restating the subject?
- [ ] Does any number on the creative carry its qualifier on the creative?

---

## Where the evidence lives

The rules above are the actionable form. The sourced research behind them stays
in the knowledge base, and the two must not be edited independently:

- `kb/linkedin-research-2026.md` — format hierarchy, the Depth Score, benchmarks
- `kb/linkedin-niche-scan.md` — what the the subject word niche already does
- `kb/linkedin-content-engine.md` — cadence, pillars, the pipeline
- `kb/ad-craft.md` — Ogilvy, the 95-5 rule, the pre-ship test

The engine writes to the same rules through `engine/prompts/generator.md`. If you
change a rule here, change it there.
