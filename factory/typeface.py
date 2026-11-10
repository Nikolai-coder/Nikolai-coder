"""FACTORY CUT: the display typeface of the DIAVLO Factory.

The letters are not a font file. Each glyph is a stroke skeleton on a small
grid, drawn at build time with a constant stroke weight. That keeps the
identity independent of whatever fonts the visitor has installed: the
wordmark and every title render identically on every device.

Design rules
    * Capital height is 7 units. Corners are cut at 45 degrees ("the cut").
    * Every stroke is horizontal, vertical or at 45 degrees. The only
      exceptions are A and V, the signature pair of DI-AV-LO: both are drawn
      as pure diagonals, and A carries no crossbar so that it mirrors V.
    * Weight is a stroke width, so one skeleton serves every weight.

Diagonals that end on the cap line or the baseline are extended and then
clipped to the cap band, which produces flat, typographically correct
terminals without computing outlines.
"""

from __future__ import annotations

import math
from typing import Callable

from .svg import Doc, n, tag

CAP = 7.0  # capital height in glyph units

Point = tuple[float, float]
Stroke = tuple[list[Point], bool]  # points, closed?
Glyph = tuple[float, list[Stroke]]  # advance (between stem centrelines), strokes


def _octagon(w: float, c: float) -> Stroke:
    return ([(c, 0), (w - c, 0), (w, c), (w, CAP - c), (w - c, CAP), (c, CAP), (0, CAP - c), (0, c)], True)


def _dot(x: float, y: float, w: float) -> Stroke:
    """A square the size of the stroke weight, centred on (x, y)."""
    return ([(x, y - w / 2), (x, y + w / 2)], False)


