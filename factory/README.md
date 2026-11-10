# How this profile is built

The profile of [@Nikolai-coder](https://github.com/Nikolai-coder) is not a template and uses no
third-party widget. Every graphic is an SVG drawn by the Python package in this folder, from two inputs:

| Input | What it holds | Who writes it |
| :-- | :-- | :-- |
| [`registry.json`](registry.json) | What the operator declares: the lines, their copy, the routing matrix, the sealed bays | You |
| [`data/snapshot.json`](data/snapshot.json) | What the public record says: repositories, releases, download counters, stars, commit dates | The build |

`python3 -m factory` reads the GitHub API, updates the snapshot, redraws the plates in [`../assets`](../assets)
and rewrites the marked blocks of [`../README.md`](../README.md). A GitHub Actions workflow runs it once a day.
It needs Python 3.9 or newer and nothing else: no packages, no actions from the marketplace, no fonts.

## The identity

**The signal chain.** DIAVLO is read as `DI · AV · LO`: direct in, audio and visual, line out. The gate animates
one pulse through that chain on a nine second loop. `AV` is the only part of the wordmark drawn in red, and it
stands alone as the seal on the last plate.

**FACTORY CUT.** The display lettering is not a font. [`typeface.py`](typeface.py) holds a stroke skeleton for
every glyph on a 7 unit grid, and the build strokes it at the weight a plate needs. Corners are cut at 45 degrees;
A and V are the two exceptions, drawn as mirrored diagonals. Because it is geometry, the wordmark and all titles
look the same on every device.

**The cut.** Every plate is a rectangle with its four corners cut at 45 degrees and a short red stroke parallel
to the top-left cut. Small technical lettering uses the visitor's own monospace font, pinned with `textLength`
so the layout does not move between Menlo, Consolas and DejaVu.

**Two shifts.** [`theme.py`](theme.py) defines NIGHT and DAY. They are two complete designs that share
geometry, not one design inverted. The gate says which shift you are on.

**Measured, not estimated.** The rule comes from DIAVLOWAV's own README. A figure that does not exist prints a
dash. Names without a public repository are shown as sealed bays, with no description at all.

## What GitHub allows, and what this design does about it

| Limit of a GitHub README | Consequence here |
| :-- | :-- |
| No CSS, no JavaScript, no inline SVG in Markdown | All graphics are separate `.svg` files shown through `<img>` |
| SVG inside `<img>` cannot run scripts or load fonts, images or stylesheets | Plates are self-contained: paths, system fonts, one `<style>` block |
| CSS animation inside such an SVG does run | Motion is CSS only, on `transform`, `opacity` and `stroke-dashoffset` |
| `<picture>` with `media` on `<source>` is kept by the sanitizer | Each plate has four files: night or day by `prefers-color-scheme`, wide or tall by `max-width: 600px` |
| A colour scheme query inside the SVG is unreliable in Safari | Theme is chosen by `<picture>`, never inside the file |
| The visitor's GitHub theme can differ from their system scheme | Every plate is opaque, so it stays legible on either page background |
| Some visitors ask for reduced motion | Every file carries `@media (prefers-reduced-motion: reduce)` and stops all animation |

`python3 -m factory --check` enforces the rest: well-formed XML, no element or attribute that reaches outside
the file, at most 16 KB per plate, and no README reference to a file that does not exist.

## Layout

```
README.md                  the profile; generated blocks sit between "factory:" markers
assets/                    generated plates, four variants each; never edit by hand
factory/
  __main__.py              the build: collect, render, inspect, write
  collect.py               GitHub API client, retries, snapshot
  model.py                 snapshot + registry -> what the plates display
  readme.py                <picture> markup and the README weave
  typeface.py              FACTORY CUT
  theme.py  parts.py  svg.py   tokens, shared parts, SVG helpers
  modules/                 one file per plate: gate, line, control, routing, vault, exit
  registry.json            what you declare
  data/snapshot.json       last good read of the public record
.github/workflows/factory.yml
archive/2026-09-30/        the previous profile, kept whole
```

## What every figure counts

| Figure | Source | Definition |
| :-- | :-- | :-- |
| Release, shipped | `GET /repos/{owner}/{repo}/releases` | Latest published release and its date; drafts are ignored |
| Downloads | same | Sum, over all releases, of the download counter of the largest file in each release |
| Stars, forks | `GET /users/{login}/repos` | As reported; forks of other people's projects are not counted in totals |
| Public lines | registry + record | Lines whose repository is public right now |
| Signal | GraphQL contribution calendar, else `GET /repos/.../commits?author=` | Contributions per week for 26 weeks; without a token, commits by the account in its public repositories |
| Status | derived | `SHIPPING` has a release, `SOURCE OPEN` has code, `IN ASSEMBLY` has neither yet |
| Seed | derived | First six hex digits of a SHA-1 over the repository facts; it shapes the skyline on the gate |

## When something fails

- Every request is retried three times. If the record still cannot be read, the build keeps the last snapshot,
  prints a warning and exits cleanly. The page simply stays as it was.
- If the repository listing fails but single repositories answer, known repositories are refreshed one by one.
- If the contribution calendar is unavailable, the previous calendar is kept; the chart never flips between two
  definitions from one day to the next.
- A line whose repository is no longer public is dropped, and so are its links. A link to a file is only
  written if that file exists on the default branch.
- Nothing is written unless every plate passes inspection.
- The workflow commits as `github-actions[bot]`, only when a file changed. Those commits do not count as your
  contributions. When nothing changes for 30 days the build date is refreshed once, which also keeps GitHub
  from pausing the schedule after 60 quiet days.

## Maintaining it

**Add or edit a line.** Add an entry to `lines` in `registry.json`:

```json
{
  "repo": "repository-name",
  "name": "NAME ON THE PLATE",
  "field": "AUDIO",
  "art": "crate",
  "claim": "ONE LINE, CAPITALS, UNDER 48 CHARACTERS IF YOU CAN",
  "summary": "One or two sentences for the README. State only what the repository shows.",
  "edge": "Optional: the one thing that makes it worth a look.",
  "stack": ["Rust", "FFmpeg"],
  "links": [{"label": "Demo", "path": "media/demo.mp4"}]
}
```

`art` is one of `stems`, `loop`, `transport`, `fanout` or `crate`. A new diagram is a function in
[`modules/line.py`](modules/line.py) registered in `ARTS`. A public repository with code or releases that is
not in the registry gets a `crate` plate automatically; list it under `ignore` to keep it off the page.

**Routing matrix.** `components` lists each component, its role, and the repositories that state they use it.

**Sealed bays.** `sealed` is a list of names. When one ships, delete it there and add a line.

**Text.** Anything outside the markers in `README.md` is yours. FACTORY CUT has capitals, figures and
`. : · - / ! + > <`; other characters are dropped from plate titles.

**Run it.**

```bash
python3 -m factory --offline    # redraw from the saved snapshot
python3 -m factory              # read the API first (set GITHUB_TOKEN to avoid the anonymous rate limit)
python3 -m factory --check      # what CI runs on pull requests
```

**The workflow.** [`factory.yml`](../.github/workflows/factory.yml) runs daily at 05:23 UTC, on pushes to `main`
that touch the generator, and from the Actions tab (*Factory* → *Run workflow*). It uses the repository's own
`GITHUB_TOKEN`; there is no secret to create. Only the `build` job may write, and only to this repository.

## Mantenimiento rápido (ES)

- **Cambiar textos o proyectos:** edita `factory/registry.json` y ejecuta `python3 -m factory --offline`.
- **Publicar un proyecto sellado:** quítalo de `sealed` y añádelo a `lines` con su repositorio.
- **Forzar una actualización:** pestaña *Actions* → *Factory* → *Run workflow*.
- **Si el flujo falla:** la página no se rompe; se queda con la última lectura buena. Mira el aviso en el
  registro de la ejecución.
- **Volver al perfil anterior:** está completo en [`archive/2026-09-30`](../archive/2026-09-30).
