"""VAULT 07: sealed bays.

Names the operator has declared but not published. There is no repository to
read, so the plate states exactly that and makes no other claim.
"""

from __future__ import annotations

from ..parts import LABEL, TITLE, base_css, mono, mount, rim
from ..svg import Doc, n, plate, polygon, tag
from ..theme import Theme


def render(data: dict, theme: Theme, layout: str) -> str:
    wide = layout == "wide"
    bays = data["sealed"]
    width = 880 if wide else 400
    pad = 36 if wide else 22
    inner = width - 2 * pad
    gap = 12 if wide else 8
    per_row = len(bays) if wide else 1
    bay_w = (inner - gap * (per_row - 1)) / per_row
    bay_h = 62 if wide else 40
    top = 112 if wide else 106
    rows = -(-len(bays) // per_row)
    height = top + rows * (bay_h + gap) - gap + (44 if wide else 52)

    doc = Doc(width, height, "Vault 07: sealed bays",
              "Declared, not yet public: " + ", ".join(bays) + ".")
    doc.style(base_css())
    mount(doc, theme, cut=16 if wide else 14)
    head = 38 if wide else 34
    doc.add(
        mono(pad, head, "VAULT 07", 10.5, theme.red),
        mono(width - pad, head, "DECLARED, NOT PUBLIC", 10.5 if wide else 9, theme.dim, "end"),
        TITLE.draw(doc, "SEALED BAYS", pad, head + 20, 24, stroke=theme.ink),
    )
    doc.define(tag("pattern", tag("path", d="M-2 10L10 -2M4 14L14 4", stroke=theme.ink, stroke_width="3",
                                  opacity="0.07" if theme.night else "0.09"),
                   id="hz", width="12", height="12", patternUnits="userSpaceOnUse"))
    for index, name in enumerate(bays):
        x = pad + (index % per_row) * (bay_w + gap)
        y = top + (index // per_row) * (bay_h + gap)
        door = polygon(plate(x + 0.5, y + 0.5, bay_w - 1, bay_h - 1, 9))
        cap = 11.0 if wide else 12.0
        cap = min(cap, cap * (bay_w - 46 if not wide else bay_w - 22) / LABEL.measure(name, cap))
        doc.add(
            tag("polygon", points=door, fill=theme.bg2),
            tag("polygon", points=door, fill="url(#hz)", stroke=theme.line2),
            tag("rect", x=n(x + 10), y=n(y + (10 if wide else bay_h / 2 - 3)), width="6", height="6", fill=theme.violet,
                class_=f"w{index % 5}"),
        )
        if wide:
            doc.add(LABEL.draw(doc, name, x + bay_w / 2, y + 23, cap, "middle", stroke=theme.ink),
                    mono(x + bay_w / 2, y + bay_h - 9, f"BAY {index + 1:02d} · SEALED", 7.5, theme.mute, "middle"))
        else:
            doc.add(LABEL.draw(doc, name, x + 28, y + (bay_h - cap) / 2, cap, stroke=theme.ink),
                    mono(x + bay_w - 12, y + bay_h / 2 + 3, f"BAY {index + 1:02d}", 7.5, theme.mute, "end"))
    note = top + rows * (bay_h + gap) - gap + 22
    if wide:
        doc.add(mono(pad, note, "NO PUBLIC REPOSITORY. NOTHING TO VERIFY, SO NOTHING IS CLAIMED.", 9, theme.mute))
    else:
        doc.add(mono(pad, note, "NO PUBLIC REPOSITORY. NOTHING TO VERIFY,", 9, theme.mute),
                mono(pad, note + 14, "SO NOTHING IS CLAIMED.", 9, theme.mute))
    doc.style("@keyframes wait{0%,100%{opacity:.25}50%{opacity:1}}"
              + "".join(f".w{i}{{animation:wait 5s ease-in-out {i}s infinite}}" for i in range(5)))
    rim(doc, theme, cut=16 if wide else 14)
    return doc.render()
