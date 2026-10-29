# Rewrite batch 29: route UPW_TO_FAB retired as a duplicate

Date: 2026-10-29

Task X-RTE-UPW_TO_FAB is done by retirement. The route ran from the UPW header HDR_UPW to the fab UPW tank FAB_UPW_TANK and carried no flow. The tank is already filled by IA-UPW-FAB at 60.0 kg/d straight from the polisher BMED_UPW_POLISH, which also feeds the header. A second path from the same source through the header adds no diversity, so the route has no case that would put it in service. It is set to presence retired on the graph, with the reason in its note.

## What changed

- `flow_graph/plant_flow_graph.json`: UPW_TO_FAB set to presence retired.
- `docs-authority/_task_plan_gen.py`: X-RTE-UPW_TO_FAB listed as a done task with its evidence.
- `docs-authority/FAB_WET_INTERFACE.md` (AQS-IF-FAB-WET-001) is now revision C, with the route removed from its stream list. The generated pages (the line list, the isometric sheets and their index, the fab and water pages) follow the graph through the regenerator, so the route's isometric sheet drops out of the set.

## Values

The route carried no flow, so the bus demand, the array, the storage and the balance closure do not move.
