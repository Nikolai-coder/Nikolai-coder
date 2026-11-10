"""LINE 01..n: one plate per public project.

The left side is lettering and four measured readouts. The right side is a
small working diagram of what the product does, drawn from facts stated in
that project's own README. A project without bespoke art gets the crate.
"""

from __future__ import annotations

from ..parts import FIGURE, LAMP_CSS, TITLE, base_css, mono, mono_width, mount, rim, status_dot
from ..svg import Doc, n, plate, polygon, tag
from ..theme import Theme

Box = tuple[float, float, float, float]  # x, y, width, height

FLOW_CSS = ("@keyframes flow{to{stroke-dashoffset:-28}}"
            ".f1,.f2,.f3{stroke-dasharray:7 21;animation:flow 1.5s linear infinite}"
            ".f2{animation-duration:1.9s}.f3{animation-duration:2.4s}")


def _chip(x: float, y: float, label: str, theme: Theme, size: float = 8.5, **attributes: object) -> tuple[str, float]:
    """An outlined label plate. Returns (markup, width)."""
    width = mono_width(label, size) + 14
    shape = tag("polygon", points=polygon(plate(x + 0.5, y + 0.5, width, 17, 4)), fill="none", stroke=theme.line2)
    return tag("g", shape + mono(x + 7, y + 12.2, label, size, theme.dim), **attributes), width


def _chips(doc: Doc, theme: Theme, labels: list[str], x: float, y: float, limit: float, cycle: bool = False,
           per_row: int = 0) -> None:
    """Lay chips out left to right, wrapping at ``limit`` or every ``per_row``; optionally light them in turn."""
    cursor, row = x, y
    for index, label in enumerate(labels):
        markup, width = _chip(cursor, row, label, theme, class_=f"c{index}" if cycle else None)
        if cursor > x and (cursor + width > limit or (per_row and index % per_row == 0)):
            cursor, row = x, row + 23
            markup, width = _chip(cursor, row, label, theme, class_=f"c{index}" if cycle else None)
        doc.add(markup)
        cursor += width + 6
    if cycle:
        span = len(labels)
        doc.style(f"@keyframes chip{{0%,{n(100 / span)}%,100%{{opacity:.45}}{n(40 / span)}%{{opacity:1}}}}"
                  + "".join(f".c{i}{{opacity:.45;animation:chip {span}s linear {i}s infinite}}" for i in range(span)))


# -- product diagrams --------------------------------------------------------

def art_stems(doc: Doc, theme: Theme, box: Box) -> None:
    """DIAVLOWAV: one mix in, six sources out."""
    x, y, w, h = box
    cy = y + h / 2
    sources = ["VOCALS", "DRUMS", "BASS", "OTHER", "GUITAR", "PIANO"]
    shape = [0.30, 0.55, 0.85, 0.45, 1.0, 0.70, 0.38, 0.92, 0.60, 0.25, 0.78, 0.50, 0.95, 0.42, 0.66, 0.30]
    reach = min(h * 0.44, 56)
    mix = "".join(f"M{n(x + 2 + i * 5)} {n(cy - reach * level)}v{n(2 * reach * level)}"
                  for i, level in enumerate(shape))
    node = x + 100
    doc.add(
        tag("path", d=mix, stroke=theme.ink, stroke_width="2.4", opacity="0.85"),
        tag("polygon", points=polygon(plate(node - 7, cy - 7, 14, 14, 4)), fill=theme.red),
        tag("path", d=f"M{n(x + 84)} {n(cy)}H{n(node - 7)}", stroke=theme.line2),
    )
    label_width = 52
    end = x + w - label_width - 8
    step = (h - 14) / (len(sources) - 1)
    for index, name in enumerate(sources):
        lane = y + 7 + index * step
        rise = lane - cy
        bend = node + 14
        route = f"M{n(node + 7)} {n(cy)}H{n(bend)}L{n(bend + abs(rise))} {n(lane)}H{n(end)}"
        doc.add(
            tag("path", d=route, fill="none", stroke=theme.line2),
            tag("path", d=route, fill="none", stroke=theme.red, stroke_width="1.6", class_=f"f{index % 3 + 1}"),
            mono(end + 8, lane + 3, name, 8.5, theme.dim),
        )
    doc.style(FLOW_CSS)


