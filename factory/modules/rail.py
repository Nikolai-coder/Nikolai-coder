"""RAIL: the conveyor that runs between stations.

A thin strip with a carriage travelling along it on the same nine second
loop as the gate. It is drawn once per shift and shared by every plate, so a
visitor downloads it once.

The rail also does a job. Each plate on the page is two image slots: in one
shift a slot shows the plate, in the other it shows this rail. That is what
lets the page switch by colour scheme and by screen width at the same time
inside GitHub's sanitizer; ``readme.py`` explains the mechanism. Because a
rail can end up on a page of the opposite scheme, it uses mid tones that
read on both backgrounds.
"""

from __future__ import annotations

from ..parts import REDUCED_MOTION
from ..svg import Doc, n, tag
from ..theme import Theme

WIDTH, HEIGHT = 880, 20
LOOP = 9  # seconds, the same period as the pulse on the gate
GRID = 22  # the dot grid of the plates


def render(theme: Theme) -> str:
    doc = Doc(WIDTH, HEIGHT, "Conveyor rail")
    line = HEIGHT / 2
    ticks = range(GRID, WIDTH, GRID)
    minor = "".join(f"M{n(x)} {n(line)}v4" for i, x in enumerate(ticks, 1) if i % 5)
    major = "".join(f"M{n(x)} {n(line)}v7" for i, x in enumerate(ticks, 1) if not i % 5)
    doc.add(
        tag("path", d=f"M0 {n(line)}H{WIDTH}M1 {n(line - 5)}v10M{WIDTH - 1} {n(line - 5)}v10",
            stroke=theme.mute, stroke_width="1.5", fill="none"),
        tag("path", d=minor, stroke=theme.mute, stroke_width="1.5", opacity="0.55"),
        tag("path", d=major, stroke=theme.mute, stroke_width="1.5"),
        tag("rect", x="-34", y=n(line - 2.5), width="34", height="5", fill=theme.red, class_="car"),
    )
    doc.style(
        f"@keyframes car{{to{{transform:translateX({WIDTH + 34}px)}}}}"
        f".car{{animation:car {LOOP}s linear infinite}}",
        REDUCED_MOTION,
    )
    return doc.render()
