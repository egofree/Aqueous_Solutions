# Documentation rewrite status

Document number: AQS-DOC-003
Revision: AQ
Date: 2026-10-29

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue | 2026-10-25 |
| B | Pages closed on 2026-10-25 without a rewrite re-opened with the reason for each; sections 3 and 4 now match the pending list, which `flow_graph/test_rewrite_todo.py` checks | 2026-10-29 |
| C | POWER_SIZING given a generator; FIRE_PROTECTION rewritten through its generator; duty sheet headers now carry the current graph revision | 2026-10-29 |
| D | FUEL_CELL, H2_EMBRITTLEMENT_REVIEW and WELD_MAP rewritten; PROTECTION found stale and its reason updated | 2026-10-29 |
| E | WATER_PURIFICATION, LIFE_MEP and MEOH_TRAIN given generators and rewritten | 2026-10-29 |
| F | PROTECTION written by its study script; ISO_SHEETS and JELLYBEAN rewritten through their generators | 2026-10-29 |
| G | Reference sweep: unregistered document numbers listed in `unregistered_doc_numbers.json` and guarded by `flow_graph/test_doc_number_refs.py` | 2026-10-29 |
| H | Batch 6: the instrument index, inspection and test plan, load list, internals register and per-unit material selections rewritten through their generators | 2026-10-29 |
| I | Batch 7: the pipe, wire and building-block family plans and the standards list rewritten through their generators | 2026-10-29 |
| J | Out-of-repository references removed from six equipment lists | 2026-10-29 |
| K | Batch 8: the load list and power sizing reconciled; the scale-down page and the matplotlib folder index rewritten; one owner question added on the rectifier feed | 2026-10-29 |
| L | Batch 9: four sizing pages rewritten through their generators | 2026-10-29 |
| M | Batch 10: the storage, electrowinning cell and reactor sizing pages rewritten through their generators; one owner question added on the sanitation page | 2026-10-29 |
| N | Batch 11: the sanitation page given a generator that reads the present graph; the rectifier finding corrected in the load list and power sizing pages; owner questions on the trim heaters and the sanitation feed | 2026-10-29 |
| O | Batch 12: the evaporator and polymers line sizing pages rewritten through their generators | 2026-10-29 |
| P | Batch 13: the per-unit sizing pages of the unit sizing sweep rewritten through their generator | 2026-10-29 |
| Q | Batch 14: the trim heaters fed by the rectifier counted at rated load in the plant bus demand by owner decision (A-M-415), with their own feeder; the bus section rating now follows the bus demand; the two owner questions on these closed | 2026-10-29 |
| R | Batch 15: the metal-forming, shop and wafer fab equipment lists given generators that read the graph; owner questions on the forming tool design, the silicon charge of the fab and its blanket gas | 2026-10-29 |
| S | Batch 16: the path of the cryogenic massing script corrected in AUTHORITY and in the history page REMAINING_BLD | 2026-10-29 |
| T | Batch 17: PARAMETRIC_MODEL rewritten through its generator `flow_graph/param/report.py` | 2026-10-29 |
| U | Batch 18: METAL_FORMING and SOLVENT_ROUTE rewritten against the graph; owner question on the ionic-liquid chain | 2026-10-29 |
| V | Batch 19: SCRUBBER_CHEMISTRY rewritten against the graph; VENT_CLOSURE given a generator that checks every closure on the graph; owner question on the caustic vents | 2026-10-29 |
| W | Batch 20: MVS_PITCH_PASS and MVS_STUDY_CLOSE marked as superseded records; MATERIALS_SEC3 and STL_MANIFEST brought to the style guide; STL importer path fixed | 2026-10-29 |
| X | Batch 21: four hand-drawn process sheets retired and replaced by graph-driven sector views | 2026-10-29 |
| Y | Batch 22: the wire die schedule, the cold-mill gauge and width and the atomiser batch derived from the graph throughputs (owner decision 2026-10-29, A-M-416); the owner question on the forming tool design closed | 2026-10-29 |
| Z | Batch 23: silicon feed to WAFER_FAB sized from the wafer need, imported through the dock (owner decision 2026-10-29, A-M-417); the owner question on the silicon charge closed | 2026-10-29 |
| AA | Batch 24: argon blanket gas for the CZ puller from the cold box in a closed loop (owner decision 2026-10-29, A-M-417); nitrogen refused for the melt; the owner question on the blanket gas closed | 2026-10-29 |
| AB | Batch 25: every route without flow put on the task list as group X-RTE, generated from the graph; five routes already noted as retired set to presence retired | 2026-10-29 |
| AC | Batch 26: METAL_FORMING revision D points to the tool design derived from the graph throughputs | 2026-10-29 |
| AD | Batch 27: standby route STOCK_TO_WIRE_DRAW sized at its rated case (A-M-418) | 2026-10-29 |
| AE | Batch 28: standby route IND_TO_ATOM sized at its rated case (A-M-418) | 2026-10-29 |
| AF | Batch 29: route UPW_TO_FAB retired as a duplicate of IA-UPW-FAB; FAB_WET_INTERFACE revision C | 2026-10-29 |
| AG | Batch 30: retired routes leave the line list, and their isometric sheets are removed through the generator | 2026-10-29 |
| AH | Batch 31: the CZ silicon is made on site (SI_REDUCE and the new SI_REFINE, A-M-419); the polysilicon import is retired; WAFER_FAB_EQUIPMENT revision G | 2026-10-29 |
| AI | Batch 32: water make-up allowed as a natural resource; Ti, Mo and Cr carbon reductant from plant char (A-M-420) | 2026-10-29 |
| AJ | Batch 33: sulfuric acid made on site by ACID_PLANT from the HF kiln cake and native sulfur ore (A-M-421) | 2026-10-29 |
| AK | Batch 34: sodium hydroxide made on site by NAOH_PLANT, lime causticising of trona ore or membrane chlor-alkali (A-M-422) | 2026-10-29 |
| AL | Batch 35: recovery first for every element taken as raw ore, with a generated inventory and check (A-M-423); sulfur, calcium and sodium revisited | 2026-10-29 |
| AM | Batch 36: pattern wax make-up from the plant C19-C28 cut (A-M-424) | 2026-10-29 |
| AN | Batch 37: Q-034 decided, the acid cake kiln runs in campaigns (A-M-425) | 2026-10-29 |
| AO | Batch 38: Q-035 and Q-036 decided, chlor-alkali top-up and cell hydrogen on the H2 header (A-M-426) | 2026-10-29 |
| AP | Batch 39: Q-037 decided, the Ti, Mo and Cr cells take the float-sink grit first (A-M-427) | 2026-10-29 |
| AQ | Batch 40: bench solvent made on site by SOLV_PLANT, recovery first (A-M-428) | 2026-10-29 |

