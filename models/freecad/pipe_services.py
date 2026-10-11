#!/usr/bin/env python3
"""Routed pipe racks, cable tray, grounding ring.

    /usr/bin/freecadcmd pipe_services.py

Meshes from mfg_pipe_rack.stl / mfg_cable_tray.stl replace these
boxes when present (import_mfg). Headers remain separate objects.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate
import electrical_yard

import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent


def pipe(d, l, x, y, z, axis="x"):
    """Hollow header. See pipes.py. A solid cylinder is not a pipe."""
    import pipes
    return pipes.tube(d, l, x, y, z, axis=axis)


def attach(doc, include_life=True):
    t = P.WALL
    # wet spine behind EW cells (operator aisle stays −Y)
    rx = P.AISLE_X0
    ry = P.AISLE_Y + P.EW_W + 2 * t + 150
    length = 9 * P.EW_PITCH + 400
    add(doc, "RACK_WET", box_at(rx, ry, 0, length, 120, 80))
    add(doc, "HDR_LIQUOR_RACK", pipe(50, length, rx, ry + 60, 2000))
    add(doc, "HDR_ACID_GAS_RACK", pipe(P.HDR_D, length, rx, ry + 60, 2200))
    add(doc, "HDR_H2_RACK", pipe(P.HDR_D, length, rx, ry + 60, 2400))
    add(doc, "HDR_DUST_RACK", pipe(P.DUST_D, length, rx, ry + 60, 2600))
    label_plate(doc, "RACK_WET", rx, ry - 200, z=2800)

    add(doc, "RACK_BMED", box_at(t + 200, P.CSTR_W + 2 * t + 200, 0, 120, P.BMED_W + 400, 80))
    add(doc, "HDR_NAOH_RACK", pipe(40, P.BMED_W + 400, t + 260, P.CSTR_W + 2 * t + 200, 1600, axis="y"))
    add(doc, "HDR_HCL_RACK", pipe(40, P.BMED_W + 400, t + 260, P.CSTR_W + 2 * t + 200, 1750, axis="y"))
    add(doc, "HDR_CAUSTIC_RACK", pipe(32, P.BMED_W + 400, t + 260, P.CSTR_W + 2 * t + 200, 1900, axis="y"))

    ox = t + P.CSTR_L + t + P.WEIR_LIP + P.FDEW_L + P.STUB_L + 100
    oy = t + (P.CSTR_W - P.WEIR_W) / 2 - 400
    ol = P.DRYER_L + P.PYRO_L + 2000
    add(doc, "RACK_OIL", box_at(ox, oy, 0, ol, 120, 80))
    add(doc, "HDR_OIL_VAPOR_RACK", pipe(80, ol, ox, oy + 60, 1500))
    label_plate(doc, "RACK_OIL", ox, oy - 200, z=1800)

    add(doc, "TRAY_EW", box_at(rx, ry + 200, 2400, length, 300, 100))
    ex, ey, _ = electrical_yard.origin()
    add(doc, "TRAY_YARD", box_at(ex, ey - 200, 2400, P.RECT_L + 1600, 300, 100))
    label_plate(doc, "TRAY_EW", rx, ry + 520, z=2600)

    add(doc, "GND_RING", box_at(-200, P.AISLE_Y - 200, 40,
                               P.CSTR_L + 9 * P.EW_PITCH + 600, 40, 8))
    rods = (
        (-200, P.AISLE_Y - 200),
        (P.CSTR_L + 400, P.AISLE_Y - 200),
        (-200, P.CSTR_W + 400),
        (ex, ey),
    )
    for i, (gx, gy) in enumerate(rods):
        add(doc, "GND_ROD_%d" % (i + 1), box_at(gx, gy, -400, 20, 20, 2900))

    if include_life:
        _life_racks(doc)


def _life_racks(doc):
    """Campus life headers on L1. Separate objects from process gas racks."""
    x0, x1 = P.LIFE_RACK_X0, P.LIFE_RACK_X1
    y0, y1 = P.LIFE_RACK_Y0, P.LIFE_RACK_Y1
    yn, ys = P.LIFE_RACK_N_Y, P.LIFE_RACK_S_Y
    xw, xe = P.LIFE_RACK_W_X, P.LIFE_RACK_E_X
    ln = x1 - x0
    ls = x1 - x0
    lw = y1 - y0
    le = y1 - y0
    z0 = P.Z_L1

    add(doc, "RACK_LIFE_N", box_at(x0, yn, z0, ln, 120, 80))
    add(doc, "RACK_LIFE_S", box_at(x0, ys, z0, ls, 120, 80))
    add(doc, "RACK_LIFE_W", box_at(xw, y0, z0, 120, lw, 80))
    add(doc, "RACK_LIFE_E", box_at(xe, y0, z0, 120, le, 80))
    label_plate(doc, "RACK_LIFE_N", x0, yn - 200, z=z0 + 3400)
    label_plate(doc, "RACK_LIFE_E", xe + 200, y0, z=z0 + 3400)

    tiers = (
        ("HDR_GREY_N", P.LIFE_D_GREY, P.LIFE_Z_GREY),
        ("HDR_UPW_N", P.LIFE_D_UPW, P.LIFE_Z_UPW),
        ("HDR_ETCH_N", P.LIFE_D_ETCH, P.LIFE_Z_ETCH),
        ("HDR_O2_N", P.LIFE_D_GAS, P.LIFE_Z_O2),
        ("HDR_N2_N", P.LIFE_D_GAS, P.LIFE_Z_N2),
        ("HDR_CO2_N", P.LIFE_D_CO2, P.LIFE_Z_CO2),
    )
    for name, d, z_rel in tiers:
        z = z0 + z_rel
        add(doc, name, pipe(d, ln, x0, yn + 60, z, axis="x"))
        add(doc, name.replace("_N", "_S"), pipe(d, ls, x0, ys + 60, z, axis="x"))
        add(doc, name.replace("_N", "_W"), pipe(d, lw, xw + 60, y0, z, axis="y"))
        add(doc, name.replace("_N", "_E"), pipe(d, le, xe + 60, y0, z, axis="y"))


def build():
    plant = OUT / "plant.FCStd"
    if plant.exists():
        App.openDocument(str(plant))
        doc = App.ActiveDocument
    else:
        doc = App.newDocument("PIPE_SERVICES")
    attach(doc)
    doc.recompute()
    out = plant if plant.exists() else OUT / "pipe_services.FCStd"
    doc.saveAs(str(out))
    print("wrote", out)


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
