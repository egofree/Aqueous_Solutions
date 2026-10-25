# Running FreeCAD for the wet-line model

Document number: AQS-CAD-002  
Revision: B  
Date: 2026-10-24  
Licence: CERN-OHL-S-2.0  
Basis: process names and equipment from `docs-authority/GLOSSARY.md` and the equipment and process pages in `docs-authority/`.

| Rev | Description | Date |
|---|---|---|
| A | Issued without a revision table | — |
| B | Rewritten to DOC_STYLE (AQS-DOC-002) for a contributor new to the project: purpose and scope, terms, captions; sections renumbered; a stale note on Phase C and D stubs removed (the stubs exist). Rules and commands unchanged. | 2026-10-24 |

## 1. Purpose and scope

This page tells a contributor how to run FreeCAD 1.0 to build or edit the 3D model of the wet line in `models/freecad/`, and how to avoid failures already met on the build host (first recorded on 2026-09-26). Read it before changing anything in `models/freecad/`.

It covers the FreeCAD program to use, the files and parameters, how to run and check a script, the script template, what not to model, how to add a unit, the rebuild sequence and what to do when a script fails. It does not define the process: process names and equipment come from the glossary and the equipment pages. Photorealistic or AI-generated images are not part of the model.

## 2. Terms

- `freecadcmd`: the FreeCAD console program, which runs a Python script without the graphical interface.
- AppImage: a self-contained Linux package of a program. Here, the FreeCAD 1.1.1 AppImage, which must not be used.
- `.FCStd`: the FreeCAD document format. STEP (`.step`): the ISO 10303 exchange format for 3D solids, used here as the integrity check.
- `Part::Feature`: a FreeCAD object that stores one solid shape.
- Massing model: the overall boxes and cylinders of the equipment, placed and sized correctly, without fine detail.
- Generator script: a Python file in `models/freecad/` that builds part of the model and writes `.FCStd` and `.step` files.

## 3. Which FreeCAD to use

The build host has two FreeCAD installs, and they are not interchangeable (Table 3.1).

Table 3.1. FreeCAD installs

| Invoke | What it is | Use |
|---|---|---|
| `/usr/bin/freecadcmd` | apt 1.0.0 console | Run every generator script |
| `/usr/bin/freecad` | apt 1.0.0 GUI | Open `.FCStd` and `.step` |
| `freecad` / `FreeCADCmd` | 1.1.1 AppImage on PATH | Do not use |

Check before running anything:

```bash
type -a freecad freecadcmd
/usr/bin/freecadcmd --version
```

The version shown should be `FreeCAD 1.0.0`. If it says `1.1.1`, or the path begins `/tmp/.mount_freeca…`, the AppImage was started instead. Stop.

The AppImage loads `~/.local/share/FreeCAD/v1-1/Mod/FreeCAD-Ribbon`, fails on a missing `RibbonStructure.json`, and then crashes (SIGSEGV) on shutdown. If 1.1.1 must be used, disable that add-on:

```bash
mv ~/.local/share/FreeCAD/v1-1/Mod/FreeCAD-Ribbon \
   ~/.local/share/FreeCAD/v1-1/Mod/FreeCAD-Ribbon.disabled
```

Do not debug the AppImage. Use 1.0.

## 4. Files and parameters

Figure 4.1 lists the model files.

Figure 4.1. Model files

```
models/openscad/params.scad              # OpenSCAD millimetres
models/openscad/leach_cstr.scad
models/openscad/ew_cell.scad
models/openscad/assembly_wet.scad
models/freecad/params.py        # must match params.scad
models/freecad/leach_cstr.py
models/freecad/ew_cell.py
models/freecad/build_wet.py
```

Units are millimetres. The origin is the bottom corner of the leach tank on its outer south-west side: +X runs along the tank, +Y across it, and +Z up.

Every dimension is in both parameter files. Change both in the same edit, and do not add a third parameter module.

Object names are the locked plant names, with underscores where FreeCAD does not allow spaces or hyphens: `LEACH_CSTR_1`, `EW_1`, `FLOAT_DEWATER`, `HDR_ACID_GAS`. Do not rename them for style.

## 5. Running a script

Run a generator script from `models/freecad/`:

```bash
cd models/freecad
/usr/bin/freecadcmd leach_cstr.py
```

A successful run prints:

```
wrote .../leach_cstr.FCStd
wrote .../leach_cstr.step
```

Table 5.1 lists failures already seen and their fixes.

Table 5.1. Known failures

