# Self-copy bill of materials: critical-path parts and their on-site feedstock

Document number: AQS-BOM-SC-001  
Revision: H  
Date: 2026-10-25  
Authority: AQS-AUTH-001. The criteria for the minimum viable system are in AQS-UI-001 Rev C, sections 3.2 and 11. Other sources are listed in section 7. Not a PE stamp.

| Rev | Description | Date |
|---|---|---|
| A | First issue: critical-path parts against on-site feedstock, flagged Partial or Closed | 2026-10-01 |
| B | Lithography deferred with its resource left unreclaimed; blow moulding out of the MVS at scale step M1; next measurements added to the Partial rows | 2026-10-01 |
| C | Project decision: lithography in scope, with a study schedule towards a modelled tool; blow moulding in MFG and in the MVS; electrode coating in scope; `reprap_bom_complete` stays false | 2026-10-01 |
| D | The MVS stated as the goal of the design; each gap stated as an open study in the plan, not as an accepted end point | 2026-10-01 |
| E | First-principles duties issued for lithography, blow moulding and electrode coating (0.1 kW, 0.5 kW and 0.3 kW electrical); solid models still to be made | 2026-10-01 |
| F | Equipment identifiers mapped for the lithography, blow moulding, electrode coating, VCD, REMIN, ORC and solar-cell units; matrix judged complete and `reprap_bom_complete` set true; the `*_on_site` flags stay false | 2026-10-02 |
| G | Reconciliation with the unit bills of materials added (X-PRO-04); `reprap_bom_complete` set false because Cr, Mo, Ti and F are not recovered | 2026-10-16 |
| H | Rewritten to the documentation style guide (AQS-DOC-002); section 4 corrected to the current flag values in the graph; stale pointer to a copy outside this repository removed. No row, rate or identifier changed. | 2026-10-25 |

Licence: CERN-OHL-S-2.0.

## 1. Purpose and scope

One aim of the project is a plant that can make the parts needed to build a copy of itself from its own recovered materials. The RepRap project set the same aim for a desktop 3D printer, which prints most of its own parts; this page uses "RepRap-class" for that aim. The minimum viable system (MVS) is the smallest set of sectors that closes every mass, energy and life-support loop, and AQS-UI-001, section 3.2, makes this self-copy ability one of its criteria.

This page lists the critical-path parts: the assemblies the plant must be able to make for a copy of itself. For each one it names the on-site feedstock or stream, the unit and sector that make it, the equipment identifiers in the plant flow graph, a status flag and the study rate or next step. It then reconciles the list with the material of every line in the unit bills of materials (BOMs).

The page is evidence for a design study. It is not a purchase list. The procurement spreadsheets `manufacturing_bom.xlsx` and `materials_shopping_list.xlsx` are a separate record. The page does not claim vendor certificates, a professional engineer's (PE) stamp or solid models that do not exist.

## 2. Completeness flags

Two separate flags in the graph record how far the self-copy evidence has reached. They were defined on 2026-10-02 and are listed in Table 2.1.

Table 2.1. Completeness flags

| Criterion | Flag | Meaning |
|---|---|---|
| C4 | `reprap_bom_complete` | Every critical-path row has a feedstock, a study rate and issued equipment identifiers |
| C3 | `*_on_site` (for example `lithography_on_site`) | The unit has a modelled solid in FreeCAD and a design basis accepted by the authority having jurisdiction (AHJ), so that it can be promoted to Present in the graph |

C4 can be true while C3 is false. Neither flag may be forced by inventing vendor certificates, PE stamps or FreeCAD solids. The graph flag `loops_closed` needs criteria C1 to C5, including C3.

## 3. Critical-path matrix

The status flags used in the matrix are defined in Table 3.1.

Table 3.1. Status flags

| Flag | Meaning |
|---|---|
| Closed (doc) | The making path is named, the feedstock stream exists, and the study rates and equipment identifiers are issued |
| Partial | The making path is named, but a rate, a CAD model or a tool measurement is still open. A Partial row does not by itself prevent C4 when its study values are filled in |
| Missing | There is no on-site path yet. An open study is queued in the plan; this is not an accepted design outcome |
| Study | A first-principles duty or a schedule is issued; the solid model (C3) is still open |
| In-scope study | The capability is required for the MVS; the solid model or the nameplate is not yet issued and the study is queued |
| Reopened | The row was closed and has been reopened; the task named in the row gives the reason |

Table 3.2 gives the matrix at the baseline scale (`SCALE_M` = 1.0). Stream identifiers (S08), interface edges (IA-MET-FEED), unit identifiers (BLOW_MOLD), equipment identifiers (BLOW-CLAMP-01) and study identifiers (ST-BLOW-01) are written as in the graph.

