#!/usr/bin/env python3
"""Assemble PLANT: process cassette on L-1 + campus on BLD levels.

    /usr/bin/freecadcmd build_plant.py

CAD authority: AQS-BLD-001 (cad/AUTHORITY.md). Wet-line local Z=0 is
L-1 FFL; this script shifts the process cassette by (PROCESS_DX,
PROCESS_DY, Z_Lm1) into world coords (Z=0 = L0 grade). XY keeps the
wet line inside SLAB_Lm1 (same bay grid as the plate).

After solids: plant_groups nests Combo View by type/subtype
(Plant → Building/Process/Life/…) and forces Visibility=True so the
file opens with everything shown.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
import labels
import wet_products
import oil_line
import glass_line
import electrical_yard
import gas_handling
import import_mfg
import stamp_materials
import pipe_services
import campus
import farm
import wafer_fab
import habitation
import cryo
import mfg_shop
import campus_shop
import fire_barriers
import building_stack
import fitout
import transparency
import plant_groups
import d1b_massing

import FreeCAD as App

OUT = Path(__file__).resolve().parent


def shift_process_cassette(doc, dx, dy, dz):
    """Translate every Part/Mesh shape currently in the document by (dx,dy,dz)."""
    n = 0
    for obj in list(doc.Objects):
        # Mesh::Feature uses Placement
        if obj.TypeId == "Mesh::Feature":
            try:
                base = obj.Placement.Base
                obj.Placement.Base = App.Vector(
                    base.x + dx, base.y + dy, base.z + dz)
                n += 1
            except Exception as exc:
                print("skip mesh shift", obj.Name, exc)
            continue
        if not hasattr(obj, "Shape") or obj.Shape is None or obj.Shape.isNull():
            continue
        try:
            shp = obj.Shape.copy()
            shp.translate(App.Vector(dx, dy, dz))
            obj.Shape = shp
            n += 1
        except Exception as exc:
            print("skip shift", obj.Name, exc)
    print("process cassette shifted by dX=%d dY=%d dZ=%d mm (%d objects)"
          % (dx, dy, dz, n))


def build():
    wet = OUT / "wet_line.FCStd"
    leach = OUT / "leach_cstr.FCStd"
    if wet.exists():
        App.openDocument(str(wet))
    elif leach.exists():
        App.openDocument(str(leach))
    else:
        import leach_cstr as LC
        LC.build()
    doc = App.ActiveDocument
    doc.Label = "PLANT"

    # --- L-1 local authoring (process cassette) --------------------------
    labels.wet_labels(doc)
    labels.wet_signs(doc)
    wet_products.attach(doc)
    oil_line.attach(doc)
    glass_line.attach(doc)
    gas_handling.attach(doc)
    pipe_services.attach(doc, include_life=False)
    import_mfg.attach(doc)

    shift_process_cassette(doc, P.PROCESS_DX, P.PROCESS_DY, P.Z_Lm1)

    # --- World coords (BLD levels) ---------------------------------------
    campus.attach(doc)
    farm.attach(doc)
    wafer_fab.attach(doc)
    habitation.attach(doc)
    cryo.attach(doc)
    mfg_shop.attach(doc)
    campus_shop.attach(doc)
    electrical_yard.attach(doc)
    import_mfg.attach_electrical(doc)
    import_mfg.attach_campus(doc)
    pipe_services._life_racks(doc)
    building_stack.attach(doc)
    fire_barriers.attach(doc)
    fitout.attach(doc)
    d1b_massing.attach(doc)  # WP-D1b TBD massing (unit_id Features)
    stamp_materials.stamp(doc, stamp_materials.load_rows())
    transparency.apply_document(doc)

    # Combo View nesting + default-visible Part/Mesh/groups
    plant_groups.organize(doc)
    plant_groups.ensure_visible(doc)

    doc.recompute()
    path = OUT / "plant.FCStd"
    doc.saveAs(str(path))
    print("wrote", path)
    transparency.patch_fcstd(path)
    plant_groups.patch_visibility_fcstd(path)

    # Summary for freecadcmd log
    summary = plant_groups.tree_summary(doc)
    parts = sum(
        1 for o in doc.Objects
        if (o.TypeId or "").startswith("Part::")
        or (o.TypeId or "").startswith("Mesh::")
    )
    groups = sum(
        1 for o in doc.Objects if o.TypeId == "App::DocumentObjectGroup"
    )
    print("object_count total=%d part_or_mesh=%d groups=%d"
          % (len(doc.Objects), parts, groups))
    if summary:
        plant = summary.get("Plant", {})
        for mid, leaves in (
            ("Building", ("Slabs", "Cores_Shafts", "Fire_Barriers",
                          "Terraces", "Fitout")),
            ("Process", ("Wet", "Oil_Glass", "Gas", "Cryo")),
            ("Life", ("Habitation", "Farm")),
        ):
            mg = plant.get("_groups", {}).get(mid, {})
            print("  %s total=%d" % (mid, mg.get("_total", 0)))
            for leaf in leaves:
                lg = mg.get("_groups", {}).get(leaf, {})
                print("    %s=%d" % (leaf, lg.get("_total", 0)))
        for leaf in ("Electrical", "Labels_Signs", "Detail_Meshes"):
            lg = plant.get("_groups", {}).get(leaf, {})
            print("  %s=%d" % (leaf, lg.get("_total", 0)))
        print("  Plant_root_loose=%d" % plant.get("_count", 0))


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
