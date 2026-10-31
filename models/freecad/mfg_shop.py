#!/usr/bin/env python3
"""MFG_SHOP envelope + crib / floor massing + metal-forming keep-out stubs.

Authority: AQS-EQP-MFG-001 / AQS-MFG-MET-001 / AQS-EQP-MFG-MET-001.
Metal-forming children are keep-out envelopes only (not detailed solids).
NOTE: plant.FCStd rebuild REQUIRED before MET_* children appear in assembled plant.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate
import FreeCAD as App

OUT = Path(__file__).resolve().parent


def _metal_forming(doc, x, y, z, suffix):
    """Keep-out envelopes for wire-draw / cold-mill / atomizer train.

    Schematic millimetre boxes for clash / keep-out only.
    Duties TBD — do not read dimensions as issued nameplates.
    """
    # Melt adjacent to crib (+Y of floor origin strip)
    add(doc, "MET_MELT%s" % suffix,
        box_at(x + 200, y + 2200, z, 1200, 1200, 1800))
    label_plate(doc, "MET_MELT%s" % suffix, x + 200, y + 2000, z=z + 1600)

    add(doc, "WIRE_DRAW%s" % suffix,
        box_at(x + 1600, y + 2200, z, 1600, 1000, 1600))
    label_plate(doc, "WIRE_DRAW%s" % suffix, x + 1600, y + 2000, z=z + 1400)

    add(doc, "COLD_MILL%s" % suffix,
        box_at(x + 3400, y + 2200, z, 2000, 1200, 1800))
    label_plate(doc, "COLD_MILL%s" % suffix, x + 3400, y + 2000, z=z + 1600)

    add(doc, "GAS_ATOMIZER%s" % suffix,
        box_at(x + 5600, y + 2200, z, 1400, 1400, 2000))
    label_plate(doc, "GAS_ATOMIZER%s" % suffix, x + 5600, y + 2000, z=z + 1800)

    # Product holds + utilities along +Y
    add(doc, "MET_POWDER_CRIB%s" % suffix,
        box_at(x + 5600, y + 3800, z, 1200, 800, 1400))
    label_plate(doc, "MET_POWDER_CRIB%s" % suffix, x + 5600, y + 3600, z=z + 1200)

    add(doc, "MET_AHU%s" % suffix,
        box_at(x + 7200, y + 2200, z, 1000, 800, 1600))
    label_plate(doc, "MET_AHU%s" % suffix, x + 7200, y + 2000, z=z + 1400)

    add(doc, "MET_SCRUB%s" % suffix,
        box_at(x + 8400, y + 4000, z, 900, 800, 1600))  # Rev B: north of REGEN, clear of STAIR_S2
    label_plate(doc, "MET_SCRUB%s" % suffix, x + 8400, y + 4800, z=z + 1400)

    add(doc, "MET_SCRUB_REGEN%s" % suffix,
        box_at(x + 8400, y + 3200, z, 900, 700, 1200))
    label_plate(doc, "MET_SCRUB_REGEN%s" % suffix, x + 8400, y + 3000, z=z + 1100)

    add(doc, "MET_HX_Q4%s" % suffix,
        box_at(x + 7200, y + 3200, z, 1000, 700, 1200))
    label_plate(doc, "MET_HX_Q4%s" % suffix, x + 7200, y + 3000, z=z + 1100)


def _textiles(doc, x, y, z, suffix):
    """POLY_FIBER crew textile line (A-M-429) - keep-out envelope on the MFG floor.

    FR-finished PP-fleece train: extruder + melt-blown lay + FR finish bath + winder.
    Dims from the graph params (X-SPEC); the CadQuery machine model follows at its
    unit task when a cadquery interpreter is available (see unit_freecad_map).
    """
    dx, dy, dz = _gsize("POLY_FIBER")
    add(doc, "POLY_FIBER%s" % suffix, box_at(x + 200, y + 5600, z, dx, dy, dz))
    label_plate(doc, "POLY_FIBER%s" % suffix, x + 200, y + 5400, z=z + min(dz, 1600))


def _gsize(uid, fallback=(1500, 1000, 1500)):
    """Unit envelope from the graph params (flat size_mm or envelope.size_mm)."""
    try:
        import json
        g = json.load(open(OUT.parents[1] / "flow_graph" / "plant_flow_graph.json"))
        n = {u["unit_id"]: u for u in g["nodes"]}[uid]
        p = n.get("params") or {}
        sz = (p.get("envelope") or {}).get("size_mm") or p.get("size_mm")
        return [float(v) for v in sz]
    except Exception as exc:
        print("  mfg_shop: %s size unreadable (%s) - fallback box" % (uid, exc))
        return list(fallback)


def attach(doc):
    x, y, z = P.MFG_X, P.MFG_Y, P.MFG_Z
    add(doc, "MFG_SHOP", box_at(x, y, z, P.MFG_L, P.MFG_W, P.MFG_H))
    label_plate(doc, "MFG_SHOP", x, y - 200, z=P.Z_L0 + 1600)
    # One crib + floor set per cassette along +X
    for c in range(P.CASSETTE_COUNT):
        cx = x + 200 + c * P.BAY
        suffix = "" if c == 0 else "_C%d" % (c + 1)
        add(doc, "MFG_CRIB%s" % suffix,
            box_at(cx, y + 200, z, 1800, 1600, 2000))
        label_plate(doc, "MFG_CRIB%s" % suffix, cx, y + 40, z=P.Z_L0 + 1600)
        add(doc, "MFG_FLOOR%s" % suffix,
            box_at(cx + 2000, y + 200, z, 3600, 3600, 800))
        label_plate(doc, "MFG_FLOOR%s" % suffix, cx + 2000, y + 40,
                    z=P.Z_L0 + 1600)
        # Metal-forming + textile stubs on first cassette only (M1 massing)
        if c == 0:
            _metal_forming(doc, x, y, z, suffix)
            _textiles(doc, x, y, z, suffix)


def build():
    plant = OUT / "plant.FCStd"
    doc = App.openDocument(str(plant)) if plant.exists() else App.newDocument("MFG")
    attach(doc)
    doc.recompute()
    doc.saveAs(str(plant if plant.exists() else OUT / "mfg_shop.FCStd"))
    print("mfg shop + metal-forming stubs attached (cassette=%s MFG_L=%d)"
          % (P.CASSETTE_ID, P.MFG_L))
    print("NOTE: full plant.FCStd rebuild via build_plant.py required for assembled plant")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
