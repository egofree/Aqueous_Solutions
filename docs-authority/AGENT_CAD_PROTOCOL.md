# Agent protocol — parametric PFD to CAD

Audience: operators and automation that generate or edit process
drawings and 3D CAD with the user. This file is design-agnostic: do not
assume a plant type, tank size, CAD version, or licence from another
project.

Purpose: move from a process idea to scripted, rebuildable CAD while
avoiding known FreeCAD / OpenSCAD headless failure modes.

---

## 0. Operating rules

1. Confirm names, materials, and dimensions with the user before they
   lock the design. One wrong synonym forks the whole tree.
2. One source of parameters. Every script includes or imports it.
   Changing a length happens in that file only.
3. Scripts generate documents. Do not click-model as the source of
   truth. A `.FCStd` without a generator is a dead end.
4. Headless first. If a feature needs the GUI, write a note and a
   console fallback, then move on.
5. Massing before manufacturing. A correct box in the right place
   beats a detailed part at the wrong origin.
6. Do not use generative image models for plant or machine layouts.
7. Licence every dependency (fonts, kernels, included parts) before
   you add it. Prefer not vendoring binary assets.

---

## 1. Questions to ask the user

Ask in this order. Skip a block only if the answer is already in a
file the user pointed at. Record answers in a short `DECISIONS.md`
(date, decision, source). Do not bury them in chat.

### 1.1 Scope and licence

- What is being designed (one machine, one line, a whole plant)?
- Who owns the design and under what licence must generators and
  models ship?
- Are there documents that already lock names, materials, or
  chemistry? Get paths.
- Metric or inch-pound? Dual units?

### 1.2 Tools

- Path and version of the FreeCAD console binary and of the GUI
  binary. Use those paths for the rest of the session. Do not mix
  installs.
- Is OpenSCAD installed? Path and version.
- May the agent install packages? Which font, if any, is allowed
  for 3D text, and under what licence?
- Working directory for generators and for `.FCStd` / `.step` / `.stl`.

### 1.3 Process (for a PFD)

- Feed, products, and forbidden mixes (streams that must never share
  a header or a vessel).
- Unit operations in order, including forks and recycles.
- What is already decided: vessel type, materials of construction,
  heating method, electrodes, and similar locks.
- Locked unit names. If none, propose a list and wait for approval.
- Heat and gas headers: how many, and may they mix?
- Manual vs automated harvest / change-out.

### 1.4 Geometry and build

- Envelope (building, skid, container) and keep-out zones.
- Which axis is process flow? Which side is the operator aisle?
- What is “done” for this pass: massing PFD-in-3D, or shop-level
  plates and holes?
- Parts that must be OpenSCAD (helices, coils, fine patterned
  plates) vs FreeCAD Part (tanks, aisles, piping runs).

### 1.5 Safety and text

- Signal-word policy (WARNING vs CAUTION vs NOTE).
- May the agent cut text into solids? If yes, which licensed font
  is allowed?
- Where do legends live if the 3D face is blank (a schedule file)?

Stop and ask if any answer would change topology (a second vessel,
a filter the user already forbade, a shared gas header).

---

## 2. Tool facts agents get wrong

### 2.1 FreeCAD console vs GUI

Use the console binary to run generator scripts. Use the GUI binary
to open `.FCStd`, inspect, and capture views. Confirm both paths and
version strings with the user once per session. Do not assume the
command on PATH is the same install as the console.

The FreeCAD console does **not** reliably set
`__name__ == "__main__"`. Gate the entry point on argv:

```python
from pathlib import Path
import sys
if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
```

### 2.2 How to put solids in a document

Use `Part::Feature` and assign `.Shape`. Do not rely on `Part.show()`
as the only registration step — objects can exist in memory and not
in the tree.

```python
obj = doc.addObject("Part::Feature", "LOCKED_NAME")
obj.Shape = shape
doc.recompute()
doc.saveAs(str(path))
```

Object `Name` / `Label` = locked name with `_` for spaces. One object
per piece of equipment.

### 2.3 Kernel landmines (Part / OCC)

- Sweeps and pipes along a helix often return a **null shape**.
  Approximate a screw with a shaft plus discrete paddles, or build
  the helix in OpenSCAD and import a mesh.
- Lofts need closed wires of similar complexity. Prefer boxes,
  cylinders, and cuts for vessels.
- Boolean fuse of hundreds of tiny parts is slow and can fail.
  Fuse in chunks or leave fasteners as separate features.
- `Draft` text tools often want a GUI and a font file. Prefer
  `Part.makeWireString(text, font_path, size_mm, tracking)` then
  `Part.Face` + `extrude`. If no font, leave the plate blank and
  keep legends in a schedule file.
- Headless has no `ViewObject` you can trust. Visibility toggles
  belong in a GUI helper, or rename stand-ins (`MASSING_*`) so a
  human can hide them.

### 2.4 OpenSCAD

