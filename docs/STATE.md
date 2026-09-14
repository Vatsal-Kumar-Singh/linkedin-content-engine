# Where this project actually stands

Written for whoever picks this up cold — including a future session of the assistant that built
it. It covers what is done, what is half-done, what is blocked and on what, and the things that
went wrong along the way that are worth not repeating.

**Last updated at commit `f8c4c24`.** If the corpus has been re-cut since, run
`python research/verify_figures.py` before trusting any number quoted here or in
[`BENCHMARKS.md`](BENCHMARKS.md).

---

## Read this first: the research is unfinished, and it is blocked

**Nothing here needs redoing. Something here needs finishing.** Four of the five axes are complete
and reported. The fifth — the three-way `offering x motion x stage` cut in [`CELLS.md`](CELLS.md)
— has **13 of 36 cells** above the floor. The other 14 are listed cell by cell below.

**It is blocked on one thing: Apify credit.** All three tokens are at or over their $5 monthly
cap, so nothing can be scraped until one is rotated or the month rolls over. Firecrawl has four
working keys but only resolves LinkedIn slugs; it cannot pull posts.

**To finish it: about 31 more company pages, about $2.50 of Apify credit, and about 1,500 posts to
read by hand.** The order is set out below and step two is not optional — **a human reviews the
candidate list before any credit is spent.** That rule is written into the sample frame, and the
one time it was skipped it put a FedEx executive into a FedEx *supplier's* person sample.

**Also outstanding and blocked on nothing:** the three Apify tokens were pasted into a chat
transcript during this work and should be rotated regardless of what credit they have left.

---

## The one-paragraph version

There are two halves. **The engine** (`engine/`) writes and renders LinkedIn posts and decides
whether a post should exist at all; it is working, tested (207 tests), and carries no measurements
of its own by design. **The research** (`research/`, written up in [`BENCHMARKS.md`](BENCHMARKS.md)
and [`CELLS.md`](CELLS.md)) measures what B2B companies actually publish on LinkedIn, so the
engine's advice is grounded in something. The research is **complete on four axes and incomplete
on the fifth**, and the incompleteness is bounded and costed below.

---

## What is done

### The corpus

| | |
|---|---|
| companies scraped | **77** across a designed frame ([`research/sample-frame.yaml`](../research/sample-frame.yaml)) |
| posts pulled | 3,597 |
| original posts labelled by hand | **3,141** |
| posts carrying the published numbers | **3,114** across the 73 pages clearing a 20-post floor |
| named people paired to those pages | 33, 1,289 posts |
| posts excluded, with a written reason each | 506 (10.1%) |
| labels | 12, defined in [`CLASSIFICATION-PROTOCOL.md`](../research/CLASSIFICATION-PROTOCOL.md) |
| `unclear` rate | 1.4%, against a 15% honesty ceiling |

Every post was **read**. A regex pass was tried first and left 95% unclassified; it is documented
in the protocol as a failure rather than deleted.

### The axes that are complete

- **offering** — saas / product / service
- **motion** — plg / pls / slg / enterprise
- **stage** — early / growth / scaled
- **buyer** — practitioner / manager / exec / procurement (procurement is 3 companies and stays a
  signal, not a result)
- **industry** — 15 verticals at three companies or more

### The axis that is incomplete

