# Documentation rewrite status

Document number: AQS-DOC-003
Revision: A
Date: 2026-10-25

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue | 2026-10-25 |

## 1. Purpose and scope

The documentation style guide (AQS-DOC-002, `DOC_STYLE.md`) sets how every published page in this repository is written. Many pages were written before the guide and have not yet been brought up to it. This page tracks that work for the pages under `docs-authority/`, so that a contributor can see which pages are finished, which are being worked on, which are still to do and which have been removed.

The list of pages that the automated style check treats as not yet rewritten is the `pending` list in `docs-authority/style_terms.json`. A page leaves that list, and moves to the done table on this page, only after a full rewrite to the guide. Passing the automated check is not enough. The records in `docs-authority/notes/` and `docs-authority/internal/` are kept as written and are not tracked here.

Each page is in one of four states:

- **pending**: not yet rewritten.
- **in progress**: part of the page, or the generator that writes it, has been rewritten.
- **done**: rewritten in full and removed from the pending list.
- **removed**: deleted from the repository, with the reason given.

Pages are rewritten in order of how early a new reader is likely to open them: the register and plans first, then the definitions of the plant, then the duty, sizing, equipment, schedule and test pages. A generated page is rewritten by changing its generator.

## 2. Done

Table 2.1. Pages rewritten in full

