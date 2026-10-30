# Rewrite batch 47a: audit of the matplotlib flow sheets

Task X-RTE-LEGACY-PFD is closed. Every script in `flow_graph/exporters/matplotlib/` was run against the current graph, its unit and stream identifiers were checked against the graph, and its imports and citations were listed. A script was to be removed only if what it draws is gone from the graph, or if a graph view already shows it with nothing of value lost. No script met either test: each draws units and streams that are on the graph or held there as placeholders, and carries equipment detail and notes that no graph view has. All the scripts are kept. The record is `flow_graph/LEGACY_PFD_SCRIPTS.md` revision B.

The audit fixed the following:

- The two building layout scripts could not find the building parameters and did not run. They now also look in `models/freecad/params.py`.
- The cold-box and vent closure sheets drew the retired stream S18. They now show S67 and S67B through FLUE_KO.
- The solar cell sheet now names its wafer feed IA-PV-WAFER and its cell product IA-PV-CELL. It and the ultrapure water sheet now point to the fab sector view instead of the retired wafer fab sheet.
- The wet line sheet now carries its number AQS-PFD-WET-001, which pages already cited.

The sheet numbers that the scripts carry were in neither register. `docs-authority/_drawings.py` now reads them from the script docstrings and sheet tables into the drawing register AQS-DWG-002. It also keeps the four sheets removed on 2026-10-29 as retired numbers, each pointing to the graph view that replaced it. Those numbers are removed from `docs-authority/unregistered_doc_numbers.json`, and the matching question in REWRITE_TODO is closed. The plant graph and the balance are not changed.
