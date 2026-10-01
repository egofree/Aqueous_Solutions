#!/usr/bin/env python3
"""Insert Phase B OpenSCAD STLs as Mesh children on the plant.

    openscad via cad/detail/build_stls.sh first.
    /usr/bin/freecadcmd import_details.py   # standalone, opens plant.FCStd
    or attach(doc) from build_plant.py
"""
from pathlib import Path
import math
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
import oil_line
import electrical_yard

import FreeCAD as App

OUT = Path(__file__).resolve().parent
STL = OUT.parent / "detail" / "stl"


def _mesh(doc, name, stl_name, x, y, z, rot_axis=None, rot_deg=0):
    path = STL / stl_name
    if not path.exists():
        print("skip (no stl)", path)
        return None
    import Mesh
    mobj = doc.addObject("Mesh::Feature", name)
    mobj.Mesh = Mesh.Mesh(str(path))
    if rot_axis and rot_deg:
        mobj.Placement.Rotation = App.Rotation(App.Vector(*rot_axis), rot_deg)
    mobj.Placement.Base = App.Vector(x, y, z)
    return mobj


def attach(doc):
    t = P.WALL
    # CSTR 3 helix along the floor trough (replaces visual of paddles, does not delete them)
    _mesh(
        doc, "DETAIL_CSTR3_FLIGHT", "cstr3_flight.stl",
        t + 60, t + P.AUGER_OFFSET_Y, P.FLOOR + P.AUGER_TROUGH_H / 2,
        rot_axis=(0, 1, 0), rot_deg=90,
    )
    # CEM cassette in EW-1
    _mesh(
        doc, "DETAIL_CEM_EW1", "cem_cassette.stl",
        P.AISLE_X0 + t + 8,
        P.AISLE_Y + t + P.EW_W / 2 - P.EW_SLOT / 2,
        P.AISLE_Z + t + 20,
    )
    # harvest valve under EW-1 funnel
    _mesh(
        doc, "DETAIL_VALVE_EW1", "funnel_valve.stl",
        P.AISLE_X0 + (P.EW_L + 2 * t) / 2,
        P.AISLE_Y + (P.EW_W + 2 * t) / 2,
        P.AISLE_Z - P.EW_FUNNEL_H - P.EW_VALVE_L,
    )
    # induction coils along pyro shell
    ox, oy, _ = oil_line.origin()
    px = ox + P.DRYER_L + 80
    py = oy + P.DRYER_W / 2
    for i in range(6):
        _mesh(
            doc, "DETAIL_COIL_%d" % (i + 1), "induction_coil.stl",
            px + 200 + i * 400, py, 400,
            rot_axis=(0, 1, 0), rot_deg=90,
        )
    # BMED repeating unit on the +Y face of the stack massing
    _mesh(doc, "DETAIL_BMED_CELL", "bmed_cell.stl",
          220, P.CSTR_W + 2 * t + 520, 200)
    # ZnBr2 IEM on the stack
    ex, ey, _ = electrical_yard.origin()
    _mesh(
        doc, "DETAIL_ZNBR2_IEM", "znbr2_iem.stl",
        ex + 40, ey + P.RECT_W + 220, 400,
    )


def build():
    plant = OUT / "plant.FCStd"
    if plant.exists():
        App.openDocument(str(plant))
    else:
        import build_plant as BP
        BP.build()
    doc = App.ActiveDocument
    attach(doc)
    doc.recompute()
    doc.saveAs(str(OUT / "plant.FCStd"))
    print("wrote", OUT / "plant.FCStd", "(details attached if stl present)")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
