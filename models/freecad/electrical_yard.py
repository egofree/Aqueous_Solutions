#!/usr/bin/env python3
"""Electrical yard: rectifier, ATS, Sol-Ark, ZnBr2, PV, BACKUP_GEN, FUEL_CELL, GEO.

Yard sits at L0 west of the **north** dock (AQS-SITE-001 / AQS-BLD-001 Rev D).
Surplus policy (AQS-SCALE-001 §5): charge batteries → pump roof tank →
controlled overflow to garden terraces when tank and batteries are full.

Yard stubs include clearances, keep-outs, tags, and utility rough-ins
(docs + massing). Duties / nameplates TBD — do not invent kW counts.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate, sign

import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent

# Working / service clearances (mm) — schematic keep-outs, not PE stamps.
CLEAR_GEN = 1500       # around BACKUP_GEN for service / exhaust
CLEAR_FC = 1500        # around FUEL_CELL stack enclosure
CLEAR_GEO = 1200       # around GEO_HP pad
CLEAR_ZNBR = 1000      # aisle face of ZnBr2 packs
SEP_GEN_FC = 3000      # preferred H₂ consumer separation (NFPA 2 practice hook)
YARD_PAD_THK = 150
YARD_FENCE_H = 2400


def origin():
    # POWER yard at grade (L0), west of north dock / plate (AQS-SITE-001).
    # Y aligns with DOCK_Y so GEN/FC/GEO abut the NW truck apron.
    return -P.MEZZ_L - 2800, P.DOCK_Y, P.Z_L0


def _yard_envelope(doc, x0, y0, z):
    """Pad, fence keep-out, and yard tag — clash / service envelope only."""
    # Rough yard pad covering rectifier–GEN–FC–GEO strip + ZnBr row start
    # Rev B (2026-10-16): pad stops at the building west face (was under ELEV_DOCK / STAIR_SERVICE);
    # fence moved west of the BACKUP_GEN 1 h room (gen had straddled the fence).
    gx = min(x0 - 2000, -int(P.YARD_WALL_CLEAR) - 3300)
    fx = min(x0 - 800, gx - 2400)
    pad_l = -100 - fx
    pad_w = max(13000, P.RECT_COUNT * (P.RECT_W + 400) + P.ZNBR_W + 4000)  # Rev B: +500 for the NW generator room
    add(doc, "YARD_PAD",
        box_at(fx, y0 - 500, z - YARD_PAD_THK, pad_l, pad_w, YARD_PAD_THK))
    label_plate(doc, "YARD_PAD", x0 - 500, y0 - 900, z=z + 200)
    # Fence / keep-out ribbon on west edge (site boundary side)
    add(doc, "YARD_FENCE_W",
        box_at(fx - 100, y0 - 500, z, 100, pad_w, YARD_FENCE_H))
    label_plate(doc, "YARD_FENCE_W", x0 - 800, y0 - 900, z=z + 1000)
    # Access gate toward north dock apron
    add(doc, "YARD_GATE_N",
        box_at(x0 + 2000, y0 + pad_w - 600, z, 2400, 200, 2200))
    label_plate(doc, "YARD_GATE_N", x0 + 2000, y0 + pad_w - 200, z=z + 1000)


def _clearance(doc, name, x, y, z, sx, sy):
    """Flat keep-out pad (height 50 mm) for service / classified extent."""
    add(doc, name, box_at(x, y, z, sx, sy, 50))
    label_plate(doc, name, x, y - 200, z=z + 200)


def _util_roughins(doc, x0, y0, z):
    """Utility rough-in stubs at yard edge — not routed piping."""
    # H₂ fuel rough-in from CRYO_H2 / H2_DRYER branch (S45 / S49)
    add(doc, "UTIL_ROUGH_H2",
        box_at(x0 + 100, y0 - 400, z, 400, 400, 900))
    label_plate(doc, "UTIL_ROUGH_H2", x0 + 100, y0 - 600, z=z + 700)
    # Q4 warm-water rough-in (GEO_HP / FC_HX_Q4 peers)
    add(doc, "UTIL_ROUGH_Q4",
        box_at(x0 + 600, y0 - 400, z, 400, 400, 700))
    label_plate(doc, "UTIL_ROUGH_Q4", x0 + 600, y0 - 600, z=z + 500)
    # 480 V / DC tray stub toward plate (Sol-Ark / rectifier feeders)
    add(doc, "UTIL_ROUGH_480V",
        box_at(x0 + 1100, y0 - 400, z, 600, 300, 500))
    label_plate(doc, "UTIL_ROUGH_480V", x0 + 1100, y0 - 600, z=z + 400)
    # GHEX header stub (off-plate bore field — keep-out only)
    add(doc, "UTIL_ROUGH_GHEX",
        box_at(x0 - 600, y0 + 200, z, 500, 500, 600))
    label_plate(doc, "UTIL_ROUGH_GHEX", x0 - 600, y0, z=z + 400)


def attach(doc):
    x0, y0, z = origin()
    _yard_envelope(doc, x0, y0, z)
    _util_roughins(doc, x0, y0, z)

    # Rectifier skids — one per cassette
    for r in range(P.RECT_COUNT):
        x = x0
        y = y0 + r * (P.RECT_W + 400)
        suffix = "" if r == 0 else "_%d" % (r + 1)
        add(doc, "RECTIFIER%s" % suffix,
            box_at(x, y, z, P.RECT_L, P.RECT_W, P.RECT_H))
        label_plate(doc, "RECTIFIER%s" % suffix, x, y - 200)
        if r == 0:
            add(doc, "ATS", box_at(x + P.RECT_L + 100, y, z, 600, P.RECT_W, 1600))
            label_plate(doc, "ATS", x + P.RECT_L + 100, y - 200)
            add(doc, "SOL_ARK_60K",
                box_at(x + P.RECT_L + 800, y, z,
                       P.SOLARK_L, P.SOLARK_W, P.SOLARK_H))
            label_plate(doc, "SOL_ARK_60K", x + P.RECT_L + 800, y - 200)
            sign(doc, "SIGN_ARC_FLASH_RECTIFIER", x, y - 700,
                 to=(x + P.RECT_L / 2.0, y + P.RECT_W / 2.0, P.RECT_H / 2.0))

    # ZnBr2 packs along -X from origin
    bx = x0
    by = y0 + P.RECT_COUNT * (P.RECT_W + 400) + 200
    for k in range(P.ZNBR_COUNT):
        ox = bx - k * (P.ZNBR_L + 200)
        suffix = "" if k == 0 else "_%d" % (k + 1)
        add(doc, "ZNBR2%s" % suffix,
            box_at(ox, by, z, P.ZNBR_L, P.ZNBR_W, P.ZNBR_H))
        label_plate(doc, "ZNBR2%s" % suffix, ox, by + P.ZNBR_W + 40)
        add(doc, "ZNBR2_POS_TANK%s" % suffix,
            box_at(ox, by + P.ZNBR_W + 80, z, 700, 700, 1200))
        add(doc, "ZNBR2_NEG_TANK%s" % suffix,
            box_at(ox + 800, by + P.ZNBR_W + 80, z, 700, 700, 1200))
        add(doc, "ZNBR2_BR2_SCRUBBER%s" % suffix,
            box_at(ox + P.ZNBR_L + 80, by, z, 500, 500, 1400))
        add(doc, "ZNBR2_BR2_REGEN%s" % suffix,
            box_at(ox + P.ZNBR_L + 80, by + 600, z, 500, 500, 1100))
        if k == 0:
            label_plate(doc, "ZNBR2_POS_TANK", ox, by + P.ZNBR_W + 800)
            label_plate(doc, "ZNBR2_NEG_TANK", ox + 800, by + P.ZNBR_W + 800)
            label_plate(doc, "ZNBR2_BR2_SCRUBBER", ox + P.ZNBR_L + 80, by - 200)
            label_plate(doc, "ZNBR2_BR2_REGEN", ox + P.ZNBR_L + 80, by + 1100)
            sign(doc, "SIGN_BR2_BATTERY", ox, by - 700,
                 to=(ox + P.ZNBR_L / 2.0, by + P.ZNBR_W / 2.0, P.ZNBR_H / 2.0))
            _clearance(doc, "CLEAR_ZNBR_AISLE",
                       ox - CLEAR_ZNBR, by - CLEAR_ZNBR, z,
                       P.ZNBR_L + 2 * CLEAR_ZNBR, P.ZNBR_W + 2 * CLEAR_ZNBR)

    # PV array modules west of yard — tilted equator-facing (same rule as ARRAY_ROOF).
    # Site north = +Y; positive rotation about +X raises north edge → south face (NH).
    tilt = float(P.SITE_LAT_DEG)
    for p in range(P.PV_COUNT):
        px = x0 - P.PV_L - 200 - p * (P.PV_L + 150)
        suffix = "" if p == 0 else "_%d" % (p + 1)
        panel = Part.makeBox(P.PV_L, P.PV_W, P.PV_H)
        panel.rotate(App.Vector(P.PV_L / 2.0, P.PV_W / 2.0, 0),
                     App.Vector(1, 0, 0), tilt)
        panel.translate(App.Vector(px, y0, z + 2000))
        add(doc, "PV_ARRAY%s" % suffix, panel)
        label_plate(doc, "PV_ARRAY%s" % suffix, px, y0 - 200, z=z + 2200)
    print("  PV_ARRAY tilt=%+.1f deg about +X (equator-facing)" % tilt)

    # Backup genset + geothermal + FC (AQS-PWR-001 / AQS-FC-001)
    # Layout lock: entire GEN/FC train stays west of ENV_WALL_W (X=0).
    # Prior placement put BACKUP_GEN / FUEL_CELL straddling the west wall and
    # FC_DCDC / FC_HX inside the plate — punch-through. Place west of rectifier.
    _fc_hx_east = 2500 + 800   # FC_HX offset + width from gx
    gx_max = -int(P.YARD_WALL_CLEAR) - _fc_hx_east
    gx = min(x0 - 2000, gx_max)
    gy = y0
    # Rev B (2026-10-16, GA_CHECK CAD clash fix): BACKUP_GEN moved to the free NW corner of the yard, in its own 1 h room.
    # Its clearance had overlapped the FUEL_CELL and ZnBr2 aisles and it straddled the old fence line; it is now >= 5 m
    # from the FUEL_CELL (SEP_GEN_FC 3 m), so the two standby sources do not share a fire area (redundancy rule).
    _fx = min(x0 - 800, gx - 2400)
    ggx, ggy = _fx + 300 + CLEAR_GEN, y0 + 9900
    add(doc, "BACKUP_GEN",
        box_at(ggx, ggy, z, 1400, 900, 1600))
    label_plate(doc, "BACKUP_GEN", ggx, ggy - 200)
    _clearance(doc, "CLEAR_BACKUP_GEN",
               ggx - CLEAR_GEN, ggy - CLEAR_GEN, z,
               1400 + 2 * CLEAR_GEN, 900 + 2 * CLEAR_GEN)
    add(doc, "GEN_H2_BUFFER",
        box_at(ggx + 1500, ggy, z, 600, 600, 1200))
    label_plate(doc, "GEN_H2_BUFFER", ggx + 1500, ggy - 200)
    add(doc, "GEN_EXHAUST_STUB",
        box_at(ggx + 400, ggy + 1000, z + 1200, 400, 400, 800))
    label_plate(doc, "GEN_EXHAUST_STUB", ggx + 400, ggy + 800, z=z + 1800)

    # PEM fuel-cell skid — offset +Y by SEP_GEN_FC intent (keep-out between)
    fx = gx
    fy = gy + max(1100, SEP_GEN_FC - 400)
    add(doc, "FUEL_CELL",
        box_at(fx, fy, z, 1600, 1000, 1600))
    label_plate(doc, "FUEL_CELL", fx, fy - 200)
    _clearance(doc, "CLEAR_FUEL_CELL",
               fx - CLEAR_FC, fy - CLEAR_FC, z,
               1600 + 2 * CLEAR_FC, 1000 + 2 * CLEAR_FC)
    add(doc, "FC_DCDC",
        box_at(fx + 1700, fy, z, 700, 700, 1400))
    label_plate(doc, "FC_DCDC", fx + 1700, fy - 200)
    add(doc, "FC_HX_Q4",
        box_at(fx + 2500, fy, z, 800, 700, 1200))
    label_plate(doc, "FC_HX_Q4", fx + 2500, fy - 200)
    add(doc, "FC_H2_MANIFOLD",
        box_at(fx + 1700, fy + 900, z, 500, 500, 1000))
    label_plate(doc, "FC_H2_MANIFOLD", fx + 1700, fy + 700)
    # Keep-out strip between GEN and FC H₂ trains
    ko_y = gy + 900
    ko_h = max(200, fy - (gy + 900) - 100)
    add(doc, "KO_GEN_FC",
        box_at(gx - 200, ko_y, z, 2000, ko_h, 50))
    label_plate(doc, "KO_GEN_FC", gx - 200, ko_y - 200, z=z + 200)

    # Geothermal HP pad; GHEX is off-plate (header stub in _util_roughins)
    hx = x0
    hy = by + P.ZNBR_W + 900
    add(doc, "GEO_HP",
        box_at(hx, hy, z, 1200, 800, 1400))
    label_plate(doc, "GEO_HP", hx, hy - 200)
    _clearance(doc, "CLEAR_GEO_HP",
               hx - CLEAR_GEO, hy - CLEAR_GEO, z,
               1200 + 2 * CLEAR_GEO, 800 + 2 * CLEAR_GEO)
    add(doc, "GEO_HDR",
        box_at(hx - 800, hy, z, 600, 600, 800))
    label_plate(doc, "GEO_HDR", hx - 800, hy - 200)
    add(doc, "GEO_ORC",
        box_at(hx + 1400, hy, z, 1000, 800, 1200))
    label_plate(doc, "GEO_ORC", hx + 1400, hy - 200)
    # Off-plate GHEX keep-out marker (bore field not modelled)
    add(doc, "KO_GEO_GHEX",
        box_at(hx - 2500, hy - 500, z, 1500, 2000, 50))
    label_plate(doc, "KO_GEO_GHEX", hx - 2500, hy - 700, z=z + 200)

    print("electrical yard modules PV=%d ZnBr2=%d RECT=%d (need=%.1f kW target=%.1f kW)"
          % (P.PV_COUNT, P.ZNBR_COUNT, P.RECT_COUNT,
             P.ELEC_NEED_KW, P.ELEC_TARGET_KW))
    print("  yard Y aligned to DOCK_Y=%d (north dock); GEN/FC east<=%d (no wall punch)"
          % (P.DOCK_Y, gx + _fc_hx_east))
    print("  CLEAR/KO/UTIL_ROUGH stubs on; YARD_WALL_CLEAR=%d"
          % P.YARD_WALL_CLEAR)


def build():
    doc = App.newDocument("ELECTRICAL_YARD")
    attach(doc)
    doc.recompute()
    doc.saveAs(str(OUT / "electrical_yard.FCStd"))
    print("wrote", OUT / "electrical_yard.FCStd")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
