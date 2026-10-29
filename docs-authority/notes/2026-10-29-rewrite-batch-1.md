# Documentation rewrite: ground loop and backup generator, habitation fixtures, structural loads

Date: 2026-10-29. Documents: AQS-PWR-002 Rev C, AQS-HAB-001 Rev C, AQS-BLD-013 Rev B, AQS-DOC-003.

## Change

- AQS-PWR-002 (`GEOTHERMAL_BACKUP.md`) is rewritten from the plant graph. Revision B called the backup generator a hydrogen machine with diesel as an emergency purchase; the graph makes it dual-fuel, burning hydrogen first and the plant's C5 to C10 cut second, and the page now says so. Units and streams that are no longer graph nodes or edges are removed, as are references to files outside the repository.
- AQS-HAB-001 (`HAB_FIXTURES.md`) is rewritten from the plant graph. The composting toilet it described is no longer a graph node; blackwater now goes to BLACK_DIGEST.
- AQS-BLD-013 (`STRUCT_LOADS.md`) is rewritten through `docs-authority/_struct_loads.py`. The generator docstring and the page said the operating liquid was taken as dead load, but the calculation takes it as live load; the text now matches the calculation. No load changed.
- AQS-DOC-003 records the three pages as done, gives a specific reason for re-opening AQS-ELEC-007 (no generator writes it and its values disagree with the graph), and notes that the duty sheet headers still name graph revision BH.
- `python3 -m flow_graph.param.regen --check` now runs `_rev_stamp.py --check-only`. It ran `--check` before, which rewrote `DERIVED_REVISIONS.md` with "working tree" stamps for every uncommitted file, so running the check left a change in the tree that later commits carried as churn. A full regeneration still refreshes the register.
- The register test failure left by the previous change (the document register not regenerated after the revision changes to AQS-DOC-002 and AQS-GLO-001) is fixed by regenerating `DOC_REGISTER.md`, and the tracker no longer uses the phrase that the generator test reads as a claim that the tracker is generated.
