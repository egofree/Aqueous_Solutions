#!/usr/bin/env python3
"""Parametric bay frame. Run: freecadcmd frame.py

One size is not the standard. Pass L, W, H, section, wall, material.
See docs-authority/FRAME_SYSTEM.md.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

import FreeCAD as App
import Part

# section mass, kg/m, square tube. Used for the load note, not the solid.
MASS = {
    (80, 5): 11.0,
    (100, 6): 17.0,
    (120, 8): 27.0,
}

BAYS = {
    "LATHE":      dict(L=1200, W=600, H=800, section=100, wall=6, material="A500"),
    "EW_1":       dict(L=1400, W=600, H=800, section=100, wall=6, material="316L"),
    "EW_SMALL":   dict(L=800,  W=600, H=800, section=80,  wall=5, material="316L"),
    "FURNACE":    dict(L=1200, W=600, H=800, section=100, wall=6, material="A500"),
    "ALIGNER":    dict(L=1200, W=600, H=800, section=80,  wall=5, material="6061"),
    "CRYO_BASE":  dict(L=600,  W=600, H=800, section=80,  wall=5, material="316L"),
}



def deflection(L, section, wall, load_kg):
    """Simply supported rail, L/240. I for a square tube, mm4. E = 200 GPa steel."""
    E = 200000.0  # N/mm2
    outer, inner = section, section - 2 * wall
    I = (outer**4 - inner**4) / 12.0
    W = load_kg * 9.81  # N, on one rail
    d = W * L**3 / (48 * E * I)
    limit = L / 240.0
    return d, limit, d <= limit

def rail(section, length, x, y, z, axis="x"):
    s = Part.makeBox(section, section, length)
    if axis == "x":
        s.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
    elif axis == "y":
        s.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
    s.translate(App.Vector(x, y, z))
    return s


def frame(L, W, H, section, wall, material):
    """Four posts, top rectangle, bottom rectangle. Wall is recorded, not cut."""
    parts = []
    for x in (0, L - section):
        for y in (0, W - section):
            parts.append(rail(section, H, x, y, 0, axis="z"))
    for z in (0, H - section):
        parts.append(rail(section, L, 0, 0, z, axis="x"))
        parts.append(rail(section, L, 0, W - section, z, axis="x"))
        parts.append(rail(section, W, 0, 0, z, axis="y"))
        parts.append(rail(section, W, L - section, 0, z, axis="y"))
    body = parts[0]
    for p in parts[1:]:
        body = body.fuse(p)
    length = 4 * H + 4 * L + 4 * W
    kg = MASS.get((section, wall), 0) * length / 1000
    return body, length, kg, material


def main():
    doc = App.newDocument("frames")
    out = Path(__file__).resolve().parent
    for name, p in BAYS.items():
        body, length, kg, mat = frame(**p)
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = body
        print(f"{name}: {p['L']}x{p['W']}x{p['H']} {mat} "
              f"tube {p['section']}x{p['wall']} length {length:.0f} mm mass {kg:.0f} kg")
    doc.recompute()
    doc.saveAs(str(out / "frames.FCStd"))
    print("wrote", out / "frames.FCStd")


if __name__ == "__main__":
    main()
