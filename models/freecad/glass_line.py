#!/usr/bin/env python3
"""GLASS / CERAMIC BRANCH massing off the existing grit stub."""
from pathlib import Path
import math
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate, sign

import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent


def cyl(d, h, x, y, z, axis="z"):
    c = Part.makeCylinder(d / 2.0, h)
    if axis == "x":
        c.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
    elif axis == "y":
        c.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
    c.translate(App.Vector(x, y, z))
    return c


def origin():
    t = P.WALL
    ang = math.radians(P.AUGER_INCLINE)
    lift_ex = t + P.CSTR_L - 40 + P.AUGER_LIFT_L * math.cos(ang)
    lift_ez = P.FLOOR + P.AUGER_TROUGH_H / 2 + P.AUGER_LIFT_L * math.sin(ang)
    x = lift_ex + P.SDEW_L + P.SPLIT_L + P.STUB_L + 100
    y = t + P.AUGER_OFFSET_Y - P.SPLIT_W / 2 - P.STUB_W - 20
    return x, y, lift_ez


def attach(doc):
    x, y, z = origin()
    add(doc, "RINSE_DEWATER", box_at(x, y, 0, P.RINSE_L, 600, 800))
    label_plate(doc, "RINSE_DEWATER", x, y - 200)
    # rinse liquor to SALT FEED / REGEN LEACH (not sewer)
    salt_y = P.CSTR_W + 2 * P.WALL + 500 + P.BMED_W + 80
    add(doc, "RINSE_TO_SALT", cyl(P.PUMP_D, max(200, abs(salt_y - y)), x + 100, min(y, salt_y), 200, axis="y"))
    rx = x + P.RINSE_L + 80
    add(doc, "BURNOUT_ROTARY", cyl(P.ROTARY_D, P.ROTARY_L, rx, y + 300, 400, axis="x"))
    label_plate(doc, "BURNOUT_ROTARY", rx, y - 200)
    mx = rx + P.ROTARY_L + 80
    add(doc, "MILL", box_at(mx, y, 0, P.MILL_L, 600, 900))
    label_plate(doc, "MILL", mx, y - 200)
    dx = mx + P.MILL_L + 80
    add(doc, "NaOH_DIGEST", box_at(dx, y, 0, P.DIGEST_L, P.DIGEST_W, P.DIGEST_H))
    label_plate(doc, "NaOH_DIGEST", dx, y - 200)
    px = dx + P.DIGEST_L + 80
    add(doc, "PROD_SILICATE", box_at(px, y, 0, 500, 400, 700))
    add(doc, "PROD_CA_AL_MG_HYDROXIDES", box_at(px + 550, y, 0, 500, 400, 700))
    add(doc, "PROD_CERAMIC_GRIT", box_at(px + 1100, y, 0, 500, 400, 700))
    label_plate(doc, "PROD_SILICATE", px, y - 200)
    label_plate(doc, "PROD_HYDROXIDES", px + 550, y - 200)
    label_plate(doc, "PROD_CERAMIC_GRIT", px + 1100, y - 200)
    rot_to = (rx + P.ROTARY_L / 2.0, y + 300, 400 + P.ROTARY_D / 2.0)
    sign(doc, "SIGN_HOT_ROTARY", rx, y - 700, to=rot_to)
    dig_to = (dx + P.DIGEST_L / 2.0, y + P.DIGEST_W / 2.0, P.DIGEST_H / 2.0)
    sign(doc, "SIGN_CAUSTIC_DIGEST", dx, y - 700, to=dig_to)


def build():
    doc = App.newDocument("GLASS_LINE")
    attach(doc)
    doc.recompute()
    doc.saveAs(str(OUT / "glass_line.FCStd"))
    print("wrote", OUT / "glass_line.FCStd")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
