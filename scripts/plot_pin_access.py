#!/usr/bin/env python3
"""Pin-access figure for the README (open problem 1).

    plot_pin_access.py out.png <placed.def> <cells.lef> <drc.rpt> [--window x0,y0,w,rows]

Left: a few rows of placed cells with their M1 signal pins and the M2 tracks
of the DEF. A pin an M2 track runs through is filled, one between two tracks
is drawn as an outline. Right: every marker of a TritonRoute DRC report on
the die.
"""
import argparse
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

PIN = "#d9531e"
TRACK = "#3b6fb6"
RAIL = "#e6e6e6"
CELL = "#9a9a9a"


def read_lef(path):
    """{macro: (w, h, [(x1, y1, x2, y2) M1 signal-pin rects])} in um."""
    cells, cur, pin, layer = {}, None, None, None
    for line in open(path):
        t = line.split()
        if not t:
            continue
        if t[0] == "MACRO":
            cur = t[1]; cells[cur] = [0, 0, []]
        elif cur and t[0] == "SIZE":
            cells[cur][0], cells[cur][1] = float(t[1]), float(t[3])
        elif cur and t[0] == "PIN":
            pin = t[1]
        elif cur and t[0] == "LAYER":
            layer = t[1]
        elif cur and pin and t[0] == "RECT" and layer == "M1" and not pin.startswith(("VDD", "VSS")):
            cells[cur][2].append(tuple(float(v) for v in t[1:5]))
        elif t[0] == "END" and len(t) > 1:
            if t[1] == pin:
                pin = None
            elif t[1] == cur:
                cur = None
    return cells


def read_def(path):
    txt = open(path).read()
    dbu = float(re.search(r"UNITS DISTANCE MICRONS (\d+)", txt).group(1))
    die = [float(v) / dbu for v in re.search(r"DIEAREA \( (\S+) (\S+) \) \( (\S+) (\S+) \)", txt).groups()]
    m2 = re.search(r"TRACKS Y (\S+) DO (\d+) STEP (\S+) LAYER M2", txt)
    tracks = (float(m2.group(1)) / dbu, int(m2.group(2)), float(m2.group(3)) / dbu)
    comps = []
    sec = txt[txt.index("\nCOMPONENTS"):txt.index("END COMPONENTS")]
    for m in re.finditer(r"- (\S+) (\S+)[^;]*?\+ (?:PLACED|FIXED) \( (\S+) (\S+) \) (\S+)", sec):
        comps.append((m.group(2), float(m.group(3)) / dbu, float(m.group(4)) / dbu, m.group(5)))
    rows = sorted({float(m.group(1)) / dbu for m in re.finditer(r"ROW \S+ \S+ \S+ (\S+)", txt)})
    return dbu, die, tracks, comps, rows


def read_drc(path):
    """[(x, y, layer)]: the centre of every violation marker."""
    pts = []
    num = r"\s*([-\d.]+),\s*([-\d.]+)\s*"
    for m in re.finditer(r"bbox = \(" + num + r"\) - \(" + num + r"\) on Layer (\S+)", open(path).read()):
        x1, y1, x2, y2 = map(float, m.groups()[:4])
        pts.append(((x1 + x2) / 2, (y1 + y2) / 2, m.group(5)))
    return pts


