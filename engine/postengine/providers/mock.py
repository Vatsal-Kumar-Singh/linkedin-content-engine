"""Mock provider — used when no API credentials are present.

This is NOT a canned transcript. The mock generator composes a draft from the
content spec, the mock judge measures that draft against independent heuristics,
and the mock generator's revision step *actually consumes the structured
feedback* — so V2 improves because the feedback changed the text, not because
the iteration counter went up.

That makes the whole pipeline — validation, isolation, iteration, persistence,
rendering — genuinely exercisable offline. It does not make the copy
model-quality. Every artifact produced this way is stamped `mode: mock`.
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from .base import Provider

# ---------------------------------------------------------------------------
# Content bank. One entry per pain point the mock can write about.
# Every line here is written to pass the deterministic gates.
# ---------------------------------------------------------------------------

BANK: Dict[str, Dict[str, Any]] = {
    "A1": {
        "focal": "No ceiling",
        "eyebrow": "COMMERCIAL MODEL",
        "deck": "Every enhancement is a change order. That is not a *budget*.",
        "qualifier": "",
        "strip": [{"label": "Instead", "value": "One fixed price per org, per month"},
                  {"label": "Included", "value": "Enhancements, not change orders"}],
        "frag": "Every scope change reopens the contract.",
        "weak_hook": "Let's talk about why silent pipeline failures are quietly becoming one of the biggest problems in modern data teams today",
        "strong_hook": "Your pipeline broke on Sunday. You found out Tuesday.",
        "status_quo": "Every enhancement is priced separately. Every scope change reopens the contract. The annual number you approved was a starting position, not a total.",
        "inaction": "Finance sees a platform that costs more every year without anyone being able to say what next year costs. That is not a forecasting problem. It is a contract structure.",
        "turn": "A fixed price per org per month prices the outcome instead of the effort. Enhancements stop being events that need approving.",
        "artifact": "Three questions worth asking before you sign the next statement of work:\n\n1. What is the total cost of this platform next year, contractually?\n2. Which changes are included, and which reopen the contract?\n3. Who is accountable if the outcome does not arrive?",
        "cta": "Which of those three does your current contract actually answer?",
        "checklist": [
            "\"What does this platform cost next year, contractually?\"",
            "\"Which changes are included, and which reopen the contract?\"",
            "\"Who is accountable if the outcome does not arrive?\"",
        ],
    },
    "B1": {
        "focal": "60",
        "focal_unit": "%",
        "eyebrow": "CAPACITY",
        "deck": "of admin time goes to *repeat tickets*, not platform improvement.",
        "qualifier": "Illustrative industry figure",
        "strip": [{"label": "Basis", "value": "Illustrative industry figure"},
                  {"label": "Where it goes", "value": "Tickets already solved once"}],
        "prop_a": "Repeat tickets", "prop_b": "Platform work",
        "weak_hook": "Here is something interesting we have noticed about how data analysts actually spend their working week",
        "strong_hook": "Your admins already solved most of this week's tickets.",
        "status_quo": "Password resets, permission-set requests, the same report rebuilt for the fourth time. Work that has an answer, being answered again.",
        "inaction": "You are not short of admin capacity. You are spending it twice — once to solve the problem, and again every time it returns. The roadmap is what pays for it.",
        "turn": "The routine belongs to the system. Exceptions and business judgement belong to people. Getting that line right is the whole job.",
        "artifact": "A rough test you can run this week: pull the last 200 tickets and count how many had been resolved before, in substance, by anyone on the team. If it is over half, the queue is not a staffing problem.",
        "cta": "How much of your admin week would survive that test?",
        "checklist": [
            "\"How many of last week's tickets had been solved before?\"",
            "\"Which of those had a documented answer already?\"",
            "\"What would the team build with that time back?\"",
        ],
    },
    "C1": {
        "focal": "Six months",
        "eyebrow": "CONTINUITY",
        "deck": "of context, gone with one *consultant rotation*.",
        "qualifier": "",
        "strip": [{"label": "What leaves", "value": "Six months of org context"},
                  {"label": "What stays", "value": "Whatever the system recorded"}],
        "frag": "Nobody wrote it down, because nobody needed to.",
        "weak_hook": "Pipeline ownership is one of those hidden costs in modern data work that nobody really budgets for",
        "strong_hook": "Nobody can tell you where that number came from.",
        "status_quo": "Why that automation exists. Which field is load-bearing. What was tried in 2023 and abandoned. None of it is written down, because it never needed to be — the person who knew was still here.",
        "inaction": "The next team rebuilds the same understanding from the same org, and you pay for it at the same hourly rate. It is the only project you fund more than once.",
        "turn": "Knowledge that accumulates in a system instead of a person stops being a rotation risk. Every ticket and every release adds to it.",
        "artifact": "One question that finds the exposure fast: if the two people who know your org best left this quarter, what would the next team have to rediscover — and how long would that take?",
        "cta": "Who are those two people in your org?",
        "checklist": [
            "\"Who are the two people who know this org best?\"",
            "\"What would the next team have to rediscover?\"",
            "\"How long did that take the last time?\"",
        ],
    },
    "D1": {
        "focal": "9–14",
        "focal_unit": "months",
        "eyebrow": "TIME TO VALUE",
        "deck": "Typical time to notice a *silent* pipeline failure.",
        "qualifier": "Contractual target: 90 days to a first governed go-live",
        "strip": [{"label": "Contractual target", "value": "90 days to first governed go-live"},
                  {"label": "Scope", "value": "First governed release in production"}],
        "frag": "Discovery, build and governance run as three handoffs.",
        "weak_hook": "Silent pipeline failures typically go unnoticed for somewhere between two and nine days before anyone reports them",
        "strong_hook": "Your go-live date is a negotiating position.",
        "status_quo": "Discovery front-loads the year. The build hands to a second team. Governance arrives after everything has already shipped.",
        "inaction": "The cost is not the invoice. It is a year of decisions made without the capability you have already bought and are already paying for.",
        "turn": "Ninety days to a first governed go-live is a contractual target, and the scope is deliberate: the first governed release path in production, not a full estate migration.",
        "artifact": "Two things worth writing into the next statement of work: the date of the first governed go-live, and what happens contractually if it moves.",
        "cta": "What is the longest you have waited for a first go-live?",
        "checklist": [
            "\"What is the date of the first governed go-live?\"",
            "\"What is in scope for that first release?\"",
            "\"What happens contractually if it moves?\"",
        ],
    },
    "E1": {
        "focal": "Who signs off?",
        "eyebrow": "GOVERNANCE",
        "deck": "Agentforce is live in your org. The *approval model* for it is not.",
        "qualifier": "",
        "strip": [{"label": "Already live", "value": "Agents that can act in production"},
                  {"label": "Still missing", "value": "The approval path for them"}],
        "frag": "The capability shipped. The governance did not.",
        "weak_hook": "Data trust is becoming a really important consideration now that dashboards are shipping as standard to every department",
        "strong_hook": "An agent can change your production org today.",
        "status_quo": "The platform shipped the capability. The operating model did not ship an approval path, an audit trail, or an escalation route for the moment an agent gets it wrong.",
        "inaction": "The first time someone asks who authorised an automated action, the answer needs to exist already. Reconstructing it afterwards is not governance.",
        "turn": "Human-in-the-loop by design: the system proposes, people decide, and sensitive actions require an approval that is recorded as part of the action.",
        "artifact": "Four questions to ask before an agent touches production:\n\n1. Which actions require a human approval, named in advance?\n2. Where is the record of who approved what, and when?\n3. What is the escalation path when the agent is wrong?\n4. Who owns the outcome — not the tool, the outcome?",
        "cta": "Which of those four can your org answer today?",
        "checklist": [
            "\"Which actions require a human approval?\"",
            "\"Where is the record of who approved what?\"",
            "\"What happens when the agent is wrong?\"",
            "\"Who owns the outcome, not the tool?\"",
        ],
    },
    "F1": {
        "focal": "40",
        "focal_unit": "%+",
        "eyebrow": "UTILISATION",
        "deck": "of pipeline alerts reach *nobody* who can fix them.",
        "qualifier": "Industry estimate",
        "strip": [{"label": "Basis", "value": "Industry estimate"},
                  {"label": "Measured when", "value": "Usually two weeks before renewal"}],
        "prop_a": "Unused at renewal", "prop_b": "In active use",
        "weak_hook": "Licence utilisation is one of those things that only ever seems to come up in the last two weeks before a renewal date",
        "strong_hook": "You are paying for seats nobody opened this quarter.",
        "status_quo": "Utilisation gets measured when procurement asks, which is usually about a fortnight before the renewal conversation, which is far too late to change anything.",
        "inaction": "You walk into the negotiation with an estimate and a hope. The other side walks in with your actual usage data. That asymmetry sets the price.",
        "turn": "Adoption monitored monthly turns the renewal from a defence into a position: here is what is used, here is what is not, here is what we are doing about it.",
        "artifact": "Before your next renewal, get three numbers: licences assigned, licences with a login in the last 30 days, and licences using the feature they were bought for. The gap between the second and third is where the money is.",
        "cta": "Do you have those three numbers today, or only the first?",
        "checklist": [
            "\"How many licences are assigned right now?\"",
            "\"How many logged in during the last 30 days?\"",
            "\"How many use the feature they were bought for?\"",
        ],
    },
}

# Structured creative content for the comparison / journey / framework
# templates. Written to the per-template limits so nothing needs shrinking.
STRUCTURED = {
    "A1": {
        "headline": "Two ways to *price* the same platform",
        "left": "Time and materials", "right": "Fixed per org",
        "compare": [
            {"old": "Every enhancement is quoted", "new": "Enhancements are included"},
            {"old": "Scope change reopens the contract", "new": "Scope moves inside the subscription"},
            {"old": "Next year is a guess", "new": "Next year is a number"},
        ],
        "steps": [
            {"title": "Ask for the ceiling", "body": "Total contractual cost, next year."},
            {"title": "Split the two lists", "body": "Included, versus reopens the contract."},
            {"title": "Name the owner", "body": "Who is accountable for the outcome."},
            {"title": "Price the outcome", "body": "One fixed figure per org, per month."},
        ],
        "statement": "Your the pipeline budget has *no ceiling*. On purpose.",
    },
    "C1": {
        "headline": "What a *rotation* actually costs",
        "left": "Knowledge in people", "right": "Knowledge in the system",
        "compare": [
            {"old": "Context lives in someone's head", "new": "Context is recorded as work happens"},
            {"old": "Every new team re-learns the org", "new": "Every new team starts from the record"},
            {"old": "You fund discovery twice", "new": "You fund it once"},
        ],
        "steps": [
            {"title": "Design", "body": "Decisions captured as they are made."},
            {"title": "Build", "body": "Every change carries its reason."},
            {"title": "Govern", "body": "Approvals are part of the record."},
            {"title": "Operate", "body": "The next team inherits the estate."},
        ],
        "statement": "Your best the pipeline knowledge just *took another job*.",
    },
    "E1": {
        "headline": "Before an agent *touches* production",
        "left": "Today", "right": "Governed",
        "compare": [
            {"old": "Agents act, nobody signs off", "new": "Named actions need a human approval"},
            {"old": "The log is reconstructed later", "new": "The record is part of the action"},
            {"old": "Escalation is improvised", "new": "Escalation is defined in advance"},
        ],
        "steps": [
            {"title": "Propose", "body": "The system drafts the action and shows its reasoning."},
            {"title": "Approve", "body": "A named person clears anything sensitive."},
            {"title": "Record", "body": "Who, what and when are captured as the action runs."},
            {"title": "Escalate", "body": "A defined route for the moment it gets something wrong."},
        ],
        "statement": "An agent can change your *production org* today.",
    },
}


GENERIC = {
    "focal": "The gap",
    "eyebrow": "OPERATING MODEL",
    "deck": "Between what your platform *can* do and what it actually does.",
    "qualifier": "",
    "strip": [],
    "weak_hook": "There is a growing gap between what the the pipeline platform ships and what most organisations are actually able to operate",
    "strong_hook": "Your platform moved on. Your operating model did not.",
    "status_quo": "The capability arrives as standard. The way it gets designed, built, governed and run has not changed in a decade.",
    "inaction": "The difference between what the org can do and what it does is not a technology gap. It is a line item.",
    "turn": "Design, build, govern and operate as one continuous outcome rather than four handoffs.",
    "artifact": "One question worth asking this quarter: which capability did you already buy that nobody has been able to put into production yet?",
    "cta": "What is sitting unused in your org right now?",
    "checklist": ['"What did we already buy that is not in production?"',
                  '"What is stopping it from getting there?"',
                  '"Who owns getting it there?"'],
}


def _bank(pain: str) -> Dict[str, Any]:
    d = dict(GENERIC)
    d.update(BANK.get(pain, {}))
    return d


# ---------------------------------------------------------------------------


class MockProvider(Provider):
    """Deterministic stand-in. `role` decides which behaviour is exercised."""

    is_mock = True
    supports_vision = True

    def __init__(self, model: str = "mock-1", role: str = "generator",
                 family: str = "mock", **kwargs: Any) -> None:
        super().__init__(model, **kwargs)
        self.role = role
        self.name = "mock:" + role
        # Generator and judge get distinct pseudo-families so the independence
        # assertion is a real check even in mock mode.
        self.family = family

    # ------------------------------------------------------------------
    def complete(self, system: str, user: str, *, task: str = "",
                 images: Optional[List[str]] = None,
                 context: Optional[Dict[str, Any]] = None) -> str:
        ctx = context or {}
        if task == "generate":
            return json.dumps(self._generate(ctx))
        if task == "revise":
            return json.dumps(self._revise(ctx))
        if task == "judge":
            return json.dumps(self._judge(ctx))
        if task == "design_critic":
            return json.dumps(self._design_critic(ctx))
        return json.dumps({"error": "mock provider received unknown task %r" % task})

    # ------------------------------------------------------------------
    # GENERATOR
    # ------------------------------------------------------------------
    def _generate(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        spec = ctx.get("spec") or {}
        b = _bank(spec.get("pain_point", ""))
        st = STRUCTURED.get(spec.get("pain_point", ""), {})
        template = spec.get("template", "CARD")
        arc = spec.get("arc", "")
        # The creative headline is a visual object, not a sentence: templates
        # that lead with type get a short one written for the slot.
        head = st.get("headline") or b["strong_hook"]
        statement = st.get("statement") or b["strong_hook"]

        # V1 deliberately opens with the weaker hook — a descriptive, over-long
        # opener is the single most common failure mode in this category, and it
        # is what the judge exists to catch.
        body = "\n\n".join([b["status_quo"], b["inaction"], b["turn"], b["artifact"]])
        draft: Dict[str, Any] = {
            "hook": b["weak_hook"],
            "body": body,
            "cta": b["cta"],
            "creative_headline": (statement if arc == "statement" else
                                  head if arc in ("before -> after", "old way -> new way",
                                                  "problem spiral", "explainer", "editorial")
                                  else b["focal"] + (b.get("focal_unit", "") if b.get("focal_unit") in ("%", "%+", "x", "×") else (" " + b["focal_unit"] if b.get("focal_unit") else ""))),
            "creative_supporting_copy": (_first_sentences(b["inaction"], 1, 120)
                                         if arc == "statement" else b["deck"]),
            "creative_qualifier": b.get("qualifier", ""),
            "creative_strip": b.get("strip", []),
            "prop_label_a": b.get("prop_a", ""), "prop_label_b": b.get("prop_b", ""),
            "frag_note": b.get("frag", ""),
            "focal": b["focal"],
            "focal_unit": b.get("focal_unit", ""),
            "eyebrow": b["eyebrow"],
            "visual_concept": "Big-number card. %s on a deep navy ground, one focal element, "
                              "supporting line beneath, brand lockup bottom-left." % b["focal"],
            "alt_text": "%s — %s" % (b["focal"], b["deck"]),
            "claims_used": _claims_in(b["deck"] + " " + body),
            "claim_qualifiers": _qualifiers_in(b["deck"] + " " + body),
            "sources_used": ["engine/pain-points.md %s" % spec.get("pain_point", "")],
            "hook_alternatives": [b["strong_hook"]],
            "comparison_rows": st.get("compare", []),
            "steps": st.get("steps", []),
            "left_label": st.get("left", "Today"),
            "right_label": st.get("right", "Operated as software"),
            "counter": "01 / 06",
            "first_comment": "",
            "private_reasoning": "MOCK-GENERATOR-PRIVATE — this string must never reach the judge.",
            "private_self_assessment": "I think this is a 3 on every criterion.",
        }
        if template == "DOC":
            draft["slides"] = _slides(b)
        return draft

    # ------------------------------------------------------------------
    def _revise(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the structured feedback. This is where V2 actually comes from."""
        prev: Dict[str, Any] = dict(ctx.get("previous_draft") or {})
        fixes: List[Dict[str, Any]] = list(ctx.get("fixes") or [])
        spec = ctx.get("spec") or {}
        b = _bank(spec.get("pain_point", ""))

        prev["private_reasoning"] = "MOCK-GENERATOR-PRIVATE — revision pass."
        prev["private_self_assessment"] = ""

        for f in fixes:
            crit = str(f.get("criterion") or f.get("id") or "")
            replacement = str(f.get("replacement") or "").strip()

            # C1 / hook — take the judge's replacement wording verbatim if given.
            if crit.startswith("C1"):
                prev["hook"] = replacement or b["strong_hook"]

            # A2.3 — the qualifier must be ON the creative.
            if crit.startswith("A2.3") and not str(prev.get("creative_qualifier", "")).strip():
                prev["creative_qualifier"] = b.get("qualifier") or "Contractual target, not a measured result"

            # A2 — a figure needs its qualifier where the figure appears.
            if crit.startswith("A2"):
                if _has_unqualified_target(prev.get("creative_supporting_copy", "")):
                    prev["creative_supporting_copy"] = _qualify(prev["creative_supporting_copy"])
                if _has_unqualified_target(prev.get("body", "")):
                    prev["body"] = _qualify(prev["body"])

            # C3 / C4 — strip the offending construction.
            if crit.startswith("C3") or crit.startswith("C4"):
                for field in ("hook", "body", "cta", "creative_supporting_copy"):
                    prev[field] = _strip_tells(str(prev.get(field, "")))

            # B4 — length band.
            if crit.startswith("B4"):
                target = f.get("target_band") or {}
                prev["body"] = _fit_length(str(prev.get("body", "")), b,
                                           target.get("unit", "chars"),
                                           target.get("min"), target.get("max"),
                                           str(prev.get("hook", "")), str(prev.get("cta", "")))

            # B12 — CTA.
            if crit.startswith("B12") and not str(prev.get("cta", "")).strip():
                prev["cta"] = b["cta"]

            # DESIGN — the creative gauntlet. Shorten to the slot rather than
            # letting the renderer shrink the type past the legibility floor.
            if crit.startswith("DESIGN"):
                if "HEADLINE" in crit and replacement:
                    prev["creative_headline"] = replacement
                    prev["focal"] = replacement
                else:
                    prev["creative_supporting_copy"] = _first_sentences(
                        str(prev.get("creative_supporting_copy", "")), 1, 110)
                    prev["creative_qualifier"] = _first_sentences(
                        str(prev.get("creative_qualifier", "")), 1, 90)
                    prev["alt_text"] = _first_sentences(str(prev.get("alt_text", "")), 2, 200)

            # B11 — something worth keeping.
            if crit.startswith("B11") and b["artifact"] not in str(prev.get("body", "")):
                prev["body"] = str(prev.get("body", "")).rstrip() + "\n\n" + b["artifact"]

        prev["claims_used"] = _claims_in(str(prev.get("body", "")) + " " +
                                         str(prev.get("creative_supporting_copy", "")))
        prev["claim_qualifiers"] = _qualifiers_in(str(prev.get("body", "")) + " " +
                                                  str(prev.get("creative_supporting_copy", "")))
        return prev

    # ------------------------------------------------------------------
    # JUDGE — measures the draft it is given. It has no access to the
    # generator's state, and no knowledge of which iteration this is.
    # ------------------------------------------------------------------
    def _judge(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        d: Dict[str, Any] = ctx.get("draft") or {}
        # The pain point reaches the judge through the packet's classification
        # block, not through the draft allowlist.
        pain = str(ctx.get("pain_point_id") or d.get("pain_point") or "")
        hook = str(d.get("hook") or "")
        body = str(d.get("body") or "")
        cta = str(d.get("cta") or "")
        caption = "\n".join([hook, body, cta])
        tier = str(d.get("funnel_stage") or "")

        hook_words = len([w for w in hook.split() if w])
        ticks = len(re.findall(r"[✓✔✅]", caption))
        notjust = len(re.findall(r"(?i)\bit'?s not just\b", caption))
        buzz = len(re.findall(
            r"(?i)\b(revolutioni[sz]\w+|game[- ]chang\w+|unlock the power of|seamless\w*|"
            r"cutting[- ]edge|best[- ]in[- ]class|world[- ]class|supercharge)\b", caption))
        sentences = [s for s in re.split(r"[.!?]+", caption) if s.strip()]
        dash_ratio = len(re.findall("—", caption)) / float(max(1, len(sentences)))
        has_artifact = bool(re.search(r"(?m)^\s*(\d[\.\)]|[-•])\s+\S", body)) or \
            bool(re.search(r"(?i)(question|questions|test you can run|three numbers|two things)", body))
        concrete = bool(re.search(r"(?i)(\d|hour|week|month|quarter|renewal|ticket|licence|license|contract)", body))
        product_first = bool(re.search(r"(?i)^(we |our |the product)", body.strip()))

        # ---- reasoning is written BEFORE any score is assigned ----------
        notes: List[str] = []
        notes.append(
            "The hook runs %d words. %s" % (
                hook_words,
                "Under ten and it works at mobile width." if hook_words <= 10 else
                "Over ten words the opening line wraps on a phone and the reader decides "
                "before reaching the point — 65%% of them decide on this line alone."))
        notes.append(
            "The opening %s a loop: %s" % (
                "keeps" if hook_words <= 10 and not hook.lower().startswith(("here is", "here's", "let's", "there is"))
                else "closes",
                "the reader has to keep going to find out what is meant."
                if hook_words <= 10 else
                "it announces the topic rather than opening a question."))
        notes.append("Cost of inaction is %s." % ("stated in concrete terms — time, money or people"
                                                  if concrete else "abstract"))
        notes.append("There %s a reusable artifact in the body — %s." % (
            ("is", "a question set or test the reader would come back to") if has_artifact
            else ("is not", "nothing here is worth saving, which is what the Depth Score rewards")))
        notes.append("Voice: %d buzzword hit(s), %d tick-mark bullet(s), %d 'not just X' construction(s), "
                     "em-dash to sentence ratio %.2f." % (buzz, ticks, notjust, dash_ratio))
        notes.append("Tier reads as %s on buying intent; this is advisory and a human confirms it." % (tier or "unclassified"))

        # ---- scores, derived from what was observed above ---------------
        c1 = 3 if hook_words <= 10 else (2 if hook_words <= 14 else 1)
        if hook.lower().startswith(("here is", "here's", "let's", "there is", "in today")):
            c1 = min(c1, 1)
        c2 = 3 if not product_first else 2
        c3 = 0 if buzz else (2 if ticks > 2 else 3)
        c4 = 3
        if notjust:
            c4 = min(c4, 1)
        if ticks > 2:
            c4 = min(c4, 1)
        if dash_ratio > 0.6:
            c4 = min(c4, 2)

        binary = {
            "B2": not product_first,
            "B3": concrete,
            "B5": len(re.findall(r"(?i)\b(also|separately|second topic)\b", body)) < 2,
            "B7": True,
            "B11": has_artifact,
        }

        fixes: List[Dict[str, Any]] = []
        if c1 < 3:
            fixes.append({
                "criterion": "C1",
                "problem": "The hook is %d words and describes the topic instead of opening a loop."
                           % hook_words,
                "fix": "Replace it with a line under ten words that states the reader's situation "
                       "and leaves the consequence unsaid.",
                "replacement": _bank(pain).get("strong_hook", ""),
            })
        if not binary["B11"]:
            fixes.append({
                "criterion": "B11",
                "problem": "Nothing in the post is worth keeping. Saves are a stronger ranking "
                           "input than likes, and the checkable proxy is a reusable artifact.",
                "fix": "Add a short question set, test or checklist the reader would return to.",
                "replacement": _bank(pain).get("artifact", ""),
            })
        if not binary["B3"]:
            fixes.append({
                "criterion": "B3",
                "problem": "The cost of inaction is asserted but never quantified in time, money or people.",
                "fix": "Name what the status quo costs in one of those three units, or drop the angle.",
                "replacement": "",
            })
        if c3 < 3:
            fixes.append({
                "criterion": "C3",
                "problem": "Buzzword or tick-mark list present — the house style of this category.",
                "fix": "Delete the phrase and state the point plainly.", "replacement": ""})
        if c4 < 3:
            fixes.append({
                "criterion": "C4",
                "problem": "Machine rhythm: %d 'not just X' construction(s), em-dash ratio %.2f, "
                           "%d tick-mark bullet(s)." % (notjust, dash_ratio, ticks),
                "fix": "Cut the construction and convert most em-dashes to full stops.",
                "replacement": ""})
        if not binary["B2"]:
            fixes.append({
                "criterion": "B2",
                "problem": "The body opens with us rather than with the reader's problem.",
                "fix": "Open on the reader's situation. A reader with zero interest in us should "
                       "still get something.", "replacement": ""})

        scored_total = c1 + c2 + c3 + c4
        verdict = "SHIP" if (scored_total >= 11 and all(binary.values()) and c3 > 0) else "REVISE"

        return {
            "reasoning": " ".join(notes),
            "binary": binary,
            "scores": {"C1": c1, "C2": c2, "C3": c3, "C4": c4},
            "verdict": verdict,
            "fixes": fixes,
            "human_flags": [
                "C2 intent tier (%s) is advisory only and needs human confirmation." % (tier or "unset")
            ],
        }

    # ------------------------------------------------------------------
    def _design_critic(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Geometry-based stand-in. It can measure canvas utilisation, type-scale
        contrast and legibility honestly; it cannot judge taste. A vision model
        is required for distinctiveness, editorial quality and stopping power —
        those are reported as unscored rather than guessed."""
        m = ctx.get("measurements") or {}
        issues: List[str] = []
        changes: List[Dict[str, str]] = []

        smallest = float(m.get("smallest_text_px") or 99)
        util = float(m.get("canvas_utilization") or 0)
        ratio = float(m.get("type_scale_ratio") or 0)
        distinct = int(m.get("distinct_type_sizes") or 0)
        overflow = bool(m.get("overflow"))
        guards = m.get("guard_overflows") or []
        headline_words = int(m.get("headline_words") or 0)
        fmt = str(m.get("format") or "CARD")
        template = str(m.get("template") or "")
        # Type-scale contrast is calibrated per composition type, not globally.
        # A stat card leads with a giant figure and should be steep; a
        # structure-led card takes its hierarchy from layout, and a good one
        # sits nearer 3:1. One global threshold would either wave through a flat
        # stat card or condemn a well-built comparison.
        RATIO_FLOOR = {
            "card/big_stat": 8.0,
            "card/editorial": 4.0,
            "card/contrarian": 4.0,
            "card/comparison": 3.0,
            "card/journey": 3.0,
            "card/framework": 3.0,
            "document/editorial": 3.5,
        }
        min_ratio = RATIO_FLOOR.get(template, 6.0 if fmt == "CARD" else 3.5)
        min_util = 0.62 if fmt == "CARD" else 0.55

        if overflow or guards:
            issues.append("Content is clipped or compressed out of view.")
            changes.append({"element": "copy", "problem": "Copy exceeds the slot",
                            "fix": "Shorten the copy or move it to another slide",
                            "replacement": ""})
        if smallest < 24:
            issues.append("Smallest rendered text is %.0fpx — below the mobile floor." % smallest)
        if util and util < min_util:
            changes.append({"element": "composition",
                            "problem": "Canvas utilisation is %.0f%% — the composition "
                                       "floats rather than occupying the page." % (util * 100),
                            "fix": "Enlarge the dominant element or add a structural band",
                            "replacement": ""})
        if ratio and ratio < min_ratio:
            changes.append({"element": "typography",
                            "problem": "Type-scale ratio is only %.1f:1 — everything is "
                                       "roughly the same size, so there is no entry point." % ratio,
                            "fix": "Push the focal element up and the supporting copy down",
                            "replacement": ""})
        if headline_words > 10:
            changes.append({"element": "headline",
                            "problem": "Headline is %d words, too long to work as a visual "
                                       "object" % headline_words,
                            "fix": "Reduce to 10 words or fewer", "replacement": ""})

        measured = {
            "readability": 9 if smallest >= 24 else 5,
            "canvas_utilization": 9 if util >= min_util * 1.16 else (7 if util >= min_util else 4),
            "typography": 9 if ratio >= min_ratio * 1.3 else (7 if ratio >= min_ratio else 4),
            "hierarchy": 8 if distinct >= 4 else 5,
            "focal_point_strength": 8 if ratio >= min_ratio * 1.3 else 6,
        }
        return {
            "verdict": "approve" if not issues and not changes else "revise",
            "scores": measured,
            "unscored": ["visual_distinctiveness", "editorial_quality", "brand_character",
                         "scroll_stopping_power", "looks_generic", "spacing", "brand",
                         "information_density"],
            "critical_issues": issues,
            "changes": changes,
            "measured": {"canvas_utilization": util, "type_scale_ratio": ratio,
                         "smallest_text_px": smallest, "distinct_type_sizes": distinct},
            "reasoning": "Mock design critic: measured geometry only — canvas utilisation "
                         "%.0f%%, type-scale ratio %.1f:1, smallest text %.0fpx. Taste "
                         "criteria are left unscored rather than guessed; a vision-capable "
                         "model is required for those." % (util * 100, ratio, smallest),
        }


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_TARGET_FIGURES = re.compile(
    r"(?i)(\b40\s?[–-]\s?50\s?%|\b70\s?%|\b30\s?[–-]\s?50\s?%|\b15\s?[–-]\s?25\s?%|"
    r"\b2\s?[–-]\s?3\s?[x×]|\b90[\s-]day|\bin 90 days\b|under an hour)")
_QUAL = re.compile(r"(?i)(target|contractual|SLA|estimated|typical|modelled|illustrative|industry estimate)")


def _has_unqualified_target(text: str) -> bool:
    for m in _TARGET_FIGURES.finditer(text or ""):
        lo, hi = max(0, m.start() - 160), min(len(text), m.end() + 160)
        if not _QUAL.search(text[lo:hi]):
            return True
    return False


def _qualify(text: str) -> str:
    def rep(m: "re.Match") -> str:
        return "%s (contractual target)" % m.group(0)
    out, n = _TARGET_FIGURES.subn(rep, text or "", count=1)
    return out if n else text


def _strip_tells(text: str) -> str:
    text = re.sub(r"(?i)\bit'?s not just ([^—,]+)[—,]\s*it'?s\s*", "It is ", text or "")
    text = re.sub(r"(?i)\b(revolutioni[sz]\w+|game[- ]chang\w+|seamlessly|cutting[- ]edge)\b", "", text)
    text = re.sub(r"[✓✔✅]\s*", "", text)
    return re.sub(r"[ ]{2,}", " ", text).strip()


def _fit_length(body: str, b: Dict[str, Any], unit: str, lo: Any, hi: Any,
                hook: str, cta: str) -> str:
    """Trim or extend the body so hook+body+cta lands inside the band."""
    if lo is None or hi is None:
        return body
    lo, hi = int(lo), int(hi)
    overhead = len(hook) + len(cta) + 4 if unit == "chars" else \
        len(hook.split()) + len(cta.split())

    def size(t: str) -> int:
        return (len(t) + overhead) if unit == "chars" else (len(t.split()) + overhead)

    paras = [p for p in body.split("\n\n") if p.strip()]
    while size("\n\n".join(paras)) > hi and len(paras) > 1:
        paras.pop()
    body = "\n\n".join(paras)
    extras = [b["artifact"], b["turn"], b["inaction"], b["status_quo"]]
    i = 0
    while size(body) < lo and i < len(extras):
        if extras[i] not in body:
            body = body.rstrip() + "\n\n" + extras[i]
        i += 1
    return body


def _first_sentences(text: str, n: int, hard_cap: int) -> str:
    """Trim to whole sentences, then to a hard character cap on a word boundary.
    Never mid-word — a clipped word reads as a bug, not as brevity."""
    text = (text or "").strip()
    if not text:
        return text
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = " ".join(parts[:max(1, n)]).strip()
    if len(out) > hard_cap:
        out = out[:hard_cap].rsplit(" ", 1)[0].rstrip(",;:—- ")
    return out


def _claims_in(text: str) -> List[str]:
    out = []
    for m in re.finditer(r"(?i)(\b\d{1,3}\s?%\+?|\b\d{1,3}\s?[–-]\s?\d{1,3}\s?%|"
                         r"\b90[\s-]days?\b|\bnine to fourteen months\b|\b\d{1,2}\s?[–-]\s?\d{1,2}\b)", text or ""):
        v = m.group(0).strip()
        if v not in out:
            out.append(v)
    return out


def _qualifiers_in(text: str) -> List[str]:
    out = []
    for m in _QUAL.finditer(text or ""):
        v = m.group(0).lower()
        if v not in out:
            out.append(v)
    return out


def _slides(b: Dict[str, Any]) -> List[Dict[str, str]]:
    """One skeleton, one arc. Headlines must carry the whole argument on their
    own (rubric B7), so each is a claim rather than a label."""
    slides = [
        {"kind": "cover", "headline": b["strong_hook"], "body": ""},
        {"kind": "point", "headline": "The capability shipped first",
         "body": b["status_quo"]},
        {"kind": "point", "headline": "The cost lands somewhere else",
         "body": b["inaction"]},
    ]
    # The checklist is the part a reader saves, and saves are the ranking
    # signal. One question per slide, headline-only — a headline that needs a
    # body repeating it is two text blocks saying one thing.
    for item in (b.get("checklist") or [])[:4]:
        slides.append({"kind": "point", "headline": item.strip('"'), "body": ""})
    slides.append({"kind": "turn", "headline": "What good looks like", "body": b["turn"]})
    slides.append({"kind": "close", "headline": "The question to take with you",
                   "body": b["cta"]})
    return slides



