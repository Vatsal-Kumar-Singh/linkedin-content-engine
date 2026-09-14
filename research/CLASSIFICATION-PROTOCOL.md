# Classification protocol

What every post in `research/raw/` gets labelled with, and the rules for deciding. This document
is the instrument. If it changes, everything measured with the old version has to be re-read,
so change it deliberately and note the date.

**Version 1 — 2026-09-12.**

---

## Why this is not a keyword classifier

The first attempt matched regular expressions against post text and left **95% of the corpus
unclassified**, which tripped this project's 15% honesty gate. The gate was right. A post reading

> Radio Flyer prototyped their full-size Loop Cargo bike frame in two days. Before Fuse X1, a
> single bike frame prototype took two months and 19 separate prints.

is obviously **validation** — a named customer, a before-and-after, a measured result — and it
matches no keyword pattern, because it never says "case study" or "results". Buying jobs are
semantic. Patterns can find the posts that announce themselves and miss every post that does the
work without naming it, which biases the measurement toward companies with a house style of
labelling their own content. That bias would then be published as a finding about the industry.

**So the posts are read.** The cost is that a reader has to do it; the benefit is that the numbers
mean what they say.

---

## What is machine-read, and never labelled by hand

Format, word count, engagement, date, and whether a post is a repost. These come from the scrape
metadata. Nobody's judgement is involved and nobody's judgement is allowed to override them.

Two limits, stated because they affect what can be claimed:

- **A document carousel cannot be told apart from a photo album.** Both arrive as
  `postImages` with several entries and no marker distinguishes them. Anything this corpus says
  about "multi-image" covers both, and a claim specifically about carousels is not supported.
- **A repost is not the reposter's content.** Posts carrying `header.linkedinUrl` are excluded
  before anything is counted, the same rule `engine/scripts/measure_corpus.py` applies to its
  `original` column. **The excluded fraction is reported per company**, because a page that is
  three-quarters reshares is running a person-led channel with an organisation-shaped amplifier,
  which is a strategy rather than an absence of one.
- **A company below 20 labelled originals does not vote.** A page with sixteen posts and a page
  with fifty do not carry equal weight, and averaging them as equals lets the quietest company
  swing a cell it barely occupies. Thin companies are reported by name with their reshare ratio
  and excluded from every percentage; they are never silently dropped, because *why* a company is
  thin is usually the finding. Set it with `classify_posts.py --min-posts`.

---

## The labels

Exactly one label per post. **Twelve labels, no free text**, so that two passes can be compared.

### Six buying jobs

The question is *what work does this post do for a buyer*, not what the post is about. A post
about a product can be doing problem identification; a post about an award is doing supplier
selection.

| Label | The work it does | Recognising it |
|---|---|---|
| `problem` | Makes a reader see a cost they are already paying | Names a status quo and what it costs. **No solution is sold.** Industry diagnosis, a stat about waste, "most teams still do X" |
| `exploration` | Explains how a category or approach works | Teaching. How it works, what it is, under the hood, a technique explained. The reader is learning, not choosing |
| `requirements` | Helps a buyer build their criteria | Comparison, trade-offs, what to look for, when *not* to use this, buyer's guides, X vs Y |
| `selection` | Argues this supplier is the credible one | Analyst placement, awards, funding, customer counts, partnerships, market entry, certifications, "why teams choose us" |
| `validation` | Proves the thing works | A named customer, a deployment, a measured before-and-after, a benchmark, a demo of real output |
| `consensus` | Arms a champion to sell internally | ROI and business case, security and compliance posture, procurement, TCO, anything addressed to the CFO/CISO/board |

### Five non-buying objectives

Real work, just not buying work. **Counted, never discarded** — a page that is 60% recruitment is
a finding about how that company uses the channel, not a hole in the taxonomy.

| Label | |
|---|---|
| `recruitment` | Hiring, open roles, "join us", team growth as a recruiting pitch |
| `culture` | Anniversaries, welcomes, team photos, values, congratulations, internal celebration |
| `event` | Booths, webinars, conferences, "come see us", registration, recaps of an event |
| `product-news` | A launch, release, version, changelog, feature announcement — **announcement only**. If it explains how the feature works it is `exploration`; if it shows a customer using it, `validation` |
| `csr` | Sustainability, donations, community programmes, awareness days, education outreach |

**On a named person's channel `culture` widens**, and this is the only definition that differs
between the two corpora. A page's culture content is team photos and anniversaries; a person's is
personal and professional narrative — a career move, a lesson learned, appreciating a colleague,
a story with no product in it. **The labels were deliberately not extended** to add a
"personal narrative" category, because a label that exists on one side of the comparison and not
the other makes the two distributions incomparable, which is the entire point of measuring the
person channel against the page.

### One escape hatch

| `unclear` | The post cannot be read confidently — too short, pure link drop, no interpretable text, a language the reader cannot assess |

**`unclear` is the honesty valve and must stay small.** Above 15% of the corpus the instrument is
reporting on itself and the distribution should not be published. Reaching for `unclear` because
a post is *ambiguous between two jobs* is wrong — pick the dominant one. Reach for it only when
there is nothing to read.

---

## Tie-breaking, in order

1. **What would the reader do next?** A post that makes you feel a problem is `problem` even if it
   mentions a product at the end.
2. **The dominant two-thirds wins.** Most posts do a little of several things. Label the bulk.
3. **A customer name plus an outcome is `validation`**, even when the post is framed as a launch.
4. **A hiring post dressed as culture is `recruitment`** if it asks anyone to apply.
5. **An event post that teaches is still `event`** if attending is the ask.
6. Never label from the format. A video can do any job.

---

## Reproducing this

```bash
python research/make_batches.py               # writes research/batches/*.txt
# read each batch, write research/labels/<batch>.tsv as "<post id>\t<label>"
python research/classify_posts.py             # joins labels to metadata and reports
```

`make_batches.py` is deterministic: same corpus, same batches, same order. A second reader can
label the same batches independently and the two files can be compared post by post, which is the
only way to find out whether these labels are stable or are one reader's opinion.
