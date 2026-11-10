"""Shared instrument parts: the plate every module is mounted on, HUD lettering
and the motion rules common to all graphics."""

from __future__ import annotations

from .svg import Doc, n, plate, polygon, tag, text
from .theme import MONO, Theme
from .typeface import Face

# Display cuts of FACTORY CUT used across the instruments.
WORDMARK = Face(width=6.2, cut=1.8, weight=1.35, gap=1.5)
TITLE = Face(width=5.0, cut=1.4, weight=0.95, gap=1.3)
FIGURE = Face(width=5.0, cut=1.4, weight=0.8, gap=1.25)
LABEL = Face(width=5.0, cut=1.4, weight=0.62, gap=1.5)

# Motion is decoration. Anyone who asked their system for less of it gets none.
REDUCED_MOTION = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def base_css() -> str:
    """Rules shared by every document."""
    return f"text{{font-family:{MONO};font-weight:500}}" + REDUCED_MOTION


def mono(x: float, y: float, string: str, size: float = 10.5, fill: str = "#000", anchor: str = "start",
         spacing: float = 0.16, **attributes: object) -> str:
    """Small technical lettering in the visitor's monospace font.

    System fonts differ in width, so the run is pinned with ``textLength``:
    the layout is identical whether the glyphs come from Menlo, Consolas or
    DejaVu, only the letterforms change.
    """
    length = len(string) * size * 0.6 + max(len(string) - 1, 0) * size * spacing
    return tag("text", text(string), x=n(x), y=n(y), font_size=n(size), fill=fill,
               text_anchor=None if anchor == "start" else anchor, textLength=n(length), **attributes)


def mono_width(string: str, size: float = 10.5, spacing: float = 0.16) -> float:
    return len(string) * size * 0.6 + max(len(string) - 1, 0) * size * spacing


def mount(doc: Doc, theme: Theme, cut: float = 16.0, texture: bool = True) -> str:
    """Draw the plate that carries a module and return the id of its clip path.

    The plate is a rectangle with all four corners cut at 45 degrees. A short
    red stroke runs parallel to the top-left cut: the Factory's maker's mark.
    """
    w, h = doc.width, doc.height
    outline = polygon(plate(0.5, 0.5, w - 1, h - 1, cut))
    clip = doc.uid("p")
    fill = doc.uid("f")
    doc.define(
        tag("clipPath", tag("polygon", points=outline), id=clip),
        tag("linearGradient", tag("stop", offset="0", stop_color=theme.bg1)
            + tag("stop", offset="1", stop_color=theme.bg0), id=fill, x1="0", y1="0", x2="0", y2="1"),
    )
    doc.add(tag("polygon", points=outline, fill=f"url(#{fill})"))
    if texture:
        dots = doc.uid("d")
        doc.define(tag("pattern", tag("rect", x="0", y="0", width="1.2", height="1.2", fill=theme.ink,
                                      opacity="0.09" if theme.night else "0.13"),
                       id=dots, width="22", height="22", patternUnits="userSpaceOnUse"))
        doc.add(tag("rect", x="11", y="11", width=n(w - 22), height=n(h - 22), fill=f"url(#{dots})",
                    clip_path=f"url(#{clip})"))
    return clip


def rim(doc: Doc, theme: Theme, cut: float = 16.0) -> None:
    """Draw the plate edge and the maker's mark on top of the module content."""
    w, h = doc.width, doc.height
    doc.add(
        tag("polygon", points=polygon(plate(0.5, 0.5, w - 1, h - 1, cut)), fill="none", stroke=theme.line2),
        tag("path", d=f"M{n(7)} {n(cut + 9)}L{n(cut + 9)} {n(7)}", stroke=theme.red, stroke_width="2"),
    )


def status_dot(x: float, y: float, colour: str, live: bool = True) -> str:
    """A small status lamp; ``live`` lamps breathe."""
    return tag("rect", x=n(x - 3), y=n(y - 3), width="6", height="6", fill=colour, class_="lamp" if live else None)


LAMP_CSS = "@keyframes lamp{0%,100%{opacity:1}50%{opacity:.25}}.lamp{animation:lamp 2.6s ease-in-out infinite}"