Table 3.2. Critical-path parts, feedstock and making units

| Part or capability | On-site feedstock or stream | Making unit and sector | Equipment identifiers (graph) | Flag | Study rate or next step |
|---|---|---|---|---|---|
| Structural metal stock and fasteners | Metals on stream S08 to the crib; metal-forming streams S57 to S63; edges IA-MET-FEED, IA-FAB-CRIB and IA-MFG-DOCK | MFG: MET_MELT, drawing and milling | Metal-forming set (AQS-EQP-MFG-001) | Closed (doc) | The residual crib split is close to zero; campaign rate in kg/h at study level |
| Frames for RepRap printers and CNC machines, and printed parts | Polymer line fed by oil cuts; scrap stream S16; edges IA-BLOW-* | MFG: polymer line, CNC machine and mill; BLOW_MOLD | BLOW-CLAMP-01, BLOW-AIR-01, BLOW-MOLD-TOOL-01 | Closed (doc) | ST-BLOW-01: 0.5 kW electrical on average; 3 kg/h for 3 h/d (study) |
| Metal powder (S60) | Plated or melted metal, atomized; edge IA-MELT-ATOM | MFG, metals | Atomizer massing model (AQS-MFG-MET-001) | Closed (doc) | Residual melt split; the FreeCAD placeholders count towards C3 |
| Wire, milled stock and melt | S08 to the metals line; edge IA-MELT-MILL | MFG | Wire drawing and mill (MFG) | Closed (doc) | Continuous share 0.2 kg/h to 2 kg/h (study, AQS-AUD-001 section 10.6) |
| Ion-exchange membrane (IEM) and membrane film | Preferred: open membrane fabrication SI-IEM-01; alternative: recycling through the oil line | MEOH; polishing in DIGESTER (formerly WET) | SI-IEM stand-in (AQS-MeOH-001) | Closed (doc) | Oil-line recycling against a full ethylene dichloride (EDC) to polyvinyl chloride (PVC) route remains a study option; the path is not missing |
| Electrodes and electrode coating | Metal mesh or plate substrate; the coating booth exhausts to MET_AHU and the scrubber | MFG: ELECTRODE_COAT | ELC-BOOTH-01, ELC-SPRAY-01, ELC-CURE-01, ELC-EXH-01 | Closed (doc) | ST-ELC-01: 0.3 kW electrical; non-precious coating at scale step M1; the booth CAD model counts towards C3 |
| Seals and elastomers | Oil cuts and polymer | MFG | Class not yet set; no vendor certificate is assumed | Partial | The class on the specification sheet is not yet set; this does not affect the coverage of the matrix |
| Sensors and power electronics | FAB wafers, assembled in MFG; lithography schedule (section 3.1) | FAB, MFG and LITHO_STUB | LITHO-COAT-01, LITHO-ALIGN-01, LITHO-DEV-01 | Closed (doc) | ST-LITHO-01: 0.1 kW electrical; 3 wafer starts per day; the solid models count towards C3 |
| Czochralski (CZ) crystal puller and wafer tools | Silicon from S08; FAB train | FAB | FAB train (AQS-EQP-FAB-001) | Partial | It is not yet shown that the tools can make copies of themselves; open study. The row is not Missing |
| Cold box and CRYO internals | Metals and vacuum fabrication | MFG and CRYO | CRYO envelope | Partial | Maximum allowable working pressure (MAWP) to the ASME code not yet set; no certificate is assumed and no Present claim is made |
| Zinc–bromine (ZnBr₂) battery stack and bromine scrubber | Electrolyte make-up study; regeneration stream S69 | ZNBR2 and GAS | ZNBR2 and scrubber set | Closed (doc) | The energy storage peer is enabled; listing and the battery management system (BMS) are finished in operation |
| Methanol synthesis and direct methanol fuel cell (DMFC) | Streams S73, S74 and S76; stand-ins SI-DMFC and SI-IEM | MEOH | MEOH_SYNTH, MEOH_FC | Closed (doc) | A stand-in is not a purchase; storage bank sizing in AQS-ESS-001 |
| Hydro turbine and pump | Metals and seals | MFG and PUMPED_HYDRO | HYDRO_SET | Closed (doc) | The energy figure at scale step M1 is nominal (AQS-ESS-001) |
| PV cells for replacing the plant's own array | Solar-cell branch, AQS-EQP-FAB-PV-001 | FAB: SOLAR_PV_CELL | PV-TEX-01, PV-EMIT-01, PV-PSG-01, PV-ARC-01, PV-CON-01, PV-FIRE-01, PV-IV-01 | Reopened (X-GOV-20) | ST-SOLAR-01: 1.0 kW share; 3 cells/d; tool nameplates from in-house designs (X-MFG-38) |
| Photolithography: coat, align and develop | Solvent streams WS_SOLV S38 and S85; photoresist | FAB: LITHO_STUB | LITHO-COAT-01, LITHO-ALIGN-01, LITHO-DEV-01 | Closed (doc) | ST-LITHO-01; `lithography_on_site=false` until the FreeCAD file exists (C3) |
| Blow moulds and shoe moulds | Polymer melt from EXTRUSION and oil cuts | MFG: BLOW_MOLD | BLOW-CLAMP-01, BLOW-AIR-01, BLOW-MOLD-TOOL-01 | Closed (doc) | ST-BLOW-01; the FreeCAD mould model counts towards C3 |
| Textiles and high-efficiency particulate air (HEPA) filters | AQS-MFG-TEX-001 withdrawn 2026-10-25: the media line has no equipment, streams or duties behind it | MFG, optional | — | Withdrawn | Optional for the electrical part of the MVS |
| Vapor-compression distillation (VCD) and remineralization (REMIN) drinking-water train | Grey water S12 and S29; condensate; Ca, Mg and K salts | WTR: VCD_TRAIN and REMIN | OSS-VCD-*, OSS-REMIN-*, HAB_UV-01 | Closed (doc) | ST-VCD-01 and ST-REMIN-01; `vcd_remin_on_site=false` until the solid models and AHJ acceptance exist (C3) |
| Geothermal organic Rankine cycle (ORC) unit and ground heat exchanger (GHEX) | Heat from the GEO ground loop; GHEX design fixed pending a site survey | GEO: GEO_GHEX and GEO_ORC | OSS-ORC-EVAP-01, OSS-ORC-TURB-01, OSS-ORC-COND-01; KO_GEO_GHEX | Closed (doc) | ST-ORC-01; surplus heat is zero at scale step M1; the field borehole is outside this repository |

