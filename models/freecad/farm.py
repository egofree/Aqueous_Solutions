#!/usr/bin/env python3
"""FARM internals — massing inside each life-plate farm envelope."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate
import FreeCAD as App

OUT = Path(__file__).resolve().parent


def _story(doc, story, z, suffix):
    x, y = P.FARM_X, P.FARM_Y
    def n(base):
        return base if suffix == "" else "%s%s" % (base, suffix)
    add(doc, n("FISH_TANK"), box_at(x + 200, y + 200, z, 3500, 2500, 1800))
    label_plate(doc, n("FISH_TANK"), x + 200, y + 40, z=z + 1600)
    add(doc, n("BIOFILTER"), box_at(x + 3900, y + 200, z, 2000, 2500, 1800))
    label_plate(doc, n("BIOFILTER"), x + 3900, y + 40, z=z + 1600)
    grow_l = min(5600, max(2000, P.FARM_L - 6400))
    # Rev B (2026-10-16): bed starts north of STAIR_S2 + its L1 landing clearance (was cut by the stair; GA_CHECK).
    gy = max(y + 200, 4100 + 300) if x + 6100 + grow_l > P.PLATE_L - 2800 else y + 200
    add(doc, n("GROW_BED"), box_at(x + 6100, gy, z, grow_l, 5000, 1600))
    label_plate(doc, n("GROW_BED"), x + 6100, y + 40, z=z + 1600)
    add(doc, n("FARM_SUMP"), box_at(x + 200, y + 3000, z, 2500, 1800, 1200))
    label_plate(doc, n("FARM_SUMP"), x + 200, y + 2900, z=z + 1600)
    add(doc, n("NUTRIENT_DOSE"), box_at(x + 2900, y + 3000, z, 1600, 1400, 1400))
    label_plate(doc, n("NUTRIENT_DOSE"), x + 2900, y + 2900, z=z + 1600)
    add(doc, n("LED_CANOPY"), box_at(x + 6100, y + 200, z + 2200, grow_l, 5000, 200))
    label_plate(doc, n("LED_CANOPY"), x + 6100, y + 5400, z=z + 2600)
    # Subdivide GROW_BED into planting trays (AQS-EQP-FRM-001 massing)
    tray_n = max(1, grow_l // 1800)
    for ti in range(tray_n):
        tx = x + 6100 + ti * 1800
        tw = min(1600, grow_l - ti * 1800)
        if tw < 800:
            break
        tname = n("GROW_TRAY_%d" % (ti + 1))
        add(doc, tname, box_at(tx, y + 400, z + 200, tw, 4600, 400))
        if ti == 0:
            label_plate(doc, tname, tx, y + 40, z=z + 800)


def attach(doc):
    for i in range(P.LIFE_LEVELS):
        suffix = "" if i == 0 else "_S%d" % (i + 1)
        _story(doc, i, P.life_z(i), suffix)


def build():
    plant = OUT / "plant.FCStd"
    doc = App.openDocument(str(plant)) if plant.exists() else App.newDocument("FARM")
    attach(doc)
    doc.recompute()
    doc.saveAs(str(plant if plant.exists() else OUT / "farm.FCStd"))
    print("farm internals attached (life_levels=%d)" % P.LIFE_LEVELS)


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
