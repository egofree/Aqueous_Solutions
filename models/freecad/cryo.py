#!/usr/bin/env python3
"""CRYO internals — cold box + receivers + child envelopes on each process basement.

Authority: AQS-CRY-002 / AQS-EQP-CRY-001. Parent COLD_BOX + receivers locked;
internal stubs + VJ_001…005 line envelopes (AQS-ASM-001 §6) are
keep-out only (not detailed solids / not fabricator isometrics).
P4 restored units (2026-10-19): H2O_ELYZ PEM skid + FB_CRYO_ELYZ_PART H2 bay,
CRYO_ASU TSA cold box (beds from params.design) and the CRYO_VENT_STACK
RELIEF_CRYO discharge — all dims from the graph / drivers.json (A-M-279).
NOTE: plant.FCStd rebuild REQUIRED before new children appear in assembled plant.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import json
import re
import params as P
from labels import add, box_at, label_plate
import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent

# Graph-driven dims for the restored units (AQS-BLD-010 rev E pattern, A-M-279): the PEM
# electrolyser skid and the CRYO_ASU TSA cold box take every dimension from the graph /
# drivers.json - never hand numbers. Missing keys fail loudly, they do not fall back.
_ROOT = OUT.parents[1]


def _graph_nodes():
    g = json.load(open(_ROOT / "flow_graph" / "plant_flow_graph.json"))
    return {n["unit_id"]: n for n in g["nodes"]}, g


def _drivers():
    return json.load(open(_ROOT / "flow_graph" / "param" / "drivers.json"))


def _edge_rate(g, sid):
    for e in g["edges"]:
        if e["stream_id"] == sid:
            return float(e["rate"]["value"] or 0)
    raise SystemExit("cryo.py: graph edge %s missing (H2O_ELYZ / CRYO_ASU cannot size)" % sid)


def _elyz_rated_kw(g, d, note):
    """Rated stack kW from the graph: IA-ELY-H2 kg/d x pem_kWh_kg_H2 / ely_window_h
    (55 kWh/kg over the 6.0 h PV window, A-M-133). Cross-checked against the
    continuous_kw note so a drifted graph fails the build instead of the GA."""
    kw = _edge_rate(g, "IA-ELY-H2") * d["pem_kWh_kg_H2"]["value"] / d["ely_window_h"]["value"]
    m = re.search(r"rated ([\d.]+) kW", note or "")
    if m and abs(kw - float(m.group(1))) > 0.2:
        raise SystemExit("cryo.py: H2O_ELYZ rated kW %.2f disagrees with graph note '%s'"
                         % (kw, m.group(0)))
    return kw


def _restored_units(doc, x, y, z):
    """P4 restored units (owner ruling 2026-10-18 D-O2): H2O_ELYZ PEM electrolyser skid
    and the CRYO_ASU TSA cold box as single Part::Feature compounds (internals travel
    with the unit through resolve_overlaps / regroup, the COLD_BOX pattern), plus the
    RELIEF_CRYO vent stack (RELIEF_H2 -> H2_STACK pattern). All dims derived on-graph
    (A-M-279)."""
    N, g = _graph_nodes()
    d = _drivers()
    CB = "CRYO.cold-box-asu-recovery-train.feed-and-recovery."

    # --- H2O_ELYZ (PEM stack skid + BoP deck: H2/O2 separators, deoxo, dryer per
    # params.internals) in a 1 h H2 bay east of the receivers. FR_CRYO_ASU ruling:
    # H2 side (CRYO_H2, H2O_ELYZ) against the O2 / ignition side.
    kw = _elyz_rated_kw(g, d, (N["H2O_ELYZ"].get("continuous_kw") or {}).get("note"))
    w = float(d[CB + "H2O_ELYZ.skid_W_mm"]["value"])
    h = float(d[CB + "H2O_ELYZ.skid_H_mm"]["value"])
    l_stack = kw * float(d[CB + "H2O_ELYZ.skid_m2_per_kW"]["value"]) / (w / 1000.0) * 1000
    l_bop = kw * float(d[CB + "H2O_ELYZ.bop_m2_per_kW"]["value"]) / (w / 1000.0) * 1000
    wall_x = x + 6750               # bolts onto FB_CRYO_H2_PART (receiver-bay wall px-450)
    bay_y0, bay_y1 = y + 1200, y + 5400   # partition wall to the bay end wall
    add(doc, "FB_CRYO_ELYZ_PART",
        box_at(wall_x, bay_y0, z, 150, bay_y1 - bay_y0, P.CRYO_H))
    ex, ey = wall_x + 150, bay_y0 + 150
    elyz = Part.makeCompound([
        box_at(ex, ey, z, w, l_stack, h),                      # stack enclosure
        box_at(ex, ey + l_stack + 100, z, w, l_bop, h)])       # BoP deck (internals)
    add(doc, "H2O_ELYZ", elyz)
    label_plate(doc, "H2O_ELYZ", ex, ey + l_stack + l_bop + 150, z=z + h - 600)
    print("  H2O_ELYZ skid: rated %.1f kW -> stack %.0f x %.0f x %.0f mm + BoP %.0f x %.0f x %.0f mm, one compound (A-M-279)"
          % (kw, l_stack, w, h, l_bop, w, h))

    # --- CRYO_ASU TSA cold box (AQS-DUTY-069 Rev C: no cryogenic column): enclosure
    # box with the 3 x 13X beds from params.design (beds, bed_D_mm, bed_L_mm) as
    # internal cylinders of the one Feature.
    de = (N["CRYO_ASU"]["params"].get("design") or {})
    beds = int(de["beds"]); bd = float(de["bed_D_mm"]); bl = float(de["bed_L_mm"])
    pitch = bd + 300                       # bed-to-bed access
    box_l = beds * pitch + 300             # 150 mm end walls each side
    box_w = bd + 600                       # 300 mm access north / south
    box_h = bl + 500                       # 350 mm skid + 150 mm headroom; kept below the
    # 1800 mm receiver height so regroup cannot park a CRYO_* receiver inside the box
    # as a bbox "internal" - the enclosure is a bed container, not a receiver swallow.
    ax, ay = x + 4000, y + 4400            # north strip, O2 / ignition side of the room
    solids = [box_at(ax, ay, z, box_l, box_w, box_h)]
    for i in range(beds):
        bx = ax + 150 + pitch * i + (pitch - bd) / 2
        solids.append(Part.makeCylinder(bd / 2, bl, App.Vector(bx, ay + 300, z + 350)))
    add(doc, "CRYO_ASU", Part.makeCompound(solids))
    label_plate(doc, "CRYO_ASU", ax, ay + box_w + 200, z=z + box_h - 300)
    print("  CRYO_ASU cold box: %d beds D%.0f x L%.0f mm in a %.0f x %.0f x %.0f mm enclosure (params.design)"
          % (beds, bd, bl, box_l, box_w, box_h))

    # --- RELIEF_CRYO discharge stack (RELIEF_H2 -> H2_STACK pattern in gas_handling:
    # 250 mm bore stack, 8 m from the L-1 floor). Base column (18250, 11000) is the
    # clear aisle over the CRYO room north strip (FAB_TOOL sits over the duty-sheet
    # origin 18300, 9500 - docs-authority/duties/RELIEF_CRYO.md - so the S56/S86
    # relief header runs ~1.6 m to this riser; NFPA 55 contingency, not the dock).
    vsx, vsy = 18250, y + 5000
    add(doc, "CRYO_VENT_STACK", Part.makeCylinder(250 / 2.0, 8000,
        App.Vector(vsx, vsy, z)))
    label_plate(doc, "CRYO_VENT_STACK", vsx, vsy - 250, z=z + 7600)
    print("  CRYO_VENT_STACK: RELIEF_CRYO discharge per the H2_STACK pattern (NFPA 55 contingency, not the dock)")


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


def ry(y, i):
    """Receiver Y: H2 alone in the south bay; O2/N2/CO2 north of the 1 h partition (Rev E)."""
    return y + 200 if i == 0 else y + 1200 + i * 700


PART_Y = 1050  # partition south face, mm from CRYO_Y (H2 receiver ends at 800)


def _vj_envelopes(doc, bx, by, z, rx, suffix):
    """Vacuum-jacketed line keep-outs COLD_BOX → receivers / yard rough-in.

    Tags match AQS-ASM-001 §6 ISO stubs VJ-001…005 (hyphen → underscore).
    Cross-section is schematic (~200×200 mm corridor) — not issued OD.
    """
    x0 = bx + 2000
    L = max(400, rx - x0)
    # VJ-001 LOX/GOX → CRYO_O2 (receiver index 1)
    add(doc, "VJ_001%s" % suffix,
        box_at(x0, ry(by - 200, 1) + 200 + 200, z + 900, L, 200, 200))
    label_plate(doc, "VJ_001%s" % suffix, x0, by + 80 + 1 * 700, z=z + 1200)
    # VJ-002 LIN/GN2 → CRYO_N2 (index 2)
    add(doc, "VJ_002%s" % suffix,
        box_at(x0, ry(by - 200, 2) + 200 + 200, z + 900, L, 200, 200))
    label_plate(doc, "VJ_002%s" % suffix, x0, by + 80 + 2 * 700, z=z + 1200)
    # VJ-003 LCO2/GCO2 → CRYO_CO2 (index 3)
    add(doc, "VJ_003%s" % suffix,
        box_at(x0, ry(by - 200, 3) + 200 + 200, z + 900, L, 200, 200))
    label_plate(doc, "VJ_003%s" % suffix, x0, by + 80 + 3 * 700, z=z + 1200)
    # VJ-004 LH2/GH2 → CRYO_H2 (index 0) — MAQ sensitive
    add(doc, "VJ_004%s" % suffix,
        box_at(x0, ry(by - 200, 0) + 200 + 200, z + 1100, L, 200, 200))
    label_plate(doc, "VJ_004%s" % suffix, x0, by + 80, z=z + 1400)
    # VJ-005 CRYO_H2 → yard UTIL_ROUGH_H2 — east stub past receivers
    add(doc, "VJ_005%s" % suffix,
        box_at(rx + 1400, by + 200, z + 1100, 1200, 200, 200))
    label_plate(doc, "VJ_005%s" % suffix, rx + 1400, by + 40, z=z + 1400)


def attach(doc):
    x, y = P.CRYO_X, P.CRYO_Y
    # Restored-unit Features (idempotent replace on a standalone re-run)
    for name in ("FB_CRYO_ELYZ_PART", "H2O_ELYZ", "LBL_H2O_ELYZ", "CRYO_ASU",
                 "LBL_CRYO_ASU", "CRYO_VENT_STACK", "LBL_CRYO_VENT_STACK"):
        if doc.getObject(name) is not None:
            doc.removeObject(name)
    # One cold-box set per discrete basement level (always underground)
    for b in range(P.BASEMENT_LEVELS):
        z = P.basement_z(b)
        suffix = "" if b == 0 else "_B%d" % (b + 1)
        # Rev E: cold box 1,000 mm further into the (now 8.7 m) room so the intake train sits inside CRYO, not in the
        # pyrolysis aisle south of it (it had overlapped AIR_INTAKE/MOL_SIEVE with the AFTERBURNER room).
        add(doc, "COLD_BOX%s" % suffix,
            box_at(x + 200, y + 1200, z, 2000, 2600, 2600))
        label_plate(doc, "COLD_BOX%s" % suffix, x + 200, y + 1040, z=z + 1600)
        _children(doc, x + 200, y + 1200, z, suffix)
        # Receivers east of utility stubs
        px = x + 5000  # east of utility + AHU_COND (9 m CRYO envelope)
        for i, name in enumerate(("CRYO_H2", "CRYO_O2", "CRYO_N2", "CRYO_CO2")):
            tag = name if b == 0 else "%s_B%d" % (name, b + 1)
            add(doc, tag, box_at(px, ry(y, i) - 0, z, 1400, 600, 1800))
            label_plate(doc, tag, px, ry(y, i) - 120, z=z + 1600)
        # 1 h partition: H2 receiver bay (south-east) vs O2 / ignition side (Rev E, GA_CHECK CAD clash fix).
        # VJ-004 passes through a firestopped sleeve (cut 50 mm round the line keep-out).
        import Part
        pw = box_at(px - 450, y + PART_Y, z, P.CRYO_X + P.CRYO_L - (px - 450), 150, P.CRYO_H)
        rw = box_at(px - 450, y, z, 150, PART_Y + 150, P.CRYO_H)
        part = pw.fuse(rw)
        _vj_envelopes(doc, x + 200, y + 200, z, px, suffix)
        sl = box_at(px - 600, ry(y, 0) + 350, z + 1050, 450, 500, 300)
        add(doc, "FB_CRYO_H2_PART%s" % suffix, part.cut(sl))
        # Dedicated CRYO egress (NFPA 2/55 / AQS-EGR-001) — rated door +
        # lobby stub to STAIR_SERVICE path; not sole reliance on process aisle.
        # Rev E: door in the west (process party) wall into the L-1 corridor; vestibule inside the CRYO room at its NW
        # corner (was a lobby built over the pyrolysis train south of CRYO).
        eg_x = x - 100
        eg_y = y + P.CRYO_W - 1700
        add(doc, "CRYO_EGRESS_DOOR%s" % suffix,
            box_at(eg_x, eg_y, z, 200, 1200, 2200))
        label_plate(doc, "CRYO_EGRESS_DOOR%s" % suffix,
                    eg_x, eg_y - 400, z=z + 1000)
        add(doc, "CRYO_EGRESS_LOBBY%s" % suffix,
            box_at(x + 150, eg_y - 300, z, 2400, 1600, 2800))
        label_plate(doc, "CRYO_EGRESS_LOBBY%s" % suffix,
                    x + 150, eg_y - 500, z=z + 1400)

    # P4 restored units (H2O_ELYZ / CRYO_ASU / RELIEF_CRYO discharge) sit in the
    # primary (uppermost) CRYO room only - single units, not per-level sets.
    _restored_units(doc, x, y, P.basement_z(0))


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