## 1. Purpose and scope

The documentation style guide (AQS-DOC-002, `DOC_STYLE.md`) sets how every published page in this repository is written. Many pages were written before the guide and have not yet been brought up to it. This page tracks that work for the pages under `docs-authority/`, so that a contributor can see which pages are finished, which are being worked on, which are still to do and which have been removed.

The list of pages that the automated style check treats as not yet rewritten is the `pending` list in `docs-authority/style_terms.json`. A page leaves that list, and moves to the done table on this page, only after a full rewrite to the guide. Passing the automated check is not enough. The records in `docs-authority/notes/` and `docs-authority/internal/` are kept as written and are not tracked here.

Each page is in one of four states:

- **pending**: not yet rewritten. The page is on the pending list.
- **in progress**: part of the page, or the generator that writes it, has been rewritten. The page stays on the pending list until the rewrite is complete.
- **done**: rewritten in full and removed from the pending list.
- **removed**: deleted from the repository, with the reason given.

Pages are rewritten in order of how early a new reader is likely to open them: the register and plans first, then the definitions of the plant, then the duty, sizing, equipment, schedule and test pages. A generated page is rewritten by changing its generator.

## 2. Done

Table 2.1 lists the pages rewritten in full. A row that says only that a page was checked against the guide has been moved back to section 4.

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
| `docs-authority/CRYO_COLD_BOX.md` | Rev D. Rewritten to the guide: numbering repaired, session wording removed, stream list corrected to the present graph (S05 and S06 retired; Q4_BUS contributors named from the graph, S70 endpoint corrected to FLUE_KO). No design decision changed. |
| `docs-authority/ASME_CODE_INTENT.md` | Rev D, through `_asme_class.py`. Purpose and scope first, numbered sections and table titles; the truncated authority line repaired. No class, stamp or test changed. |
| `docs-authority/BALANCE_RECONCILIATION.md` | Rev E, through `flow_graph/param/balance.py`. Purpose and scope first, revision record in order, sections and table titles renumbered (0-4 to 2-6; cross-references in balance.py, closure_tf.py and assumptions A-M-120/A-M-123 updated in the same change). No method, rate or result changed. Also fixed in this batch: the assumptions-register scan crashed on any model params.json whose `assumptions` entry is a list (CAST_LINE); params.json converted to the keyed form and the register runs again. |
| `docs-authority/BOUGHT_SPECS.md` | Rev B, through `_bought_specs.py`. Purpose and scope first, numbered sections and table titles. No roster row, class or size changed. |
| `docs-authority/CONTROL_SOFTWARE.md` | Rev B, through `flow_graph/control/plc_programs.py`. Purpose and scope first, revision record added, sections renumbered. No program, classification or check changed. |
| `docs-authority/SECTOR_DEFINITIONS.md` | Verified compliant against the checker and the guide's structure rules (revision record, purpose first, numbered sections); closed without further edits. |
| `docs-authority/ASSUMPTIONS_REGISTER.md` | Rev C, through `_assumptions_register.py`. Already guide-structured; the document-line mining section removed as index noise (the curated assumptions and the graph/parameter scans stay). |
| `docs-authority/DERIVED_REVISIONS.md` | Rev B, through `_rev_stamp.py`. Purpose and scope added; the count line states its authority (the regeneration command). Tracking rule unchanged. |
| `docs-authority/EDGE_RATING_DUTY.md` | Rev B. Rewritten to the guide; stays the record of the Rev L edge rating (the Rev M balances live in AQS-DUTY-011 and the regenerated sheets). Banned phrase removed; CHG defined at first use. No rating changed. |
| `docs-authority/EGRESS_CALC.md` | Rev B. Has the guide structure; study assumptions stay labeled as such and the stair tags are written whole (STAIR_MAINT, not a bare fragment). No width, occupancy or factor changed. |
| `docs-authority/FAB_WET_INTERFACE.md` | Rev B. Rewritten from the graph: retired units removed, crossings restated with rates from the live edges (S10 WET_BENCH to LEACH_CSTR_1; returns S39/S39B/IA-FAB-SPENT from WAFER_FAB), wet-chemical supply train stated, POLISH_BANK / FAB_UPW / WS_* naming disambiguation kept. Chases and nozzles stay the piping-pass open item. |
| `docs-authority/FAB_WET_REAGENTS.md` | Rev C. Style pass: narrative references spelled out, deferred-placement wording aligned with the FreeCAD pass. Forks, IDs and study rates unchanged; study rates stay labeled. |
| `docs-authority/FAN_STACK.md` | Rev C. Purpose first, above-ground-level spelled out; stacks stay the upset/contingency path with closure at AQS-VENT-001. No height, curve or duty changed. |
| `docs-authority/GAS_DETECTION.md` | Rev B, through `_gas_det.py`. Purpose and scope added, table titles, per-unit detail section numbered. No detector, mounting or set point changed. |
| `docs-authority/FRAME_SYSTEM.md` | Rev D. Purpose first, numbered sections and table titles; the former-number line carries the AQS-MOD-001 duplicate clear. No parameter, class, size or load rule changed. |
| `docs-authority/GA_CHECK.md` | Rev B, through `_ga_check.py`. Purpose and scope added; sections and table titles numbered. No envelope, overlap or clearance result changed. |
| `docs-authority/HAB_WATER.md` | Rev C. Purpose and scope added, sections renumbered. No unit, stream or rate changed. |
| `docs-authority/HAZOP.md` | Rev B, through `_hazop.py`. Purpose and scope added, sections numbered. No deviation, cause, safeguard or action changed; the team-HAZOP study scope statement stays. |
| `docs-authority/HEAT_LADDER_DUTIES.md` | Rev E. Status note added: it stays the historical record of the Rev K to Rev M edge-duty derivation; the live duties regenerate into the graph each pass and the page is not reissued per graph revision. |
| `docs-authority/SITE_BASIS_ANTARCTIC.md` | Rev A. Profile, environment, scaling actions, closure status; the locale run is blocked on the wind-primary write-stage integration (the X-LOC-08 design pass). |
| `docs-authority/SITE_BASIS_MARS.md` | Rev A. Profile, environment, scaling actions and design consequences for the Mars variant. |
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
| `docs-authority/GEOTHERMAL_BACKUP.md` | Rev C. Rewritten from the plant graph: the generator is dual-fuel (hydrogen, then the C5 to C10 cut) as `params.fuel_selection` states; the organic Rankine cycle unit is an installed standby option; units and streams that are not in the graph (GEN_H2_BUFFER, FC_DCDC, FC_HX_Q4, S05) and references to files outside the repository removed; the renumbering recorded on a `Former number:` line. |
| `docs-authority/HAB_FIXTURES.md` | Rev C. Rewritten from the plant graph: blackwater goes to BLACK_DIGEST on HAB_BLACK (the COMPOST_TOILET node and the edges IA-WASH, IA-E-HABOUT and IA-I-DOSE are no longer in the graph); grey water rate pointed to the stream register; the missing plumbing code recorded. |
| `docs-authority/STRUCT_LOADS.md` | Rev B, through `_struct_loads.py`. Purpose, method and table titles added; the text now says that the operating liquid is taken as live load, which is what the calculation does (it said dead load before). No load changed. |
| `docs-authority/POWER_SIZING.md` | Rev G. Now written by `docs-authority/_power_sizing_doc.py` from the graph and the drivers (regen stage `doc_power_sizing`). The page does not duplicate the flow battery outputs: it is the only page that reports the array, storage, inverter and generator sizing together and is cited by the sizing scripts and the backup generator page. Section 5 reports two mismatches for the owner. |
| `docs-authority/FIRE_PROTECTION.md` | Rev C. Rewritten through `docs-authority/_fire.py`: purpose and scope with defined hazard classes, the two descriptions of the water supplies merged, fragments from `fire.py` replaced by sentences, tables numbered and a numbered reference list. |
| `docs-authority/FUEL_CELL.md` | Rev C. Rewritten against the graph: streams and rates from the graph, the reversible loop with the electrolyser, the difference from the backup generator and the methanol fuel cell; references outside the repository (POWER/, hub ELECTRICAL.md, share mirror) removed. |
| `docs-authority/H2_EMBRITTLEMENT_REVIEW.md` | Rev C. Rewritten against the graph: electrolyser and hydrogen compressor added, cathodes changed to titanium as AQS-STD-002 section 9 decided, the store described as a compressed-gas tube bank, and the false statement that the edges carry pressure and temperature withdrawn. |
| `docs-authority/WELD_MAP.md` | Rev B. The joint tags, corrupted by a text replacement in the 2026-10-25 bulk closure, restored to JW-nnn; the hanger and hydrogen header joints brought in line with AQS-STD-002. |
| `docs-authority/WATER_PURIFICATION.md` | Rev C. Now written by `docs-authority/_water_purification.py` (stage `doc_water_purification`): the treatment trains described by their graph units, every stream and the unit balances from the graph; references to SLINGSHOT/ and the numbered root documents removed; the quality targets kept, with their published sources listed as an open item. |
| `docs-authority/LIFE_MEP.md` | Rev B. Now written by `docs-authority/_life_mep.py` (stage `doc_life_mep`): crew size from the graph, pipe sizes from `params.py`, drains named by graph unit, arrow diagrams replaced by sentences, the citation of AQS-AUD-001 (not in the repository) removed. |
| `docs-authority/MEOH_TRAIN.md` | Rev B. Now written by `docs-authority/_meoh_train_doc.py` (stage `doc_meoh_train`): units, streams and rates from the graph, including the methanol product shipped at the dock, which Rev A did not describe; ranges, tags not on the graph and references to root documents removed. |
| `docs-authority/PROTECTION.md` | Rev E. Now written by `docs-authority/_protection.py`, which already computed the study: inverter count and rating, section mains and the rectifier name from the graph, feeders from the one-line diagram, grid values from `_grounding_study.py` (not changed). The code basis section appended by `code_basis.py` is carried over. |
| `docs-authority/ISO_SHEETS.md` | Rev B. Rewritten through `docs-authority/_iso_sheets.py`: purpose and scope, the summary and basis as sentences, numbered tables. |
| `docs-authority/JELLYBEAN.md` | Rev B. Rewritten through `docs-authority/_jellybean.py`: purpose and scope, an introductory sentence and numbered table for each family, the pipe entries no longer contradict their schedule, and the line list cited as AQS-PIP-004 instead of an unregistered number. |
| `docs-authority/INSTRUMENT_INDEX.md` | Rev B. Rewritten through `docs-authority/_instr_index.py`: record of revisions, purpose and scope, counts and loops as sentences, numbered tables. |
| `docs-authority/ITP.md` | Rev B. Rewritten through `docs-authority/_itp.py`: record of revisions, purpose and scope, inspection points defined, one numbered section and table per route. |
| `docs-authority/LOAD_LIST.md` | Rev D. Rewritten through `docs-authority/_load_list.py`: the load bases defined, the status written as sentences, numbered tables. |
| `docs-authority/INTERNALS.md` | Rev B. Rewritten through `docs-authority/_internals.py`: purpose and scope, the method and limits as sentences, fixed counts removed. |
| `docs-authority/UNIT_MATERIALS.md` | Rev B. Rewritten through `docs-authority/_unit_materials.py`: purpose and scope, the summary and rule as sentences, fixed counts removed, no empty table. |
| `docs-authority/PIPE_SPECS.md` | Rev B. Rewritten through `docs-authority/_pipe_specs.py`: purpose and scope, rules and family plans as sentences, the stale family count replaced by the inventory count. |
| `docs-authority/WIRE_SPECS.md` | Rev D. Rewritten through `docs-authority/_wire_specs.py`: purpose and scope, the production steps and family sheets as sentences, numbered tables. |
| `docs-authority/BLOCK_FAMILY_PLANS.md` | Rev B. Rewritten through `docs-authority/_block_fam_plans.py`: purpose and scope, category plans as sentences, stale counts of bought families and spares removed. |
| `docs-authority/STANDARDS_LIST.md` | Rev B. Rewritten through `docs-authority/_standards_list.py`: record of revisions, purpose and scope, numbered tables, full standard titles. |
| `docs-authority/BACKUP_GEN_EQUIPMENT.md` | Rev E. References to documents outside the repository removed; FreeCAD script paths corrected where cited. |
| `docs-authority/FUEL_CELL_EQUIPMENT.md` | Rev F. References to documents outside the repository removed; FreeCAD script paths corrected where cited. |
| `docs-authority/GEOTHERMAL_EQUIPMENT.md` | Rev E. References to documents outside the repository removed; FreeCAD script paths corrected where cited. |
| `docs-authority/CRYO_EQUIPMENT.md` | Rev G. References to documents outside the repository removed; FreeCAD script paths corrected where cited. |
| `docs-authority/FARM_EQUIPMENT.md` | Rev E. References to documents outside the repository removed; FreeCAD script paths corrected where cited. |
| `docs-authority/SOLAR_CELL_EQUIPMENT.md` | Rev D. References to documents outside the repository removed; FreeCAD script paths corrected where cited. |
| `docs-authority/LOAD_LIST.md` | Rev G. Section 3 reconciles the connected load with the plant bus demand of AQS-ELEC-007, from the graph; the trim heaters fed by the rectifier are counted at rated load and the rectifier has three feeders. |
| `docs-authority/POWER_SIZING.md` | Rev J. The plant bus demand split into its parts, the trim heaters fed by the rectifier among them at rated load; the three rectifier feeders and the bus section rating checked against the bus demand. |
| `docs-authority/ONE_LINE.md` | Rev F. The RECT-TRIM feeder added for the trim heaters fed by the rectifier, sized from their rated load by `docs-authority/_one_line.py`. |
| `docs-authority/SCALE_DOWN_UNRECLAIMED.md` | Rev F. Rewritten through `flow_graph/param/scale_down.py`: purpose and scope, the revision history taken out of the summary, the terms table captioned. |
| `flow_graph/exporters/matplotlib/README.md` | Rev B. Hand-written folder index (it has no generator; the earlier entry here was wrong). Purpose and scope added, and the images built by the regeneration stated from `flow_graph/regen_derived.py`. |
| `docs-authority/sizing/H2_COMPRESSOR.md` | Rev C. Rewritten through `flow_graph/param/h2_compressor.py`: record of revisions, purpose and scope, the method as sentences with driver values in place of fixed figures, numbered tables. |
| `docs-authority/sizing/HEADERS.md` | Rev B. Rewritten through `flow_graph/param/headers.py`: record of revisions, purpose and scope, the method as sentences with driver values in place of fixed figures, numbered tables. |
| `docs-authority/sizing/UPW_POLISH.md` | Rev B. Rewritten through `flow_graph/param/upw_polish.py`: record of revisions, purpose and scope, the method as sentences with driver values in place of fixed figures, numbered tables. |
| `docs-authority/sizing/PV_CELL_LINE.md` | Rev B. Rewritten through `flow_graph/param/pv_cell_line.py`: record of revisions, purpose and scope, the method as sentences with driver values in place of fixed figures, numbered tables. |
| `docs-authority/sizing/STORAGE_HOLDUP.md` | Rev B. Rewritten through `docs-authority/_storage_sizing.py`: record of revisions, purpose and scope, the method with the hold-up and minimum-volume drivers, results in a numbered table and a section on units sized elsewhere. |
| `docs-authority/sizing/EW_CELLS.md` | Rev D. Rewritten through `docs-authority/_ew_sizing.py`: purpose and scope, the cell basis from the driver values, results in a numbered table, and findings as sentences; the tank length range is now computed. The finding on the hydrogen-cell list is unchanged while the owner question is open. |
| `docs-authority/sizing/REACTOR_DESIGN.md` | Rev C. Rewritten through `flow_graph/param/reactor_design.py`: purpose and scope, the basis written as sentences with the driver values in place of typed figures, numbered tables, and no section for a reactor type with no unit on the graph. |
| `docs-authority/sizing/SANITATION.md` | Rev C. Now written by `flow_graph/param/sanitation.py`, rewritten to read the present graph and write only the page (regen stage `sanitation_doc`; the script was a retired one-time graph edit). The train is sized from the flows of BLACK_DIGEST; purpose and scope, numbered tables, sentences. |
| `docs-authority/sizing/EVAP_DESIGN.md` | Rev C. Rewritten through `flow_graph/param/evap_design.py`: document number, revision and date lines, record of revisions with dates, purpose and scope, the basis as sentences with the driver values, tables numbered and labelled with units, and the comparison with an earlier upper bound removed. |
| `docs-authority/sizing/POLYMERS_LINE.md` | Rev B. Rewritten through `docs-authority/_polymers_sizing.py`: purpose and scope, sentences, numbered tables; the fluoropolymer train is now reported from the graph, where it runs on imported fluorspar, in place of text that called it blocked; the stale open item on the film caster feed is dropped when the graph has that feed. |
| `docs-authority/sizing/<UNIT>.md` (AQS-SIZE-<UNIT>, every page of the unit sizing sweep) | Rev B. Rewritten through `docs-authority/_unit_sizing_sweep.py`, which had stopped writing them: purpose and scope, design parameters in a table, the envelope from the graph or the placement files, the hold-up vessel in millimetres from the larger of inflow and outflow with a real fit check, and the material from the duty sheet. |
| `docs-authority/METAL_FORMING_EQUIPMENT.md` | Rev E. Now written by `docs-authority/_mfg_equipment.py` (regen stage `doc_mfg_equipment`) from the metal-forming units of sector MFG and the tool list AQS-MFG-010: units, tools, streams, mass balance and separation checks. Tags no longer on the graph, the nitrogen atomising gas and the TBD tool sizes removed. |
| `docs-authority/MFG_SHOP_EQUIPMENT.md` | Rev E. Now written by `docs-authority/_mfg_equipment.py` from the other units of sector MFG and the shop tools of AQS-MFG-010: units, tools, streams and mass balance. |
| `docs-authority/WAFER_FAB_EQUIPMENT.md` | Rev D. Now written by `docs-authority/_wafer_fab_equipment.py` (regen stage `doc_wafer_fab_equipment`) from the units of sector FAB, the equipment list of WAFER_FAB and the fab edges; references outside the repository removed. |
| `docs-authority/AUTHORITY.md` | Rev Z. The vacuum-jacketed line envelopes now point to `models/freecad/cryo.py`, where they are defined. |
| `docs-authority/internal/REMAINING_BLD.md` | Rev Z. History page kept as it is; two file paths corrected, one to `models/freecad/cryo.py` and one to a folder outside the repository. |
| `docs-authority/PARAMETRIC_MODEL.md` | Rev C. Rewritten through `flow_graph/param/report.py`: purpose, scope and terms; the framework and the acid-loop decision as sentences in order; the relief and scrubber rows read from the graph; stale pointers removed. |
| `docs-authority/METAL_FORMING.md` | Rev C. Rewritten against the graph: the route of the metal by stream, the choices that fix it, air handling, heat recovery and hazards; stale tags, outside references and the nitrogen atomising gas removed; values left to the generated equipment list. |
| `docs-authority/SOLVENT_ROUTE.md` | Rev D. Rewritten against the graph: the methanol train by stream, the ionic-liquid route as chemistry only, and the fab reagent uses; the rates of graph revision BH removed. |
| `docs-authority/SCRUBBER_CHEMISTRY.md` | Rev B. Rewritten against the graph: scrubbers mapped to graph units and streams, reactions and controls kept as sentences, liquor destinations and materials in numbered tables; the acid-gas and caustic headers that are not on the graph removed. |
| `docs-authority/VENT_CLOSURE.md` | Rev D. Now written by `docs-authority/_vent_closure.py` (regen stage `doc_vent_closure`): the closure rule, each former open discharge with its end state, and a check of every closure stream, contingency route and relief sink against the graph. |
| `docs-authority/MVS_PITCH_PASS.md` | Rev B. Identity lines, record of revisions and purpose; marked as a superseded placement record pointing to the placement seed and AQS-SITE-013. |
| `docs-authority/MVS_STUDY_CLOSE.md` | Rev B. Identity lines, record of revisions and purpose; marked as a superseded study record pointing to the stub activation. |
| `docs-authority/MATERIALS_SEC3.md` | Rev B. Purpose and scope added; working phrasing and the unit count removed. No selection changed. |
| `docs-authority/STL_MANIFEST.md` | Rev B. Rewritten; the expected meshes are those mapped in `import_mfg.py`, whose read folder is now the one the build writes. |
| `flow_graph/exporters/matplotlib/` metal_forming_pfd, mfg_shop_pfd, wafer_fab_pfd, fab_reagent_forks_pfd | Removed after checking what each drew and who cited it; replaced by the sector views `flow_graph/views/pfd-mfg.svg` and `pfd-fab.svg` (owner decision 2026-10-29). |
| `docs-authority/METAL_FORMING_EQUIPMENT.md` | Rev F. Section 7 sets the die schedule, the cold-mill gauge and width and the atomiser batch from the graph throughputs (A-M-416); `docs-authority/_mfg_tools.py` designs the tools. |
| `docs-authority/WAFER_FAB_EQUIPMENT.md` | Rev E. Section 4.1 gives the silicon charge from the wafer need (`flow_graph/param/fab_silicon.py`, A-M-417); STOCK_TO_FAB now carries the feed. |
| `docs-authority/WAFER_FAB_EQUIPMENT.md` | Rev F. Section 4.1 adds the argon loop IA-AR-CZ / IA-AR-CZ-BACK with the cold box, sized from the puller (A-M-417). |
| `docs-authority/_task_plan_gen.py` (AQS-PLAN-007) | Task group X-RTE generated from the graph: one task per open route without flow, grouped standby, return and retired routes, and the done routes with evidence (owner decision 2026-10-29). |
| `docs-authority/METAL_FORMING.md` | Rev D. Section 3.4 explains the tool design from the throughputs and points to the equipment list; the atomiser argon receiver described. |
| `flow_graph/param/standby_routes.py` (A-M-418) | New: a standby feed route carries the rate of the case that puts it in service; STOCK_TO_WIRE_DRAW rated at the S57 copper feed, with the METAL_STORE holding for the outage. |
| `flow_graph/param/standby_routes.py` (A-M-418) | IND_TO_ATOM rated at the IA-MELT-ATOM atomiser charge for a MET_MELT outage; IND_MELT runs one more heat a day in the outage. |
| `docs-authority/FAB_WET_INTERFACE.md` | Rev C. Route UPW_TO_FAB removed from the stream list; the route is retired on the graph as a duplicate of IA-UPW-FAB (X-RTE). |
| `docs-authority/_line_list.py`, `docs-authority/_iso_sheets.py` | Retired routes are skipped, and a sheet whose line left the line list is removed; five sheets of retired routes gone (owner decision 2026-10-29). |
| `flow_graph/param/si_refine.py` (A-M-419) | New: quartz reduction and chlorosilane refining sized from the CZ charge, with a selectable backup of a different technology; IA-SI-IMPORT retired; other imports that break the rule listed as X-RTE-IMPORT tasks (owner decision t58u). |
| `flow_graph/param/foundry_poly.py` (A-M-420) | The chlorinator carbon is plant pyrolysis char from OIL_PYRO, sized from the carbon need over its fixed carbon; the petcoke imports are gone; water make-up is allowed and the baseline site profile lists its water sources. |
| `flow_graph/param/sulfuric.py` (A-M-421) | New: ACID_PLANT makes the HF kiln acid on the contact process; the kiln cake is reduced with plant char and the rest of the sulfur is native sulfur ore, with a sulfur-ore-only route selectable; IA-H2SO4-MU retired (owner decision t59u). |
| `flow_graph/param/caustic.py` (A-M-422) | New: NAOH_PLANT makes the NaOH make-up from trona ore by lime causticising, with membrane chlor-alkali on the leach purge salt and halite ore selectable; EVAP_BASE removes the liquor water; IA-NAOH-MU retired (owner decision t59u). |
| `flow_graph/param/recovery.py` (A-M-423) | New: recovery-first inventory and check for every element taken as raw ore; the acid kiln now recovers the free acid sulfur too, the causticiser takes its lime from the acid-plant residue before limestone ore, and every ore-taking transfer function stamps a recovery record (owner decision t61u). |
| `flow_graph/param/foundry_poly.py` (A-M-424) | The pattern wax make-up is the plant C19-C28 paraffin cut on C19_TO_WAX after the dewax reclaim; IA-WAX-MU retired and the C19-C28 export falls by the draw (owner decision t59u). |
| `flow_graph/param/sulfuric.py` (A-M-425) | Q-034 closed under the owner delegation t62u: GYPSUM_LOOP stays (recovery first), and the cake kiln runs in campaigns from a cake store with an acid day store, which cuts its average load to about a fifth; CONTINUOUS duty is selectable. |
| `flow_graph/param/caustic.py` (A-M-426) | Q-035 and Q-036 closed under the owner delegation t62u: the sodium hydroxide top-up runs on the chlor-alkali cells with halite ore, with CAUSTICIZE selectable, and the cell hydrogen stays on the H2 header to the hydrogen store. |
| `flow_graph/param/foundry_poly.py` (A-M-427) | Q-037 closed under the owner delegation t62u: the cells take their oxide from the float-sink dense grit first, with the assay as driver inputs at 0 until AQS-ASSAY-TI-MO lands, and the dock concentrate covers the rest as the redundant source. |
| `flow_graph/param/solvent.py` (A-M-428) | IA-SOLV-MU retired: SOLV_PLANT redistils the spent bench solvent first and makes the shortfall from plant methanol and the chlorinator CO (MEOH_CO), with a galley food-waste fermentation selectable (FERMENT). |

