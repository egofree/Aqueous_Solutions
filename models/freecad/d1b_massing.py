#!/usr/bin/env python3
"""WP-D1b / CAD-M1 — TBD massing boxes for 18 present unmapped process units.

Part::Feature envelopes only. Feature Names = graph unit_id.
Dims = aliases of existing params stub/tote/digest/tank/BMED classes
(D1B_TBD_*). No invented PE nameplates or rates.

    /usr/bin/freecadcmd d1b_massing.py

Called from build_plant after process-cassette shift (world coords).
Licence: CERN-OHL-S-2.0. SCALE_M from params (baseline 1.0).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate
import electrical_yard

import FreeCAD as App

OUT = Path(__file__).resolve().parent

# In-scope unit_ids (plan WP-D1b). Logical BOUNDARY_EXPORT / LOAD_AGG / Q4_BUS excluded.
D1B_UNITS = (
    "MEOH_FC",
    "MEOH_FERM",
    "MEOH_SYNTH",
    "MEOH_TANK",
    "BLACK_DIGEST",
    "BMED_UPW_POLISH",
    "GREY_TREAT",
    "S13_CLASS_TREAT",
    "FAB_UPW_TANK",
    "WS_AMMONIA",
    "WS_DOPE",
    "WS_HF_ED",
    "WS_KOH",
    "WS_NITRIC",
    "WS_PEROX",
    "WS_SLURRY",
    "WS_SOLV",
    "GEO_HP_CLOSED_LOOP",
)


def _box(doc, name, x, y, z, dx, dy, dz):
    add(doc, name, box_at(x, y, z, dx, dy, dz))
    label_plate(doc, name, x, y - 200, z=z + min(dz, 1600))


def _meoh_yard(doc):
    """MEOH ESS train — L0 yard west of plate, south of FUEL_CELL strip."""
    x0, y0, z = electrical_yard.origin()
    # South of GEO pad row used in electrical_yard (ZnBr + GEO strip)
    mx = x0 - 2000
    my = y0 + P.RECT_COUNT * (P.RECT_W + 400) + P.ZNBR_W + 4500
    # Keep east face west of ENV_WALL_W
    mx = min(mx, -int(P.YARD_WALL_CLEAR) - P.D1B_TBD_SKID_L)

    _box(doc, "MEOH_FC", mx, my, z,
         P.D1B_TBD_SKID_L, P.D1B_TBD_SKID_W, P.D1B_TBD_SKID_H)
    _box(doc, "MEOH_SYNTH", mx + P.D1B_TBD_SKID_L + 200, my, z,
         P.D1B_TBD_SKID_L, P.D1B_TBD_SKID_W, P.D1B_TBD_SKID_H)
    _box(doc, "MEOH_TANK", mx + 2 * (P.D1B_TBD_SKID_L + 200), my, z,
         P.D1B_TBD_TANK_L, P.D1B_TBD_TANK_W, P.D1B_TBD_TANK_H)
    # Ferment near farm organics intent — still yard/life edge stub (TBD XY)
    _box(doc, "MEOH_FERM",
         P.FARM_X + 200, P.FARM_Y + P.FARM_W - P.D1B_TBD_DIGEST_W - 400,
         P.FARM_Z,
         P.D1B_TBD_DIGEST_L, P.D1B_TBD_DIGEST_W, P.D1B_TBD_DIGEST_H)


def _hab_water(doc):
    """GREY_TREAT / BLACK_DIGEST — life plate near HAB_WASTE (AQS-WTR-001)."""
    x, y, z = P.HAB_X, P.HAB_Y, P.HAB_Z
    # HAB_WASTE sits at x+2400, y+3200 — place treat digesters further +Y
    _box(doc, "GREY_TREAT",
         x + 200, y + 5000, z,
         P.D1B_TBD_SKID_L, P.D1B_TBD_SKID_W, P.D1B_TBD_SKID_H)
    _box(doc, "BLACK_DIGEST",
         x + 200 + P.D1B_TBD_SKID_L + 200, y + 5000, z,
         P.D1B_TBD_DIGEST_L, P.D1B_TBD_DIGEST_W, P.D1B_TBD_DIGEST_H)


def _wet_basement(doc):
    """BMED_UPW_POLISH + S13_CLASS_TREAT — world coords beside shifted BMED."""
    # wet_products BMED local origin → world after PROCESS_* + Z_Lm1 shift
    bx = 200 + P.PROCESS_DX
    by = P.CSTR_W + 2 * P.WALL + 500 + P.PROCESS_DY
    bz = P.Z_Lm1
    _box(doc, "BMED_UPW_POLISH",
         bx + P.BMED_L + 100 + 2 * P.TOTE_L + 200, by, bz,
         P.D1B_TBD_SKID_L, P.D1B_TBD_SKID_W, P.D1B_TBD_SKID_H)
    _box(doc, "S13_CLASS_TREAT",
         bx, by + P.BMED_W + 80 + P.TOTE_W + 200, bz,
         P.D1B_TBD_SKID_L, P.D1B_TBD_SKID_W, P.D1B_TBD_SKID_H)


def _fab_reagents(doc):
    """FAB_UPW_TANK + WS_* totes — L0 FAB envelope (AQS-EQP-FAB-UPW / RGN)."""
    x, y, z = P.FAB_X, P.FAB_Y, P.FAB_Z
    # West strip inside FAB (tools occupy +200..~7600 on cassette 0)
    rx = x + 200
    ry = y + P.FAB_W - P.D1B_TBD_TOTE_W - 400
    _box(doc, "FAB_UPW_TANK",
         rx, ry, z,
         P.D1B_TBD_TANK_L, P.D1B_TBD_TANK_W, P.D1B_TBD_TANK_H)
    ws = (
        "WS_AMMONIA",
        "WS_DOPE",
        "WS_HF_ED",
        "WS_KOH",
        "WS_NITRIC",
        "WS_PEROX",
        "WS_SLURRY",
        "WS_SOLV",
    )
    # Row of tote-class stubs east of UPW tank (XY TBD per FAB_WET_INTERFACE)
    wx0 = rx + P.D1B_TBD_TANK_L + 200
    for i, name in enumerate(ws):
        _box(doc, name,
             wx0 + i * P.D1B_WS_PITCH, ry, z,
             P.D1B_TBD_TOTE_L, P.D1B_TBD_TOTE_W, P.D1B_TBD_TOTE_H)


def _geo_loop(doc):
    """GEO_HP_CLOSED_LOOP — yard stub beside GEO_HP / GHEX rough-in."""
    x0, y0, z = electrical_yard.origin()
    # Match electrical_yard GEO_HP pad row
    hx = x0
    hy = y0 + P.RECT_COUNT * (P.RECT_W + 400) + 200 + P.ZNBR_W + 900
    _box(doc, "GEO_HP_CLOSED_LOOP",
         hx - 1600, hy + 1000, z,
         P.D1B_TBD_STUB_L, P.D1B_TBD_STUB_W, P.D1B_TBD_STUB_H)


def attach(doc):
    """Emit all 18 D1B massing Features (idempotent replace if re-run)."""
    for name in D1B_UNITS:
        obj = doc.getObject(name)
        if obj is not None:
            doc.removeObject(name)
    _meoh_yard(doc)
    _hab_water(doc)
    _wet_basement(doc)
    _fab_reagents(doc)
    _geo_loop(doc)
    print("d1b_massing: attached %d TBD Part::Feature units (SCALE_M=%s)"
          % (len(D1B_UNITS), P.SCALE_M))


def build():
    plant = OUT / "plant.FCStd"
    doc = App.openDocument(str(plant)) if plant.exists() else App.newDocument("D1B")
    attach(doc)
    doc.recompute()
    out = plant if plant.exists() else OUT / "d1b_massing.FCStd"
    doc.saveAs(str(out))
    print("wrote", out)


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