def _glyphs() -> dict[str, Callable[[float, float, float], Glyph]]:
    """Return the glyph table. Each entry maps (width, cut, weight) to a glyph."""
    g: dict[str, Callable[[float, float, float], Glyph]] = {}
    mid = CAP / 2
    jaw = 0.85  # length of the short vertical terminals on open bowls

    def small(c: float) -> float:
        """Cut used where two bowls are stacked and a full cut would not fit."""
        return min(c, 1.45)

    # -- signature pair ---------------------------------------------------
    g["A"] = lambda W, c, w: (W * 1.04, [([(0, CAP), (W * 0.52, 0), (W * 1.04, CAP)], False)])
    g["V"] = lambda W, c, w: (W * 1.04, [([(0, 0), (W * 0.52, CAP), (W * 1.04, 0)], False)])

    # -- capitals ---------------------------------------------------------
    def B(W, c, w):
        c = small(c)
        k = c * 0.55
        return W, [
            ([(0, 0), (W - c, 0), (W, c), (W, 3.4 - k), (W - k, 3.4), (W, 3.4 + k),
              (W, CAP - c), (W - c, CAP), (0, CAP)], True),
            ([(0, 3.4), (W - k, 3.4)], False),
        ]

    g["B"] = B
    g["C"] = lambda W, c, w: (W, [([(W, c + jaw), (W, c), (W - c, 0), (c, 0), (0, c), (0, CAP - c),
                                   (c, CAP), (W - c, CAP), (W, CAP - c), (W, CAP - c - jaw)], False)])
    g["D"] = lambda W, c, w: (W, [([(0, 0), (W - c, 0), (W, c), (W, CAP - c), (W - c, CAP), (0, CAP)], True)])
    g["E"] = lambda W, c, w: (W * 0.86, [([(W * 0.86, 0), (0, 0), (0, CAP), (W * 0.86, CAP)], False),
                                         ([(0, mid), (W * 0.7, mid)], False)])
    g["F"] = lambda W, c, w: (W * 0.84, [([(W * 0.84, 0), (0, 0), (0, CAP)], False),
                                         ([(0, mid), (W * 0.67, mid)], False)])
    g["G"] = lambda W, c, w: (W, [([(W, c + jaw), (W, c), (W - c, 0), (c, 0), (0, c), (0, CAP - c),
                                   (c, CAP), (W - c, CAP), (W, CAP - c), (W, 3.75), (W * 0.52, 3.75)], False)])
    g["H"] = lambda W, c, w: (W, [([(0, 0), (0, CAP)], False), ([(W, 0), (W, CAP)], False),
                                  ([(0, mid), (W, mid)], False)])
    g["I"] = lambda W, c, w: (0, [([(0, 0), (0, CAP)], False)])
    g["J"] = lambda W, c, w: (W * 0.8, [([(W * 0.8, 0), (W * 0.8, CAP - c), (W * 0.8 - c, CAP), (c, CAP),
                                         (0, CAP - c), (0, CAP - c - jaw)], False)])
    g["K"] = lambda W, c, w: (W, [([(0, 0), (0, CAP)], False),
                                  ([(W, 0), (W, 1.1), (W - 2.5, 3.6), (0, 3.6)], False),
                                  ([(W, CAP), (W, 5.9), (W - 2.0, 3.9)], False)])
    g["L"] = lambda W, c, w: (W * 0.78, [([(0, 0), (0, CAP), (W * 0.78, CAP)], False)])
    g["M"] = lambda W, c, w: (W * 1.28, [([(0, CAP), (0, 0)], False), ([(W * 1.28, 0), (W * 1.28, CAP)], False),
                                         ([(0, 1.0), (W * 0.64, 1.0 + W * 0.64), (W * 1.28, 1.0)], False)])
    g["N"] = lambda W, c, w: (W, [([(0, CAP), (0, 0)], False), ([(W, 0), (W, CAP)], False),
                                  ([(0, (CAP - W) / 2), (W, (CAP + W) / 2)], False)])
    g["O"] = lambda W, c, w: (W, [_octagon(W, c)])

    def P(W, c, w):
        k = c * 0.75
        return W, [([(0, CAP), (0, 0), (W - c, 0), (W, c), (W, 3.9 - k), (W - k, 3.9), (0, 3.9)], False)]

    g["P"] = P
    g["Q"] = lambda W, c, w: (W, [_octagon(W, c), ([(W * 0.56, 4.7), (W * 0.56 + 2.3, CAP)], False)])

    def R(W, c, w):
        k = c * 0.75
        return W, [([(0, CAP), (0, 0), (W - c, 0), (W, c), (W, 3.9 - k), (W - k, 3.9), (0, 3.9)], False),
                   ([(W - 2.0, 4.1), (W, 6.1), (W, CAP)], False)]

    g["R"] = R

    def S(W, c, w):
        c = small(c)
        return W, [([(W, c + jaw), (W, c), (W - c, 0), (c, 0), (0, c), (0, mid - c), (c, mid),
                     (W - c, mid), (W, mid + c), (W, CAP - c), (W - c, CAP), (c, CAP), (0, CAP - c),
                     (0, CAP - c - jaw)], False)]

    g["S"] = S
    g["T"] = lambda W, c, w: (W, [([(0, 0), (W, 0)], False), ([(W / 2, 0), (W / 2, CAP)], False)])
    g["U"] = lambda W, c, w: (W, [([(0, 0), (0, CAP - c), (c, CAP), (W - c, CAP), (W, CAP - c), (W, 0)], False)])
    g["W"] = lambda W, c, w: (W * 1.28, [([(0, 0), (0, CAP)], False), ([(W * 1.28, CAP), (W * 1.28, 0)], False),
                                         ([(0, 6.0), (W * 0.64, 6.0 - W * 0.64), (W * 1.28, 6.0)], False)])
    g["X"] = lambda W, c, w: (W, [([(0, 0), (0, (CAP - W) / 2), (W, (CAP + W) / 2), (W, CAP)], False),
                                  ([(W, 0), (W, (CAP - W) / 2), (0, (CAP + W) / 2), (0, CAP)], False)])
    g["Y"] = lambda W, c, w: (W, [([(0, 0), (0, 3.9 - W / 2), (W / 2, 3.9), (W, 3.9 - W / 2), (W, 0)], False),
                                  ([(W / 2, 3.9), (W / 2, CAP)], False)])
    g["Z"] = lambda W, c, w: (W, [([(0, 0), (W, 0), (W, (CAP - W) / 2), (0, (CAP + W) / 2), (0, CAP),
                                    (W, CAP)], False)])

    # -- figures ----------------------------------------------------------
    g["0"] = lambda W, c, w: (W * 0.9, [_octagon(W * 0.9, small(c)), _dot(W * 0.45, mid, w)])
    g["1"] = lambda W, c, w: (1.6, [([(0, 1.6), (1.6, 0), (1.6, CAP)], False)])

    def two(W, c, w):
        c = small(c)
        return W * 0.9, [([(0, c + jaw), (0, c), (c, 0), (W * 0.9 - c, 0), (W * 0.9, c), (W * 0.9, mid - c),
                           (W * 0.9 - c, mid), (c, mid), (0, mid + c), (0, CAP), (W * 0.9, CAP)], False)]

    g["2"] = two

    def three(W, c, w):
        c = small(c)
        k = c * 0.55
        v = W * 0.9
        return v, [([(0, c + jaw), (0, c), (c, 0), (v - c, 0), (v, c), (v, 3.4 - k), (v - k, 3.4), (v, 3.4 + k),
                     (v, CAP - c), (v - c, CAP), (c, CAP), (0, CAP - c), (0, CAP - c - jaw)], False),
                   ([(v * 0.42, 3.4), (v - k, 3.4)], False)]

    g["3"] = three
    g["4"] = lambda W, c, w: (W * 0.94, [([(W * 0.94 - 1.3, CAP), (W * 0.94 - 1.3, 0), (0, W * 0.94 - 1.3),
                                           (0, 4.9), (W * 0.94, 4.9)], False)])

    def five(W, c, w):
        c = small(c)
        v = W * 0.9
        return v, [([(v, 0), (0, 0), (0, 3.1), (v - c, 3.1), (v, 3.1 + c), (v, CAP - c), (v - c, CAP),
                     (c, CAP), (0, CAP - c), (0, CAP - c - jaw)], False)]

    g["5"] = five

    def six(W, c, w):
        c = small(c)
        v = W * 0.9
        return v, [([(v, c + jaw), (v, c), (v - c, 0), (c, 0), (0, c), (0, CAP - c), (c, CAP), (v - c, CAP),
                     (v, CAP - c), (v, 3.2 + c), (v - c, 3.2), (0, 3.2)], False)]

    g["6"] = six
    g["7"] = lambda W, c, w: (W * 0.88, [([(0, 0), (W * 0.88, 0), (W * 0.88, 1.2), (W * 0.88 - 2.5, 3.7),
                                           (W * 0.88 - 2.5, CAP)], False)])

    def eight(W, c, w):
        c = small(c)
        k = c * 0.55
        v = W * 0.9
        return v, [([(c, 0), (v - c, 0), (v, c), (v, 3.4 - k), (v - k, 3.4), (v, 3.4 + k), (v, CAP - c),
                     (v - c, CAP), (c, CAP), (0, CAP - c), (0, 3.4 + k), (k, 3.4), (0, 3.4 - k), (0, c)], True),
                   ([(k, 3.4), (v - k, 3.4)], False)]

    g["8"] = eight

    def nine(W, c, w):
        c = small(c)
        v = W * 0.9
        return v, [([(0, CAP - c - jaw), (0, CAP - c), (c, CAP), (v - c, CAP), (v, CAP - c), (v, c), (v - c, 0),
                     (c, 0), (0, c), (0, 3.8 - c), (c, 3.8), (v, 3.8)], False)]

    g["9"] = nine

    # -- punctuation ------------------------------------------------------
    g[" "] = lambda W, c, w: (W * 0.42, [])
    g["."] = lambda W, c, w: (0, [_dot(0, CAP, w)])
    g[":"] = lambda W, c, w: (0, [_dot(0, 2.3, w), _dot(0, CAP, w)])
    g["·"] = lambda W, c, w: (0, [_dot(0, mid, w)])
    g["-"] = lambda W, c, w: (W * 0.5, [([(0, mid), (W * 0.5, mid)], False)])
    g["/"] = lambda W, c, w: (W * 0.5, [([(W * 0.5, 0), (0, CAP)], False)])
    g["!"] = lambda W, c, w: (0, [([(0, 0), (0, 4.6)], False), _dot(0, CAP, w)])
    g["+"] = lambda W, c, w: (2.8, [([(0, mid), (2.8, mid)], False), ([(1.4, mid - 1.4), (1.4, mid + 1.4)], False)])
    g[">"] = lambda W, c, w: (1.7, [([(0, mid - 1.7), (1.7, mid), (0, mid + 1.7)], False)])
    g["<"] = lambda W, c, w: (1.7, [([(1.7, mid - 1.7), (0, mid), (1.7, mid + 1.7)], False)])
    return g


