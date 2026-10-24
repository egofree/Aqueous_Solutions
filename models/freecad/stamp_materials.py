#!/usr/bin/env python3
"""Stamp Material / Form / Spec from tables/materials.csv onto FreeCAD objects.

STL has no materials. This is the embed path: custom properties on
Part::Feature and Mesh::Feature. Combo View → Data after a rebuild.

    /usr/bin/freecadcmd stamp_materials.py
"""
from pathlib import Path
import csv
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import FreeCAD as App

OUT = Path(__file__).resolve().parent
CSV = next((p for p in (OUT.parent / "materials.csv", OUT.parents[1] / "tables" / "materials.csv") if p.exists()), OUT.parent / "materials.csv")

PROPS = (
    ("MatName", "material"),
    ("MatForm", "form"),
    ("MatSpec", "spec"),
    ("MatMakeBuy", "make_buy"),
    ("MatQty", "qty"),
    ("MatUnit", "unit"),
)


def load_rows():
    rows = []
    with CSV.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def ensure_prop(obj, name, value):
    if not hasattr(obj, name):
        try:
            obj.addProperty("App::PropertyString", name, "Material", name)
        except Exception:
            return
    try:
        setattr(obj, name, str(value) if value is not None else "")
    except Exception:
        pass


def stamp(doc, rows):
    by_name = {}
    for r in rows:
        by_name.setdefault(r["name"], []).append(r)
    n = 0
    for obj in doc.Objects:
        key = obj.Name
        # MASSING_ prefix from import_mfg
        if key.startswith("MASSING_"):
            key = key[len("MASSING_"):]
        if key.startswith("MFG_"):
            key = key[len("MFG_"):]
        if key.startswith("LBL_") or key.startswith("SIGN_"):
            continue
        hits = by_name.get(key) or by_name.get(obj.Label.replace(" ", "_"))
        if not hits:
            continue
        # first row is the primary material for the object
        r = hits[0]
        for prop, col in PROPS:
            ensure_prop(obj, prop, r.get(col, ""))
        n += 1
    return n


def build():
    plant = OUT / "plant.FCStd"
    if not plant.exists():
        print("no plant.FCStd — run build_plant.py first")
        return
    App.openDocument(str(plant))
    doc = App.ActiveDocument
    n = stamp(doc, load_rows())
    doc.recompute()
    doc.saveAs(str(plant))
    print("stamped", n, "objects from", CSV)


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