### 3.1 Photolithography study schedule

On 2026-10-01 the project decided that photolithography is in scope, because a self-sustaining plant needs it to make sensors and power electronics. Table 3.3 gives the study schedule towards a modelled tool. It remains in force.

Table 3.3. Photolithography study schedule

| Step | Study tag | Duty | Streams and utilities | Status |
|---|---|---|---|---|
| 1 | LITHO_COAT | Spin or spray coating of photoresist, then soft bake | Resist; solvent WS_SOLV S38; nitrogen S03 | Closed (doc) schedule; equipment LITHO-COAT-01 |
| 2 | LITHO_ALIGN | Alignment and exposure, contact or projection type | Optical or ultraviolet exposure; interim reference tool `MIDAS MDA-150` | Closed (doc) schedule; equipment LITHO-ALIGN-01 |
| 3 | LITHO_DEV | Development and hard bake; rinse | Developer to the organics and oil path; UPW | Closed (doc) schedule; equipment LITHO-DEV-01 |
| 4 | FAB_TOOL etch, implant and metal deposition | Existing L0 train (AQS-EQP-FAB-001) | Etch return S10 | Closed (doc) massing model |

The seed unit `LITHO_STUB` keeps `lithography_in_mvs=true` and `lithography_on_site=false` until its FreeCAD child objects exist (C3).

### 3.2 Blow moulding

Blow moulding is in the MFG sector and in the MVS (decision of revision C, still in force). Table 3.4 records the details.

Table 3.4. Blow moulding

| Item | Decision |
|---|---|
| Sector | MFG, in the polymer aisle beside INJECTION and EXTRUSION |
| Seed unit | `BLOW_MOLD` |
| Equipment identifiers | BLOW-CLAMP-01, BLOW-AIR-01, BLOW-MOLD-TOOL-01 |
| Solid model (C3) | Open; the FreeCAD mould solid does not yet exist |
| If switched off in a design study | The solver reports an open study in the queue, not an accepted unreclaimed end point |

### 3.3 Electrode coating

Electrode coating is in scope (decision of revision C, still in force). Table 3.5 records the details.

Table 3.5. Electrode coating

