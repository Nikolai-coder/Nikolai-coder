"""GATE 00: the entrance to the Factory.

The wordmark is read as a signal chain. DI is the direct input, AV is where
audio and visuals are worked, LO is the line out. One pulse travels the whole
chain on a nine second loop: in along the line, across the letters as a scan,
out the other side. The skyline underneath is generated from the build seed,
so it only changes when something on the public record changes.
"""

from __future__ import annotations

import math
import random

from ..parts import LAMP_CSS, WORDMARK, base_css, mono, mount, rim, status_dot
from ..svg import Doc, n, tag
from ..theme import Theme

LOOP = 9  # seconds for one pass of the pulse through the chain

CHAIN = (  # glyph range in "DIAVLO", caption
    (0, 2, "DIRECT IN"),
    (2, 4, "AUDIO / VISUAL"),
    (4, 6, "LINE OUT"),
)


def skyline(seed: str, count: int, tallest: float) -> list[float]:
    """Bar heights for the skyline: a slow envelope with grain, fixed by the seed."""
    rng = random.Random(int(seed, 16))
    waves = [(rng.uniform(0.6, 2.6), rng.uniform(0, math.tau), rng.uniform(0.5, 1.0)) for _ in range(3)]
    total = sum(amplitude for _, _, amplitude in waves)
    heights = []
    for i in range(count):
        t = i / (count - 1)
        envelope = 0.5 + sum(a * math.sin(f * math.tau * t + p) for f, p, a in waves) / (2 * total)
        envelope = 0.16 + 0.84 * envelope ** 1.6
        heights.append(max(2.5, tallest * envelope * rng.uniform(0.42, 1.0)))
    return heights


