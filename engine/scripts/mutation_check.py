#!/usr/bin/env python3
"""Mutation testing: break things on purpose and check the suite notices.

A green suite proves the tests run. It does not prove they test anything. Of the
first eight mutations below, two survived — and both were covered by tests whose
names claimed to prevent exactly that defect:

  · A CTA rendered onto the creative. The guard iterated a hand-written list of
    three templates out of seven, so it never checked the one Round 1 uses. And
    even once that was fixed it still passed, because `cta` is never placed in
    the slots — so a template referencing it renders empty and the assertion
    succeeds for the wrong reason.

  · Gate C0.1, the requirement that every headline names the subject word, replaced
    with a pattern matching any single letter. The most load-bearing gate in the
    project had no test at all.

Run it after adding a guard, to check the guard actually guards.

Each mutation edits one file, runs the named tests, and restores the file in a
finally block — nothing is left modified even if a run is interrupted.
"""
import io
import os
import subprocess
import sys

ENGINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS = os.path.join(ENGINE, "tests")


def _run(tests):
    """True when the named tests PASS."""
    r = subprocess.run([sys.executable, "-m", "unittest"] + tests,
                       cwd=TESTS, capture_output=True, text=True)
    return r.returncode == 0


def _p(*parts):
    return os.path.join(ENGINE, *parts)


# (description, file to break, how to break it, tests that should catch it)
MUTATIONS = [
    ("banned phrase reaches the generator's brief",
     _p("config", "registry.yaml"),
     lambda s: s.replace("nobody finds out until a dashboard is wrong",
                         "an operating model problem, not a tooling one"),
     ["test_registry_content"]),

    # Added with the contrast guard. Colour contrast was measured by check_palette.py and
    # enforced by nothing, so a brand whose foreground was unreadable on its own background
    # rendered, passed every test, and shipped. That matters most for the case this engine
    # exists to serve: somebody swapping in their own palette, who never touches a template.
    ("foreground colour made unreadable on its own ground",
     _p("config", "brand.yaml"),
     lambda s: s.replace('cloud_white:   "#F7F9FC"', 'cloud_white:   "#0C2036"'),
     ["test_render.TestPaletteIsLegible"]),

    ("animation freeze removed from stills",
     _p("postengine", "render", "renderer.py"),
     lambda s: s.replace("a.currentTime = 0;", "a.currentTime = 0; a.play();"),
     ["test_motion"]),

    ("every stroke given identical weight (depth removed)",
     _p("postengine", "render", "backgrounds.py"),
     lambda s: s.replace('"sw": round(max(0.55, w), 2)', '"sw": round(base_w, 2)'),
     ["test_motion"]),

    ("type-column mask removed from the wash",
     _p("templates", "_shared", "wash.html"),
     lambda s: s.replace('mask="url(#washmask)"', ''),
     ["test_motion"]),

    ("CTA rendered onto the creative",
     _p("templates", "card", "wash", "template.html"),
     lambda s: s.replace('<div class="sign">', '<div class="sign">{{cta}}'),
     ["test_motion"]),

    ("gate C0.1 no longer requires the subject word",
     _p("config", "claim-rules.yaml"),
     # Neuter C0.1 by replacing its pattern with one that matches any letter.
     lambda s: s.replace("(meridian|data pipeline|pipelines?)", "."),
     ["test_claim_rules", "test_pipeline"]),
]


def main():
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__.strip())
        print()
        print("usage: python scripts/mutation_check.py")
        print("       exits 1 if any mutation survives, so CI can gate on it")
        return 0
    print("%-58s %s" % ("MUTATION", "RESULT"))
    print("-" * 78)
    survived, skipped = [], []
    for name, path, mutate, tests in MUTATIONS:
        original = io.open(path, encoding="utf-8").read()
        broken = mutate(original)
        if broken == original:
            # The code moved on and the mutation no longer applies. That is a
            # silent loss of coverage, so say so rather than printing a pass.
            print("%-58s SKIPPED (pattern gone)" % name[:57])
            skipped.append(name)
            continue
        io.open(path, "w", encoding="utf-8").write(broken)
        try:
            passed = _run(tests)
        finally:
            io.open(path, "w", encoding="utf-8").write(original)
        if passed:
            print("%-58s SURVIVED  <-- tests did not notice" % name[:57])
            survived.append(name)
        else:
            print("%-58s caught" % name[:57])

    print()
    print("survived: %d of %d" % (len(survived), len(MUTATIONS)))
    for s in survived:
        print("   -", s)
    if skipped:
        print("stale mutations (no longer apply, coverage unverified): %d" % len(skipped))
        for s in skipped:
            print("   -", s)
    return 1 if survived else 0


if __name__ == "__main__":
    sys.exit(main())
