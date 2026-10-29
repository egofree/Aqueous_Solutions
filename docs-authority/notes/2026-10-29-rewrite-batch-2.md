# Rewrite batch 2: power sizing, fire protection and duty sheet headers

Date: 2026-10-29

AQS-ELEC-007 (`POWER_SIZING.md`) had no generator, and its values had drifted from the graph. It is cited by the sizing scripts, the code basis stage and the backup generator page, so it was kept rather than removed. It is now written by `docs-authority/_power_sizing_doc.py` from the graph and the drivers, as regen stage `doc_power_sizing`, which runs after `write_graph_power` and before `code_basis`. Section 5 of the page reports two mismatches for the owner: the backup generator driver holds 40 kW while the rule in its note gives 20 kW, and the bus section rating was computed for an older bus demand.

AQS-SAF-005 (`FIRE_PROTECTION.md`) was rewritten through `docs-authority/_fire.py`. The calculations are unchanged.

`docs-authority/_duty_basis.py` now refreshes the "Graph Rev" header of every existing duty sheet, not only of sheets it authors, so the sheets carry the current graph revision.
