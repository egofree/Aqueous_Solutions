# SPDX-License-Identifier: CERN-OHL-S-2.0
# Instances EW-1..EW-9 and the overflow into POLISH_BANK.
# Does not open plant.FCStd. Local aisle frame. build_plant applies PROCESS_DX/DY.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent


def _cyl(d, h, x, y, z, axis="z"):
    c = Part.makeCylinder(d / 2.0, h)
    if axis == "x":
        c.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
    elif axis == "y":
        c.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
    c.translate(App.Vector(x, y, z))
    return c


def build():
    doc = App.newDocument("EW_CASCADE")
    pitch = []
    for i, tag in enumerate(P.EW_TAGS):
        # EW_TAGS is EW-1..EW-9. Origin pitch is params.EW_PITCH (750 mm).
        x = P.AISLE_X0 + i * P.EW_PITCH
        name = tag.replace("-", "_")
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = Part.makeBox(P.EW_L, P.EW_W, P.EW_H)
        obj.Placement = App.Placement(App.Vector(x, P.AISLE_Y, P.AISLE_Z), App.Rotation())
        pitch.append((name, x, P.AISLE_Y, P.AISLE_Z))

    # Overflow launder. Diameter is the existing liquor line (PUMP_D),
    # the same class as LEACHATE_TO_EW1. Not a new size.
    y_c = P.AISLE_Y + P.EW_W / 2.0
    z_c = P.AISLE_Z + P.EW_H - P.PUMP_D / 2.0
    hops = []
    # Seat each launder WALL mm into the upstream and downstream cell
    # so the solid intersection is a volume, not a shared face.
    seat = P.WALL
    for i in range(8):
        x0 = P.AISLE_X0 + i * P.EW_PITCH + P.EW_L - seat
        length = P.EW_PITCH - P.EW_L + 2 * seat
        name = "OVF_EW_%d_%d" % (i + 1, i + 2)
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = _cyl(P.PUMP_D, length, x0, y_c, z_c, axis="x")
        hops.append(name)

    # IA-EW-09: EW-9 tail to POLISH_BANK. Bank origin matches wet_products.precip_x0 / pk_y.
    px = P.AISLE_X0 + 9 * P.EW_PITCH + 400
    pk_y = P.AISLE_Y - (P.EW_W + 2 * P.WALL) - 800
    polish = doc.addObject("Part::Feature", "POLISH_BANK")
    polish.Shape = Part.makeBox(P.EW_L, P.EW_W, P.EW_H)
    polish.Placement = App.Placement(App.Vector(px, pk_y, P.AISLE_Z), App.Rotation())

    x9 = P.AISLE_X0 + 8 * P.EW_PITCH + P.EW_L - seat
    run_x = px - x9
    pk_yc = pk_y + P.EW_W / 2.0
    import pipes
    seg_x = pipes.tube(P.PUMP_D, run_x, x9, y_c, z_c, axis="x")
    seg_y = pipes.tube(P.PUMP_D, y_c - pk_yc, px, pk_yc, z_c, axis="y")
    pipes.connect(doc, "OVF_EW_9_POLISH", [seg_x, seg_y])

    doc.recompute()
    doc.saveAs(str(OUT / "ew_cascade.FCStd"))
    print("wrote", OUT / "ew_cascade.FCStd")
    export_step(doc)
    print("PITCH", pitch)
    print("HOPS", hops)
    print("POLISH", px, pk_y, P.AISLE_Z)
    print("TAIL", x9, run_x, y_c, pk_yc, z_c)


STEP_DESC = "EW-1 through EW-9, OVF_EW_1_2 through OVF_EW_8_9, POLISH_BANK, OVF_EW_9_POLISH"
STEP_DATE = "2026-10-07"


def export_step(doc):
    # Same objects as the FCStd. Header is rewritten so no host path is published.
    import re
    import Import
    step = OUT / "ew_cascade.step"
    objs = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
    Import.export(objs, str(step))
    txt = step.read_text()
    txt = re.sub(r"FILE_DESCRIPTION\(\(.*?\),'2;1'\);",
                 "FILE_DESCRIPTION(('%s'),'2;1');" % STEP_DESC, txt, count=1, flags=re.S)
    txt = re.sub(r"FILE_NAME\(.*?\);\n",
                 "FILE_NAME('ew_cascade.step','%s',('Aqueous'),(''),'','','');\n" % STEP_DATE,
                 txt, count=1, flags=re.S)
    step.write_text(txt)
    print("wrote", step, len(objs), "solids")


if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
