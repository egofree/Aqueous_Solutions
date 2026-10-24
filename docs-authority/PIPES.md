# Pipe junctions

Document number: AQS-PIP-006  

The FreeCAD failure is an internal wall. A polar pattern or a boolean fuse of overlapping pipe solids leaves a face across the bore. A section cut shows it. The video is MangoJelly, "One FreeCAD Tool Solves a Common Pipe Modeling Problem," https://youtu.be/3A2R8FJpspM. The fix shown is Part, Join, Connect Shapes, not a fuse.

Our headers were solid cylinders. `LEACHATE_TO_EW1` was `p1.fuse(p2).fuse(p3)`. `OVF_EW_9_POLISH` was `seg_x.fuse(seg_y)`. Both are the failure.

`models/freecad/pipes.py` makes a hollow tube, 4 mm wall, and joins with `Part::Connect`. If this FreeCAD build has no Connect object, it fuses the hollow tubes. The bore is already cut, so that fuse does not refill it.

Straight headers in `pipe_services.py` use the same hollow tube. A solid cylinder is not a pipe.
