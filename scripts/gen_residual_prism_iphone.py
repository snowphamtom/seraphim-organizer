#!/usr/bin/env python3
"""Residual Prism — iPhone portrait wallpaper (1170×2532).

Same Fibonacci crystalline polytope / dual-plane rings / claimed≤hull /
cyan→violet→magenta language as residual-prism, baked on solid black for
Lock Screen / wallpaper. Prism sits in the upper-mid third, clear of
Dynamic Island and home-indicator zones.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

from PIL import Image

ROOT = Path("/workspace/state/seraphim-organizer")
SPEC = importlib.util.spec_from_file_location(
    "gen_residual_prism", ROOT / "scripts" / "gen_residual_prism.py"
)
gen = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gen)

# Portrait wallpaper (iPhone 14/15 logical @3x)
W, H = 1170, 2532
PRISM = 820
FRAMES = 28
DURATION_MS = 35
QUALITY = 72
# Upper-mid third center (clear of Dynamic Island + home indicator)
CY = int(H * 0.355)


def main():
    out_dirs = [ROOT / "media", ROOT / "docs" / "media"]
    for d in out_dirs:
        d.mkdir(parents=True, exist_ok=True)

    gen.SIZE = PRISM
    gen.FRAMES = FRAMES
    gen.DURATION_MS = DURATION_MS

    verts0 = gen.fibonacci_sphere(gen.N_VERT)
    edges, lengths, is_skip = gen.build_edges(verts0)
    len_min, len_max = float(lengths.min()), float(lengths.max())
    print(f"iphone {W}x{H} prism={PRISM} frames={FRAMES} dur={DURATION_MS}ms cy={CY}")

    frames_rgb = []
    x0 = (W - PRISM) // 2
    y0 = CY - PRISM // 2
    for f in range(FRAMES):
        square = gen.render_frame(
            f, FRAMES, verts0, edges, lengths, is_skip, len_min, len_max
        )
        # Solid black bake (opaque — Lock Screen / wallpaper safe)
        canvas = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        canvas.alpha_composite(square, (x0, y0))
        frames_rgb.append(canvas.convert("RGB"))
        if f % 7 == 0:
            print(f"  frame {f}/{FRAMES}")

    still = frames_rgb[FRAMES // 5]

    for d in out_dirs:
        webp = d / "residual-prism-iphone.webp"
        png = d / "residual-prism-iphone.png"
        gif = d / "residual-prism-iphone.gif"
        frames_rgb[0].save(
            webp,
            "WEBP",
            save_all=True,
            append_images=frames_rgb[1:],
            duration=DURATION_MS,
            loop=0,
            quality=QUALITY,
            method=4,
        )
        still.save(png, "PNG", optimize=True)
        frames_rgb[0].save(
            gif,
            "GIF",
            save_all=True,
            append_images=frames_rgb[1:],
            duration=DURATION_MS,
            loop=0,
            disposal=2,
            optimize=True,
        )
        print(
            f"wrote {d.name}/ {webp.name} {webp.stat().st_size} "
            f"{png.name} {png.stat().st_size} {gif.name} {gif.stat().st_size}"
        )


if __name__ == "__main__":
    main()
