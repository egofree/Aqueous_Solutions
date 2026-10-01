#!/usr/bin/env python3
"""Phase D waypoints in mm. Prints paths. Also used by render_frames.py.

    python3 animate_shots.py
"""
from pathlib import Path
import math
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P


def drop_xy():
    t = P.WALL
    return t + P.DROP_X + P.DROP_L / 2, t + (P.CSTR_W - P.DROP_W) / 2


def oil_origin():
    t = P.WALL
    x = t + P.CSTR_L + t + P.WEIR_LIP + P.FDEW_L + P.STUB_L + 100
    y = t + (P.CSTR_W - P.WEIR_W) / 2
    z = P.FLOOR + P.WEIR_CREST - 20 + P.FDEW_RISE
    return x, y, z


def shots():
    t = P.WALL
    dx, dy = drop_xy()
    weir_x = t + P.CSTR_L + t + P.WEIR_LIP
    weir_y = t + (P.CSTR_W - P.WEIR_W) / 2
    ang = math.radians(P.AUGER_INCLINE)
    lift_ex = t + P.CSTR_L - 40 + P.AUGER_LIFT_L * math.cos(ang)
    lift_ez = P.FLOOR + P.AUGER_TROUGH_H / 2 + P.AUGER_LIFT_L * math.sin(ang)
    oil_x = weir_x + P.FDEW_L + P.STUB_L
    ox, oy, oz = oil_origin()
    px = ox + P.DRYER_L + 80
    qx = px + P.PYRO_L + 80
    fx = qx + 900
    ax = fx + 1200
    return {
        "D1_shred_drop": [
            (-P.MEZZ_L + 200, dy, P.MEZZ_H + P.SHRED_H + P.HOPPER_H),
            (-P.MEZZ_L + 400, dy, P.MEZZ_H + 200),
            (dx, dy, P.FLOOR + P.CSTR_H + P.WALL + P.DROP_COAM),
            (dx, dy, P.FLOOR + P.CSTR_H / 2),
        ],
        "D2_float": [
            (t + P.CSTR_L * 0.4, weir_y + P.WEIR_W / 2, P.FLOOR + P.WEIR_CREST - 20),
            (weir_x, weir_y + P.WEIR_W / 2, P.FLOOR + P.WEIR_CREST),
            (weir_x + P.FDEW_L, weir_y, P.FLOOR + P.WEIR_CREST + P.FDEW_RISE),
            (oil_x, weir_y, P.FLOOR + P.WEIR_CREST + P.FDEW_RISE),
        ],
        "D2_sink": [
            (t + 200, t + P.AUGER_OFFSET_Y, P.FLOOR + 40),
            (t + P.CSTR_L - 40, t + P.AUGER_OFFSET_Y, P.FLOOR + P.AUGER_TROUGH_H / 2),
            (lift_ex, t + P.AUGER_OFFSET_Y, lift_ez),
            (lift_ex + P.SDEW_L, t + P.AUGER_OFFSET_Y, lift_ez),
        ],
        "D2_grit": [
            (lift_ex + P.SDEW_L, t + P.AUGER_OFFSET_Y, lift_ez),
            (lift_ex + P.SDEW_L + P.SPLIT_L, t + P.AUGER_OFFSET_Y - 200, lift_ez),
        ],
        "D3_ew_overflow": [
            (P.AISLE_X0 + i * P.EW_PITCH + P.EW_L / 2,
             P.AISLE_Y + P.EW_W / 2,
             P.AISLE_Z + P.EW_H - 40)
            for i in range(9)
        ],
        "D4_powder": [
            (P.AISLE_X0 + P.EW_L / 2, P.AISLE_Y + P.EW_W / 2, P.AISLE_Z),
            (P.AISLE_X0 + P.EW_L / 2, P.AISLE_Y + P.EW_W / 2,
             P.AISLE_Z - P.EW_FUNNEL_H - P.EW_VALVE_L),
            (P.AISLE_X0 + P.EW_L / 2, P.AISLE_Y + P.EW_W / 2,
             P.AISLE_Z - P.EW_FUNNEL_H - P.EW_VALVE_L - P.PAIL_W),
        ],
        "D4_fe": [
            (P.AISLE_X0 + 5 * P.EW_PITCH + P.EW_L / 2,
             P.AISLE_Y + P.EW_W / 2, P.AISLE_Z),
            (P.AISLE_X0 + 5 * P.EW_PITCH + P.EW_L / 2,
             P.AISLE_Y + P.EW_W / 2,
             P.AISLE_Z - P.EW_FUNNEL_H - P.EW_VALVE_L - P.PAIL_W),
        ],
        "D5_pyro": [
            (ox, oy, 400),
            (px, oy + P.DRYER_W / 2, 400),
            (px + P.PYRO_L, oy + P.DRYER_W / 2, 400),
            (qx, oy, 200),
        ],
        "D6_cuts": [
            (qx + 400, oy, 400),
            (fx + P.FRAC_D / 2, oy + P.DRYER_W / 2, 1400),
            (fx + 700, oy, 350),
            (fx + 700, oy + 350, 350),
            (fx + 700, oy + 700, 350),
            (fx + 700, oy + 1050, 350),
        ],
        "D6_c29_recycle": [
            (fx + 700, oy + 1050, 740),
            (px, oy + 1050, 740),
        ],
        "D6_ncg": [
            (qx + 400, oy, 900),
            (ax, oy + P.DRYER_W / 2, 800),
        ],
    }


DURATION_S = {
    "D1_shred_drop": 4,
    "D2_float": 6,
    "D2_sink": 6,
    "D2_grit": 3,
    "D3_ew_overflow": 8,
    "D4_powder": 5,
    "D4_fe": 3,
    "D5_pyro": 6,
    "D6_cuts": 8,
    "D6_c29_recycle": 4,
    "D6_ncg": 4,
}

FPS = 12


def lerp_path(pts, n):
    if len(pts) == 1:
        return [pts[0]] * n
    segs = len(pts) - 1
    out = []
    for i in range(n):
        u = 0 if n == 1 else i / (n - 1)
        f = u * segs
        k = min(int(f), segs - 1)
        t = f - k
        a, b = pts[k], pts[k + 1]
        out.append(tuple(a[j] + t * (b[j] - a[j]) for j in range(3)))
    return out


def build():
    for name, pts in shots().items():
        print(name, DURATION_S.get(name, 0), "s")
        for p in pts:
            print("  %.0f, %.0f, %.0f" % p)


if __name__ == "__main__" or any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
