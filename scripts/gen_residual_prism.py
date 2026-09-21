#!/usr/bin/env python3
"""Residual Prism — crystalline Fibonacci admission field for Seraphim.

Unique visual language: Magpie cyan/magenta spectral polytope on keyed black.
Not a paste of PI-SLICES / quad-fib / lattice GIFs.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PHI = (1.0 + math.sqrt(5.0)) / 2.0
GA = 2.0 * math.pi / (PHI * PHI)

SIZE = 592
FRAMES = 60
DURATION_MS = 50
QUALITY = 70
N_VERT = 72
NEAR_K = 3
PHI_SKIP = 13


def fibonacci_sphere(n: int) -> np.ndarray:
    i = np.arange(n, dtype=np.float64)
    y = 1.0 - 2.0 * (i + 0.5) / n
    r = np.sqrt(np.maximum(0.0, 1.0 - y * y))
    theta = GA * i
    x = r * np.cos(theta)
    z = r * np.sin(theta)
    return np.stack([x, y, z], axis=1)


def rot_y(pts, a):
    c, s = math.cos(a), math.sin(a)
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float64)
    return pts @ R.T


def rot_x(pts, a):
    c, s = math.cos(a), math.sin(a)
    R = np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float64)
    return pts @ R.T


def rot_z(pts, a):
    c, s = math.cos(a), math.sin(a)
    R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float64)
    return pts @ R.T


def project(pts, scale, cx, cy, cam_z=3.55):
    z = pts[:, 2]
    d = np.clip(cam_z - z, 0.6, None)
    f = scale / d
    x2 = cx + pts[:, 0] * f
    y2 = cy - pts[:, 1] * f
    depth = (z - z.min()) / (z.max() - z.min() + 1e-9)
    return np.stack([x2, y2], axis=1), depth, f


def build_edges(pts):
    n = len(pts)
    d2 = np.sum((pts[:, None, :] - pts[None, :, :]) ** 2, axis=2)
    np.fill_diagonal(d2, np.inf)
    edges = set()
    skip_set = set()
    for i in range(n):
        nn = np.argpartition(d2[i], NEAR_K)[:NEAR_K]
        for j in nn:
            a, b = (i, int(j)) if i < j else (int(j), i)
            if a != b:
                edges.add((a, b))
        j = (i + PHI_SKIP) % n
        a, b = (i, j) if i < j else (j, i)
        edges.add((a, b))
        skip_set.add((a, b))
        j2 = (i + 8) % n
        a, b = (i, j2) if i < j2 else (j2, i)
        edges.add((a, b))
        skip_set.add((a, b))
    elist = sorted(edges)
    lengths = np.array([np.linalg.norm(pts[a] - pts[b]) for a, b in elist])
    is_skip = np.array([(a, b) in skip_set for a, b in elist])
    return elist, lengths, is_skip


def residual_color(t, alpha):
    t = float(np.clip(t, 0.0, 1.0))
    stops = [
        (0.00, (55, 235, 242)),
        (0.30, (95, 155, 255)),
        (0.60, (175, 85, 235)),
        (1.00, (240, 70, 205)),
    ]
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if t <= t1 or i == len(stops) - 2:
            u = 0.0 if t1 == t0 else (t - t0) / (t1 - t0)
            u = float(np.clip(u, 0.0, 1.0))
            r = int(c0[0] + (c1[0] - c0[0]) * u)
            g = int(c0[1] + (c1[1] - c0[1]) * u)
            b = int(c0[2] + (c1[2] - c0[2]) * u)
            return (r, g, b, alpha)
    return (240, 70, 205, alpha)


def soft_disk(draw, xy, r, color, layers=7):
    x, y = xy
    for i in range(layers, 0, -1):
        f = i / layers
        a = int(color[3] * (0.25 + 0.75 * (1.0 - f) ** 1.55))
        rr = r * (0.4 + 0.7 * f)
        c = (color[0], color[1], color[2], max(0, min(255, a)))
        draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=c)


def draw_ring_3d(draw, radius, tilt, yaw, roll, cx, cy, scale, cam_z,
                 solid=True, color=(80, 220, 230, 180), width=2, phase=0.0,
                 dash_on_n=6, dash_off_n=5):
    n = 120
    t = np.linspace(0, 2 * math.pi, n, endpoint=False) + phase
    pts = np.stack([radius * np.cos(t), radius * np.sin(t), np.zeros_like(t)], axis=1)
    pts = rot_x(pts, tilt)
    pts = rot_y(pts, yaw)
    pts = rot_z(pts, roll)
    p2, depth, _ = project(pts, scale, cx, cy, cam_z)
    seq = list(range(n)) + [0]
    if solid:
        for i in range(n):
            a, b = seq[i], seq[i + 1]
            d = 0.5 * (depth[a] + depth[b])
            aa = int(color[3] * (0.50 + 0.50 * d))
            col = (color[0], color[1], color[2], aa)
            # soft underglow
            gcol = (color[0], color[1], color[2], int(aa * 0.35))
            draw.line([tuple(p2[a]), tuple(p2[b])], fill=gcol, width=width + 2)
            draw.line([tuple(p2[a]), tuple(p2[b])], fill=col, width=width)
    else:
        dash_on = True
        run = 0
        path = []
        for i in range(n):
            a = seq[i]
            path.append(tuple(p2[a]))
            run += 1
            limit = dash_on_n if dash_on else dash_off_n
            if run >= limit:
                if dash_on and len(path) >= 2:
                    d = depth[a]
                    aa = int(color[3] * (0.35 + 0.45 * d))
                    col = (color[0], color[1], color[2], aa)
                    draw.line(path, fill=col, width=max(1, width))
                path = [tuple(p2[a])]
                run = 0
                dash_on = not dash_on


def claimed_core_radius(frame, frames, hull_r):
    phase = 2 * math.pi * frame / frames
    base = 0.34 + 0.05 * math.sin(phase * PHI)
    r = hull_r * min(0.47, max(0.28, base))
    contract = 0.5 + 0.5 * math.sin(phase)
    return r, contract


def headroom_chord(draw, cx, cy, size, fill_t):
    w = size * 0.38
    h = size * 0.014
    x0 = cx - w / 2
    y0 = cy + size * 0.40
    draw.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=h / 2, fill=(25, 40, 55, 70))
    fw = w * float(np.clip(fill_t, 0.0, 1.0))
    if fw > 1.5:
        steps = max(10, int(fw / 3))
        for i in range(steps):
            u = i / max(1, steps - 1)
            col = residual_color(u * 0.9, int(150 + 55 * u))
            xa = x0 + fw * i / steps
            xb = x0 + fw * (i + 1) / steps + 0.5
            draw.rectangle([xa, y0, xb, y0 + h], fill=col)
        soft_disk(draw, (x0 + fw, y0 + h / 2), 5.5, (70, 220, 230, int(50 + 70 * fill_t)), layers=4)


def render_frame(frame, frames, verts0, edges, lengths, is_skip, len_min, len_max):
    size = SIZE
    cx = cy = size / 2.0
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")

    t = frame / frames
    yaw = t * 2 * math.pi
    pitch = 0.20 + 0.18 * math.sin(t * 2 * math.pi / PHI)
    roll = t * 2 * math.pi / (PHI ** 2) * 0.4

    verts = rot_z(rot_x(rot_y(verts0, yaw), pitch), roll)
    scale = size * 0.36
    cam_z = 3.55
    p2, depth, _ = project(verts, scale, cx, cy, cam_z)
    hull_r = scale / cam_z * 1.08

    # Dual-plane orbital rings — distinct radii, φ-related rates, never fuse
    ring_yaw_solid = t * 2 * math.pi / PHI
    ring_yaw_dash = -t * 2 * math.pi / (PHI ** 2)
    # solid Boolean plane (bright cyan) — outer
    draw_ring_3d(
        draw, radius=1.22, tilt=0.72, yaw=ring_yaw_solid, roll=0.12,
        cx=cx, cy=cy, scale=scale, cam_z=cam_z,
        solid=True, color=(70, 235, 242, 220), width=2, phase=0.0,
    )
    # dashed η plane (quiet magenta) — inner, parallel tilt family, offset
    draw_ring_3d(
        draw, radius=1.02, tilt=0.74, yaw=ring_yaw_dash, roll=-0.10,
        cx=cx, cy=cy, scale=scale, cam_z=cam_z,
        solid=False, color=(220, 95, 215, 155), width=1, phase=math.pi / 6,
        dash_on_n=5, dash_off_n=4,
    )

    edge_depth = []
    for (a, b), L, sk in zip(edges, lengths, is_skip):
        d = 0.5 * (depth[a] + depth[b])
        edge_depth.append((d, a, b, L, sk))
    edge_depth.sort(key=lambda x: x[0])
    mid = len(edge_depth) // 2

    def draw_edge(a, b, L, d, sk):
        tn = (L - len_min) / (len_max - len_min + 1e-9)
        aa = int(70 + 150 * d)
        if sk:
            aa = int(aa * 0.72)
            w = 1
        else:
            w = 2 if d > 0.45 else 1
        col = residual_color(tn, aa)
        gcol = residual_color(tn, int(aa * 0.4))
        draw.line([tuple(p2[a]), tuple(p2[b])], fill=gcol, width=w + 2)
        draw.line([tuple(p2[a]), tuple(p2[b])], fill=col, width=w)

    for i, (d, a, b, L, sk) in enumerate(edge_depth):
        if i == mid:
            cr, _ = claimed_core_radius(frame, frames, hull_r)
            pulse = 0.90 + 0.10 * math.sin(t * 2 * math.pi * PHI)
            # CLAIMED ≤ INTERIOR — soft core never breaches hull
            soft_disk(draw, (cx, cy), cr * pulse * 1.55, (30, 160, 210, 32), layers=6)
            soft_disk(draw, (cx, cy), cr * pulse * 1.15, (55, 220, 235, 80), layers=8)
            soft_disk(draw, (cx, cy), cr * pulse * 0.62, (190, 110, 230, 55), layers=5)
            soft_disk(draw, (cx, cy), cr * pulse * 0.28, (240, 250, 255, 110), layers=4)
            br = cr * pulse
            draw.ellipse([cx - br, cy - br, cx + br, cy + br], outline=(100, 235, 245, 130), width=1)
            # second whisper ring inside hull affirmation
            hr = hull_r * 1.05
            draw.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], outline=(70, 150, 190, 40), width=1)
        draw_edge(a, b, L, d, sk)

    order = np.argsort(depth)
    for i in order:
        d = depth[i]
        r = 1.8 + 2.6 * d
        col = residual_color(0.12 + 0.65 * (1.0 - d), int(140 + 90 * d))
        soft_disk(draw, (float(p2[i, 0]), float(p2[i, 1])), r * 2.1,
                  (col[0], col[1], col[2], int(col[3] * 0.4)), layers=4)
        draw.ellipse(
            [p2[i, 0] - r, p2[i, 1] - r, p2[i, 0] + r, p2[i, 1] + r],
            fill=(min(255, col[0] + 30), min(255, col[1] + 20), min(255, col[2] + 20), min(255, col[3] + 50)),
        )

    # residual energy → headroom fill (contracts → fills)
    V = 0.5 + 0.5 * math.cos(t * 2 * math.pi)
    fill_t = float(np.clip(1.0 - V * 0.88, 0.10, 1.0))
    headroom_chord(draw, cx, cy, size, fill_t)

    bloom = layer.filter(ImageFilter.GaussianBlur(radius=1.25))
    img = Image.alpha_composite(img, bloom)
    img = Image.alpha_composite(img, layer)

    # gentle black key — only near-empty pixels
    arr = np.array(img)
    lum = arr[:, :, 0].astype(np.int16) + arr[:, :, 1] + arr[:, :, 2]
    mask = (lum < 10) & (arr[:, :, 3] < 28)
    arr[mask, 3] = 0
    return Image.fromarray(arr, "RGBA")


def main():
    root = Path("/workspace/state/seraphim-organizer")
    out_dirs = [root / "media", root / "docs" / "media"]
    for d in out_dirs:
        d.mkdir(parents=True, exist_ok=True)

    verts0 = fibonacci_sphere(N_VERT)
    edges, lengths, is_skip = build_edges(verts0)
    len_min, len_max = float(lengths.min()), float(lengths.max())
    print(f"verts={N_VERT} edges={len(edges)} frames={FRAMES} size={SIZE}")

    frames = []
    for f in range(FRAMES):
        frames.append(render_frame(f, FRAMES, verts0, edges, lengths, is_skip, len_min, len_max))
        if f % 15 == 0:
            print(f"  frame {f}/{FRAMES}")

    still = frames[FRAMES // 5]
    for d in out_dirs:
        webp = d / "residual-prism.webp"
        png = d / "residual-prism.png"
        gif = d / "residual-prism.gif"
        frames[0].save(
            webp, "WEBP", save_all=True, append_images=frames[1:],
            duration=DURATION_MS, loop=0, quality=QUALITY, method=4,
        )
        still.save(png, "PNG", optimize=True)
        frames[0].save(
            gif, "GIF", save_all=True, append_images=frames[1:],
            duration=DURATION_MS, loop=0, disposal=2, optimize=True,
        )
        print(f"wrote {webp.name} {webp.stat().st_size} {png.name} {png.stat().st_size} {gif.name} {gif.stat().st_size}")


if __name__ == "__main__":
    main()