GLYPHS = _glyphs()

# Glyphs whose diagonals reach the cap line or baseline and must be clipped flat.
_NEEDS_BAND = set("AVQ/14")

# Pairs whose shapes leave a hole when set at the normal distance (glyph units).
_KERN = {
    ("L", "T"): -0.9, ("L", "Y"): -0.9, ("L", "V"): -0.9, ("T", "A"): -0.9, ("A", "T"): -0.9,
    ("Y", "A"): -0.9, ("A", "Y"): -0.9, ("F", "A"): -0.7, ("P", "A"): -0.7, ("T", "J"): -0.6,
    ("L", "O"): -0.5, ("W", "A"): -0.5, ("A", "W"): -0.5, ("1", "1"): 0.3,
}


class Face:
    """One cut of the typeface: glyph width, corner cut and stroke weight."""

    def __init__(self, width: float = 5.0, cut: float = 1.4, weight: float = 1.0, gap: float = 1.3) -> None:
        self.width = width
        self.cut = cut
        self.weight = weight  # stroke width, glyph units
        self.gap = gap  # clear space between neighbouring stems, glyph units

    # -- layout -----------------------------------------------------------
    def _kern(self, left: str, right: str) -> float:
        if {left, right} == {"A", "V"}:
            # Set the two diagonals parallel with exactly one normal gap between them.
            half = self.width * 0.52
            slope = math.cos(math.atan(half / CAP))
            return -half + (self.gap + self.weight) * (1 / slope - 1)
        return _KERN.get((left, right), 0.0)

    def layout(self, string: str) -> tuple[list[tuple[float, float, list[Stroke]]], float]:
        """Place glyphs on the baseline. Returns [(x, advance, strokes)] and the ink width."""
        placed: list[tuple[float, float, list[Stroke]]] = []
        x = self.weight / 2
        previous = ""
        last_advance = 0.0
        for char in string.upper():
            maker = GLYPHS.get(char)
            if maker is None:
                raise KeyError(f"FACTORY CUT has no glyph for {char!r}")
            advance, strokes = maker(self.width, self.cut, self.weight)
            if previous:
                x += last_advance + self.weight + self.gap + self._kern(previous, char)
            placed.append((x, advance, strokes))
            previous, last_advance = char, advance
        return placed, x + last_advance + self.weight / 2

    def measure(self, string: str, cap: float) -> float:
        """Ink width of ``string`` set at capital height ``cap`` (user units)."""
        return self.layout(string)[1] * cap / CAP

    # -- drawing ----------------------------------------------------------
    def set(self, string: str, x: float, y: float, cap: float, anchor: str = "start") -> "Setting":
        """Set ``string`` with its cap line at ``y`` and return the result."""
        scale = cap / CAP
        placed, ink = self.layout(string)
        width = ink * scale
        origin = x - {"start": 0.0, "middle": width / 2, "end": width}[anchor]
        reach = self.weight * 1.6  # how far diagonal terminals run past the band
        glyphs: list[tuple[str, str, float, float]] = []
        for char, (gx, advance, strokes) in zip(string.upper(), placed):
            data: list[str] = []
            for points, closed in strokes:
                pts = list(points)
                if not closed and len(pts) > 1:
                    pts[0] = _terminal(pts[1], pts[0], advance, self.weight, reach)
                    pts[-1] = _terminal(pts[-2], pts[-1], advance, self.weight, reach)
                head, *tail = [(origin + (gx + px) * scale, y + py * scale) for px, py in pts]
                data.append(f"M{n(head[0])} {n(head[1])}" + "".join(f"L{n(px)} {n(py)}" for px, py in tail)
                            + ("Z" if closed else ""))
            left = origin + (gx - self.weight / 2) * scale
            right = origin + (gx + advance + self.weight / 2) * scale
            glyphs.append((char, "".join(data), left, right))
        return Setting(string.upper(), glyphs, origin, y, width, cap, self.weight * scale)

    def draw(self, doc: Doc, string: str, x: float, y: float, cap: float, anchor: str = "start",
             **attributes: object) -> str:
        """Return finished markup for ``string``."""
        return self.set(string, x, y, cap, anchor).markup(doc, **attributes)


