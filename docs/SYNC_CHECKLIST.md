# Seraphim sync checklist

Run this against a named commit before calling a build canon. Every item gets
PASS, FAIL or UNKNOWN plus evidence (file:line, sha256, screenshot path or a
request log). PASS without evidence counts as UNKNOWN. Read-only: no pushes or
posts while checking.

Target: `https://snowphamtom.github.io/seraphim-organizer/?v=<sha>` and `docs/`
at `<sha>`. First confirm the live `index.html` is byte-identical to
`docs/index.html` at that sha. If it isn't, stop and report the mismatch.

## 1. Desk labels
The rendered labels match the lanes exactly: ORGANIZED / HOLD / WATCH / NOISE /
INTAKE, plus the REFUSE and ASIDE stars. Quote the strings from the rendered DOM.

## 2. Plain visible copy
List every visible term or tooltip a first-time visitor wouldn't understand
(internal words such as residual, Δ, coh, GR-21, Magpie, CTI, interior, admit).
Exempt under HERO LOCK (Taylor's design choice): the `## ` headings, the
`> sort` syntax, the `## Disorganized` input and the title card's layout and
MACHINE THEATER heading. The title card's other text and all tooltips are NOT
exempt (Wizard scope decision, 2026-09-27).

## 3. Reduced motion
With `prefers-reduced-motion: reduce` emulated, the mesh drift, pulse, core rays,
spectrum bars and the background scan animation all stop or go static. Evidence
is two screenshots taken 2 s apart with a pixel diff near 0, plus the CSS/JS lines.

## 4. Overlays never cover text
At 1280×800 and 390×844, and at 0.5 s, 3 s, 8 s, after a sort and after the demo:
the title card, stars, lanes, mesh and spectrum bars never sit over or show
through the input, the trays, the buttons or the helper and status text. Check
with rect intersection and `elementFromPoint`, and check that the desk
background is opaque enough that nothing reads through it.

## 5. Standalone copy
`docs/index.html` and `docs/standalone.html` both exist and are byte-identical
(sha256 plus `cmp`). The live `/standalone.html` returns 200.

## 6. CANON.md is current
`docs/CANON.md` names the audited sha, and every line marked current matches
what actually renders (request count, palette, features).

## 7. Nothing uploaded
The header claim "runs in your browser · nothing is uploaded" holds: zero
network requests after the load event, in both a headless and a normal browser,
over 15 s of waiting, typing, sort, demo, CSV download and clear. That includes
the favicon. List every request made during load too.

## 8. Palette
Purple, black and white only. No gold, cyan, orange or pink in computed styles,
the favicon or rendered pixels. Leftover literals in the source are listed with
file:line even when overridden.

## Output
One line per item: `N. PASS|FAIL|UNKNOWN — evidence`. Then the fixes for each
FAIL. Record the commit you audited and where the evidence folder is.
