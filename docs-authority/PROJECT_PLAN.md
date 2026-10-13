# Project plan

Document number: AQS-PLAN-005
Revision: A
Date: 2026-10-12
Authority: graph Rev BH until `flow_graph/plant_flow_graph.json` says otherwise. Not a PE stamp.

The status of these lines is `docs-authority/MASTER_PLAN.md` (AQS-PLAN-004).
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

Active item: 1.2 on AQS-PLAN-004. Digester. It does not invent a volatile-solids number.

## Limits

The graph is the plant. A duty page does not outrank an edge.

`mvs.mvs_criteria.loops_closed` stays false. On-site evidence is not in the repo. A cut-test result is not that flag.

A missing measurement stays named on the open line.

Aqueous cells do not make aluminum, magnesium, calcium, lithium, titanium, silicon, or the rare earths. Anodes do not use iridium.

The frame standard is the parameter set in AQS-MOD-001.

Section 8 of a duty is the gap list. A unit with a gap in section 8 is not finished.

The 500 kg/day moonshot is not this graph.
