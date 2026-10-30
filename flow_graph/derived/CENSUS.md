# Flow graph census — DERIVED

Source: AQS-FLOW-GRAPH-001 Rev AC
Graph date: 2026-10-17 (output is a pure function of the graph; no run date, so regen is idempotent)

- nodes: **200** (present=182, placeholder=16)
- edges: **650** (present=598, placeholder=6)
- by namespace: {'IA': 486, 'TBD': 1, 'S': 162, 'SANDBOX': 1}
- locks: layered_views, full_depth_now, efd_three_layers, typed_graph_sole, present_plus_placeholders, site_lat_design_sandbox, true_closure_residuals_wp, reprap_bom_complete_c4, site_ghex_design_survey_locked, wp_l3_evidence_pack, wp_l4_claim_discipline, wp_ew_cascade_explode

## Gaps

- **DOCK_EXPORT_TBD** (high): Placeholder edge; no S## invented; shown as TBD on mass_flow_pfd
- **DOCK_PFD** (medium): Dedicated hydro_dock_pfd graph-bridged; DOCK_EXPORT_TBD remains TBD (no S##)
- **GENERATOR_MIGRATION** (medium): Other matplotlib flow_graph/exporters/matplotlib/* still legacy bootstrap; electrical_sld + mass_flow_pfd graph-bridged
- **INTRA_AISLE_RATES** (medium): IA-* IDs assigned; rates null until measured/issued
- **MEOH_MF_SLD_BRIDGED** (low): S73–S82 on graph-bridged mass_flow_pfd + S79 on electrical_sld; MF claim_status rows still end S72
- **PUMPED_HYDRO_PFD** (medium): Dedicated hydro_dock_pfd graph-bridged; HYDRO elec still rate null / placeholder on SLD
- **REV_E_SYNC_SKIPPED_STREAMS** (low): Still skipped (handoff or Rev E conflict): IA-REC-Q3, IA-WET-C29-01, IA-GLASS-Q2/IA-OIL-Q1 (HL-* owns), other Rev G study IA-*. NOW ON GRAPH: S83–S86 + relief/headers from Rev F; EW_3…EW_8 cascade (incl. IA-EW-10 EW_4→EW_5); IA-HDR-H2-01…04 Faraday from E+local.
- **S17_bridged** (low): S17 labeled on graph-bridged electrical_sld.png; still sparse on line PFDs
- **SANDBOX_S08G_S14X** (medium): Keep sandbox or promote — do not invent third ID
- **WP_EW_CASCADE_EXPLODE** (low): EW_3…EW_8 present. Cascade hops EW_1→…→EW_9 complete incl. IA-EW-10 EW_4→EW_5 (Rev F was missing that hop). IA-HDR-H2 Faraday restored. loops_closed=false.
- **WP_L2_PRESENT_CAD** (medium): Equipment IDs / BOM matrix on disk (C4 true). FreeCAD Features for VCD/REMIN/LITHO/BLOW/ELC absent (placeholder_skip). *_on_site=false (C3). AHJ design-basis USA_Dallas_class — no fake certificates. Primary remaining loops_closed gate under Rev E topology.
- **WP_L2_SITE_SURVEY** (low): CLOSED as design_survey_locked 2026-10-02 (reaffirmed on Rev E sync). SITE_LAT=33.0 Dallas sandbox (params.py); jurisdiction_theme=USA_Dallas_class; GHEX design-basis ST-ORC-01. Field bore/conductivity still external — not claimed as measured.
- **WP_TRUE_CLOSURE_RESIDUALS** (low): S87/S88 left in place under Mike HOLD pending endpoint write-up (the unpublished planning note S87_S88_ENDPOINTS). IA-HDR-H2-01…04 restored after EW_3…EW_8 nodes. loops_closed still false — C3 Present CAD.
- **FOUNDRY_POLY_MISSING_EDGES** (low): Foundry/polymers sizing pass Rev B (AQS-DUTY-072/073): the D-DOCK feedstock program unblocked the pot/cell, Kroll and investment trains (A-M-284.285). Remaining absent/blocked: DRAW feed (CAST/ROLL->DRAW) and FORGE edges (both N+1 alternates at standby-zero, A-M-283), FILM_CAST feed, POLY_COND outlet to PELLET, SALT_FEED source (flux now fed from the Kroll drag-out), F_RECOVER feed (F recovery, Q-013). The Kroll gangue/Fe terms wait on the concentrate assays (A-M-284).
