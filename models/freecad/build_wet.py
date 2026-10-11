#!/usr/bin/env python3
"""Wet line assembly: load leach_cstr.FCStd, instance EW-1..9, bund, pipe, harvest, headers.

    /usr/bin/freecadcmd build_wet.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from ew_cell import make_cell

import FreeCAD as App
import Part


OUT = Path(__file__).resolve().parent


def box_at(x, y, z, dx, dy, dz):
    s = Part.makeBox(dx, dy, dz)
    s.translate(App.Vector(x, y, z))
    return s


def cyl(d, h, x, y, z, axis="z"):
    c = Part.makeCylinder(d / 2.0, h)
    if axis == "x":
        c.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
    elif axis == "y":
        c.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
    c.translate(App.Vector(x, y, z))
    return c


def add(doc, name, shape):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj


def build():
    existing = OUT / "leach_cstr.FCStd"
    if existing.exists():
        App.openDocument(str(existing))
        doc = App.ActiveDocument
    else:
        import leach_cstr as LC
        LC.build()
        doc = App.ActiveDocument
    doc.Label = "WET_LINE"

    t = P.WALL
    cell_w = P.EW_W + 2 * t
    cell_l = P.EW_L + 2 * t
    aisle_len = 9 * P.EW_PITCH

    for i, tag in enumerate(P.EW_TAGS):
        cell, cem = make_cell()
        dx = P.AISLE_X0 + i * P.EW_PITCH
        cell.translate(App.Vector(dx, P.AISLE_Y, P.AISLE_Z))
        cem.translate(App.Vector(dx, P.AISLE_Y, P.AISLE_Z))
        add(doc, tag.replace("-", "_"), cell)
        add(doc, tag.replace("-", "_") + "_CEM", cem)

    x0 = P.AISLE_X0 - P.BUND_PAD
    y0 = P.AISLE_Y - P.BUND_PAD
    bund_z = P.AISLE_Z - P.EW_FUNNEL_H - P.EW_VALVE_L - P.BUND_H
    bund = box_at(x0, y0, bund_z, aisle_len + P.BUND_PAD, cell_w + 2 * P.BUND_PAD, P.BUND_H)
    sump = box_at(
        x0 - P.SUMP_L, y0 + (cell_w + 2 * P.BUND_PAD) / 2 - P.SUMP_W / 2,
        bund_z - 80, P.SUMP_L, P.SUMP_W, P.SUMP_H,
    )
    add(doc, "EW_BUND", bund.fuse(sump))

    py = t + P.PUMP_Y
    pz = P.FLOOR + P.PUMP_Z
    run_y = py - (P.AISLE_Y + cell_w / 2)
    import pipes
    p1 = pipes.tube(P.PUMP_D, run_y, -80, P.AISLE_Y + cell_w / 2, pz, axis="y")
    p2 = pipes.tube(P.PUMP_D, P.AISLE_X0 + 80, -80, P.AISLE_Y + cell_w / 2, pz, axis="x")
    p3 = pipes.tube(P.PUMP_D, P.AISLE_Z + P.EW_H - 80 - pz, P.AISLE_X0, P.AISLE_Y + cell_w / 2, pz)
    pipes.connect(doc, "LEACHATE_TO_EW1", [p1, p2, p3])

    vdf = cyl(
        P.VDF_D, P.VDF_L,
        P.AISLE_X0 + aisle_len + 200,
        P.AISLE_Y + cell_w / 2,
        P.AISLE_Z - P.EW_FUNNEL_H,
        axis="x",
    )
    add(doc, "HARVEST_VACUUM_DRUM_FILTER", vdf)
    pails = None
    for i in range(9):
        p = box_at(
            P.AISLE_X0 + i * P.EW_PITCH + cell_l / 2 - P.PAIL_W / 2,
            P.AISLE_Y + cell_w / 2 - P.PAIL_W / 2,
            P.AISLE_Z - P.EW_FUNNEL_H - P.EW_VALVE_L - P.PAIL_W,
            P.PAIL_W, P.PAIL_W, P.PAIL_W,
        )
        pails = p if pails is None else pails.fuse(p)
    add(doc, "PAIL_STATIONS", pails)

    hdr_len = P.AISLE_X0 + aisle_len + 800
    acid = cyl(P.HDR_D, hdr_len, -200, P.AISLE_Y - 80, P.HDR_Z, axis="x")
    h2 = cyl(P.HDR_D, hdr_len, -200, P.AISLE_Y + cell_w + 80, P.HDR_Z, axis="x")
    dust = cyl(P.DUST_D, P.MEZZ_L + 400, -200, P.CSTR_W / 2,
               P.MEZZ_H + P.SHRED_H + P.HOPPER_H + 400, axis="x")
    oil = cyl(P.HDR_D, 800,
              P.WALL + P.CSTR_L + P.WALL + P.WEIR_LIP + P.FDEW_L,
              P.WALL + (P.CSTR_W - P.WEIR_W) / 2,
              P.FLOOR + P.CSTR_H + 600, axis="x")
    add(doc, "HDR_ACID_GAS", acid)
    add(doc, "HDR_H2", h2)
    add(doc, "HDR_DUST", dust)
    add(doc, "HDR_OIL_VAPOR", oil)

    doc.recompute()
    doc.saveAs(str(OUT / "wet_line.FCStd"))
    print("wrote", OUT / "wet_line.FCStd")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
