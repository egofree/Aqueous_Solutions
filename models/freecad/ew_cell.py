#!/usr/bin/env python3
"""FreeCAD Part script: one funnel-bottom EW cell, A | CEM | C.

    freecadcmd ew_cell.py
"""
from pathlib import Path
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


def make_cell():
    t = P.WALL
    L, W, H = P.EW_L, P.EW_W, P.EW_H
    body_o = box_at(0, 0, 0, L + 2 * t, W + 2 * t, H + t)
    body_i = box_at(t, t, t, L, W, H + 1)
    body = body_o.cut(body_i)

    top_l, top_w = L + 2 * t, W + 2 * t
    bot = P.EW_VALVE_D + 2 * t
    outer_pts = [
        App.Vector(0, 0, 0),
        App.Vector(top_l, 0, 0),
        App.Vector(top_l, top_w, 0),
        App.Vector(0, top_w, 0),
    ]
    inner_top = [
        App.Vector(t, t, 0.5),
        App.Vector(t + L, t, 0.5),
        App.Vector(t + L, t + W, 0.5),
        App.Vector(t, t + W, 0.5),
    ]
    # loft funnel via makeLoft of two wires is fussy; use a cut cone-ish hull of boxes
    funnel_o = Part.makeLoft([
        Part.makePolygon([
            App.Vector(0, 0, 0), App.Vector(top_l, 0, 0),
            App.Vector(top_l, top_w, 0), App.Vector(0, top_w, 0),
            App.Vector(0, 0, 0),
        ], True),
        Part.makePolygon([
            App.Vector((top_l - bot) / 2, (top_w - bot) / 2, -P.EW_FUNNEL_H),
            App.Vector((top_l + bot) / 2, (top_w - bot) / 2, -P.EW_FUNNEL_H),
            App.Vector((top_l + bot) / 2, (top_w + bot) / 2, -P.EW_FUNNEL_H),
            App.Vector((top_l - bot) / 2, (top_w + bot) / 2, -P.EW_FUNNEL_H),
            App.Vector((top_l - bot) / 2, (top_w - bot) / 2, -P.EW_FUNNEL_H),
        ], True),
    ], True)
    v_in = P.EW_VALVE_D
    funnel_i = Part.makeLoft([
        Part.makePolygon([
            App.Vector(t, t, 1), App.Vector(t + L, t, 1),
            App.Vector(t + L, t + W, 1), App.Vector(t, t + W, 1),
            App.Vector(t, t, 1),
        ], True),
        Part.makePolygon([
            App.Vector((top_l - v_in) / 2, (top_w - v_in) / 2, -P.EW_FUNNEL_H + 1),
            App.Vector((top_l + v_in) / 2, (top_w - v_in) / 2, -P.EW_FUNNEL_H + 1),
            App.Vector((top_l + v_in) / 2, (top_w + v_in) / 2, -P.EW_FUNNEL_H + 1),
            App.Vector((top_l - v_in) / 2, (top_w + v_in) / 2, -P.EW_FUNNEL_H + 1),
            App.Vector((top_l - v_in) / 2, (top_w - v_in) / 2, -P.EW_FUNNEL_H + 1),
        ], True),
    ], True)
    funnel = funnel_o.cut(funnel_i)

    valve = Part.makeCylinder((P.EW_VALVE_D + 2 * t) / 2.0, P.EW_VALVE_L + 2)
    valve_b = Part.makeCylinder(P.EW_VALVE_D / 2.0, P.EW_VALVE_L + 4)
    valve_b.translate(App.Vector(0, 0, -1))
    valve = valve.cut(valve_b)
    valve.translate(App.Vector(top_l / 2, top_w / 2, -P.EW_FUNNEL_H - P.EW_VALVE_L))

    overflow = box_at(t + L - 1, t + W * 0.55, t + H - 70, t + 2, W * 0.30, 80)
    slot = box_at(t + 8, t + W / 2 - P.EW_SLOT / 2, t - 1, L - 16, P.EW_SLOT, H)

    cell = body.fuse(funnel).fuse(valve).cut(overflow).cut(slot)

    cem = box_at(
        t + 10,
        t + W / 2 - P.EW_MEM_T / 2,
        t + 24,
        L - 20,
        P.EW_MEM_T,
        H - 50,
    )
    return cell, cem


def build():
    doc = App.newDocument("EW_CELL")
    cell, cem = make_cell()
    o1 = doc.addObject("Part::Feature", "EW_CELL")
    o1.Shape = cell
    o2 = doc.addObject("Part::Feature", "CEM")
    o2.Shape = cem
    doc.recompute()
    doc.saveAs(str(OUT / "ew_cell.FCStd"))
    Part.export([o1, o2], str(OUT / "ew_cell.step"))
    print("wrote", OUT / "ew_cell.FCStd")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