## 3. In progress

Table 3.1 lists the pending pages whose rewrite has started.

Table 3.1. Pages partly rewritten

| Page | Note |
| --- | --- |
| `docs-authority/GLOSSARY.md` | Entries added in bulk on 2026-10-25 to clear the automated check gave wrong expansions (for example PA, PG, IED, FFC, CRC) or two meanings for one abbreviation; those were corrected on 2026-10-29. Many entries are still fragments, and some terms are defined twice under different headings. |
| `docs-authority/TASK_PLAN.md` | Sections 1 to 6 rewritten in `_task_plan_gen.py`; the task texts in sections 7 and 8 are still to rewrite. |
| `docs-authority/OPEN_QUESTIONS.md` | Purpose and scope rewritten; the question rows are still to rewrite. |

## 4. Pending

On 2026-10-25 every remaining page was taken off the pending list in one change because each passed the automated style check. Section 16 of the guide says that passing the check is not enough, and a review on 2026-10-29 found that most of those pages lack the identity lines, the record of revisions or the purpose and scope section that section 10 of the guide requires. They are back on the pending list. Each row gives the defects found; a page can have others that a reader will find only in the full rewrite.

Table 4.1 lists the pending pages directly under `docs-authority/`. Table 4.2 lists those in subfolders; most of them are generated, so the work is in their generators.

