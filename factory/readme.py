"""Weave the generated blocks into README.md.

Only the text between ``<!-- factory:name -->`` and ``<!-- /factory:name -->``
is rewritten. Everything else in the README is the operator's to edit.

Each plate is served through one ``<picture>`` element with four sources:
night or day by the visitor's colour scheme, wide or tall by the width of
their screen. The fallback ``<img>`` is the wide night plate.
"""

from __future__ import annotations

import html
import re

ASSETS = "assets"
NARROW = "(max-width: 600px)"


def picture(name: str, alt: str, href: str | None = None) -> str:
    """Markup for one plate. ``name`` is the file stem shared by its four variants.

    The block opens with ``<p>`` on a line of its own. That makes the whole
    thing one raw HTML block for GitHub's Markdown parser; without it, a
    leading ``<a>`` is read as inline text and the ``<source>`` lines are torn
    out of their ``<picture>``.
    """
    stem = f"{ASSETS}/{name}"
    rows = [
        "<picture>",
        f'<source media="(prefers-color-scheme: dark) and {NARROW}" srcset="{stem}.night.tall.svg">',
        f'<source media="(prefers-color-scheme: light) and {NARROW}" srcset="{stem}.day.tall.svg">',
        f'<source media="(prefers-color-scheme: light)" srcset="{stem}.day.wide.svg">',
        f'<img src="{stem}.night.wide.svg" width="100%" alt="{html.escape(alt, quote=True)}">',
        "</picture>",
    ]
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
        picture(f"line.{line['repo'].lower()}", line["alt"], line["url"]),
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
        "gate": picture("gate", "DIAVLO Factory. The wordmark read as a signal chain: DI, direct in. "
                                "AV, audio and visual. LO, line out."),
        "lines": "\n\n".join(_line(line) for line in view["lines"]),
        "control": picture("control", f"Telemetry, read on {view['captured']}: {totals['releases']} releases shipped, "
                                      f"{totals['downloads']} installer downloads, {totals['stars']} stars, "
                                      f"{totals['lines']} public lines, {activity['total']} {kind} in "
                                      f"{len(activity['weeks'])} weeks.") + "\n\n" + _legend(view),
        "routing": picture("routing", "Routing matrix, as stated by each repository. " + " ".join(
            f"{component['name']}: {', '.join(view['lines'][i - 1]['name'] for i in component['lines'])}."
            for component in view["components"] if component["lines"])),
        "vault": picture("vault", "Sealed bays, declared but not public: " + ", ".join(view["sealed"]) + "."),
        "exit": picture("exit", "Manufactured, not templated. Every plate on this page is drawn by code in this "
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
