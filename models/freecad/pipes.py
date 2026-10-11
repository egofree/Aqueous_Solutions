#!/usr/bin/env python3
"""Hollow pipes and clean junctions.

MangoJelly, "One FreeCAD Tool Solves a Common Pipe Modeling Problem"
(https://youtu.be/3A2R8FJpspM): a Part Design polar pattern or a boolean
fuse of overlapping pipe solids leaves an internal wall. A section cut
shows it. Part, Join, Connect Shapes splits at the intersection, keeps
the largest piece of each, and adds the crossed volume. The bore stays open.

These headers are straight runs or two-segment corners. A solid cylinder
is the same failure. A pipe is an outer cylinder minus a bore. A corner
is Connect, not fuse.
"""
import FreeCAD as App
import Part

WALL = 4.0  # mm, on an 80 mm header


def tube(od, length, x, y, z, axis="x", wall=WALL):
    """Hollow pipe. Bore is longer than the shell so the cut is clean."""
    outer = Part.makeCylinder(od / 2.0, length)
    bore = Part.makeCylinder(max(od / 2.0 - wall, 1.0), length + 4.0)
    bore.translate(App.Vector(0, 0, -2.0))
    body = outer.cut(bore)
    if axis == "x":
        body.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
    elif axis == "y":
        body.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
    body.translate(App.Vector(x, y, z))
    return body


def connect(doc, name, shapes):
    """Join pipes without an internal wall.

    Prefer Part.Connect. If this FreeCAD build has no Connect object,
    fuse the hollow tubes. The bore is already cut, so the fuse does not
    refill it the way a solid fuse does.
    """
    objs = []
    for i, shape in enumerate(shapes):
        obj = doc.addObject("Part::Feature", "%s_SEG_%d" % (name, i + 1))
        obj.Shape = shape
        objs.append(obj)
    doc.recompute()
    if hasattr(doc, "addObject"):
        try:
            joined = doc.addObject("Part::Connect", name)
            joined.Objects = objs
            doc.recompute()
            return joined
        except (AttributeError, RuntimeError, TypeError):
            pass
    body = shapes[0]
    for shape in shapes[1:]:
        body = body.fuse(shape)
    return _feature(doc, name, body)


def _feature(doc, name, shape):
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj
