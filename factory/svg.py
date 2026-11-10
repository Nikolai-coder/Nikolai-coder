"""Minimal SVG authoring helpers.

Everything the Factory draws is plain SVG text assembled by hand. There is no
templating engine and no dependency: the output has to stay small, diffable and
valid inside GitHub's image sandbox (no scripts, no external resources).
"""

from __future__ import annotations

from xml.sax.saxutils import escape, quoteattr


def n(value: float) -> str:
    """Format a number with at most two decimals and no trailing zeros."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def tag(name: str, content: str | None = None, **attributes: object) -> str:
    """Build one element.

    Keyword names map to attribute names: underscores become dashes and a
    trailing underscore is dropped, so ``class_="x"`` and ``stroke_width=2``
    do what they look like. ``None`` values are skipped.
    """
    parts = [name]
    for key, value in attributes.items():
        if value is None:
            continue
        key = key.rstrip("_").replace("_", "-")
        if isinstance(value, float):
            value = n(value)
        parts.append(f"{key}={quoteattr(str(value))}")
    opening = " ".join(parts)
    if content is None:
        return f"<{opening}/>"
    return f"<{opening}>{content}</{name}>"


def text(value: str) -> str:
    """Escape character data."""
    return escape(value)


def polygon(points: list[tuple[float, float]]) -> str:
    """Return the ``points`` attribute value for a polygon or polyline."""
    return " ".join(f"{n(x)},{n(y)}" for x, y in points)


def path(points: list[tuple[float, float]], closed: bool = False) -> str:
    """Return path data for a straight-segment polyline."""
    head, *tail = points
    data = f"M{n(head[0])} {n(head[1])}" + "".join(f"L{n(x)} {n(y)}" for x, y in tail)
    return data + ("Z" if closed else "")


def plate(x: float, y: float, w: float, h: float, cut: float) -> list[tuple[float, float]]:
    """A rectangle with 45-degree cut corners: the Factory's signature shape."""
    return [
        (x + cut, y), (x + w - cut, y), (x + w, y + cut), (x + w, y + h - cut),
        (x + w - cut, y + h), (x + cut, y + h), (x, y + h - cut), (x, y + cut),
    ]


class Doc:
    """One SVG document: definitions, styles and body collected separately."""

    def __init__(self, width: float, height: float, title: str, desc: str = "") -> None:
        self.width = width
        self.height = height
        self.title = title
        self.desc = desc
        self.defs: list[str] = []
        self.css: list[str] = []
        self.body: list[str] = []
        self._ids: dict[str, int] = {}

    def uid(self, prefix: str) -> str:
        """Return an id that is unique inside this document."""
        count = self._ids.get(prefix, 0)
        self._ids[prefix] = count + 1
        return f"{prefix}{count}"

    def add(self, *fragments: str) -> None:
        self.body.extend(fragments)

    def define(self, *fragments: str) -> None:
        self.defs.extend(fragments)

    def style(self, *rules: str) -> None:
        self.css.extend(rules)

    def render(self) -> str:
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{n(self.width)}" '
            f'height="{n(self.height)}" viewBox="0 0 {n(self.width)} {n(self.height)}" '
            f'role="img" aria-label={quoteattr(self.title)}>'
        )
        out = [head, f"<title>{text(self.title)}</title>"]
        if self.desc:
            out.append(f"<desc>{text(self.desc)}</desc>")
        if self.css:
            out.append("<style>" + "".join(self.css) + "</style>")
        if self.defs:
            out.append("<defs>" + "".join(self.defs) + "</defs>")
        out.extend(self.body)
        out.append("</svg>")
        return "".join(out) + "\n"
