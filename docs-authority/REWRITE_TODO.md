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
| `docs-authority/HEAT_LADDER.md` | Rewritten in full; it was not on the pending list but did not follow the guide (no record of revisions, sentence fragments). |
| `docs-authority/SELF_COPY_BOM.md` | Rewritten in full, with the generated reconciliation section rewritten in `_sc_reconcile.py`; section 4 corrected to the flag values in the graph. |

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
| `docs-authority/CAMPUS_PLAN.md` | |
| `docs-authority/CO2_HEADER_DUTY.md` | |
| `docs-authority/CONTROL_ARCH.md` | |
| `docs-authority/CONTROL_SOFTWARE.md` | |
| `docs-authority/CRYO_COLD_BOX.md` | |
| `docs-authority/DERIVED_REVISIONS.md` | |
| `docs-authority/DESIGN_CHECK.md` | |
| `docs-authority/EDGE_RATING_DUTY.md` | |
| `docs-authority/EGRESS_CALC.md` | |
| `docs-authority/ELECTRODE_FAB.md` | |
| `docs-authority/ENCLOSURE_EGRESS.md` | |
| `docs-authority/FAB_WET_INTERFACE.md` | |
| `docs-authority/FAB_WET_REAGENTS.md` | |
| `docs-authority/FAN_STACK.md` | |
| `docs-authority/FARM.md` | |
| `docs-authority/FIRE_PROTECTION.md` | |
| `docs-authority/FONTS.md` | |
| `docs-authority/FOUNDATION.md` | |
| `docs-authority/FRAME_CHECK.md` | |
| `docs-authority/FRAME_SYSTEM.md` | |
| `docs-authority/FUEL_CELL.md` | |
| `docs-authority/FURNACE.md` | |
| `docs-authority/GAS_DETECTION.md` | |
| `docs-authority/GA_CHECK.md` | |
| `docs-authority/GEOTHERMAL_BACKUP.md` | |
| `docs-authority/GLOSSARY.md` | |
| `docs-authority/GREENHOUSE_ENVELOPE.md` | |
| `docs-authority/GROUNDING.md` | |
| `docs-authority/H2_EMBRITTLEMENT_REVIEW.md` | |
| `docs-authority/HAB_FIXTURES.md` | |
| `docs-authority/HAB_WATER.md` | |
| `docs-authority/HAZARD_SEPARATION_LAYOUT.md` | |
| `docs-authority/HAZMAT_SEPARATION.md` | |
| `docs-authority/HAZOP.md` | |
| `docs-authority/HEAT_LADDER_DUTIES.md` | Rev D (2026-10-08), authority graph Rev K; not reissued for graph Rev AC. |
| `docs-authority/INSTRUMENT_INDEX.md` | |
| `docs-authority/INSTRUMENT_LOOPS.md` | |
| `docs-authority/INTERNALS.md` | |
| `docs-authority/ISO_SHEETS.md` | |
| `docs-authority/ITP.md` | |
| `docs-authority/JELLYBEAN.md` | |
| `docs-authority/LIFE_FITOUT_PLAN.md` | |
| `docs-authority/LIFE_HEADERS.md` | |
| `docs-authority/LIFE_MEP.md` | |
| `docs-authority/LIFE_NOZZLE_SCHEDULE.md` | |
| `docs-authority/LOAD_LIST.md` | |
| `docs-authority/MATERIALS_SEC3.md` | |
| `docs-authority/MATERIALS_STD.md` | |
| `docs-authority/MEOH_EQUIPMENT.md` | |
| `docs-authority/MEOH_TRAIN.md` | |
| `docs-authority/METAL_FORMING.md` | |
| `docs-authority/MFG_MODEL_PLAN.md` | |
| `docs-authority/MFG_SHOP_EQUIPMENT.md` | |
| `docs-authority/MFG_TOOLS.md` | |
| `docs-authority/MOTOR_FIRST_ARTICLE.md` | |
| `docs-authority/MVS_PITCH_PASS.md` | |
| `docs-authority/MVS_STUDY_CLOSE.md` | |
| `docs-authority/NUTRIENT_GAPS.md` | |
| `docs-authority/O2_SOURCE.md` | |
| `docs-authority/O2_SOURCE_AUDIT.md` | |
| `docs-authority/OSE_CSK_ALIGNMENT.md` | |
| `docs-authority/PARAMETRIC_MODEL.md` | |
| `docs-authority/PERF_TEST.md` | |
| `docs-authority/PERMITS.md` | |
| `docs-authority/PIPE_SPECS.md` | |
| `docs-authority/PIPING_CLASSES.md` | |
| `docs-authority/POWER_SIZING.md` | |
| `docs-authority/PROTECTION.md` | |
| `docs-authority/RECT_EW.md` | |
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
| `docs-authority/inventory/MOTOR_INVENTORY.md` | |
| `docs-authority/inventory/OTHER_INVENTORY.md` | |
| `docs-authority/inventory/PIPE_INVENTORY.md` | |
| `docs-authority/inventory/WIRE_INVENTORY.md` | |
| `docs-authority/inventory/motor_families/MF-04.md` | |
| `docs-authority/inventory/motor_families/MF-05.md` | |
| `docs-authority/inventory/motor_families/MF-06.md` | |
| `docs-authority/inventory/motor_families/MF-07.md` | |
| `docs-authority/inventory/motor_families/MF-08.md` | |
| `docs-authority/inventory/motor_families/MF-09.md` | |
| `docs-authority/inventory/motor_families/MF-10.md` | |
| `docs-authority/inventory/motor_families/MF-11.md` | |
| `docs-authority/inventory/motor_families/MF-12.md` | |
| `docs-authority/inventory/motor_families/MF-13.md` | |
| `docs-authority/inventory/motor_families/MF-14.md` | |
| `docs-authority/inventory/motor_families/MF-15.md` | |
| `docs-authority/inventory/motor_families/MF-16.md` | |
| `docs-authority/inventory/motor_families/MF-17.md` | |
| `docs-authority/inventory/motor_families/MF-18.md` | |
| `docs-authority/inventory/motor_families/MF-20.md` | |
| `docs-authority/inventory/motor_families/MF-21.md` | |
| `docs-authority/inventory/motor_families/MF-24.md` | |
| `docs-authority/inventory/motor_families/MF-25.md` | |
| `docs-authority/inventory/motor_families/MF-26.md` | |
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
