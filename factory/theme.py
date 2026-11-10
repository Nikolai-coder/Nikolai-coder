"""Colour and type tokens.

The Factory runs two shifts. NIGHT is served to visitors whose system prefers
a dark scheme, DAY to everyone else. Both are complete designs, not an
inversion: night is a lit control room, day is a printed specification sheet.
Every module draws from these tokens only, so the two shifts never drift.
"""

from __future__ import annotations

from dataclasses import dataclass

MONO = 'ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace'


@dataclass(frozen=True)
class Theme:
    name: str  # "night" | "day"
    shift: str  # wording shown on the gate
    bg0: str  # deepest surface
    bg1: str  # plate surface
    bg2: str  # raised surface
    line: str  # hairline
    line2: str  # stronger hairline
    ink: str  # primary type
    dim: str  # secondary type
    mute: str  # tertiary type, annotations
    red: str  # the signal colour
    violet: str  # the secondary accent
    sheen: str  # core of the light that scans the wordmark
    glow: bool  # are light effects (glows, sheens) drawn?

    @property
    def night(self) -> bool:
        return self.name == "night"


NIGHT = Theme(
    name="night", shift="NIGHT SHIFT",
    bg0="#07060A", bg1="#0C0A11", bg2="#14111B",
    line="#272231", line2="#3D3649",
    ink="#EDE7DB", dim="#A49EAF", mute="#6E687A",
    red="#FF2E4D", violet="#8B5CF6", sheen="#FFFFFF",
    glow=True,
)

DAY = Theme(
    name="day", shift="DAY SHIFT",
    bg0="#F5F1E9", bg1="#EFEADF", bg2="#E7E1D4",
    line="#D6CFC1", line2="#BCB4A4",
    ink="#16121C", dim="#57515F", mute="#8B8593",
    red="#C8102E", violet="#6D28D9", sheen="#16121C",
    glow=False,
)

THEMES = (NIGHT, DAY)
