# SPDX-License-Identifier: CERN-OHL-S-2.0
# Instances EW-3..EW-8 from the existing EW cell. Does not open plant.FCStd.
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
import FreeCAD as App
import Part

OUT = Path(__file__).resolve().parent

def build():
    doc = App.newDocument("EW_CASCADE")
    for i, tag in enumerate(P.EW_TAGS):
        # EW_TAGS is EW-1..EW-9. Local aisle frame. build_plant applies PROCESS_DX/DY.
        x = P.AISLE_X0 + i * P.EW_PITCH
        name = tag.replace("-", "_")
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = Part.makeBox(P.EW_L, P.EW_W, P.EW_H)
        obj.Placement = App.Placement(App.Vector(x, P.AISLE_Y, P.AISLE_Z), App.Rotation())
    doc.recompute()
    doc.saveAs(str(OUT / "ew_cascade.FCStd"))
    print("wrote", OUT / "ew_cascade.FCStd")

if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
