# Documentation map

This folder holds the plant's authority documents and everything generated
from the plant flow graph. Use this page to find your way in. The repository
[README](../README.md) explains the project, the authority chain and how to run
the model; the [glossary](GLOSSARY.md) explains the names, acronyms and
identifiers used throughout.

## How to read these documents

- **The graph is the authority.** `flow_graph/plant_flow_graph.json` is the
  sole topology authority. Where a document and the graph disagree, the graph
  wins and the document is regenerated.
- **Generated or hand-written.** Files listed in
  [DERIVED_REVISIONS.md](DERIVED_REVISIONS.md) are written by
  `python3 -m flow_graph.param.regen`; change their generator or inputs, never
  the file. Everything else is hand-written.
- **Document numbers.** Each document carries an `AQS-...` number, a revision
  and a date. [DOC_REGISTER.md](DOC_REGISTER.md) lists them. A few planning
  documents share AQS-PLAN-007 because they are parts of one plan.
- **Identifiers.** Task ids (`X-PAR-12`), assumption ids (`A-M-145`), stream
  ids (`S64`) and graph revisions (`Rev AC`) are explained in the
  [glossary](GLOSSARY.md#project-identifiers-and-conventions).
- **Sector names.** The current sector ids are those in the graph (see
  [SECTOR_DEFINITIONS.md](SECTOR_DEFINITIONS.md) and the glossary). Older
  documents and dated notes may use former names, for example `WET` for the
  line now called `DIGESTER`.
- **Former paths.** Some older documents refer to files that lived in a
  previous shared layout and are not part of this repository, for example
  process overviews such as `POWER/Power_System_overview.md` or numbered
  chapters such as `03-silicon-wafer-fabrication.md`, and process-sheet images
  named `*_pfd.png` that are now produced on demand by
  `flow_graph/exporters/`. Treat these as historical references.

## Subfolders

| Folder | Contents |
|---|---|
| [duties/](duties/) | Per-unit duty sheets (generated) |
| [sizing/](sizing/) | Per-unit sizing calculations (generated) |
| [nozzles/](nozzles/) | Per-unit nozzle schedules (generated) |
| [pid/](pid/) | Unit P&ID sheets (generated) |
| [iso/](iso/) | Piping isometric sheets (generated) |
| [process/](process/) | Retired: its copies of equipment lists were removed; the current lists are in this folder ([process/README.md](process/README.md)) |
| [fab/](fab/) | Per-unit fabrication routes |
| [inventory/](inventory/) | Building-block inventories (motors, wire, pipe, parts) |
| [drawings/](drawings/) | Drawing sheets (SVG) |
| [plc/](plc/) | Control program source per sector (IEC 61131-3 structured text) |
| [data/](data/) | Input data such as the PV typical-meteorological-year series |
| [notes/](notes/) | Dated change records, rulings and evidence notes |
| [internal/](internal/README.md) | Working notes kept for history: handoffs, run logs, superseded plans and status boards. Not design authority |

Scripts named `_*.py` in this folder are the study calculators and document
generators; most run as stages of the regen pipeline
(`flow_graph/param/regen_manifest.json`).

## Start here

The documents that explain how the design is organised and where its numbers come from.

| Document | Number | Title |
|---|---|---|
| [AUTHORITY.md](AUTHORITY.md) | AQS-AUTH-001 | CAD authority lock |
| [PARAMETRIC_MODEL.md](PARAMETRIC_MODEL.md) | AQS-PAR-001 | Parametric model |
| [SECTOR_DEFINITIONS.md](SECTOR_DEFINITIONS.md) | AQS-SEC-001 | Sector Definitions catalogue — plant sector_id map (generated from the graph) |
| [STREAM_REGISTER.md](STREAM_REGISTER.md) | AQS-STR-001 | Stream register — inter-block only |
| [GLOSSARY.md](GLOSSARY.md) | AQS-GLO-001 | Glossary |
| [DOC_REGISTER.md](DOC_REGISTER.md) | AQS-REG-001 | Document number register |
| [ASSUMPTIONS_REGISTER.md](ASSUMPTIONS_REGISTER.md) | AQS-REG-002 | Assumptions register |
| [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) | AQS-OQ-001 | Open questions |
| [DERIVED_REVISIONS.md](DERIVED_REVISIONS.md) | AQS-GOV-006 | Derived file revisions |

## Design basis, codes and house style

| Document | Number | Title |
|---|---|---|
| [AQS-STD-001.md](AQS-STD-001.md) | AQS-STD-001 | Unit duty standard |
| [CODE_BASIS.md](CODE_BASIS.md) | AQS-STD-007 | Code basis |
| [STANDARDS_BASIS.md](STANDARDS_BASIS.md) | AQS-STD-003 | Standards basis for the audit fixes |
| [STANDARDS_LIST.md](STANDARDS_LIST.md) | AQS-STD-004 | Codes and standards list |
| [COMPLIANCE_MATRIX.md](COMPLIANCE_MATRIX.md) | AQS-COMPL-001 | Compliance matrix — design intent vs code themes |
| [PERMITS.md](PERMITS.md) | AQS-COD-002 | Permit list |
| [SITE_BASIS.md](SITE_BASIS.md) | AQS-SITE-002 | Site basis — AQS-SITE-002 Rev A |
| [LOCALIZATION_PLAN.md](LOCALIZATION_PLAN.md) | AQS-PLAN-011 | Localization plan: site profiles and locale variants |
| [SITE_BASIS_DEATH_VALLEY.md](SITE_BASIS_DEATH_VALLEY.md) | AQS-SITE-006 | Death Valley site basis - environment, design consequences and first locale-run closure |
| [SITE_BASIS_FLOATING_ISLAND.md](SITE_BASIS_FLOATING_ISLAND.md) | AQS-SITE-007 | Floating island site basis - seawater environment, scaling actions and first locale-run closure |
| [SITE_BASIS_ANTARCTIC.md](SITE_BASIS_ANTARCTIC.md) | AQS-SITE-008 | Antarctic site basis - cold-climate environment, scaling actions, closure status |
| [SITE_BASIS_LEO.md](SITE_BASIS_LEO.md) | AQS-SITE-010 | LEO site basis - microgravity environment, scaling findings, design gap |
| [SITE_BASIS_MARS.md](SITE_BASIS_MARS.md) | AQS-SITE-009 | Mars site basis - CO2 atmosphere, ground-ice water, pressurised shells, partial gravity |
| [SITE_POWER.md](SITE_POWER.md) | AQS-SITE-005 | Site power portfolio and redundancy of energy and life-support functions (generated) |
| [SITE_SCALING.md](SITE_SCALING.md) | AQS-SITE-004 | Site scaling: capabilities, scaling actions and unit needs for the selected site (generated) |
| [FEED_ASSAY.md](FEED_ASSAY.md) | AQS-ASSAY-001 | Feed assay |
| [ASSAY.md](ASSAY.md) | AQS-ASSAY-002 | Assay |
| [MATERIALS_STD.md](MATERIALS_STD.md) | AQS-STD-002 | Materials standard |
| [MATERIALS_SEC3.md](MATERIALS_SEC3.md) | AQS-STD-006 | Duty section 3 material selections, batch issue (AQS-STD-006) |
| [UNIT_MATERIALS.md](UNIT_MATERIALS.md) | AQS-STD-005 | Per-unit material selections (duty section 3 sweep) |
| [ASME_CODE_INTENT.md](ASME_CODE_INTENT.md) | AQS-ASME-002 | In-house code intent per unit |
| [ASME_CLASS_SHEETS.md](ASME_CLASS_SHEETS.md) | AQS-ASM-001 | ASME vessel inventory & B31.3 piping class sheets (templates) |
| [H2_EMBRITTLEMENT_REVIEW.md](H2_EMBRITTLEMENT_REVIEW.md) | AQS-REV-H2-001 | Hydrogen embrittlement review |
| [DOC_STYLE.md](DOC_STYLE.md) | AQS-DOC-002 | Documentation style (practical application) |
| [DRAWING_STANDARD.md](DRAWING_STANDARD.md) | AQS-DWG-001 | Drawing standard and title block |
| [FONTS.md](FONTS.md) | AQS-FONT-001 | Fonts for 3D sign glyphs |

## Model, balances and closure

Mass and energy closure studies built on the graph. Several are generated; see DERIVED_REVISIONS.md.

| Document | Number | Title |
|---|---|---|
| [BALANCE_RECONCILIATION.md](BALANCE_RECONCILIATION.md) | AQS-PAR-003 | Mass balance reconciliation |
| [BALANCE_CLOSE.md](BALANCE_CLOSE.md) | AQS-DUTY-078 | Balance close |
| [BALANCE_CLOSE_N.md](BALANCE_CLOSE_N.md) | AQS-DUTY-012 | Balance close, remaining nodes |
| [REV_M_CLOSURE_DUTY.md](REV_M_CLOSURE_DUTY.md) | AQS-DUTY-011 | Rev M closure: node balances, chloride loop, heater ratings and Q4 sin |
| [EDGE_RATING_DUTY.md](EDGE_RATING_DUTY.md) | AQS-DUTY-010 | Edge rating and node conservation |
| [MASS_FLOW.md](MASS_FLOW.md) | AQS-MF-001 | Mass-flow claim status |
| [MASS_DISPOSITION.md](MASS_DISPOSITION.md) | AQS-DUTY-023 | Residual close |
| [GAS_SPECIES.md](GAS_SPECIES.md) | AQS-PAR-004 | Oxygen species ledger |
| [O2_SOURCE.md](O2_SOURCE.md) | AQS-PAR-005 | O2 source duty summary |
| [O2_SOURCE_AUDIT.md](O2_SOURCE_AUDIT.md) | AQS-PAR-005A | O2 source study |
| [CO2_HEADER_DUTY.md](CO2_HEADER_DUTY.md) | AQS-DUTY-009 | HDR_CO2 consumer duty |
| [S83_S88.md](S83_S88.md) | AQS-DUTY-082 | S83–S88 endpoints |
| [COMPLETION_DUTIES.md](COMPLETION_DUTIES.md) | AQS-DUTY-007 | Completion duties |
| [CHECKS.md](CHECKS.md) | AQS-DUTY-080 | Cathode size from the sheet |
| [PATHWAY_AUDIT.md](PATHWAY_AUDIT.md) | AQS-DUTY-024 | No placeholders |
| [GRAPH_AUDIT.md](GRAPH_AUDIT.md) | AQS-AUD-GRAPH-001 | Graph audit |
| [RESIZE_SWEEP.md](RESIZE_SWEEP.md) | AQS-PLAN-010 | Bounding-case resize sweep |
| [MVS_SIZE.md](MVS_SIZE.md) | AQS-DUTY-038 | Sector size and MVS |
| [MVS_STUDY_CLOSE.md](MVS_STUDY_CLOSE.md) | AQS-STUDY-CLOSE-001 | Study close — the 15 skipped nodes |
| [SURPLUS_PASS_THRESHOLDS.md](SURPLUS_PASS_THRESHOLDS.md) | AQS-SUR-001 | Surplus pass thresholds — study freeze criteria (MVS) |
| [SCALE_DOWN_UNRECLAIMED.md](SCALE_DOWN_UNRECLAIMED.md) | AQS-SCALE-UR-001 | Scale-down → unreclaimed-resource map |
| [SELF_COPY_BOM.md](SELF_COPY_BOM.md) | AQS-BOM-SC-001 | Self-copy critical-path BOM — parts × feedstock (RepRap-class) |

## Process line (DIGESTER sector: leach, electrowinning, regeneration)

| Document | Number | Title |
|---|---|---|
| [CSTR_NOZZLE_SCHEDULE.md](CSTR_NOZZLE_SCHEDULE.md) | AQS-NZ-001 | LEACH CSTR 1 nozzle schedule |
| [EW_MODULE.md](EW_MODULE.md) | AQS-EW-MOD-001 | Electrowinning module |
| [RECT_EW.md](RECT_EW.md) | AQS-ELEC-004 | EW rectifier sizing (RECT-EW) |
| [BUSBAR.md](BUSBAR.md) | AQS-BUS-001 | Rectifier bus |
| [CUT_LIST.md](../models/openscad/foam_ew/CUT_LIST.md) | AQS-FOAM-001 | Foam EW cascade — cut list (generated in `models/openscad/foam_ew/`) |
| [DECISIONS.md](../models/openscad/foam_ew/DECISIONS.md) | - | Decisions — foam-board EW cascade (in `models/openscad/foam_ew/`) |
| [INTERNALS.md](INTERNALS.md) | AQS-DSN-INT-001 | Unit internals register |
| [ELECTRODE_FAB.md](ELECTRODE_FAB.md) | AQS-MFG-ELC-001 | Electrode fabrication / coating — architecture (in scope) |
| [OXIDIZER_REAGENTS.md](OXIDIZER_REAGENTS.md) | AQS-DSN-OX-001 | Nitric acid and hydrogen peroxide systems |
| [SOLVENT_ROUTE.md](SOLVENT_ROUTE.md) | AQS-DUTY-026 | Sugar and reagent stores |
| [SILICON.md](SILICON.md) | AQS-SI-001 | Silicon reduction |
| [POLYMER_HX_SIZING.md](POLYMER_HX_SIZING.md) | AQS-DUTY-049 | Polymer exchanger sizing, HX-5 and HX8 |

## Gas handling and cryogenics

| Document | Number | Title |
|---|---|---|
| [SCRUBBER_CHEMISTRY.md](SCRUBBER_CHEMISTRY.md) | AQS-GAS-002 | Scrubber chemistry |
| [FAN_STACK.md](FAN_STACK.md) | AQS-GAS-003 | Fan curves and stack heights |
| [VENT_CLOSURE.md](VENT_CLOSURE.md) | AQS-VENT-001 | Vent and stack closure — scrub / regen or CRYO |
| [VENT_SCRUB_EQUIPMENT.md](VENT_SCRUB_EQUIPMENT.md) | AQS-EQP-VENT-001 | Vent / scrub / regenerator equipment stubs |
| [CRYO_ASU.md](CRYO_ASU.md) | AQS-DUTY-018 | Cold box gas rate |
| [CRYO_COLD_BOX.md](CRYO_COLD_BOX.md) | AQS-CRY-002 | Cryogenic cold-box internals |
| [CRYO_EQUIPMENT.md](CRYO_EQUIPMENT.md) | AQS-EQP-CRY-001 | Cryogenic equipment list |
| [COLD_BOX.md](COLD_BOX.md) | AQS-CRY-003 | Cold box |
| [SIDE_CRYO.md](SIDE_CRYO.md) | AQS-SIDE-003 | Cold box module |

## Wafer fab, PV cells and fab utilities

| Document | Number | Title |
|---|---|---|
| [WAFER_FAB_EQUIPMENT.md](WAFER_FAB_EQUIPMENT.md) | AQS-EQP-FAB-001 | Wafer fab equipment / process list |
| [FAB_UPW.md](FAB_UPW.md) | AQS-EQP-FAB-UPW-001 | Fab UPW — equipment list |
| [FAB_WET_REAGENTS.md](FAB_WET_REAGENTS.md) | AQS-EQP-FAB-RGN-001 | Fab wet reagents — wet-line synth forks |
| [FAB_WET_INTERFACE.md](FAB_WET_INTERFACE.md) | AQS-IF-FAB-WET-001 | Fab ↔ wet-line interface |
| [SOLAR_CELL_EQUIPMENT.md](SOLAR_CELL_EQUIPMENT.md) | AQS-EQP-FAB-PV-001 | Solar-cell branch — equipment schedule (architecture Partial) |
| [PV_CELL_MOD.md](PV_CELL_MOD.md) | AQS-PV-001 | Photovoltaic cell |
| [ALIGNER.md](ALIGNER.md) | AQS-LITH-001 | Contact aligner |

## Farm, habitation and water

| Document | Number | Title |
|---|---|---|
| [FARM_EQUIPMENT.md](FARM_EQUIPMENT.md) | AQS-EQP-FRM-001 | Farm equipment / process list |
| [NUTRIENT_DOSE.md](NUTRIENT_DOSE.md) | AQS-EQP-NUT-001 | Nutrient dose / N-P process list |
| [GREENHOUSE_ENVELOPE.md](GREENHOUSE_ENVELOPE.md) | AQS-TRR-GH-001 | Enclosed greenhouse envelope — schedule stub (optional FreeCAD) |
| [GREENHOUSE_WATER.md](GREENHOUSE_WATER.md) | AQS-DUTY-013 | Greenhouse water and battery margin |
| [TERRACE_LANDSCAPE.md](TERRACE_LANDSCAPE.md) | AQS-TRR-001 | Terrace landscape — planting, irrigation, open vs greenhouse |
| [HAB_FIXTURES.md](HAB_FIXTURES.md) | AQS-HAB-001 | Habitation fixtures |
| [HAB_WATER.md](HAB_WATER.md) | AQS-EQP-HAB-001 | Habitation water — equipment list |
| [WATER_PURIFICATION.md](WATER_PURIFICATION.md) | AQS-WTR-001 | Water purification — habitation and fab UPW |
| [LIFE_FITOUT_PLAN.md](LIFE_FITOUT_PLAN.md) | AQS-LIFE-001 | Habitation and farm fit-out plan |
| [LIFE_HEADERS.md](LIFE_HEADERS.md) | AQS-PIP-002 | Life-header racks |
| [LIFE_MEP.md](LIFE_MEP.md) | AQS-MEP-001 | Life MEP — Phase D (duct / fixture / one-line study) |
| [LIFE_NOZZLE_SCHEDULE.md](LIFE_NOZZLE_SCHEDULE.md) | AQS-NZ-002 | Campus unit nozzle schedule |
| [SIDE_ASSAY.md](SIDE_ASSAY.md) | AQS-SIDE-001 | Assay and relief |

## Energy, storage and heat

| Document | Number | Title |
|---|---|---|
| [POWER.md](POWER.md) | AQS-PWR-001 | Power |
| [POWER_SIZING.md](POWER_SIZING.md) | AQS-ELEC-007 | Storage and generation sizing |
| [CONTINUOUS_KW_REQUIREMENTS.md](CONTINUOUS_KW_REQUIREMENTS.md) | AQS-REQ-KW-001 | Continuous kW requirements — GEN / FC / PECVD / belt fire / CRYO / M |
| [ESS_DUTY_MATRIX.md](ESS_DUTY_MATRIX.md) | AQS-ESS-001 | ESS duty matrix — ZnBr₂ / MeOH / pumped hydro (study) |
| [FLOW_BATTERY.md](FLOW_BATTERY.md) | AQS-ESS-002 | ZnBr2 flow battery |
| [ZNBR2_STACK_TEST.md](ZNBR2_STACK_TEST.md) | AQS-TST-002 | ZNBR2 stack test |
| [MEOH_TRAIN.md](MEOH_TRAIN.md) | AQS-MeOH-001 | Methanol train — diverse MeOH sources + IEM fuel cell (gap fill) |
| [MEOH_EQUIPMENT.md](MEOH_EQUIPMENT.md) | AQS-EQP-MEOH-001 | Methanol train equipment list |
| [FUEL_CELL.md](FUEL_CELL.md) | AQS-FC-001 | PEM fuel cell — plant H₂ / O₂ on Sol-Ark DC bus |
| [FUEL_CELL_EQUIPMENT.md](FUEL_CELL_EQUIPMENT.md) | AQS-EQP-FC-001 | Fuel-cell equipment list |
| [BACKUP_GEN_EQUIPMENT.md](BACKUP_GEN_EQUIPMENT.md) | AQS-EQP-GEN-001 | Backup generator equipment list |
| [GEOTHERMAL_BACKUP.md](GEOTHERMAL_BACKUP.md) | AQS-PWR-002 | Geothermal loop and backup generator |
| [GEOTHERMAL_EQUIPMENT.md](GEOTHERMAL_EQUIPMENT.md) | AQS-EQP-GEO-001 | Geothermal equipment list |
| [HYDRO_SITING.md](HYDRO_SITING.md) | AQS-RED-002 | Pumped-hydro reservoir siting trade study |
| [WATER_TOWER.md](WATER_TOWER.md) | AQS-BLD-014 | Water tower: pumped-hydro reservoirs in the building |
| [HEAT_LADDER.md](HEAT_LADDER.md) | AQS-HEAT-LADDER-001 | Dual heat ladder |
| [HEAT_LADDER_DUTIES.md](HEAT_LADDER_DUTIES.md) | AQS-DUTY-008 | Heat-ladder edge duties |
| [HVAC.md](HVAC.md) | AQS-THM-002 | Ventilation and HVAC design |
| [INSULATION_SCHEDULE.md](INSULATION_SCHEDULE.md) | AQS-THM-003 | Insulation schedule |
| [RED_AUDIT.md](RED_AUDIT.md) | AQS-RED-001 | Redundancy audit, energy and life support |

## Electrical

| Document | Number | Title |
|---|---|---|
| [ELECTRICAL.md](ELECTRICAL.md) | AQS-ELC-001 | Electrical analysis |
| [ONE_LINE.md](ONE_LINE.md) | AQS-ELEC-002 | One line |
| [LOAD_LIST.md](LOAD_LIST.md) | AQS-ELEC-003 | Load list |
| [COLLECTION_BUS.md](COLLECTION_BUS.md) | AQS-ELEC-008 | Collection bus sections |
| [CABLE_SCHEDULE.md](CABLE_SCHEDULE.md) | AQS-ELEC-010 | Cable and busbar schedule |
| [GROUNDING.md](GROUNDING.md) | AQS-ELEC-005 | Grounding and bonding |
| [PROTECTION.md](PROTECTION.md) | AQS-ELEC-006 | Protection and coordination |
| [HAZ_AREA.md](HAZ_AREA.md) | AQS-ELEC-009 | Hazardous area classification |
| [ELECTRONICS.md](ELECTRONICS.md) | AQS-ELEC-001 | Electronics bay |

## Piping, instruments and control

| Document | Number | Title |
|---|---|---|
| [LINE_LIST.md](LINE_LIST.md) | AQS-PIP-004 | Plant line list |
| [PIPING_CLASSES.md](PIPING_CLASSES.md) | AQS-PIP-003 | Piping class sheets |
| [PIPE_SPECS.md](PIPE_SPECS.md) | AQS-INV-006 | Pipe family production plans |
| [PIPES.md](PIPES.md) | AQS-PIP-006 | Pipe junctions |
| [SUPPORTS.md](SUPPORTS.md) | AQS-PIP-005 | Pipe supports and thermal flexibility |
| [ISO_DRAWING_INDEX.md](ISO_DRAWING_INDEX.md) | AQS-ISO-000 | Isometric fabrication set |
| [ISO_ROUTES.md](ISO_ROUTES.md) | AQS-ISO-001 | Isometric route data |
| [ISO_SHEETS.md](ISO_SHEETS.md) | AQS-ISO-002 | Isometric sheets |
| [RELIEF.md](RELIEF.md) | AQS-REL-001 | Relief |
| [RELIEF_REGISTER.md](RELIEF_REGISTER.md) | AQS-SAF-004 | Relief register |
| [INSTRUMENT_INDEX.md](INSTRUMENT_INDEX.md) | AQS-CTL-001 | Instrument index |
| [INSTRUMENT_LOOPS.md](INSTRUMENT_LOOPS.md) | AQS-INST-001 | Instrument loops |
| [CONTROL_ARCH.md](CONTROL_ARCH.md) | AQS-CTL-002 | Control philosophy and PLC architecture |
| [CONTROL_SOFTWARE.md](CONTROL_SOFTWARE.md) | AQS-CTL-004 | Control program source and scan simulation |
| [CAUSE_EFFECT.md](CAUSE_EFFECT.md) | AQS-CTL-003 | Safety instrumented functions and cause and effect |
| [WELD_MAP.md](WELD_MAP.md) | AQS-WLD-001 | Weld and joint map |
| [WPS_REGISTER.md](WPS_REGISTER.md) | AQS-WLD-002 | WPS and PQR register |

## Safety

| Document | Number | Title |
|---|---|---|
| [HAZOP.md](HAZOP.md) | AQS-SAF-001 | HAZOP worksheets |
| [HAZOP_ACTION_REGISTER.md](HAZOP_ACTION_REGISTER.md) | AQS-SAF-008 | HAZOP action register |
| [HAZARD_SEPARATION.md](HAZARD_SEPARATION.md) | AQS-HSE-001 | Hazard separation and containment — design locks |
| [HAZARD_SEPARATION_LAYOUT.md](HAZARD_SEPARATION_LAYOUT.md) | AQS-SAF-007 | Hazard separation applied to the layout |
| [HAZMAT_SEPARATION.md](HAZMAT_SEPARATION.md) | AQS-BLD-011 | Incompatible hazardous-material separation |
| [FIRE_PROTECTION.md](FIRE_PROTECTION.md) | AQS-SAF-005 | Fire protection and detection |
| [GAS_DETECTION.md](GAS_DETECTION.md) | AQS-SAF-006 | Gas detection |
| [EGRESS_CALC.md](EGRESS_CALC.md) | AQS-EGR-001 | Means of egress — study calculation (NFPA 101 / IBC Ch. 10 themes) |
| [HALL_EGRESS.md](HALL_EGRESS.md) | AQS-EGR-002 | Extension hall egress |
| [ENCLOSURE_EGRESS.md](ENCLOSURE_EGRESS.md) | AQS-BLD-018 | Enclosure, floor plates, stairs and egress |

## Building, site and structure

| Document | Number | Title |
|---|---|---|
| [BUILDING_STACK.md](BUILDING_STACK.md) | AQS-BLD-001 | Building stack — vertical campus |
| [CAMPUS_PLAN.md](CAMPUS_PLAN.md) | AQS-CMP-001 | Campus plan — recycle core + farm + fab + habitation + cryo |
| [SITE_ACCESS.md](SITE_ACCESS.md) | AQS-SITE-001 | Site access — orientation, north dock, service / egress |
| [SITE_ACCESS_CHECK.md](SITE_ACCESS_CHECK.md) | AQS-SITE-003 | Site access and dock check |
| [ACCESS_CHECK.md](ACCESS_CHECK.md) | AQS-BLD-012 | Access and electrical working-space check |
| [FOUNDATION.md](FOUNDATION.md) | AQS-BLD-017 | Foundation design |
| [FRAME_SYSTEM.md](FRAME_SYSTEM.md) | AQS-MOD-002 | Frame system |
| [FRAME_CHECK.md](FRAME_CHECK.md) | AQS-BLD-016 | Building frame member check |
| [STRUCT_LOADS.md](STRUCT_LOADS.md) | AQS-BLD-013 | Equipment structural loads |
| [MODULE.md](MODULE.md) | AQS-MOD-001 | Module standard |
| [PATH_MODULES.md](PATH_MODULES.md) | AQS-PATH-001 | Path modules on the frame |
| [LIFTING.md](LIFTING.md) | AQS-BLD-015 | Lifting and cranes |
| [RIGGING_PLANS.md](RIGGING_PLANS.md) | AQS-ASM-003 | Rigging plans |
| [INSTALL_SEQUENCE.md](INSTALL_SEQUENCE.md) | AQS-ASM-002 | Install sequence |
| [GA_CHECK.md](GA_CHECK.md) | AQS-BLD-010 | General arrangement clash check |
| [SCALE_MODEL.md](SCALE_MODEL.md) | AQS-SCALE-001 | Scale model — parametric building growth |
| [PHASE_F_ENVELOPES.md](PHASE_F_ENVELOPES.md) | AQS-PHF-001 | Phase F — farm / wafer fab / habitation / cryo envelopes |
| [PHASE9_INTERFACES.md](PHASE9_INTERFACES.md) | AQS-IF-009 | Phase 9 interfaces |
| [SIGN_SCHEDULE.md](SIGN_SCHEDULE.md) | AQS-SIGN-001 | Sign and label schedule |

## Manufacturing, parts and testing

| Document | Number | Title |
|---|---|---|
| [MFG_SHOP_EQUIPMENT.md](MFG_SHOP_EQUIPMENT.md) | AQS-EQP-MFG-001 | MFG shop equipment list |
| [MFG_TOOLS.md](MFG_TOOLS.md) | AQS-MFG-010 | MFG_SHOP tool list |
| [METAL_FORMING.md](METAL_FORMING.md) | AQS-MFG-MET-001 | Metal forming path — wire draw / cold mill / gas atomizer |
| [METAL_FORMING_EQUIPMENT.md](METAL_FORMING_EQUIPMENT.md) | AQS-EQP-MFG-MET-001 | Metal-forming equipment list |
| [LATHE.md](LATHE.md) | AQS-TOOL-001 | Lathe module |
| [MILL.md](MILL.md) | AQS-TOOL-002 | Mill module |
| [WELDER.md](WELDER.md) | AQS-TOOL-003 | Welder module |
| [JELLYBEAN.md](JELLYBEAN.md) | AQS-MFG-011 | Jellybean parts: standard sizes and in-house lines |
| [BLOCK_FAMILY_PLANS.md](BLOCK_FAMILY_PLANS.md) | AQS-INV-009 | Building-block family production plans |
| [WIRE_SPECS.md](WIRE_SPECS.md) | AQS-INV-007 | Wire family specifications and production plans |
| [MOTOR_FIRST_ARTICLE.md](MOTOR_FIRST_ARTICLE.md) | AQS-INV-008 | Motor first articles: drawings, traveller and type-test rig |
| [BOUGHT_SPECS.md](BOUGHT_SPECS.md) | AQS-PRO-002 | Bought-item specification sheets |
| [PLANT_BOM.md](PLANT_BOM.md) | AQS-PRO-001 | Plant BOM roll-up |
| [SPARES.md](SPARES.md) | AQS-OPS-003 | Critical spares list |
| [EOL_RETURN.md](EOL_RETURN.md) | AQS-END-002 | End-of-life material return |
| [STUDY_UNITS_STUB.md](STUDY_UNITS_STUB.md) | AQS-EQP-STUDY-001 | Study / deferred units — VCD·remin, ORC, litho, solar, blow-mold, e |
| [TEST_PLAN.md](TEST_PLAN.md) | AQS-TST-001 | Testing and prototyping rollout plan |
| [TEST_RIGS.md](TEST_RIGS.md) | AQS-TST-003 | In-house test rigs: build packages |
| [BENCH_TEST_H2_COMPRESSOR.md](BENCH_TEST_H2_COMPRESSOR.md) | AQS-TST-005 | Hydrogen compressor first-article bench run |
| [BENCH_TEST_UPW_POLISH.md](BENCH_TEST_UPW_POLISH.md) | AQS-TST-004 | UPW polish module bench test (RO permeance, rejection, EDI resistivity |

## CAD, drawings and the design tool

| Document | Number | Title |
|---|---|---|
| [BUILD_3D_FROM_FLOW.md](BUILD_3D_FROM_FLOW.md) | AQS-3D-BUILD-001 | Building 3D models from the plant flow graph |
| [STACK_3D_DECISION.md](STACK_3D_DECISION.md) | AQS-3D-STACK-001 | Stack decision — 3D and diagram surfaces |
| [REBUILD.md](REBUILD.md) | AQS-REB-001 | Master rebuild tool |
| [FREECAD_PROTOCOL.md](FREECAD_PROTOCOL.md) | AQS-CAD-002 | FreeCAD protocol — Aqueous wet line |
| [CAD_SCRIPTING_PROTOCOL.md](CAD_SCRIPTING_PROTOCOL.md) | AQS-CAD-001 | Scripted CAD protocol: process flow diagram to rebuildable model |
| [STL_MANIFEST.md](STL_MANIFEST.md) | AQS-STL-001 | STL rebuild manifest |
| [DRAWING_REGISTER.md](DRAWING_REGISTER.md) | AQS-DWG-002 | Drawing register |
| [MFG_MODEL_PLAN.md](MFG_MODEL_PLAN.md) | AQS-PLAN-006 | Manufacturing model plan |
| [DESIGN_TOOL_ARCHITECTURE.md](DESIGN_TOOL_ARCHITECTURE.md) | AQS-UI-001 | Design-tool architecture — Aqueous MVS sandbox |
| [MVS_PITCH_PASS.md](MVS_PITCH_PASS.md) | AQS-PLACE-SEED-001 | Pitch pass — yard through water stubs |
| [OSE_CSK_ALIGNMENT.md](OSE_CSK_ALIGNMENT.md) | AQS-REF-CSK-001 | OSE Civilization Starter Kit — Aqueous alignment map |

## Commissioning, operation and quality

| Document | Number | Title |
|---|---|---|
| [COMMISSIONING.md](COMMISSIONING.md) | AQS-COM-001 | Commissioning plan |
| [STARTUP.md](STARTUP.md) | AQS-COM-002 | Startup sequence (cold start from empty) |
| [PERF_TEST.md](PERF_TEST.md) | AQS-COM-003 | Performance test |
| [OPERATING_PROCEDURES.md](OPERATING_PROCEDURES.md) | AQS-OPS-001 | Operating procedures |
| [MAINT_PLAN.md](MAINT_PLAN.md) | AQS-OPS-002 | Maintenance plan |
| [DECOMMISSIONING.md](DECOMMISSIONING.md) | AQS-END-001 | Decommissioning plan |
| [ITP.md](ITP.md) | AQS-QA-001 | Inspection and test plan |
| [DESIGN_CHECK.md](DESIGN_CHECK.md) | AQS-QA-002 | Independent design check record |

## Planning and status (working documents)

The live task list and the project plan. Older plans, status boards and handoff notes are in [internal/](internal/README.md); they record history and are not design authority.

| Document | Number | Title |
|---|---|---|
| [TASK_PLAN.md](TASK_PLAN.md) | AQS-PLAN-007 | Task plan |
| [PROJECT_PLAN.md](PROJECT_PLAN.md) | AQS-PLAN-005 | Project plan |
| [REWRITE_TODO.md](REWRITE_TODO.md) | AQS-DOC-003 | Documentation rewrite status |

## Licence

CERN-OHL-S-2.0. See the repository [LICENSE](../LICENSE).
