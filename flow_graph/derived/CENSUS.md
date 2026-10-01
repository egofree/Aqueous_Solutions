# Flow graph census — DERIVED

Source: AQS-FLOW-GRAPH-001 Rev B
Generated: 2026-10-01

- nodes: **91** (present=79, placeholder=12)
- edges: **114** (present=78, placeholder=36)
- by namespace: {'S': 82, 'SANDBOX': 2, 'TBD': 1, 'IA': 29}
- locks: layered_views, full_depth_now, efd_three_layers, typed_graph_sole, present_plus_placeholders

## Gaps

- **S17_bridged** (low): S17 labeled on graph-bridged electrical_sld.png; still sparse on line PFDs
- **DOCK_EXPORT_TBD** (high): Placeholder edge; no S## invented; shown as TBD on mass_flow_pfd
- **MEOH_MF_SLD_BRIDGED** (low): S73–S82 on graph-bridged mass_flow_pfd + S79 on electrical_sld; MF claim_status rows still end S72
- **PUMPED_HYDRO_PFD** (medium): Dedicated hydro_dock_pfd graph-bridged; HYDRO elec still rate null / placeholder on SLD
- **DOCK_PFD** (medium): Dedicated hydro_dock_pfd graph-bridged; DOCK_EXPORT_TBD remains TBD (no S##)
- **INTRA_AISLE_RATES** (medium): IA-* IDs assigned; rates null until measured/issued
- **SANDBOX_S08G_S14X** (medium): Keep sandbox or promote — do not invent third ID
- **GENERATOR_MIGRATION** (medium): Other matplotlib pfd_scripts/* still legacy bootstrap; electrical_sld + mass_flow_pfd graph-bridged
