# Software for 3D models and diagrams

Document number: AQS-3D-STACK-001  
Revision: B  
Date: 2026-10-24  
Licence: CERN-OHL-S-2.0  
Basis: project decision of 2026-10-01 (record the decision before changing the software used to go from the graph to 3D); consistent with `DESIGN_TOOL_ARCHITECTURE.md` (AQS-UI-001) §3.3 and the unpublished planning note STACK_REEVAL_2026-10-01.  
Audience: contributors choosing software for the plant's 3D models and 2D diagrams.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | First issue | FreeCAD default; Three.js gated; matplotlib optional | 2026-10-01 |
| B | Plain language | Rewritten to DOC_STYLE (AQS-DOC-002) for a reader new to the project: purpose and scope merged into §1, terms in §2, captions. Decision unchanged. | 2026-10-24 |

## 1. Purpose and scope

This page is the written decision on which software produces the plant's 3D models and secondary diagrams, and how each relates to the typed plant graph and to the FreeCAD rebuild. It answers two questions: whether Three.js is in scope (not yet), and whether the matplotlib images are authoritative (they are not).

Table 1.1. Scope

| In | Out |
|---|---|
| Default 3D generator stack | Inventing a graph→geometry solver |
| When Three.js may be adopted | Implementing browser mesh / LOD campus |
| matplotlib PFD/SLD disposition | Changing React/SVG Phase B′ UI |
| Pointers to the rebuild documents (`REBUILD.md`, `BUILD_3D_FROM_FLOW.md`) | Remote/push or GitHub authorize |

## 2. Terms

- Plant graph: the typed graph in `flow_graph/`, the only source of units and streams (AQS-FLOW-GRAPH-001).
- FreeCAD rebuild: regenerating the 3D model from `models/freecad/params.py` with the FreeCAD console program `freecadcmd` (AQS-REB-001).
- Massing: the overall boxes of the buildings and equipment, placed and sized correctly, before any detailed shape.
- Three.js: a JavaScript library for 3D graphics in a web browser.
- LOD (level of detail): simplified versions of a 3D model shown at a distance.
- Phase B′, Phase D: phases of the design-tool roadmap (AQS-UI-001 §9). Phase D is the 3D phase.

## 3. Decision

Table 3.1 records the decision for each layer. It applies to all work in this repository.

Table 3.1. Decision by layer

| Layer | Verdict | Disposition |
|---|---|---|
| **FreeCAD / `freecadcmd` 1.0 rebuild** | **Keep / prefer** | Default Phase D path. Params → builders → `.FCStd`. Binary: `/usr/bin/freecadcmd` (not AppImage 1.1). |
| **OpenSCAD detail → STL → import** | **Keep** | Manufacturing detail under FreeCAD massing (CAD_SCRIPTING_PROTOCOL §5.4–5.5). |
| **Three.js / live browser mesh / LOD campus** | **Defer** | Adopt **only** with a **later written decision** that revises this file (and notes `DESIGN_TOOL_ARCHITECTURE.md` §3.3). Default remains FreeCAD rebuild. |
| **matplotlib PFD/SLD PNG** | **Optional / not authority** | Generators may live under `flow_graph/exporters/matplotlib/`. PNGs are **not** published. Topology authority is the typed graph + **`flow_graph/views/*.svg`**. |
| **React + SVG graph-layer** | **Keep (2D UI)** | Schematic-first interactive surface; not a 3D stack. |
| **Typed `flow_graph/`** | **Sole topology authority** | Graph drives 2D views and design_tool; **does not yet** drive FreeCAD placement. |

## 4. Reasons

1. One parameter path. The FreeCAD builders already take their millimetre geometry from `params.py`. A separate Three.js campus would develop its own sizes unless it were deliberately built to read the same parameters or export recipe.
2. Massing before a mesh interface. The CAD scripting protocol requires the right box in the right place before shop detail or animation. FreeCAD Part modelling does exactly that.
3. A known limit. The step from the graph to geometry is not yet built. It is better to document how the baseline plant is rebuilt than to offer a browser 3D view that could not read the graph either.
4. The 2D authority has already moved. The primary published drawings are the graph-layer SVG files, not matplotlib images.

## 5. What contributors should do

1. Follow `BUILD_3D_FROM_FLOW.md` to rebuild end to end and to use the bridge from the graph.
2. Use `models/REBUILD.sh` and FreeCAD 1.0 only.
3. Treat a pack's `params.json` as a study overlay. It does not rewrite `params.py`.
4. Do not start a Three.js campus, a live parametric mesh, or work that makes matplotlib authoritative, unless this page is first revised with an explicit decision (date, owner, and why the FreeCAD rebuild is not enough).

## 6. Conditions for adopting Three.js

A written decision that adopts Three.js shall state:

- why the FreeCAD rebuild alone does not meet the need;
- whether Three.js is only a viewer (reading STEP, STL or glTF exported from FreeCAD) or a second parametric source (discouraged);
- how `SCALE_M` and the other parameters keep a single source;
- the licence and dependency list under CERN-OHL-S-2.0.

Until that revision exists, Three.js is not the default and no work on it starts.

## 7. Related documents

Table 7.1. Related documents

| Doc | Role |
|---|---|
| `BUILD_3D_FROM_FLOW.md` | End-to-end rebuild and limitations |
| `CAD_SCRIPTING_PROTOCOL.md` | Design-agnostic PFD→CAD pipeline |
| `FREECAD_PROTOCOL.md` | Console binary / script rules |
| `DESIGN_TOOL_ARCHITECTURE.md` | §3.3 schematic first; Phase D default |
| `SCALE_MODEL.md` | `SCALE_M = 1.0` baseline |
