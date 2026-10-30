# Matplotlib flow sheets: audit and status

Document number: AQS-FLOW-GRAPH-001 annex  
Revision: B  
Date: 2026-10-30  
Licence: CERN-OHL-S-2.0

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue: the matplotlib sheets and how far each is bridged to the plant graph. | 2026-10-01 |
| B | Audit of every script in `flow_graph/exporters/matplotlib/` (task X-RTE-LEGACY-PFD): what each draws, who cites it, whether it runs, and whether it is kept. Each sheet number is now in the drawing register AQS-DWG-002. The rebuild commands are corrected to the repository paths. | 2026-10-30 |

## Purpose and scope

This page records the status of the scripts in `flow_graph/exporters/matplotlib/` that draw process flow sheets, layout sheets and the electrical single-line diagram with matplotlib. The plant graph `flow_graph/plant_flow_graph.json` is the only authority for units, streams and rates. A script places boxes and labels by hand and overlays the stream identifiers and rates that it reads from the graph through `flow_graph/pfd_bridge.py`. The graph-driven layer views in `flow_graph/views/` are drawn by `flow_graph/render_layer_views.py` and are not covered here.

## 1. Audit method

Each script was checked in four ways on 2026-10-30. It was run against the current graph. Every unit and stream identifier it names was checked against the graph. Its citations in tracked files and its imports were listed. Its content was compared with the graph views, to find sheets that only repeat a view.

A script is removed only when what it draws is gone from the graph, or when a graph view shows the same thing with nothing of value lost. No script met either test in this audit. Every sheet draws units and streams that are present or held as placeholders, and the hand-placed equipment detail, interfaces and fit-out notes that the sheets carry are not in any graph view. All the scripts are therefore kept. The four sheets that only repeated a sector view were removed on 2026-10-29, and their numbers are kept in the register as retired (section 5).

## 2. Fixes made in the audit

- `campus_life_hazard_pfds.py` and `building_stack_pfds.py` could not find the building parameters, because they looked for them only in locations that no longer exist. They now also look in `models/freecad/params.py`, and both run.
- `cryo_pfd.py` and `vent_closure_pfd.py` drew the retired claim stream S18 as the afterburner carbon dioxide path. They now show S67 and S67B through FLUE_KO, which carry it (A-M-434).
- `solar_cell_pfd.py` said that the cell line had no streams of its own. It now names the wafer feed IA-PV-WAFER and the cell product IA-PV-CELL (A-M-437). It and `fab_upw_pfd.py` pointed to the retired wafer fab sheet; they now point to the fab sector view.
- `wet_line_factory_pfd.py` now carries its sheet number AQS-PFD-WET-001, which the pages already cited.
- The sheet numbers that the scripts carry were registered in neither register. `docs-authority/_drawings.py` now reads them from the scripts into the drawing register, and they are removed from `docs-authority/unregistered_doc_numbers.json`.

## 3. Scripts

Table 3.1 gives every script, its sheet number, how it is run, and its status. The images of the sheets that the regeneration does not run are not tracked; run the script to see one.

Table 3.1. Scripts in `flow_graph/exporters/matplotlib/`