def render(data: dict, theme: Theme, layout: str) -> str:
    wide = layout == "wide"
    width, height = (880, 420) if wide else (400, 370)
    pad = 36 if wide else 22
    cap = 112 if wide else 58
    top = 108 if wide else 86  # cap line of the wordmark
    small = 10.5 if wide else 9.5

    doc = Doc(width, height, "DIAVLO Factory, gate 00",
              "The DIAVLO wordmark drawn as a signal chain: DI direct in, AV audio and visual, LO line out.")
    clip = mount(doc, theme, cut=18 if wide else 14)

    word = WORDMARK.set("DIAVLO", width / 2, top, cap, "middle")
    band = word.band(doc)
    mid = top + cap / 2
    beam = cap * 1.4  # width of the scanning light
    travel = word.width + beam + 40

    # -- light ------------------------------------------------------------
    if theme.glow:
        doc.define(
            tag("radialGradient", tag("stop", offset="0", stop_color=theme.red, stop_opacity="0.30")
                + tag("stop", offset="1", stop_color=theme.red, stop_opacity="0"), id="ga"),
            tag("radialGradient", tag("stop", offset="0", stop_color=theme.violet, stop_opacity="0.26")
                + tag("stop", offset="1", stop_color=theme.violet, stop_opacity="0"), id="gb"),
        )
        doc.add(tag("g", tag("ellipse", cx=n(width * 0.44), cy=n(height * 0.74), rx=n(width * 0.5),
                             ry=n(height * 0.5), fill="url(#ga)")
                    + tag("ellipse", cx=n(width * 0.76), cy=n(height * 0.9), rx=n(width * 0.42),
                          ry=n(height * 0.44), fill="url(#gb)"), clip_path=f"url(#{clip})"))

    # -- skyline ----------------------------------------------------------
    floor = height - (52 if wide else 84)
    pitch = 6 if wide else 5
    count = int((width - 2 * pad) // pitch) + 1
    bars = "".join(f"M{n(pad + i * pitch)} {n(floor)}v{n(-h)}"
                   for i, h in enumerate(skyline(data["seed"], count, 62 if wide else 54)))
    window = 240 if wide else 150
    doc.define(
        tag("path", d=bars, id="sk", fill="none", stroke_width="2.6"),
        tag("linearGradient", tag("stop", offset="0", stop_color="#fff", stop_opacity="0")
            + tag("stop", offset="0.5", stop_color="#fff") + tag("stop", offset="1", stop_color="#fff",
                                                                 stop_opacity="0"), id="fade"),
        tag("mask", tag("rect", x=n(-window), y=n(floor - 70), width=n(window), height="72", fill="url(#fade)"),
            id="win", maskUnits="userSpaceOnUse", x=n(-window), y=n(floor - 70), width=n(window), height="72"),
    )
    doc.add(
        tag("use", href="#sk", stroke=theme.ink, opacity="0.17" if theme.night else "0.22"),
        tag("g", tag("g", tag("use", href="#sk", stroke=theme.red), class_="back"), class_="go", mask="url(#win)"),
        tag("path", d=f"M{n(pad)} {n(floor + 0.5)}H{n(width - pad)}", stroke=theme.line2),
    )

    # -- the line in and the line out --------------------------------------
    if wide:
        runs = ((pad, word.x - 20, "pin"), (word.x + word.width + 20, width - pad, "pout"))
        for start, stop, name in runs:
            lane = doc.uid("l")
            doc.define(tag("clipPath", tag("rect", x=n(start), y=n(mid - 3), width=n(stop - start), height="6"),
                           id=lane))
            doc.add(
                tag("path", d=f"M{n(start)} {n(mid)}H{n(stop)}", stroke=theme.line2),
                tag("g", tag("rect", x=n(start - 60), y=n(mid - 1), width="60", height="2", fill=theme.red,
                             class_=name), clip_path=f"url(#{lane})"),
            )
        arrow = "l-5 -5m5 5l-5 5"
        doc.add(
            tag("path", d=f"M{n(pad)} {n(mid - 5)}v10M{n(width - pad)} {n(mid - 5)}v10"
                f"M{n(runs[0][1])} {n(mid)}{arrow}M{n(runs[1][1] - 12)} {n(mid)}{arrow}",
                stroke=theme.dim, fill="none"),
            mono(pad, mid - 14, "IN", small, theme.mute),
            mono(width - pad, mid - 14, "OUT", small, theme.mute, "end"),
        )
        lengths = (runs[0][1] - runs[0][0] + 60, runs[1][1] - runs[1][0] + 60)
    else:
        lengths = (0, 0)

    # -- wordmark ---------------------------------------------------------
    doc.define(
        tag("g", word.shape(0, 2) + word.shape(4, 6), id="wa", clip_path=f"url(#{band})"),
        tag("g", word.shape(2, 4), id="wb", clip_path=f"url(#{band})"),
        tag("mask", tag("use", href="#wa", stroke="#fff") + tag("use", href="#wb", stroke="#fff"), id="wm",
            maskUnits="userSpaceOnUse", x=n(word.x - 4), y=n(top - 12), width=n(word.width + 8), height=n(cap + 24)),
        tag("linearGradient", tag("stop", offset="0", stop_color=theme.red, stop_opacity="0")
            + tag("stop", offset="0.32", stop_color=theme.red) + tag("stop", offset="0.5", stop_color=theme.sheen)
            + tag("stop", offset="0.68", stop_color=theme.red)
            + tag("stop", offset="1", stop_color=theme.red, stop_opacity="0"), id="sheen"),
    )
    doc.add(
        tag("use", href="#wa", stroke=theme.ink),
        tag("use", href="#wb", stroke=theme.red),
        tag("g", tag("rect", x=n(word.x - beam - 20), y=n(top - 12), width=n(beam), height=n(cap + 24),
                     fill="url(#sheen)", class_="scan"), mask="url(#wm)"),
    )

    # -- the chain, annotated ----------------------------------------------
    rule = top + cap + (20 if wide else 14)
    for start, stop, caption in CHAIN:
        left, right = word.span(start, stop)
        signal = start == 2
        doc.add(
            tag("path", d=f"M{n(left)} {n(rule)}v6H{n(right)}v-6", fill="none",
                stroke=theme.red if signal else theme.line2),
            mono((left + right) / 2, rule + (24 if wide else 21), caption, small,
                 theme.dim if signal else theme.mute, "middle"),
        )

    # -- lettering --------------------------------------------------------
    head = 40 if wide else 34
    doc.add(
        mono(pad, head, "DIAVLO FACTORY", small, theme.ink),
        mono(pad + (128 if wide else 0), head + (0 if wide else 15), "GATE 00", small, theme.mute),
        status_dot(width - pad - 3, head - 3.5, theme.red),
        mono(width - pad - 14, head, theme.shift, small, theme.dim, "end"),
    )
    operator = f"OPERATOR {data['login'].upper()}"
    build = f"BUILD {data['captured'].replace('-', '.')}"
    seed = f"SEED {data['seed'].upper()}"
    output = " · ".join(data["output"])
    foot = height - 22
    if wide:
        doc.add(
            mono(pad, foot, operator, small, theme.mute),
            mono(width / 2, foot, output, small, theme.dim, "middle"),
            mono(width - pad, foot, f"{build} · {seed}", small, theme.mute, "end"),
        )
    else:
        doc.add(
            mono(width / 2, foot - 34, output, small, theme.dim, "middle"),
            mono(pad, foot - 15, operator, small, theme.mute),
            mono(width - pad, foot - 15, build, small, theme.mute, "end"),
            mono(pad, foot, data["site"], small, theme.mute),
            mono(width - pad, foot, seed, small, theme.mute, "end"),
        )
    rim(doc, theme, cut=18 if wide else 14)

    # -- motion -----------------------------------------------------------
    sweep = width + window
    css = [
        base_css(), LAMP_CSS,
        f"@keyframes scan{{0%,17%{{transform:translateX(0)}}46%,100%{{transform:translateX({n(travel)}px)}}}}",
        f".scan{{animation:scan {LOOP}s cubic-bezier(.45,0,.2,1) infinite}}",
        f"@keyframes go{{to{{transform:translateX({n(sweep)}px)}}}}",
        f"@keyframes back{{to{{transform:translateX({n(-sweep)}px)}}}}",
        f".go{{animation:go {LOOP}s linear infinite}}.back{{animation:back {LOOP}s linear infinite}}",
    ]
    if wide:
        css += [
            f"@keyframes pin{{0%{{transform:translateX(0)}}17%,100%{{transform:translateX({n(lengths[0])}px)}}}}",
            f"@keyframes pout{{0%,46%{{transform:translateX(0)}}63%,100%{{transform:translateX({n(lengths[1])}px)}}}}",
            f".pin{{animation:pin {LOOP}s linear infinite}}.pout{{animation:pout {LOOP}s linear infinite}}",
        ]
    doc.style(*css)
    return doc.render()