Table 4.1. Pending pages directly under docs-authority/

| Page | Defects found |
| --- | --- |
| `docs-authority/INSTRUMENT_LOOPS.md` | No purpose and scope section; working or stock phrasing. |
| `docs-authority/LIFE_FITOUT_PLAN.md` | No purpose and scope section; working or stock phrasing. |
| `docs-authority/LIFE_NOZZLE_SCHEDULE.md` | No record of revisions; no purpose and scope section. |
| `docs-authority/MATERIALS_STD.md` | No purpose and scope section; list items written as fragments; working or stock phrasing. |
| `docs-authority/MFG_MODEL_PLAN.md` | No purpose and scope section. |
| `docs-authority/O2_SOURCE.md` | No purpose and scope section. Written by `flow_graph/param/o2_source.py`; fix the generator. |
| `docs-authority/O2_SOURCE_AUDIT.md` | No record of revisions; no purpose and scope section. Written by `flow_graph/param/o2_source.py`; fix the generator. |
| `docs-authority/REV_M_CLOSURE_DUTY.md` | Arrows used in place of sentences; working or stock phrasing. |
| `docs-authority/SIGN_SCHEDULE.md` | No purpose and scope section. |
| `docs-authority/STUDY_UNITS_STUB.md` | Arrows used in place of sentences; working or stock phrasing. |
| `docs-authority/TERRACE_LANDSCAPE.md` | No purpose and scope section; list items written as fragments. |
| `docs-authority/TEST_PLAN.md` | No purpose and scope section; working or stock phrasing. |

