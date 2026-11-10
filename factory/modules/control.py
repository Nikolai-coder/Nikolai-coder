"""CONTROL 05: telemetry.

Three instruments, all read from the public record: four counters, the
shipping log (one bar per release, in order of publication, as tall as its
installer download count) and the activity signal for the last 26 weeks.
Nothing on this plate is estimated.
"""

from __future__ import annotations

import datetime as dt

from ..parts import FIGURE, LAMP_CSS, TITLE, base_css, mono, mono_width, mount, rim
from ..svg import Doc, n, tag
from ..theme import Theme

MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()


def _counters(doc: Doc, theme: Theme, data: dict, x: float, y: float, width: float, columns: int) -> None:
    totals = data["totals"]
    cells = [("RELEASES SHIPPED", totals["releases"]), ("INSTALLER DOWNLOADS", totals["downloads"]),
             ("STARS", totals["stars"]), ("PUBLIC LINES", totals["lines"])]
    step = width / columns
    for index, (label, value) in enumerate(cells):
        cx = x + (index % columns) * step
        cy = y + (index // columns) * 62
        doc.add(mono(cx, cy, label, 8.5, theme.mute), FIGURE.draw(doc, str(value), cx, cy + 11, 28, stroke=theme.ink))


def _shipping_log(doc: Doc, theme: Theme, data: dict, x: float, y: float, width: float, height: float) -> None:
    """One bar per release, oldest to newest; month changes are marked on the axis."""
    floor = y + height - 26
    releases = data["shipped"][-int(width // 9):]
    doc.add(mono(x, y, "SHIPPING LOG · DOWNLOADS PER RELEASE", 8.5, theme.mute),
            tag("path", d=f"M{n(x)} {n(floor + 0.5)}H{n(x + width)}", stroke=theme.line2))
    if not releases:
        doc.add(mono(x, floor - 20, "NO PUBLIC RELEASE ON RECORD", 9, theme.dim))
        return
    doc.add(mono(x + width, y, f"LATEST {releases[-1][1].upper()}", 8.5, theme.red, "end"))
    pitch = width / len(releases)
    bar = min(10.0, pitch * 0.56)
    room = height - 56
    peak = max(item[2] for item in releases) or 1
    plain, marked, labels = [], [], []
    month, rows = None, [-1e9, -1e9]  # right edge of the last month caption on each of two rows
    for index, (date, tag_name, downloads, _line) in enumerate(releases):
        cx = x + pitch * (index + 0.5)
        tall = 3 + (room - 3) * downloads / peak
        latest = index == len(releases) - 1
        milestone = tag_name.lstrip("vV") == "1.0.0"
        (marked if latest or milestone else plain).append(f"M{n(cx)} {n(floor)}v{n(-tall)}")
        if milestone or index == 0:
            labels.append((cx, floor - tall - 7, tag_name.upper()))
        elif downloads == peak:
            labels.append((cx, floor - tall - 7, str(downloads)))
        if date[:7] != month:
            month = date[:7]
            edge = x + pitch * index
            caption = MONTHS[int(date[5:7]) - 1]
            doc.add(tag("path", d=f"M{n(edge)} {n(floor)}v5", stroke=theme.dim))
            left = min(edge + 3, x + width - mono_width(caption, 8, 0.1))
            for row in (0, 1):  # captions of short months step down a row instead of colliding
                if left > rows[row] + 5:
                    rows[row] = left + mono_width(caption, 8, 0.1)
                    doc.add(mono(left, floor + 14 + row * 10, caption, 8, theme.mute, spacing=0.1))
                    break
    doc.add(
        tag("path", d="".join(plain), stroke=theme.ink, stroke_width=n(bar), opacity="0.8"),
        tag("path", d="".join(marked), stroke=theme.red, stroke_width=n(bar)),
    )
    taken = -1e9
    for cx, top, label in labels:
        span = mono_width(label, 8, 0.08)
        left = min(max(cx - span / 2, x), x + width - span)
        if left < taken + 6:
            continue
        taken = left + span
        doc.add(mono(left, top, label, 8, theme.dim, spacing=0.08))
    # the reading head
    doc.add(tag("path", d=f"M{n(x)} {n(floor - room - 4)}V{n(floor)}", stroke=theme.red, opacity="0.55",
                class_="read"))
    doc.style(f"@keyframes read{{0%{{transform:translateX(0);opacity:0}}6%,94%{{opacity:.55}}"
              f"100%{{transform:translateX({n(width)}px);opacity:0}}}}"
              ".read{opacity:0;animation:read 10s linear infinite}")


def _signal(doc: Doc, theme: Theme, data: dict, x: float, y: float, width: float, height: float) -> None:
    """Weekly activity as a mirrored waveform; quiet weeks stay on the centre line."""
    activity = data["activity"]
    weeks = activity["weeks"]
    kind = "CONTRIBUTIONS" if activity["source"] == "calendar" else "PUBLIC COMMITS"
    doc.add(mono(x, y, f"SIGNAL · {len(weeks)} WEEKS", 8.5, theme.mute))
    centre = y + 8 + (height - 34) / 2
    reach = (height - 44) / 2
    peak = max(count for _, count in weeks) or 1
    pitch = width / len(weeks)
    loud = "".join(f"M{n(x + pitch * (i + 0.5))} {n(centre - reach * count / peak)}v{n(2 * reach * count / peak)}"
                   for i, (_, count) in enumerate(weeks) if count)
    quiet = "".join(f"M{n(x + pitch * (i + 0.5))} {n(centre - 2)}v4" for i, (_, count) in enumerate(weeks) if not count)
    doc.add(
        tag("path", d=f"M{n(x)} {n(centre)}H{n(x + width)}", stroke=theme.line2),
        tag("path", d=quiet, stroke=theme.mute) if quiet else "",
        tag("path", d=loud, stroke=theme.red, stroke_width=n(min(6.0, pitch * 0.6))) if loud else "",
        mono(x, y + height - 4, f"{activity['total']} {kind}", 8, theme.dim, spacing=0.1),
        mono(x + width, y + height - 4, _span(weeks), 8, theme.mute, "end", spacing=0.1),
    )


def _span(weeks: list) -> str:
    first = dt.date.fromisoformat(weeks[0][0])
    last = dt.date.fromisoformat(weeks[-1][0])
    return f"{MONTHS[first.month - 1]} {first.year} > {MONTHS[last.month - 1]} {last.year}"


def render(data: dict, theme: Theme, layout: str) -> str:
    wide = layout == "wide"
    width, height = (880, 350) if wide else (400, 566)
    pad = 36 if wide else 22
    doc = Doc(width, height, "Control 05: telemetry",
              f"{data['totals']['releases']} releases shipped, {data['totals']['downloads']} installer downloads, "
              f"{data['totals']['stars']} stars. Measured on {data['captured']}.")
    doc.style(base_css(), LAMP_CSS)
    mount(doc, theme, cut=16 if wide else 14)

    head = 38 if wide else 34
    doc.add(
        mono(pad, head, "CONTROL 05", 10.5, theme.red),
        mono(width - pad, head, f"READ {data['captured'].replace('-', '.')}", 10.5, theme.dim, "end"),
        TITLE.draw(doc, "TELEMETRY", pad, head + 20, 24, stroke=theme.ink),
        mono(pad, head + 66, "MEASURED, NOT ESTIMATED. A VALUE THAT DOES NOT EXIST PRINTS A DASH.", 9, theme.mute)
        if wide else mono(pad, head + 66, "MEASURED, NOT ESTIMATED.", 9, theme.mute),
    )
    inner = width - 2 * pad
    if wide:
        _counters(doc, theme, data, pad, 136, inner, 4)
        _shipping_log(doc, theme, data, pad, 216, inner * 0.62, 112)
        _signal(doc, theme, data, pad + inner * 0.62 + 40, 216, inner * 0.38 - 40, 112)
    else:
        _counters(doc, theme, data, pad, 132, inner, 2)
        _shipping_log(doc, theme, data, pad, 272, inner, 136)
        _signal(doc, theme, data, pad, 440, inner, 104)
    rim(doc, theme, cut=16 if wide else 14)
    return doc.render()
