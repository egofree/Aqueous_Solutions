#!/usr/bin/env python3
"""Process modules on the parametric frame. Run: freecadcmd process_modules.py

Each module is a frame plus the process. Frame parameters come from FRAME_SYSTEM.md.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import frame
import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent


def box(x, y, z, dx, dy, dz):
    s = Part.makeBox(dx, dy, dz)
    s.translate(App.Vector(x, y, z))
    return s


def lathe(doc):
    """300 mm swing, 750 mm centers, on the dry 1200 frame."""
    bay, *_ = frame.frame(1200, 600, 800, 100, 6, "A500")
    bed = box(100, 200, 800, 1000, 200, 80)
    head = box(100, 180, 880, 200, 240, 200)
    tail = box(900, 200, 880, 120, 200, 160)
    body = bay.fuse(bed).fuse(head).fuse(tail)
    obj = doc.addObject("Part::Feature", "LATHE")
    obj.Shape = body
    return obj


def ew_cell(doc, plates=21):
    """Plate rack on the wet frame. 50 mm pitch. Frame length follows the rack."""
    rack = plates * 50 + 200
    L = max(1400, rack + 150)
    bay, *_ = frame.frame(L, 600, 800, 100, 6, "316L")
    tank = box(100, 80, 100, rack, 440, 650)
    body = bay.fuse(tank)
    for i in range(plates):
        body = body.fuse(box(120 + i * 50, 100, 150, 4, 400, 500))
    obj = doc.addObject("Part::Feature", "EW_%d" % plates)
    obj.Shape = body
    print("EW plates", plates, "frame", L)
    return obj


def furnace(doc):
    """10 kW induction. Graphite crucible, 15-turn coil, on the hot frame."""
    bay, *_ = frame.frame(1200, 600, 800, 100, 6, "A500")
    crucible = Part.makeCylinder(100, 250)
    crucible.translate(App.Vector(600, 300, 200))
    coil = Part.makeCylinder(140, 250)
    coil.translate(App.Vector(600, 300, 200))
    bore = Part.makeCylinder(120, 260)
    bore.translate(App.Vector(600, 300, 195))
    coil = coil.cut(bore)
    body = bay.fuse(crucible).fuse(coil)
    obj = doc.addObject("Part::Feature", "FURNACE")
    obj.Shape = body
    return obj


def silicon(doc):
    """Same frame and coil as the furnace. Charge is silica and char."""
    return furnace(doc)


def aligner(doc):
    """Contact aligner. 100 mm stage, on the clean frame."""
    bay, *_ = frame.frame(1200, 600, 800, 80, 5, "6061")
    stage = box(400, 200, 800, 400, 200, 40)
    head = box(450, 180, 900, 300, 240, 200)
    body = bay.fuse(stage).fuse(head)
    obj = doc.addObject("Part::Feature", "ALIGNER")
    obj.Shape = body
    return obj


def electronics(doc):
    """Six clean frames: coat, align, develop, etch, strip, probe."""
    names = ("COAT", "ALIGN", "DEVELOP", "ETCH", "STRIP", "PROBE")
    for i, name in enumerate(names):
        bay, *_ = frame.frame(1200, 600, 800, 80, 5, "6061")
        bay.translate(App.Vector(i * 1400, 0, 0))
        obj = doc.addObject("Part::Feature", "ELEC_" + name)
        obj.Shape = bay
    print("electronics bay 6 x 1400 mm")



def mill(doc):
    """300 x 200 mm table, 1.1 kW, dry frame."""
    bay, *_ = frame.frame(1200, 600, 800, 100, 6, "A500")
    table = box(200, 150, 800, 800, 300, 40)
    column = box(150, 200, 840, 200, 200, 400)
    body = bay.fuse(table).fuse(column)
    obj = doc.addObject("Part::Feature", "MILL")
    obj.Shape = body
    return obj


def welder(doc):
    """200 A, dry frame. Transformer in the base."""
    bay, *_ = frame.frame(800, 600, 800, 100, 6, "A500")
    xfrm = box(150, 150, 100, 500, 300, 400)
    body = bay.fuse(xfrm)
    obj = doc.addObject("Part::Feature", "WELDER")
    obj.Shape = body
    return obj


def farm_bay(doc):
    """Four farm frames: tank, biofilter, biofilter, beds."""
    for i, name in enumerate(("TANK", "BIO_A", "BIO_B", "BEDS")):
        bay, *_ = frame.frame(2000, 1000, 400, 80, 5, "A500")
        bay.translate(App.Vector(i * 2200, 0, 0))
        obj = doc.addObject("Part::Feature", "FARM_" + name)
        obj.Shape = bay
    print("farm bay 4 x 2000 mm")


def cryo_base(doc):
    """Cold-box base. Column is a pipe, not this frame."""
    bay, *_ = frame.frame(600, 600, 800, 80, 5, "316L")
    expander = box(100, 100, 800, 400, 400, 300)
    body = bay.fuse(expander)
    obj = doc.addObject("Part::Feature", "CRYO_BASE")
    obj.Shape = body
    return obj

def main():
    doc = App.newDocument("process")
    lathe(doc)
    mill(doc)
    welder(doc)
    ew_cell(doc, 21)
    furnace(doc)
    aligner(doc)
    electronics(doc)
    farm_bay(doc)
    cryo_base(doc)
    doc.recompute()
    doc.saveAs(str(OUT / "process_modules.FCStd"))
    print("wrote", OUT / "process_modules.FCStd")


if __name__ == "__main__":
    main()
