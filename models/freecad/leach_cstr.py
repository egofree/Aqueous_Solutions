#!/usr/bin/env python3
"""FreeCAD Part script: LEACH CSTR 1 + CSTR 2 weir + CSTR 3 floor auger.

    freecadcmd leach_cstr.py
    # or: FreeCADCmd leach_cstr.py

Saves leach_cstr.FCStd and leach_cstr.step next to this file.
This environment has no FreeCAD binary; run it on a machine that does.
"""
from pathlib import Path
import math
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P

import FreeCAD as App
import Part


OUT = Path(__file__).resolve().parent


def box_at(x, y, z, dx, dy, dz):
    s = Part.makeBox(dx, dy, dz)
    s.translate(App.Vector(x, y, z))
    return s


def cyl(d, h, x, y, z, axis="z"):
    c = Part.makeCylinder(d / 2.0, h)
    if axis == "x":
        c.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
    elif axis == "y":
        c.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
    c.translate(App.Vector(x, y, z))
    return c


def helix_flight(length, pitch, od, shaft, origin, axis="+x"):
    """Shaft + discrete helical paddles. makePipe(helix) is a null shape on FC 1.0."""
    solid = Part.makeCylinder(shaft / 2.0, length)
    blade_w = (od - shaft) / 2.0
    blade_t = 5.0
    blade_h = 14.0
    step = 8.0
    n = max(1, int(length / step))
    for i in range(n):
        z = i * step
        ang = (z / float(pitch)) * 360.0
        b = Part.makeBox(blade_w, blade_t, blade_h)
        b.translate(App.Vector(shaft / 2.0, -blade_t / 2.0, z))
        b.rotate(App.Vector(0, 0, z), App.Vector(0, 0, 1), ang)
        solid = solid.fuse(b)
    if axis == "+x":
        solid.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
    solid.translate(origin)
    return solid


