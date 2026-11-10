"""Weave the generated blocks into README.md.

Only the text between ``<!-- factory:name -->`` and ``<!-- /factory:name -->``
is rewritten. Everything else in the README is the operator's to edit.

How a plate reaches the visitor
    Every plate exists as four files: night or day, wide or tall. GitHub's
    sanitizer keeps ``<picture>``, and on ``<source>`` it keeps ``media`` and
    the first URL of ``srcset``. It removes ``sizes``, width descriptors and
    ``srcset`` on ``<img>`` (probed on 2026-11-10), so the choice has to be
    made with media queries alone.

    On profile pages GitHub also wraps each picture in a ``<themed-picture>``
    element. When the visitor uses a fixed GitHub theme, that element rewrites
    every source whose query mentions a colour scheme: sources of the chosen
    theme are forced on, the others off. A query such as
    ``(prefers-color-scheme: dark) and (max-width: 600px)`` then loses its
    width condition, and desktops are served the phone layout.

    So the two conditions are never combined in one query. Each plate is two
    pictures, one per shift. The first source of a picture names the opposite
    colour scheme and shows the conveyor rail; when it does not match, a
    plain width query picks the tall or the wide plate. In every state one
    picture shows the plate and the other shows a rail: the rail simply
    changes side between shifts. ``audit`` proves this before a build is
    written.
"""

from __future__ import annotations

import html
import itertools
import re

ASSETS = "assets"
NARROW = "(max-width: 600px)"
DARK = "(prefers-color-scheme: dark)"
LIGHT = "(prefers-color-scheme: light)"
SHIFT = {"dark": "night", "light": "day"}


# -- markup -----------------------------------------------------------------

def _slot(stem: str, shift: str, alt: str) -> list[str]:
    """One picture: the rail when the visitor is on the other shift, else the plate."""
    other_query, other_shift = (LIGHT, "day") if shift == "night" else (DARK, "night")
    return [
        "<picture>",
        f'<source media="{other_query}" srcset="{ASSETS}/rail.{other_shift}.svg">',
        f'<source media="{NARROW}" srcset="{stem}.{shift}.tall.svg">',
        f'<img src="{stem}.{shift}.wide.svg" width="100%" alt="{html.escape(alt, quote=True)}">',
        "</picture>",
    ]


def plate(name: str, alt: str, href: str | None = None, rail: str = "above") -> str:
    """Markup for one plate. ``name`` is the file stem shared by its four variants.

    ``rail`` says where the conveyor rail sits on the night shift, ``above``
    or ``below`` the plate; on the day shift it is on the other side. The
    description is carried by the night picture and the day picture is marked
    decorative, so a screen reader announces each plate exactly once.

    The block opens with ``<p>`` on a line of its own. That makes it one raw
    HTML block for GitHub's Markdown parser; without it, a leading ``<a>`` is
    read as inline text and the ``<source>`` lines are torn out of their
    ``<picture>``.
    """
    stem = f"{ASSETS}/{name}"
    night, day = _slot(stem, "night", alt), _slot(stem, "day", "")
    rows = day + night if rail == "above" else night + day
    if href:
        rows = [f'<a href="{html.escape(href, quote=True)}">', *rows, "</a>"]
    return "\n".join(["<p>", *rows, "</p>"])


def _line(line: dict) -> str:
    """One line: its plate, a paragraph of copy, then the stack and the links."""
    text = f"**{line['name']}** · {line['summary']}"
    if line.get("edge"):
        text += f" {line['edge']}"
    chips = " ".join(f"`{item}`" for item in line.get("stack", []))
    links = " · ".join(f"[{label}]({url})" for label, url in line["links"])
    return "\n\n".join([
        plate(f"line.{line['repo'].lower()}", line["alt"], line["url"]),
        text + "<br>\n<sub>" + " &nbsp;·&nbsp; ".join(part for part in (chips, links) if part) + "</sub>",
    ])


def _legend(view: dict) -> str:
    """One line under the telemetry plate that says exactly what each figure counts."""
    if view["activity"]["source"] == "calendar":
        signal = "The signal is GitHub's contribution calendar, summed per week."
    else:
        signal = f"The signal counts commits by @{view['login']} in public repositories, per week."
    return ('<p align="center"><sub>Read from the GitHub API on ' + view["captured"] + ". A release's download "
            "figure is the counter of its largest file, the installer. " + signal + "</sub></p>")


