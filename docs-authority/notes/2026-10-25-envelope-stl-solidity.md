# Envelope STL pipeline: working solids, registry pruned to the graph

Date: 2026-10-25. Scope: `flow_graph/param/envelopes.py` and the `cad/stl/` registry (X-PAR-04). No graph change.

## Problem

Every envelope STL in `cad/stl/` was a zero-thickness closed box surface: 12 triangles, no wall thickness, and (from the aged export path) inconsistent triangle winding, so kernels reported `is_volume: false`. Slicers and CAD tools reject such files as "a single surface", which is exactly what a user saw. The registry had also drifted: 254 files against 179 present graph units, 86 of them for units that have left the graph entirely, and 65 more for present units whose size no longer sits on the graph.

## Fix

- `flow_graph/param/envelopes.py` now builds each envelope as a thick-walled open-top tray: outer faces exactly on the claimed envelope (the registry bounding-box rule is unchanged), walls and floor stepping inward 10 mm (clamped for small envelopes), exported with explicit tolerance. Result: watertight, consistently wound, positive-volume solid meshes. `--all` also prunes files of units no longer in the graph; `--repair` re-trays files of present units that have no graph size at each file's own bounding box (a geometry repair that changes no claimed size).
- Registry after the run: 168 files - 103 for graph-sized units (regenerated as trays) and 65 repaired trays for present units whose size is not on the graph. 86 files of departed units deleted. Verified: all 168 watertight, `is_volume` true, nonzero volume.
- Follow-through: the retired units' duty sheets and the EXPANDER work order no longer cite withdrawn envelope files (the duty section 7 line in `_duty_basis.py` is now presence-aware: "retired from the graph; no envelope is issued"). The OpenSCAD detail models and the manufacturing-model exports were checked and are healthy solids; they were left alone.

## Open item recorded

65 present units carry no `size_mm` on the graph (their envelopes came from earlier registry generations; the FreeCAD GA params carry block sizes, not per-unit sizes). The repaired trays keep those units' last claimed bounding boxes. Re-sourcing per-unit sizes for them - graph or GA as the single authority - is a separate decision and is not silently taken here.
