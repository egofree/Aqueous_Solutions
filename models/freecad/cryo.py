#!/usr/bin/env python3
"""CRYO internals — cold box + receivers + child envelopes on each process basement.

Authority: AQS-CRY-002 / AQS-EQP-CRY-001. Parent COLD_BOX + receivers locked;
internal stubs + VJ_001…005 line envelopes (AQS-ASM-001 §6) are
keep-out only (not detailed solids / not fabricator isometrics).
NOTE: plant.FCStd rebuild REQUIRED before new children appear in assembled plant.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate
import FreeCAD as App

OUT = Path(__file__).resolve().parent


def _children(doc, x, y, z, suffix):
    """Internal envelope stubs inside / adjacent to COLD_BOX keep-out.

    Layout is schematic millimetre boxes for clash / keep-out only.
    Duties TBD — do not read dimensions as issued nameplates.
    """
    # Intake train along -Y face of cold box
    add(doc, "AIR_INTAKE%s" % suffix,
        box_at(x + 100, y - 900, z, 800, 700, 1400))
    label_plate(doc, "AIR_INTAKE%s" % suffix, x + 100, y - 1100, z=z + 1200)
    add(doc, "MOL_SIEVE%s" % suffix,
        box_at(x + 1000, y - 900, z, 800, 700, 1400))
    label_plate(doc, "MOL_SIEVE%s" % suffix, x + 1000, y - 1100, z=z + 1200)
    add(doc, "HEPA_BANK%s" % suffix,
        box_at(x + 1900, y - 900, z, 700, 700, 1400))
    label_plate(doc, "HEPA_BANK%s" % suffix, x + 1900, y - 1100, z=z + 1200)

    # Inside cold-box footprint
    add(doc, "STIRLING_COLD_HEAD%s" % suffix,
        box_at(x + 250, y + 300, z + 200, 700, 800, 1200))
    label_plate(doc, "STIRLING_COLD_HEAD%s" % suffix, x + 250, y + 80, z=z + 1400)
    add(doc, "DIST_COL_PRI%s" % suffix,
        box_at(x + 1100, y + 300, z + 200, 500, 500, 2200))
    label_plate(doc, "DIST_COL_PRI%s" % suffix, x + 1100, y + 80, z=z + 2000)
    add(doc, "DIST_COL_SEC%s" % suffix,
        box_at(x + 1700, y + 300, z + 200, 400, 400, 1800))
    label_plate(doc, "DIST_COL_SEC%s" % suffix, x + 1700, y + 80, z=z + 1800)
    add(doc, "DIST_COL_TER%s" % suffix,
        box_at(x + 2200, y + 300, z + 200, 400, 400, 1600))
    label_plate(doc, "DIST_COL_TER%s" % suffix, x + 2200, y + 80, z=z + 1600)
    add(doc, "REBOILER_COND%s" % suffix,
        box_at(x + 250, y + 1300, z + 200, 900, 600, 1000))
    label_plate(doc, "REBOILER_COND%s" % suffix, x + 250, y + 1100, z=z + 1200)
    add(doc, "COMP_EXPAND%s" % suffix,
        box_at(x + 1300, y + 1300, z + 200, 1000, 700, 1100))
    label_plate(doc, "COMP_EXPAND%s" % suffix, x + 1300, y + 1100, z=z + 1200)

    # Utility HX / cooling / room AHU along +X of cold box (before receivers)
    ux = x + 2800
    add(doc, "CRYO_HX_Q4%s" % suffix,
        box_at(ux, y + 200, z, 700, 600, 1100))
    label_plate(doc, "CRYO_HX_Q4%s" % suffix, ux, y + 20, z=z + 1000)
    add(doc, "CRYO_DED_COOL%s" % suffix,
        box_at(ux, y + 1000, z, 700, 600, 1100))
    label_plate(doc, "CRYO_DED_COOL%s" % suffix, ux, y + 820, z=z + 1000)
    add(doc, "CRYO_AHU%s" % suffix,
        box_at(ux, y + 1800, z, 700, 700, 1200))
    label_plate(doc, "CRYO_AHU%s" % suffix, ux, y + 1620, z=z + 1100)
    add(doc, "CRYO_AHU_COND%s" % suffix,
        box_at(ux + 800, y + 1800, z, 600, 700, 1000))
    label_plate(doc, "CRYO_AHU_COND%s" % suffix, ux + 800, y + 1620, z=z + 900)
    add(doc, "FLUE_CAP%s" % suffix,
        box_at(ux + 800, y + 1000, z, 600, 700, 1100))
    label_plate(doc, "FLUE_CAP%s" % suffix, ux + 800, y + 820, z=z + 1000)


def _vj_envelopes(doc, bx, by, z, rx, suffix):
    """Vacuum-jacketed line keep-outs COLD_BOX → receivers / yard rough-in.

    Tags match AQS-ASM-001 §6 ISO stubs VJ-001…005 (hyphen → underscore).
    Cross-section is schematic (~200×200 mm corridor) — not issued OD.
    """
    x0 = bx + 2000
    L = max(400, rx - x0)
    # VJ-001 LOX/GOX → CRYO_O2 (receiver index 1)
    add(doc, "VJ_001%s" % suffix,
        box_at(x0, by + 200 + 1 * 700 + 200, z + 900, L, 200, 200))
    label_plate(doc, "VJ_001%s" % suffix, x0, by + 80 + 1 * 700, z=z + 1200)
    # VJ-002 LIN/GN2 → CRYO_N2 (index 2)
    add(doc, "VJ_002%s" % suffix,
        box_at(x0, by + 200 + 2 * 700 + 200, z + 900, L, 200, 200))
    label_plate(doc, "VJ_002%s" % suffix, x0, by + 80 + 2 * 700, z=z + 1200)
    # VJ-003 LCO2/GCO2 → CRYO_CO2 (index 3)
    add(doc, "VJ_003%s" % suffix,
        box_at(x0, by + 200 + 3 * 700 + 200, z + 900, L, 200, 200))
    label_plate(doc, "VJ_003%s" % suffix, x0, by + 80 + 3 * 700, z=z + 1200)
    # VJ-004 LH2/GH2 → CRYO_H2 (index 0) — MAQ sensitive
    add(doc, "VJ_004%s" % suffix,
        box_at(x0, by + 200 + 0 * 700 + 200, z + 1100, L, 200, 200))
    label_plate(doc, "VJ_004%s" % suffix, x0, by + 80, z=z + 1400)
    # VJ-005 CRYO_H2 → yard UTIL_ROUGH_H2 — east stub past receivers
    add(doc, "VJ_005%s" % suffix,
        box_at(rx + 1400, by + 200, z + 1100, 1200, 200, 200))
    label_plate(doc, "VJ_005%s" % suffix, rx + 1400, by + 40, z=z + 1400)


def attach(doc):
    x, y = P.CRYO_X, P.CRYO_Y
    # One cold-box set per discrete basement level (always underground)
    for b in range(P.BASEMENT_LEVELS):
        z = P.basement_z(b)
        suffix = "" if b == 0 else "_B%d" % (b + 1)
        add(doc, "COLD_BOX%s" % suffix,
            box_at(x + 200, y + 200, z, 2000, 2600, 2600))
        label_plate(doc, "COLD_BOX%s" % suffix, x + 200, y + 40, z=z + 1600)
        _children(doc, x + 200, y + 200, z, suffix)
        # Receivers east of utility stubs
        px = x + 5000  # east of utility + AHU_COND (9 m CRYO envelope)
        for i, name in enumerate(("CRYO_H2", "CRYO_O2", "CRYO_N2", "CRYO_CO2")):
            tag = name if b == 0 else "%s_B%d" % (name, b + 1)
            add(doc, tag, box_at(px, y + 200 + i * 700, z, 1400, 600, 1800))
            label_plate(doc, tag, px, y + 80 + i * 700, z=z + 1600)
        _vj_envelopes(doc, x + 200, y + 200, z, px, suffix)
        # Dedicated CRYO egress (NFPA 2/55 / AQS-EGR-001) — rated door +
        # lobby stub to STAIR_SERVICE path; not sole reliance on process aisle.
        eg_x = x + 200
        eg_y = y - 200
        add(doc, "CRYO_EGRESS_DOOR%s" % suffix,
            box_at(eg_x, eg_y, z, 1200, 200, 2200))
        label_plate(doc, "CRYO_EGRESS_DOOR%s" % suffix,
                    eg_x, eg_y - 400, z=z + 1000)
        add(doc, "CRYO_EGRESS_LOBBY%s" % suffix,
            box_at(eg_x, eg_y - 1800, z, 2400, 1600, 2800))
        label_plate(doc, "CRYO_EGRESS_LOBBY%s" % suffix,
                    eg_x, eg_y - 2200, z=z + 1400)


def build():
    plant = OUT / "plant.FCStd"
    doc = App.openDocument(str(plant)) if plant.exists() else App.newDocument("CRYO")
    attach(doc)
    doc.recompute()
    doc.saveAs(str(plant if plant.exists() else OUT / "cryo.FCStd"))
    print("cryo internals + VJ envelopes attached (basement_levels=%d)"
          % P.BASEMENT_LEVELS)
    print("NOTE: full plant.FCStd rebuild via build_plant.py required for assembled plant")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
