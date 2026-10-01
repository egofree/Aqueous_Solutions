#!/usr/bin/env python3
"""WAFER_FAB internals — massing; discrete tool sets per cassette + PV strip.

Solar-cell PV_* keep-out envelopes (AQS-EQP-FAB-PV-001) sit on the east
strip inside the FAB envelope so CZ/wet/tool footprints stay put.
Duties / kW TBD — boxes are clash envelopes only.
NOTE: plant.FCStd rebuild REQUIRED before PV_* appear in assembled plant.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate
import FreeCAD as App

OUT = Path(__file__).resolve().parent


def _pv_strip(doc, x, y, z, suffix):
    """East-strip PV train keep-outs (cassette 0 / primary only).

    Layout intent AQS-EQP-FAB-PV-001 §5: south or east strip inside FAB
    without relocating CZ train. Place east of FAB_TOOL (~x+8000).
    """
    px = x + 8000
    py = y + 200
    # Row 1 — wet / diffusion
    row1 = (
        ("PV_TEXTURE", 0, 0, 1400, 1800, 1800),
        ("PV_EMITTER", 0, 2000, 1400, 1800, 2000),
        ("PV_PSG_ETCH", 0, 4000, 1400, 1800, 1600),
        ("PV_ARC", 0, 6000, 1400, 1800, 1800),
    )
    # Row 2 — contact / fire / test / Q4 stub (further east)
    row2 = (
        ("PV_CONTACT", 1600, 0, 1400, 1800, 1600),
        ("PV_FIRE", 1600, 2000, 1400, 1800, 2000),
        ("PV_IV", 1600, 4000, 1400, 1600, 1600),
        ("PV_HX_Q4", 1600, 6000, 1400, 1600, 1400),
    )
    for name, dx, dy, L, W, H in row1 + row2:
        tag = name if suffix == "" else "%s%s" % (name, suffix)
        add(doc, tag, box_at(px + dx, py + dy, z, L, W, H))
        label_plate(doc, tag, px + dx, py + dy - 200, z=z + min(H, 1600))


def attach(doc):
    x, y, z = P.FAB_X, P.FAB_Y, P.FAB_Z
    for c in range(P.CASSETTE_COUNT):
        cx = x + c * P.BAY
        suffix = "" if c == 0 else "_C%d" % (c + 1)
        add(doc, "FAB_PREP%s" % suffix,
            box_at(cx + 200, y + 200, z, 2200, 2600, 2200))
        label_plate(doc, "FAB_PREP%s" % suffix, cx + 200, y + 40,
                    z=P.Z_L0 + 1600)
        add(doc, "WET_BENCH%s" % suffix,
            box_at(cx + 2600, y + 200, z, 2400, 2600, 2200))
        label_plate(doc, "WET_BENCH%s" % suffix, cx + 2600, y + 40,
                    z=P.Z_L0 + 1600)
        add(doc, "FAB_TOOL%s" % suffix,
            box_at(cx + 5200, y + 200, z, 2500, 2600, 2200))
        label_plate(doc, "FAB_TOOL%s" % suffix, cx + 5200, y + 40,
                    z=P.Z_L0 + 1600)
        add(doc, "ETCH_RETURN%s" % suffix,
            box_at(cx + 2600, y + 3200, z, 2400, 1400, 1600))
        label_plate(doc, "ETCH_RETURN%s" % suffix, cx + 2600, y + 3000,
                    z=P.Z_L0 + 1600)
        # PV_* on primary cassette only (M1 massing; same class as MET_*)
        if c == 0:
            _pv_strip(doc, cx, y, z, suffix)


def build():
    plant = OUT / "plant.FCStd"
    doc = App.openDocument(str(plant)) if plant.exists() else App.newDocument("WAFER_FAB")
    attach(doc)
    doc.recompute()
    doc.saveAs(str(plant if plant.exists() else OUT / "wafer_fab.FCStd"))
    print("wafer fab + PV_* stubs attached (cassette=%s FAB_L=%d)"
          % (P.CASSETTE_ID, P.FAB_L))


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
