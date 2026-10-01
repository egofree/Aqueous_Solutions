#!/usr/bin/env python3
"""Phase F keep-out envelopes. Origins from params.py (AQS-SCALE-001).

    /usr/bin/freecadcmd campus.py

Life floors: discrete HAB||FARM between roof and L0.
Basements: wet + CRYO always underground; replicas per BASEMENT_LEVELS.
MFG / FAB stay on L0 (see mfg_shop / wafer_fab).
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate

import FreeCAD as App

OUT = Path(__file__).resolve().parent


def _life_pair(doc, story, z):
    """HAB west + FARM east on one discrete life floor (never mixed)."""
    if story == 0:
        hab_n, farm_n = "HABITATION", "FARM"
    else:
        hab_n, farm_n = "HABITATION_S%d" % (story + 1), "FARM_S%d" % (story + 1)
    add(doc, hab_n, box_at(P.HAB_X, P.HAB_Y, z, P.HAB_L, P.HAB_W, P.HAB_H))
    label_plate(doc, hab_n, P.HAB_X, P.HAB_Y - 200, z=z + 1600)
    add(doc, farm_n, box_at(P.FARM_X, P.FARM_Y, z, P.FARM_L, P.FARM_W, P.FARM_H))
    label_plate(doc, farm_n, P.FARM_X, P.FARM_Y - 200, z=z + 1600)


def _basement_process(doc):
    """CRYO + process keep-outs on each discrete basement level."""
    for i in range(P.BASEMENT_LEVELS):
        z = P.basement_z(i)
        cryo_n = "CRYO" if i == 0 else "CRYO_B%d" % (i + 1)
        add(doc, cryo_n, box_at(P.CRYO_X, P.CRYO_Y, z,
                                P.CRYO_L, P.CRYO_W, P.CRYO_H))
        label_plate(doc, cryo_n, P.CRYO_X, P.CRYO_Y - 200, z=z + 1600)
        # Extra basements: process keep-out stub (primary wet cassette is on B1)
        if i > 0:
            stub_n = "PROCESS_B%d" % (i + 1)
            add(doc, stub_n, box_at(
                P.PROCESS_DX, P.PROCESS_DY, z,
                min(12000, P.PLATE_L - P.PROCESS_DX),
                min(8000, P.PLATE_W - P.PROCESS_DY),
                min(4500, P.CLEAR_Lm1 - 500)))
            label_plate(doc, stub_n, P.PROCESS_DX, P.PROCESS_DY - 200,
                        z=z + 1600)


def attach(doc):
    for i in range(P.LIFE_LEVELS):
        _life_pair(doc, i, P.life_z(i))
    add(doc, "WAFER_FAB", box_at(P.FAB_X, P.FAB_Y, P.FAB_Z,
                                 P.FAB_L, P.FAB_W, P.FAB_H))
    label_plate(doc, "WAFER_FAB", P.FAB_X, P.FAB_Y - 200, z=P.FAB_Z + 1600)
    _basement_process(doc)


def build():
    plant = OUT / "plant.FCStd"
    if plant.exists():
        App.openDocument(str(plant))
        doc = App.ActiveDocument
    else:
        doc = App.newDocument("CAMPUS")
    attach(doc)
    doc.recompute()
    doc.saveAs(str(plant if plant.exists() else OUT / "campus.FCStd"))
    print("campus envelopes attached (cassette=%s life=%d basement=%d)"
          % (P.CASSETTE_ID, P.LIFE_LEVELS, P.BASEMENT_LEVELS))


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
