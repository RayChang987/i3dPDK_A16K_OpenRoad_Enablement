#!/usr/bin/env python3
"""One line per OpenROAD run: a16k_openroad_enablement/out/<design>/<LIB>/<tag>/metrics.json.

Usage: summarize.py [--md] [glob over <design>/<LIB>/<tag>, default */*/*]
All numbers are 1x (the OpenROAD flow runs on the 1x LEFs).
"""
import glob
import json
import pathlib
import sys

out = pathlib.Path(__file__).resolve().parent.parent / "out"
args = sys.argv[1:]
md = "--md" in args
args = [a for a in args if a != "--md"]
pattern = args[0] if args else "*/*/*"
cols = [("run", None), ("stage", "stage"), ("cells", "cells"), ("die_um", "die_um"),
        ("util", "util"), ("WNS", "final_setup_wns"), ("hold", "final_hold_wns"),
        ("WL_um", "wirelength_um"), ("mW", "power_mw"), ("DRC", "drc"),
        ("PG", None), ("runtime_s", None)]
rows = []
for d in sorted(out.glob(pattern)):
    f = d / "metrics.json"
    if d.name.startswith("_") or not f.exists():
        continue
    m = json.loads(f.read_text())
    rt = "?"
    v = d / "flow_version"
    if v.exists():
        for line in v.read_text().splitlines():
            if line.startswith("runtime_s"):
                rt = line.split()[1]
    row = []
    for name, key in cols:
        if name == "run":
            row.append(str(d.relative_to(out)))
        elif name == "PG":
            row.append("clean" if m.get("pg_VDD") == m.get("pg_VSS") == "clean" else "FAIL")
        elif name == "runtime_s":
            row.append(rt)
        else:
            row.append(str(m.get(key, "-")))
    rows.append(row)
head = [c[0] for c in cols]
if md:
    print("| " + " | ".join(head) + " |")
    print("|" + "---|" * len(head))
    for r in rows:
        print("| " + " | ".join(r) + " |")
else:
    w = [max(len(x) for x in col) for col in zip(head, *rows)]
    for r in [head] + rows:
        print("  ".join(x.ljust(n) for x, n in zip(r, w)))