| Page | Note |
| --- | --- |
| `docs-authority/DOC_REGISTER.md` | Purpose and scope added; generator text in `_doc_register.py` rewritten; part qualifiers no longer truncated mid-path. |
| `docs-authority/PROJECT_PLAN.md` | Rewritten in full; phases, limits and values unchanged. |
| `docs-authority/SURPLUS_PASS_THRESHOLDS.md` | Rewritten in full; thresholds and inputs unchanged. |
| `docs-authority/FEED_ASSAY.md` | Rewritten in full; record of revisions put in order and revision E added. Section numbers 1 to 8 kept because other pages and `drivers.json` cite them, so the purpose and scope section is unnumbered. |
| `docs-authority/CRYO_ASU.md` | Rewritten in full. The undefined code class "shop" is recorded as an open item. |
| `docs-authority/RELIEF.md` | Rewritten in full. |
| `docs-authority/RED_AUDIT.md` | Purpose, scope and record of revisions added; the audit table is unchanged. Two rows name units that are no longer graph nodes (COMPOST_TOILET, EXPANDER); see section 6. |
| `docs-authority/LIFTING.md` | Rev B, through `docs-authority/_lifting.py`. Revision record, purpose and sizing rule added. The closing sentence is now generated from the table; the old fixed text said level L-2 had no lifted equipment while the table listed HYDRO_SET on L-2. |
| `docs-authority/WPS_REGISTER.md` | Rev B, through `docs-authority/_wps.py`. Revision record and purpose added; pipe lines with no stated material are reported in words instead of as a raw tuple. See section 6. |
| `docs-authority/HAZ_AREA.md` | Rev B, through `docs-authority/_haz_area.py`. Revision record, purpose, basis and numbered table added. No zone changed. |
| `docs-authority/FONTS.md` | Rev A. Purpose added; both label scripts named. Policy unchanged. |
| `docs-authority/GROUNDING.md` | Rev B. Values of revision A kept; section 5 records that the grid has been superseded. See section 6. |
| `docs-authority/PERMITS.md` | Rev B. Purpose, numbered table and held items added. No permit changed. |
| `docs-authority/LIFE_HEADERS.md` | Rev B. Tier elevations stated relative to the level 1 floor, as `models/freecad/pipe_services.py` builds them (revision A said above grade). Fixed spine coordinates of revision A kept as history; the parametric placement in `models/freecad/params.py` is described. |
| `docs-authority/GREENHOUSE_ENVELOPE.md` | Rev C. Purpose and numbered table added; records that S40 and S42 are not graph edges. See section 6. |
| `docs-authority/MEOH_EQUIPMENT.md` | Rev B. Purpose added; new column shows which tags are graph nodes. No tag or rating changed. See section 6. |
| `docs-authority/CO2_HEADER_DUTY.md` | Rev D. Rewritten to the guide and updated to graph Rev AC through `_co2_header_study.py`: S85 is 0, the header runs on hab metabolic CO2, the bed dose is on S89 and the remainder goes to MEOH_SYNTH on IA-HCO2-MEOH (study extended; balance closes at 0). Setpoint question recorded as Q-020. |
| `docs-authority/CAMPUS_PLAN.md` | Rev C. Rewritten to the guide: purpose first, phases named in plain words, the invented label "Salria" replaced by plain wording (Q-017 ruling), every locked name marked present or retired against graph Rev AC, rule 4 aligned to stream S10 (WET_BENCH to LEACH_CSTR_1). No rule or envelope changed. |
| `docs-authority/HEAT_LADDER.md` | Rewritten in full; it was not on the pending list but did not follow the guide (no record of revisions, sentence fragments). |
| `docs-authority/SELF_COPY_BOM.md` | Rewritten in full, with the generated reconciliation section rewritten in `_sc_reconcile.py`; section 4 corrected to the flag values in the graph. |
| `docs-authority/RECT_EW.md` | Rev C. Purpose and numbered table added; section 4 records how the graph now represents the rectifier. See section 6. |
| `docs-authority/PIPING_CLASSES.md` | Rev C. Purpose, class-letter key and table titles added. Table rows unchanged, because `_pipe_specs.py`, `_gasket_census.py` and `flow_graph/test_pipe_specs.py` parse them. |
| `docs-authority/ELECTRODE_FAB.md` | Rev D. The revision line said B although revision C had been issued; corrected. Section 5 records the coating load in the graph. See section 6. |
| `docs-authority/HAZMAT_SEPARATION.md` | Rev B, through `flow_graph/sep_check.py`. Revision record, purpose, rule and numbered table added. No pair changed. |
| `docs-authority/MFG_TOOLS.md` | Rev D, through `docs-authority/_mfg_tools.py`. Purpose added; totals in sentences; the hard-coded tool count removed. The tool table is unchanged, because `flow_graph/inventory/motors.py` parses it. |
| `docs-authority/ENCLOSURE_EGRESS.md` | Rev B, through `docs-authority/_egress_env.py`. Revision record, purpose, pass rule and numbered sections added. No value changed. |
| `docs-authority/PERF_TEST.md` | Rev B, through `docs-authority/_perf_test.py`. Purpose, criteria and numbered table added; the plant load row, which sat in a table of its own with no header, is now the last row of Table 3.1. See section 6. |
| `docs-authority/DESIGN_CHECK.md` | Rev B, through `docs-authority/_design_check.py`. Purpose, numbered sections and table title added; failures stated in a sentence, and the result "FAIL" is now written "fail". No check changed. |
| `docs-authority/CONTROL_ARCH.md` | Rev B, through `docs-authority/_plc_arch.py`. Purpose, numbered sections and table titles added. See section 6. |
| `docs-authority/FRAME_CHECK.md` | Rev B, through `docs-authority/_frame_check.py`. Purpose, basis, symbol definitions and table titles added; the beam span heading now comes from the bay size. No load or section changed. |
| `docs-authority/FOUNDATION.md` | Rev B, through `docs-authority/_foundation.py`. Purpose, basis, symbol definitions and numbered table added. The uplift row is unchanged because `_design_check.py` check QC-18 parses it. The plate size is still subject to question Q-015. |
| `docs-authority/MOTOR_FIRST_ARTICLE.md` | Rev B, through `docs-authority/_motor_fa.py`. Purpose, table titles and rig description in sentences added. The paragraph on flagged families printed an empty list of required core lengths when no family was flagged; it is now written only when a family is flagged. |
| `docs-authority/inventory/motor_families/` (every MF sheet) | Rev B, through `flow_graph/inventory/motor_designs.py`. Revision record, purpose, table title, manufacturing steps in full sentences and open items in prose added. No design value changed. `docs-authority/_motor_fa.py` now reads the motor count from the new purpose sentence. |
| `docs-authority/inventory/MOTOR_INVENTORY.md` | Rev B, through `flow_graph/inventory/motors.py`. Revision record, purpose, counting and motor-type rules in sentences, table titles. No motor changed. |
| `docs-authority/inventory/OTHER_INVENTORY.md` | Rev B, through `flow_graph/inventory/other.py`. Revision record, purpose, totals in sentences, table titles. No item changed. |
| `docs-authority/inventory/PIPE_INVENTORY.md` | Rev B, through `flow_graph/inventory/pipe.py`. Revision record, purpose, totals in sentences, table titles. No line changed. |
| `docs-authority/inventory/WIRE_INVENTORY.md` | Rev D, through `flow_graph/inventory/wire.py`. Revision record, purpose, sizing basis and panel-merge rule in sentences, table title. Electrical metallic tubing is defined in the glossary. No circuit changed. |