| Script | Sheet | What it draws | Run by | Status |
| --- | --- | --- | --- | --- |
| `drawlib.py`, `params.py`, `labels.py`, `sector_style.py` | — | Drawing helpers, colours and label text imported by the sheets | imported | Kept |
| `completion_pfd.py`, `continuous_recycling_pfd.py`, `glass_ceramic_pfd.py`, `master_disassembly_pfd.py`, `oil_line_pfd.py`, `polish_bank_pfd.py` | AQS-PFD-IMG-* | Sector sheets whose images go to `media/pfd/` | the regeneration (`flow_graph/regen_derived.py`) | Kept |
| `wet_line_factory_pfd.py` | AQS-PFD-WET-001 | The factory wet line: leach vessel, weir and auger, electrowinning aisle | the regeneration | Kept |
| `electrical_sld.py` | — | Electrical single-line diagram with the storage peers | by hand | Kept; cited by the electrical pages |
| `mass_flow_pfd.py` | — | The drawing of the mass-flow claim page AQS-MF-001 | by hand | Kept with its page |
| `bmed_regen_pfd.py`, `ew_cascade_pfd.py`, `znbr2_flow_pfd.py` | — | Detail of one unit: the bipolar membrane regenerator, the electrowinning cascade, the flow battery | by hand | Kept |
| `hydro_dock_pfd.py` | — | The pumped-hydro set and the dock | by hand | Kept |
| `meoh_train_pfd.py` | AQS-PFD-MEOH-001 | The methanol train and its storage | by hand | Kept |
| `fuel_cell_pfd.py`, `backup_gen_pfd.py`, `geothermal_pfd.py` | AQS-PFD-FC-001, AQS-PFD-GEN-001, AQS-PFD-GEO-001 | The fuel cell, the backup generator, the ground loop and heat pump | by hand | Kept |
| `cryo_pfd.py`, `vent_closure_pfd.py` | AQS-PFD-CRY-001, AQS-PFD-VENT-001 | The cold-box internals; the vent and stack closure | by hand | Kept; S18 removed |
| `fab_upw_pfd.py`, `solar_cell_pfd.py` | AQS-PFD-FAB-UPW-001, AQS-PFD-FAB-PV-001 | The ultrapure water polish; the solar cell line | by hand | Kept; updated |
| `habitation_pfd.py`, `hab_water_pfd.py` | AQS-PFD-HAB-001, AQS-PFD-HAB-WTR-001 | The habitation fit-out; its water purification | by hand | Kept |
| `farm_pfd.py`, `nutrient_pfd.py`, `terrace_irrigation_pfd.py` | AQS-PFD-FRM-001, AQS-PFD-NUT-001, AQS-PFD-TRR-001 | The farm, the nutrient cycle, the terrace irrigation | by hand | Kept; in areas the owner holds |
| `container_layout.py` | — | Plan of the wet and thermal containers with their air headers | by hand | Kept |
| `campus_life_hazard_pfds.py` | AQS-PFD-CMP-001, AQS-PFD-HSE-001, AQS-PFD-PIP-002, AQS-PFD-GAS-001, AQS-PFD-WTR-001 | Campus, hazard separation, life headers, life gas and water cycle layout sheets | by hand | Kept; path fixed |
| `building_stack_pfds.py` | AQS-PFD-BLD-001 to AQS-PFD-BLD-006 | The building section and the floor, roof and core plans | by hand | Kept; path fixed |

## 4. Rebuilding the sheets

Run a script from the repository root with a headless matplotlib backend, for example:

```
MPLBACKEND=Agg python3 flow_graph/exporters/matplotlib/electrical_sld.py
```

A script writes its image next to itself, or to an `images/` folder there if one exists. Do not commit those images. An image that should be tracked must be added to `flow_graph/regen_derived.py` and to the outputs of its stage. The graph views are rebuilt by `python3 flow_graph/render_layer_views.py`, which the regeneration runs.

## 5. Sheets removed earlier

The wafer fab sheet AQS-PFD-FAB-001, the fab reagent forks sheet AQS-PFD-FAB-RGN-001, the manufacturing shop sheet AQS-PFD-MFG-001 and the metal forming sheet AQS-PFD-MFG-MET-001 were removed on 2026-10-29. Each only repeated what the sector views `flow_graph/views/pfd-fab.svg` and `flow_graph/views/pfd-mfg.svg` show from the graph. Their numbers stay in the drawing register as retired, with the view that replaced each.

## 6. Open items

- The sheet titles and labels are placed by hand. A label that states a claim, such as a stream being closed, is checked only when its script is audited. A sheet whose content moves into a graph view should be retired the same way as the sheets of section 5.
- The placeholders GEO_ORC, S48, DOCK_EXPORT_TBD, IA-POL-01 and IA-ESS-HYDRO-ELEC are drawn as placeholders, which is their state on the graph.
