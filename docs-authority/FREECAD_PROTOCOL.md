# FreeCAD protocol — Aqueous wet line

For any agent building or editing the 3D model. Read this before touching
`cad/freecad/`. Process authority is `GLOSSARY.md` and
`LOCAL_BOT_HANDOFF.md`. This file is only how to drive FreeCAD 1.0 on the
operator’s box without repeating the failures from 2026-09-26.

Licence: CERN-OHL-S-2.0. No photoreal / diffusion images.

---

## 1. Which binary

The machine has two FreeCAD installs. They are not interchangeable.

| Invoke | What it is | Use |
|---|---|---|
| `/usr/bin/freecadcmd` | apt 1.0.0 console | Run every generator script |
| `/usr/bin/freecad` | apt 1.0.0 GUI | Open `.FCStd` and `.step` |
| `freecad` / `FreeCADCmd` | 1.1.1 AppImage on PATH | Do not use |

Check before you run anything:

```bash
type -a freecad freecadcmd
/usr/bin/freecadcmd --version
```

You want `FreeCAD 1.0.0`. If the banner says `1.1.1` or the path is
`/tmp/.mount_freeca…`, you invoked the AppImage. Stop.

The AppImage loads `~/.local/share/FreeCAD/v1-1/Mod/FreeCAD-Ribbon` and
dies on a missing `RibbonStructure.json`, then SIGSEGV on shutdown. If
someone must use 1.1.1:

```bash
mv ~/.local/share/FreeCAD/v1-1/Mod/FreeCAD-Ribbon \
   ~/.local/share/FreeCAD/v1-1/Mod/FreeCAD-Ribbon.disabled
```

Do not debug the AppImage. Use 1.0.

---

## 2. Working directory and params

```
cad/params.scad              # OpenSCAD millimetres
cad/leach_cstr.scad
cad/ew_cell.scad
cad/assembly_wet.scad
cad/freecad/params.py        # must match params.scad
cad/freecad/leach_cstr.py
cad/freecad/ew_cell.py
cad/freecad/build_wet.py
```

Units are millimetres. Origin is the leach outer SW bottom corner:
+X down the tank, +Y across, +Z up.

A dimension exists in **both** param files. Change both in the same edit.
Do not invent a third params module.

Object names are the locked plant names (underscores instead of spaces /
hyphens where FreeCAD forbids them): `LEACH_CSTR_1`, `EW_1`,
`FLOAT_DEWATER`, `HDR_ACID_GAS`. Do not rename for style.

---

## 3. How to run a script

```bash
cd ~/dev/Aqueous/Diagrams/aqueous_diagrams/cad/freecad
/usr/bin/freecadcmd leach_cstr.py
```

Success looks like:

```
wrote .../leach_cstr.FCStd
wrote .../leach_cstr.step
```

Failure modes already seen:

| Symptom | Cause | Fix |
|---|---|---|
| Banner only, no files | `if __name__ == "__main__"` never fires under `freecadcmd` | Gate on argv (below) |
| `NullShapeException` / `makeShapeWithElementMap` | `makePipe(helix)`, bad loft, or fuse with a null | Discrete boxes / cylinders; never pipe a helix on 1.0 |
| `.FCStd` opens with an empty tree | `Part.show()` did not persist the shape | `Part::Feature` + `obj.Shape = solid` |
| GUI empty but STEP is 40k entities | Looking at the FCStd, not the STEP | Open the `.step`, View → Fit all (`V` `F`) |
| `build_wet` runs for many minutes | Rebuilding the tank (hundreds of paddle fuses) | `App.openDocument("leach_cstr.FCStd")` |
| `freecadcmd: command not found` | Wrong case / PATH | `/usr/bin/freecadcmd` |
| Ribbon `FileNotFoundError` | AppImage + broken addon | `/usr/bin/freecad`, not `freecad` |

Open the check file:

```bash
/usr/bin/freecad leach_cstr.step
```

If the STEP is empty, the script failed before `Part.export`. Read the
console; do not stare at the GUI.

OpenSCAD is the independent check:

```bash
openscad cad/leach_cstr.scad
openscad cad/assembly_wet.scad
```

Keep the two geometries the same topology. OpenSCAD may use `hull` and
`linear_extrude` twists; FreeCAD 1.0 may not. Approximate, do not skip
the part.

---

## 4. Script template

Every new generator in `cad/freecad/` starts from this. Do not “improve”
the entry point.

