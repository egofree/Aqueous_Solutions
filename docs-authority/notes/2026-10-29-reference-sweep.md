# Reference sweep: unregistered document numbers and paths outside the repository

Date: 2026-10-29

A sweep of every tracked Markdown page found document numbers that are registered in neither the document register (`DOC_REGISTER.md`) nor the drawing register (`DRAWING_REGISTER.md`). None of them was ever the number of a page in this repository's history; they belong to documents kept outside it (the hub, SLINGSHOT/, POWER/ and the numbered root documents), or to process flow diagram numbers that were never registered. The most cited are AQS-AUD-001, AQS-GAP-001, AQS-MVS-GAP-001 and AQS-PID-001; most of the rest are AQS-PFD-* drawing numbers.

The numbers are listed in `docs-authority/unregistered_doc_numbers.json`. The new test `flow_graph/test_doc_number_refs.py` fails if a page cites a new unregistered number, and fails if a listed number is fixed but left on the list, so the list can only shrink. Each citation is to be fixed when its page is rewritten, as was done for FUEL_CELL, WATER_PURIFICATION, LIFE_MEP and MEOH_TRAIN.

Pages that still cite paths outside the repository include the equipment lists for the fuel cell, the cryogenic plant, the farm, the fab and metal forming, `AUTHORITY.md`, `ELECTRICAL.md`, `PARAMETRIC_MODEL.md` and `internal/REMAINING_BLD.md`. They stay on the rewrite list.

Two questions are recorded for the owner in `REWRITE_TODO.md` section 6: whether the AQS-PFD-* flow diagram numbers should be registered in the drawing register, and what replaces AQS-AUD-001, the crew and water audit that many pages cite.