| Item | Decision |
|---|---|
| Seed unit | `ELECTRODE_COAT` (sector MFG) |
| Equipment identifiers | ELC-BOOTH-01, ELC-SPRAY-01, ELC-CURE-01, ELC-EXH-01 (exhaust to MET_AHU) |
| Exhaust | MET_AHU to MET_SCRUB (streams S71 to S72) |
| `electrode_coating_on_site` | False until the booth solid model and the coating formulation exist (C3) |
| Precious-metal coating (RuO₂–IrO₂) | Deferred; no nameplate is assumed |

### 3.4 Equipment identifiers by unit

Table 3.6 maps each study unit to its equipment identifiers and gives the state of its FreeCAD model and of its `*_on_site` flag. In the last column, `placeholder_skip` means the FreeCAD build places no solid for the unit, and `massing_only` means it places a block of the right size.

Table 3.6. Equipment identifiers by unit (revision F)

| Unit | Study | Equipment identifiers | FreeCAD model / on site |
|---|---|---|---|
| LITHO_STUB | ST-LITHO-01 | LITHO-COAT-01, LITHO-ALIGN-01, LITHO-DEV-01 | placeholder_skip / false |
| BLOW_MOLD | ST-BLOW-01 | BLOW-CLAMP-01, BLOW-AIR-01, BLOW-MOLD-TOOL-01 | placeholder_skip / false |
| ELECTRODE_COAT | ST-ELC-01 | ELC-BOOTH-01, ELC-SPRAY-01, ELC-CURE-01, ELC-EXH-01 | placeholder_skip / false |
| VCD_TRAIN | ST-VCD-01 | OSS-VCD-FEED-01, OSS-VCD-HX-01, OSS-VCD-EVAP-01, OSS-VCD-COMP-01, OSS-VCD-COND-01 | placeholder_skip / false |
| REMIN | ST-REMIN-01 | OSS-REMIN-CA-01, OSS-REMIN-MG-01, OSS-REMIN-K-01, OSS-REMIN-MIX-01, HAB_UV-01, OSS-POTABLE-TK-01 | placeholder_skip / false |
| SOLAR_PV_CELL | ST-SOLAR-01 | PV-TEX-01, PV-EMIT-01, PV-PSG-01, PV-ARC-01, PV-CON-01, PV-FIRE-01, PV-IV-01 | placeholder_skip / false |
| GEO_ORC | ST-ORC-01 | OSS-ORC-EVAP-01, OSS-ORC-TURB-01, OSS-ORC-COND-01 | massing_only |
| GEO_GHEX | ST-ORC-01 | KO_GEO_GHEX (mapped FreeCAD feature) | mapped; design fixed pending the site survey |

No vendor certificate or PE stamp is claimed for any row.

### 3.5 What still blocks C3

Table 3.7 lists, for each capability, the decision taken at revision F and the work that still blocks its `*_on_site` flag (C3). None of these items blocks C4.

Table 3.7. Decisions and remaining C3 blockers (revision F)

| Topic | Decision | Still blocks C3 |
|---|---|---|
| Lithography | In scope; equipment identifiers and rates issued | FreeCAD LITHO_* solids; choice of the ultraviolet exposure source |
| Blow moulding | In MFG and in the MVS; equipment identifiers and rates issued | FreeCAD mould solid |
| Electrode coating | In scope, with MFG as the main sector; equipment identifiers and rates issued | FreeCAD booth model; laboratory coating recipe |
| VCD and REMIN | Physical basis and equipment identifiers issued | FreeCAD skids; AHJ acceptance for drinking water |
| Metal powder and membranes | Feedstock paths named | Optional deeper campaigns in kg/h |

## 4. Completeness flags in the graph

Table 4.1 lists the self-copy flags held in the graph (`mvs.mvs_criteria.self_copy` in `flow_graph/plant_flow_graph.json`) and in the seed model `design_tool/aqs_design_tool/data/candidate_mvs.json`, with their values at this revision. The graph is the authority if this table and the graph disagree.

Table 4.1. Self-copy flags

| Flag | Meaning | Value |
|---|---|---|
| `self_copy.critical_path_documented` | This matrix exists | true |
| `self_copy.reprap_bom_complete` | The matrix, equipment identifiers and study rates are complete (C4) | false since revision G (section 8); true at revision F |
| `self_copy.lithography_on_site` | The lithography path has a modelled solid (C3) | false |
| `self_copy.lithography_in_mvs` | Lithography is required for the MVS | true |
| `self_copy.blow_mold_in_mvs` | Blow moulding is required for the MVS | true |
| `self_copy.vcd_remin_on_site` | The drinking-water train has a modelled solid (C3) | false |
| `self_copy.electrode_coating_on_site` | Electrode coating has a modelled solid (C3) | false |
| `self_copy.shopping_list_only` | A procurement spreadsheet exists without a feedstock map | false |

