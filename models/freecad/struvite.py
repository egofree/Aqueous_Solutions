#!/usr/bin/env python3
"""Struvite settler. Run with FreeCAD: freecadcmd struvite.py"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import FreeCAD as App
import Part

doc = App.newDocument("struvite")
tank = Part.makeBox(1000, 1000, 1200)
cone = Part.makeCone(400, 50, 400)
cone.translate(App.Vector(500, 500, 0))
body = tank.fuse(cone)
obj = doc.addObject("Part::Feature", "STRUVITE")
obj.Shape = body
doc.recompute()
out = Path(__file__).resolve().parent / "struvite.FCStd"
doc.saveAs(str(out))
Part.export([obj], str(out.with_suffix(".step")))
print("wrote", out)
