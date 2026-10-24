#!/usr/bin/env python3
"""Nozzle stubs on campus units. STL swap is import_mfg."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add
from pipe_services import pipe
import FreeCAD as App

OUT = Path(__file__).resolve().parent


def attach(doc):
    fx, fy, fz = P.FARM_X, P.FARM_Y, P.FARM_Z
    add(doc, "FISH_TANK_F1", pipe(80, 140, fx + 200 + 3500, fy + 200 + 1250, fz + 1550))
    add(doc, "FISH_TANK_F2", pipe(50, 140, fx + 200 + 3500, fy + 200 + 850, fz + 320))
    add(doc, "FISH_TANK_F3", pipe(25, 140, fx + 200 - 140, fy + 200 + 1250, fz + 1400))
    add(doc, "BIOFILTER_B1", pipe(80, 140, fx + 3900 - 140, fy + 200 + 1250, fz + 1400))
    add(doc, "BIOFILTER_B2", pipe(80, 140, fx + 3900 + 2000, fy + 200 + 1250, fz + 1400))
    add(doc, "GROW_BED_G3", pipe(25, 140, fx + 6100 + 2800, fy + 200 - 140, fz + 500, axis="y"))
    add(doc, "FARM_SUMP_S2", pipe(50, 140, fx + 200 + 2500, fy + 3000 + 900, fz + P.LIFE_Z_GREY))
    add(doc, "NUTRIENT_DOSE_D2", pipe(20, 120, fx + 2900 + 1600, fy + 3000 + 700, fz + 400))

    bx, by, bz = P.FAB_X, P.FAB_Y, P.FAB_Z
    add(doc, "WET_BENCH_W1", pipe(25, 130, bx + 2600 - 130, by + 200 + 400, bz + 900))
    add(doc, "WET_BENCH_W5", pipe(25, 130, bx + 2600 + 2400, by + 200 + 1300, bz + 200))
    add(doc, "ETCH_RETURN_E2", pipe(25, 130, bx + 2600 + 2400, by + 3200 + 700, bz + 200))

    hx, hy, hz = P.HAB_X, P.HAB_Y, P.HAB_Z
    add(doc, "HAB_WATER_A1", pipe(25, 120, hx + 200 - 120, hy + 3200 + 800, hz + 1200))
    add(doc, "HAB_WATER_A2", pipe(40, 120, hx + 200 + 2000, hy + 3200 + 800, hz + P.LIFE_Z_GREY))
    add(doc, "HAB_WASTE_J1", pipe(40, 120, hx + 2400 + 2000, hy + 3200 + 800, hz + 200))

    cx, cy, cz = P.CRYO_X, P.CRYO_Y, P.CRYO_Z
    add(doc, "COLD_BOX_C1", pipe(25, 140, cx + 200 - 140, cy + 200 + 400, cz + 1800))
    add(doc, "COLD_BOX_C3", pipe(25, 140, cx + 200 + 2000, cy + 200 + 400, cz + 1600))
    add(doc, "COLD_BOX_C4", pipe(25, 140, cx + 200 + 2000, cy + 200 + 900, cz + 1600))
    add(doc, "COLD_BOX_C5", pipe(40, 140, cx + 200 + 2000, cy + 200 + 1400, cz + 1600))


def build():
    plant = OUT / "plant.FCStd"
    doc = App.openDocument(str(plant)) if plant.exists() else App.newDocument("CAMPUS_SHOP")
    attach(doc)
    doc.recompute()
    doc.saveAs(str(plant if plant.exists() else OUT / "campus_shop.FCStd"))
    print("campus shop nozzles attached")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
