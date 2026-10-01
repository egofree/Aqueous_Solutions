#!/usr/bin/env python3
"""HABITATION internals — massing inside each life-plate hab envelope."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate
import FreeCAD as App

OUT = Path(__file__).resolve().parent


def _story(doc, story, z, suffix):
    x, y = P.HAB_X, P.HAB_Y
    def n(base):
        return base if suffix == "" else "%s%s" % (base, suffix)
    add(doc, n("SLEEP"), box_at(x + 200, y + 200, z, 3600, 2800, 2800))
    label_plate(doc, n("SLEEP"), x + 200, y + 40, z=z + 1600)
    add(doc, n("GALLEY"), box_at(x + 4000, y + 200, z, 3800, 2000, 2800))
    label_plate(doc, n("GALLEY"), x + 4000, y + 40, z=z + 1600)
    add(doc, n("HAB_AIR"), box_at(x + 4000, y + 2400, z + 1800, 1800, 1600, 1200))
    label_plate(doc, n("HAB_AIR"), x + 4000, y + 2300, z=z + 2200)
    add(doc, n("HAB_WATER"), box_at(x + 200, y + 3200, z, 2000, 1600, 1600))
    label_plate(doc, n("HAB_WATER"), x + 200, y + 3100, z=z + 1600)
    add(doc, n("HAB_WASTE"), box_at(x + 2400, y + 3200, z, 2000, 1600, 1600))
    label_plate(doc, n("HAB_WASTE"), x + 2400, y + 3100, z=z + 1600)


def attach(doc):
    for i in range(P.LIFE_LEVELS):
        suffix = "" if i == 0 else "_S%d" % (i + 1)
        _story(doc, i, P.life_z(i), suffix)


def build():
    plant = OUT / "plant.FCStd"
    doc = App.openDocument(str(plant)) if plant.exists() else App.newDocument("HABITATION")
    attach(doc)
    doc.recompute()
    doc.saveAs(str(plant if plant.exists() else OUT / "habitation.FCStd"))
    print("habitation internals attached (life_levels=%d)" % P.LIFE_LEVELS)


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