def blocks(view: dict) -> dict[str, str]:
    """All generated README blocks, keyed by marker name."""
    totals = view["totals"]
    activity = view["activity"]
    kind = "contributions" if activity["source"] == "calendar" else "public commits"
    return {
        "gate": plate("gate", "DIAVLO Factory. The wordmark read as a signal chain: DI, direct in. "
                              "AV, audio and visual. LO, line out.", rail="below"),
        "lines": "\n\n".join(_line(line) for line in view["lines"]),
        "control": plate("control", f"Telemetry, read on {view['captured']}: {totals['releases']} releases shipped, "
                                    f"{totals['downloads']} installer downloads, {totals['stars']} stars, "
                                    f"{totals['lines']} public lines, {activity['total']} {kind} in "
                                    f"{len(activity['weeks'])} weeks.") + "\n\n" + _legend(view),
        "routing": plate("routing", "Routing matrix, as stated by each repository. " + " ".join(
            f"{component['name']}: {', '.join(view['lines'][i - 1]['name'] for i in component['lines'])}."
            for component in view["components"] if component["lines"])),
        "vault": plate("vault", "Sealed bays, declared but not public: " + ", ".join(view["sealed"]) + "."),
        "exit": plate("exit", "Manufactured, not templated. Every plate on this page is drawn by code in this "
                              f"repository. Build {view['captured']}, seed {view['seed']}.", "factory/README.md"),
    }


def weave(text: str, generated: dict[str, str]) -> str:
    """Replace the content of every marked block; fail loudly on a missing marker."""
    for name, content in generated.items():
        pattern = re.compile(rf"(<!-- factory:{name} -->)\n(?:.*?\n)??(<!-- /factory:{name} -->)", re.S)
        text, count = pattern.subn(lambda match: f"{match.group(1)}\n{content}\n{match.group(2)}", text)
        if count != 1:
            raise ValueError(f"README.md must contain exactly one 'factory:{name}' block, found {count}")
    return text


def references(text: str) -> list[str]:
    """Every repository-relative file the README points at."""
    found = re.findall(r'(?:src|srcset|href)="([^"]+)"', text) + re.findall(r"\]\(([^)\s]+)\)", text)
    return sorted({ref for ref in found if not re.match(r"[a-z]+:|#", ref)})


# -- proof ------------------------------------------------------------------

def _matches(query: str, system: str, narrow: bool) -> bool:
    """Evaluate one of the three media queries this page is allowed to use."""
    if query == NARROW:
        return narrow
    if query in (DARK, LIGHT):
        return (query == DARK) == (system == "dark")
    raise ValueError(f"media query {query!r} is not one the audit can prove safe")


def shown(sources: list[tuple[str, str]], fallback: str, mode: str, element: bool, system: str, narrow: bool) -> str:
    """Which file a ``<picture>`` displays for one visitor.

    ``mode`` is the visitor's GitHub appearance setting (``auto``, ``light``
    or ``dark``), ``element`` says whether the page defines ``<themed-picture>``
    (profile pages do; the newer repository view does not), ``system`` is the
    colour scheme the browser reports and ``narrow`` is the width test.

    This follows the HTML rule (the first source whose query matches wins,
    otherwise the ``<img>``) and GitHub's rewrite, read from its own script on
    2026-11-10: with a fixed theme, any source whose query contains a colour
    scheme is switched fully on or fully off, whatever else the query says.
    """
    forcing = element and mode != "auto" and any("prefers-color-scheme" in query for query, _ in sources)
    for query, file in sources:
        if forcing and "prefers-color-scheme" in query:
            # GitHub tests for "light" first, so a query naming both counts as light.
            theme = "light" if "prefers-color-scheme: light" in query else "dark"
            if theme == mode:
                return file
            continue
        if _matches(query, system, narrow):
            return file
    return fallback


def audit(page: str) -> list[str]:
    """Check every plate of the README in every state a visitor can be in.

    Returns the problems found; an empty list means that each block shows
    exactly one plate, in the right shift and layout, and rails of that same
    shift in its other slots.
    """
    problems = []
    states = list(itertools.product(("auto", "light", "dark"), (True, False), ("light", "dark"), (True, False)))
    for block in re.findall(r"^<p>\n(.*?)\n</p>$", page, re.S | re.M):
        pictures = [(re.findall(r'<source media="([^"]*)" srcset="([^"]*)">', body),
                     re.search(r'<img src="([^"]*)"', body).group(1))
                    for body in re.findall(r"<picture>(.*?)</picture>", block, re.S)]
        if not pictures:
            continue
        label = pictures[0][1].split("/")[-1].split(".night.")[0].split(".day.")[0]
        for mode, element, system, narrow in states:
            shift = SHIFT[mode if element and mode != "auto" else system]
            want = f".{shift}.{'tall' if narrow else 'wide'}.svg"
            try:
                files = [shown(sources, fallback, mode, element, system, narrow) for sources, fallback in pictures]
            except ValueError as error:
                problems.append(f"README.md: {label}: {error}")
                break
            plates = [file for file in files if not file.startswith(f"{ASSETS}/rail.")]
            rails = [file for file in files if file.startswith(f"{ASSETS}/rail.")]
            if len(plates) != 1 or not plates[0].endswith(want) or any(r != f"{ASSETS}/rail.{shift}.svg" for r in rails):
                state = (f"GitHub theme {mode}, {'profile page' if element else 'repository view'}, "
                         f"system {system}, {'phone' if narrow else 'desktop'}")
                problems.append(f"README.md: {label} resolves to {files} for [{state}], expected one *{want}")
                break
    return problems
