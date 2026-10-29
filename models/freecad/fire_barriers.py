#!/usr/bin/env python3
"""Fire-area walls and horizontal assemblies. AQS-HSE-001 / AQS-BLD-001.

    /usr/bin/freecadcmd fire_barriers.py

FB_* = vertical barriers. HA_* = horizontal assemblies between levels.

FB_HAB_CORE (3 h) vs FB_HAB_FARM (2 h) are distinct assemblies:
  - FB_HAB_FARM — HAB ↔ FARM party wall outside the CORE Y-band (2 h,
    T=200 mm massing). Locked name AQS-HSE-001.
  - FB_HAB_CORE — CORE enclosure toward HABITATION + centreline segment
    through the CORE Y-band where HAB meets CORE_PROCESS / recycle
    (3 h, T=300 mm massing). Not co-located with FB_HAB_FARM.
3 h also on HA_L1_L0, HA_L0_Lm1 (life/grade/basement family).
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate
import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent
T = 200       # default 2 h wall / slab assembly thickness mm
T_2H = 200    # FB_HAB_FARM massing
T_3H = 300    # FB_HAB_CORE massing (thicker = distinct 3 h assembly)


def _fuse(parts):
    """Boolean-fuse or compound a list of shapes into one solid."""
    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    shp = parts[0]
    for p in parts[1:]:
        try:
            shp = shp.fuse(p)
        except Exception:
            return Part.makeCompound(parts)
    return shp


def _life_hab_barriers(doc, z, suffix):
    """Per life floor: distinct FB_HAB_FARM (2 h) and FB_HAB_CORE (3 h)."""
    def n(base):
        return base if suffix == "" else "%s%s" % (base, suffix)

    h_farm = max(P.HAB_H, P.FARM_H)
    h_core = max(int(P.CLEAR_L1) - 100, 3200)  # near full life clear

    x_party = P.HAB_X + P.HAB_L
    y0 = P.HAB_Y
    y1 = P.HAB_Y + P.HAB_W
    cy0 = max(P.CORE_Y, y0)
    cy1 = min(P.CORE_Y + P.CORE_W, y1)

    # --- FB_HAB_FARM (2 h): party wall segments outside CORE Y-band -----
    farm_parts = []
    if cy1 <= y0 or cy0 >= y1:
        # CORE does not intersect life plate Y — full party wall
        farm_parts.append(box_at(
            x_party - T_2H // 2, y0, z, T_2H, P.HAB_W, h_farm))
    else:
        if cy0 > y0 + 10:
            farm_parts.append(box_at(
                x_party - T_2H // 2, y0, z, T_2H, cy0 - y0, h_farm))
        if y1 > cy1 + 10:
            farm_parts.append(box_at(
                x_party - T_2H // 2, cy1, z, T_2H, y1 - cy1, h_farm))
    shp_farm = _fuse(farm_parts)
    if shp_farm is not None:
        add(doc, n("FB_HAB_FARM"), shp_farm)
        label_plate(doc, n("FB_HAB_FARM"), x_party + 80, y0 - 200,
                    z=z + min(2800, h_farm - 200))

    # --- FB_HAB_CORE (3 h): CORE interface toward HAB + recycle ---------
    # 1) Centreline through CORE Y-band: HAB ↔ CORE_PROCESS (recycle)
    # 2) West face of CORE: HAB rooms ↔ core entry
    # 3–4) South / north CORE faces (enclosure)
    core_parts = []
    if cy1 > cy0 + 10:
        core_parts.append(box_at(
            x_party - T_3H // 2, cy0, z, T_3H, cy1 - cy0, h_core))
    core_parts.append(box_at(
        P.CORE_X - T_3H // 2, P.CORE_Y, z, T_3H, P.CORE_W, h_core))
    core_parts.append(box_at(
        P.CORE_X, P.CORE_Y - T_3H // 2, z, P.CORE_L, T_3H, h_core))
    core_parts.append(box_at(
        P.CORE_X, P.CORE_Y + P.CORE_W - T_3H // 2, z, P.CORE_L, T_3H, h_core))
    shp_core = _fuse(core_parts)
    add(doc, n("FB_HAB_CORE"), shp_core)
    label_plate(doc, n("FB_HAB_CORE"), P.CORE_X, P.CORE_Y - 400,
                z=z + min(2800, h_core - 200))


def attach(doc):
    # --- Vertical FB_* on each discrete life floor -----------------------
    for i in range(P.LIFE_LEVELS):
        suffix = "" if i == 0 else "_S%d" % (i + 1)
        _life_hab_barriers(doc, P.life_z(i), suffix)

    # FAB ↔ recycle (2 h) on L0 — north face of fab toward plate
    add(doc, "FB_FAB_CORE", box_at(
        P.FAB_X, P.FAB_Y - T // 2, P.Z_L0,
        P.FAB_L, T, P.FAB_H))
    label_plate(doc, "FB_FAB_CORE", P.FAB_X, P.FAB_Y - 400,
                z=P.Z_L0 + 2800)

    # CRYO enclosure (2 h) on L-1 — west face separates process from CRYO.
    # No process-atmosphere duct through this wall (AQS-HSE-001).
    add(doc, "FB_CRYO", box_at(
        P.CRYO_X - T, P.CRYO_Y - T, P.CRYO_Z,
        P.CRYO_L + 2 * T, T, P.CRYO_H))
    label_plate(doc, "FB_CRYO", P.CRYO_X, P.CRYO_Y - 400,
                z=P.CRYO_Z + 2800)
    # Rated party wall process ↔ CRYO (full L-1 clear height)
    add(doc, "FB_CRYO_PROCESS", box_at(
        P.CRYO_X - T // 2, P.CRYO_Y, P.Z_Lm1,
        T, P.CRYO_W, P.CLEAR_Lm1))
    label_plate(doc, "FB_CRYO_PROCESS", P.CRYO_X, P.CRYO_Y - 400,
                z=P.Z_Lm1 + 2800)

    # ZnBr2 / ESS open-air or 2 h screen at grade (south of plate)
    add(doc, "FB_ESS", box_at(
        -2000, -4000, P.Z_L0, 4000, T, 2400))
    label_plate(doc, "FB_ESS", -2000, -4200, z=P.Z_L0 + 2000)

    # --- Horizontal assemblies (full plate) -------------------------------
    # LIFE ↔ GRADE 3 h
    add(doc, "HA_L1_L0", box_at(
        0, 0, P.Z_L1 - T, P.PLATE_L, P.PLATE_W, T))
    label_plate(doc, "HA_L1_L0", 200, -600, z=P.Z_L1 + 200)

    # GRADE ↔ BASEMENT 3 h
    add(doc, "HA_L0_Lm1", box_at(
        0, 0, P.Z_L0 - T, P.PLATE_L, P.PLATE_W, T))
    label_plate(doc, "HA_L0_Lm1", 200, -800, z=P.Z_L0 + 200)

    # Between process basement plates (2 h) when depth > 1
    for i in range(1, P.BASEMENT_LEVELS):
        z = P.basement_z(i)
        name = "HA_BASEMENT_B%d" % (i + 1)
        add(doc, name, box_at(0, 0, z - T, P.PLATE_L, P.PLATE_W, T))
        label_plate(doc, name, 200, -1000 - 200 * i, z=z + 200)

    # Deepest process basement ↔ CATCH room 2 h (CATCH always deepest)
    z_deep = P.basement_z(P.BASEMENT_LEVELS - 1)
    add(doc, "HA_Lm1_Lm2", box_at(
        0, 0, z_deep - T, P.PLATE_L, P.PLATE_W, T))
    label_plate(doc, "HA_Lm1_Lm2", 200, -1000, z=z_deep + 200)

    # Life-story horizontal assemblies when LIFE_LEVELS > 1 (1 h, tank/life family)
    for i in range(1, P.LIFE_LEVELS):
        z = P.life_z(i)
        name = "HA_LIFE_S%d" % (i + 1)
        add(doc, name, box_at(0, 0, z - T, P.PLATE_L, P.PLATE_W, T))
        label_plate(doc, name, 200, -600 - 200 * i, z=z + 200)

    # _rated_rooms(doc) runs last from build_plant.py (needs every solid in place; Rev C)

    # Tank / top life 1 h (AQS-BLD-001 HA_L2_L1)
    add(doc, "HA_L2_L1", box_at(0, 0, P.Z_L2 - T, P.PLATE_L, P.PLATE_W, T))
    label_plate(doc, "HA_L2_L1", 200, -1200, z=P.Z_L2 + 200)


DBG = False


def _rated_rooms(doc):
    """FR_<unit>: 1 h rooms (AQS-SAF-007, X-SAF-02) around each unit in flow_graph/fire_rooms.json. The room is built on the unit's
    CAD solid; each wall sits mid-way to the nearest neighbouring solid on that side (max 1,000 mm, min 300 mm), so walls do not cut
    neighbours. Units with no CAD solid fall back to the placement position."""
    import json
    findings = OUT.parents[1] / "docs-authority" / "inventory" / "CAD_ROOM_FINDINGS.json"
    findings.parent.mkdir(parents=True, exist_ok=True)
    findings.write_text("")                    # one run's findings, never accreted
    f = Path(__file__).resolve().parents[2] / "flow_graph" / "fire_rooms.json"
    if not f.exists():
        return
    zl = {"L-2": P.Z_Lm2, "L-1": P.Z_Lm1, "L0": P.Z_L0, "L1": P.Z_L1, "L2": P.Z_L2}
    t = 150
    skip = ("FB_", "HA_", "SLAB", "ENV_", "GROUND", "CRYO", "LBL", "LABEL", "SIGN", "CLEAR_", "UTIL_ROUGH", "VJ_", "HDR_", "RACK_", "FR_")
    solids = [o for o in doc.Objects if hasattr(o, "Shape") and o.TypeId.startswith("Part::") and not o.Shape.isNull()
              and o.Shape.Volume > 1e6 and not o.Label.startswith(skip) and o.Label not in ("CRYO",)]
    HARD = ("STAIR", "ELEV", "YARD_FENCE", "ENV_WALL", "FB_", "SHAFT", "CATCH_TANK", "DOCK_APRON")
    allsol = [o for o in doc.Objects if hasattr(o, "Shape") and o.TypeId.startswith("Part::") and not o.Shape.isNull()
              and o.Shape.Volume > 1e5 and not o.Label.startswith(("FR_", "LBL", "LABEL", "SIGN", "SLAB", "GROUND", "HA_", "HDR_", "RACK_", "ENV_"))
              and o.Label not in ("CRYO",) and not o.Label.startswith("CRYO_B")]
    cr = (P.CRYO_X, P.CRYO_Y, P.CRYO_X + P.CRYO_L, P.CRYO_Y + P.CRYO_W)

    def ov(a, b):  # 3-D bbox overlap, a and b as (x0,y0,z0,x1,y1,z1)
        return all(a[i] < b[i + 3] and b[i] < a[i + 3] for i in range(3))
    rooms = json.load(open(f))["rooms"]; own = {q["unit"] for q in rooms}
    for r in rooms:
        me = [o for o in solids if o.Label == r["unit"]]
        if me:
            bb = me[0].Shape.BoundBox; x0, y0, z, L, W, H = bb.XMin, bb.YMin, bb.ZMin, bb.XLength, bb.YLength, max(bb.ZLength + 500, 3000)
        else:
            x0, y0 = r["origin_mm"][0], r["origin_mm"][1]; L, W = r["size_mm"][0] - 2000, r["size_mm"][1] - 2000
            z = zl.get(r["level"], P.Z_L0); H = max(r["size_mm"][2] + 500, 3000)
        # Rev C: units inside the CRYO 2 h enclosure use it plus the 1 h FB_CRYO_H2_PART (cryo.py); no room of their own.
        if cr[0] <= x0 + L/2 <= cr[2] and cr[1] <= y0 + W/2 <= cr[3] and z < P.Z_L0:
            continue
        # Rev C: a solid the room walls would cut joins the room (own ancillaries, clearances, the line it feeds);
        # a rated shaft, stair, fence or wall bounds the room instead. Repeat until stable.
        members = {me[0].Label} if me else set(); clip = {}; pen = []
        up = [v for v in list(zl.values()) + [getattr(P, "Z_ROOF", P.Z_L2 + 5400)] if v > z + 100]
        Hcap = (min(up) - z - P.SLAB_THK) if up else H
        H = min(H, Hcap)
        for it in range(16):
            off = {"w": 1000.0, "e": 1000.0, "s": 1000.0, "n": 1000.0}
            for o in solids:
                if o.Label in members: continue
                b = o.Shape.BoundBox
                if b.ZMax <= z or b.ZMin >= z + H: continue
                yo = b.YMin < y0 + W + 1000 and b.YMax > y0 - 1000; xo = b.XMin < x0 + L + 1000 and b.XMax > x0 - 1000
                if yo and b.XMax <= x0: off["w"] = min(off["w"], (x0 - b.XMax)/2)
                if yo and b.XMin >= x0 + L: off["e"] = min(off["e"], (b.XMin - x0 - L)/2)
                if xo and b.YMax <= y0: off["s"] = min(off["s"], (y0 - b.YMax)/2)
                if xo and b.YMin >= y0 + W: off["n"] = min(off["n"], (b.YMin - y0 - W)/2)
            off = {k: max(t + 10.0, v) for k, v in off.items()}  # Rev C: wall fits any gap >= 320 mm
            X0, Y0, X1, Y1 = x0 - off["w"], y0 - off["s"], x0 + L + off["e"], y0 + W + off["n"]
            for k, v in clip.items():
                if k == "w": X0 = max(X0, v)
                if k == "e": X1 = min(X1, v)
                if k == "s": Y0 = max(Y0, v)
                if k == "n": Y1 = min(Y1, v)
            R = (X0, Y0, z, X1, Y1, z + H); I = (X0 + t, Y0 + t, z - 1, X1 - t, Y1 - t, z + H + 1)
            grew = False
            for o in allsol:
                if o.Label in members: continue
                b = o.Shape.BoundBox; B = (b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax)
                if not ov(R, B): continue
                if o.Label.startswith(("CORR_", "LOBBY", "TOILET", "WETROOM")): continue  # circulation zones are not boundaries (equipment-in-corridor is a GA finding)
                if all(I[i] <= B[i] and B[i + 3] <= I[i + 3] for i in range(2)): continue  # already inside
                if B[0] <= R[0] and B[1] <= R[1] and B[3] >= R[3] and B[4] >= R[4]: continue  # envelope / floor zone holding the room
                fits = len(members) < 25 and max(x0 + L, B[3]) - min(x0, B[0]) <= 10000 and max(y0 + W, B[4]) - min(y0, B[1]) <= 10000
                small = fits and max(B[3] - B[0], B[4] - B[1]) <= 4000 and z - 100 <= B[2] < z + 500
                if o.Label in own: small = False  # another rated unit (e.g. the other standby source) never shares this room
                if o.Label == "CLEAR_%s" % r["unit"]: small = True  # the unit's own service clearance is inside its room
                thin = sorted([B[3] - B[0], B[4] - B[1], B[5] - B[2]])
                if thin[0] <= 300 and thin[2] >= 1000 and not o.Label.startswith(("CLEAR_", "KO_")) and not o.Label.startswith(HARD):
                    pen.append(B); continue  # line keep-out (pipe, VJ, flue): firestopped sleeve cut below, not a clash
                if B[2] >= z + 2400 and not o.Label.startswith(HARD):
                    H = min(H, B[2] - z - 10) if not small else H; continue  # canopy / overhead: wall stops beneath it
                if B[2] >= z + 500 and max(B[3] - B[0], B[4] - B[1]) <= 4000 and fits:
                    small = True  # elevated attachment of a member (exhaust stub, hood)
                if o.Label.startswith(HARD) or not small:
                    d = {"w": x0 - B[3], "e": B[0] - x0 - L, "s": y0 - B[4], "n": B[1] - y0 - W}
                    k = max(d, key=d.get)
                    clip[k] = {"w": B[3] + 10, "e": B[0] - 10, "s": B[4] + 10, "n": B[1] - 10}[k]; grew = True
                    if DBG: print("  clip", r["unit"], k, o.Label)
                else:
                    members.add(o.Label); grew = True
                    nx0, ny0 = min(x0, B[0]), min(y0, B[1]); L, W = max(x0 + L, B[3]) - nx0, max(y0 + W, B[4]) - ny0; x0, y0 = nx0, ny0
                    H = min(Hcap, max(H, B[5] - z + 300))
            if not grew: break
        if X1 - X0 <= 2 * t or Y1 - Y0 <= 2 * t:
            # boundaries on opposite sides (stair + its door, twin walls) can squeeze
            # the room inside out; that is a layout conflict to surface, not a crash
            print("  FR_%s: room bounds inverted (X %g..%g, Y %g..%g) after clips %s"
                  " - room skipped, recorded as a GA finding"
                  % (r["unit"], X0, X1, Y0, Y1, {k: round(v) for k, v in clip.items()}))
            with open(findings, "a") as fh:
                fh.write(json.dumps({"unit": r["unit"], "X": [round(X0), round(X1)],
                                     "Y": [round(Y0), round(Y1)], "clips": {k: round(v) for k, v in clip.items()}}) + "\n")
            continue
        walls = [box_at(X0, Y0, z, X1 - X0, t, H), box_at(X0, Y1 - t, z, X1 - X0, t, H),
                 box_at(X0, Y0, z, t, Y1 - Y0, H), box_at(X1 - t, Y0, z, t, Y1 - Y0, H)]
        sh = _fuse(walls)
        for B in pen:
            sh = sh.cut(box_at(B[0] - 50, B[1] - 50, B[2] - 50, B[3] - B[0] + 100, B[4] - B[1] + 100, B[5] - B[2] + 100))
        add(doc, "FR_%s" % r["unit"], sh)
        if len(members) > 1: print("  FR_%s encloses %s" % (r["unit"], ", ".join(sorted(members))))
        if DBG: print("  room", r["unit"], [round(v) for v in (X0, Y0, X1, Y1, z, H)], clip, it)


def build():
    plant = OUT / "plant.FCStd"
    doc = App.openDocument(str(plant)) if plant.exists() else App.newDocument("FB")
    attach(doc)
    _rated_rooms(doc)
    doc.recompute()
    doc.saveAs(str(plant if plant.exists() else OUT / "fire_barriers.FCStd"))
    print("fire barriers attached (life_levels=%d basement=%d)"
          % (P.LIFE_LEVELS, P.BASEMENT_LEVELS))


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
