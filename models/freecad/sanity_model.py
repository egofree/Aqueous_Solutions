# SPDX-License-Identifier: CERN-OHL-S-2.0
# Read-only. Opens ew_cascade.FCStd and plant_placed.FCStd. Does not open plant.FCStd.
import FreeCAD as App
from pathlib import Path

here = Path(__file__).resolve().parent

def report_cascade():
    doc = App.openDocument(str(here / "ew_cascade.FCStd"))
    xs = []
    for i in range(1, 10):
        obj = doc.getObject(f"EW_{i}")
        if obj is None:
            print("MISSING", f"EW_{i}")
            continue
        b = obj.Shape.BoundBox
        xs.append(obj.Placement.Base.x)
        print(f"EW_{i} origin {obj.Placement.Base.x:.0f} {obj.Placement.Base.y:.0f} {obj.Placement.Base.z:.0f} size {b.XLength:.0f}x{b.YLength:.0f}x{b.ZLength:.0f}")
    pitches = [round(xs[i+1] - xs[i], 1) for i in range(len(xs)-1)]
    print("pitches", pitches)
    print("pitch_ok", pitches == [750.0] * 8)
    App.closeDocument(doc.Name)

def report_copy():
    doc = App.openDocument(str(here / "plant_placed.FCStd"))
    want = {
        "BACKUP_GEN": (2000, 1000, 1600),
        "FUEL_CELL": (1800, 800, 1600),
        "MEOH_FERM": (2200, 900, 1400),
        "MEOH_SYNTH": (2200, 900, 1400),
        "MEOH_TANK": (800, 800, 1100),
        "MEOH_FC": (1800, 800, 1600),
    }
    boxes = []
    for name, expect in want.items():
        obj = doc.getObject(name)
        if obj is None:
            print("MISSING", name)
            continue
        b = obj.Shape.BoundBox
        size = (round(b.XLength), round(b.YLength), round(b.ZLength))
        print(name, "bound", size, "expect", expect, "match", size == expect)
        boxes.append((name, b))
    hits = []
    for i in range(len(boxes)):
        for j in range(i+1, len(boxes)):
            a, b = boxes[i][1], boxes[j][1]
            if a.intersect(b):
                hits.append((boxes[i][0], boxes[j][0]))
    print("issued_skid_overlaps", hits)
    App.closeDocument(doc.Name)

report_cascade()
report_copy()