def art_loop(doc: Doc, theme: Theme, box: Box) -> None:
    """DIAVLO MIND: the seven step loop and its four effort modes."""
    x, y, w, h = box
    steps = ["FRAME", "SCOPE", "GROUND", "PLAN", "BUILD", "PROVE", "DELIVER"]
    pitch = w / len(steps)
    roomy = h > 120
    rail = y + h * (0.3 if roomy else 0.24)
    doc.add(tag("path", d=f"M{n(x + pitch / 2)} {n(rail)}H{n(x + w - pitch / 2)}", stroke=theme.line2))
    for index, name in enumerate(steps):
        cx = x + pitch * (index + 0.5)
        doc.add(
            tag("polygon", points=polygon(plate(cx - 6, rail - 6, 12, 12, 3.5)), fill=theme.bg1, stroke=theme.dim),
            tag("polygon", points=polygon(plate(cx - 3.5, rail - 3.5, 7, 7, 2)), fill=theme.red, class_=f"s{index}"),
            mono(cx, rail + 22, name, 8, theme.dim, "middle", spacing=0.1),
        )
    doc.style("@keyframes step{0%,100%{opacity:.12}6%{opacity:1}20%{opacity:.12}}"
              + "".join(f".s{i}{{opacity:.12;animation:step 7s linear {i}s infinite}}" for i in range(len(steps))))
    base = y + (h * 0.7 if roomy else h - 19)
    doc.add(mono(x, base + 12.2, "EFFORT", 8.5, theme.mute))
    _chips(doc, theme, ["FAST", "STANDARD", "DEEP", "AUTONOMOUS"], x + 50, base, x + w)


def art_transport(doc: Doc, theme: Theme, box: Box) -> None:
    """DIAVLO PLAYER: open, drop, listen."""
    x, y, w, h = box
    radius = min(h / 2 - 2, 52)
    cx, cy = x + radius + 2, y + h / 2
    doc.add(
        tag("polygon", points=polygon(plate(cx - radius, cy - radius, 2 * radius, 2 * radius, radius * 0.58)),
            fill="none", stroke=theme.ink, stroke_width="2"),
        tag("polygon", points=polygon([(cx - radius * 0.24, cy - radius * 0.38), (cx + radius * 0.42, cy),
                                       (cx - radius * 0.24, cy + radius * 0.38)]), fill=theme.red),
    )
    left = cx + radius + 22
    track = cy - 22
    length = x + w - left
    doc.add(
        mono(left, track - 12, "OPEN. DROP. LISTEN.", 9, theme.dim),
        tag("path", d=f"M{n(left)} {n(track)}H{n(x + w)}", stroke=theme.line2, stroke_width="2"),
        tag("rect", x=n(left), y=n(track - 5), width="3", height="10", fill=theme.red, class_="head"),
    )
    doc.style(f"@keyframes head{{to{{transform:translateX({n(length - 3)}px)}}}}"
              ".head{animation:head 14s linear infinite}")
    _chips(doc, theme, ["WAV", "FLAC", "MP3", "AAC", "OGG", "OPUS", "AIFF", "M4A"], left, track + 18, x + w,
           cycle=True, per_row=4)


def art_fanout(doc: Doc, theme: Theme, box: Box) -> None:
    """DIAVLO DROP: one beat, a frame for every platform."""
    x, y, w, h = box
    stage = h - 62  # height left for the frames, above their captions and the chip row
    cy = y + stage / 2
    shape = [0.4, 0.8, 0.55, 1.0, 0.65, 0.35, 0.9, 0.5]
    beat = "".join(f"M{n(x + 4 + i * 5)} {n(cy - 16 * level)}v{n(32 * level)}" for i, level in enumerate(shape))
    doc.add(
        tag("path", d=beat, stroke=theme.ink, stroke_width="2.4", opacity="0.85"),
        tag("path", d=f"M{n(x + 52)} {n(cy)}H{n(x + 84)}l-5 -5m5 5l-5 5", fill="none", stroke=theme.line2),
        tag("path", d=f"M{n(x + 52)} {n(cy)}H{n(x + 84)}", stroke=theme.red, stroke_width="1.6", class_="f1"),
    )
    unit = min(stage / 16, (w - 140) / 36)  # one unit of the 16:9 grid
    frames = [("16:9", 16 * unit, 9 * unit), ("1:1", 11 * unit, 11 * unit), ("9:16", 9 * unit, 16 * unit)]
    cursor = x + 104
    for index, (ratio, fw, fh) in enumerate(frames):
        top = cy - fh / 2
        bars = "".join(f"M{n(cursor + fw / 2 + (k - 2) * 4)} {n(top + fh * 0.72)}v{n(-fh * level)}"
                       for k, level in enumerate([0.22, 0.4, 0.3, 0.46, 0.26]))
        doc.add(
            tag("rect", x=n(cursor), y=n(top), width=n(fw), height=n(fh), fill=theme.bg2, stroke=theme.dim),
            tag("path", d=bars, stroke=theme.red, stroke_width="2", class_=f"v{index}"),
            mono(cursor + fw / 2, cy + 8 * unit + 14, ratio, 8.5, theme.mute, "middle", spacing=0.08),
        )
        cursor += fw + 18
    doc.style(FLOW_CSS, "@keyframes view{0%,100%{opacity:.25}12%{opacity:1}36%{opacity:.25}}"
              + "".join(f".v{i}{{opacity:.25;animation:view 4.5s linear {i * 1.5}s infinite}}" for i in range(3)))
    _chips(doc, theme, ["WAV", "MP3", "TAGGED", "COVER", "METADATA", "ZIP"], x, y + h - 19, x + w)