def orient(rect, w, h, o):
    x1, y1, x2, y2 = rect
    if o in ("FS", "S"):
        y1, y2 = h - y2, h - y1
    if o in ("FN", "S"):
        x1, x2 = w - x2, w - x1
    return x1, y1, x2, y2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("png")
    ap.add_argument("def_file")
    ap.add_argument("lef")
    ap.add_argument("drc")
    ap.add_argument("--window", default="", help="x0,y0,width,rows in um (default: centre of the core)")
    a = ap.parse_args()

    cells = read_lef(a.lef)
    dbu, die, (t0, tn, tstep), comps, rows = read_def(a.def_file)
    pts = read_drc(a.drc)
    row_h = rows[1] - rows[0]
    tracks = [t0 + k * tstep for k in range(tn)]

    if a.window:
        x0, y0, ww, nrows = (float(v) for v in a.window.split(","))
        nrows = int(nrows)
    else:
        ww, nrows = 0.46, 4                  # 4 rows of 54 nm = 9 M2 pitches: every track phase
        x0, y0 = (die[0] + die[2]) / 2 - ww / 2, rows[len(rows) // 2]
    y1 = y0 + nrows * row_h

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 14})
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(14, 5.6), dpi=130,
                                 gridspec_kw=dict(width_ratios=[1.75, 1]))
    nm = lambda v, o: (v - o) * 1000

    # left: cells, pins, tracks (nm, relative to the window)
    for r in rows:
        if y0 - 1e-6 <= r <= y1 + 1e-6:
            ax.add_patch(Rectangle((0, nm(r, y0) - 13.5), ww * 1000, 27, color=RAIL, lw=0, zorder=0))
    for t in tracks:
        if y0 - 0.014 <= t <= y1 + 0.014:
            ax.axhline(nm(t, y0), color=TRACK, lw=1, ls="--", zorder=1)
    on_track = [[0, 0] for _ in range(nrows)]          # per row: square pins, of them on a track
    n_pins = n_hit = 0
    for name, cx, cy, o in comps:
        if name not in cells:
            continue
        w, h, pins = cells[name]
        if cx + w < x0 or cx > x0 + ww or cy + h <= y0 + 1e-6 or cy >= y1 - 1e-6:
            continue
        ax.add_patch(Rectangle((nm(cx, x0), nm(cy, y0)), w * 1000, h * 1000, fill=False,
                               ec=CELL, lw=0.8, zorder=2))
        for p in pins:
            px1, py1, px2, py2 = orient(p, w, h, o)
            gx1, gy1, gx2, gy2 = cx + px1, cy + py1, cx + px2, cy + py2
            if gx2 < x0 or gx1 > x0 + ww:
                continue
            hit = any(gy1 - 1e-9 <= t <= gy2 + 1e-9 for t in tracks)
            n_pins += 1
            n_hit += hit
            if gy2 - gy1 < 0.013:
                r = int((gy1 - y0) // row_h)
                if 0 <= r < nrows:
                    on_track[r][0] += 1
                    on_track[r][1] += hit
            ax.add_patch(Rectangle((nm(gx1, x0), nm(gy1, y0)), (gx2 - gx1) * 1000, (gy2 - gy1) * 1000,
                                   fc=PIN if hit else "white", ec=PIN, lw=1.5, zorder=3))
    for r, (n, k) in enumerate(on_track):
        if n:
            ax.text(ww * 1000 + 8, (r + 0.5) * row_h * 1000, "on a track" if k > n / 2 else "between tracks",
                    va="center", fontsize=13, color=PIN, clip_on=False)
    ax.set_xlim(0, ww * 1000)
    ax.set_ylim(-14, nrows * row_h * 1000 + 14)
    ax.set_aspect("equal")
    ax.set_xlabel("nm")
    ax.set_title("CFET 3T cells: M1 pins (orange) and M2 tracks (dashed)", fontsize=15, loc="left")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)

    # right: DRC markers on the die
    bx.scatter([p[0] for p in pts], [p[1] for p in pts], s=6, color=PIN, alpha=0.45, lw=0)
    bx.add_patch(Rectangle((die[0], die[1]), die[2] - die[0], die[3] - die[1], fill=False, ec="black", lw=1))
    bx.set_xlim(die[0] - 0.15, die[2] + 0.15)
    bx.set_ylim(die[1] - 0.15, die[3] + 0.15)
    bx.set_aspect("equal")
    bx.set_xlabel("µm")
    m2 = sum(p[2] == "M2" for p in pts) / max(1, len(pts))
    bx.set_title(f"SERV: {len(pts):,} DRC markers", fontsize=15, loc="left")
    for side in ("top", "right"):
        bx.spines[side].set_visible(False)

    fig.tight_layout(w_pad=4)
    fig.savefig(a.png, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    print(f"{a.png}: window pins {n_pins}, on an M2 track {n_hit}; {len(pts)} DRC markers, {m2:.0%} on M2")


if __name__ == "__main__":
    main()
