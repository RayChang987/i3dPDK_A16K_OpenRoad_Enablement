#!/usr/bin/env python3
"""Re-snap the signal-pin RECTs of a platform cell LEF outward.

The platform cell LEFs put every coordinate on the 0.5 nm grid (DBU 2000).
They were first made with pins snapped *inward* (and OBS outward), which
narrowed pins the PDK draws at exactly 12 nm, the M1 minimum width, to
11.5 nm: on CFET_4T, INV_X16.A, NOR2_X1.A1 and 7 more, which TritonRoute then
cannot access (DRT-0073). This takes every signal-pin RECT from the PDK's own
cell LEF again and snaps it outward (at most 0.4 nm per edge), so no pin is
narrower than the PDK draws it. OBS and power pins are left as they are.

Usage: resnap_pins.py PDK_CELL_LEF PLATFORM_CELL_LEF   (rewrites the latter)
   e.g. resnap_pins.py $PDK_ROOT/BE/CFET/4T/i3dPDK_A16K_0V7_27C_4T.lef platform/lef/CFET_4T_cells.lef
"""
import math
import re
import sys

GRID = 0.0005


def is_signal(pin_body_lines):
    return not any(re.search(r"\bUSE (POWER|GROUND)\b", l) for l in pin_body_lines)


def signal_rects(text):
    """Signal-pin RECTs of the PDK LEF, in file order: (cell, pin, layer, rect)."""
    out = []
    for cell, body in re.findall(r"^MACRO (\S+)\n(.*?)^END \1", text, re.M | re.S):
        for pin, pb in re.findall(r"^\s*PIN (\S+)\n(.*?)^\s*END \1", body, re.M | re.S):
            if not is_signal(pb.splitlines()):
                continue
            layer = None
            for line in pb.splitlines():
                s = line.strip()
                if s.startswith("LAYER "):
                    layer = s.split()[1]
                elif s.startswith("RECT"):
                    out.append((cell, pin, layer, [float(v) for v in s.rstrip(";").split()[1:5]]))
    return out


def outward(r):
    f = lambda v: math.floor(v / GRID + 1e-6) * GRID
    c = lambda v: math.ceil(v / GRID - 1e-6) * GRID
    return [f(r[0]), f(r[1]), c(r[2]), c(r[3])]


def main():
    pdk_lef, plat_lef = sys.argv[1:3]
    src = signal_rects(open(pdk_lef).read())
    lines = open(plat_lef).read().splitlines()
    # signal-pin RECT lines of the platform LEF, in file order
    out, k, changed = [], 0, 0
    cell = pin = layer = None
    pin_lines, in_pin = [], False
    text = "\n".join(lines)
    sig = {(c, p) for c, body in re.findall(r"^MACRO (\S+)\n(.*?)^END \1", text, re.M | re.S)
           for p, pb in re.findall(r"^\s*PIN (\S+)\n(.*?)^\s*END \1", body, re.M | re.S)
           if is_signal(pb.splitlines())}
    for line in lines:
        s = line.strip()
        if s.startswith("MACRO "):
            cell = s.split()[1]
        elif s.startswith("PIN "):
            pin = s.split()[1]
        elif pin and s == f"END {pin}":
            pin = None
        elif s.startswith("LAYER "):
            layer = s.split()[1]
        elif s.startswith("RECT") and pin and (cell, pin) in sig:
            sc, sp, sl, r = src[k]
            if (sc, sp, sl) != (cell, pin, layer):
                sys.exit(f"order mismatch at {cell}/{pin}/{layer} vs PDK {sc}/{sp}/{sl}")
            k += 1
            new = "RECT " + " ".join(f"{v:.4f}" for v in outward(r)) + " ;"
            if new != s:
                changed += 1
            line = line[: len(line) - len(line.lstrip())] + new
        out.append(line)
    if k != len(src):
        sys.exit(f"{k} signal RECTs in {plat_lef}, {len(src)} in {pdk_lef}")
    for i, l in enumerate(out[:5]):
        if "coordinates snapped" in l:
            out[i] = l.replace("coordinates snapped to the 0.5nm manufacturing grid",
                               "coordinates on the 0.5nm grid (signal pins snapped outward, OBS outward)")
    open(plat_lef, "w").write("\n".join(out) + "\n")
    print(f"{plat_lef}: {k} signal-pin RECTs, {changed} changed")


if __name__ == "__main__":
    main()