class Setting:
    """A string set in FACTORY CUT: per-glyph path data plus its metrics."""

    def __init__(self, string: str, glyphs: list[tuple[str, str, float, float]], x: float, y: float,
                 width: float, cap: float, stroke: float) -> None:
        self.string = string
        self.glyphs = glyphs  # (character, path data, ink left, ink right)
        self.x = x  # ink left edge
        self.y = y  # cap line
        self.width = width
        self.cap = cap
        self.stroke = stroke  # stroke width, user units

    def data(self, start: int = 0, stop: int | None = None) -> str:
        """Path data for glyphs ``start`` to ``stop``."""
        return "".join(d for _, d, _, _ in self.glyphs[start:stop])

    def span(self, start: int, stop: int) -> tuple[float, float]:
        """Ink extent (left, right) of glyphs ``start`` to ``stop``."""
        chunk = self.glyphs[start:stop]
        return chunk[0][2], chunk[-1][3]

    def band(self, doc: Doc) -> str:
        """Register the clip band that cuts diagonal terminals flat; return its id."""
        band = doc.uid("b")
        doc.define(tag("clipPath", tag("rect", x=n(self.x - self.cap), y=n(self.y - self.stroke / 2),
                                       width=n(self.width + 2 * self.cap), height=n(self.cap + self.stroke)),
                       id=band))
        return band

    def shape(self, start: int = 0, stop: int | None = None, **attributes: object) -> str:
        """A bare stroked path. The caller is responsible for the clip band."""
        return tag("path", d=self.data(start, stop), fill="none", stroke_width=n(self.stroke),
                   stroke_linejoin="miter", stroke_miterlimit="4", **attributes)

    def markup(self, doc: Doc, **attributes: object) -> str:
        """The whole string, clipped only when one of its glyphs needs it."""
        shape = self.shape(**attributes)
        if not _NEEDS_BAND.intersection(self.string):
            return shape
        return tag("g", shape, clip_path=f"url(#{self.band(doc)})")


def _terminal(inner: Point, end: Point, advance: float, weight: float, reach: float) -> Point:
    """Finish an open stroke end so that every glyph fills the same box.

    Strokes are drawn with butt caps on their centrelines, so a stem that stops
    on the cap line would sit half a stroke short of a horizontal bar drawn on
    that same line. Stems and free arms are therefore pushed out by half the
    weight; diagonals are pushed well past the band and clipped flat.
    """
    dx, dy = end[0] - inner[0], end[1] - inner[1]
    on_band = abs(end[1]) < 1e-9 or abs(end[1] - CAP) < 1e-9
    if abs(dx) < 1e-9:  # vertical
        return (end[0], end[1] + math.copysign(weight / 2, dy)) if on_band else end
    if abs(dy) < 1e-9:  # horizontal
        outward = (dx > 0 and abs(end[0] - advance) < 1e-9) or (dx < 0 and abs(end[0]) < 1e-9)
        return (end[0] + math.copysign(weight / 2, dx), end[1]) if outward else end
    if not on_band:
        return end
    length = math.hypot(dx, dy)
    return (end[0] + dx / length * reach, end[1] + dy / length * reach)
