#!/usr/bin/env python3
"""Technology roadmap: the same designs on open PDKs and on i3dPDK_A16K.

Collects the OpenROAD-flow-scripts reference runs (scripts/orfs_ref.sh, in
out/_orfs/<platform>_<design>/) and this flow's runs (out/<design>/<LIB>/<tag>/),
and writes docs/roadmap/results.json, a markdown table on stdout and, with
--plot, docs/images/roadmap.png.

    roadmap.py [--plot]

Each ORFS platform keeps its own reference settings (clock, utilization);
the A16K runs use the clock of GT2N's reference design. Logic area = buffers,
inverters, flops and combinational cells (no fill, tap or endcap cells).
A16K timing and power use placeholder wire RC (the PDK has none), so they are
optimistic; the area is the PDK's own cell area.
"""
import json
import pathlib
import re
import sys

R = pathlib.Path(__file__).resolve().parent.parent
PLATFORMS = [  # (ORFS platform, label, node in nm for ordering)
    ("gf180", "GF 180 nm", 180), ("sky130hd", "SkyWater 130 nm", 130), ("ihp-sg13g2", "IHP 130 nm", 130),
    ("nangate45", "FreePDK 45 nm", 45), ("asap7", "ASAP7 7 nm", 7), ("gt2n", "GT2N 2 nm", 2)]
A16K = [("NSFET_5T", "A16K NSFET 5T", 1.6), ("CFET_3T", "A16K CFET 3T", 1.6)]
# this flow's runs used in the table: design -> (tag, clock ns)
A16K_RUNS = {"gcd": "p170", "aes": "rm350"}
LOGIC = ("clock_buffer", "clock_inverter", "timing_repair_buffer", "buffer", "inverter",
         "sequential_cell", "multi_input_combinational_cell")


def sdc_period(p, d, log):
    """Clock period (ns) of an ORFS run: from the copy of its SDC in the results."""
    f = R / f"out/_orfs/{p}_{d}/results/{p}/{d}/base/6_final.sdc"
    m = re.search(r"create_clock .*-period (\S+)", f.read_text()) if f.exists() else None
    if not m:
        return None
    v = float(m.group(1))
    return v / 1000 if p in ("asap7", "gt2n") else v   # these two platforms use ps


def orfs(p, label, d):
    b = R / f"out/_orfs/{p}_{d}/logs/{p}/{d}/base"
    try:
        f = json.loads((b / "6_report.json").read_text())
        r = json.loads((b / "5_2_route.json").read_text())
    except (OSError, ValueError):
        return None
    per = sdc_period(p, d, b)
    return dict(platform=label, flow="ORFS reference", clock_ns=per,
                fmax_ghz=f.get("finish__timing__fmax", 0) / 1e9,
                logic_area_um2=sum(f.get(f"finish__design__instance__area__class:{c}", 0) for c in LOGIC),
                logic_cells=sum(f.get(f"finish__design__instance__count__class:{c}", 0) for c in LOGIC),
                die_um2=f["finish__design__die__area"], wirelength_um=r["detailedroute__route__wirelength"],
                power_mw=f["finish__power__total"] * 1e3, drc=r["detailedroute__route__drc_errors"],
                routed=True)


def a16k(lib, label, d, tag):
    f = R / f"out/{d}/{lib}/{tag}"
    try:
        m = json.loads((f / "metrics.json").read_text())
        p = json.loads((f / "run_params.json").read_text())
    except (OSError, ValueError):
        return None
    per = float(p["clk_period_ns"])
    w, h = (float(x) for x in m["die_um"].split(" x "))
    routed = m["stage"] == "route"
    if routed:
        wns, wl, pw = float(m["final_setup_wns"]), m["wirelength_um"], m["power_mw"]
        drc = len(re.findall("violation type", (f / "rpt/drc.rpt").read_text()))
    else:  # STOP_AFTER=grt: global-route wirelength, post-GRT power estimate
        wns = float(m["grt_setup_wns"])
        wl = float(re.findall(r"GRT-0018\] Total wirelength: ([\d.]+)", (f / "openroad.log").read_text())[-1])
        tot = re.search(r"^Total\s+\S+\s+\S+\s+\S+\s+(\S+)", (f / "rpt/grt.rpt").read_text(), re.M)
        pw, drc = float(tot.group(1)) * 1e3, None
    return dict(platform=label, flow="this flow", clock_ns=per, fmax_ghz=1 / (per - wns),
                logic_area_um2=float(m["std_area_um2"]), logic_cells=m["cells"], die_um2=w * h,
                wirelength_um=wl, power_mw=pw, drc=drc, routed=routed)


def collect():
    out = {}
    for d in ("gcd", "aes"):
        rows = [orfs(p, label, d) for p, label, _ in PLATFORMS]
        rows += [a16k(lib, label, d, A16K_RUNS[d]) for lib, label, _ in A16K]
        out[d] = [r for r in rows if r]
    return out


def markdown(data):
    for d, rows in data.items():
        print(f"\n**{d}**\n")
        print("| Platform | Clock (ns) | Fmax (GHz) | Logic area (µm²) | Die (µm²) | Wirelength (µm) | Power (mW) | Energy / cycle (pJ) | DRC |")
        print("|---|---|---|---|---|---|---|---|---|")
        for r in rows:
            e = r["power_mw"] * r["clock_ns"]
            a16k = r["platform"].startswith("A16K")
            name = f"**{r['platform']}**" if a16k else r["platform"]
            drc = r["drc"] if r["routed"] else "not routed²"
            star = "¹" if a16k else ""
            fmt = lambda v: f"{v:,.0f}" if v >= 100 else f"{v:.3g}"
            print(f"| {name} | {r['clock_ns']:g} | {r['fmax_ghz']:.2f}{star} | {fmt(r['logic_area_um2'])} | "
                  f"{fmt(r['die_um2'])} | {fmt(r['wirelength_um'])} | {fmt(r['power_mw'])}{star} | {fmt(e)}{star} | {drc} |")


def plot(data, png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 14})
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), dpi=130, sharey=True)
    labels = [label for _, label, _ in PLATFORMS] + [label for _, label, _ in A16K]
    for ax, d in zip(axes, ("gcd", "aes")):
        rows = {r["platform"]: r for r in data[d]}
        ys = list(range(len(labels)))[::-1]
        for y, lab in zip(ys, labels):
            r = rows.get(lab)
            if not r:
                ax.text(1.2, y, "n/a", va="center", color="#777")
                continue
            a16k = lab.startswith("A16K")
            v = r["logic_area_um2"]
            ax.barh(y, v, height=0.6, color="#d9531e" if a16k else "#8c8c8c")
            txt = f"{v:,.0f}" if v >= 100 else f"{v:.3g}"
            if not r["routed"]:
                txt += " *"
            ax.text(v * 1.15, y, txt, va="center", fontsize=13)
        ax.set_xscale("log")
        ax.set_xlim(1, ax.get_xlim()[1] * 10)
        ax.set_yticks(ys)
        ax.set_yticklabels(labels)
        ax.tick_params(axis="y", length=0)
        ax.set_title(d, fontsize=16, loc="left")
        ax.set_xlabel("logic area (µm², log scale)")
        ax.grid(axis="x", color="#e5e5e5")
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
    fig.tight_layout()
    fig.savefig(png, facecolor="white")


def main():
    data = collect()
    out = R / "docs/roadmap"
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(data, indent=1) + "\n")
    markdown(data)
    if "--plot" in sys.argv:
        plot(data, R / "docs/images/roadmap.png")


if __name__ == "__main__":
    main()
