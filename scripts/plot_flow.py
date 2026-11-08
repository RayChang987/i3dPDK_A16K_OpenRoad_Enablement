#!/usr/bin/env python3
"""Flow diagram for the README ("The flow"): two columns of four steps.

    plot_flow.py [out.png]          (default docs/images/flow.png)

The left column runs down, the arrow leaves the last step to the right, goes
up over the right column and comes down into its first step.
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path
from matplotlib.patches import PathPatch

LEFT = [("Yosys netlist", ""),
        ("Floorplan", "IO pins, macros"),
        ("Power grid", "BPR, M3 stripes, ring"),
        ("Placement", "PDN-aware")]
RIGHT = [("CTS", "+ timing repair"),
         ("Global route", "+ timing repair"),
         ("Detailed route", "TritonRoute"),
         ("Outputs", "DEF, netlist, reports")]

W, H = 240, 62            # box
GAP = 36                  # between boxes in a column
X = (30, 350)             # left edge of each column
Y0 = 64                   # top of the first row
INK, SUB, EDGE, FILL = "#222222", "#666666", "#555555", "#f5f5f5"


def box(ax, x, y, title, sub):
    ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle="round,pad=0,rounding_size=8",
                                fc=FILL, ec=EDGE, lw=1.4))
    if sub:
        ax.text(x + W / 2, y + H / 2 - 9, title, ha="center", va="center", fontsize=15,
                color=INK, fontweight="bold")
        ax.text(x + W / 2, y + H / 2 + 12, sub, ha="center", va="center", fontsize=12.5, color=SUB)
    else:
        ax.text(x + W / 2, y + H / 2, title, ha="center", va="center", fontsize=15,
                color=INK, fontweight="bold")


def arrow(ax, verts):
    """Polyline with rounded corners and an arrow head at the end (y grows downward)."""
    r = 12
    codes, pts = [Path.MOVETO], [verts[0]]
    for i in range(1, len(verts) - 1):
        (x0, y0), (x1, y1), (x2, y2) = verts[i - 1], verts[i], verts[i + 1]
        def toward(ax_, ay, bx, by, d):
            dx, dy = bx - ax_, by - ay
            n = (dx * dx + dy * dy) ** 0.5
            return ax_ + dx / n * d, ay + dy / n * d
        pts += [toward(x1, y1, x0, y0, r), (x1, y1), toward(x1, y1, x2, y2, r)]
        codes += [Path.LINETO, Path.CURVE3, Path.CURVE3]
    # stop the line short of the tip; the arrow patch draws the last bit
    (xa, ya), (xb, yb) = verts[-2], verts[-1]
    n = ((xb - xa) ** 2 + (yb - ya) ** 2) ** 0.5
    stub = (xb - (xb - xa) / n * 8, yb - (yb - ya) / n * 8)
    pts.append(stub)
    codes.append(Path.LINETO)
    ax.add_patch(PathPatch(Path(pts, codes), fill=False, ec=EDGE, lw=1.6, capstyle="round"))
    ax.add_patch(FancyArrowPatch(stub, verts[-1], arrowstyle="-|>,head_length=7,head_width=4",
                                 color=EDGE, lw=1.6, shrinkA=0, shrinkB=0))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "docs/images/flow.png"
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    width = X[1] + W + 30
    height = Y0 + 4 * H + 3 * GAP + 30
    fig = plt.figure(figsize=(width / 100, height / 100), dpi=200)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")

    for col, steps in zip(X, (LEFT, RIGHT)):
        for i, (title, sub) in enumerate(steps):
            y = Y0 + i * (H + GAP)
            box(ax, col, y, title, sub)
            if i < len(steps) - 1:
                arrow(ax, [(col + W / 2, y + H), (col + W / 2, y + H + GAP)])

    # last step on the left -> right, up over the right column, down into its first step
    y_last = Y0 + 3 * (H + GAP) + H / 2
    x_mid = (X[0] + W + X[1]) / 2
    top = Y0 - 40
    arrow(ax, [(X[0] + W, y_last), (x_mid, y_last), (x_mid, top), (X[1] + W / 2, top), (X[1] + W / 2, Y0)])

    fig.savefig(out, facecolor="white")
    print(out)


if __name__ == "__main__":
    main()
