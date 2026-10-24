# Scripted CAD protocol: from process flow diagram to rebuildable models

Document number: AQS-CAD-001  
Revision: B  
Date: 2026-10-24

| Rev | Description | Date |
|---|---|---|
| A | First issue, as an assistant protocol | 2026-10-01 |
| B | Rewritten for contributors to DOC_STYLE (AQS-DOC-002); renamed from AGENT_CAD_PROTOCOL.md; technical content unchanged | 2026-10-24 |

## 1. Purpose and scope

This protocol describes how to turn a process design into scripted, rebuildable computer-aided design (CAD) models without falling into the known failure modes of FreeCAD and OpenSCAD run without a graphical interface. It applies to anyone, person or script, who writes process flow diagram (PFD) generators or CAD generators for this repository.

The protocol does not assume a plant type, vessel size, CAD version or licence. The plant-specific CAD rules are in `docs-authority/FREECAD_PROTOCOL.md` and `docs-authority/BUILD_3D_FROM_FLOW.md`.

Terms used here:

- **Massing model:** a simple solid (usually a box or cylinder) that holds a unit's place and size before it is detailed.
- **Locked name:** the one agreed spelling of a unit, stream or header, used on every drawing and in every model.
- **Console binary:** the FreeCAD command-line program (`freecadcmd`), as distinct from the graphical program.

## 2. Rules

1. Agree names, materials and dimensions with the design owner before they are fixed. One wrong synonym splits the model tree.
2. Keep one source of parameters. Every script includes or imports it, and a length is changed in that file only.
3. Scripts generate the models and documents. Do not model by hand as the source; a `.FCStd` file without a generator cannot be rebuilt.
4. Work without the graphical interface first. If a feature needs it, record that in a note, provide a console fallback and continue.
5. Build massing before manufacturing detail. A correct box in the right place is worth more than a detailed part at the wrong origin.
6. Do not use generative image models for plant or machine layouts.
7. Check the licence of every dependency (fonts, geometry kernels, included parts) before adding it. Avoid committing binary assets from other projects.

## 3. Questions to settle before modelling

Settle these in order, and record each answer in a short `DECISIONS.md` (date, decision, source). Skip a question only if a referenced file already answers it.

Stop and ask the design owner if an answer would change the topology, for example a second vessel, a filter that was ruled out, or a shared gas header.

### 3.1 Scope and licence

- What is being designed: one machine, one line or a whole plant?
- Who owns the design, and under what licence will generators and models be published?
- Which documents already fix names, materials or chemistry? Record their paths.
- Metric, inch-pound or both?

### 3.2 Tools

- The path and version of the FreeCAD console binary and of the graphical program. Use those paths throughout and do not mix installations.
- Whether OpenSCAD is installed, with its path and version.
- Whether packages may be installed, and which font, under which licence, may be used for 3D text.
- The working folder for generators and for `.FCStd`, `.step` and `.stl` files.

### 3.3 Process

- Feeds, products and forbidden mixes: streams that must never share a header or a vessel.
- Unit operations in order, including branches and recycles.
- What is already decided: vessel type, materials of construction, heating method, electrodes and similar.
- The locked unit names. If there are none, propose a list and have it approved.
- The heat and gas headers, and whether any may be combined.
- Whether harvest and change-out are manual or automated.

### 3.4 Geometry and build

- The envelope (building, skid or container) and keep-out zones.
- Which axis is the process flow direction, and which side is the operator aisle.
- What this pass must deliver: massing only, or shop-level plates and holes.
- Which parts must be built in OpenSCAD (helices, coils, finely patterned plates) and which in FreeCAD Part (tanks, aisles, pipe runs).

### 3.5 Safety and text

- The signal-word policy (WARNING, CAUTION, NOTE; see DOC_STYLE section 13).
- Whether text may be cut into solids, and with which licensed font.
- Where legends are kept if a 3D face is left blank (a schedule file).

## 4. Tool behaviour that causes errors

### 4.1 FreeCAD console and graphical program

Run generator scripts with the console binary. Use the graphical program to open `.FCStd` files, inspect them and capture views. Confirm both paths and versions before starting; the `freecad` command on the path may not be the same installation as the console.

The FreeCAD console does not reliably set `__name__ == "__main__"`. Gate the entry point on the arguments instead:

```python
from pathlib import Path
import sys
if any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
```

### 4.2 Adding solids to a document

Use `Part::Feature` and assign its `.Shape`. Do not rely on `Part.show()` alone: objects can exist in memory without appearing in the document tree.

```python
obj = doc.addObject("Part::Feature", "LOCKED_NAME")
obj.Shape = shape
doc.recompute()
doc.saveAs(str(path))
```

Set the object `Name` and `Label` to the locked name, with underscores for spaces. Use one object per item of equipment.

### 4.3 Geometry kernel limitations (Part and Open CASCADE)

- Sweeps and pipes along a helix often return a null shape. Approximate a screw with a shaft and discrete paddles, or build the helix in OpenSCAD and import a mesh.
- Lofts need closed wires of similar complexity. Build vessels from boxes, cylinders and cuts.
- A Boolean fuse of hundreds of small parts is slow and can fail. Fuse in groups, or keep fasteners as separate features.
- Draft text tools often need the graphical program and a font file. Use `Part.makeWireString(text, font_path, size_mm, tracking)`, then `Part.Face` and an extrusion. If no font is available, leave the plate blank and keep the legend in a schedule file.
- Without the graphical program, `ViewObject` cannot be relied on. Put visibility changes in a separate helper for the graphical program, or name stand-ins `MASSING_*` so a reader can hide them.