## 3. In progress

Table 3.1. Pages partly rewritten

| Page | Note |
| --- | --- |
| `docs-authority/TASK_PLAN.md` | Sections 1 to 6 rewritten in `_task_plan_gen.py`; next tasks generated from the triage tags; hand-kept list and progress record moved to Appendix A. Task texts in sections 7 and 8 still to rewrite. |
| `docs-authority/OPEN_QUESTIONS.md` | Purpose and scope rewritten. Question rows still to rewrite. |
| `docs-authority/SECTOR_DEFINITIONS.md` | Generator text in `_sector_definitions.py` rewritten and the catalogue split into three tables. The sector notes in the graph (`mvs.sectors`) and the sector descriptions in `flow_graph/system_tree.yaml` are still in working shorthand; rewriting them changes the graph hash and the model workbook, so it needs a full regeneration. |

## 4. Pending

Table 4.1 lists the pages directly under `docs-authority/` that are still to be rewritten, in the order they will be taken. Table 4.2 lists the pending pages in subfolders; most of them are generated, so the work is in their generators.

Table 4.1. Pending pages directly under docs-authority/

| Page | Note |
| --- | --- |
| `docs-authority/ASME_CODE_INTENT.md` | |
| `docs-authority/ASSUMPTIONS_REGISTER.md` | |
| `docs-authority/BALANCE_RECONCILIATION.md` | |
| `docs-authority/BLOCK_FAMILY_PLANS.md` | |
| `docs-authority/BOUGHT_SPECS.md` | |
| `docs-authority/CONTROL_SOFTWARE.md` | |
| `docs-authority/CRYO_COLD_BOX.md` | |
| `docs-authority/DERIVED_REVISIONS.md` | |
| `docs-authority/EDGE_RATING_DUTY.md` | |
| `docs-authority/EGRESS_CALC.md` | |
| `docs-authority/FAB_WET_INTERFACE.md` | |
| `docs-authority/FAB_WET_REAGENTS.md` | |
| `docs-authority/FAN_STACK.md` | |
| `docs-authority/FARM.md` | |
| `docs-authority/FIRE_PROTECTION.md` | |
| `docs-authority/FRAME_SYSTEM.md` | |
| `docs-authority/FUEL_CELL.md` | |
| `docs-authority/FURNACE.md` | |
| `docs-authority/GAS_DETECTION.md` | |
| `docs-authority/GA_CHECK.md` | |
| `docs-authority/GEOTHERMAL_BACKUP.md` | |
| `docs-authority/GLOSSARY.md` | In part. All style-check findings are cleared: undefined abbreviations, a banned phrase in the DIY entry, and the stale note on capital letters. Many entries are still fragments, and several terms have two entries (for example MVS); a full rewrite is still needed. |
| `docs-authority/H2_EMBRITTLEMENT_REVIEW.md` | |
| `docs-authority/HAB_FIXTURES.md` | |
| `docs-authority/HAB_WATER.md` | |
| `docs-authority/HAZARD_SEPARATION_LAYOUT.md` | |
| `docs-authority/HAZOP.md` | |
| `docs-authority/HEAT_LADDER_DUTIES.md` | Rev D (2026-10-08), authority graph Rev K; not reissued for graph Rev AC. |
| `docs-authority/INSTRUMENT_INDEX.md` | |
| `docs-authority/INSTRUMENT_LOOPS.md` | |
| `docs-authority/INTERNALS.md` | |
| `docs-authority/ISO_SHEETS.md` | |
| `docs-authority/ITP.md` | |
| `docs-authority/JELLYBEAN.md` | |
| `docs-authority/LIFE_FITOUT_PLAN.md` | |
| `docs-authority/LIFE_MEP.md` | |
| `docs-authority/LIFE_NOZZLE_SCHEDULE.md` | |
| `docs-authority/LOAD_LIST.md` | |
| `docs-authority/MATERIALS_SEC3.md` | |
| `docs-authority/MATERIALS_STD.md` | |
| `docs-authority/MEOH_TRAIN.md` | |
| `docs-authority/METAL_FORMING.md` | |
| `docs-authority/MFG_MODEL_PLAN.md` | |
| `docs-authority/MFG_SHOP_EQUIPMENT.md` | |
| `docs-authority/MVS_PITCH_PASS.md` | |
| `docs-authority/MVS_STUDY_CLOSE.md` | |
| `docs-authority/NUTRIENT_GAPS.md` | |
| `docs-authority/O2_SOURCE.md` | |
| `docs-authority/O2_SOURCE_AUDIT.md` | |
| `docs-authority/OSE_CSK_ALIGNMENT.md` | |
| `docs-authority/PARAMETRIC_MODEL.md` | |
| `docs-authority/PIPE_SPECS.md` | |
| `docs-authority/POWER_SIZING.md` | |
| `docs-authority/PROTECTION.md` | |
| `docs-authority/REV_M_CLOSURE_DUTY.md` | |
| `docs-authority/SCALE_DOWN_UNRECLAIMED.md` | |
| `docs-authority/SCRUBBER_CHEMISTRY.md` | |
| `docs-authority/SIDE_FARM.md` | |
| `docs-authority/SIGN_SCHEDULE.md` | |
| `docs-authority/SOLVENT_ROUTE.md` | |
| `docs-authority/STANDARDS_LIST.md` | |
| `docs-authority/STL_MANIFEST.md` | |
| `docs-authority/STRUCT_LOADS.md` | |
| `docs-authority/STUDY_UNITS_STUB.md` | |
| `docs-authority/TERRACE_LANDSCAPE.md` | |
| `docs-authority/TEST_PLAN.md` | |
| `docs-authority/TEXTILES_HEPA.md` | |
| `docs-authority/UNIT_MATERIALS.md` | |
| `docs-authority/VENT_CLOSURE.md` | |
| `docs-authority/WATER_PURIFICATION.md` | |
| `docs-authority/WELD_MAP.md` | |
| `docs-authority/WIRE_SPECS.md` | |

