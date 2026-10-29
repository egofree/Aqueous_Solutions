# Rewrite batch 15: the manufacturing and wafer fab equipment lists

Date: 2026-10-29

The three equipment lists below were hand-kept pages that no longer matched the plant graph. Each is now written by a generator that reads the graph, and each generator is a regeneration stage.

- `docs-authority/METAL_FORMING_EQUIPMENT.md` (AQS-EQP-MFG-MET-001), Rev E, and `docs-authority/MFG_SHOP_EQUIPMENT.md` (AQS-EQP-MFG-001), Rev E, are written by `docs-authority/_mfg_equipment.py` (stage `doc_mfg_equipment`). The units of sector MFG in the melt, forming, air-handling, scrubber and heat-recovery classes go to the metal-forming list; the others go to the shop list. Tool nameplates and daily energy come from the tool list AQS-MFG-010, which `docs-authority/_mfg_tools.py --json` now reports without rewriting its page.
- `docs-authority/WAFER_FAB_EQUIPMENT.md` (AQS-EQP-FAB-001), Rev D, is written by `docs-authority/_wafer_fab_equipment.py` (stage `doc_wafer_fab_equipment`) from the units of sector FAB, the equipment list of WAFER_FAB and the fab edges.

## What the check against the graph found

- The metal-forming list named tags that are not on the graph: the product bins, the powder crib, the nitrogen blanket, the swarf collection, the scrubber regenerator, the shop air and the electrode blank station. The shop list named the stock crib and the work floor. These are gone from the pages.
- The metal-forming list gave nitrogen as the atomising gas; the tool list sizes the atomiser on argon recirculation.
- The tool sizes left as TBD are now the nameplates of AQS-MFG-010. The die schedule, the mill gauge and width, and the atomiser batch rate are an owner question.
- The fab list named computer-aided design massing names (FAB_PREP, FAB_TOOL, ETCH_RETURN and the crystal-to-wafer stage names) as units. On the graph the stages are equipment inside WAFER_FAB, whose equipment loads sum to its average load, and the wet bench, the reagent forks, the lithography tools and the solar-cell line are units of their own.
- No stream brings silicon to WAFER_FAB: STOCK_TO_FAB carries no flow, so the wafer stream to LITHO_COAT is not backed by a silicon charge. This is an owner question; no rate was changed.
- The separation rules hold on the graph: MET_MELT takes mass only from EW_9 and the atomiser remelt, the metal-aisle air handler exchanges air only with its scrubber, and the heat recovery exchanger sends only heat to the Q4 header.
- References to documents outside the repository and to unregistered drawing numbers were removed. The drawings are now the plant view `flow_graph/views/pfd.svg`.

## Left for later

- The older drawing scripts `metal_forming_pfd.py`, `mfg_shop_pfd.py`, `wafer_fab_pfd.py` and `fab_reagent_forks_pfd.py` in `flow_graph/exporters/matplotlib/` still draw tags that are not on the graph. Deleting them is held with the other deletions.
- The process page `docs-authority/METAL_FORMING.md` (AQS-MFG-MET-001) has the same stale tags and references; it is not on the pending list yet.