| Symptom | Cause | Fix |
|---|---|---|
| Banner only, no files | `if __name__ == "__main__"` never fires under `freecadcmd` | Gate on argv (below) |
| `NullShapeException` / `makeShapeWithElementMap` | `makePipe(helix)`, bad loft, or fuse with a null | Discrete boxes / cylinders; never pipe a helix on 1.0 |
| `.FCStd` opens with an empty tree | `Part.show()` did not persist the shape | `Part::Feature` + `obj.Shape = solid` |
| GUI empty but STEP is 40k entities | Looking at the FCStd, not the STEP | Open the `.step`, View → Fit all (`V` `F`) |
| `build_wet` runs for many minutes | Rebuilding the tank (hundreds of paddle fuses) | `App.openDocument("leach_cstr.FCStd")` |
| `freecadcmd: command not found` | Wrong case / PATH | `/usr/bin/freecadcmd` |
| Ribbon `FileNotFoundError` | AppImage + broken addon | `/usr/bin/freecad`, not `freecad` |

Open the STEP file to check the result:

```bash
/usr/bin/freecad leach_cstr.step
```

If the STEP file is empty, the script failed before `Part.export`. Read the console output rather than the graphical interface.

OpenSCAD is the independent check:

```bash
openscad models/openscad/leach_cstr.scad
openscad models/openscad/assembly_wet.scad
```

Keep the two geometries topologically the same. OpenSCAD may use `hull` and twisted `linear_extrude`; FreeCAD 1.0 may not. Approximate the part rather than leave it out.

## 6. Script template

Every new generator script in `models/freecad/` starts from Figure 6.1. Do not change its entry point.

Figure 6.1. Generator script template

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

1. One `Part::Feature` per named plant item. Do not fuse the whole plant into one solid.
2. Use only `box_at` and `cyl` unless an alternative has already been tested with `/usr/bin/freecadcmd`. Not allowed until proven: `makePipe`, `makeHelix` with a sweep, `makeLoft` of open wires, and `Part.show`.
3. Augers, screws and flights: a shaft cylinder with separate paddle boxes, as in `helix_flight()` in `leach_cstr.py`.
4. Funnels: already implemented in `ew_cell.make_cell()` with `makeLoft` of closed polygons. Copy that; do not rewrite it.
5. After adding objects, call `doc.recompute()`, then both `saveAs` and `Part.export` to STEP. The STEP file is the integrity check.
6. Assembly scripts load an existing `.FCStd`. They do not call another file's `build()` if that file has already written a document (Figure 6.2).

Figure 6.2. Loading an existing document

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

7. Print `wrote <path>`, so that success is visible without opening the graphical interface.

## 7. What not to model in FreeCAD Part

- Photorealistic plant views.
- Threads, fasteners and gasket details.
- Full cable trays, or every instrument.
- A second leach tank.
- A filter between the shredder and CSTR 1.
- FR-4 in the induction pyrolysis pipe.
- Shared gas headers: dust, acid gas, hydrogen and oil vapour stay in separate headers.
- Titanium walls: CPVC or PVDF on oxidiser service, PP on caustic service.

These belong on the process flow diagram or a later detailed drawing, not in this parametric massing model.

## 8. Adding a unit

1. Put the dimensions in `models/openscad/params.scad` and `models/freecad/params.py`.
2. Add the OpenSCAD module to the file that owns the parent: tank extras stay in `leach_cstr.scad`, aisle extras in `assembly_wet.scad`.
3. Add the matching `Part::Feature` in the matching `*.py` file.
4. Run `/usr/bin/freecadcmd` on that file only.
5. Open the new `.step` file and fit all. Confirm the new body sits on the locked face (weir lip, lift outlet, lid slot, electrowinning cell pitch).
6. Only then add it to `build_wet.py`.

Build order matters: later parts are located from faces of earlier ones (§9).

## 9. Rebuild sequence

Figure 9.1. Rebuild sequence

```bash
cd models/freecad
/usr/bin/freecadcmd leach_cstr.py    # vessel, feed train, fork stubs
/usr/bin/freecadcmd ew_cell.py       # one funnel cell
/usr/bin/freecadcmd build_wet.py     # load tank, instance EW-1..9, bund,
                                    # pipe, harvest, four headers
/usr/bin/freecad wet_line.FCStd
```

If `leach_cstr.py` fails, fix it before running `build_wet.py`. Otherwise an old `leach_cstr.FCStd` is loaded without warning and the new code appears to have run.

## 10. When a script fails

1. Copy the `sErrMsg` or `sfunction` line, not the Qt shutdown stack.
2. A `Null shape` error in `TopoShapeExpansion.cpp` means a Boolean operation received a null shape. Comment out the last `fuse` or `cut` and bisect.
3. Do not switch to the AppImage to see whether 1.1 behaves better.
4. Do not replace the weir with a second tank to simplify the model.
5. After a fix, delete the stale `.FCStd` if `openDocument` would hide the failure (Figure 10.1).

Figure 10.1. Clearing stale documents

```bash
rm -f leach_cstr.FCStd wet_line.FCStd
/usr/bin/freecadcmd leach_cstr.py
```
