"""EXIT 08: the maker's plate.

States how the page is made and stamps it with the build date and seed. The
AV pair of the wordmark stands alone here as the Factory's seal.
"""

from __future__ import annotations

from ..parts import WORDMARK, base_css, mono, mount, rim
from ..svg import Doc, n, tag
from ..theme import Theme

HEADLINE = "MANUFACTURED, NOT TEMPLATED."
WIDE_COPY = ["EVERY PLATE ON THIS PAGE IS DRAWN BY CODE IN THIS REPOSITORY",
             "AND REBUILT BY GITHUB ACTIONS FROM THE PUBLIC RECORD."]
TALL_COPY = ["EVERY PLATE ON THIS PAGE IS DRAWN BY CODE",
             "IN THIS REPOSITORY AND REBUILT BY GITHUB",
             "ACTIONS FROM THE PUBLIC RECORD."]


def render(data: dict, theme: Theme, layout: str) -> str:
    wide = layout == "wide"
    width, height = (880, 150) if wide else (400, 214)
    pad = 36 if wide else 22
    doc = Doc(width, height, "Exit 08: maker's plate",
              "Every plate on this page is drawn by code in this repository and rebuilt from the public record.")
    doc.style(base_css())
    mount(doc, theme, cut=16 if wide else 14)

    head = 38 if wide else 34
    stamp = f"BUILD {data['captured'].replace('-', '.')} · SEED {data['seed'].upper()}"
    doc.add(mono(pad, head, "EXIT 08", 10.5, theme.red),
            mono(width - pad, head, stamp, 10.5 if wide else 9, theme.dim, "end"))

    # the seal
    seal = WORDMARK.set("AV", pad, head + 20, 44 if wide else 40)
    doc.add(tag("g", seal.shape(stroke=theme.red), clip_path=f"url(#{seal.band(doc)})"))

    # the statement
    column = pad + seal.width + (28 if wide else 20)
    if wide:
        doc.add(mono(column, head + 32, HEADLINE, 10.5, theme.ink))
        for index, row in enumerate(WIDE_COPY):
            doc.add(mono(column, head + 48 + index * 16, row, 9, theme.mute))
    else:
        for index, row in enumerate(HEADLINE.split(", ")):
            doc.add(mono(column, head + 32 + index * 16, row + ("," if index == 0 else ""), 10.5, theme.ink))
        for index, row in enumerate(TALL_COPY):
            doc.add(mono(pad, head + 92 + index * 14, row, 9, theme.mute, spacing=0.12))

    # the line out
    floor = height - 26
    run = width - 2 * pad
    lane = doc.uid("l")
    doc.define(tag("clipPath", tag("rect", x=n(pad), y=n(floor - 3), width=n(run), height="6"), id=lane))
    doc.add(
        tag("path", d=f"M{n(pad)} {n(floor)}H{n(width - pad)}l-5 -5m5 5l-5 5", fill="none", stroke=theme.line2),
        tag("g", tag("rect", x=n(pad - 60), y=n(floor - 1), width="60", height="2", fill=theme.red, class_="out"),
            clip_path=f"url(#{lane})"),
        mono(pad, floor + 15, "HECHO EN CANARIAS", 8.5, theme.mute),
        mono(width - pad, floor + 15, "NO THIRD-PARTY WIDGETS" if wide else "NO WIDGETS", 8.5, theme.mute, "end"),
    )
    doc.style(f"@keyframes out{{0%{{transform:translateX(0)}}60%,100%{{transform:translateX({n(run + 60)}px)}}}}"
              ".out{animation:out 9s linear infinite}")
    rim(doc, theme, cut=16 if wide else 14)
    return doc.render()
