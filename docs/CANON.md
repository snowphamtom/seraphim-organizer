# Seraphim Organizer — canon

- **Centerpiece:** Taylor hex-iridescent GIF (`hexIridescentBg` / iridescent honeycomb on black) full-bleed — NOT keyed-star / cyber-nature / lattice / gold / gift-stack as hero
- **Overlay:** keyed neon-blue dodeca wire (`keyedDodecaWireOverlay` / `dodeca-wire-keyed.webp|.png`) hub-locked on the seal/dodeca (`--seal-x/--seal-y`), `mix-blend-mode:screen`, sized to the dodeca — not full-bleed
- **Core seed:** keyed yellow/magenta Seed-of-Life (`clientSeedInDodeca` / `seed-in-dodeca-keyed.webp|.png`) CENTERED INSIDE the wire at the same hub, screen/lighter, ~0.48 wire scale — not full-bleed hero
- **Proportional figures:** `clientProportionalFigures|sharedSealMetrics` — ALL figures share ONE center (`--seal-x/--seal-y` + `syncGyroSharedCenter`), ONE size family from `--seal-r` (seed < wire ≤ dodeca < network < field), ONE angle/orientation (shared `--gyro-*` / φ rigid stack); no independent random sizes or spins
- **Gold overlays:** `goldKeyedOverlays` — `gold-dotfield-keyed` depth/field hub-locked (`--seal-x/--seal-y`, screen/normal) + `gold-network-keyed` on/near dodeca inside `.omniGyroRig` (screen/lighter); content gold, backgrounds keyed out; reduced-motion → stills
- **Sync:** `clientOmniGyroSync|dodecaGyroAgreed|clientDodecaSync` — ONE shared hub (`--seal-x/--seal-y` + `syncGyroSharedCenter`); wire+seed+gold-network in `.omniGyroRig` (+ gold-dotfield) share cam YPR (`--gyro-yaw/--gyro-pitch/--gyro-roll`) with canvas dodeca — one rigid stack; ONE φ TEMPO (`syncTempoClock` / `--field-T*`); no second dodeca off-hub; no overlay drift
- **Palette:** void black `#000` + cyan/magenta/yellow/orange neon (purpleOnly removed)
- **Bg:** `#000` void + `media/hex-iridescent-bg.webp` (anim) / `hex-iridescent-bg.gif` fallback / `hex-iridescent-bg-still.webp` (reduced-motion / coarse); `object-fit:cover` centered
- **Chrome:** left `#dataRail`, bottom `#specBar`; desk labels **Disorganized / Organized / Aside**
- **Depth ladder (back→front):** void → hex-iridescent hero → gold-dotfield depth → canvas/procedural dodeca → keyed dodeca wire → gold-network → keyed seed core → desk (dark glass)
- **Seal:** thick readable cyan↔magenta Magpie bones; shared hub `--seal-x/--seal-y`; φ TEMPO only
- **Motion:** one φ family (`--field-T3` / `--Tphi3`); cam.gyro full omni rates; reduced-motion / coarse → stills / no tumble; idle demo pauses on type/focus
- **Fences:** no crystallize / release / dump / S_H in user-visible strings; no XYZ room grid; no white-paper void; no lattice-as-hero; prior heroes opacity 0 / display none
- **Live tip:** `?v=<shortsha>` — tip: clientProportionalFigures|sharedSealMetrics|goldKeyedOverlays|clientOmniGyroSync|dodecaGyroAgreed (proportional one-center/size/angle + gold keyed overlays on φ-gyro stack)
