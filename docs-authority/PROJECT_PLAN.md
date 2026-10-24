# Project plan

Document number: AQS-PLAN-005
Revision: B
Date: 2026-10-19
Authority: graph Rev AC per `flow_graph/plant_flow_graph.json` (2026-10-17). Not a PE stamp.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue | 2026-10-12 |
| B | Authority restamped AC; limits updated for the closed balance, the D-DOCK trade-boundary ruling, and the D-PV derivation direction. No rate change. | 2026-10-19 |

The status of these lines is `docs-authority/internal/MASTER_PLAN.md` (AQS-PLAN-004).
AQS-PLAN-003 is the module order against the tech tree. It is not this sequence.
AQS-PLAN-002 is the definition of a buildable unit.
AQS-PLAN-001, AQS-REM-001, and AQS-MVS-CHK-001 are history.

## Buildable

A unit is buildable when the inlet composition is on the edge, the nozzles have a location and a rating, the internals are drawn, relief has a destination, an instrument trips or the page says there is none, and a mesh exists. The 199 duty pages do not meet that test.

## Sequence

One phase, then the next. The active item is named here.

| Phase | Work | Stops when |
| --- | --- | --- |
| 0 | Record, cut test, electrical and thermal book | No rate has changed, and the Rev N drawings are marked or replaced |
| 1 | Feed composition, sheet split, digester, then the other streams that already have parts | Nothing is resized before its inlet composition is on the edge |
| 2 | Nozzles, line lists, the four missing classes | A connection can be built |
| 3 | Internals and holdup | No residence time is an envelope divided by a flow |
| 4 | Relief | Pressurized nodes have a case. Atmospheric nodes say so |
| 5 | Solids, on the operator box | Meshes match the duties at the revision that enters the phase |
| 6 | Self-copy | Not started until 0 through 5 are accepted |

Active item: 0.2 on AQS-PLAN-004. Cut test. It does not change a rate.

## Limits

The graph is the plant. A duty page does not outrank an edge. Independent numbers live once, in `flow_graph/param/drivers.json`, each with a basis; nothing is fixed arbitrarily (AQS-PAR-001).

`mvs.mvs_criteria.loops_closed` stays false. On-site evidence is not in the repo. A cut-test result is not that flag. The balance closing on the graph (0 failing units at Rev AC) is a model result, not that flag either.

The dock is the inter-plant trade boundary, not a process sector. Imports of feedstock and exports of surplus are a reported trade statement; the dock is exempt from intra-plant closure standards, and product buffer storage for what crosses it is assumed built (owner ruling D-DOCK 2026-10-19, `notes/first_principles_audit_2026-10-17.md`).

PV is derived, never assumed: nameplate from the bounding electrical demand at `pv_oversize_factor` (2.0), and the roof area and building footprint derived from the PV array, not the reverse (owner ruling D-PV 2026-10-18, same note; D75).

A missing measurement stays named on the open line.

Aqueous cells do not make aluminum, magnesium, calcium, lithium, titanium, silicon, or the rare earths. Anodes do not use iridium.

The frame standard is the parameter set in AQS-MOD-002.

Section 8 of a duty is the gap list. A unit with a gap in section 8 is not finished.

The 500 kg/day moonshot is not this graph.
