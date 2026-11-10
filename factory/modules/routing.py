"""ROUTING 06: which component runs in which line.

A patch bay. Rows are components, columns are the public lines, and a red
node marks a connection that the project's own repository states. The matrix
is declared in ``registry.json`` and only shows lines that are still public.
"""

from __future__ import annotations

from ..parts import TITLE, base_css, mono, mount, rim
from ..svg import Doc, n, plate, polygon, tag
from ..theme import Theme


def render(data: dict, theme: Theme, layout: str) -> str:
    wide = layout == "wide"
    lines = data["lines"]
    components = [component for component in data["components"] if component["lines"]]
    pad = 36 if wide else 22
    row = 22 if wide else 30
    names = 196 if wide else 152
    width = 880 if wide else 400
    column = min(70 if wide else 44, (width - 2 * pad - names) / max(len(lines), 1))
    grid = pad + names
    captions = [f"{line['index']:02d} {line['name']}" for line in lines]
    size = 9.0  # the slanted captions shrink together until the last one fits inside the plate
    for index, caption in enumerate(captions):
        room = width - 14 - (grid + column * (index + 0.5))
        size = min(size, 9.0 * room / (len(caption) * 9.0 * 0.76 * 0.7071))
    slant = max(len(caption) for caption in captions) * size * 0.76 * 0.7071 + 12  # rise of the captions
    top = (104 if wide else 96) + slant
    height = top + row * len(components) + (30 if wide else 26)

    doc = Doc(width, height, "Routing 06: routing matrix",
              "Components and the lines they run in: "
              + "; ".join(f"{c['name']} in {len(c['lines'])} of {len(lines)} lines" for c in components) + ".")
    doc.style(base_css())
    mount(doc, theme, cut=16 if wide else 14)
    head = 38 if wide else 34
    doc.add(
        mono(pad, head, "ROUTING 06", 10.5, theme.red),
        mono(width - pad, head, "AS STATED BY EACH REPOSITORY", 10.5 if wide else 9, theme.dim, "end"),
        TITLE.draw(doc, "ROUTING MATRIX", pad, head + 20, 24, stroke=theme.ink),
    )

    for index, caption in enumerate(captions):
        cx = grid + column * (index + 0.5)
        doc.add(
            tag("path", d=f"M{n(cx)} {n(top - 8)}V{n(top + row * len(components) - row / 2)}", stroke=theme.line),
            tag("text", caption, x=n(cx + 2), y=n(top - 14), font_size=n(size), fill=theme.dim,
                transform=f"rotate(-45 {n(cx + 2)} {n(top - 14)})", textLength=n(len(caption) * size * 0.76)),
        )
    for position, component in enumerate(components):
        cy = top + row * position + 4
        doc.add(
            mono(pad, cy + 3.5, component["name"], 10 if wide else 9, theme.ink, spacing=0.12),
            tag("path", d=f"M{n(grid)} {n(cy)}H{n(grid + column * len(lines))}", stroke=theme.line),
        )
        if wide:
            doc.add(mono(grid + column * len(lines) + 26, cy + 3.5, component["role"], 9, theme.mute))
        else:
            doc.add(mono(pad, cy + 15, component["role"], 7.5, theme.mute, spacing=0.1))
        for index, line in enumerate(lines):
            cx = grid + column * (index + 0.5)
            if line["index"] in component["lines"]:
                doc.add(tag("polygon", points=polygon(plate(cx - 5, cy - 5, 10, 10, 3)), fill=theme.red,
                            class_=f"k{index % 4}"))
            else:
                doc.add(tag("rect", x=n(cx - 1), y=n(cy - 1), width="2", height="2", fill=theme.mute))
    doc.style("@keyframes node{0%,100%{opacity:1}50%{opacity:.55}}"
              + "".join(f".k{i}{{animation:node 4s ease-in-out {i}s infinite}}" for i in range(4)))
    rim(doc, theme, cut=16 if wide else 14)
    return doc.render()
