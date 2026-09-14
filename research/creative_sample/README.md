# The creative sample

36 images pulled from the corpus by [`../sample_creative.py`](../sample_creative.py), plus
[`manifest.json`](manifest.json) (what each file is) and [`coded.tsv`](coded.tsv) (the attributes
read off all 36).

## What these are, and whose they are

**These are other companies' copyrighted creatives.** They were published on those companies'
LinkedIn pages; they are reproduced here as a research sample, attributed by filename and in the
manifest, and they are not ours to redistribute further.

**They are committed on the repository owner's decision, and only hold while this repository is
private.** If it is ever made public, this directory has to come out of the *history*, not just
the working tree — see [`../../docs/STATE.md`](../../docs/STATE.md).

If you need the sample and do not have it, you do not need permission and you do not need a
scraping key. It regenerates exactly, from the tracked corpus, for free:

```bash
python research/classify_posts.py --dump research/findings.json
python research/sample_creative.py --out research/creative_sample
```

The sample is deterministic: same corpus, same pairing rule, same 36 files. The script checks
that the manifest and the directory agree before it finishes, because an earlier version named
files without the post id, two names collided, and it wrote 34 files beside a manifest claiming
36 without saying so.

## How the sample was drawn, and why it is paired

For each buying job, the script takes the images from that job's **best-performing** posts and the
images from its **worst-performing** posts, at the same company-normalised scale. Comparing a
strong `validation` creative against a weak `validation` creative holds the content roughly
constant, so a difference that shows up is more likely to be about the design.

Comparing strong creatives against weak ones *across* jobs would only rediscover that awards
outperform buyer's guides, which the rest of the study already establishes.

## What the coding can and cannot support

`coded.tsv` fixes its attribute list **before** the images were opened, so the coding could not
become a search for a story. `aspect` is machine-read from the scrape metadata and is not a
judgement; everything else is one reader's judgement, and no second reader has checked it.

**All 36 are coded, and the coding is not blind.** Each filename carries the post's engagement
ratio, so every judgement was made knowing which side of the pair the image was on. That is how a
coding exercise finds the pattern it went looking for, and it is the main reason the section is
written as a hypothesis rather than a result. **The fix is cheap and has not been done: a second
reader, shuffled files, no ratios in the names.**

The one number in the design section of [`BENCHMARKS.md`](../../docs/BENCHMARKS.md) that *is* a
benchmark is the aspect-ratio table, measured on all 1,277 image posts and needing none of these
files.

**One pair contradicts the rest and is kept for that reason.** `product-news` is the only job
where the weaker post carries the better-made image: Samsara's is a commissioned documentary
photograph of a real warehouse and earned 0.10x, while Flexport's is a small, low-resolution stock
shot and earned 10.25x. A paired design holds the *job* constant, not the caption, the news or the
moment — and that pair is the standing reminder that the creative is not always what moved the
number.