Table 4.2. Pending pages in subfolders

| Page | Note |
| --- | --- |
| `docs-authority/duties/ACID_POLISH_SCRUB.md` | |
| `docs-authority/duties/AFTERBURNER_FLUE.md` | |
| `docs-authority/duties/ALK_SCRUBBER.md` | |
| `docs-authority/duties/BIOFILTER.md` | |
| `docs-authority/duties/BLACK_DIGEST.md` | |
| `docs-authority/duties/C29_RECYCLE.md` | |
| `docs-authority/duties/CATCH_TANK.md` | |
| `docs-authority/duties/CONTINUOUS_RECYCLE.md` | |
| `docs-authority/duties/CRYO_AHU_COND_CONDENSABLE.md` | |
| `docs-authority/duties/CRYO_AR.md` | |
| `docs-authority/duties/CRYO_ASU.md` | |
| `docs-authority/duties/CRYO_CO2.md` | |
| `docs-authority/duties/CRYO_H2.md` | |
| `docs-authority/duties/CRYO_HE.md` | |
| `docs-authority/duties/CRYO_HX_Q4.md` | |
| `docs-authority/duties/CRYO_KR.md` | |
| `docs-authority/duties/CRYO_N2.md` | |
| `docs-authority/duties/CRYO_NE.md` | |
| `docs-authority/duties/CRYO_O2.md` | |
| `docs-authority/duties/CRYO_XE.md` | |
| `docs-authority/duties/CURTAIL.md` | |
| `docs-authority/duties/EMETH.md` | |
| `docs-authority/duties/EVAP_ACID.md` | |
| `docs-authority/duties/EW_1.md` | |
| `docs-authority/duties/EW_2.md` | |
| `docs-authority/duties/EW_3.md` | |
| `docs-authority/duties/EW_4.md` | |
| `docs-authority/duties/EW_5.md` | |
| `docs-authority/duties/EW_6.md` | |
| `docs-authority/duties/EW_7.md` | |
| `docs-authority/duties/EW_8.md` | |
| `docs-authority/duties/EW_9.md` | |
| `docs-authority/duties/EXT_HALL.md` | |
| `docs-authority/duties/FAB_UPW_TANK.md` | |
| `docs-authority/duties/FLOAT_SINK.md` | |
| `docs-authority/duties/FLUE_KO.md` | |
| `docs-authority/duties/GEO_ORC.md` | |
| `docs-authority/duties/GLASS_DIGEST.md` | |
| `docs-authority/duties/HDR_CO2.md` | |
| `docs-authority/duties/HDR_H2.md` | |
| `docs-authority/duties/HDR_N2.md` | |
| `docs-authority/duties/HDR_O2.md` | |
| `docs-authority/duties/HDR_UPW.md` | |
| `docs-authority/duties/HEAT_SINK.md` | |
| `docs-authority/duties/HX8.md` | |
| `docs-authority/duties/IODIDE.md` | |
| `docs-authority/duties/LEACH_CSTR_1.md` | |
| `docs-authority/duties/LIGNO_PRE.md` | |
| `docs-authority/duties/MEOH_COND.md` | |
| `docs-authority/duties/MEOH_SYNTH.md` | |
| `docs-authority/duties/MEOH_TANK.md` | |
| `docs-authority/duties/MET_HX_Q4.md` | |
| `docs-authority/duties/MET_SCRUB.md` | |
| `docs-authority/duties/NCG_HEADER.md` | |
| `docs-authority/duties/NOX_SCRUB.md` | |
| `docs-authority/duties/PROD_C11_C18.md` | |
| `docs-authority/duties/PROD_C19_C28.md` | |
| `docs-authority/duties/PROD_C29.md` | |
| `docs-authority/duties/PROD_C5_C10.md` | |
| `docs-authority/duties/Q1_A.md` | |
| `docs-authority/duties/Q1_B.md` | |
| `docs-authority/duties/Q2_A.md` | |
| `docs-authority/duties/Q2_B.md` | |
| `docs-authority/duties/Q3_A.md` | |
| `docs-authority/duties/Q3_B.md` | |
| `docs-authority/duties/Q4_A.md` | |
| `docs-authority/duties/Q4_B.md` | |
| `docs-authority/duties/Q4_BUS.md` | |
| `docs-authority/duties/REMIN.md` | |
| `docs-authority/duties/ROOF_TANK.md` | |
| `docs-authority/duties/TERRACE_IRRIG.md` | |
| `docs-authority/duties/VAC_IND.md` | |
| `docs-authority/duties/ZNBR2_BR2_REGEN.md` | |
| `docs-authority/fab/AL_POT.md` | |
| `docs-authority/fab/COMB_HEAT.md` | |
| `docs-authority/fab/POLY_OLEFIN.md` | |
| `docs-authority/fab/VAC_IND.md` | |
| `docs-authority/sizing/EVAP_DESIGN.md` | |
| `docs-authority/sizing/EW_CELLS.md` | |
| `docs-authority/sizing/H2_COMPRESSOR.md` | |
| `docs-authority/sizing/HEADERS.md` | |
| `docs-authority/sizing/LITHO_DEV.md` | |
| `docs-authority/sizing/POLYMERS_LINE.md` | |
| `docs-authority/sizing/PV_CELL_LINE.md` | |
| `docs-authority/sizing/REACTOR_DESIGN.md` | |
| `docs-authority/sizing/SANITATION.md` | |
| `docs-authority/sizing/SOLAR_PV_CELL.md` | |
| `docs-authority/sizing/STORAGE_HOLDUP.md` | |
| `docs-authority/sizing/UPW_POLISH.md` | |
| `docs-authority/sizing/VAC_IND.md` | |
| `docs-authority/sizing/VCD_TRAIN.md` | |

