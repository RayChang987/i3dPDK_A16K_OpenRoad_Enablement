#!/usr/bin/env python3
"""Routed wirelength of the regular (signal and clock) nets of a DEF, in um.

One definition for every router: the sum of the centre-line lengths of the
wire segments in NETS (special nets, vias, patches and virtual connections
are not counted).

Usage: def_wirelength.py ROUTED.def [--scale 1/4]   (--scale: back to 1x)
"""
import argparse
import re
from fractions import Fraction

TOK = re.compile(r'"[^"]*"|\S+')


def wirelength(path):
    dbu = None
    total = 0
    in_nets = False
    prev = None          # last point of the current wire
    routing = False      # inside "+ ROUTED ..." (not the "( inst pin )" list)
    for line in open(path):
        s = line.strip()
        if s.startswith("UNITS DISTANCE MICRONS"):
            dbu = int(s.split()[3])
        elif re.match(r"NETS \d+", s):
            in_nets = True
            continue
        elif s.startswith("END NETS"):
            break
        if not in_nets:
            continue
        toks = TOK.findall(s)
        i = 0
        while i < len(toks):
            t = toks[i]
            if t in ("ROUTED", "FIXED", "COVER", "NOSHIELD", "NEW"):
                routing = True
                prev = None
            elif t in (";", "-", "+"):
                routing = False
                prev = None
            elif not routing:
                pass
            elif t in ("RECT", "VIRTUAL"):
                # a patch or a virtual jump: skip its parenthesised values
                j = i + 1
                while j < len(toks) and toks[j] != ")":
                    j += 1
                i = j
                if t == "VIRTUAL":
                    prev = None
            elif t == "(":
                x, y = toks[i + 1], toks[i + 2]
                j = i + 3
                while toks[j] != ")":
                    j += 1
                if prev is None:
                    cur = (int(x), int(y))
                else:
                    cur = (prev[0] if x == "*" else int(x), prev[1] if y == "*" else int(y))
                    total += abs(cur[0] - prev[0]) + abs(cur[1] - prev[1])
                prev = cur
                i = j
            i += 1
    return total / dbu


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("def_file")
    ap.add_argument("--scale", default="1")
    a = ap.parse_args()
    print(f"{wirelength(a.def_file) * float(Fraction(a.scale)):.1f}")
