"""Mobile legibility check.

A LinkedIn feed image is shown at roughly 430pt wide. What matters is not the
artboard font size but the *apparent* size once the image is scaled down. The
rule used here: text must be at least 2% of the image height to survive the
feed, and the dominant element at least 6%.
"""
from __future__ import annotations

from typing import Any, Dict, List

MIN_TEXT_RATIO = 0.020      # ~24px on a 1200px artboard
MIN_FOCAL_RATIO = 0.060     # ~72px — the element that has to stop the scroll


def check(measure: Dict[str, Any], height: int, mobile_width: int = 430,
          artboard_width: int = 1200, require_focal: bool = True) -> List[str]:
    """`require_focal` applies to anything that has to stop a scroll on its own:
    a single-image card, or a carousel cover. Interior carousel slides are read
    after the reader has already stopped, so they need legible hierarchy rather
    than a dominant element."""
    problems: List[str] = []
    scale = float(mobile_width) / float(artboard_width)

    smallest = measure.get("smallest_text_px")
    if smallest is not None:
        ratio = float(smallest) / float(height)
        if ratio < MIN_TEXT_RATIO:
            problems.append(
                "smallest text is %.0fpx (%.2f%% of image height, %.1fpx once scaled to a "
                "%dpx feed) — under the %.1f%% floor it will not survive the feed"
                % (smallest, ratio * 100, smallest * scale, mobile_width,
                   MIN_TEXT_RATIO * 100))

    largest = measure.get("largest_text_px")
    if require_focal and largest is not None:
        ratio = float(largest) / float(height)
        if ratio < MIN_FOCAL_RATIO:
            problems.append(
                "the largest element is only %.1f%% of image height — nothing dominates, "
                "so there is no focal point at feed size" % (ratio * 100))
    return problems