## 5. Removed

Table 5.1. Pages and entries removed

| Removed item | Reason |
| --- | --- |
| `docs-authority/DUTY_CALC.md` (AQS-DUTY-081, number withdrawn) | Orphaned snapshot of a retired duty calculation at an earlier graph revision (it states a unit count that no longer holds); no generator writes it and no document cites it. The duty sheets in `docs-authority/duties/` replace it. |
| `docs-authority/ISOMETRIC.md` (AQS-ISO-003, number withdrawn) | Orphaned list of close-pipe isometrics; most of its IA-CLOSE edges and several of its units are no longer in the graph, and no generator writes it. The per-line isometric set AQS-ISO-002 (`ISO_SHEETS.md`) replaces it. |
| Row for `DOCUMENTATION_STYLE.md` in the documentation map (`docs-authority/README.md`) | The page was merged into `DOC_STYLE.md` on 2026-10-24 and no longer exists; its number is a former number of AQS-DOC-002. |

## 6. Questions for the project owner

Table 6.1 lists pages that look abandoned or out of date but are kept until the project owner decides. Each is a candidate for deletion or for a full update.

Table 6.1. Pages kept pending a decision

| Page | Finding |
|---|---|
| `docs-authority/MVS_SIZE.md` (AQS-DUTY-038) | Not cited by any page or generator. It records the crop floor at graph Rev BD and the 24 m × 24 m module plate, which is the subject of open question Q-015. |
| `docs-authority/MASS_DISPOSITION.md` (AQS-DUTY-023), `docs-authority/GREENHOUSE_WATER.md` (AQS-DUTY-013), `docs-authority/BALANCE_CLOSE_N.md` (AQS-DUTY-012) | Short records of balance closures at early graph revisions (Rev Y, Rev O and Rev N). They are cited by notes in the graph and by the assumptions register, so they are kept as history. They could move to `docs-authority/internal/` as records. |
| `docs-authority/ISO_DRAWING_INDEX.md` (AQS-ISO-000) | Marked superseded by AQS-ISO-002 and kept for its PNG and PDF history; cited by `_iso_routes.py` and the task plan. |
| `docs-authority/FARM_WASTE.md` (AQS-DUTY-015) | Reviewed 2026-10-25. Cited by no other page. It sets duties for hydrochar composting and electrochemical pretreatment, but neither process appears in the graph, and its units LIGNO_PRE and COMPOST are no longer graph nodes. Proposed for deletion. |
| `docs-authority/NUTRIENT_BALANCE.md` (AQS-DUTY-034) | Reviewed 2026-10-25. Cited by no other page. It balances nutrients through a fish, larvae, duckweed and azolla loop; FISH, BSFL, DUCKWEED and AZOLLA are no longer graph nodes. Proposed for deletion. |
| `docs-authority/NUTRIENT_GAPS.md` (AQS-DUTY-048) | Reviewed 2026-10-25. Cited by no other page. Its supply column relies on fish, a urine tank and farm animals that are not in the graph, and it cites AQS-DUTY-049 for nutrient recovery, but AQS-DUTY-049 is the polymer exchanger sizing. Proposed for deletion, or a rewrite against NUTRIENT_DOSE if a farm nutrient gap list is still wanted. |
| `docs-authority/HAB_FIXTURES.md` (AQS-HAB-001) | Reviewed 2026-10-25. The number is cited by the graph and the load list, so the page cannot simply be deleted. Its content is out of date: COMPOST_TOILET is no longer a graph node (sanitation is now the blackwater train of AQS-DUTY-063), the edge IA-WASH no longer exists, and S12 now carries 319.6 kg/d, not 339 kg/d. Needs an update against `duties/HAB_WASH.md` and `sizing/SANITATION.md`, or a renumbering decision. |
| `docs-authority/FURNACE.md` (AQS-FURN-001) | Reviewed 2026-10-25. Cited by no other page. It sizes a 10 kW induction furnace for 50 kg of steel; the graph unit for melting is IND_MELT in FOUNDRY, and the progress record in the task plan gives a 7.5 kW coreless furnace (X-MFG-37). Probably superseded; update or delete. |
| `docs-authority/SIDE_FARM.md` (AQS-SIDE-002) | Reviewed 2026-10-25. Cited by no other page. It frames the biofilter and a fish tank; BIOFILTER and the fish units are no longer graph nodes. Proposed for deletion. |
| `docs-authority/FARM.md` (AQS-DUTY-044) | Reviewed 2026-10-25. Cited by no other page. Its nitrogen-fixation duty relies on the fish loop and on clover and seed-bank pages (AQS-DUTY-045 to AQS-DUTY-047); the fish units are no longer graph nodes. Update against the current farm or delete. |
| `docs-authority/SOLVENT_ROUTE.md` (AQS-DUTY-026) | Reviewed 2026-10-25. It describes the route to the ionic liquid [Bmim] acetate through 1-methylimidazole; the units IMID and QUAT are no longer graph nodes. The number is cited elsewhere, so it is kept until a decision. |
| `docs-authority/RED_AUDIT.md` (AQS-RED-001) | Rewritten, but two rows need a factual update: the sanitation row names COMPOST_TOILET and the cold-box row names EXPANDER, and neither is a graph node now. |
| `docs-authority/inventory/PIPE_INVENTORY.csv` (AQS-INV-003) | Lines S36 (WS_DOPE, FAB) and S57 (MET_MELT, MFG) have no piping class, material or joint type ("—" and "-"), so `WPS_REGISTER.md` cannot assign them a procedure. The class and material need to be set in the pipe inventory generator. |

