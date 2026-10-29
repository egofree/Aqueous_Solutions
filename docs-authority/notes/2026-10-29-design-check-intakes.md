# Design check: intakes are not balanced as process units

Date: 2026-10-29. Files: `docs-authority/_design_check.py`, `docs-authority/AUTHORITY.md`.

## Finding

A locale run for the Death Valley profile at the head of `main` (2026-10-26) wrote a site design check with two failures: the mass balance of GW_INTAKE (out 255 kg/d, in 0) and the unit count that includes it. GW_INTAKE is an intake unit: it draws groundwater from outside the plant, so it has no inflow to balance. The baseline does not show the fault because its intakes carry no flow.

## Change

Check QC-01 in `docs-authority/_design_check.py` skips units of class `intake` (GW_INTAKE, SW_INTAKE, ATM_INT) in the same way as boundaries. The baseline mass balance result does not change. Running the generator also added `flow_graph/param/site_units.py` to the module record of AQS-QA-002: that module was committed on 2026-10-26 without the record being regenerated, and the staleness check did not detect it because the record is gated on the graph, not on the module list.

A path in AQS-AUTH-001 that had been shortened with an ellipsis is written in full (`design_tool/aqs_design_tool/solver/scale_down_map.py`).
