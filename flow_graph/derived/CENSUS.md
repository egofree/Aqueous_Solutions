# Flow graph census — DERIVED

Source: AQS-FLOW-GRAPH-001 Rev G
Generated: 2026-10-02

- nodes: **91** (present=91, placeholder=0)
- edges: **145** (present=145, placeholder=0)
- by namespace: {'S': 88, 'SANDBOX': 2, 'IA': 55}
- locks: layered_views, full_depth_now, efd_three_layers, typed_graph_sole, present_study_rates_wp_l2, true_closure_rates_wp, site_lat_design_sandbox, true_closure_residuals_wp, reprap_bom_complete_c4, site_ghex_design_survey_locked, wp_l3_evidence_pack, wp_l4_claim_discipline

## Gaps

- **S17_bridged** (low): S17 labeled on graph-bridged electrical_sld.png; still sparse on line PFDs
- **MEOH_MF_SLD_BRIDGED** (low): S73–S82 on graph-bridged mass_flow_pfd + S79 on electrical_sld; MF claim_status rows still end S72
- **PUMPED_HYDRO_PFD** (low): S22/S23/IA-ESS-HYDRO continuous rates = 0 by design (inventory cycle). Energy asymmetry vs ZnBr2 remains AQS-ESS-001.
- **DOCK_PFD** (low): Dedicated hydro_dock_pfd graph-bridged; S86 dock export issued (was DOCK_EXPORT_TBD).
- **INTRA_AISLE_RATES** (low): IA-* and campaign nulls filled true-closure study rates. Remain status=study.
- **SANDBOX_S08G_S14X** (medium): Keep sandbox or promote — do not invent third ID
- **GENERATOR_MIGRATION** (medium): Other matplotlib pfd_scripts/* still legacy bootstrap; electrical_sld + mass_flow_pfd graph-bridged
- **WP_L2_MASS_BALANCE** (low): Superseded by WP_TRUE_CLOSURE_RESIDUALS capture edges/rates. Study balances≈0; Present CAD still blocks loops_closed.
- **WP_L2_PRESENT_CAD** (medium): Equipment IDs on disk; FreeCAD Features for VCD/REMIN/LITHO/BLOW/ELC absent (placeholder_skip). *_on_site=false (C3). C4 reprap_bom_complete=true independent (AQS-BOM-SC-001 Rev F). AHJ design-basis USA_Dallas_class — no fake certificates. WP_PRESENT_CAD.md. Primary remaining loops_closed gate.
- **WP_L2_SITE_SURVEY** (low): CLOSED as design_survey_locked 2026-10-02. SITE_LAT=33.0 Dallas sandbox (params.py); jurisdiction_theme=USA_Dallas_class; GHEX T_source=285 K / k_ground=1.5 / Q_surplus=0 (ST-ORC-01). Field bore/conductivity measurement still labeled external — not claimed as measured.
- **WP_TRUE_CLOSURE_RESIDUALS** (low): Species residuals≈0 (Rev F capture retained). loops_closed still false — C3 Present CAD (vcd_remin_on_site=false). C4 BOM complete. See WP_TRUE_CLOSURE_RESIDUALS.md / WP_C4_GHEX_L3.md.
- **WP_L3_CLAIM_DISCIPLINE** (low): WP-L3 evidence pack 2026-10-02: WCC/SCC recomputed; solver dry-run partial; C4 true; C3 false → loops_closed remains false. WP-L4: never flip loops_closed/mvs_equivalent from topology or BOM alone; Present CAD gate explicit.
- **WP_C4_REPRAP_BOM** (low): CLOSED 2026-10-02: AQS-BOM-SC-001 Rev F matrix + equipment ID map warrants reprap_bom_complete=true. *_on_site remain false (C3≠C4).