| `docs-authority/GROUNDING.md` (AQS-ELEC-005) | Sections 1 and 4 describe the revision A grid (35 × 20 m ring, 12 rods, 1.14 Ω; GPR 494 V). AQS-ELEC-006 section 4 describes grid Rev B (196 × 174 m, 74 rods, 0.128 Ω, GPR 887 V), and `docs-authority/_grounding_study.py` now prints 0.150 Ω with 65 rods (area 25 392 m²). The three need to be reconciled before section 1 is restated. |
| `docs-authority/FAB_WET_INTERFACE.md` (AQS-IF-FAB-WET-001) | Not rewritten. Much of it no longer matches the graph: FAB_PREP, FAB_TOOL, ETCH_RETURN and CORE_PROCESS are not graph nodes; S10 runs WET_BENCH to LEACH_CSTR_1 (the page says REGEN LEACH); S08 runs LEACH_CSTR_1 to MFG_SHOP (the page lists it as crib solids crossing to the fab); S38 runs WET_BENCH to OIL_FRAC (the page lists it among reagents to the fab); S21 runs ROOF_TANK to HABITATION (the page gives it as a fab ultrapure water feed). It is cited by `WAFER_FAB_EQUIPMENT.md` and two exporters. Proposal: rewrite it from the graph edges between the FAB sector and the wet line, or fold it into `WAFER_FAB_EQUIPMENT.md` and retire the number. |