def build():
    doc = App.newDocument("LEACH_CSTR_1")
    t, fl = P.WALL, P.FLOOR
    L, W, H = P.CSTR_L, P.CSTR_W, P.CSTR_H

    outer = box_at(0, 0, 0, L + 2 * t, W + 2 * t, H + fl)
    inner = box_at(t, t, fl, L, W, H + 1)
    shell = outer.cut(inner)

    weir = box_at(
        t + L - 1,
        t + (W - P.WEIR_W) / 2,
        fl + P.WEIR_CREST,
        t + 2,
        P.WEIR_W,
        P.WEIR_SLOT_H + 200,
    )
    shell = shell.cut(weir)

    spout_outer = box_at(
        t + L + t,
        t + (W - P.WEIR_W) / 2 - t,
        fl + P.WEIR_CREST - t,
        P.WEIR_LIP,
        P.WEIR_W + 2 * t,
        P.WEIR_SLOT_H + t + 20,
    )
    spout_inner = box_at(
        t + L + t - 1,
        t + (W - P.WEIR_W) / 2,
        fl + P.WEIR_CREST,
        P.WEIR_LIP + 2,
        P.WEIR_W,
        P.WEIR_SLOT_H + 40,
    )
    spout = spout_outer.cut(spout_inner)

    ty = t + P.AUGER_OFFSET_Y - P.AUGER_TROUGH_W / 2
    trough_o = box_at(t + 40, ty, fl, L - 80, P.AUGER_TROUGH_W, P.AUGER_TROUGH_H)
    trough_i = box_at(t + 39, ty + 12, fl + 12, L - 78, P.AUGER_TROUGH_W - 24, P.AUGER_TROUGH_H)
    trough = trough_o.cut(trough_i)

    auger = helix_flight(
        L - 140,
        P.AUGER_PITCH,
        P.AUGER_D,
        P.AUGER_SHAFT,
        App.Vector(t + 60, t + P.AUGER_OFFSET_Y, fl + P.AUGER_TROUGH_H / 2),
        "+x",
    )

    # inclined lift housing
    lift_len = 700
    start = App.Vector(t + L - 40, t + P.AUGER_OFFSET_Y, fl + P.AUGER_TROUGH_H / 2)
    housing = Part.makeCylinder((P.AUGER_D + 24) / 2.0, lift_len)
    bore = Part.makeCylinder((P.AUGER_D + 4) / 2.0, lift_len + 2)
    bore.translate(App.Vector(0, 0, -1))
    housing = housing.cut(bore)
    housing.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90 - P.AUGER_INCLINE)
    housing.translate(start)

    drop_x = t + P.DROP_X
    drop_y = t + (W - P.DROP_W) / 2

    lid = box_at(0, 0, fl + H, L + 2 * t, W + 2 * t, t)
    drop = box_at(drop_x, drop_y, fl + H - 1, P.DROP_L, P.DROP_W, t + 2)
    mixer_h = cyl(P.MIXER_D, t + 2, t + L * 0.55, t + W * 0.55, fl + H - 1)
    gas_h = cyl(P.GAS_D, t + 2, t + L * 0.80, t + W * 0.20, fl + H - 1)
    lid = lid.cut(drop).cut(mixer_h).cut(gas_h)

    mixer = cyl(36, H + 200, t + L * 0.55, t + W * 0.55, fl + 80)

    pump_bore = cyl(P.PUMP_D, t + 4, -1, t + P.PUMP_Y, fl + P.PUMP_Z, axis="x")
    shell = shell.cut(pump_bore)

    nozzle = cyl(P.PUMP_D + 16, t + 180, 0, t + P.PUMP_Y, fl + P.PUMP_Z, axis="x")
    nozzle_b = cyl(P.PUMP_D, t + 182, -1, t + P.PUMP_Y, fl + P.PUMP_Z, axis="x")
    nozzle = nozzle.cut(nozzle_b)
    strainer = box_at(
        t, t + P.PUMP_Y - P.STRAINER_W / 2, fl + P.PUMP_Z - P.STRAINER_H / 2,
        P.STRAINER_L, P.STRAINER_W, P.STRAINER_H,
    )
    strainer_i = box_at(
        t + 12, t + P.PUMP_Y - P.STRAINER_W / 2 + 12,
        fl + P.PUMP_Z - P.STRAINER_H / 2 + 12,
        P.STRAINER_L - 16, P.STRAINER_W - 24, P.STRAINER_H - 24,
    )
    strainer = strainer.cut(strainer_i)
    pump_body = box_at(-220, t + P.PUMP_Y - 90, fl + P.PUMP_Z - 90, 180, 180, 180)
    pump = nozzle.fuse(strainer).fuse(pump_body)

    coam_o = box_at(drop_x - 20, drop_y - 20, fl + H + t, P.DROP_L + 40, P.DROP_W + 40, P.DROP_COAM)
    coam_i = box_at(drop_x, drop_y, fl + H + t - 1, P.DROP_L, P.DROP_W, P.DROP_COAM + 2)
    coaming = coam_o.cut(coam_i)

    mezz = box_at(-P.MEZZ_L, 0, P.MEZZ_H, P.MEZZ_L + 80, W + 2 * t, P.MEZZ_THK)
    post1 = box_at(-P.MEZZ_L + 40, t, 0, 80, 80, P.MEZZ_H)
    post2 = box_at(-P.MEZZ_L + 40, t + W, 0, 80, 80, P.MEZZ_H)
    mezz = mezz.fuse(post1).fuse(post2)

    hx = -P.MEZZ_L + 80
    hy = t + (W - P.HOPPER_W) / 2
    hz = P.MEZZ_H + P.MEZZ_THK + P.SHRED_H
    hopper = box_at(hx, hy, hz, P.HOPPER_L, P.HOPPER_W, P.HOPPER_H)
    sx = hx + (P.HOPPER_L - P.SHRED_L) / 2
    sy = t + (W - P.SHRED_W) / 2
    shred = box_at(sx, sy, P.MEZZ_H + P.MEZZ_THK, P.SHRED_L, P.SHRED_W, P.SHRED_H)
    hood = box_at(sx - 20, sy - 20, P.MEZZ_H + P.MEZZ_THK + P.SHRED_H - 20,
                  P.SHRED_L + 40, P.SHRED_W + 40, 160)
    hood_i = box_at(sx, sy, P.MEZZ_H + P.MEZZ_THK + P.SHRED_H - 21,
                    P.SHRED_L, P.SHRED_W, 140)
    hood = hood.cut(hood_i)
    dust = cyl(P.DUST_D, 200, sx + P.SHRED_L / 2, sy + P.SHRED_W / 2,
               P.MEZZ_H + P.MEZZ_THK + P.SHRED_H + 140)
    feed = hopper.fuse(shred).fuse(hood).fuse(dust)

    conv_sx = sx + P.SHRED_L
    conv_sy = drop_y + (P.DROP_W - P.CONV_W) / 2
    conv_sz = P.MEZZ_H + P.MEZZ_THK + 80
    conv_ex = drop_x
    conv_len = conv_ex - conv_sx
    conv = box_at(conv_sx, conv_sy, conv_sz, conv_len, P.CONV_W, P.CONV_H)

    weir_sx = t + L + t + P.WEIR_LIP
    weir_sy = t + (W - P.WEIR_W) / 2
    weir_sz = fl + P.WEIR_CREST - 20
    fdew = box_at(weir_sx, weir_sy, weir_sz, P.FDEW_L, P.FDEW_W, P.FDEW_H)
    fpan = box_at(weir_sx - 40, weir_sy + 20, weir_sz - 50, 200, P.FDEW_W - 40, 40)
    fdew = fdew.fuse(fpan)

    ang = math.radians(P.AUGER_INCLINE)
    lift_ex = t + L - 40 + P.AUGER_LIFT_L * math.cos(ang)
    lift_ez = fl + P.AUGER_TROUGH_H / 2 + P.AUGER_LIFT_L * math.sin(ang)
    sdew = box_at(
        lift_ex, t + P.AUGER_OFFSET_Y - P.SDEW_W / 2, lift_ez - 20,
        P.SDEW_L, P.SDEW_W, P.SDEW_H,
    )
    span = box_at(
        lift_ex - 80, t + P.AUGER_OFFSET_Y - P.SDEW_W / 2 + 20, lift_ez - 60,
        120, P.SDEW_W - 40, 30,
    )
    sdew = sdew.fuse(span)

    split = box_at(
        lift_ex + P.SDEW_L, t + P.AUGER_OFFSET_Y - P.SPLIT_W / 2, lift_ez - 20,
        P.SPLIT_L, P.SPLIT_W, P.SPLIT_H,
    )
    oil = box_at(
        weir_sx + P.FDEW_L, weir_sy + (P.FDEW_W - P.STUB_W) / 2,
        weir_sz + P.FDEW_RISE - 40,
        P.STUB_L, P.STUB_W, P.STUB_H,
    )
    glass = box_at(
        lift_ex + P.SDEW_L + P.SPLIT_L,
        t + P.AUGER_OFFSET_Y - P.SPLIT_W / 2 - P.STUB_W - 20,
        lift_ez - 20,
        P.STUB_L, P.STUB_W, P.STUB_H,
    )

    body = shell.fuse(spout).fuse(trough).fuse(lid).fuse(coaming)

    def add(name, shape):
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        return obj

    add("LEACH_CSTR_1", body)
    add("CSTR3_AUGER", auger)
    add("CSTR3_LIFT_TUBE", housing)
    add("MIXER", mixer)
    add("LEACHATE_PUMP", pump)
    add("MEZZANINE", mezz)
    add("HOPPER_SHREDDER", feed)
    add("VIBRATORY_CONVEYOR", conv)
    add("FLOAT_DEWATER", fdew)
    add("SINK_DEWATER", sdew)
    add("VIBRATORY_SPLIT", split)
    add("OIL_LINE_STUB", oil)
    add("GLASS_CERAMIC_STUB", glass)
    doc.recompute()

    fcstd = OUT / "leach_cstr.FCStd"
    step = OUT / "leach_cstr.step"
    doc.saveAs(str(fcstd))
    Part.export([
        doc.getObject("LEACH_CSTR_1"),
        doc.getObject("CSTR3_AUGER"),
        doc.getObject("CSTR3_LIFT_TUBE"),
        doc.getObject("MIXER"),
        doc.getObject("LEACHATE_PUMP"),
        doc.getObject("MEZZANINE"),
        doc.getObject("HOPPER_SHREDDER"),
        doc.getObject("VIBRATORY_CONVEYOR"),
        doc.getObject("FLOAT_DEWATER"),
        doc.getObject("SINK_DEWATER"),
        doc.getObject("VIBRATORY_SPLIT"),
        doc.getObject("OIL_LINE_STUB"),
        doc.getObject("GLASS_CERAMIC_STUB"),
    ], str(step))
    print("wrote", fcstd)
    print("wrote", step)


# FreeCADCmd does not set __name__ == "__main__". Run if this file is on argv.
if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