- One part per file. Include the shared params file only.
- `$fn` modest unless a bearing journal needs more.
- Export STL or AMF from CLI: `openscad -o out.stl in.scad`.
- OpenSCAD is for detailed parts (flights, coils, flanges). Do not
  rebuild the whole plant in OpenSCAD if FreeCAD already owns the
  assembly.

### 2.5 Importing detail into FreeCAD

STL → `Mesh::Feature`, not a boolean into the parent solid.

```python
import Mesh
m = doc.addObject("Mesh::Feature", "MFG_UNIT")
m.Mesh = Mesh.Mesh(str(stl_path))
m.Placement.Base = App.Vector(x, y, z)
```

If the STL is missing, skip and print the path. Do not crash.
Hide or rename the massing box; do not delete it until the user
says the mesh is the source.

Meshes are display geometry. Making a solid from a mesh is a later,
optional step.

---

## 3. Pipeline

```
decisions and locked names
        ↓
2D PFD (scripted)
        ↓
shared parameters
        ↓
3D massing (FreeCAD Part), positional order
        ↓
detail parts (OpenSCAD) → STL
        ↓
import meshes, hide massing
        ↓
(optional) shop drawings, animation waypoints
```

### 3.1 Locked names and parameters

Create two files before geometry:

- `NAMES.md` or a glossary — every unit, stream, and header, spelled
  once. Drawings and `Part::Feature` names must match.
- `params.py` and/or `params.scad` — one unit system. Same numbers
  in both. Comment the datum (inner floor, aisle centreline).

### 3.2 Scripted PFD

Use a plotting library with a shared draw helper: box, arrow, stream
colour, header. One script per sheet (overview, one unit,
electrical). Fonts large enough that the whole sheet is readable
when zoomed to page width.

PFD rules:

- Flow from a stated direction (top→bottom or left→right). No
  crossed streams unless the crossing is a real header crossing.
- Heat exchangers as cross-links, not as mystery boxes.
- Products and utilities labelled with the locked names.

### 3.3 Massing CAD — positional order

Do not instance a conveyor until the nozzle it aims at exists.

Typical order for a process line:

1. Primary vessel or skid datum.
2. Nozzles and weirs on that vessel.
3. Feed equipment that dumps into those nozzles.
4. Discharge conveyors that start at those nozzles.
5. Downstream units located off the last discharge.
6. Shared aisles, bunds, pipes, headers last among that line.
7. Side branches only after their stubs exist.

One generator per subsystem. An assembly script opens the previous
`.FCStd` and adds objects. Save after each subsystem so a null-shape
failure does not wipe the vessel.

### 3.4 Manufacturing detail

Replace one massing box at a time. A detail file is done when it has
plates or walls, flanges or holes, the drive or coil, and the wetted
material in a comment. It is not a certified fabrication drawing
until the user asks for welds, balloons, and tolerances.

### 3.5 Animation (optional)

Do not start until massing origins are frozen. Publish waypoints
and a shot list. Capture frames from the GUI the user named. Do not
add people, emissions, or mixed headers that the PFD forbids.

---

## 4. Step-by-step session

1. Read this file and any user `DECISIONS.md` / glossary.
2. Ask the §1 questions that are still open. Wait.
3. Write or update `params` and the name list. Stop if names collide.
4. Draw or update the PFD scripts. User reviews names and forks.
5. Build the datum solid (vessel, frame, skid). User opens it in the
   GUI and confirms it is visible (`Part::Feature` in the tree,
   Fit All).
6. Add nozzles. Freeze those faces. Everything else locates off them.
7. Walk the positional list. After each script: console binary,
   check for `NullShapeException`, save.
8. Generate OpenSCAD details for parts the kernel cannot sweep.
9. Export STLs. Import. Hide massing.
10. Sign schedule and (if licensed) face glyphs.
11. Only then: animation, shop packs, or a second line.

If the console reports a null shape, replace the offending sweep
with discrete solids or move that part to OpenSCAD. Do not retry the
same sweep.

If the GUI opens an empty document, the script used `Part.show`
without `Part::Feature`, or a different FreeCAD install opened the
file. Rebuild with the console path the user named.

---

## 5. File layout (suggested)

```
params.py / params.scad
pfd/                  # 2D generators + output png
cad/freecad/          # massing and assembly generators
cad/detail/           # OpenSCAD parts + stl export
DECISIONS.md
NAMES.md
SIGN_SCHEDULE.md      # if signs exist
```

Keep generators next to outputs only if the user wants a
self-contained pack. Do not scatter a second `params.py`.

---

## 6. Definition of done (massing pass)

- Every PFD unit has a `Part::Feature` or a mesh at a documented
  origin.
- Tree names match `NAMES.md`.
- Headers that must stay separate are separate objects.
- Rebuild from the agreed console binary produces the same `.FCStd`.
- No dependency the licence file cannot explain.

---

## 7. What not to do

- Do not “fix” a lock by adding a second tank, a forbidden filter,
  or a shared stack “for simplicity.”
- Do not copy repeated units by hand; instance from one function.
- Do not vendor a font whose licence the user did not accept.
- Do not mix FreeCAD installs in one rebuild.
- Do not treat chat transcripts as the parameter store; use `params` files.
