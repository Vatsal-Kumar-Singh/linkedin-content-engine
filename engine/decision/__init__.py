"""Deciding what to publish: Gate, Lift, Fit, and the channel split.

`postengine` writes a post. This decides whether it should exist, on which channel, and
in what form. **It carries no measurements of its own** — every number comes from the
profile of the company being written for, and without one it refuses rather than guessing.
"""
