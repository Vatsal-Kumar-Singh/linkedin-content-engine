"""The registry is what the GENERATOR reads, so it must obey the content rules.

`Generator._brief()` pulls each pain's title and value from `config/registry.yaml`,
falling back to the spec only when the registry has no entry. So the registry —
not any markdown document you keep beside it — is what actually reaches the model.

On the original project it was never resynced after two rewrites. Eight of
twenty-nine entries carried language a gate refuses outright, seven fed unsourced
numbers to the model as fact, and twenty-eight of twenty-nine never said the
subject word, while the prompt sitting beside them insisted on all three. Nothing
detected it, because nothing checked the registry against the rules.
"""
import io
import os
import re
import unittest

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _rules():
    with io.open(os.path.join(ROOT, "config", "claim-rules.yaml"), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _find(node, rule_id):
    if isinstance(node, dict):
        if node.get("id") == rule_id:
            return node
        for v in node.values():
            hit = _find(v, rule_id)
            if hit:
                return hit
    if isinstance(node, list):
        for v in node:
            hit = _find(v, rule_id)
            if hit:
                return hit
    return None


def _registry():
    with io.open(os.path.join(ROOT, "config", "registry.yaml"), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class TestRegistryObeysTheContentRules(unittest.TestCase):
    def setUp(self):
        self.pains = _registry().get("pain_points") or {}
        self.assertTrue(self.pains, "registry has no pain points — this test would "
                                    "otherwise pass vacuously")

    def test_no_banned_language_reaches_the_brief(self):
        """Whatever gate C0.2 refuses in a draft, the registry must not feed in.

        Covers the family sentences and eyebrows as well as the pains. The
        generator's brief prints all three, and a mutation planting a banned
        phrase in a FAMILY line survived a version of this test that only looked
        at pain points — the same partial-coverage mistake that let a CTA guard
        check three templates out of seven.
        """
        pat = re.compile(_find(_rules(), "C0.2")["pattern"])
        reg = _registry()
        bad = []
        for pid, v in self.pains.items():
            blob = "%s %s" % (v.get("title", ""), v.get("value", ""))
            m = pat.search(blob)
            if m:
                bad.append("pain %s: %r" % (pid, m.group(0)))
        for key in ("families", "eyebrows"):
            for fid, text in (reg.get(key) or {}).items():
                m = pat.search(str(text))
                if m:
                    bad.append("%s %s: %r" % (key[:-3], fid, m.group(0)))
        for key in ("brandline", "meta_label", "positioning_line"):
            m = pat.search(str(reg.get(key) or ""))
            if m:
                bad.append("%s: %r" % (key, m.group(0)))
        self.assertFalse(bad, "gate C0.2 refuses these in a draft, yet the generator "
                              "is handed them in its brief: %s" % bad)

    def test_no_unsourced_figures_are_stated_as_fact(self):
        """A number in the brief is a number the model will repeat. Anything with
        a figure needs an entry in your evidence register, so keep them out of the
        register unless you have checked."""
        withnums = [pid for pid, v in self.pains.items()
                    if re.search(r"\d+\s?%|[$£€]\s?\d",
                                 "%s %s" % (v.get("title", ""), v.get("value", "")))]
        self.assertFalse(withnums,
                         "these pains carry a figure the model will treat as fact; "
                         "check your evidence register before allowing them: %s" % withnums)

    def test_the_star_pains_name_the_subject_word(self):
        """Starred pains stand in for their family, so their wording is what the
        model imitates most."""
        pat = re.compile(_find(_rules(), "C0.1")["pattern"])
        for pid, v in self.pains.items():
            if not v.get("star"):
                continue
            blob = "%s %s" % (v.get("title", ""), v.get("value", ""))
            self.assertIsNotNone(pat.search(blob),
                                 "%s is a star pain and never names the subject" % pid)

    def test_every_pain_belongs_to_a_declared_family(self):
        fams = set(_registry().get("families") or {})
        orphans = [p for p, v in self.pains.items() if v.get("family") not in fams]
        self.assertFalse(orphans, "pains with no family entry: %s" % orphans)


if __name__ == "__main__":
    unittest.main()
