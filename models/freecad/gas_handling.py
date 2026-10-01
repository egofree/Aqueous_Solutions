#!/usr/bin/env python3
"""Phase C: equipment on the four headers. Br2 scrubber stays on the battery."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
from labels import add, box_at, label_plate, sign
import oil_line
import glass_line

import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent


def cyl(d, h, x, y, z, axis="z"):
    c = Part.makeCylinder(d / 2.0, h)
    if axis == "x":
        c.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
    elif axis == "y":
        c.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
    c.translate(App.Vector(x, y, z))
    return c


def attach(doc):
    t = P.WALL
    # acid-gas train off the CSTR lid takeoff, +Y of tank near BMED
    ax = t + P.CSTR_L * 0.80
    ay = P.CSTR_W + 2 * t + 200
    add(doc, "DEMISTER", box_at(ax, ay, 800, 600, 500, 700))
    add(doc, "ALK_SCRUBBER", box_at(ax + 700, ay, 0, 700, 700, 1800))
    # ACID_POLISH post-alkali pack (AQS-VENT-001 / AQS-EQP-VENT-001)
    add(doc, "ACID_POLISH_SCRUB", box_at(ax + 1450, ay, 0, 600, 600, 1200))
    add(doc, "FAN_STACK", cyl(360, 12000, ax + 2200, ay + 350, 0))
    label_plate(doc, "DEMISTER", ax, ay - 200)
    label_plate(doc, "ALK_SCRUBBER", ax + 700, ay - 200)
    label_plate(doc, "ACID_POLISH_SCRUB", ax + 1450, ay - 200)
    label_plate(doc, "FAN_STACK", ax + 2100, ay - 200)
    # pregnant scrubber liquor to CRU (not sewer)
    add(doc, "SCRUBBER_TO_CRU", cyl(P.PUMP_D, 800, ax + 700, ay + 700, 200, axis="y"))
    add(doc, "ACID_POLISH_REGEN", box_at(ax + 1450, ay + 700, 0, 500, 500, 900))
    label_plate(doc, "ACID_POLISH_REGEN", ax + 1450, ay + 900)

    # dust baghouse at hopper
    add(doc, "BAGHOUSE", box_at(-P.MEZZ_L - 200, t + P.CSTR_W + 200, P.MEZZ_H,
                                800, 800, 1600))
    label_plate(doc, "BAGHOUSE", -P.MEZZ_L - 200, t + P.CSTR_W + 40)
    add(doc, "FINES_TO_CSTR", cyl(P.DUST_D, 900, -200, t + P.CSTR_W / 2, P.MEZZ_H, axis="x"))

    # H2 dryer on cathode side of EW aisle — not tied to oil vapor
    hx = P.AISLE_X0 + 9 * P.EW_PITCH + 200
    hy = P.AISLE_Y + P.EW_W + 2 * t + 200
    add(doc, "H2_DRYER", box_at(hx, hy, 400, 700, 500, 900))
    add(doc, "H2_STACK", cyl(250, 8000, hx + 900, hy + 250, 0))
    label_plate(doc, "H2_DRYER", hx, hy - 200)
    # Target is H2_DRYER massing (legend unit name DRYER)
    h2_to = (hx + 350, hy + 250, 400 + 450)
    sign(doc, "SIGN_H2_DRYER", hx, hy - 700, to=h2_to)

    # HVAC condensate / Q4 to SALT FEED
    add(doc, "HVAC_Q4", box_at(200, P.CSTR_W + 2 * t + P.BMED_W + 700, 0, 500, 500, 700))
    label_plate(doc, "HVAC_Q4", 200, P.CSTR_W + 2 * t + P.BMED_W + 500)

    # flue jacket AFTERBURNER → BURNOUT ROTARY, atmospheres isolated
    ox, oy, _ = oil_line.origin()
    gx, gy, _ = glass_line.origin()
    ab_x = ox + P.DRYER_L + 80 + P.PYRO_L + 80 + 900 + 1200
    rot_x = gx + P.RINSE_L + 80
    mid_y = (oy + gy) / 2.0
    jacket = cyl(180, max(200, abs(rot_x - ab_x)), min(ab_x, rot_x), mid_y, 1800, axis="x")
    add(doc, "HX7_FLUE_JACKET", jacket)
    label_plate(doc, "HX7_FLUE_JACKET", min(ab_x, rot_x), mid_y - 200, z=2000)


def build():
    doc = App.newDocument("GAS_HANDLING")
    attach(doc)
    doc.recompute()
    doc.saveAs(str(OUT / "gas_handling.FCStd"))
    print("wrote", OUT / "gas_handling.FCStd")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
