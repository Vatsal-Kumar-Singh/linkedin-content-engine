"""Deterministic text-fit validation.

Two layers:
  1. A cheap pre-render character budget, so absurd input never reaches a browser.
  2. Measured geometry after layout — real scrollHeight, real computed font-size.
     Guessing is how templates silently ship clipped text.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# Slot budgets in characters. Generous — this rejects the absurd, not the tight.
BUDGETS: Dict[str, Tuple[int, int]] = {
    "focal": (1, 18),
    "eyebrow": (2, 28),
    "deck": (0, 120),
    "statement": (1, 150),
    "qualifier": (0, 130),
    "headline": (1, 90),
    "sub": (0, 180),
    "copy": (0, 320),
    "left_label": (0, 24),
    "right_label": (0, 24),
}


class FitError(ValueError):
    pass


def precheck(slots: Dict[str, Any]) -> List[str]:
    problems: List[str] = []
    for name, value in slots.items():
        if name not in BUDGETS or value is None:
            continue
        if isinstance(value, list):
            for i, v in enumerate(value):
                problems.extend(_one("%s[%d]" % (name, i), str(v), BUDGETS[name]))
            continue
        problems.extend(_one(name, str(value), BUDGETS[name]))
    return problems


def _one(name: str, value: str, band: Tuple[int, int]) -> List[str]:
    lo, hi = band
    n = len(value.strip())
    if n > hi:
        return ["slot `%s` is %d characters; the template holds %d. "
                "Shorten the copy — do not shrink the type below the mobile floor."
                % (name, n, hi)]
    if lo and n < lo:
        return ["slot `%s` is empty but required" % name]
    return []


# The autofit + measurement script. Runs in the page after fonts are ready.
FIT_JS = r"""
(function(opts){
  function fits(el){
    // Display type is set with line-height below 1, so descenders legitimately
    // overflow their line boxes and scrollHeight exceeds clientHeight by a
    // fraction of the font size. Without this tolerance the autofit shrinks
    // type that fits perfectly well.
    var fs = parseFloat(getComputedStyle(el).fontSize) || 16;
    var tol = Math.max(2, fs * 0.34);
    return el.scrollHeight <= el.clientHeight + tol &&
           el.scrollWidth <= el.clientWidth + 2;
  }
  var adjusted = [];
  var nodes = document.querySelectorAll('[data-fit]');
  for (var i=0;i<nodes.length;i++){
    var el = nodes[i];
    var max = parseFloat(el.getAttribute('data-max')) ||
              parseFloat(getComputedStyle(el).fontSize);
    var min = parseFloat(el.getAttribute('data-min')) || opts.floor;
    var size = max, steps = 0;
    el.style.fontSize = size + 'px';
    while (!fits(el) && size > min && steps < opts.maxSteps){
      size = size * opts.ratio;
      el.style.fontSize = size + 'px';
      steps++;
    }
    if (steps > 0){
      adjusted.push({selector: el.className || el.tagName,
                     from: max, to: Math.round(size*10)/10, steps: steps});
    }
    el.setAttribute('data-final-size', Math.round(size*10)/10);
  }

  // Measure everything AFTER the fitting pass.
  var overflowing = [], clipped = [], smallest = Infinity, texts = [];
  var all = document.querySelectorAll('body *');
  var SKIP = {STYLE:1, SCRIPT:1, TITLE:1, LINK:1, META:1, NOSCRIPT:1};
  for (var j=0;j<all.length;j++){
    var n = all[j];
    if (SKIP[n.tagName]) continue;
    var txt = (n.childNodes.length && n.textContent || '').trim();
    var direct = Array.prototype.filter.call(n.childNodes, function(c){
      return c.nodeType === 3 && c.textContent.trim().length;
    }).length > 0;
    if (direct && txt){
      var fs = parseFloat(getComputedStyle(n).fontSize);
      if (fs < smallest) smallest = fs;
      texts.push({tag:n.tagName, cls:n.className, px:Math.round(fs*10)/10,
                  chars:txt.length});
    }
    // A clipping container that is scrolling is content being silently cut off.
    // This is the case that matters: the page itself never reports it, because
    // the clip happens inside the container.
    var st = getComputedStyle(n);
    var clips = st.overflow === 'hidden' || st.overflow === 'clip' ||
                st.overflowY === 'hidden' || st.overflowY === 'clip';
    // Same tolerance rationale as fits(): descenders from display type set with
    // line-height below 1 overflow the container by a few pixels without any
    // content being lost. Real clipping is tens or hundreds of pixels.
    if (clips && (n.scrollHeight > n.clientHeight + opts.clipTolerance ||
                  n.scrollWidth > n.clientWidth + opts.clipTolerance)){
      clipped.push((n.className || n.tagName) + ' ' +
        n.scrollHeight + '>' + n.clientHeight);
    }
    if (!clips && (n.scrollHeight > n.clientHeight + opts.clipTolerance ||
                   n.scrollWidth > n.clientWidth + opts.clipTolerance)){
      overflowing.push((n.className || n.tagName) + ' ' +
        n.scrollHeight + '>' + n.clientHeight);
    }
  }
  // Content containers that must never be squeezed. A flex child that shrinks
  // paints its overflow underneath the next opaque block, which is invisible to
  // an artboard-level check but loses content just the same.
  var guards = [];
  var gnodes = document.querySelectorAll('[data-overflow-guard]');
  for (var g=0; g<gnodes.length; g++){
    var gn = gnodes[g];
    if (gn.scrollHeight > gn.clientHeight + opts.clipTolerance ||
        gn.scrollWidth > gn.clientWidth + opts.clipTolerance){
      guards.push((gn.className || gn.tagName) + ' ' + gn.scrollHeight + '>' + gn.clientHeight);
    }
  }

  // ---- design measurements ------------------------------------------------
  // Canvas utilisation: the union bounding box of real content (backgrounds and
  // decorative layers excluded) as a share of the artboard. A composition that
  // occupies 45% of its canvas reads as unfinished however good the type is.
  var minX = 1e9, minY = 1e9, maxX = -1e9, maxY = -1e9, contentCount = 0;
  var sizes = [];
  var cnodes = document.querySelectorAll('body *');
  for (var c=0; c<cnodes.length; c++){
    var cn = cnodes[c];
    if (SKIP[cn.tagName]) continue;
    if (cn.closest && cn.closest('.bg')) continue;
    if (cn.classList && (cn.classList.contains('bg') || cn.classList.contains('stage')
        || cn.classList.contains('frame') || cn.classList.contains('spacer'))) continue;
    var hasText = Array.prototype.filter.call(cn.childNodes, function(x){
      return x.nodeType === 3 && x.textContent.trim().length; }).length > 0;
    var isGraphic = cn.tagName === 'svg' || (cn.classList &&
      (cn.classList.contains('bar') || cn.classList.contains('node')
       || cn.classList.contains('panel') || cn.classList.contains('band')));
    if (!hasText && !isGraphic) continue;
    var r = cn.getBoundingClientRect();
    if (r.width < 4 || r.height < 4) continue;
    if (r.right < 0 || r.bottom < 0 || r.left > opts.width || r.top > opts.height) continue;
    minX = Math.min(minX, Math.max(0, r.left)); minY = Math.min(minY, Math.max(0, r.top));
    maxX = Math.max(maxX, Math.min(opts.width, r.right));
    maxY = Math.max(maxY, Math.min(opts.height, r.bottom));
    contentCount++;
    if (hasText) sizes.push(parseFloat(getComputedStyle(cn).fontSize));
  }
  var util = contentCount ? ((maxX-minX)*(maxY-minY))/(opts.width*opts.height) : 0;

  // Ink coverage: the share of the artboard actually occupied by content,
  // sampled on a coarse grid. The union bounding box can read as "full" while
  // the middle of the composition is empty — this is the measure that catches
  // the "headline on a coloured rectangle" failure.
  var STEP = 20, hit = 0, total = 0;
  var boxes = [];
  for (var e=0; e<cnodes.length; e++){
    var en = cnodes[e];
    if (SKIP[en.tagName]) continue;
    if (en.closest && en.closest('.bg')) continue;
    if (en.classList && (en.classList.contains('bg') || en.classList.contains('stage')
        || en.classList.contains('frame') || en.classList.contains('spacer')
        || en.classList.contains('band'))) continue;
    var ht = Array.prototype.filter.call(en.childNodes, function(x){
      return x.nodeType === 3 && x.textContent.trim().length; }).length > 0;
    var gr = en.tagName === 'svg' || (en.classList && (en.classList.contains('bar')
             || en.classList.contains('node') || en.classList.contains('panel')));
    if (!ht && !gr) continue;
    var rb = en.getBoundingClientRect();
    if (rb.width < 4 || rb.height < 4) continue;
    boxes.push(rb);
  }
  for (var px=0; px<opts.width; px+=STEP){
    for (var py=0; py<opts.height; py+=STEP){
      total++;
      for (var bi=0; bi<boxes.length; bi++){
        var bb = boxes[bi];
        if (px >= bb.left && px <= bb.right && py >= bb.top && py <= bb.bottom){ hit++; break; }
      }
    }
  }
  var coverage = total ? hit/total : 0;
  sizes.sort(function(a,b){return b-a;});
  var distinct = [];
  for (var q=0;q<sizes.length;q++){
    if (!distinct.length || Math.abs(distinct[distinct.length-1]-sizes[q]) > 3) distinct.push(sizes[q]);
  }

  var doc = document.documentElement;
  var pageOverflow = doc.scrollHeight > opts.height + opts.clipTolerance ||
                     doc.scrollWidth > opts.width + opts.clipTolerance;

  return {
    adjusted: adjusted,
    overflow: pageOverflow || clipped.length > 0,
    clipped_elements: clipped.slice(0, 8),
    guard_overflows: guards.slice(0, 8),
    overflowing_elements: overflowing.slice(0, 8),
    smallest_text_px: smallest === Infinity ? null : Math.round(smallest*10)/10,
    text_nodes: texts,
    canvas_utilization: Math.round(util*1000)/1000,
    content_coverage: Math.round(coverage*1000)/1000,
    largest_text_px: sizes.length ? sizes[0] : null,
    type_scale_ratio: (sizes.length && sizes[sizes.length-1])
                      ? Math.round((sizes[0]/sizes[sizes.length-1])*10)/10 : null,
    distinct_type_sizes: distinct.length,
    content_elements: contentCount,
    page: {scrollHeight: doc.scrollHeight, scrollWidth: doc.scrollWidth}
  };
})
"""


def evaluate(measure: Dict[str, Any], min_body_px: float, min_caption_px: float,
             fail_on_overflow: bool) -> List[str]:
    """Turn raw geometry into rubric-relevant failures (B9 legibility, overflow)."""
    problems: List[str] = []
    for g in measure.get("guard_overflows") or []:
        problems.append(
            "content container `%s` is compressed — some of it renders behind the "
            "next block and is lost. Shorten the copy or move it to another slide." % g)
    if measure.get("overflow") and fail_on_overflow:
        where = (measure.get("clipped_elements")
                 or measure.get("overflowing_elements") or ["page"])
        problems.append("content is being clipped by the artboard: %s. The copy is "
                        "longer than the slot holds." % "; ".join(where))
    smallest = measure.get("smallest_text_px")
    if smallest is not None and smallest < min_caption_px:
        problems.append(
            "smallest rendered text is %.0fpx, below the %.0fpx caption floor — "
            "rubric B9 requires it to be legible on a phone, not just a laptop"
            % (smallest, min_caption_px))
    for a in measure.get("adjusted") or []:
        if a["to"] < min_body_px and "qualifier" not in str(a["selector"]):
            problems.append(
                "autofit had to shrink `%s` to %.0fpx (below the %.0fpx body floor) "
                "to make the copy fit — the copy is too long for the slot"
                % (a["selector"], a["to"], min_body_px))
    return problems
