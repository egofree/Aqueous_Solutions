# Project plan

Document number: AQS-PLAN-005
Revision: C
Date: 2026-10-25
Authority: graph Rev AC per `flow_graph/plant_flow_graph.json` (2026-10-17). Not a PE stamp.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue | 2026-10-12 |
| B | Authority restamped AC; limits updated for the closed balance, the D-DOCK trade-boundary ruling, and the D-PV derivation direction. No rate change. | 2026-10-19 |
| C | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No change to the phases, the limits or any rate. | 2026-10-25 |

## 1. Purpose and scope

This plan sets the order in which the design of the plant is completed and the engineering limits that every change to the design must respect. It is written for an engineer joining the project who needs to know what is being worked on now, what must be finished before the next step starts, and which rules cannot be relaxed.

The plan does not list individual tasks or their status. The master task list is `docs-authority/TASK_PLAN.md` (AQS-PLAN-007). The status of each line of this plan is recorded in `docs-authority/internal/MASTER_PLAN.md` (AQS-PLAN-004). The design is a study: no professional engineer (PE) has reviewed or stamped it.

Three older planning documents are kept as history and do not control the work. AQS-PLAN-003 orders the plant modules against the technology tree, which is a different sequence from the one in section 3. AQS-PLAN-002 defines a buildable unit; section 2 restates that definition. AQS-PLAN-001, AQS-REM-001 and AQS-MVS-CHK-001 are superseded working lists.

## 2. When a unit is buildable

A unit of the plant is buildable when all of the following are true:

- The composition of every inlet stream is recorded on the corresponding edge of the plant flow graph.
- Every nozzle has a location and a pressure rating.
- The internals of the unit are drawn.
- Every relief device has a stated destination.
- An instrument trips the unit on an unsafe condition, or the unit's page states that no trip is needed.
- A three-dimensional mesh of the unit exists.

The generated duty pages in `docs-authority/duties/` do not yet meet this test.

## 3. Sequence of work

The work proceeds in phases. Each phase is finished before the next one starts. Table 3.1 lists the phases and the condition that ends each one.

Table 3.1. Phases of work

| Phase | Work | The phase ends when |
| --- | --- | --- |
| 0 | Record the revision history, run the loop closure check, and check the electrical and thermal pages against the graph | No rate has changed, and every drawing that still refers to graph revision N is marked as not current or is replaced |
| 1 | Record the feed composition and the split of each feed between output streams, then the digester, then the other streams whose equipment is already specified | No unit is resized before the composition of its inlet is recorded on the graph edge |
| 2 | Nozzles, line lists and the four missing piping classes | Every connection can be built from the documents |
| 3 | Internals and liquid holdup | No residence time is calculated by dividing an envelope volume by a flow |
| 4 | Relief | Every pressurized unit has a relief case, and every atmospheric unit is stated to be atmospheric |
| 5 | Solid models, built on the operator's workstation | The meshes match the duties at the graph revision current when the phase starts |
| 6 | The bill of materials for building a copy of the plant from its own output | Not started until phases 0 to 5 are accepted |

The active item is line 0.2 of AQS-PLAN-004, the loop closure check. It runs `python3 flow_graph/loop_closure.py` and reports whether every material loop in the graph closes. The check does not change any rate.

## 4. Engineering limits

### 4.1 Authority of the model

The plant flow graph (`flow_graph/plant_flow_graph.json`) defines the plant. Where a duty page and an edge of the graph disagree, the edge is correct. Every independent number is set once, in `flow_graph/param/drivers.json`, with a stated basis. No value is fixed arbitrarily (AQS-PAR-001).

### 4.2 Loop closure flag

The minimum viable system (MVS) is the smallest set of sectors that closes every mass, energy and life-support loop. The graph flag `mvs.mvs_criteria.loops_closed` stays false until evidence from a built plant is in the repository. A passing loop closure check does not set the flag. A closed balance in the model, such as the result of no failing units at graph revision AC, does not set it either.

### 4.3 Trade boundary at the dock

The dock is the point where material crosses between this plant and other plants. It is not a process sector. Imported feedstock and exported surplus are reported in a trade statement. The closure standards that apply inside the plant do not apply at the dock, and the design assumes that buffer storage is built for the products that cross it. This was decided on 2026-10-19 (decision D-DOCK, recorded in `notes/first_principles_audit_2026-10-17.md`).

### 4.4 Photovoltaic array

The photovoltaic (PV) array is sized from demand and is never an assumed input. Its nameplate rating is the bounding electrical demand multiplied by `pv_oversize_factor` (2.0). The roof area and the building footprint are then derived from the array, not the array from the building. This was decided on 2026-10-18 (decision D-PV and item D75, recorded in the same note).

### 4.5 Missing measurements

A measurement that the design needs but does not have remains named on the open line of the plan until it is supplied.

### 4.6 Electrochemistry

Aqueous electrolytic cells are not used to produce aluminum, magnesium, calcium, lithium, titanium, silicon or the rare earth elements. Anodes do not use iridium.

### 4.7 Frame standard

The structural frame of every module follows the parameter set in AQS-MOD-002.

### 4.8 Open gaps in duty pages

Section 8 of each duty page lists the gaps in that unit's design. A unit with an entry in section 8 is not finished.

### 4.9 Scale

This graph models the baseline plant. It does not model the 500 kg/d wet-feed scale given as cassette step M3 in AQS-SCALE-001.
