# The intake: documents and questions

**The goal is to learn as much as possible before recommending anything**, because every weak
recommendation this system could make traces back to something it did not ask.

**Two principles run through this.**

**Ask for artefacts before asking for answers.** People describe their company in marketing language
and describe their documents accurately. A pitch deck reveals positioning that an interview will not.

**Ask about behaviour, never intent.** "Will your CEO post?" gets a yes from everyone. "How many
posts has your CEO written in the last twelve months?" is checkable and predicts the outcome. Every
question below that could be answered aspirationally has been rewritten to ask about the past.

---

# Part A: documents to request

Ranked by what they unlock per minute of effort to obtain.

| Document | What it actually tells you | Substitute if unavailable |
|---|---|---|
| **Investor or pitch deck** | The real positioning, the market they think they are in, the claims they are willing to make to people who do diligence | Website about page plus any funding announcement |
| **Demo or sales call transcripts**, 3 to 5 | **The highest-value item on this list.** The buyer's own words, the objections that actually come up, who else is in the room | Sales team interview, second best by a distance |
| **Lost-deal notes or reasons** | Who blocked it and why. Usually contains the content gap nobody has named | Ask the sales lead for the last five losses |
| **Brand book** | Claims discipline, tone constraints, what is barred, and who owns sign-off | Any existing content guidelines |
| **Product or spec documentation** | What is defensibly true, which sets the Gate | Datasheets, brochures |
| **Existing content inventory with performance** | The Lift baseline. Without it, Lift cannot be computed for this company | Platform exports; even 20 posts with engagement is enough to start |
| **Customer list with segment and deal size** | Who actually buys, which is frequently not who they say they target | Anonymised is fine |
| **Competitor list, from sales rather than marketing** | Who they actually lose to. Often a different list | Ask "who else was in the final round" |
| **Analytics access, read-only** | The observable-metric list in section 8 of the profile | Screenshots of what they can see |
| **Org chart or team list for content** | Who can produce what, which constrains every recommendation | Headcount and roles |

**On transcripts.** Three demo recordings outperform any amount of interviewing, because they
contain the buyer speaking rather than the seller summarising. If only one artefact can be obtained,
make it this one.

---

# Part B: the questions

Each carries **what it decides**, so no question exists for its own sake. Roughly 45 minutes if the
documents arrived first, closer to two hours if they did not.

## Section 1: what is true about the business

1. What do you sell, in the words a customer would use rather than your own?
2. What does it cost, and is that a subscription, a project or a capital purchase?
3. Which geographies, and in which language does the buyer read?
4. How old is the company, and what stage do you consider yourself in?
5. What changed in the business in the last six months that marketing has not caught up with?

**Decides:** profile sections 1 and 2. Question 5 catches the gap between the deck and reality, which
is where most stale content strategies come from.

## Section 2: how it gets bought

6. Walk me through the last deal you won. Who first heard of you, and how?
7. Who signed it, and who else had to agree?
8. **Who could have stopped it?** Including people who never spoke to you.
9. How long from first contact to money?
10. What does the buyer risk if they choose you and it goes wrong?
11. Does your content get forwarded inside the buyer's company? To whom?
12. Can a claim you make be checked by the buyer, and what happens if one is wrong?

**Decides:** buying model, the blocker audience, whether artefacts must survive being forwarded, and
how hard the Gate has to be. **Questions 8 and 12 are the ones most often skipped and most often
decisive.** The blocker is invisible in content planning and decides deals.

## Section 3: the objective

13. If content could only achieve one thing in the next two quarters, what?
14. What is the second thing?
15. **What are you willing to give up to get the first one?**
16. How would you know it worked, without using the word awareness?
17. Who else in the company has an opinion on this, and do they agree?

**Decides:** profile section 3, and therefore every weight. **Question 15 is the whole section.**
Objectives that cost nothing are not objectives, and a company that cannot answer it has not chosen.
Question 17 surfaces the disagreement that will otherwise arrive in month three.

