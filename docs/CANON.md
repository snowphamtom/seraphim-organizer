# Seraphim Organizer — saved canon

- **Live:** https://snowphamtom.github.io/seraphim-organizer/?v=PLACEHOLDER
- **Commit:** `PLACEHOLDER` (`tunnelAsSent` after `gatherThenSort`)
- **Saved:** 2026-09-21 CT

## Markers
`tunnelAsSent` · `gatherThenSort` · `tunnelGridBg` · `stripToBones` · `excessPrune` · `bgSealCenterLock` · `hybridEngineTrio` · `masterpieceFlow` · `balancePolish` · `refinePolish2` · `sortTheater` · `idleDemoLoop` · `markdownMaster` · `motionIntricateFast` · `dodecaSeal`

## tunnelAsSent (GIF as Taylor sent)

Hard-refresh must look like Taylor’s tunnel-dots GIF as the site background.

**KEEP**
- Original-fidelity `media/tunnel-grid.gif` (light gray bg, black dots, 500×500) — no invert, no heavy recompress
- Full-bleed `object-fit:cover`; opacity ≈0.95
- VP center on seal via `--seal-x/--seal-y` + simple `translate(-50%,-50%)` (no perspective / rotateX corridor warp)
- Seal (`#fx`) + desk (`#sortDesk`) above (z-index); soft dark scrim under desk only

**KILL**
- `filter:invert`, `mix-blend-mode:screen`
- Heavy dark vignette / mask / `#bgField .tunnelGrid::after`
- Perspective corridor warp that makes the GIF unrecognizable
- Muddy canvas underlays: beams / plasma / aurora / WebGL `#fxgl` (no-op or display:none)
- Full-field seal contrast veil over the tunnel

## gatherThenSort (visible gather + sort)

Idle loop is gather→sort ≈ every 21s when desk idle.

**KEEP**
- Real gather: `fetch("media/live-gather.csv?t="+Date.now())` same-origin (site public corpus file — not live X API from the browser)
- Soft path into `organize()` like idle; on fail → `IDLE_PUBLIC_PACK`
- Visible `#phaseWhisper`: `gathering…` → `sorting…` → quiet
- Pause on user type (`idleDemoAllowed` / desk touch cooldown)
- `tunnelAsSent` sole `#bgField`; `stripToBones` seal/desk skeleton

**Corpus**
- `docs/media/live-gather.csv` (+ root `media/` mirror) — public-safe Drive-shaped + scrubbed post-style titles; no Magpie secrets/patents

## stripToBones (honest skeleton)

Aggressive subtract. Keep only what makes Seraphim hit.

**KEEP**
- Dodeca seal authority (`drawHexFrame` + breath)
- Center lock (`syncGyroSharedCenter` → `--seal-x/--seal-y`)
- Desk story: Disorganized → Organized / Aside (markdown desk + sort theater + idle demo)
- φ TEMPO motion (shared clocks)
- Clear light/shadow (soft bloomClamp under seal — anti-blotch, quiet)

**KILL / no-op** (fight clarity when stacked)
- Aurora, fog shards, ghost/dual hex underlays, starfield-in-panels, three/webgl star underlays
- Chimera custom field, ink-wash, nested seals, geodesic accents, chromatic edge fringe
- Hybrid bridge spokes, gyro orbit rings, CRT polish, constellation, depth-fog vignette, prove-break HUD
- Prior densify ornament: stipple, biomorphic filigree, ink-echo chords, quasicrystal, Ylm/Hopf sphereWire
- Old `#bgField` whispers (codeRain / beamWhisper / coreWhisper) and retired `.meta` GIF plates
- Beams / plasma under `tunnelAsSent` (muddy light GIF)

## Layers
`#bgField` light field + sole `tunnelGrid` (Taylor GIF **as sent**, α≈0.95, VP = seal) → canvas `#fx` seal boss → desk with soft local scrim

## Labels
Disorganized → Organized / Aside
