#!/usr/bin/env python3
"""FARM internals — massing inside each life-plate farm envelope."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate
import FreeCAD as App

OUT = Path(__file__).resolve().parent


def _gsize(uid, fallback=(1500, 1000, 1500)):
    """Unit envelope L x W x H from the graph params (flat size_mm or envelope.size_mm).

    CAD dims are read, never re-typed: the graph is the sizing authority
    (AQS-PAR-001), and a resize on the graph moves the GA on the next rebuild.
    """
    try:
        import json
        g = json.load(open(OUT.parents[1] / "flow_graph" / "plant_flow_graph.json"))
        n = {u["unit_id"]: u for u in g["nodes"]}[uid]
        p = n.get("params") or {}
        sz = (p.get("envelope") or {}).get("size_mm") or p.get("size_mm")
        return [float(v) for v in sz]
    except Exception as exc:
        print("  farm: %s size unreadable (%s) - fallback box" % (uid, exc))
        return list(fallback)


def _animals(doc, z, n, _lab):
    """Animal chain + feed prep + RAS UV loop (A-M-415..429; X-FARM build-out).

    Dims from the graph; positions hand-laid in the free west/south floor of the
    farm plate (the grow bed owns x >= 6100 down to y 9400, the MEOH_FERM stub
    owns the north strip). Every unit gets the story suffix via n().
    """
    x, y = P.FARM_X, P.FARM_Y

    def put(uid, ox, oy, note_ref):
        w, d, h = _gsize(uid)
        add(doc, n(uid), box_at(x + ox, y + oy, z, w, d, h))
        _lab(doc, n(uid), x + ox, y + oy - 160, z=z + min(h, 1600))
        return w, d

    # RAS loop: optional UV sanitizer between BIOFILTER (ends x+5900) and the grow
    # beds (start x+6100), normally bypassed; ozone deep-clean is a contingency
    put("AQUA_UV", 4700, 3000, "A-M-424")
    # Feed formulation row, west column south of FARM_SUMP (ends y+4800)
    put("FEED_PREP", 200, 5600, "A-M-426")
    # Animal row 1 (layer + quail; A-M-417/418)
    put("CHICKEN_COOP", 200, 6800, "A-M-417")
    put("QUAIL_CAGE", 2900, 6800, "A-M-418")
    # Animal row 2 (rabbit + hive; A-M-421/422)
    put("RABBIT_HUTCH", 200, 8300, "A-M-421")
    put("BEE_HIVE", 2300, 8300, "A-M-422")
    # Waste row: manure drops to the BSFL bin (A-M-419), vermicompost beside it
    put("BSFL_BIN", 200, 9700, "A-M-419")
    put("VERMI_BIN", 2900, 9700, "A-M-423")
    # Waterfowl south of the grow bed (ends y+9400)
    put("DUCK_PEN", 5200, 9700, "A-M-420")
    # Duckweed raceway (A-M-420): 30.1 x 10.1 m ground basin - fits only once the
    # plate is ~3x the M1 baseline; the guard keeps the GA honest at any scale
    rw = _gsize("DUCKWEED")
    if P.FARM_L >= rw[0] + 400 and P.FARM_W >= 11400 + rw[1]:
        add(doc, n("DUCKWEED"), box_at(x + 200, y + 11400, z, rw[0], rw[1], rw[2]))
        _lab(doc, n("DUCKWEED"), x + 200, y + 11240, z=z + min(rw[2], 1600))
    else:
        print("  farm: DUCKWEED raceway %gx%g mm does not fit the %gx%g mm plate "
              "- appears at the scale that fits it" % (rw[0], rw[1], P.FARM_L, P.FARM_W))


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
    _animals(doc, z, n, label_plate)


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