```python
#!/usr/bin/env python3
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


def cyl(d, h, x, y, z, axis="z"):
    c = Part.makeCylinder(d / 2.0, h)
    if axis == "x":
        c.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
    elif axis == "y":
        c.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), -90)
    c.translate(App.Vector(x, y, z))
    return c


def add(doc, name, shape):
    if shape is None or shape.isNull():
        raise RuntimeError("null shape for %s" % name)
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    return obj


def build():
    doc = App.newDocument("UNIT")
    body = box_at(0, 0, 0, 100, 100, 100)
    add(doc, "UNIT", body)
    doc.recompute()
    doc.saveAs(str(OUT / "unit.FCStd"))
    Part.export([doc.getObject("UNIT")], str(OUT / "unit.step"))
    print("wrote", OUT / "unit.FCStd")


# freecadcmd does not set __name__ == "__main__"
if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
```

Rules inside `build()`:

1. One `Part::Feature` per named plant item. Do not fuse the whole plant
   into one solid.
2. `box_at` and `cyl` only unless you have already tested the alternative
   on `/usr/bin/freecadcmd`. Banned until proven: `makePipe`, `makeHelix`
   + sweep, `makeLoft` of open wires, `Part.show`.
3. Augers, screws, flights: shaft cylinder + discrete paddle boxes, as in
   `helix_flight()` in `leach_cstr.py`.
4. Funnels: already implemented in `ew_cell.make_cell()` with `makeLoft`
   of *closed* polygons. Copy that; do not rewrite it.
5. After `add`, `doc.recompute()`, then `saveAs` **and** `Part.export`
   STEP. The STEP is the integrity check.
6. Assembly scripts load an existing `.FCStd`. They do not call another
   file’s `build()` if that file already wrote a document.

```python
existing = OUT / "leach_cstr.FCStd"
if existing.exists():
    App.openDocument(str(existing))
    doc = App.ActiveDocument
else:
    import leach_cstr as LC
    LC.build()
    doc = App.ActiveDocument
```

7. Print `wrote <path>` so a human (or the next agent) can see success
   without opening the GUI.

---

## 5. What not to model in FreeCAD Part

- Photoreal plant views
- Threads, fasteners, gasket details
- Full cable trays or every instrument
- A second leach tank
- A filter between shredder and CSTR 1
- FR-4 in the induction pyro pipe
- Shared gas headers (dust ≠ acid gas ≠ H₂ ≠ oil vapor)
- Titanium walls (CPVC/PVDF on oxidizer; PP on caustic)

Those belong in the PFD or a later detailed drawing, not this parametric
massing model.

---

## 6. Adding a unit

1. Put dimensions in `cad/params.scad` and `cad/freecad/params.py`.
2. OpenSCAD module in the file that owns the parent (tank extras stay in
   `leach_cstr.scad`; aisle extras stay in `assembly_wet.scad`).
3. Matching `Part::Feature` in the matching `*.py`.
4. Run `/usr/bin/freecadcmd` on that file only.
5. Open the new `.step`. Fit all. Confirm the new body sits on the
   locked face (weir lip, lift outlet, lid slot, EW pitch).
6. Only then instance it from `build_wet.py`.

Build order is positional. Later parts locate off earlier faces. See
Phase A in `LOCAL_BOT_HANDOFF.md`. Do not start Phase C/D solids until
the OIL LINE and GLASS / CERAMIC stubs exist — they do, as of Phase A 6.

---

## 7. Current rebuild sequence

```bash
cd ~/dev/Aqueous/Diagrams/aqueous_diagrams/cad/freecad
/usr/bin/freecadcmd leach_cstr.py    # vessel, feed train, fork stubs
/usr/bin/freecadcmd ew_cell.py       # one funnel cell
/usr/bin/freecadcmd build_wet.py     # load tank, instance EW-1..9, bund,
                                    # pipe, harvest, four headers
/usr/bin/freecad wet_line.FCStd
```

If `leach_cstr.py` errors, fix that before `build_wet.py`. An old
`leach_cstr.FCStd` will be loaded silently and you will think the new
code ran.

---

## 8. When a script throws

1. Copy the `sErrMsg` / `sfunction` line, not the Qt shutdown stack.
2. If it is `Null shape` in `TopoShapeExpansion.cpp`, a boolean got a
   null. Comment out the last `fuse`/`cut` and bisect.
3. Do not switch to the AppImage “to see if 1.1 is better.”
4. Do not replace the weir with a second tank to “simplify.”
5. After a fix, delete the stale `.FCStd` if `openDocument` would hide
   the failure:

```bash
rm -f leach_cstr.FCStd wet_line.FCStd
/usr/bin/freecadcmd leach_cstr.py
```
