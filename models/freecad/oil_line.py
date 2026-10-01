#!/usr/bin/env python3
"""OIL LINE massing off the existing float-discharge stub."""
from pathlib import Path
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
    c.translate(App.Vector(x, y, z))
    return c


def origin():
    t = P.WALL
    x = t + P.CSTR_L + t + P.WEIR_LIP + P.FDEW_L + P.STUB_L + 100
    y = t + (P.CSTR_W - P.WEIR_W) / 2
    z = P.FLOOR + P.WEIR_CREST - 20 + P.FDEW_RISE
    return x, y, z


def attach(doc):
    x, y, z = origin()
    add(doc, "DRYER", box_at(x, y, 0, P.DRYER_L, P.DRYER_W, P.DRYER_H))
    label_plate(doc, "DRYER", x, y - 200)
    px = x + P.DRYER_L + 80
    add(doc, "INDUCTION_PYROLYZER", cyl(P.PYRO_D, P.PYRO_L, px, y + P.DRYER_W / 2, 400, axis="x"))
    label_plate(doc, "INDUCTION_PYROLYZER", px, y - 200)
    qx = px + P.PYRO_L + 80
    add(doc, "QUENCH", box_at(qx, y, 0, 800, P.DRYER_W, 1200))
    label_plate(doc, "QUENCH", qx, y - 200)
    fx = qx + 900
    add(doc, "FRACTIONATOR", cyl(P.FRAC_D, P.FRAC_H, fx + P.FRAC_D / 2, y + P.DRYER_W / 2, 0))
    label_plate(doc, "FRACTIONATOR", fx, y - 200)
    cuts = ("PROD_C5_C10", "PROD_C11_C18", "PROD_C19_C28", "PROD_C29")
    for i, name in enumerate(cuts):
        add(doc, name, box_at(fx + 400, y + i * 350, 0, 600, 300, 700))
        label_plate(doc, name, fx + 400, y + i * 350 - 80, z=900)
    ax = fx + 1200
    add(doc, "AFTERBURNER", cyl(P.AB_D, P.AB_H, ax, y + P.DRYER_W / 2, 0))
    label_plate(doc, "AFTERBURNER", ax, y - 200)
    rec_len = (fx + 400) - px
    if rec_len > 50:
        add(doc, "C29_RECYCLE", cyl(60, rec_len, px, y + 3 * 350 + 40, 740, axis="x"))
    pyro_to = (px + P.PYRO_L / 2.0, y + P.DRYER_W / 2.0, 400 + P.PYRO_D / 2.0)
    sign(doc, "SIGN_HOT_PYRO", px, y - 700, to=pyro_to)
    ab_to = (ax, y + P.DRYER_W / 2.0, P.AB_H / 2.0)
    sign(doc, "SIGN_NCG_AFTERBURNER", ax, y - 700, to=ab_to)
    # Quench / fractionator area on the oil line
    oil_to = (qx + 400, y + P.DRYER_W / 2.0, 600)
    sign(doc, "SIGN_OIL_VAPOR", qx, y - 700, to=oil_to)


def build():
    doc = App.newDocument("OIL_LINE")
    attach(doc)
    doc.recompute()
    doc.saveAs(str(OUT / "oil_line.FCStd"))
    print("wrote", OUT / "oil_line.FCStd")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