## 5. Gaps

At revision F the matrix in section 3 was judged complete for C4. The reconciliation in section 8 later showed that the stainless steel, titanium and fluoropolymer lines have no on-site source, so C4 is not met. The solid models, AHJ acceptance, the field borehole for the GHEX, the MAWP values and the in-house design data remain open for C3. Each is queued as a study in the plan; none is an accepted omission. The design tool tracks progress towards the MVS as these studies finish.

## 6. Owner question

Open question Q-013 in `OPEN_QUESTIONS.md` (AQS-OQ-001) asks whether to add recovery routes for Cr, Mo, Ti and F or to change the materials of the affected lines. Until it is answered, `reprap_bom_complete` stays false and the materials are unchanged.

## 7. Related documents

The sources for this page are AQS-MVS-GAP-001 section 4.3, AQS-GAP-001, AQS-EQP-STUDY-001, AQS-STUDY-L2-001, AQS-STUDY-PRESENT-001 and the unpublished planning note DECISION_LOG_A3_A5. The equipment pages are AQS-MFG-MET-001, AQS-EQP-MFG-001, AQS-EQP-FAB-001, AQS-EQP-FAB-PV-001 and AQS-MFG-ELC-001. The methanol, materials-flow and stream pages are AQS-MeOH-001, AQS-MF-001 and AQS-STR-001.

<!-- X-PRO-04 BEGIN -->
## 8. Reconciliation with the unit bills of materials

This section is generated by `docs-authority/_sc_reconcile.py` (task X-PRO-04, assumption A-M-206). It compares the material of each of the 1436 lines of the plant bill of materials (AQS-PRO-001) with the chemical species carried on the present edges of the graph. A line is Closed when the graph carries every element its material needs, Partial when an on-site route is named but not yet built as units, Missing when no on-site source exists, and Unstated when the line does not state a classifiable material. The result for each line is in `docs-authority/inventory/SELF_COPY_RECON.csv`.

Table 8.1 gives the number of lines under each flag.

Table 8.1. Bill of materials lines by flag

| Flag | BOM lines |
|---|---|
| Closed | 269 |
| Partial | 372 |
| Missing | 356 |
| Unstated | 439 |

Table 8.2 gives the reason for each line that is not Closed.

Table 8.2. Reasons for lines that are not Closed

| Flag | Gap | Lines |
|---|---|---|
| Unstated | material not stated on the unit BOM line | 358 |
| Unstated | not classed: aluminium | 20 |
| Unstated | not classed: PE (rotomoulded / fabricated) (graph nod | 13 |
| Unstated | not classed: carbon (ram class) | 12 |
| Unstated | not classed: n/a (massing only) | 10 |
| Unstated | not classed: ceramic-fibre board 128 kg/m3 | 7 |
| Unstated | not classed: purchase item | 6 |
| Unstated | not classed: pine | 5 |
| Unstated | not classed: per AQS-STD-002 | 4 |
| Unstated | not classed: 1 | 3 |
| Unstated | not classed: alumina (90 % class) | 1 |
| Missing | needs Cr (and Mo for 316L); Cr/Mo not recovered by the leach/EW train | 265 |
| Missing | no fluorine source on site; end of life Q-011 | 62 |
| Missing | Ti not recovered (ilmenite route not in the graph) | 21 |
| Missing | reason not stated by the classification rule | 4 |
| Missing | no mica source; substitute glass-mica from GLASS is a study | 3 |
| Missing | line says bought: no on-site path stated | 1 |
| Partial | olefin cracking and polymerisation are not yet units in the graph | 238 |
| Partial | Cl on site; ethylene and VCM steps not yet units | 72 |
| Partial | graphitisation above 2,500 C not in the heat ladder | 22 |
| Partial | monomer route not yet in the graph | 14 |
| Partial | glass fibre from GLASS; vinyl ester resin route is a study | 14 |
| Partial | boron not recovered; soda-lime or high-silica glass from GLASS is the substitute study | 8 |
| Partial | electrical steel and magnet wire enamel are studies | 2 |
| Partial | Al stays in the leach liquor as solute; alumina recovery is a study | 2 |

Result: the rows of Table 3.2 for structural metal stock and for wire, milled stock and melt hold for carbon steel, Cu and Ni. They do not hold for the stainless steel and titanium lines, which need Cr, Mo and Ti that the graph does not recover. Those lines, and every fluoropolymer line, are Missing until an on-site route or a substitute material is designed. `reprap_bom_complete` is therefore false from revision G.
<!-- X-PRO-04 END -->