def art_crate(doc: Doc, theme: Theme, box: Box) -> None:
    """A project that has not been catalogued yet."""
    x, y, w, h = box
    side = min(h - 8, 110)
    left, top = x + (w - side) / 2, y + (h - side) / 2
    doc.add(
        tag("polygon", points=polygon(plate(left, top, side, side, side * 0.16)), fill="none", stroke=theme.dim),
        tag("polygon", points=polygon(plate(left + side * 0.2, top + side * 0.2, side * 0.6, side * 0.6, side * 0.1)),
            fill="none", stroke=theme.line2),
        tag("path", d=f"M{n(left + 4)} {n(top + 6)}H{n(left + side - 4)}", stroke=theme.red, stroke_width="1.6",
            class_="probe"),
    )
    doc.style(f"@keyframes probe{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY({n(side - 12)}px)}}}}"
              ".probe{animation:probe 6s ease-in-out infinite}")


ARTS = {"stems": art_stems, "loop": art_loop, "transport": art_transport, "fanout": art_fanout, "crate": art_crate}


# -- the plate ---------------------------------------------------------------

def _wrap(string: str, limit: int) -> list[str]:
    """Greedy word wrap by character count."""
    rows, current = [], ""
    for word in string.split():
        if current and len(current) + 1 + len(word) > limit:
            rows.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    return rows + [current] if current else rows


def render(line: dict, theme: Theme, layout: str) -> str:
    wide = layout == "wide"
    width, height = (880, 250) if wide else (400, 352)
    pad = 36 if wide else 22
    doc = Doc(width, height, f"Line {line['index']:02d}: {line['name']}", line["alt"])
    doc.style(base_css(), LAMP_CSS)
    mount(doc, theme, cut=16 if wide else 14)

    # header
    head = 38 if wide else 34
    code = f"LINE {line['index']:02d}"
    lamp = {"SHIPPING": theme.red, "SOURCE OPEN": theme.violet}.get(line["status"], theme.mute)
    doc.add(
        mono(pad, head, code, 10.5, theme.red),
        mono(pad + mono_width(code) + 16, head, line["field"], 10.5, theme.mute),
        status_dot(width - pad - 3, head - 3.5, lamp, live=line["status"] == "SHIPPING"),
        mono(width - pad - 14, head, line["status"], 10.5, theme.dim, "end"),
    )

    # name and claim
    column = (width - 2 * pad) * (0.5 if wide else 1.0)
    cap = 32.0 if wide else 26.0
    cap = min(cap, cap * column / TITLE.measure(line["name"], cap))
    name_top = head + (22 if wide else 20)
    doc.add(TITLE.draw(doc, line["name"], pad, name_top, cap, stroke=theme.ink))
    claim_top = name_top + cap + (26 if wide else 22)
    rows = _wrap(line["claim"].upper(), int(column / (10 * 0.76)))
    for index, row in enumerate(rows[:2]):
        doc.add(mono(pad, claim_top + index * 15, row, 10, theme.dim))

    # readouts
    if wide:
        cursor, base = pad, height - 62
        for label, value in line["readouts"]:
            span = max(FIGURE.measure(value, 14), mono_width(label, 8.5))
            doc.add(mono(cursor, base, label, 8.5, theme.mute), FIGURE.draw(doc, value, cursor, base + 10, 14,
                                                                          stroke=theme.ink))
            cursor += span + 30
        box = (pad + column + 24, 62, column - 24, height - 62 - 36)
    else:
        base = height - 84
        for index, (label, value) in enumerate(line["readouts"]):
            cx = pad + (index % 2) * (width - 2 * pad) / 2
            cy = base + (index // 2) * 40
            doc.add(mono(cx, cy, label, 8.5, theme.mute), FIGURE.draw(doc, value, cx, cy + 9, 13, stroke=theme.ink))
        art_top = claim_top + (len(rows[:2]) - 1) * 15 + 20
        box = (pad, art_top, width - 2 * pad, base - 22 - art_top)

    ARTS.get(line["art"], art_crate)(doc, theme, box)
    rim(doc, theme, cut=16 if wide else 14)
    return doc.render()
