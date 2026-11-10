"""Build the profile.

    python3 -m factory             read the public record and rebuild what changed
    python3 -m factory --offline   rebuild from the saved snapshot, no network
    python3 -m factory --dry-run   read the public record, verify, write nothing
    python3 -m factory --check     verify that the committed files match the snapshot

The build never leaves the profile half-written: every plate is rendered and
inspected in memory first, and files are only touched when all of them pass.
If the public record cannot be read, the last good snapshot is used instead.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

from . import collect, readme
from .model import view
from .modules import control, exit as exit_plate, gate, line, routing, vault
from .theme import THEMES

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "factory" / "registry.json"
SNAPSHOT = ROOT / "factory" / "data" / "snapshot.json"
README = ROOT / "README.md"
ASSETS = ROOT / readme.ASSETS
BUDGET = 16_000  # bytes allowed for a single plate

FORBIDDEN = {"script", "foreignObject", "image", "iframe", "a", "audio", "video"}


def render(model: dict) -> dict[str, str]:
    """Every plate in every variant, keyed by file name."""
    plates: dict[str, str] = {}
    for theme in THEMES:
        for layout in ("wide", "tall"):
            suffix = f"{theme.name}.{layout}.svg"
            plates[f"gate.{suffix}"] = gate.render(model, theme, layout)
            for entry in model["lines"]:
                plates[f"line.{entry['repo'].lower()}.{suffix}"] = line.render(entry, theme, layout)
            plates[f"control.{suffix}"] = control.render(model, theme, layout)
            plates[f"routing.{suffix}"] = routing.render(model, theme, layout)
            plates[f"vault.{suffix}"] = vault.render(model, theme, layout)
            plates[f"exit.{suffix}"] = exit_plate.render(model, theme, layout)
    return plates


def inspect(plates: dict[str, str], page: str) -> list[str]:
    """Return every reason the build must not be published. Empty means safe."""
    problems = []
    for name, markup in plates.items():
        size = len(markup.encode("utf-8"))
        if size > BUDGET:
            problems.append(f"{name}: {size} bytes is over the {BUDGET} byte budget")
        try:
            root = ET.fromstring(markup)
        except ET.ParseError as error:
            problems.append(f"{name}: not well-formed XML ({error})")
            continue
        if not root.tag.endswith("}svg") or "viewBox" not in root.attrib:
            problems.append(f"{name}: root element must be <svg> with a viewBox")
        for element in root.iter():
            tag = element.tag.split("}")[-1]
            if tag in FORBIDDEN:
                problems.append(f"{name}: <{tag}> does not survive GitHub's image sandbox")
            for key, value in element.attrib.items():
                key = key.split("}")[-1]
                if key.startswith("on") or (key == "href" and not value.startswith("#")):
                    problems.append(f"{name}: attribute {key}={value!r} reaches outside the file")
        if re.search(r"url\((?!#)|@import|https?://(?!www\.w3\.org/)", markup):
            problems.append(f"{name}: refers to an external resource")
    for reference in readme.references(page):
        local = reference.split("#")[0]
        if local.startswith(f"{readme.ASSETS}/"):
            if local[len(readme.ASSETS) + 1:] not in plates:
                problems.append(f"README.md: {reference} is not a plate this build produces")
        elif not (ROOT / local).exists():
            problems.append(f"README.md: {reference} does not exist in the repository")
    return problems


def load(path: pathlib.Path) -> dict | None:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m factory", description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true", help="rebuild from the saved snapshot, no network")
    mode.add_argument("--dry-run", action="store_true", help="read the public record, verify, write nothing")
    mode.add_argument("--check", action="store_true", help="verify that the committed files match the snapshot")
    parser.add_argument("--today", help="override today's date (YYYY-MM-DD), for tests")
    args = parser.parse_args(argv)

    registry = load(REGISTRY)
    previous = load(SNAPSHOT)
    today = dt.date.fromisoformat(args.today) if args.today else dt.datetime.now(dt.timezone.utc).date()

    snapshot = previous
    if not (args.offline or args.check):
        try:
            snapshot = collect.snapshot(registry, previous, today)
        except collect.Unavailable as error:
            print(f"::warning::Public record unavailable ({error}); keeping the snapshot of "
                  f"{previous['captured'] if previous else 'nothing'}.")
    if snapshot is None:
        print("::error::No snapshot exists yet and the public record could not be read.")
        return 1

    model = view(snapshot, registry)
    plates = render(model)
    page = readme.weave(README.read_text(encoding="utf-8"), readme.blocks(model))
    problems = inspect(plates, page)
    for problem in problems:
        print(f"::error::{problem}")
    if problems:
        return 1

    outputs = {ASSETS / name: markup for name, markup in plates.items()}
    outputs[README] = page
    outputs[SNAPSHOT] = json.dumps(snapshot, indent=1, ensure_ascii=False) + "\n"
    changed = [path for path, content in outputs.items()
               if not path.exists() or path.read_text(encoding="utf-8") != content]
    stale = [path for path in ASSETS.glob("*.svg") if path not in outputs] if ASSETS.exists() else []

    total = sum(len(markup.encode("utf-8")) for markup in plates.values())
    print(f"{len(plates)} plates, {total / 1024:.0f} KB in all, largest {max(map(len, plates.values()))} bytes. "
          f"Activity source: {snapshot['activity']['source']}. Seed {snapshot['seed']}, "
          f"record of {snapshot['captured']}.")
    for path in changed + stale:
        print(f"  {'stale  ' if path in stale else 'changed'} {path.relative_to(ROOT)}")

    if args.check:
        if changed or stale:
            print("::error::Committed files do not match the generator. Run: python3 -m factory --offline")
            return 1
        print("Committed files match the generator.")
        return 0
    if args.dry_run:
        print("Dry run: nothing was written.")
        return 0
    for path in changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(outputs[path], encoding="utf-8")
    for path in stale:
        path.unlink()
    return 0


if __name__ == "__main__":
    sys.exit(main())
