# Stack decision — 3D and diagram surfaces

Document number: **AQS-3D-STACK-001**  
Revision: **A**  
Date: 2026-10-01  
Licence: CERN-OHL-S-2.0  
Authority: Project decision **docs_first** for graph→3D (2026-10-01); aligns with
`DESIGN_TOOL_ARCHITECTURE.md` §3.3 and planning `STACK_REEVAL_2026-10-01.md`
(planning-only; not mirrored here).  
Audience: Contributors and outsiders choosing tools for plant 3D / 2D.

| Rev | Change | Description | Date |
|---|---|---|---|
| A | First issue | FreeCAD bias; Three.js gated; matplotlib optional | 2026-10-01 |

---

## 1. Purpose

Record the **written stack decision** for how 3D and secondary diagram
surfaces relate to the typed plant graph and the FreeCAD rebuild path.
This file is the share-tree answer to “do we use Three.js?” and “are
matplotlib PNGs authority?”

## 2. Scope

| In | Out |
|---|---|
| Default 3D generator stack | Inventing a graph→geometry solver |
| When Three.js may be adopted | Implementing browser mesh / LOD campus |
| matplotlib PFD/SLD disposition | Changing React/SVG Phase B′ UI |
| Pointers to rebuild / BUILD docs | Remote/push or GitHub authorize |

## 3. Decision (binding for share work)

| Layer | Verdict | Disposition |
|---|---|---|
| **FreeCAD / `freecadcmd` 1.0 rebuild** | **Keep / prefer** | Default Phase D path. Params → builders → `.FCStd`. Binary: `/usr/bin/freecadcmd` (not AppImage 1.1). |
| **OpenSCAD detail → STL → import** | **Keep** | Manufacturing detail under FreeCAD massing (AGENT_CAD_PROTOCOL §3.4–3.5). |
| **Three.js / live browser mesh / LOD campus** | **Defer** | Adopt **only** with a **later written decision** that revises this file (and notes `DESIGN_TOOL_ARCHITECTURE.md` §3.3). Default remains FreeCAD rebuild. |
| **matplotlib PFD/SLD PNG** | **Optional / not authority** | Generators may live under `flow_graph/exporters/matplotlib/`. PNGs are **not** shipped in share. Topology authority is the typed graph + **`flow_graph/views/*.svg`**. |
| **React + SVG graph-layer** | **Keep (2D UI)** | Schematic-first interactive surface; not a 3D stack. |
| **Typed `flow_graph/`** | **Sole topology authority** | Graph drives 2D views and design_tool; **does not yet** drive FreeCAD placement. |

## 4. Rationale (short)

1. **One params path.** FreeCAD builders already own millimetre geometry
   via `params.py`. A parallel Three.js campus would fork sizes unless
   deliberately designed as a consumer of the same params / export recipe.
2. **Massing before mesh UI.** AGENT_CAD_PROTOCOL: correct box in the
   right place before shop detail or animation; FreeCAD Part matches that.
3. **Honest gap.** Graph→geometry is **not wired**. Prefer documenting
   rebuild of the baseline plant over claiming a browser 3D that also
   would not read the graph.
4. **2D authority already relocated.** Primary published drawings are
   graph-layer SVGs, not matplotlib PNGs.

## 5. How outsiders should act

1. Follow **`BUILD_3D_FROM_FLOW.md`** for end-to-end rebuild and stub use.
2. Use **`models/REBUILD.sh`** and FreeCAD **1.0** only.
3. Treat pack `params.json` as overlay study — it does **not** rewrite
   `params.py`.
4. Do **not** start a Three.js campus, live parametric mesh, or
   matplotlib-as-authority work unless this document is revised with an
   explicit decision (date, owner, why FreeCAD rebuild is insufficient).

## 6. Future Three.js gate (when/if)

A written decision that *adopts* Three.js **shall** state:

- Why FreeCAD rebuild alone fails the use case
- Whether Three.js is viewer-only (consumes STEP/STL/glTF from FreeCAD) or
  a second parametric source (discouraged)
- How `SCALE_M` / params stay single-sourced
- Licence and dependency list under CERN-OHL-S-2.0

Until that revision exists, **Three.js is not the default and not
started**.

## 7. Related

| Doc | Role |
|---|---|
| `BUILD_3D_FROM_FLOW.md` | Outsider end-to-end + honest gap |
| `AGENT_CAD_PROTOCOL.md` | Design-agnostic PFD→CAD pipeline |
| `FREECAD_PROTOCOL.md` | Console binary / script rules |
| `DESIGN_TOOL_ARCHITECTURE.md` | §3.3 schematic first; Phase D bias |
| `SCALE_MODEL.md` | `SCALE_M = 1.0` baseline |
