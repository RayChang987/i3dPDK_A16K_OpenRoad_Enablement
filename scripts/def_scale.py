#!/usr/bin/env python3
"""Scale every length in a DEF by N (e.g. 4) or 1/N, keeping the DBU.

Used to hand a placed design between this 1x flow and a flow that runs the
same PDK on N-x LEFs (lef_x4: every length x4, DBU 2000 in both). Only
geometry is scaled: coordinates, widths, steps, via parameters, halos,
spacings. Counts (DO/BY, ROWCOL), masks and names are not.

Usage:
  def_scale.py IN.def OUT.def --scale 4        1x -> 4x
  def_scale.py IN.def OUT.def --scale 1/4      4x -> 1x
Options:
  --strip-routing        drop the routing of regular nets (keep connectivity
                         and the special nets): a placed, unrouted design
  --keep-row-sites S,..  keep only ROWs on these sites (others are dropped)
  --drop-gcellgrid       drop GCELLGRID (each router builds its own)
A down-scaled value that is not a whole DBU is rounded and counted; the
count is printed (it should be 0).
"""
import argparse
import re
import sys
from fractions import Fraction

TOK = re.compile(r'"[^"]*"|\S+')
# keyword -> number of following values that are lengths
KW_LEN = {"CUTSIZE": 2, "CUTSPACING": 2, "ENCLOSURE": 4, "ORIGIN": 2, "OFFSET": 4,
          "DESIGNRULEWIDTH": 1, "WIREEXT": 1, "DIAGWIDTH": 1, "ROUTEHALO": 1}
WIRE_KW = {"ROUTED", "FIXED", "COVER", "NEW", "NOSHIELD"}
NET_ATTR_END = {"+", ";"}


def is_num(t):
    return re.fullmatch(r"-?\d+(\.\d+)?", t) is not None


class Scaler:
    def __init__(self, f):
        self.f = f
        self.inexact = 0

    def __call__(self, t):
        v = Fraction(t) * self.f
        if v.denominator != 1:
            self.inexact += 1
            return str(round(v))
        return str(v.numerator)


def statements(text):
    """Yield token lists, one per DEF statement (ending in ';')."""
    cur = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if not cur and s.startswith("END "):
            # "END COMPONENTS", "END DESIGN": no ';'
            yield s.split()
            continue
        for t in TOK.findall(s):
            cur.append(t)
            if t == ";":
                yield cur
                cur = []
    if cur:
        yield cur


def scale_stmt(toks, section, sc):
    out = list(toks)
    n = len(out)
    head = out[0]
    i = 0
    paren = False
    # positional values of top-level statements
    if head == "ROW" and n > 5:
        out[3], out[4] = sc(out[3]), sc(out[4])
    if head in ("TRACKS", "GCELLGRID"):
        for k in range(n - 1):
            if out[k] in ("X", "Y") and is_num(out[k + 1]):
                out[k + 1] = sc(out[k + 1])
                break
    step_n = 1 if head in ("TRACKS", "GCELLGRID") else 2
    while i < n:
        t = out[i]
        if t == "(":
            paren = True
        elif t == ")":
            paren = False
        elif paren:
            if is_num(t):
                out[i] = sc(t)
        elif t == "STEP":
            for k in range(1, step_n + 1):
                if i + k < n and is_num(out[i + k]):
                    out[i + k] = sc(out[i + k])
            i += step_n
        elif t in KW_LEN:
            for k in range(1, KW_LEN[t] + 1):
                if i + k < n and is_num(out[i + k]):
                    out[i + k] = sc(out[i + k])
            i += KW_LEN[t]
        elif t == "HALO":
            k = i + 1
            if k < n and out[k] == "SOFT":
                k += 1
            for m in range(k, min(k + 4, n)):
                if is_num(out[m]):
                    out[m] = sc(out[m])
            i = k + 3
        elif t == "SPACING" and i + 1 < n and is_num(out[i + 1]):
            out[i + 1] = sc(out[i + 1])
            i += 1
        elif t == "WIDTH" and i + 1 < n:
            # NDR "WIDTH w" or special net "+ WIDTH layer w"
            if is_num(out[i + 1]):
                out[i + 1] = sc(out[i + 1])
                i += 1
            elif i + 2 < n and is_num(out[i + 2]):
                out[i + 2] = sc(out[i + 2])
                i += 2
        elif section == "SPECIALNETS" and t in WIRE_KW | {"SHIELD"} and i + 2 < n:
            # "+ ROUTED layer width", "NEW layer width", "+ SHIELD net layer width"
            k = i + (3 if t == "SHIELD" else 2)
            if k < n and is_num(out[k]):
                out[k] = sc(out[k])
                i = k
        i += 1
    return out


def strip_routing(toks):
    """Regular net: drop '+ ROUTED|FIXED|COVER|NOSHIELD ...' up to the next '+' or ';'."""
    out = []
    i = 0
    n = len(toks)
    while i < n:
        if toks[i] == "+" and i + 1 < n and toks[i + 1] in ("ROUTED", "FIXED", "COVER", "NOSHIELD"):
            i += 2
            while i < n and toks[i] not in NET_ATTR_END:
                i += 1
            continue
        out.append(toks[i])
        i += 1
    return out


def fmt(toks):
    s = " ".join(toks)
    # one wire segment / attribute per line keeps big nets readable
    s = s.replace(" NEW ", "\n    NEW ").replace(" + ", "\n  + ")
    return s


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--scale", required=True, help="e.g. 4 or 1/4")
    ap.add_argument("--strip-routing", action="store_true")
    ap.add_argument("--keep-row-sites", default="")
    ap.add_argument("--drop-gcellgrid", action="store_true")
    a = ap.parse_args()
    sc = Scaler(Fraction(a.scale))
    keep_sites = set(filter(None, a.keep_row_sites.split(",")))
    text = open(a.inp).read()
    section = None
    dropped_rows = 0
    lines = []
    for toks in statements(text):
        head = toks[0]
        if head == "END":
            section = None
            lines.append(" ".join(toks))
            continue
        if head in ("VIAS", "COMPONENTS", "PINS", "SPECIALNETS", "NETS", "BLOCKAGES",
                    "REGIONS", "NONDEFAULTRULES", "GROUPS", "FILLS", "PINPROPERTIES",
                    "PROPERTYDEFINITIONS", "SCANCHAINS", "STYLES") and section is None:
            section = head
            lines.append(" ".join(toks))
            continue
        if head == "ROW" and keep_sites and toks[2] not in keep_sites:
            dropped_rows += 1
            continue
        if head == "GCELLGRID" and a.drop_gcellgrid:
            continue
        if section == "PROPERTYDEFINITIONS" or head in ("VERSION", "DIVIDERCHAR", "BUSBITCHARS",
                                                         "DESIGN", "UNITS", "HISTORY", "TECHNOLOGY"):
            lines.append(" ".join(toks))
            continue
        if section == "NETS" and a.strip_routing:
            toks = strip_routing(toks)
        lines.append(fmt(scale_stmt(toks, section, sc)))
    text_out = "\n".join(lines) + "\n"
    open(a.out, "w").write(text_out)
    print(f"{a.inp} -> {a.out}: scale {a.scale}, inexact values {sc.inexact}, rows dropped {dropped_rows}")
    if sc.inexact:
        print("WARNING: some values were not on the target DBU grid and were rounded", file=sys.stderr)


if __name__ == "__main__":
    main()