**offering x motion x stage**, the three-way cut, reported in [`CELLS.md`](CELLS.md). **13 of 36
cells** clear a three-company floor. See [the gap](#what-is-blocked-and-on-what) below.

### What is written up

| Document | What it holds |
|---|---|
| [`BENCHMARKS.md`](BENCHMARKS.md) | the main findings: content split by every axis, format, text shape, cadence, the person channel, post-shape library, design |
| [`CELLS.md`](CELLS.md) | the three-axis grid, per cell, with named exemplars. Body is generated |
| [`PLAYBOOK.md`](PLAYBOOK.md) | the order the pieces go in when standing this up for a company |
| `.claude/skills/` | the method, as seven skills. Each written from something that went wrong |

### Tooling that exists and works

```bash
python research/scrape_sample.py --all --batch 5     # pull, needs APIFY_TOKENS
python research/resolve_slugs.py --write             # fix the empties, needs FIRECRAWL_API_KEY
python research/make_batches.py --remaining          # only what is unlabelled -> batches_todo/
python research/audit_corpus.py --prune              # write the exclusion view
python research/classify_posts.py --dump research/findings.json
python research/analyse_format.py research/findings.json
python research/analyse_cadence.py
python research/analyse_deeper.py                    # the within-company vote test
python research/analyse_templates.py                 # the post-shape library
python research/analyse_cells.py --grid              # three-axis occupancy, including holes
python research/sample_creative.py --measure-only    # aspect ratio, all image posts
python research/make_calendar.py --cell "saas x plg x early" --deviate
python research/verify_figures.py                    # does the document still match the corpus
```

---

## What is blocked, and on what

**All three Apify tokens are at or over their $5 monthly cap.** Nothing can be scraped until one
is rotated or a month rolls over. Firecrawl has four working keys, but Firecrawl only resolves
LinkedIn slugs — it cannot pull posts.

### The gap, precisely

14 of the 36 three-axis cells are below the three-company floor. Three offering-motion pairs are
**structurally empty** and recorded as such rather than left looking like an oversight:

- `service x plg` — you cannot self-serve a consultancy
- `service x pls` — productised services with a self-serve tier are mostly design subscriptions;
  none met the sample's B2B bar
- `product x pls` — hardware bought on a card that converts to a contract is a thin band between
  PLG and SLG; no clean example found

The rest are fillable. `python research/analyse_cells.py --grid` prints the live list. As of
`f8c4c24`:

| Cell | has | needs |
|---|---:|---:|
| saas x pls x early | 0 | 3 |
| saas x slg x early | 1 | 2 |
| saas x enterprise x early | 0 | 3 |
| product x plg x early | 0 | 3 |
| product x plg x growth | 2 | 1 |
| product x plg x scaled | 1 | 2 |
| product x slg x early | 1 | 2 |
| product x slg x growth | 2 | 1 |
| product x slg x scaled | 1 | 2 |
| product x enterprise x early | 2 | 1 |
| service x slg x early | 1 | 2 |
| service x slg x scaled | 0 | 3 |
| service x enterprise x early | 0 | 3 |
| service x enterprise x growth | 0 | 3 |

**Roughly 31 more companies. About $2.50 of Apify credit and about 1,500 posts to read by hand.**

### The order to do it in

1. Draft the 31 candidates into `sample-frame.yaml` with a stated reason each, on the frame's own
   rule: **a company enters because its cell is missing, not because its content is good.**
2. **Have a human review the list before spending anything.** This is written into the frame and
   it is not ceremony — see [Tier A](#the-mistakes-worth-not-repeating) below for what skipping it
   cost last time.
3. `scrape_sample.py --all` → `resolve_slugs.py --write` for the empties → re-scrape.
4. `make_batches.py --remaining`, read and label into `research/labels/r3_*.tsv`.
5. `audit_corpus.py --prune`, `classify_posts.py --dump`, then every analyse script.
6. `verify_figures.py`, and update the registry in it with any new headline figure.

### Other open items

- **No second-reader reliability pass.** Every label is one reader's judgement applied
  consistently. The protocol exists specifically so a second reader can label the same batches
  independently and the two files be compared post by post. That pass has never been run, and
  until it is, "1.4% unclear" measures confidence rather than accuracy.
- **Engagement is the only outcome signal.** Nothing in this corpus observed a deal. The whole
  first section of `BENCHMARKS.md` exists because reach and commercial value diverge sharply.
- **Follower counts are unknown**, so every paired person-versus-page ratio is confounded. Read
  them as a direction, not a multiple.
- **The design section rests on all 36 coded images**, in `research/creative_sample/` with the
  coding in `coded.tsv`. The aspect-ratio table underneath it rests on all 1,277 image posts and
  is solid. **The coding is not blind** — each filename carries the engagement ratio, so every
  judgement was made knowing the answer. That is the biggest remaining weakness in the section and
  the fix is cheap: a second reader coding shuffled, unlabelled files, which needs no key and no
  credit. One pair (`product-news`) contradicts the rest and is kept for that reason.
- **The type-column mask defect** in the renderer is diagnosed in `CLAUDE.md` and not fixed: a
  three-line headline overflows the dimmed band and the motif crosses the type.

---

## Security and hygiene, before anything is pushed

**This repository must be private, and the reason is concrete.**

1. **No keys, ever.** `APIFY_TOKENS` and `FIRECRAWL_API_KEY` are read from the environment and
   nothing is read from disk. No `.env` is tracked. The tree and the history have been scanned.
2. **The scraped corpus IS tracked, and that is why the repository must stay private.**
   `research/raw/` (77 company pages), `research/raw_people/` (47 profiles) and the three batch
   directories hold **the full text of other companies' LinkedIn posts**, about 24MB. They are
   tracked on the owner's decision so the corpus is reproducible without re-scraping: a new reader
   can re-label and re-audit for free instead of spending about $2.50 of Apify credit and waiting
   on a working token.

   **If this repository is ever made public, those five directories have to come out of the
   history, not just out of the working tree.** Deleting the files in a later commit leaves them
   in every clone, every fork and GitHub's caches. The reversal is `git filter-repo` and a force
   push, and it gets less effective the longer the content has been reachable.
3. **`research/creative_sample/` holds 36 of those companies' creatives**, committed under the
   same decision and the same condition as the post text. They are attributed by filename and in
   the manifest, and they regenerate deterministically from the tracked corpus for free, so if the
   condition ever stops holding they can be removed without losing the ability to check the
   finding.
4. **The branch `virya-local-DO-NOT-PUSH` must never be pushed.** It holds client work for a
   named company. It is not merged into `main` and must not be.

**Outstanding action for a human: rotate the Apify tokens.** Three were pasted into a chat
transcript during this work and should be treated as exposed regardless of what they can still
spend.

---

## The mistakes worth not repeating

Each of these cost real time and each is now guarded in code or in a protocol. They are the most
useful thing on this page.

**A regex classifier cannot find buying jobs.** The first pass matched patterns against post text
and left **95% unclassified**, which tripped the 15% honesty gate. Patterns only find posts that
announce themselves, which biases the result toward companies with a house style of labelling
their own content — and that bias would then have been published as a finding about the industry.
Fix: read every post. Cost: expensive. Benefit: the numbers mean what they say.

**Roughly a third of LinkedIn slugs guessed from a company name are wrong**, measured twice: 14 of
47 in round one, 10 of 28 in round two. Retool is `tryretool`, Ironclad is `ironclad-inc-`,
Sylvera is `sylveracarbon`. **An empty dataset is what a wrong slug and an exhausted quota both
look like**, and neither is the finding "they post nothing". Always resolve before concluding.

**A division of a conglomerate is often a LinkedIn showcase page.** ABB Robotics publishes from
`/showcase/abbrobotics/`; `/company/abb-robotics/` returns nothing. The frame supports a `url:`
override for exactly this.

**The two corpora did not cover the same window.** Company pages were pulled as one recent slice
spanning twelve months. Person feeds were pulled to the same post cap and reached back to **2014**.
LinkedIn in 2014 is not the platform being measured: pre-window person posts are 60.5% text-only
against 35.2% in-window, and the published person/page composition gap was inflated by it.

**Selecting people by "whose posts does this page reshare" conflates employees with everybody
else.** A page reshares its customers, partners and community figures. Four people in the person
sample did not work at the company they were paired to — including a **FedEx executive reshared by
a FedEx supplier**. A paired comparison asking "does this company's person beat this company's
page" is meaningless for them. This is what the human review step in the frame is for.

**A threshold must count usable posts, not pulled ones.** Counting the raw pull let an account
whose every post was later excluded still appear in the headcount while contributing nothing —
which is how a corpus quietly reports more evidence than it holds. Fixing it took the person
sample from 43 to 33.

**Company attributes must be joined from the frame, not from the scrape snapshot.** Each
`raw/<slug>.json` stores a copy of the frame entry as it stood on scrape day. Adding the
`industry` axis in round two therefore gave all 49 round-one companies a null for it, and they
silently formed a `None` bucket of 1,987 posts that printed as a row looking exactly like a real
vertical. The frame is the study design; the raw file is an artefact of one pull.

**A detector that matches 59% of the corpus is broken, not insightful.** The post-shape miner
originally had a `named` opening bucket meant to catch posts opening on a customer's name. Its
test — a capitalised word among the first three — also matched *Today*, *Introducing*, *Most* and
every sentence starting with a proper noun. Three posts in five landed in it, crowding every other
bucket out of the ranking. There is no cheap honest test for a named entity, so the bucket was
deleted rather than widened.

**Backslash escapes do not survive a shell heredoc.** Writing a patch script inline with `<<'PY'`
mangles `\s`, `\b`, `\w` and `\d`, so a regex silently changes meaning and the assertion that was
supposed to catch it fails for the wrong reason. This cost time **three separate times**. Write
patch scripts to a file with the editor tool instead.

**A hard-wrapped document breaks any pattern that encodes one line break.** Match on collapsed
whitespace: `re.compile(r"\s+".join(re.escape(w) for w in old.split()))`.

**`companies:` was not the last key in the frame.** Appending 28 new entries to the end of the
file filed them under `empty_cells:` instead — with no parse error, and a count that silently
stayed at 49. Insert before the next top-level key, and assert the count afterwards.

**Published a false claim about cadence, once.** An early version said cadence does not
differentiate these companies, because post counts came out at a median of 45–48 for every cohort.
That was the **50-post scrape cap**, not behaviour: uniformity produced by a ceiling looks exactly
like uniformity produced by a habit. Measured on span instead, cadence varies thirty-fold. The
correction and its reasoning are kept in `BENCHMARKS.md` rather than quietly edited out.

**A bigger sample mostly demotes findings.** The within-company vote test found four labels
"consistent" on 46 companies and **two** on 73. `product-news` and `culture` crossed back over the
line at 70% and 69%. Nothing reversed; things stopped being reliable. Expect this, report it, and
never quote a corpus median as though it were a rule.

**Verify figures mechanically.** The eye-sweep across a document holding ~150 numbers missed drift
twice. `research/verify_figures.py` now checks a registry of headline figures against the live
corpus and exits non-zero on drift. It cannot catch a *sentence* that has become false beside a
correct number — prose still needs reading.

**Verify the state of an outward-facing thing; do not take it on report.** This repository was
described as private at the moment 24MB of other companies' post text was about to be pushed into
it. One unauthenticated call to the GitHub API said otherwise — `private: false`, readable without
logging in. Costs nothing to check, and the action it gates is irreversible: content that has been
publicly reachable survives in clones, forks and caches after any later deletion.

**A filename that omits the identifier collides, and collides silently.** The creative sampler
named files `job_side_company_ratio.jpg`. Two posts from one company, in one job, on one side,
with the same rounded ratio produce the same name, so the second download overwrote the first.
This happened twice. The manifest went on claiming 36 images beside a directory holding 34, and
every downstream count read the manifest. **A count that is written in one place and checked
nowhere is not a count, it is an assumption.** The name now carries the post id and the script
refuses to finish if the manifest and the directory disagree.

**A refusal written into code is a judgement, not a law.** `sample_creative.py` refused to write
inside the repository because redistributing other companies' creatives seemed wrong. The owner
decided otherwise. The right response is to change the code and state the new condition in it —
not to work around the check, and not to leave a script whose behaviour contradicts the tree it
sits in.

**A document that contradicts the tree is worse than no document.** Three files said "no
third-party post text" on the day that stopped being true. Anyone reading them would have acted on
a rule the repository no longer followed. They moved in the same commit as the change, which is
the only version of this that works: canon lives in exactly one place, and the place has to be
right at every commit rather than eventually.

**Coding that can see the answer finds the pattern it went looking for.** All 36 creatives were
coded against a list fixed in advance, which guards against inventing categories to fit — and the
filenames carried the engagement ratio, which does not guard against anything. The result is a
15-to-2 split that looks much stronger than it is. Fixing it costs nothing but a shuffle and a
second reader. **Fixing the attribute list in advance is half the control; hiding the outcome is
the other half, and only the cheap half was done.**

**A paired design holds the thing you paired on, and nothing else.** The creative sample pairs a
job's best-performing post against its worst, so the *job* is constant — not the caption, the news,
the moment or the audience. Seven jobs showed the same pattern and the eighth inverted it: in
`product-news` a commissioned documentary photograph earned 0.10x and a small low-resolution stock
shot earned 10.25x. **Keep the pair that breaks the pattern.** It is the only thing in the section
that tells a reader how much weight the other seven can carry.

---

## What is deliberately kept in the corpus, and why

An audit removes data that cannot answer the question asked of it. **"Carries no information" is
not the same as "is bad content."** These all stay:

- **One-line posts** — "This is awesome!". Weak content, and a real finding: it is how several
  executives in this sample actually use the channel.
- **Zero-engagement posts.** A real outcome. Dropping them would raise every median by hiding the
  failures.
- **Memes, in-jokes and off-topic posts.** Real decisions with real opportunity costs.
- **Non-English posts.** A finding about who these companies are talking to.
- **Zebra Technologies' identical newsletter blurb, published ten times** — a fifth of its feed.
  Nine copies are excluded as duplicates; the repetition itself is reported.

What goes: posts with no text, posts outside the page corpus window, exact duplicates, people not
employed by the company they were paired to, and **posts LinkedIn's job widget wrote rather than
the company** (28% of one page's feed). Nothing is deleted from `raw/`; `research/excluded.json`
is a filter and every exclusion carries a written reason.
