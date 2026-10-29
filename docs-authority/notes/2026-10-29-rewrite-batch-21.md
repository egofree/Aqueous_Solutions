# Rewrite batch 21: four hand-drawn process sheets retired

Date: 2026-10-29

Owner decision of 2026-10-29: obsolete drawing scripts are removed once it is shown what each one draws, who cites or imports it, and whether anything still valid would be lost. A diagram that is still needed is drawn from the graph instead.

## Removals and evidence

Table 1. Scripts removed

| Script | What it drew | Who used it | What replaces it |
| --- | --- | --- | --- |
| `metal_forming_pfd.py` (in `flow_graph/exporters/matplotlib/`) | A hand-placed sheet of the metal-forming train (AQS-PFD-MFG-MET-001), with product bins, a powder crib, a nitrogen blanket, the electrode blank station and an induction pyrolyzer that are not on the graph. | No script imports it. The regenerator does not run it and its PNG was never committed. The metal-forming equipment page and the legacy annex named it. | `flow_graph/views/pfd-mfg.svg`, drawn from the graph by `flow_graph/render_layer_views.py`. |
| `mfg_shop_pfd.py` (in `flow_graph/exporters/matplotlib/`) | A sheet of the shop (AQS-PFD-MFG-001), with an extrusion line, injection moulding, a sheet press, a shredder and a silicate step that are not on the graph. | Not imported or run; its PNG was cited by the internal build log only. | `flow_graph/views/pfd-mfg.svg`. |
| `wafer_fab_pfd.py` (in `flow_graph/exporters/matplotlib/`) | A sheet of the wafer fab (AQS-PFD-FAB-001), with crystal-growth and wafering tool tags (CZ_PULLER, ID_WIRE_SAW, LAP_CMP and others) that are tool rows inside WAFER_FAB, not graph units. | Not imported or run; cited by FAB_UPW, the fab equipment page, SOLAR_CELL_EQUIPMENT and the internal build log. | `flow_graph/views/pfd-fab.svg`. The tool train itself is listed by the generated page WAFER_FAB_EQUIPMENT. |
| `fab_reagent_forks_pfd.py` (in `flow_graph/exporters/matplotlib/`) | A sheet of the fab reagent forks (AQS-PFD-FAB-RGN-001), naming a PV texture step and placeholders that are not on the graph. | Not imported or run; cited by FAB_WET_REAGENTS and the fab equipment page. | `flow_graph/views/pfd-fab.svg`, which includes every reagent fork into the fab. |

Nothing of value is lost. The scripts held no logic beyond placing boxes and labels by hand; every stream they could draw is on the graph and now appears in the sector views. The two new views are presets of `render_layer_views.py` (`pfd-mfg` and `pfd-fab`): every mass stream with an end in the sector, regenerated with the other views.

The citations were moved to the sector views in FAB_UPW, FAB_WET_REAGENTS, SOLAR_CELL_EQUIPMENT, the internal build log, the legacy annex `flow_graph/LEGACY_PFD_SCRIPTS.md` and the two equipment-page generators. Each removed path is listed in `docs-authority/retired_names.json` with its replacement. The four drawing numbers are withdrawn.

## Not removed in this batch

The other scripts in `flow_graph/exporters/matplotlib/` that the regenerator does not run also draw some tags that are not on the graph. Each still has live citations and needs the same check before removal. `terrace_irrigation_pfd.py` draws the terrace irrigation that the owner deleted on 2026-10-18; it will be retired with the rewrite of TERRACE_LANDSCAPE, which cites it.
