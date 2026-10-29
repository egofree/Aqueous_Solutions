# Rewrite batch 7: pipe, wire and building-block family plans, and the standards list

Date: 2026-10-29

Four generated pages were rewritten through their generators: the pipe family plans AQS-INV-006 (`_pipe_specs.py`), the wire family specifications AQS-INV-007 (`_wire_specs.py`), the building-block family plans AQS-INV-009 (`_block_fam_plans.py`) and the codes and standards list AQS-STD-004 (`_standards_list.py`). Each page now has a purpose and scope section, its rules and plans written as sentences and numbered tables. The standards list also gains a record of revisions, and its standard titles are no longer cut off at 140 characters.

Several counts were fixed in the text and had gone stale. The pipe page said 18 families where the inventory has 21. The building-block page said 64 bought families where the inventory has 82, and named a fleet-wide count of spares that no generator computes. These counts are now computed from the inventories or removed.

The page tests (`test_pipe_specs.py`, `test_wire_specs.py`, `test_block_fam_plans.py`) were updated to the new wording; they check the same facts as before. No values changed.
