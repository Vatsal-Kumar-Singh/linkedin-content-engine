"""Mustache-lite. Enough for our templates, and no dependency.

Supports:
    {{var}}              escaped interpolation
    {{{var}}}            unescaped — for the small set of inline tags we allow
    {{#var}}…{{/var}}    section: repeat over a list, or show when truthy.
                         A list of dicts pushes each dict onto the context.
    {{^var}}…{{/var}}    inverted section
    {{.}}                the current item inside a list section
    {{> partial}}        include another template file, same context
"""
from __future__ import annotations

import html as _html
import os
import re
from typing import Any, Callable, Dict, List, Optional

_SECTION = re.compile(r"\{\{([#^])([\w\.]+)\}\}(.*?)\{\{/\2\}\}", re.DOTALL)
_TRIPLE = re.compile(r"\{\{\{([\w\.]+)\}\}\}")
_VAR = re.compile(r"\{\{([\w\.]+)\}\}")
_DOT_TRIPLE = re.compile(r"\{\{\{\.\}\}\}")
_DOT = re.compile(r"\{\{\.\}\}")
_PARTIAL = re.compile(r"\{\{>\s*([\w\-/]+)\s*\}\}")

# The only markup a content field may carry. Everything else is escaped, so a
# generated string can never inject structure into the page.
_ALLOWED_INLINE = ("em", "b", "u", "s", "br", "span")
_TAG = re.compile(r"</?([a-zA-Z][\w-]*)[^>]*>")


def sanitize_inline(value: str) -> str:
    """Escape everything, then restore only the inline emphasis tags."""
    escaped = _html.escape(str(value or ""), quote=False)
    for tag in _ALLOWED_INLINE:
        escaped = escaped.replace("&lt;%s&gt;" % tag, "<%s>" % tag)
        escaped = escaped.replace("&lt;/%s&gt;" % tag, "</%s>" % tag)
        escaped = escaped.replace("&lt;%s/&gt;" % tag, "<%s/>" % tag)
    return escaped


def _truthy(v: Any) -> bool:
    if isinstance(v, (list, tuple, dict, str)):
        return len(v) > 0
    return bool(v)


def render(template: str, ctx: Dict[str, Any], escape: bool = True,
           partial_dir: Optional[str] = None, _depth: int = 0) -> str:
    if _depth > 6:
        return template

    def partials(text: str) -> str:
        def sub(m: "re.Match") -> str:
            if not partial_dir:
                return ""
            path = os.path.join(partial_dir, m.group(1) + ".html")
            if not os.path.exists(path):
                return ""
            with open(path, "r", encoding="utf-8") as fh:
                return render(fh.read(), ctx, escape=escape,
                              partial_dir=partial_dir, _depth=_depth + 1)
        return _PARTIAL.sub(sub, text)

    def sections(text: str, scope: Dict[str, Any]) -> str:
        while True:
            m = _SECTION.search(text)
            if not m:
                return text
            sigil, name, inner = m.group(1), m.group(2), m.group(3)
            value = scope.get(name, ctx.get(name))
            if sigil == "^":
                out = sections(inner, scope) if not _truthy(value) else ""
            elif isinstance(value, list):
                parts: List[str] = []
                for item in value:
                    if isinstance(item, dict):
                        child = dict(scope)
                        child.update(item)
                        parts.append(interpolate(sections(inner, child), child))
                    else:
                        body = sections(inner, scope)
                        body = _DOT_TRIPLE.sub(lambda _m: _raw(item), body)
                        body = _DOT.sub(lambda _m: _esc(item, escape), body)
                        parts.append(body)
                out = "".join(parts)
            else:
                out = sections(inner, scope) if _truthy(value) else ""
            text = text[:m.start()] + out + text[m.end():]

    def interpolate(text: str, scope: Dict[str, Any]) -> str:
        text = _TRIPLE.sub(lambda m: _raw(scope.get(m.group(1), ctx.get(m.group(1), ""))), text)
        return _VAR.sub(lambda m: _esc(scope.get(m.group(1), ctx.get(m.group(1), "")), escape), text)

    return interpolate(sections(partials(template), ctx), ctx)


def _esc(value: Any, escape: bool) -> str:
    s = "" if value is None else str(value)
    return _html.escape(s, quote=False) if escape else s


def _raw(value: Any) -> str:
    return "" if value is None else str(value)
