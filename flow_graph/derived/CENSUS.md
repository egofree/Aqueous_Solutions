# Flow graph census — DERIVED

Source: AQS-FLOW-GRAPH-001 Rev M
Generated: 2026-10-08

- nodes: **123** (present=122, placeholder=1)
- edges: **179** (present=179, placeholder=0)
- by namespace: {'IA': 74, 'TBD': 1, 'S': 102, 'SANDBOX': 2}
- locks: layered_views, full_depth_now, efd_three_layers, typed_graph_sole, present_plus_placeholders, site_lat_design_sandbox, true_closure_residuals_wp, reprap_bom_complete_c4, site_ghex_design_survey_locked, wp_l3_evidence_pack, wp_l4_claim_discipline, wp_ew_cascade_explode

## Gaps

- **DOCK_EXPORT_TBD** (medium): Rev L: present and rated (MFG goods export, by difference at MFG_SHOP). ID stays DOCK_EXPORT_TBD: no S## invented.
- **DOCK_PFD** (medium): Dedicated hydro_dock_pfd graph-bridged; DOCK_EXPORT_TBD remains TBD (no S##)
- **GENERATOR_MIGRATION** (medium): Other matplotlib pfd_scripts/* still legacy bootstrap; electrical_sld + mass_flow_pfd graph-bridged
- **INTRA_AISLE_RATES** (low): Rev L (AQS-DUTY-010): every present IA-* edge rated with rate_basis/rate_source in params. IA-POL-01 and IA-ESS-MEOH-CHG/DIS retired.
- **MEOH_MF_SLD_BRIDGED** (low): S73–S82 on graph-bridged mass_flow_pfd + S79 on electrical_sld; MF claim_status rows still end S72
- **PUMPED_HYDRO_PFD** (low): Rev L: IA-ESS-HYDRO-CHG/DIS 200 t/d (one cycle/d), S22/S23 0.409 kW hydraulic, IA-ESS-HYDRO-ELEC 0.292 kW (7 kWh/cycle).
- **REV_E_SYNC_SKIPPED_STREAMS** (low): Still skipped (handoff or Rev E conflict): IA-REC-Q3, IA-WET-C29-01, IA-GLASS-Q2/IA-OIL-Q1 (HL-* owns), other Rev G study IA-*. NOW ON GRAPH: S83–S86 + relief/headers from Rev F; EW_3…EW_8 cascade (incl. IA-EW-10 EW_4→EW_5); IA-HDR-H2-01…04 Faraday from E+local.
- **S17_bridged** (low): S17 labeled on graph-bridged electrical_sld.png; still sparse on line PFDs
- **SANDBOX_S08G_S14X** (medium): Keep sandbox or promote — do not invent third ID
- **WP_EW_CASCADE_EXPLODE** (low): EW_3…EW_8 present. Cascade hops EW_1→…→EW_9 complete incl. IA-EW-10 EW_4→EW_5 (Rev F was missing that hop). IA-HDR-H2 Faraday restored. loops_closed=false.
- **WP_L2_PRESENT_CAD** (medium): Equipment IDs / BOM matrix on disk (C4 true). FreeCAD Features for VCD/REMIN/LITHO/BLOW/ELC absent (placeholder_skip). *_on_site=false (C3). AHJ design-basis USA_Dallas_class — no fake certificates. Primary remaining loops_closed gate under Rev E topology.
- **WP_L2_SITE_SURVEY** (low): CLOSED as design_survey_locked 2026-10-02 (reaffirmed on Rev E sync). SITE_LAT=33.0 Dallas sandbox (params.py); jurisdiction_theme=USA_Dallas_class; GHEX design-basis ST-ORC-01. Field bore/conductivity still external — not claimed as measured.
- **WP_TRUE_CLOSURE_RESIDUALS** (medium): Rev M: S87 and S88 retired (no physical flow; AQS-DUTY-011). Required studies in REV_M_REQUIRED_STUDIES. loops_closed false.
- **REV_M_CONSERVATION** (low): AQS-DUTY-011 node conservation (+-1 %, daily average): no open node balances. See REV_M_CLOSURE_DUTY.md.
- **REV_M_REQUIRED_STUDIES** (medium): RS-LEACH-H2: leach lid H2 under oxidant upset (Cl2 sparge or O2 off): purge dilution to < 25 % LFL and interlock. | RS-HAB-N2: hab envelope leak rate at operating pressure; sets HDR_N2 -> HABITATION make-up (the only N2 consumer candidate). | RS-RESIDUE-TCLP: S96 sink residue and S97 cake leachate characterization before disposal or sale. | RS-DSP: bench confirmation that glass Na leaves in the pH-9 cake as sodium aluminosilicate (Na <= Al). | RS-CL2-SPARGE: anode Cl2 absorption in LEACH_CSTR_1 (0.95 basis) and the Fe3+ effect on EW CE. | RS-GHEX-RECHARGE: borefield temperature drift under S102 continuous recharge (field bore data external, design_survey_locked).