Table 4.2. Pending pages in subfolders

| Page | Defects found |
| --- | --- |
| `docs-authority/duties/ACID_POLISH_SCRUB.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/AFTERBURNER_FLUE.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/ALK_SCRUBBER.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/BIOFILTER.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section; working or stock phrasing. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/BLACK_DIGEST.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/C29_RECYCLE.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CATCH_TANK.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CONTINUOUS_RECYCLE.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CRYO_AHU_COND_CONDENSABLE.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CRYO_AR.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CRYO_ASU.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CRYO_CO2.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CRYO_H2.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CRYO_HE.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CRYO_HX_Q4.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CRYO_KR.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CRYO_N2.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CRYO_NE.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CRYO_O2.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CRYO_XE.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/CURTAIL.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/EMETH.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/EVAP_ACID.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/EW_1.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/EW_2.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/EW_3.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/EW_4.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/EW_5.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/EW_6.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/EW_7.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/EW_8.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/EW_9.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/EXT_HALL.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/FAB_UPW_TANK.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/FLOAT_SINK.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/FLUE_KO.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/GEO_ORC.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/GLASS_DIGEST.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/HDR_CO2.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/HDR_H2.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/HDR_N2.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/HDR_O2.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/HDR_UPW.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/HEAT_SINK.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/HX8.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/IODIDE.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/LEACH_CSTR_1.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/LIGNO_PRE.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/MEOH_COND.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/MEOH_SYNTH.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/MEOH_TANK.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/MET_HX_Q4.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/MET_SCRUB.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/NCG_HEADER.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/NOX_SCRUB.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/PROD_C11_C18.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/PROD_C19_C28.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/PROD_C29.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/PROD_C5_C10.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/Q1_A.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/Q1_B.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/Q2_A.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/Q2_B.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/Q3_A.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/Q3_B.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/Q4_A.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/Q4_B.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/Q4_BUS.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/REMIN.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/ROOF_TANK.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/TERRACE_IRRIG.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/VAC_IND.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/duties/ZNBR2_BR2_REGEN.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. Section 1 is refreshed by `docs-authority/_duty_basis.py`; the rest of the sheet was written once and is not refreshed, so its header still names graph revision BH. |
| `docs-authority/fab/AL_POT.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. |
| `docs-authority/fab/COMB_HEAT.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. |
| `docs-authority/fab/POLY_OLEFIN.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section; working or stock phrasing. |
| `docs-authority/fab/VAC_IND.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. |
| `flow_graph/derived/MASS_FLOW_DERIVED.md` | No revision line; no date line; no record of revisions; no purpose and scope section; working or stock phrasing. |
| `models/mfg/AL_POT/build_log.md` | No document number line; no revision line; no record of revisions; no purpose and scope section; working or stock phrasing. |
| `models/mfg/BLACK_DEWATER/WORK_ORDER.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. |
| `models/mfg/EXPANDER/WO.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. |
| `models/mfg/FILM_CAST/WORK_ORDER.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. |
| `models/mfg/FLUX_PREP/WORK_ORDER.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section; working or stock phrasing. |
| `models/mfg/HF_GEN/WORK_ORDER.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. |
| `models/mfg/IND_MELT/WORK_ORDER.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. |
| `models/mfg/POLY_F/WORK_ORDER.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. |
| `models/mfg/POWDER_RESIN/WORK_ORDER.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. |
| `models/mfg/SHELL_BURNOUT/WORK_ORDER.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section; working or stock phrasing. |
| `models/mfg/TFE_SYN/WORK_ORDER.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. |
| `models/mfg/VDF_SYN/WORK_ORDER.md` | No document number line; no revision line; no date line; no record of revisions; no purpose and scope section. |
| `models/openscad/foam_ew/CUT_LIST.md` | No record of revisions; no purpose and scope section; working or stock phrasing. |
| `models/openscad/foam_ew/DECISIONS.md` | No document number line; no revision line; no record of revisions; no purpose and scope section; working or stock phrasing. |

## 5. Removed

Table 5.1. Pages and entries removed

| Removed item | Reason |
| --- | --- |
| `docs-authority/FARM_WASTE.md` (AQS-DUTY-015, number withdrawn) | set duties for processes (hydrochar composting, electrochemical pretreatment) that are not in the graph, with units no longer on the graph; no citations |
| `docs-authority/NUTRIENT_BALANCE.md` (AQS-DUTY-034, number withdrawn) | balanced a fish/larvae/duckweed/azolla loop whose units are no longer graph nodes; no citations |
| `docs-authority/NUTRIENT_GAPS.md` (AQS-DUTY-048, number withdrawn) | supply column relied on retired units and miscited AQS-DUTY-049; no citations |
| `docs-authority/SIDE_FARM.md` (AQS-SIDE-002, number withdrawn) | framed the biofilter and a fish tank, both no longer graph nodes; no citations |
| `docs-authority/TEXTILES_HEPA.md` (AQS-MFG-TEX-001, number withdrawn) | placeholder with no equipment, streams, duties or model; two authorities not in the repository |
| `docs-authority/FURNACE.md` (AQS-FURN-001, number withdrawn) | superseded by IND_MELT in FOUNDRY and the 7.5 kW coreless furnace of X-MFG-37; no citations |
| `docs-authority/FARM.md` (AQS-DUTY-044, number withdrawn) | Nitrogen-fixation study of the retired fish/clover/azolla farm model; no graph unit or page cites it. The live farm units carry their own duty sheets. |
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
| `docs-authority/SOLVENT_ROUTE.md` (AQS-DUTY-026) | Reviewed 2026-10-25. It describes the route to the ionic liquid [Bmim] acetate through 1-methylimidazole; the units IMID and QUAT are no longer graph nodes. The number is cited elsewhere, so it is kept until a decision. |
| `docs-authority/RED_AUDIT.md` (AQS-RED-001) | Rewritten, but two rows need a factual update: the sanitation row names COMPOST_TOILET and the cold-box row names EXPANDER, and neither is a graph node now. |
| `docs-authority/inventory/PIPE_INVENTORY.csv` (AQS-INV-003) | Lines S36 (WS_DOPE, FAB) and S57 (MET_MELT, MFG) have no piping class, material or joint type ("—" and "-"), so `WPS_REGISTER.md` cannot assign them a procedure. The class and material need to be set in the pipe inventory generator. |
| `docs-authority/GROUNDING.md` (AQS-ELEC-005) | Sections 1 and 4 describe the revision A grid (35 × 20 m ring, 12 rods, 1.14 Ω; GPR 494 V). AQS-ELEC-006 section 4 describes grid Rev B (196 × 174 m, 74 rods, 0.128 Ω, GPR 887 V), and `docs-authority/_grounding_study.py` now prints 0.150 Ω with 65 rods (area 25 392 m²). The three need to be reconciled before section 1 is restated. |
| `docs-authority/GREENHOUSE_ENVELOPE.md` (AQS-TRR-GH-001) | Streams S40 (overflow to terrace irrigation) and S42 (fertigation return) are named here, in AQS-TRR-001 and in the stream register, but neither is an edge of the plant flow graph. Should they be added to the graph or removed from the pages? |
| `docs-authority/MEOH_EQUIPMENT.md` (AQS-EQP-MEOH-001) | Only MEOH_SYNTH, MEOH_COND, MEOH_TANK and MEOH_FC are graph nodes. The graph has one MEOH_FERM where the list has MEOH_FERM_DIG and MEOH_FERM_STILL, and the remaining tags are on the list only. Should the list be cut to the graph, or the graph extended? |
| `docs-authority/RECT_EW.md` (AQS-ELEC-004) | Finding 1 names node RECT_EW, streams S17-EW and IA-RECT-EW-LOSS (7.73 kW) and a 38.66 kW AC input. The graph now has node RECTIFIER, supply S17 at 12.0 kW (A-M-231) and loss IA-RECT-Q4 at 1.0 kW; the channel streams IA-DC-EW_1 to IA-DC-EW_9 still match Table 2.1. Which AC input is correct? |
| `docs-authority/ELECTRODE_FAB.md` (AQS-MFG-ELC-001) | Study ST-ELC-01 gives about 0.3 kW average; the graph supplies ELECTRODE_COAT with 0.0792 kW (SF-ELECTRODE_COAT). Which is correct? |
| `docs-authority/PERF_TEST.md` (AQS-COM-003) | `_perf_test.py` takes every solid stream leaving an electrowinning cell as harvested metal, so IA-COAT-IN (0.02 kg/d, EW_1 to ELECTRODE_COAT, the electrode sent for coating) appears as a guarantee point measured by weighed cathode harvest. Should the selection exclude streams that do not go to a product? |
| `docs-authority/CONTROL_ARCH.md` (AQS-CTL-002) | The closing note says that, if the inventory already counts the high-level switches, the DI count is 113 too high. The figure 113 is a fixed number in `_plc_arch.py`; the instrument index now has 82 digital-input rows (`24 V DC discrete (DI)`). Should the note be computed from the index? |
| `docs-authority/O2_SOURCE.md` (AQS-PAR-005) | Not rewritten. Two generators write this page: `flow_graph/param/o2_source.py` (the current Rev D duty summary) and `flow_graph/param/o2_close.py` report(), whose Rev C closure report would overwrite it if run. The page says the Rev C sections regenerate at the next balance run. Which generator owns the page? Once that is settled, the template can be rewritten without the risk of the other writer restoring the old text. |
| `docs-authority/POWER_SIZING.md` (AQS-ELEC-007) | The note on driver `backup_gen_rated_kW` states 125 % of the critical load list in 5 kW steps, which gives 20 kW for the present critical loads, but the driver holds 40 kW (AQS-ELEC-007 section 5). Should the driver or its note change? |
| `docs-authority/duties/` | Duty sheets remain for units that are no longer on the graph, mostly farm, crop and animal units (for example ABE, CHICKENS, CROP_TOMATO, RECT_EW). `_duty_basis.py` skips them, so they keep Graph Rev BH and stale values. Should they be deleted, or moved to an archive? |
| `docs-authority/H2_EMBRITTLEMENT_REVIEW.md` (AQS-REV-H2-001) | The graph sends cathode hydrogen from EW_1 to EW_3 and EW_5 to EW_9, while AQS-STD-002 section 9 names EW_1, EW_2, EW_4 and EW_9. Which is correct? |
| `docs-authority/sizing/SANITATION.md` (AQS-DUTY-063) | The graph carries the sanitation train as the one node BLACK_DIGEST: Rev AC retired BLACK_DEWATER, BLACK_PASTEUR and BLACK_ALK_HOLD, although their equipment is still built. The electrical load of the train from its sizing is about 0.21 kW, while stream SF-BLACK_DIGEST feeds 0.105 kW, the digester alone. Should the barrier units return to the graph as nodes, and should the feed carry the whole train? Either change moves the bus demand, so neither was made. |
| `docs-authority/SOLVENT_ROUTE.md` (AQS-DUTY-026) | The ionic-liquid solvent chain (fermentation, acetic acid, glyoxal, formaldehyde, methylimidazole, chlorobutane and the quaternisation) has build models in `models/mfg/` but no units on the present graph. Should it be put back on the graph with its rates, or retired with its build models? |
| `docs-authority/SCRUBBER_CHEMISTRY.md` (AQS-GAS-002) | Revision A had a separate caustic scrubber for the vents of the glass digest and the BMED base tank, trimming the mist to salt for the BMED salt feed. Neither that scrubber nor its header is on the graph. Do these vents need their own unit, or does another unit cover them? |
| `docs-authority/sizing/FUEL_CELL.md` | The sizing page reports an empty envelope and a polyethylene vessel for the fuel cell. Should `flow_graph/param` sizing skip bought stacks, or size them from the vendor envelope? |
| `docs-authority/unregistered_doc_numbers.json` | Pages cite AQS-PFD-* flow diagram numbers that are in neither register. Should they be added to the drawing register with the scripts in `flow_graph/exporters/matplotlib/` as their source, or removed from the pages? |
| `docs-authority/unregistered_doc_numbers.json` | Many pages cite AQS-AUD-001, a crew and water audit that is not in the repository. Should it be added, or should each citation be replaced by the graph value it stood for? |