| `docs-authority/GREENHOUSE_ENVELOPE.md` (AQS-TRR-GH-001) | Streams S40 (overflow to terrace irrigation) and S42 (fertigation return) are named here, in AQS-TRR-001 and in the stream register, but neither is an edge of the plant flow graph. Should they be added to the graph or removed from the pages? |
| `docs-authority/MEOH_EQUIPMENT.md` (AQS-EQP-MEOH-001) | Only MEOH_SYNTH, MEOH_COND, MEOH_TANK and MEOH_FC are graph nodes. The graph has one MEOH_FERM where the list has MEOH_FERM_DIG and MEOH_FERM_STILL, and the remaining tags are on the list only. Should the list be cut to the graph, or the graph extended? |
| `docs-authority/TEXTILES_HEPA.md` (AQS-MFG-TEX-001) | Not rewritten; proposed for deletion. It is a placeholder for a filter media line with no equipment, streams, duties or model. Two of its authorities, AQS-GAP-001 and AQS-AUD-001, are not documents in the repository. Only the glossary entry for HEPA cites it, and that entry can stand without it. |

| `docs-authority/RECT_EW.md` (AQS-ELEC-004) | Finding 1 names node RECT_EW, streams S17-EW and IA-RECT-EW-LOSS (7.73 kW) and a 38.66 kW AC input. The graph now has node RECTIFIER, supply S17 at 12.0 kW (A-M-231) and loss IA-RECT-Q4 at 1.0 kW; the channel streams IA-DC-EW_1 to IA-DC-EW_9 still match Table 2.1. Which AC input is correct? |
| `docs-authority/ELECTRODE_FAB.md` (AQS-MFG-ELC-001) | Study ST-ELC-01 gives about 0.3 kW average; the graph supplies ELECTRODE_COAT with 0.0792 kW (SF-ELECTRODE_COAT). Which is correct? |

| `docs-authority/PERF_TEST.md` (AQS-COM-003) | `_perf_test.py` takes every solid stream leaving an electrowinning cell as harvested metal, so IA-COAT-IN (0.02 kg/d, EW_1 to ELECTRODE_COAT, the electrode sent for coating) appears as a guarantee point measured by weighed cathode harvest. Should the selection exclude streams that do not go to a product? |

| `docs-authority/CONTROL_ARCH.md` (AQS-CTL-002) | The closing note says that, if the inventory already counts the high-level switches, the DI count is 113 too high. The figure 113 is a fixed number in `_plc_arch.py`; the instrument index now has 82 digital-input rows (`24 V DC discrete (DI)`). Should the note be computed from the index? |

| `docs-authority/O2_SOURCE.md` (AQS-PAR-005) | Not rewritten. Two generators write this page: `flow_graph/param/o2_source.py` (the current Rev D duty summary) and `flow_graph/param/o2_close.py` report(), whose Rev C closure report would overwrite it if run. The page says the Rev C sections regenerate at the next balance run. Which generator owns the page? Once that is settled, the template can be rewritten without the risk of the other writer restoring the old text. |
