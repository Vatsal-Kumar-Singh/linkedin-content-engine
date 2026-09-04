---
name: verify-your-tests
description: Check whether the test suite actually tests anything, using mutation testing. Use after adding a guard or a gate, before trusting a green suite, or when a defect ships despite tests covering it. Also covers vacuous test patterns and derived-versus-hardcoded lists.
---

# Verifying the tests

A green suite proves the tests ran. It does not prove they test anything.

## The method

Break one thing on purpose. Run the tests that claim to cover it. If they still
pass, the guard is decorative.

`engine/scripts/mutation_check.py` in this repo does that: each entry names a
defect, a file, an edit that introduces it, and the tests that should catch it. It
restores the file in a `finally` block, so nothing is left modified even if the
run is interrupted, and exits non-zero when a mutation survives so CI can gate on
it.

Run it after adding any guard.

## What it found here

Eight mutations, six caught, **two survived — and both were in tests whose names
claimed to prevent exactly that defect.**

**A guard covering three of seven templates.** The list of templates was
hand-written and had not been updated as templates were added, so the check was
not looking at the one actually in use.

**A guard passing for the wrong reason.** Even after fixing the list, the CTA
check still passed. It asserted the rendered HTML contained no CTA — but the field
is never placed in the slots, so a template referencing it renders *empty* and the
assertion succeeds by coincidence. The day someone adds that field for an
unrelated reason, every dormant reference starts printing. It needed a second
check on the template source.

**A load-bearing gate with no test at all.** The rule requiring the subject word
in every headline could be replaced with a pattern matching any single letter and
the entire suite stayed green. Every gate added later had a test. The oldest and
most important one did not.

## Vacuous patterns to look for

**A loop with no non-empty guard.** `for x in things: self.assertSomething(x)`
passes when `things` is empty. If `things` is derived — parsed from a file,
globbed, computed — assert it is non-empty first. On this project a drift test
would have gone silently vacuous if its parser broke, which is precisely when you
need it.

**A test with no assertion.** Rare, but they exist.

**A `try/except: pass` around the thing under test.**

**A test that would pass if the feature were deleted.** The real question for any
test, and the one mutation testing answers mechanically.

## Prefer derived lists to hand-written ones

Anything enumerating templates, shapes, gates, motifs or config keys should read
them from the filesystem or the config, not from a literal in the test file. A
hardcoded list drifts out of reality while continuing to look correct — and a
partial list is worse than none, because it reports success over the part it
skipped.

## Report what you did not cover

If a mutation no longer applies because the code moved on, say so rather than
counting it as a pass. A stale mutation is lost coverage, not a win. Silent
truncation reads as "covered everything" when it did not.
