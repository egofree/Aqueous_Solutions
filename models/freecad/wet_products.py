#!/usr/bin/env python3
"""P-Al/Mg/Ca, POLISH BANK, BMED REGEN, PROD_METALS. Attach to an open doc or build alone."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from ew_cell import make_cell
from labels import add, box_at, label_plate

import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent


def cyl(d, h, x, y, z, axis="z"):
    c = Part.makeCylinder(d / 2.0, h)
    if axis == "x":
        c.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
    c.translate(App.Vector(x, y, z))
    return c


def precip_x0():
    return P.AISLE_X0 + 9 * P.EW_PITCH + 400


def attach(doc):
    t = P.WALL
    px = precip_x0()
    py = P.AISLE_Y
    pz = P.AISLE_Z
    for i, name in enumerate(("P_Al", "P_Mg", "P_Ca")):
        tank = box_at(px + i * P.P_PITCH, py, pz, P.P_TANK_L, P.P_TANK_W, P.P_TANK_H)
        add(doc, name, tank)
        label_plate(doc, name, px + i * P.P_PITCH, py - 200)

    pk_y = P.AISLE_Y - (P.EW_W + 2 * t) - 800
    for i, tag in enumerate(P.PK_TAGS):
        dx = px + i * P.PK_PITCH
        key = tag.replace("-", "_")
        if tag in ("PK-4", "PK-5"):
            box = box_at(dx, pk_y, pz, P.EW_L, P.EW_W, P.EW_H)
            add(doc, key + "_CEM_BOX", box)
        else:
            cell, cem = make_cell()
            cell.translate(App.Vector(dx, pk_y, pz))
            cem.translate(App.Vector(dx, pk_y, pz))
            add(doc, key, cell)
            add(doc, key + "_CEM", cem)
            if tag in ("PK-6", "PK-9"):
                lid = box_at(dx, pk_y, pz + P.EW_H + P.WALL,
                             P.EW_L + 2 * P.WALL, P.EW_W + 2 * P.WALL, 20)
                add(doc, key + "_SEALED_LID", lid)
                hose = cyl(40, 500, dx + P.EW_L / 2, pk_y + P.EW_W / 2,
                           pz + P.EW_H + P.WALL + 20)
                add(doc, key + "_ACID_HOSE", hose)
        label_plate(doc, key, dx, pk_y - 200)

    bx = 200
    by = P.CSTR_W + 2 * t + 500
    add(doc, "BMED_REGEN", box_at(bx, by, 0, P.BMED_L, P.BMED_W, P.BMED_H))
    add(doc, "NaOH_PRODUCT", box_at(bx + P.BMED_L + 100, by, 0, P.TOTE_L, P.TOTE_W, P.TOTE_H))
    add(doc, "HCl_PRODUCT", box_at(bx + P.BMED_L + 100 + P.TOTE_L + 80, by, 0,
                                   P.TOTE_L, P.TOTE_W, P.TOTE_H))
    add(doc, "CRU", box_at(bx + P.BMED_L + 100, by + P.BMED_W + 80, 0,
                          P.TOTE_L, P.TOTE_W, P.TOTE_H))
    add(doc, "SALT_FEED", box_at(bx, by + P.BMED_W + 80, 0, 600, 600, 800))
    regen = cyl(P.PUMP_D, by - (P.CSTR_W + 2 * t), bx + 200, P.CSTR_W + 2 * t, 400, axis="y")
    add(doc, "REGEN_LEACH", regen)
    label_plate(doc, "BMED_REGEN", bx, by + P.BMED_W + 40)
    label_plate(doc, "NaOH_PRODUCT", bx + P.BMED_L + 100, by + P.TOTE_W + 40)
    label_plate(doc, "HCl_PRODUCT", bx + P.BMED_L + 200 + P.TOTE_L, by + P.TOTE_W + 40)
    label_plate(doc, "CRU", bx + P.BMED_L + 100, by + P.BMED_W + P.TOTE_W + 40)

    crib_x = P.AISLE_X0 + 9 * P.EW_PITCH + 1600
    crib_y = P.AISLE_Y
    add(doc, "PROD_METALS", box_at(crib_x, crib_y, 0, 1800, 800, 400))
    for i, metal in enumerate(P.EW_METALS):
        bin_ = box_at(crib_x + 40 + i * 190, crib_y + 40, 400, 170, 300, 400)
        add(doc, "PROD_" + metal, bin_)
    label_plate(doc, "PROD_METALS", crib_x, crib_y - 200)
    add(doc, "MELT", box_at(crib_x + 1800 + 100, crib_y, 0, 800, 800, 1200))
    label_plate(doc, "MELT", crib_x + 1900, crib_y - 200)


def build():
    doc = App.newDocument("WET_PRODUCTS")
    attach(doc)
    # Safety signs live in labels.wet_signs (authoritative face + leaders).
    doc.recompute()
    doc.saveAs(str(OUT / "wet_products.FCStd"))
    print("wrote", OUT / "wet_products.FCStd")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
