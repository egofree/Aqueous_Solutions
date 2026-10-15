#!/usr/bin/env python3
"""Building stack solids — AQS-BLD-001 / AQS-SCALE-001.

    /usr/bin/freecadcmd building_stack.py

World Z=0 is L0 grade FFL. Site north = +Y (AQS-SITE-001).
North dock + paired ELEV_DOCK (discrete E–W jump) + SERVICE_ENTRY /
STAIR_SERVICE to basement. Life-floor terraces on S/E/W with floor doors.
ARRAY_ROOF / PV tilt toward equator (south in NH). SHAFT_H2: no traps.
Scale: cad/SCALE_MODEL.md.
"""
from pathlib import Path
import math
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate

import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent
T_WALL = 200


def _slab(doc, name, z_ffl, thk=None):
    thk = P.SLAB_THK if thk is None else thk
    add(doc, name, box_at(0, 0, z_ffl - thk, P.PLATE_L, P.PLATE_W, thk))
    label_plate(doc, name, 200, -400, z=z_ffl + 200)


def _shaft(doc, name, x, y, z0, z1, sx=800, sy=800):
    h = z1 - z0
    if h <= 0:
        return
    add(doc, name, box_at(x, y, z0, sx, sy, h))
    label_plate(doc, name, x, y - 200, z=z0 + min(2000, h // 2))


def _core_rooms(doc):
    """CORE_LIFE (W half) + CORE_PROCESS (E half) through full stack height."""
    z0 = P.Z_Lm2
    h = (P.Z_L2 + P.ROOF_TANK_H + 2000) - z0
    cx, cy = P.CORE_X, P.CORE_Y
    half = P.CORE_L // 2
    add(doc, "CORE_LIFE", box_at(cx, cy, z0, half, P.CORE_W, h))
    label_plate(doc, "CORE_LIFE", cx, cy - 200, z=P.Z_L1 + 2000)
    add(doc, "CORE_PROCESS", box_at(cx + half, cy, z0, half, P.CORE_W, h))
    label_plate(doc, "CORE_PROCESS", cx + half, cy - 200, z=P.Z_L1 + 2000)


def _stairs_elev(doc):
    z0 = P.Z_Lm2
    z_roof = max(P.Z_L2 + 2000, getattr(P, 'Z_ROOF', 0) + 2000)   # X-BLD-05: STAIR_P and STAIR_S1 reach the reservoir levels and the roof
    add(doc, "STAIR_P", box_at(P.CORE_X + 100, P.CORE_Y + 100,
                               P.Z_L0, P.STAIR_BOX, 4800, z_roof - P.Z_L0))
    label_plate(doc, "STAIR_P", P.CORE_X + 100, P.CORE_Y - 200, z=P.Z_L1 + 500)
    add(doc, "STAIR_MAINT", box_at(P.CORE_X + 100, P.CORE_Y + 5000,
                                   z0, P.STAIR_MAINT_W, 2400, P.Z_L0 - z0 + 500))
    label_plate(doc, "STAIR_MAINT", P.CORE_X + 100, P.CORE_Y + 4900,
                z=P.Z_Lm1 + 500)
    add(doc, "STAIR_S1", box_at(200, P.PLATE_W - 2800, P.Z_L0,
                                P.STAIR_BOX, P.STAIR_BOX, max(P.Z_L2, getattr(P, 'Z_ROOF', 0)) - P.Z_L0))
    label_plate(doc, "STAIR_S1", 200, P.PLATE_W - 2800, z=P.Z_L1 + 500)
    add(doc, "STAIR_S2", box_at(P.PLATE_L - 2800, 200, P.Z_L0,
                                P.STAIR_BOX, P.STAIR_BOX, P.Z_L2 - P.Z_L0))
    label_plate(doc, "STAIR_S2", P.PLATE_L - 2600, 0, z=P.Z_L1 + 500)
    add(doc, "ELEV_SVC", box_at(P.CORE_X + P.STAIR_BOX + 200, P.CORE_Y + 100,
                                z0, 2700, 3200, z_roof - z0))
    label_plate(doc, "ELEV_SVC", P.CORE_X + 2600, P.CORE_Y - 200,
                z=P.Z_L0 + 500)
    # SERVICE_ENTRY (L0 vestibule, north face) + STAIR_SERVICE (L0–L-2).
    # Secondary egress from underground AND equipment/service access.
    # Hab sleeping egress stays on STAIR_P / STAIR_S* (no H-area routing).
    add(doc, "SERVICE_ENTRY", box_at(
        P.SERVICE_ENTRY_X, P.SERVICE_ENTRY_Y, P.Z_L0,
        P.SERVICE_ENTRY_L, P.SERVICE_ENTRY_W, P.SERVICE_ENTRY_H))
    label_plate(doc, "SERVICE_ENTRY",
                P.SERVICE_ENTRY_X, P.SERVICE_ENTRY_Y - 200, z=P.Z_L0 + 500)
    # Exterior service door on north wall
    add(doc, "SERVICE_DOOR_N", box_at(
        P.SERVICE_ENTRY_X + 400, P.PLATE_W - 100, P.Z_L0, 1800, 200, 2400))
    label_plate(doc, "SERVICE_DOOR_N",
                P.SERVICE_ENTRY_X + 400, P.PLATE_W + 200, z=P.Z_L0 + 1200)
    # STAIR_SERVICE: full height L-2 FFL to L0 + headroom; doors at L-1 / L-2
    z_svc0 = P.Z_Lm2
    h_svc = (P.Z_L0 + 500) - z_svc0
    add(doc, "STAIR_SERVICE", box_at(
        P.STAIR_SERVICE_X, P.STAIR_SERVICE_Y, z_svc0,
        P.STAIR_SERVICE_L, P.STAIR_SERVICE_W, h_svc))
    label_plate(doc, "STAIR_SERVICE",
                P.STAIR_SERVICE_X, P.STAIR_SERVICE_Y - 200, z=P.Z_Lm1 + 500)
    # Rated door / lobby stubs at basement levels (egress discharge path)
    add(doc, "STAIR_SERVICE_DOOR_Lm1", box_at(
        P.STAIR_SERVICE_X + 200, P.STAIR_SERVICE_Y - 200, P.Z_Lm1,
        1200, 200, 2200))
    label_plate(doc, "STAIR_SERVICE_DOOR_Lm1",
                P.STAIR_SERVICE_X, P.STAIR_SERVICE_Y - 400, z=P.Z_Lm1 + 500)
    add(doc, "STAIR_SERVICE_DOOR_Lm2", box_at(
        P.STAIR_SERVICE_X + 200, P.STAIR_SERVICE_Y - 200, P.Z_Lm2,
        1200, 200, 2200))
    label_plate(doc, "STAIR_SERVICE_DOOR_Lm2",
                P.STAIR_SERVICE_X, P.STAIR_SERVICE_Y - 400, z=P.Z_Lm2 + 500)


def _shafts(doc):
    z_bot = P.basement_z(P.BASEMENT_LEVELS - 1)
    z_top = P.Z_L2 + P.ROOF_TANK_H + 1500
    px = P.CORE_X + P.CORE_L // 2 + 200
    py = P.CORE_Y + 200
    _shaft(doc, "SHAFT_H2", px, py, z_bot, z_top, 800, 800)
    _shaft(doc, "SHAFT_ACID", px, py + 1000, z_bot, z_top, 800, 800)
    _shaft(doc, "SHAFT_OIL", px, py + 2000, z_bot, z_top, 800, 800)
    lx = P.CORE_X + 200
    ly = P.CORE_Y + 200
    _shaft(doc, "SHAFT_UTIL", lx, ly + 2000, P.Z_Lm2, z_top, 1200, 2400)
    _shaft(doc, "SHAFT_PENSTOCK", lx + 1600, ly + 2000, P.Z_Lm2, z_top, 800, 800)
    _shaft(doc, "SHAFT_DUST", px + 1000, py, z_bot, z_top, 800, 800)


def _tanks(doc):
    add(doc, "ROOF_TANK", box_at(
        P.ROOF_TANK_X, P.ROOF_TANK_Y, P.ROOF_TANK_Z,
        P.ROOF_TANK_L, P.ROOF_TANK_W, P.ROOF_TANK_H))
    label_plate(doc, "ROOF_TANK", P.ROOF_TANK_X, P.ROOF_TANK_Y - 200,
                z=P.ROOF_TANK_Z + 2000)
    add(doc, "CATCH_TANK", box_at(
        P.CATCH_TANK_X, P.CATCH_TANK_Y, P.CATCH_TANK_Z,
        P.CATCH_TANK_L, P.CATCH_TANK_W, P.CATCH_TANK_H))
    label_plate(doc, "CATCH_TANK", P.CATCH_TANK_X, P.CATCH_TANK_Y - 200,
                z=P.CATCH_TANK_Z + 2000)
    hydro_x = min(P.CATCH_TANK_X + P.CATCH_TANK_L, P.PLATE_L - 6000)
    add(doc, "HYDRO_SET", box_at(hydro_x, P.CATCH_TANK_Y, P.Z_Lm2,
                                 6000, 6000, 3500))
    label_plate(doc, "HYDRO_SET", hydro_x, P.CATCH_TANK_Y - 200,
                z=P.Z_Lm2 + 2000)
    # North (pole-facing) dock + paired freight elevator — AQS-SITE-001.
    # Discrete jump: DOCK_COUNT = CASSETTE_COUNT; one dock+ELEV_DOCK pair
    # at M1 baseline; add pairs along +X as plate grows E–W.
    apron_l = max(P.DOCK_L * P.DOCK_COUNT, 12000, getattr(P, 'DOCK_APRON_W', 0))
    add(doc, "DOCK_APRON_N", box_at(
        P.DOCK_X, P.PLATE_W, P.Z_L0, apron_l, P.DOCK_APRON_N, 150))
    label_plate(doc, "DOCK_APRON_N",
                P.DOCK_X + 200, P.PLATE_W + P.DOCK_APRON_N + 200,
                z=P.Z_L0 + 400)
    z_elev0 = P.Z_Lm2
    z_elev1 = P.Z_L2 + 2000
    for d in range(P.DOCK_COUNT):
        suf = "" if d == 0 else "_%d" % (d + 1)
        dx = P.DOCK_X + d * P.DOCK_L
        add(doc, "DOCK%s" % suf, box_at(
            dx, P.DOCK_Y, P.DOCK_Z, P.DOCK_L, P.DOCK_W, 200))
        label_plate(doc, "DOCK%s" % suf,
                    dx + 200, P.DOCK_Y + P.DOCK_W + 200, z=P.Z_L0 + 500)
        door_x = dx + (P.DOCK_L - P.DOCK_DOOR_W) // 2
        add(doc, "DOCK_DOOR_N%s" % suf, box_at(
            door_x, P.PLATE_W - 100, P.Z_L0, P.DOCK_DOOR_W, 200, 4200))
        label_plate(doc, "DOCK_DOOR_N%s" % suf,
                    door_x, P.PLATE_W + 200, z=P.Z_L0 + 2000)
        # Associated freight elevator — inside dock bay, south of door strip
        ex = dx + P.DOCK_L - P.ELEV_DOCK_L - 200
        ey = P.DOCK_Y + 200
        add(doc, "ELEV_DOCK%s" % suf, box_at(
            ex, ey, z_elev0, P.ELEV_DOCK_L, P.ELEV_DOCK_W, z_elev1 - z_elev0))
        label_plate(doc, "ELEV_DOCK%s" % suf, ex, ey - 200, z=P.Z_L0 + 500)
        # L0 dock-side elevator door stub
        add(doc, "ELEV_DOCK_DOOR_L0%s" % suf, box_at(
            ex + 400, ey - 200, P.Z_L0, 1600, 200, 2400))
        label_plate(doc, "ELEV_DOCK_DOOR_L0%s" % suf,
                    ex + 400, ey - 400, z=P.Z_L0 + 1200)
    print("dock pairs DOCK_COUNT=%d (cassette=%s); ELEV_DOCK paired each"
          % (P.DOCK_COUNT, P.CASSETTE_ID))


def _envelope_walls(doc):
    """Exterior wall shells L-2 top of wall to L2 — translucent in plant view."""
    t = T_WALL
    z0 = P.Z_Lm2
    h = (P.Z_L2 + 2000) - z0
    add(doc, "ENV_WALL_S", box_at(0, -t, z0, P.PLATE_L, t, h))
    add(doc, "ENV_WALL_N", box_at(0, P.PLATE_W, z0, P.PLATE_L, t, h))
    add(doc, "ENV_WALL_W", box_at(-t, 0, z0, t, P.PLATE_W, h))
    add(doc, "ENV_WALL_E", box_at(P.PLATE_L, 0, z0, t, P.PLATE_W, h))
    label_plate(doc, "ENV_WALL_S", 200, -t - 400, z=P.Z_L0 + 500)
    pad = 6000
    add(doc, "GROUND_PLANE", box_at(-pad, -pad, P.Z_L0 - 50,
                                    P.PLATE_L + 2 * pad, P.PLATE_W + 2 * pad, 50))
    label_plate(doc, "GROUND_PLANE", -pad, -pad - 400, z=P.Z_L0 + 200)


def _array_roof(doc, lat_deg=None):
    """Tilted PV canopy above tank. Air gap ≥ 800 mm. Tilt = site latitude.

    FreeCAD positive rotation about +X raises +Y. Site north = +Y, so
    tilt = +SITE_LAT_DEG faces the equator (south in NH, north in SH).
    Negative tilt would face the pole / dock — layout lock forbids that.
    """
    lat = P.SITE_LAT_DEG if lat_deg is None else float(lat_deg)
    gap = 800
    z_base = P.ROOF_TANK_Z + P.ROOF_TANK_H + gap
    panel = Part.makeBox(P.PLATE_L, P.PLATE_W, 120)
    # Equator-facing: +lat raises +Y (north edge high) → south face in NH.
    tilt = float(lat)
    panel.rotate(App.Vector(P.PLATE_L / 2, P.PLATE_W / 2, 0),
                 App.Vector(1, 0, 0), tilt)
    panel.translate(App.Vector(0, 0, z_base))
    add(doc, "ARRAY_ROOF", panel)
    label_plate(doc, "ARRAY_ROOF", 200, -600, z=z_base + 1500)
    print("ARRAY_ROOF tilt=%+.1f deg about +X (equator-facing; +Y rises)"
          % tilt)


def _life_terraces(doc):
    """Balconies on each life floor — S+E+W (NH) or N+E+W (SH).

    Starts at the top life floor and steps down/out one band per floor.
    Each floor gets a door onto its terrace (TERRACE_DOOR_*). Not
    roof-only overflow beds — those remain grade OVERFLOW_* receivers.
    """
    lat = float(P.SITE_LAT_DEG)
    thk = P.TERRACE_SLAB_THK
    w = int(P.TERRACE_WIDTH)
    dw = int(P.TERRACE_DOOR_W)
    dh = int(P.TERRACE_DOOR_H)
    rh = int(P.TERRACE_RAIL_H)
    faces = ("S", "E", "W") if lat >= 0 else ("N", "E", "W")
    n_life = max(1, int(P.LIFE_LEVELS))

    for i in range(n_life):
        z_ffl = P.life_z(i)
        z_slab = z_ffl - thk
        # Top floor (i = n_life-1) sits at plate face; lower floors step out.
        steps_from_top = (n_life - 1 - i)
        lvl = "L1" if i == 0 else "L1_S%d" % (i + 1)
        for face in faces:
            tname = "TERRACE_%s_%s" % (face, lvl)
            dname = "TERRACE_DOOR_%s_%s" % (face, lvl)
            rname = "TERRACE_RAIL_%s_%s" % (face, lvl)
            if face == "S":
                y0 = -w * (steps_from_top + 1)
                add(doc, tname, box_at(0, y0, z_slab, P.PLATE_L, w, thk))
                label_plate(doc, tname, 200, y0 - 400, z=z_ffl + 200)
                # Door centred on south wall, life → terrace
                dx = P.PLATE_L // 2 - dw // 2
                add(doc, dname, box_at(dx, -100, z_ffl, dw, 200, dh))
                label_plate(doc, dname, dx, -400, z=z_ffl + 1000)
                add(doc, rname, box_at(0, y0, z_ffl, P.PLATE_L, 80, rh))
            elif face == "N":
                y0 = P.PLATE_W + w * steps_from_top
                add(doc, tname, box_at(0, y0, z_slab, P.PLATE_L, w, thk))
                label_plate(doc, tname, 200, y0 + w - 200, z=z_ffl + 200)
                dx = P.PLATE_L // 2 - dw // 2
                add(doc, dname, box_at(dx, P.PLATE_W - 100, z_ffl, dw, 200, dh))
                label_plate(doc, dname, dx, P.PLATE_W + 200, z=z_ffl + 1000)
                add(doc, rname, box_at(0, y0 + w - 80, z_ffl, P.PLATE_L, 80, rh))
            elif face == "E":
                x0 = P.PLATE_L + w * steps_from_top
                # Match S/N terrace Y extent for wrap continuity
                y0 = -w * (steps_from_top + 1) if lat >= 0 else 0
                dy = P.PLATE_W + w * (steps_from_top + 1)
                add(doc, tname, box_at(x0, y0, z_slab, w, dy, thk))
                label_plate(doc, tname, x0 + 200, -400, z=z_ffl + 200)
                dy_door = P.PLATE_W // 2 - dw // 2
                add(doc, dname, box_at(P.PLATE_L - 100, dy_door, z_ffl, 200, dw, dh))
                label_plate(doc, dname, P.PLATE_L + 200, dy_door, z=z_ffl + 1000)
                add(doc, rname, box_at(x0 + w - 80, y0, z_ffl, 80, dy, rh))
            else:  # W
                x0 = -w * (steps_from_top + 1)
                y0 = -w * (steps_from_top + 1) if lat >= 0 else 0
                dy = P.PLATE_W + w * (steps_from_top + 1)
                add(doc, tname, box_at(x0, y0, z_slab, w, dy, thk))
                label_plate(doc, tname, x0, -400, z=z_ffl + 200)
                dy_door = P.PLATE_W // 2 - dw // 2
                add(doc, dname, box_at(-100, dy_door, z_ffl, 200, dw, dh))
                label_plate(doc, dname, -400, dy_door, z=z_ffl + 1000)
                add(doc, rname, box_at(x0, y0, z_ffl, 80, dy, rh))
    print("life terraces floors=%d faces=%s (doors + rails)"
          % (n_life, ",".join(faces)))


def _overflow_terraces(doc):
    """Grade overflow bands + life terraces + optional GH envelopes.

    Life balconies: `_life_terraces`. Grade OVERFLOW_* receive clean
    tower surplus (AQS-SCALE-001). Northern hemisphere: S+E+W.
    """
    _life_terraces(doc)

    lat = float(P.SITE_LAT_DEG)
    thk = P.TERRACE_SLAB_THK
    run = float(P.TERRACE_RUN)
    n = max(1, int(P.TERRACE_BANDS))
    drop = float(P.TERRACE_DROP)
    band = run / float(n)
    step = drop / float(max(1, n - 1)) if n > 1 else 0.0
    apron = P.TERRACE_WIDTH
    d = int(P.TERRACE_DOWNCOMER_D)

    if lat >= 0:
        faces = ("S", "E", "W")
    else:
        faces = ("N", "E", "W")

    # Conceptual overflow: roof-tank spill lip on equator edge → downcomer
    # → grade outfall onto innermost terrace band (clean water only).
    rx = P.ROOF_TANK_X + P.ROOF_TANK_L // 2 - d // 2
    if lat >= 0:
        ry_spill = P.ROOF_TANK_Y - d
        ry_dc = -d
        dc_name = "OVERFLOW_DOWNCOMER_S"
        outfall_name = "OVERFLOW_OUTFALL_S"
        outfall = box_at(rx - d, -apron, P.Z_L0, d * 3, apron, max(100, thk // 2))
    else:
        ry_spill = P.ROOF_TANK_Y + P.ROOF_TANK_W
        ry_dc = P.PLATE_W
        dc_name = "OVERFLOW_DOWNCOMER_N"
        outfall_name = "OVERFLOW_OUTFALL_N"
        outfall = box_at(rx - d, P.PLATE_W, P.Z_L0, d * 3, apron, max(100, thk // 2))
    z_spill = P.ROOF_TANK_Z + P.ROOF_TANK_H - thk
    add(doc, "OVERFLOW_SPILL_ROOF",
        box_at(rx, ry_spill, z_spill, d, d, thk + 100))
    label_plate(doc, "OVERFLOW_SPILL_ROOF", rx, ry_spill - 400,
                z=z_spill + 200)
    add(doc, dc_name,
        box_at(rx, ry_dc, P.Z_L0, d, d,
               max(100, (P.ROOF_TANK_Z + P.ROOF_TANK_H) - P.Z_L0)))
    label_plate(doc, dc_name, rx, ry_dc - 400, z=P.Z_L1 + 500)
    add(doc, outfall_name, outfall)
    label_plate(doc, outfall_name, rx, ry_dc - 400, z=P.Z_L0 + 200)

    def _band_z(i):
        # i=0 innermost (near plate, near grade); i=n-1 outermost (lowest)
        return P.Z_L0 - int(round(i * step)) - thk

    for face in faces:
        for i in range(n):
            name = "OVERFLOW_TERRACE_%s_B%d" % (face, i + 1)
            z = _band_z(i)
            if face == "S":
                y0 = -int(round((i + 1) * band))
                shp = box_at(0, y0, z, P.PLATE_L, int(round(band)), thk)
                lbl_y = y0 - 400
                lbl_x = 200
            elif face == "N":
                y0 = P.PLATE_W + int(round(i * band))
                shp = box_at(0, y0, z, P.PLATE_L, int(round(band)), thk)
                lbl_y = y0 + int(round(band)) - 200
                lbl_x = 200
            elif face == "E":
                x0 = P.PLATE_L + int(round(i * band))
                y0 = -int(round(band)) if lat >= 0 else 0
                dy = P.PLATE_W + int(round(band))
                shp = box_at(x0, y0, z, int(round(band)), dy, thk)
                lbl_y = -400
                lbl_x = x0 + 200
            else:  # W
                x0 = -int(round((i + 1) * band))
                y0 = -int(round(band)) if lat >= 0 else 0
                dy = P.PLATE_W + int(round(band))
                shp = box_at(x0, y0, z, int(round(band)), dy, thk)
                lbl_y = -400
                lbl_x = x0
            add(doc, name, shp)
            if i == 0 or i == n - 1:
                label_plate(doc, name, lbl_x, lbl_y, z=P.Z_L0 + 200)
        mid = n // 2
        fam = "OVERFLOW_TERRACE_%s" % face
        if face == "S":
            label_plate(doc, fam, 200, -int(round((mid + 0.5) * band)) - 400,
                        z=P.Z_L0 + 400)
        elif face == "N":
            label_plate(doc, fam, 200,
                        P.PLATE_W + int(round((mid + 0.5) * band)) - 200,
                        z=P.Z_L0 + 400)
        elif face == "E":
            label_plate(doc, fam,
                        P.PLATE_L + int(round((mid + 0.5) * band)) + 200,
                        -400, z=P.Z_L0 + 400)
        else:
            label_plate(doc, fam, -int(round((mid + 0.5) * band)), -400,
                        z=P.Z_L0 + 400)

    if lat >= 0:
        add(doc, "OVERFLOW_APRON_S",
            box_at(0, -min(apron, int(round(band))), P.Z_L0,
                   P.PLATE_L, min(apron, int(round(band))), max(100, thk)))
    else:
        add(doc, "OVERFLOW_APRON_N",
            box_at(0, P.PLATE_W, P.Z_L0,
                   P.PLATE_L, min(apron, int(round(band))), max(100, thk)))
    add(doc, "OVERFLOW_APRON_E",
        box_at(P.PLATE_L - min(apron, int(round(band))), 0, P.Z_L0,
               min(apron, int(round(band))), P.PLATE_W, max(100, thk)))
    add(doc, "OVERFLOW_APRON_W",
        box_at(0, 0, P.Z_L0,
               min(apron, int(round(band))), P.PLATE_W, max(100, thk)))

    # Planting beds on innermost S grade band + irrig (AQS-TRR-001).
    if "S" in faces:
        z_bed = _band_z(0) + thk
        bed_w = int(round(band * 0.55))
        bed_h = 400
        for bi in range(3):
            bx = 2000 + bi * 6000
            if bx + 4000 > P.PLATE_L:
                break
            bname = "TERRACE_BED_S_%d" % (bi + 1)
            add(doc, bname,
                box_at(bx, -int(round(band * 0.85)), z_bed, 4000, bed_w, bed_h))
            label_plate(doc, bname, bx, -int(round(band)) - 400, z=P.Z_L0 + 300)
        add(doc, "TERRACE_IRRIG_HDR_S",
            box_at(500, -int(round(band * 0.25)), z_bed + bed_h,
                   P.PLATE_L - 1000, 150, 150))
        label_plate(doc, "TERRACE_IRRIG_HDR_S", 500, -400, z=P.Z_L0 + 500)

        # Optional enclosed greenhouse envelopes (AQS-TRR-GH-001).
        run_i = int(round(run))
        gh_h = 3500
        add(doc, "GH_ENV_S",
            box_at(200, -run_i, P.Z_L0, P.PLATE_L - 400, run_i, gh_h))
        label_plate(doc, "GH_ENV_S", 400, -run_i - 400, z=P.Z_L0 + 2800)
        wrap = int(round(band))
        add(doc, "GH_ENV_E",
            box_at(P.PLATE_L, -wrap, P.Z_L0, wrap, P.PLATE_W + wrap, gh_h))
        label_plate(doc, "GH_ENV_E", P.PLATE_L + 200, -400, z=P.Z_L0 + 2800)
        add(doc, "GH_ENV_W",
            box_at(-wrap, -wrap, P.Z_L0, wrap, P.PLATE_W + wrap, gh_h))
        label_plate(doc, "GH_ENV_W", -wrap, -400, z=P.Z_L0 + 2800)
        add(doc, "GH_AHU",
            box_at(P.PLATE_L // 2 - 800, -run_i + 200, P.Z_L0, 1600, 1200, 2200))
        label_plate(doc, "GH_AHU", P.PLATE_L // 2 - 800, -run_i - 200, z=P.Z_L0 + 2000)
        add(doc, "GH_IRRIG_HDR",
            box_at(500, -int(round(band * 0.45)), z_bed + bed_h + 200,
                   P.PLATE_L - 1000, 150, 150))
        label_plate(doc, "GH_IRRIG_HDR", 500, -600, z=P.Z_L0 + 700)
        add(doc, "GH_DOOR_AIRLOCK",
            box_at(P.PLATE_L // 2 - 1200, -1200, P.Z_L0, 2400, 1200, 2800))
        label_plate(doc, "GH_DOOR_AIRLOCK", P.PLATE_L // 2 - 1200, -1600,
                    z=P.Z_L0 + 2400)


def _life_slabs(doc):
    """One structural slab per discrete life floor (HAB∥FARM between roof and L0)."""
    for i in range(P.LIFE_LEVELS):
        name = "SLAB_L1" if i == 0 else "SLAB_L1_S%d" % (i + 1)
        _slab(doc, name, P.life_z(i))


def _basement_slabs(doc):
    """Process basement slabs; CATCH slab is always deepest (SLAB_Lm2)."""
    for i in range(P.BASEMENT_LEVELS):
        name = "SLAB_Lm1" if i == 0 else "SLAB_Lm1_B%d" % (i + 1)
        _slab(doc, name, P.basement_z(i))
    _slab(doc, "SLAB_Lm2", P.Z_Lm2)  # catch plate — deepest


def attach(doc, lat_deg=None):
    _basement_slabs(doc)
    _slab(doc, "SLAB_L0", P.Z_L0)
    _life_slabs(doc)
    _slab(doc, "SLAB_L2", P.Z_L2)
    _core_rooms(doc)
    _shafts(doc)
    _stairs_elev(doc)
    _tanks(doc)
    _envelope_walls(doc)
    _array_roof(doc, lat_deg=lat_deg)
    _overflow_terraces(doc)


def build():
    plant = OUT / "plant.FCStd"
    doc = App.openDocument(str(plant)) if plant.exists() else App.newDocument("BLD")
    attach(doc)
    doc.recompute()
    out = plant if plant.exists() else OUT / "building_stack.FCStd"
    doc.saveAs(str(out))
    print("building stack attached →", out)
    print("scale SCALE_M=%s bays=%dx%d cassette=%s life=%d basement=%d"
          % (P.SCALE_M, P.MODULE_BAYS_X, P.MODULE_BAYS_Y,
             P.CASSETTE_ID, P.LIFE_LEVELS, P.BASEMENT_LEVELS))


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