### 4.4 OpenSCAD

- One part per file. Include only the shared parameter file.
- Keep `$fn` modest unless a bearing journal needs more facets.
- Export from the command line: `openscad -o out.stl in.scad`.
- Use OpenSCAD for detailed parts (flights, coils, flanges). Do not rebuild the whole plant in OpenSCAD when FreeCAD holds the assembly.

### 4.5 Importing detail into FreeCAD

Import an STL as a `Mesh::Feature`, not as a Boolean into the parent solid:

```python
import Mesh
m = doc.addObject("Mesh::Feature", "MFG_UNIT")
m.Mesh = Mesh.Mesh(str(stl_path))
m.Placement.Base = App.Vector(x, y, z)
```

If the STL file is missing, print its path and continue. Hide or rename the massing box, but do not delete it until the design owner accepts the mesh as the source. Meshes are display geometry; converting a mesh to a solid is a later, optional step.

## 5. Pipeline

Figure 5.1 shows the order of work.

```
decisions and locked names
        ↓
scripted 2D PFD
        ↓
shared parameters
        ↓
3D massing (FreeCAD Part), in positional order
        ↓
detail parts (OpenSCAD) → STL
        ↓
import meshes, hide massing
        ↓
(optional) shop drawings, animation waypoints
```

Figure 5.1. From decisions to models

### 5.1 Locked names and parameters

Create two files before any geometry:

- `NAMES.md` or a glossary, in which every unit, stream and header is spelled once. Drawings and `Part::Feature` names must match it.
- `params.py`, `params.scad` or both, in one unit system with the same numbers in each. State the datum in a comment (for example the inner floor or the aisle centreline).

### 5.2 Scripted PFD

Use a plotting library with a shared drawing helper for boxes, arrows, stream colours and headers. Write one script per sheet (overview, single unit, electrical). Make the text large enough that the whole sheet is readable at page width.

- Draw flow in one stated direction (top to bottom or left to right). Do not cross streams unless the crossing is a real header crossing.
- Draw heat exchangers as links between the two streams, not as unlabelled boxes.
- Label products and utilities with their locked names.

### 5.3 Massing in positional order

Do not place a conveyor until the nozzle it serves exists. A typical order for a process line is:

1. The primary vessel or skid datum.
2. Nozzles and weirs on that vessel.
3. Feed equipment that discharges into those nozzles.
4. Discharge conveyors that start at those nozzles.
5. Downstream units, located from the last discharge.
6. Shared aisles, bunds, pipes and headers, last for that line.
7. Side branches, only after their stubs exist.

Write one generator per subsystem. An assembly script opens the previous `.FCStd` file and adds objects. Save after each subsystem, so that a null-shape failure does not lose the vessel.

### 5.4 Manufacturing detail

Replace one massing box at a time. A detail file is complete when it has plates or walls, flanges or holes, the drive or coil, and the wetted material stated in a comment. It is not a fabrication drawing until welds, balloons and tolerances are added at the design owner's request.

### 5.5 Animation (optional)

Do not start until the massing origins are fixed. Publish the waypoints and a shot list, and capture frames from the agreed graphical program. Do not show people, emissions or mixed headers that the PFD does not allow.

## 6. Procedure

1. Read this protocol and any `DECISIONS.md` and glossary for the work.
2. Settle the questions of section 3 that are still open.
3. Write or update the parameter files and the name list. Stop if two names collide.
4. Write or update the PFD scripts, and have the names and branches reviewed.
5. Build the datum solid (vessel, frame or skid). Open it in the graphical program and confirm that it appears in the tree as a `Part::Feature` and is visible with Fit All.
6. Add the nozzles and fix those faces. Everything else is located from them.
7. Work through the positional order. After each script, run it with the console binary, check for `NullShapeException` and save.
8. Generate OpenSCAD detail for parts the kernel cannot sweep.
9. Export the STL files, import them and hide the massing.
10. Complete the sign schedule and, where a licensed font is available, the face text.
11. Only then start animation, shop packs or a second line.

If the console reports a null shape, replace the failing sweep with discrete solids or move the part to OpenSCAD; repeating the same sweep will fail again. If the graphical program opens an empty document, either the script used `Part.show` without `Part::Feature`, or a different FreeCAD installation opened the file. Rebuild with the agreed console binary.

## 7. Suggested file layout

```
params.py / params.scad
pfd/                      2D generators and output images
models/freecad/           massing and assembly generators
models/openscad/detail/   OpenSCAD parts and STL export
DECISIONS.md
NAMES.md
SIGN_SCHEDULE.md          if there are signs
```

Keep generators next to their outputs only when a self-contained pack is wanted. Do not create a second `params.py`.

## 8. Completion criteria for a massing pass

- Every PFD unit has a `Part::Feature` or a mesh at a documented origin.
- Names in the model tree match `NAMES.md`.
- Headers that must stay separate are separate objects.
- A rebuild with the agreed console binary produces the same `.FCStd` file.
- Every dependency is covered by the licence file.

## 9. Practices to avoid

- Working around a fixed decision by adding a second tank, a ruled-out filter or a shared stack "for simplicity".
- Copying repeated units by hand instead of creating them from one function.
- Committing a font whose licence has not been accepted.
- Mixing FreeCAD installations in one rebuild.
- Keeping parameters anywhere other than the parameter files.
