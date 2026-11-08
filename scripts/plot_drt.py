#!/usr/bin/env python3
"""Detailed-routing convergence plot: DRT violations per iteration.

    plot_drt.py out.png <run_dir>:<label> [<run_dir>:<label> ...] [--dark]

Each run_dir is an out/<design>/<LIB>/<tag>/ directory; the violation counts
come from its openroad.log ("Number of violations = N" after every
optimization iteration). Log y axis; a run that reaches 0 ends in a marker on
the "0" line below the axis.
"""
import argparse
import math
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LIGHT = dict(surface="#fcfcfb", text="#0b0b0b", muted="#52514e", grid="#e4e3df",
             series=["#2a78d6", "#eb6834", "#1baf7a", "#eda100"])
DARK = dict(surface="#1a1a19", text="#f0efec", muted="#c3c2b7", grid="#33332f",
            series=["#3987e5", "#d95926", "#199e70", "#c98500"])


def violations(run_dir):
    txt = open(f"{run_dir}/openroad.log", errors="replace").read()
    return [int(n) for n in re.findall(r"Number of violations = (\d+)", txt)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("png")
    ap.add_argument("runs", nargs="+", metavar="run_dir:label")
    ap.add_argument("--dark", action="store_true")
    ap.add_argument("--title", default="Detailed routing convergence (TritonRoute)")
    a = ap.parse_args()
    th = DARK if a.dark else LIGHT
    if len(a.runs) > len(th["series"]):
        raise SystemExit("at most %d runs" % len(th["series"]))

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11})
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    fig.patch.set_facecolor(th["surface"])
    ax.set_facecolor(th["surface"])
    zero_y = 0.3                                   # where "0 violations" is drawn
    xmax = 0
    ymax = 1
    for i, spec in enumerate(a.runs):
        run, label = spec.split(":", 1)
        v = violations(run)
        c = th["series"][i]
        xs = list(range(len(v)))
        ys = [n if n > 0 else zero_y for n in v]
        ax.plot(xs, ys, color=c, linewidth=2, solid_capstyle="round", zorder=3)
        ax.plot(xs[-1], ys[-1], "o", color=c, markersize=8, markeredgecolor=th["surface"],
                markeredgewidth=2, zorder=4)
        end = "0 DRC" if v[-1] == 0 else f"{v[-1]:,}"
        ax.annotate(f"{label}  ({end})", (xs[-1], ys[-1]), xytext=(8, 0), textcoords="offset points",
                    va="center", color=th["text"], fontsize=10)
        ax.plot([], [], color=c, linewidth=2, label=label)
        xmax = max(xmax, xs[-1])
        ymax = max(ymax, max(v))
    ax.set_yscale("log")
    ax.set_ylim(zero_y * 0.7, 10 ** math.ceil(math.log10(ymax)))
    ax.axhline(zero_y, color=th["muted"], linewidth=0.8, linestyle=(0, (2, 3)), zorder=1)
    ticks = [t for t in (1, 10, 100, 1000, 10000, 100000) if t <= ax.get_ylim()[1]]
    ax.set_yticks([zero_y] + ticks)
    ax.set_yticklabels(["0"] + [f"{t:,}" for t in ticks])
    ax.minorticks_off()
    ax.set_xlim(-0.5, xmax * 1.45 + 1)
    ax.set_xlabel("Optimization iteration", color=th["muted"])
    ax.set_ylabel("DRC violations (log)", color=th["muted"])
    ax.grid(axis="y", color=th["grid"], linewidth=0.8, zorder=0)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(th["grid"])
    ax.tick_params(colors=th["muted"], length=0)
    ax.set_title(a.title, loc="left", color=th["text"], fontsize=13, pad=12)
    leg = ax.legend(loc="upper right", frameon=False, fontsize=9.5)
    for t in leg.get_texts():
        t.set_color(th["text"])
    fig.tight_layout()
    fig.savefig(a.png, facecolor=th["surface"])


if __name__ == "__main__":
    main()