## Section 4: the people who can publish

18. Who at the company will publish under their own name this quarter?
19. **How many original posts has each of them written in the last twelve months?**
20. Do they have a network in the market you sell to, or elsewhere?
21. Has anyone here been burned publishing something? What happened?
22. Who reviews before publication, and how long does that take?
23. If a post gets a hostile comment, who answers it?

**Decides:** whether an executive-led strategy is viable at all, and the realistic cadence.

**Question 19 is the single best failure predictor in this bank.** Stated intent is worthless and
past posting is public. In our own case the answer was four original posts in nine years, which
changed the plan from weekly to something achievable. Question 21 finds the real constraint behind
polite reluctance.

## Section 5: claims and constraints

24. What can you not say, and who decided that?
25. Which customers can be named, and is that in writing?
26. What certifications do you hold, and which are in progress?
27. Is there a figure everyone repeats internally that nobody can source?
28. Who signs off on a claim, and what happens if something wrong ships?
29. **Can a named individual make a claim about your product without creating personal or
    regulatory exposure?** Ask it of the specific people you want publishing, not in general.

**Decides:** the Gate, and one channel decision. **Question 29 is the condition under which the
executive-led split inverts**: where a named person carries the risk, claim-bearing content
belongs on the company page even when the funnel stage says otherwise. `engine/channel.py` reads
it as `named_person_exposure`. **Question 27 finds the unsourced number that is already
circulating**, which
in our experience exists at almost every company and has usually reached a website.

## Section 6: channels and measurement

29. Which channels are you on, who owns each, and how often do you publish?
30. For each: what numbers can you actually see, and where do they come from?
31. **What do you wish you could measure and cannot?**
32. Is anyone searching for what you sell, in the words they would use?
33. Does your buyer know this category exists?
34. When someone hears about you, where do they go to check you are real?

**Decides:** profile sections 5 and 8, and the demand creation versus capture balance. **Question 31
builds the not-observable list**, which is the honesty mechanism. A company that answers "nothing"
has not thought about it.

## Section 7: the corpus

35. Where is everything you have published, and can I have it?
36. What performed best, and do you know why?
37. What flopped that you expected to work?
38. Who do you actually lose deals to, and what do they publish?
39. Has anyone measured any of this, or is it all impression?

**Decides:** whether Lift can be computed at all, and the competitor corpus. **Question 37 is more
informative than 36**, because success has many parents and failure is usually specific.

## Section 8: production reality

40. Who writes, who designs, who approves, and how many hours a week exist?
41. What creative can you produce without a designer?
42. What is the longest your approval chain has ever taken?
43. What broke last time you tried a content push?

**Decides:** what is recommendable at all. **A plan that needs more hours than exist is not a plan.**
In our own case, ruling out video and designed cards on bandwidth cost almost nothing in performance,
because phone photographs measured 436 against 536 for designed carousels.

---

# Part C: the five questions that predict failure

If time is short, these five carry the most weight.

1. **How many original posts has the named executive written in the last twelve months?** (Q19)
2. **What are you willing to give up to get your top objective?** (Q15)
3. **Who could have stopped your last deal?** (Q8)
4. **What do you wish you could measure and cannot?** (Q31)
5. **What broke last time you tried this?** (Q43)

Each has an unhelpful aspirational answer and a checkable factual one. **Take only the factual one.**

---

# Part D: running the intake

**Documents first, then questions.** Reading the deck and three transcripts before talking changes
what you ask and roughly halves the interview.

**Record the answer and the source.** "The CBO said X on 11 Sep" is auditable; "the objective is X"
is not, and in six months nobody will remember who decided.

**Ask the objective question to more than one person separately.** Disagreement here is common,
material, and almost never surfaced voluntarily.

**Write down what you could not find out.** A profile with no gaps has been filled in optimistically.
Unknowns are inputs: they set confidence, and section 9 of the profile reports it.
