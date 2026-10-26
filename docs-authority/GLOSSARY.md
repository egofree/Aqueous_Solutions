# Glossary

Document number: AQS-GLO-001  
Revision: B  
Date: 2026-10-25  

| Rev | Description | Date |
|---|---|---|
| A | First issue | — |
| B | Purpose statement added; the withdrawn document-line scan removed from the A-M entry; style findings cleared | 2026-10-25 |


## 1. Purpose and scope

This glossary fixes the vocabulary of the design. Fixed names are written in capital letters, exactly as they appear on the drawings, and no other names are used for them.

## 2. Entries

Each entry is `{term -- definition}`. Acronyms used in the plant flow graph, design-tool UI, PFDs/MFD/EFD layers, sector taxonomy, and authority docs are listed here with expansion and plant role. No invented rates or nameplates.

## Project identifiers and conventions

{AQS-xxx-nnn -- Document number. Every controlled document carries one, with a revision letter and a date (e.g. AQS-SEC-001 Rev H). DOC_REGISTER.md lists them.}

{Rev (graph) -- Revision of the plant flow graph, AQS-FLOW-GRAPH-001. The letters run from A to Z and then continue as Rev AA, Rev AB, Rev AC and so on. The current revision is stated in the `revision` field of `flow_graph/plant_flow_graph.json` (Rev AC at the time of writing). A document that says "checked against graph Rev X" was last reconciled at that graph revision. Document revisions are separate and also use letters.}

{X-xxx-nn -- Task id in TASK_PLAN.md (AQS-PLAN-007). The middle part is the work group, e.g. X-PAR parametric model, X-PIP piping, X-SAF safety, X-MAT materials, X-INV building-block inventories, X-ELS electrical, X-GOV governance. TASK_PLAN.md lists all groups.}

{Triage tag -- Every open task in TASK_PLAN.md is tagged desk (can be closed from files in this repository), hardware (needs a built item, a test or a site measurement) or owner (waits on a project decision recorded in OPEN_QUESTIONS.md).}

{A-M-nnn -- Curated assumption, kept in assumptions_manual.json with its basis, sensitivity and the test that would replace it. ASSUMPTIONS_REGISTER.md also lists scanned entries: A-G-xxxxxx (study and assumed values in the graph), and A-P-xxxxxx (model parameters in models/mfg/*/params.json).}

{Q-nnn -- Open question in OPEN_QUESTIONS.md, with the default the work proceeded on.}

{S## -- Inter-block stream id from the stream register (AQS-STR-001), e.g. S64. Intra-block edges in the graph use prefixed ids: IA-* (intra-aisle process edges, e.g. IA-ACID-01) and HL-* (heat-ladder edges, e.g. HL-HX8-Q4-A).}

{Unit id -- Upper-case name of a unit in the graph, e.g. LEACH_CSTR_1. It names the duty sheet (duties/LEACH_CSTR_1.md), the sizing sheet, the P&ID and any CAD model. Unit ids are locked; see the Locked units section.}

{Sector id -- Upper-case name of a sector, the top level of the system tree (flow_graph/system_tree.yaml). The current sectors are listed in Plant sectors and systems below.}

{Study -- A value or document that is the model's current best calculation, not a certified or stamped figure.}

{By design -- A derived file that is intentionally not regenerated from the current graph, with the reason recorded in DERIVED_REVISIONS.md.}

{Owner ruling / project decision -- A design choice made by the project owner and recorded with its date, usually in OPEN_QUESTIONS.md, a dated note under notes/ or the document it affects. It is the basis for a value where no reference or calculation applies.}

{MVS -- Minimum viable system: the smallest set of sectors that closes every loop (mass, energy, life support) and still exports a surplus. See SECTOR_DEFINITIONS.md and DESIGN_TOOL_ARCHITECTURE.md.}

{Bounding case -- The feed assay or operating case that sets the largest duty for a unit. Units are sized for it so the plant stays feedstock-agnostic.}

## Process and chemistry

{Anolyte -- Oxidizing chloride liquor on the anode side of an EW or CRU cell. In this plant it is Salria (HCl + NaClO₃, high ORP). Wall: CPVC or PVDF. Not PP, not HDPE, not bare metal.}

{AEM -- Anion-exchange membrane. Aminated PS–PVC on PP felt. Drawn orange. Passes Cl⁻ into the ACID chamber of BMED.}

{BMED -- Bipolar-membrane electrodialysis. A 3-compartment repeating unit (BASE | SALT | ACID) bounded by bipolar membranes. Splits NaCl brine into NaOH, HCl, and the water the BPM consumes. Chlorate is not made in this stack.}

{BPM -- Bipolar membrane. CEL (cation-exchange layer, drawn blue) faces the cathode. AEL (anion-exchange layer, drawn orange) faces the anode. Water splits at the junction: H⁺ leaves the CEL into ACID, OH⁻ leaves the AEL into BASE.}

{Catholyte -- Metal-bearing liquor on the cathode side of an EW cell. Fed from LEACH CSTR 1 through a coarse strainer into EW-1, then by overflow EW-2 … EW-9.}

{CEM -- Cation-exchange membrane. Sulfonated PS–PVC on PP felt, double-layer, hot-swappable. Drawn blue. Passes Na⁺, metal cations; blocks Cl⁻ and chlorate.}

{Chlorate / NaClO₃ -- The leach oxidant. Regenerated in CRU from Cl₂ absorbed into NaOH or brine. Not generated inside BMED.}

{CRU / CHLORATE -- Chlorate regeneration unit. Takes Cl₂ from EW and BMED anodes and converts it to NaClO₃ for REGEN LEACH.}

{CSTR -- Continuous stirred-tank reactor. LEACH CSTR 1 is the only leach vessel. CSTR 2 is the float weir on that vessel, not a second tank. CSTR 3 is the injection-molded PVC / fiberglass sink auger in the floor of CSTR 1. Together they are LEACH CSTR 2–3 FORK.}

{E° -- Standard reduction potential. The EW aisle plates in descending E°: Au → Ag → Cu → Pb → Sn → Ni → Fe → Cd → Zn.}

{EW -- Electrowinning. Metal ions reduced onto a cathode as sheet or powder.}

{Faradaic yield -- Fraction of cell current that plates the intended metal. 70–95 % on the main aisle; much lower in the polish bank.}

{Float–sink -- Density split inside the leach liquor. Light organics float; metals, glass, ceramic, FR-4, and dense plastic sink.}

{FR-4 -- Glass-epoxy circuit-board laminate. Must not enter the induction pyrolyzer. Leaves at VIBRATORY SPLIT → BURNOUT ROTARY.}
{FRM -- Former short name for the FARM sector, still found in older CAD files. It is not a sector identifier; read it as FARM.}


{Leach / Salria -- Oxidative chloride leach: HCl + NaClO₃, 70–85 °C, ORP > 1.5 V, pH ≈ 0. Dissolves metals. Doubles as the float–sink medium.}

{MMO -- Not used. The anode is titanium with a 0.5 mm lead-dioxide coat, or carbon, or nickel. Iridium and IrO₂–Ta₂O₅ are not on the anode spec.}

{NCG -- Non-condensable gas from pyrolysis quench. Goes to AFTERBURNER, not to atmosphere.}

{ORP -- Oxidation–reduction potential. Leach target > 1.5 V vs. SHE-equivalent probe.}

{pH-shift precip -- P-Al (pH 5.0–5.5, Al(OH)₃), P-Mg (pH 10.5–11, Mg(OH)₂), P-Ca (pH 12–12.5, Ca(OH)₂ / CaCO₃). NaOH from BMED BASE. These metals are not electrowon.}

{Pregnant liquor -- Metal-laden leachate pumped from LEACH CSTR 1 into EW-1. Solids leave the tank on CSTR 3, not on a pre-EW drum. Coarse strainer only on the pump suction.}

{REGEN LEACH -- HCl from BMED ACID plus NaClO₃ from CRU, returned to LEACH CSTR 1.}

{REE -- Rare-earth elements. Not aqueous-EW from this chloride liquor. CEM concentrate then oxalate or hydroxide (PK-5).}

{S.E.M / SEM Tech -- Salt Electro Mining. Rowow’s electrochemical separation platform. Core (membranes, cells, general methods) is CERN-OHL-S. This flowsheet uses that core; it is not a Rowow product.}

{SALT FEED -- Filtered brine into the BMED SALT chamber: depleted EW / polish liquor, rinse, and Br⁻ / HCl condensate. Q4 condensate is the makeup water the BPM splits.}

{Tenor -- Dissolved-metal concentration in liquor. Main aisle is high tenor; POLISH BANK is mg–g / L leftovers.}

## Locked units

{AFTERBURNER -- Destroys NCG and tars. Q1 source. Flue jackets BURNOUT ROTARY (HX-7). Atmospheres stay separate — oil vapor does not enter the rotary.}

{BMED REGEN -- The BMED stack plus product tanks (NaOH PRODUCT, HCl PRODUCT) and CRU.}

{BURNOUT ROTARY -- Indirect-fired rotary, 450–550 °C air / steam, SiC or high-Ni tube. Burns epoxy and residual organics off glass / ceramic / FR-4. Not the oil auger.}

{CERAMIC GRIT -- Undigested ceramic (Al₂O₃, SiC, filler). Product: media, aggregate, or the host matrix that vitrifies PK-9 sludge.}

{DRYER -- Paddle or belt, 80–120 °C from HX-4 (Q3). Float plus dense-plastic jumper. Condensate to Q4.}

{EW CASCADE -- Nine CEM cells in E° order, EW-1 through EW-9. Each cell harvests independently to METALS / ELEMENTS.}

{FLOAT DEWATER -- Conveyor after CSTR 2 (the weir on LEACH CSTR 1). Liquor drains back to CSTR 1. Solids go DRYER → INDUCTION PYROLYZER.}

{FRACTIONATOR -- Continuous packed or tray column. HX-3 reboiler from Q2. Cuts: C5–C10, C11–C18, C19–C28, C29+ (heavies recycle to pyro).}

{GLASS / CERAMIC BRANCH -- VIBRATORY SPLIT → RINSE + DEWATER → BURNOUT ROTARY → MILL → NaOH DIGEST → SILICATE + Ca / Al / Mg HYDROXIDES + CERAMIC GRIT.}

{HOPPER -- Bulk-waste feed.}

{INDUCTION PYROLYZER -- Ti Grade 2 outer pipe, cast-iron conical auger, external induction coils couple to the iron. 400–600 °C. Charge is dry. Liquor never enters this pipe. No FR-4.}

{LEACH CSTR 1 -- The only leach vessel. Receives shred from the vibratory conveyor and REGEN LEACH. Lidded; acid-gas takeoff. Heated by HX-5 (Q3). CSTR 2 (float weir) and CSTR 3 (sink auger) are fittings on this tank, not sister vessels.}

{LEACH CSTR 2–3 FORK -- The density split on LEACH CSTR 1. CSTR 2 = float weir. CSTR 3 = injection-molded PVC / fiberglass auger in the tank floor. No second leach tank.}

{METALS / ELEMENTS -- Plated products from the EW aisle and polish plates. Sheets: Ag, Cu, Pb, Sn, Ni, Cd, Zn. Powder: Au, Fe (Sn optional).}

{MILL -- Dry mill after burnout, < 300 µm, feed to NaOH DIGEST.}

{NaOH DIGEST -- 80–90 °C BMED caustic. Glass → silicate liquor. Al / Ca / Mg → hydroxides. Wall PP or Ni. HX-6 (Q3).}

{OIL LINE -- FLOAT DEWATER → DRYER → INDUCTION PYROLYZER → QUENCH / CONDENSER → FRACTIONATOR → hydrocarbon cuts. NCG to AFTERBURNER.}

{POLISH BANK -- Nine parallel CEM cells (PK-1…PK-9) on POLISH HEADER after EW-9 and pH-shift. Not a second E° aisle.}

{POLISH HEADER -- Manifold that feeds every polish cell the same depleted liquor.}

{QUENCH / CONDENSER -- Direct oil quench. Condensable oil down to the still; NCG across to AFTERBURNER.}

{RINSE + DEWATER -- Countercurrent wash of glass / ceramic / FR-4. Liquor and fines to REGEN LEACH / BMED SALT.}

{SHREDDER -- Continuous size reduction. Sits above LEACH CSTR 1. Feeds a vibratory conveyor that dumps shred straight into the tank. No filter on that drop. Dust hood at the throat.}

{SILICATE -- Na-silicate liquor from digest. Farm Si, silica gel, wafer-fab slurries.}

{VACUUM DRUM FILTER -- Harvest filter only. Manual / startup: one shared drum after the bund pails. Auto: one drum per EW cell, then induction or oil-gas melt. Not a pre-leach or pre-EW solids filter. Pump suction has a coarse strainer only.}

{SINK DEWATER -- Conveyor after CSTR 3. Liquor drains back to LEACH CSTR 1. Solids to VIBRATORY SPLIT.}

{VIBRATORY CONVEYOR -- Elevated belt or pan from SHREDDER into LEACH CSTR 1. No screening, no filter.}

{VIBRATORY SPLIT -- Wet classification of drained sink solids. Dense thermoplastic to OIL LINE. Glass / ceramic / FR-4 down the glass branch.}

## Cells

{EW-1 -- Au. Plate on Ti blank. Product powder.}

{EW-2 -- Ag. Plate on Ti blank. Product sheet / powder.}

{EW-3 -- Cu. Plate on 316L starter. Product sheet.}

{EW-4 -- Pb. Plate on 316L. Product sheet.}

{EW-5 -- Sn. Plate on 316L. Product sheet / powder.}

{EW-6 -- Ni. Plate on Ti blank. Product sheet.}

{EW-7 -- Fe. Plate on 316L or graphite. Product powder.}

{EW-8 -- Cd. Plate on 316L. Product sheet.}

{EW-9 -- Zn. Plate on Ti or Al starter. Product sheet.}

{P-Al -- Al(OH)₃ at pH 5.0–5.5.}

{P-Mg -- Mg(OH)₂ at pH 10.5–11.}

{P-Ca -- Ca(OH)₂ / CaCO₃ at pH 12–12.5.}

{PK-1 -- Co. Plate.}

{PK-2 -- Mn. Plate or anodic MnO₂.}

{PK-3 -- Cr. Cr(III) plate or Cr(OH)₃.}

{PK-4 -- Li. CEM concentrate → Li₂CO₃ / Li₃PO₄. Not aqueous EW.}

{PK-5 -- REE. CEM concentrate → oxalate / hydroxide. Not aqueous EW.}

{PK-6 -- Hg. Sealed plate on Ti / graphite.}

{PK-7 -- Tl. Plate or iodide precip.}

{PK-8 -- Bi / Sb. Plate.}

{PK-9 -- U / Th / Ra / Po. Sealed CEM; sludge vitrified into CERAMIC GRIT.}

{OVERFLOW LAUNDER -- Gravity overflow between adjacent EW cells, OVF_EW_1_2 … OVF_EW_8_9. Ø80 mm (PUMP_D, the liquor-line class), seated 12 mm (WALL) into each cell on the solid. OVF_EW_9_POLISH carries the EW-9 tail to POLISH BANK (IA-EW-09). Not a pumped line.}

## Heat

{Q1 -- 400–800 °C. Pyro wall, pyrolysis vapor, afterburner flue.}

{Q2 -- 150–250 °C. Thermal-oil / steam; still reboiler; burnout jacket.}

{Q3 -- 80–120 °C. Charged only downhill from Q2. Draws: dryer (HX-4), digest (HX-6), leach (HX-5). No EW heat (no lift).}

{Q4 -- < 80 °C. Still condenser, rinse, BMED makeup, HVAC. EW / polish ohmic reject through HX-8.}

{HX-1 -- Q1 pyro wall recovery.}

{HX-2 -- Q1 flue → oil / thermal loop.}

{HX-3 -- Q2 fractionator reboiler.}

{HX-4 -- Q3 dryer.}

{HX-5 -- Q3 leach CSTRs.}

{HX-6 -- Q3 NaOH digest.}

{HX-7 -- Q2 burnout rotary jacket.}

{HX-8 -- EW aisle exchanger to Q4. EW liquor 55 → 51 °C preheats the Q4 return 45 → 49 °C, 6 K approach. Edges HL-HX8-Q4-A/B. AQS-DUTY-008 Rev B.}

{HX-8b -- Polish ohmic reject onto the EW tap; reaches Q4 through HX-8.}

{Heat rule -- EW heat goes to Q4 through HX-8, never to Q3. Q3 serves its draws in order dryer, digest, leach; any shortfall is electric trim at the process. If pyro is down, Q3 runs on inventory and then on trim.}

{Loop thermosyphon -- Downhill ladder step (HL-Q1/Q2/Q3-*-DOWN). Evaporator high in the hotter store, condenser low in the colder store, the colder store raised on a stand so the condensate leg rises at least 0.30 m; vapor riser and condensate return with a low-cracking check. The hardware diode. Own fluid per step. AQS-DUTY-008 Rev C §14.2.}

{Stepped stores -- Heat-ladder store elevations from Rev K: Q1 z −6000, Q2 −5150, Q3 −4250, Q4 −3350 mm on both ladders, plan positions unchanged. Gives the gravity rise for the downhill steps.}

{XL-Q1..XL-Q4 -- Cross-tie loops. One pumped single-phase loop per tier joining Q*_A and Q*_B; carries both HL-Q*-X and HL-Q*-X-BA. Pump runs only when the two stores differ by more than 5 K; normally off. Oil on Q1/Q2, water on Q3 (2.5 bar a) and Q4. AQS-DUTY-008 Rev C §14.3.}

{Rated duty -- For an HL-* edge, the single-ladder throughput × 1.25; carried as the edge rate. Normal duty is both ladders on line. AQS-DUTY-008.}

{S89 -- HDR_CO2 → GROW_BED CO₂ enrichment dose through the FARM AHU, 3.0 bar a, DN15 316L. 11.616 kg/d at Rev K; 15.637 kg/d at Rev L (S85 + S90); 16.101 kg/d from Rev M (S11 carbon in the afterburner basis). Only consumer of HDR_CO2. CO₂ only: no tee to HDR_O2, hab air, the HAB return or the dock. AQS-DUTY-009.}

{S90 -- HABITATION → HDR_CO2, 4.021 kg/d metabolic CO₂ (S02 3.36 kg/d O₂ × respiratory quotient 0.87 × 44/32), desorbed from the hab CO₂ sorbent bed. CO₂ only; hab air never enters the header. Rev L, AQS-DUTY-010.}

{rate_basis / rate_source -- Edge params from Rev L. rate_basis is the derivation in one line; rate_source is the document or graph value it rests on. With medium, conditions and rate_kind (derived or by_difference). AQS-DUTY-010.}

{By difference -- A rate set so that one node balance closes, for example the leach-loop brine bleed (level control) or S10 (spent bench liquor = sum of bench inputs − S38). Marked rate_kind by_difference; a node that closes this way is reported separately from one whose terms are all derived.}

{balance_rev_l -- Node params block from Rev L listing the off-graph terms used in the node balance (feed, harvest, vents, losses, life loads), each with its basis. AQS-DUTY-010.}

{Design day -- Rev L and Rev M conservation basis: daily average, plant running normal on both ladders, dry weather, one pumped-hydro cycle per day.}

{HOLD placeholder -- S87 and S88 in Rev L: placeholder edges with the reason on the edge. Retired in Rev M (no physical flow; AQS-DUTY-011 §4.16).}

{balance_rev_m -- Node params block from Rev M listing the off-graph terms used in the node balance, replacing balance_rev_l. AQS-DUTY-011.}

{rev_l_value / rev_l_from / rev_l_to -- Edge params from Rev M recording the Rev L rate and, for a retargeted edge, the Rev L endpoints. AQS-DUTY-011.}

{Rating case -- For a trim heater, the duty with no ladder heat, no Q4 preheat and the lowest reaction credit; the issued rating is ceil(rating case × 1.25) to 0.5 kW. AQS-DUTY-011.}

{HX-9 -- Q4_BUS branch exchanger preheating the cold leach make-up (S68, S10, S16, S39, S72, S28) to 55 °C. Duty is the S100 rate. Not an HL-* edge. AQS-DUTY-011.}

{HX-10 -- Q4_BUS branch exchanger preheating the GLASS_DIGEST caustic to 55 °C. Duty is the S101 rate. Not an HL-* edge. AQS-DUTY-011.}

{S91 / S92 -- BMED_BASE → GLASS_DIGEST NaOH for the cullet digest, and GLASS_DIGEST → SALT_FEED silicate liquor, which leaves in the pH-9 cake (S97). Rev M. AQS-DUTY-011 §4.7.}

{S93 / S94 -- PV_ARRAY → SOL_ARK_60K daily-average PV energy, and SOL_ARK_60K → LOAD_AGG itemized process and life loads. Rev M. AQS-DUTY-011.}

{S95 -- HDR_O2 → LEACH_CSTR_1 O₂ sparge that closes the leach electron balance after the anode Cl₂ sparge and CRU chlorate. Rev M. AQS-DUTY-011.}

{S96 / S97 -- GLASS_RINSE → BOUNDARY_EXPORT sink residue (unleached metal, fillers, unassigned assay) and SALT_FEED → BOUNDARY_EXPORT pH-9 filter cake (silica, sodium aluminosilicate, hydroxides). Both pending leachate characterization (RS-RESIDUE-TCLP). Rev M.}

{S98 / S99 -- SALT_FEED → VCD_TRAIN BMED diluate, and VCD_TRAIN → BOUNDARY_EXPORT distillate export (MVS clean-water surplus). Rev M.}

{S100 / S101 / S102 -- Q4_BUS sinks: HX-9 leach make-up preheat, HX-10 caustic preheat, and borefield recharge to GEO_GHEX (by difference). Rev M. AQS-DUTY-011.}

{IA-BMED-05..10 -- Rev M chloride-loop edges: brine bleed POLISH_BANK → SALT_FEED (05), BMED HCl → CONTINUOUS_RECYCLE (06), NaOH to ALK_SCRUBBER (07), alkaline scrubber liquor to CRU (08), CRU liquor to CONTINUOUS_RECYCLE (09), NaOH to SALT_FEED (10). AQS-DUTY-011 §4.6.}

{Option B (chloride) -- Rev M provisional decision: anode Cl₂ is sparged back into LEACH_CSTR_1 as oxidant (0.95 absorbed), the remainder goes ALK_SCRUBBER → CRU → CONTINUOUS_RECYCLE, and BMED regenerates HCl from the brine bleed. Option A (all Cl₂ to ALK_SCRUBBER) needs about 16 kW of BMED. AQS-DUTY-011.}

{Utility import -- The GRID-port term that closes the SOL_ARK_60K balance by difference on the design day. Rev M: about 40 kW average; the MVS energy-surplus criterion is not met. AQS-DUTY-011 §4.9.}

{CO₂ enrichment -- Farm air held at 1000 ppm in the 16 h photoperiod. GROW_BED fixes S04 (1.109 kg/d); the S89 carbon leaves with farm exhaust air. Use, not sequestration.}

{CO2-rich cut -- S67B. The product of the vacuum swing adsorption (VSA) unit at FLUE_KO, ≥ 90 mol % CO2, dry. N2, O2, and NOx are rejected at FLUE_KO. Not raw flue. The only CRYO_CO2 credit for afterburner carbon; S18 carries none since Rev J.}

## Gas headers

Four process headers stay isolated. A fifth caustic branch is local to BMED / digest. The ZnBr2 Br2 scrubber is not on any of these.

{HDR_DUST -- Negative at hopper, shredder, split, and bag inlets. Baghouse then ID fan. Fines return to LEACH CSTR 1. Do not tee into acid-gas.}

{HDR_ACID_GAS -- Negative at CSTR lid and EW / polish anode hoods. HCl, Cl2, acid mist. Knit demister → packed NaOH scrubber (BMED BASE) → FRP induced-draft fan → stack. Pregnant liquor to CRU. Not sewer.}

{HDR_H2 -- Negative at cathode hoods. Flame arrestor → H2 dryer → stack or fuel. No ignition sources. Do not join oil vapor or acid-gas.}

{HDR_OIL_VAPOR -- Negative at pyro vapor nozzle → QUENCH. NCG to AFTERBURNER under forced draft. HX-7 is a flue jacket on BURNOUT ROTARY, not a duct tee. Oil vapor does not enter the rotary.}

{HDR_CAUSTIC -- NaOH mist from NaOH DIGEST and BMED BASE. Packed water column with BMED ACID trim. Liquor to SALT FEED. Do not dump this stream into HDR_ACID_GAS.}

## Materials

{316L -- Low-carbon stainless. Cathode starter sheets on Cu, Pb, Sn, Cd, Fe, Co, Bi/Sb. Pits in hot Salria — not a cell wall.}

{CPVC -- Chlorinated PVC. Default wet-wall for Salria, EW mid-aisle, polish, BMED ACID. Solid sheet, not foam-core. Solvent-weld with Weld-On 724 class (THF / MEK / cyclohexanone). Welds PVC and CPVC only.}

{PP -- Polypropylene. BMED BASE, P-Mg, P-Ca, digest caustic. Wrong for hot oxidizer.}

{PVDF -- Polyvinylidene fluoride. Alternate for anolyte / BMED ACID. Wrong for hot NaOH. Does not solvent-weld with PVC cement.}

{Ti Grade 2 -- Commercially pure titanium. Anode substrate and some cathode blanks. Dry pyro shell. Erodes as a tank wall in hot high-ORP chloride — do not use it that way.}

{Weld-On 724 -- Chemical-resistant CPVC cement. Cure fully before Salria fill.}

## Streams

{Dark grey -- Solids / shred.}

{Green -- Aqueous / leach / brine.}

{Rust -- Organics / oil.}

{Blue -- Glass–ceramic.}

{Amber dashed -- Heat / HX.}

{Teal -- Products.}

{Blue bar -- CEM.}

{Orange bar -- AEM.}

{Blue | orange bar -- BPM.}

## Products

{Ca / Al / Mg HYDROXIDES -- Cakes from pH-shift and from NaOH DIGEST. Farm / metal-line feed.}

{CHAR / ASH -- Inorganics that rode the float through pyro. Handed to the glass-branch mill.}

{GAS OIL / WAX -- C19–C28 cut. Lube / polyolefin feed.}

{HCl PRODUCT -- From BMED ACID. Wall CPVC or PVDF.}

{HYDROCARBON CUTS -- Collective oil-line products headed back to monomers / resins.}

{MID DISTILLATE -- C11–C18. Diesel-range / polymer oil.}

{NAPHTHA / LIGHTS -- C5–C10 overhead. Solvent and cracking feed.}

{NaOH PRODUCT -- From BMED BASE. Wall PP. Feeds pH-shift, digest, and CRU.}

{POLISH METALS -- Co, Mn (or MnO₂), Cr, Hg, Tl, Bi, Sb. Join METALS / ELEMENTS.}


## Diagram layers and design tool

{PFD -- Process flow diagram. Line or campus view of process units and streams. In the typed plant graph, PFD is a view filter over the same unit_id / stream_id set (lock layered_views), not a competing topology authority.}

{MFD -- Mass-flow diagram. Inter-block mass edges and claim status (extends mass_flow / STREAM_REGISTER themes). Graph view filter; campus MFD may collapse intra-aisle detail.}

{EFD -- Energy-flow diagram. Three energy layers over the same graph: electrical, thermal (Q1–Q4 / HX), and chemical-storage ESS charge–discharge (lock efd_three_layers). UI labels: EFD-elec, EFD-thermal, EFD-ess.}

{SLD -- Single-line diagram. Electrical one-line (utility → Sol-Ark → ATS → loads). Graph export path uses the efd-elec layer; matplotlib `electrical_sld.png` is an optional exporter.}

{MVS -- Minimum Viable System. Smallest self-sustaining human colony design intent: full manufacture and habitation, self-copy, scale up/down, closed loops including all three ESS peers, plus surplus export of food, clean water, materials/goods, and energy. Sandbox must not overwrite locked MVS.}

{IA / IA-* -- Intra-aisle stream identifiers on the typed graph (e.g. IA-EW-*, IA-ESS-*). Distinct from inter-block S## in STREAM_REGISTER. Required under lock full_depth_now; rates stay null until Present authority supplies them.}

{CAD -- Computer-aided design. FreeCAD solids, campus placement, and parametric envelopes under CAD_SCRIPTING_PROTOCOL / FREECAD_PROTOCOL. Topology authority remains the typed plant flow graph.}

{BOM -- Bill of materials. Self-copy critical-path list (AQS-BOM-SC-001) and export-pack bom artefacts from graph nodes/flags.}

{UI -- Design-tool user interface. React + SVG graph-layer schematic (AQS-UI-001); loads flow-graph views PFD/MFD/EFD-*.}

{GUI -- Graphical user interface. Same design-tool surface as UI in architecture prose.}

{SCALE_M -- Parametric plant scale multiplier (AQS-SCALE-001). On-disk baseline is 1.0 (M1). Layout driver; not a rate invention.}

{WP -- Work package. Planning tranche label (e.g. WP-A10, WP-Bp1) for design-tool / flow-graph delivery. Not a plant unit.}

{Issued envelope -- L×W×H in mm held in a graph node's params.size_mm with size_note "L×W×H mm, issued envelope". A massing and clearance size, not a vendor nameplate.}

{Placement copy -- plant_placed.FCStd. Generated by flow_graph/apply_placement.py from placement_seed.json; mapped Features with an issued envelope are re-boxed to that size. plant.FCStd is copied on disk, never opened or written. Not tracked in git.}

{Maintenance clearance -- Minimum box-to-box gap in placement_seed.json rules: maint_clear_mm 600; electrical_face_clear_mm 1100 for BACKUP_GEN and FUEL_CELL on every face. Line items (recycle pipes, headers) are exempt but may not intersect. Applies within one level; pairs separated by a structural slab are checked for no intersection only (seed Rev H clearance_scope).}

{Study envelope -- L×W×H in mm in params.size_mm with size_note "L×W×H mm, study envelope (basis)". Derived from the unit duty when no envelope is issued (HX8, NOX_SCRUB, MEOH_COND, RELIEF_CRYO, CONTINUOUS_RECYCLE in Rev K). Created on the placement copy, never used to resize a mapped Feature. Not a nameplate.}

{Boundary class -- Graph node class for a logical, non-physical node with no solid: BOUNDARY_EXPORT (dock freight door) and, since Rev K, LOAD_AGG (S17/S20 electrical accounting). Counted separately from solids and headers in the done test.}

{Fixed-feature row -- Seed row with "fixed_feature": true. Records where an existing Feature already sits (CATCH_TANK, FLUE_KO = FLUE_CAP, RELIEF_H2 = H2_STACK). The applicator never writes it.}

## Plant sectors and systems

{AQS -- Aqueous Solutions document and plant namespace prefix. Document numbers take the form AQS-*-### (e.g. AQS-SEC-001, AQS-STR-001, AQS-FLOW-GRAPH-001).}

{SEC / AQS-SEC -- Sector Definitions catalogue (AQS-SEC-001). Maps every plant sector_id to one Sector Definition class and required_for_mvs_closure flags.}

{STR / AQS-STR -- Stream register (AQS-STR-001). Inter-block stream_id scheme S## between sectors/blocks.}

{MF / AQS-MF -- Mass-flow authority (AQS-MF-001). Closed-loop claims and surplus language for mass paths.}

{DIGESTER -- Process sector: L-1 leach / EW / BMED / CRU / polish line; 150 kg/d feed basis. Primary mass recycle. Named WET before graph Rev AC.}

{WET -- Former name of the DIGESTER sector, renamed at graph Rev AC. Older documents and dated notes still use it.}

{FOUNDRY -- Process sector: smelting pots, casting, forging and rolling. Goods-surplus train with MFG and FAB.}

{POLYMERS -- Process sector: fluoropolymer synthesis, polyolefin and form factors.}

{HEAT -- Utility sector: heat-ladder batteries Q1–Q4, Q4_BUS and Q4 services (AQS-HEAT-LADDER-001).}

{MEOH -- Energy storage sector (electrochemical): methanol synthesis, store and the MEOH_FC fuel cell. An ESS peer; also feeds other processes.}

{PUMPED_HYDRO -- Energy storage sector (gravity): roof reservoir to catch tank through a penstock turbine-pump. One of the three ESS peers.}

{OIL -- Process sector: dryer → pyro → fractionator hydrocarbon cuts; afterburner flue to CRYO.}

{GLASS -- Process sector: rinse → burnout → mill → NaOH digest; silicate / ceramic products.}

{GAS -- Process sector: scrub / demister / baghouse / stacks; acid-gas and dust returns. Secondary utility/header role for HDR_*.}

{FAB -- Process sector: wafer fab, UPW, wet-bench reagents, solar-cell stub. Goods surplus path.}

{MFG -- Process sector: shop, polymer line, metal forming (MET folded under MFG). Goods surplus path.}

{NUT -- Process sector: nutrient dose (P-Al/Mg/Ca and BMED salts → farm). Distinct from REMIN potable dose.}

{FARM -- Life-support sector: grow beds / aquaculture / LED; food surplus. CAD name FARM (alias FRM).}

{HAB -- Life-support sector: habitation, galley, sleep, grey/black return; crew load driver.}

{CRYO -- Utility sector: cold box and O₂/N₂/CO₂/H₂ receivers; H₂ normal path S64. Former alias: `CRY`.}

{WTR -- Utility sector: roof/catch tanks, VCD / REMIN / UPW polish, grey treat (AQS-WTR-001).}

{TRR -- Former utility sector for terrace overflow / irrigation, retired 2026-10-18 with the TERRACE_IRRIG unit. AQS-TRR-001 keeps its document number.}

{ELEC -- Utility sector: Sol-Ark / ATS / RECT / MCC distribution hub, plus the PV array, the ZnBr2 flow battery, the standby genset and the fuel cell as units since graph Rev AC.}

{ELEC_PV -- Former sector for PV generation; since graph Rev AC the PV_ARRAY unit sits in ELEC. Panel and PLC tags such as LP-ELEC_PV keep the old name.}

{GEO -- Utility sector (study): ground heat exchanger and heat pump to Q4; optional GEO_ORC electric stub.}

{DOCK -- Export / dock sector: north dock and freight elevators for surplus goods export.}

{MET -- Metal forming capability folded under MFG (not a separate sector_id).}

{CORE -- Building distribution (cores, shafts, stairs). Not a mass–energy sector toggle.}

## Water and life support

{UPW -- Ultrapure water. Plant HDR_UPW / S01 class (< 1 µS/cm post-ED polish); fab further polishes to S27. Pre-remin water serves farm/fab; drinking uses REMIN.}

{VCD -- Vapor-compression distillation. Regenerates clean distillate from condensate and treated grey (heat exchanger `VCD_HX`, then evaporator `EVAP`, compressor `COMP` and condenser `COND`). VCD_TRAIN is class vessel. Rates are on the graph.}

{REMIN -- Remineralization. Doses Ca²⁺ / Mg²⁺ / K⁺ (and related) from core salt inventory into drinking water (S26). For potable only — not farm nutrient dose S07.}

{ED -- Electrodialysis. Hab/UPW polish stage (HAB_ED_POLISH / UPW POLISH) toward S01 conductivity claim; BMED middle chamber may assist, not as a second wet-line stack.}

{EDI -- Electrodeionization. Optional fab UPW polish peer to mixed-bed IX on FAB_UPW_IX.}

{IX -- Ion exchange. Mixed-bed polish on the fab UPW train.}

{UF -- Ultrafiltration. Particulate / colloidal barrier on FAB_UPW_UF.}

{NF -- Nanofiltration. Potable integrity check class after remin (with UF/UV).}

{VCM -- Vinyl chloride monomer, the monomer polymerized to make polyvinyl chloride (PVC).}

{UV -- Ultraviolet disinfection / TOC destruction on potable finish and fab UPW.}

{TOC -- Total organic carbon. Fab rinse target class on UPW.}

{MED -- Membrane electrodialysis (grey stage GREY_MED). Root-07 multi-effect distillation narrative is adapted; VCD remains primary distillate regenerator.}

{RPZ -- Reduced-pressure-zone backflow preventer. Required theme on HDR_UPW at potable taps.}

{HEPA -- High-efficiency particulate air filtration. Life and clean-space filtration theme.}

{MEP -- Mechanical, electrical, and plumbing. Life-plate utility fit-out (AQS-MEP-001).}

{AHU -- Air-handling unit. Hab / cryo / greenhouse HVAC air side.}

{HVAC -- Heating, ventilation, and air conditioning. Q4 reject and life climate; keep process and life air paths separated per HSE.}

{FFL -- Finished-floor level. Building-stack datum for each level (world Z = 0 is L0 grade FFL).}

## Power, ESS, and electrical

{ESS -- Energy Storage System. MVS requires all three peers: ZNBR2 (electrochemical), MEOH (electrochemical), and PUMPED_HYDRO (gravity). Disabling a peer in sandbox flags unreclaimed_resource / incomplete closure.}

{ZNBR2 / ZnBr₂ -- Zinc–bromide hybrid flow battery ESS peer. Outdoor skid preference; Br₂ scrub/regen on S69. Couples to Sol-Ark BATT DC.}

{MEOH / MeOH -- Methanol train and store. Required ESS peer; also process feed. IEM-based DMFC path preferred; synth and FC discharge edges on EFD-ess / MFD.}

{ORC -- Organic Rankine Cycle. Binary geothermal electric stub GEO_ORC (S48). Rating TBD until GHEX survey; do not invent kW.}

{GHEX -- Ground heat exchanger. Closed-loop vertical bore-field class GEO_GHEX; loop fluid dedicated (not UPW / CATCH).}

{PEM -- Proton-exchange membrane. H₂/O₂ fuel-cell chemistry on FUEL_CELL (AQS-FC-001); couples BATT DC via FC_DCDC. Not the Sol-Ark GEN AC port.}

{DM -- Dry matter: the mass of a food or biomass sample after its water is removed.}

{DMFC -- Direct methanol fuel cell. MeOH discharge path; IEM-based preferred over conventional packaging. Distinct from PEM H₂ FC.}

{IEM -- Ion-exchange membrane. Generic SEM-Tech membrane family (CEM/AEM style) used on EW, BMED, ZnBr₂, and MeOH FC paths.}

{FC -- Fuel cell. The FUEL_CELL unit (PEM, in ELEC) or MEOH_FC discharge; electrical offtake to BATT DC, not GEN.}

{PV -- Photovoltaic. Roof/yard array generation (PV_ARRAY, in ELEC).}

{ATS -- Automatic transfer switch. Selects utility vs Sol-Ark LOAD for plant main; service bypass path.}

{MCC -- Motor control center. Plant AC distribution after ATS.}

{RECT -- Rectifier skid. Process DC for EW / BMED / polish (RECT-EW, RECT-BMED, RECT-PK).}

{DC -- Direct current. BATT bus, rectifiers, the DC-to-DC converter outputs of the fuel cells and the methanol fuel cell.}

{AC -- Alternating current. Utility, Sol-Ark LOAD/GEN, MCC, ORC couple stubs.}

{GEN -- Sol-Ark generator AC port. BACKUP_GEN (H₂ genset) only — not FC or RECT hard-tee.}

{BATT -- Sol-Ark battery DC window. The zinc–bromine battery and the DC-to-DC converters of the fuel cells connect here.}

{HSE -- Health, safety, and environment. Hazard separation and fire-area authority (AQS-HSE-001).}

## Compliance and codes

{HAZOP -- Hazard and operability study. Worksheets in HAZOP.md, actions in HAZOP_ACTION_REGISTER.md.}

{SIF / SIL -- Safety instrumented function and its safety integrity level (IEC 61511). Listed in CAUSE_EFFECT.md.}

{P&ID -- Piping and instrumentation diagram. One sheet per unit under pid/.}

{ITP -- Inspection and test plan (ITP.md).}

{WPS / PQR -- Welding procedure specification and the procedure qualification record that supports it (WPS_REGISTER.md).}

{VFD -- Variable-frequency drive.}

{ESD -- Emergency shutdown.}

{GA -- General arrangement: the plant layout model and drawings.}

{RO / EDI -- Reverse osmosis and electrodeionization, the UPW polish steps.}

{AHJ -- Authority Having Jurisdiction. Local building/fire official whose edition and amendments govern permits; design docs are not a PE stamp.}

{MAQ -- Maximum Allowable Quantity. Code inventory cap for hazardous materials (oxidizers, H₂, flammables) before occupancy upgrade.}

{MAWP -- Maximum Allowable Working Pressure. Vessel/piping design pressure; relief set ≤ MAWP (study values in AQS-ASM-001 until PE/AHJ).}

{OFL -- SIL Open Font License, the licence of the Liberation fonts (SPDX identifier OFL-1.1).}

{PE -- Professional Engineer. Stamp/permit role; architecture docs state Compliant-intent or study until PE confirmation.}

{NFPA -- National Fire Protection Association. Fire/H₂/ESS/oxidizer themes (e.g. NFPA 2, 13, 30, 55, 400, 855).}

{CGP -- Construction General Permit, the TPDES general permit for stormwater from construction sites.}

{EPCRA -- Emergency Planning and Community Right-to-Know Act, the United States law that requires Tier II chemical inventory reports.}

{LEPC -- Local Emergency Planning Committee, which receives EPCRA Tier II reports.}

{NSR -- New Source Review, the air permit programme for new or modified emission sources.}

{POTW -- Publicly owned treatment works, a municipal sewage treatment plant.}

{TAC -- Texas Administrative Code.}

{TCEQ -- Texas Commission on Environmental Quality, the state environmental regulator.}

{TPDES -- Texas Pollutant Discharge Elimination System, the TCEQ water discharge permit programme.}

{VOC -- Volatile organic compound.}

{ORD -- Prefix of Parker Hannifin handbook numbers; ORD 5700 is the Parker O-Ring Handbook.}

{WPB -- Wrought pipe, grade B: the carbon steel butt-weld fitting grade of ASTM A234.}

{WS -- Wet synthesis: the reagent units (WS_*) that make fab chemicals such as hydrofluoric acid, peroxide, ammonia, nitric acid and potassium hydroxide.}

{CAMEO -- Computer-Aided Management of Emergency Operations; CAMEO Chemicals is the NOAA database of chemical hazards and reactivity groups.}

{GMR -- Gas-to-metal ratio: the mass of atomising gas used per unit mass of metal powder produced.}

{UA -- The product of thermal transmittance (U-value) and area, summed over a building envelope, in W/K.}

{FS -- Full scale: an instrument accuracy stated as a percentage of the top of its range.}

{AI -- Analogue input: a controller input channel that reads a continuous signal such as 4-20 mA.}

{AO -- Analogue output: a controller output channel that sends a continuous signal, such as a speed reference to a variable-frequency drive.}

{MRP -- Media Redundancy Protocol of IEC 62439-2, which recovers an Ethernet ring after a single break.}

{PI -- Proportional-integral: a feedback control loop that acts on the error and on its integral over time.}

{AISC -- American Institute of Steel Construction, publisher of AISC 360, the specification for structural steel buildings.}

{KL -- Effective length of a column: the actual length L multiplied by the effective length factor K for its end conditions.}

{AG -- Aktiengesellschaft, a German public limited company; part of company names such as SFC Energy AG.}

{VSA -- Vacuum swing adsorption: gas separation by adsorbing a component under pressure and releasing it under vacuum.}

{EMT -- Electrical metallic tubing, a thin-wall steel conduit for electrical conductors.}
{NEC -- National Electrical Code. Service, disconnect, and working-space themes.}

{ASME -- American Society of Mechanical Engineers. Vessel and B31.3 piping class sheets (AQS-ASM-001).}

{IBC -- International Building Code. Occupancy and construction overlays with NFPA/HSE.}

{OSHA -- Occupational Safety and Health Administration. Egress, LOTO, and workplace themes.}

{LOTO -- Lockout/tagout. Energy isolation for rectifiers, shredder, pyro, melt, Sol-Ark.}

{WEEE -- Waste electrical and electronic equipment. One case inside the AQS-ASSAY-001 feed envelope. Mixed WEEE is the reference point the held rates were built on, not the design feed.}

{SPDX -- Software Package Data Exchange. Licence identifier convention (CERN-OHL-S-2.0).}

{OSE -- Open Source Ecology. Upstream GVCS / Civilization Starter Kit reference map (AQS-REF-CSK-001); not bundled into the tree.}

{CSK -- Civilization Starter Kit. OSE documentation set for a subset of GVCS machines.}

{GVCS -- Global Village Construction Set. OSE catalogue of industrial machines mapped as coverage/study/candidate against Aqueous sectors.}


{M1 -- Module / plant baseline at SCALE_M = 1.0. Layout and study duties reference M1; do not copy legacy campus kW claims onto M1 without evidence.}

{BMS -- Battery management system. ZnBr₂ / ESS charge–discharge inhibit and Sol-Ark gateway theme.}

{SOC -- State of charge. ESS energy state from amp-hours and chemistry indicators (e.g. ORP on ZnBr₂).}

{LEL -- Lower explosive limit. H₂ headspace trip theme on zinc-tank / H₂ headers.}

{LFL -- Lower flammable limit. NFPA 69 explosion-prevention theme (H₂ < 25% LFL class).}

{SG -- Specific gravity (relative density, water = 1). Used for the liquid head term of the atmospheric design pressure (A-M-174).}
{AUD -- The plant audit document AQS-AUD-001, whose numbered sections carry the study bands cited by the closure transfer functions.}
{BH -- Graph revision BH, the revision whose rates were restored verbatim into CRYO_ASU and its edges (owner ruling 2026-10-18, D-AIR).}
{PQ -- Photosynthetic quotient, the mol CO2 fixed per mol O2 released by the grow bed (1.0 in the closure layer, TAIZ2015).}
{MJ -- Megajoule, 10^6 joule. The latent heat of vaporisation of water is 2.454 MJ/kg at 20 C (NIST_WEBBOOK); the basis of the AHU latent load and the site evaporative rejection charge.}
{TF -- Transfer function: the rate rule that sets a graph edge's flow (closure by difference, stoichiometry or a published relation), tagged in the rate note (X-PAR-02).}
{LT -- Level transmitter (ISA 5.1).}
{TEFC -- Totally enclosed fan-cooled: motor enclosure class (IEC 60034).}
{BOD -- Biochemical oxygen demand: the biodegradable-organic load of a water stream.}
{FOG -- Fats, oils and grease: the floatable organic fraction of a waste water stream.}
{CIP -- Clean-in-place: recirculated chemical cleaning of equipment without opening it.}
{CGA -- Compressed Gas Association: the US cylinder-valve and gas-equipment standard body.}
{NIST -- National Institute of Standards and Technology, source of the property tables cited in the balance layer.}
{BVAD -- Baseline Values and Assumptions Document, NASA/TP-2015-218570: the life-support baseline values source (BVAD2022).}
{EDBM -- Electrodialysis with bipolar membranes: the BMED process class.}
{OA -- Outside air (ventilation intake).}
{DHF -- Dilute hydrofluoric acid: the wet-bench oxide etch class.}
{ASF -- Anderson-Schulz-Flory: the chain-growth distribution that sets the hydrocarbon cut spread of an oligomerization or synthesis product.}
{WC -- Water column: pressure head unit (mmWC).}
{SW -- Seawater (site profiles: the seawater source and rejection mode).}
{ALK -- The alkaline house scrubber class (ALK_SCRUBBER).}
{GPM -- Gallons per minute (US liquid flow unit).}
{TIG -- Tungsten inert gas welding (GTAW).}
{HCFC -- Hydrochlorofluorocarbon.}
{ADS -- The adsorption chiller class (ADS_CHILL): driver heat, chilled-water output.}
{CDRA -- Carbon dioxide removal assembly: the sorbent-bed CO2 removal train of the habitation air loop.}
{NOX -- Nitrogen oxides (NO and NO2, reported as NO2): combustion and scrubber chemistry species.}
{ORR -- Oxygen reduction reaction: the fuel-cell cathode reaction.}
{RQ -- Respiratory quotient: mol CO2 exhaled per mol O2 consumed (0.87 study crew value).}
{SF -- Supply feed: the electrical feed edge prefix of the load list (SF-<UNIT>).}
{SWL -- Safe working load: the rated capacity of a hoist or lifting device.}
{LSHH -- High-high level switch: the 90 percent overfill trip element (ISA 5.1).}
{TL -- Long-period transition period of the design response spectrum (ASCE 7-22 Chapter 22 maps).}
{HE -- Helium (CRYO_HE noble-gas stream).}
{VAC -- Vacuum (the vacuum melting and casting chain: VAC_IND, VAC_CAST).}
{WO -- Work order (the per-unit fabrication document).}
{GDE -- Gas diffusion electrode: the porous gas-side electrode class of the peroxide and fuel cells.}
{STOI -- Stoichiometric: the exact reaction proportion, used in rate-note derivations.}
{SDC -- Seismic design category (IBC 1613 assignment from the design spectral accelerations).}
{ICC -- International Code Council, publisher of the IBC.}
{ELYZ -- The electrolyser plant unit tag (H2O_ELYZ node and its SF feed).}
{POLYF -- The fluoropolymer resin stream prefix (POLY_F outputs).}
{QPL -- Qualified products list: the buyer's subset of a standard class.}
{CEA -- Controlled environment agriculture: indoor crop production under artificial light and climate control (the Cornell CEA lettuce handbook is the DLI and efficacy source).}
{DLC -- DesignLights Consortium: the horticultural lighting qualification programme whose QPL lists LED efficacy ranges.}
{GCR -- Ground coverage ratio: photovoltaic array area divided by the ground or roof area it occupies; PVWatts applies a default when the site has none.}
{HDS -- Hydrostatic design stress: the long-term rated stress of a thermoplastic pipe material (CPVC 2000 psi class; manufacturer derating tables apply at temperature).}
{SIC -- Silicon carbide (the SIC_FURNACE deoxidation-carbon charge and its CO return).}
{HD -- Harmonization document of CENELEC (HD 231 harmonizes motor frame dimensions to IEC 60072-1).}
{HI -- Harvest index: the edible fraction of the total dry biomass that the crop line produces.}
{PO -- Purchase-order document: the buying document. The applicable standard class, never the maker sheet, is the design basis (AQS-PLAN-006 rule).}
{HDR -- Plant header prefix (HDR_H2, HDR_O2, HDR_CO2, HDR_UPW, HDR_N2): the gas and fluid collection lines.}
{IND -- Shorthand for the induction melt chain (IND_MELT and its 25 kW share of the foundry feed).}
{CHG -- Charge: the charging-side quantity of a storage pair, against the discharge quantity DIS.}
{IMO -- International Maritime Organization, publisher of the SOLAS, MARPOL, MODU and intact-stability instruments cited by the floating-island site family.}
{QC -- Quality control (check prefix QC-nn in the design-check record).}
{XY -- The plan-view coordinate pair (x, y) in millimetres.}
{FFC -- Free-flow chlorine: the chlorine product form shipped at the dock from the pot cells.}
{CRC -- Chemical resistance chart: the per-material compatibility table in AQS-STD-002.}
{PA -- Phosphoric acid (H3PO4), the WS_PHOS store.}
{SUMP -- The collection sump of a scrubber or tank system.}
{PG -- Pressure gauge.}
{DOE -- United States Department of Energy, publisher of OTEC and hydrogen cost studies.}
{DSC -- Differential scanning calorimetry: the thermal-analysis test for phase-change and decomposition.}
{EER -- Energy efficiency ratio: cooling output in BTU/h per watt of electrical input.}
{GC -- Gas chromatograph: the composition-analysis instrument.}
{HPA -- High-pressure aeroponics: misting at 40 to 80 psi with sub-100 micron droplets (JAE2022_AERO).}
{IACS -- International Annealed Copper Standard: the 100 percent conductivity reference for copper and aluminium conductors.}
{IED -- Intelligent electronic device: any microprocessor-based protection or control device on the network.}
{IMC -- Intermediate metal conduit: the steel wiring raceway class (NEC Article 342).}
{NDIR -- Non-dispersive infrared: the absorption-based gas-analysis method.}
{NPSH -- Net positive suction head: the pump inlet pressure margin above the liquid vapour pressure.}
{TGA -- Thermogravimetric analysis: the mass-loss thermal test for sorbent and catalyst characterisation.}
{WHO -- World Health Organization, source of the drinking-water quality guidelines (GDWQ).}
{WHSV -- Weight hourly space velocity: mass of feed per mass of catalyst per hour.}
{XRF -- X-ray fluorescence: the non-destructive elemental composition analysis method.}
{LR -- Load ratio: the ratio of applied to rated load in the structural checks.}
{CSA -- Compressive stress area, or the Canadian Standards Association (context-dependent).}
{HTHA -- High-temperature hydrogen attack: the Nelson-curve damage mechanism for steels in hydrogen service.}
{RP -- Recommended practice (e.g. API Recommended Practice).}
{DWV -- Drain, waste and vent: the non-pressure plumbing piping class.}
{AE -- Analytical element or alarm element, per ISA 5.1 tag letters.}
{ST -- Speed transmitter, or temperature element (context-dependent ISA 5.1 tag).}
{ZT -- Position transmitter (ISA 5.1): reports ram or valve stroke position.}
{EDTA -- Ethylenediaminetetraacetic acid: the chelating agent used in lithium and metal recovery.}
{PMI -- Positive material identification: the alloy-verification test (XRF or optical emission spectroscopy).}
{UT -- Ultrasonic testing: the non-destructive thickness and flaw examination method.}
{ETAG -- European Technical Assessment Group (construction products).}
{PECS -- Power and energy conversion system.}
{PTL -- Photothermal layer, or the partial transmission loss (context-dependent).}
{UHMW -- Ultra-high molecular weight (polyethylene): the wear-resistant polymer class.}
{ECTFE -- Ethylene-chlorotrifluoroethylene: the fluoropolymer lining and piping material.}
{FFKM -- Perfluoroelastomer: the highest-grade elastomer for aggressive chemical seals.}
{IGA -- Integrated gate amplifier, or iodine gas absorption (context-dependent).}
{PPI -- Pulses per inch, or the polypropylene intermediate (context-dependent).}
{TIMET -- TIMET (Titanium Metals Corporation), the titanium-alloy grade reference.}
{CRI -- Chemical reaction index, or the reduction ratio (context-dependent).}
{EMF -- Electromotive force: the cell potential in volts.}
{ORG -- Organic (the organics fraction of a waste stream, to the oil line).}
{ASSY -- Assembly (drawing and BOM shorthand).}
{FERM -- Fermentation (the MEOH_FERM unit).}
{HHO -- Hybrid hydrogen-oxygen (a misnomer for stoichiometric H2/O2 gas; not used as a design basis).}
{BPC -- Byproduct chemical, or bypass damper (context-dependent).}
{HFTO -- Hydrogen fuel technology office (US DOE programme name).}
{QY -- Quantum yield: the mol product per photon absorbed in a photochemical process.}
{ALCRM -- An invented label with no established meaning; replaced by plain wording (Q-017).}
{CEPCI -- Chemical Engineering Plant Cost Index: the escalation index for cost estimates.}
{CEB -- Chemically enhanced backwash: the membrane-cleaning method with chemical dosing.}
{ABC -- Activated carbon block, or the ABC fire classification (context-dependent).}
{AHRI -- Air-Conditioning, Heating and Refrigeration Institute: the HVAC equipment rating body.}
{AISI -- American Iron and Steel Institute: the steel grade designation system.}
{AIT -- Auto-ignition temperature.}
{ASRT -- Advanced silicon refinement technology (historical study reference).}
{BEI -- Biomass energy intake, or the biological exposure index (context-dependent).}
{CIAAW -- Commission on Isotopic Abundances and Atomic Weights (IUPAC).}
{DALY -- Disability-adjusted life year: the health-impact metric.}
{DME -- Dimethyl ether: the alternative fuel and propellant.}
{EP -- Extreme pressure (lubricant additive class), or the edit point (context-dependent).}
{EPS -- Expanded polystyrene: the insulation board material.}
{HHV -- Higher heating value: the combustion energy including the latent heat of water condensation.}
{IE -- Inherently safer design, or id est (context-dependent).}
{IIB -- IEC gas group IIB (ethylene class) for explosion-protected equipment.}
{ISBN -- International Standard Book Number.}
{IUPAC -- International Union of Pure and Applied Chemistry.}
{IWA -- International Water Association.}
{LDPE -- Low-density polyethylene.}
{NTP -- Normal temperature and pressure (0 C, 101.325 kPa).}
{NTRS -- NASA Technology Roadmap Series.}
{P&I -- piping and instrumentation (as in P&I diagram, synonymous with P&ID).}
{PD -- Positive displacement (pump or meter class), or the probability of detection.}
{PF -- Power factor, or the polymeric foam (context-dependent).}
{PLOS -- Public Library of Science (journal publisher).}
{PPF -- Photosynthetic photon flux: the photon delivery rate in micromoles per second.}
{REL -- Recommended exposure limit (NIOSH occupational exposure).}
{SRD -- Safety requirements document, or the standard reference diet (context-dependent).}
{STEL -- Short-term exposure limit: the 15-minute occupational exposure ceiling.}
{TC -- Thermocouple, or the thermosyphon circuit (context-dependent).}
{TLV -- Threshold limit value (ACGIH occupational exposure).}
{TWA -- Time-weighted average: the 8-hour occupational exposure average.}
{USC -- United States Code (federal law).}
{VDROP -- Voltage drop across a circuit segment.}
{WMO -- World Meteorological Organization.}
{GHSV -- Gas hourly space velocity: volume of gas per volume of catalyst per hour.}
{GSHP -- Ground-source heat pump.}
{LOC -- Level of concern, or the loss of containment (context-dependent).}
{PM -- Preventive maintenance, or particulate matter (context-dependent).}
{VE -- Value engineering, or the verification event.}
{AOX -- Adsorbable organic halogen: the halogenated-organic discharge metric.}
{APART -- Separate, not adjacent (layout note shorthand).}
{TAR -- The target acceptance range.}
{CCIM -- Cold crucible induction melting.}
{VAR -- Vacuum arc remelting.}
{VIM -- Vacuum induction melting.}
{CONC -- Concentrate or concentrated (stream note shorthand).}
{ECF -- Electrochemical fluoride cell, or elemental chlorine-free (pulp bleaching; context-dependent).}
{SKU -- Stock keeping unit.}
{ALIGN -- The lithography alignment tool (LITHO_ALIGN).}
{DEV -- The lithography developer tool (LITHO_DEV).}
{ATOM -- The gas atomizer (GAS_ATOMIZER).}
{HPDC -- High-pressure die casting.}
{RCOO -- Carboxylate anion (R-COO-).}
{RCOOH -- Carboxylic acid (R-COOH).}
{DERA -- Defense Threat Reduction Agency, or a derated value (context-dependent).}
{KMML -- Korean molybdenum melting limit (historical study reference).}
{MDPI -- Multidisciplinary Digital Publishing Institute (journal publisher).}
{ZNBR -- Zinc-bromide (the ZNBR2 flow battery electrolyte).}
{HRT -- Hydraulic residence time.}
{BIO -- Biological (the biofilter or biological treatment class).}
{HL -- Heat-ladder edge prefix (HL-Q1-A through HL-Q4-REJ).}
{EPR -- Ethylene propylene rubber: the insulation compound for flexible and medium-voltage cable.}
{PCD -- Pitch circle diameter: the bolt-circle dimension of a flange or terminal plate.}
{XLPE -- Cross-linked polyethylene: the insulation compound for power cable.}
{THHN -- Thermoplastic high-heat nylon-coated: the building-wire insulation designation.}
{PLTC -- Power-limited tray cable: the instrumentation and control cable class.}
{CAPEX -- Capital expenditure.}
{EBM -- Electron beam melting (the metal additive-process class).}
{PK -- The peak (maximum instantaneous) value of a rate or duty.}
{BN -- Building block number (the construction block series identifier).}
{NH -- Nutrient hose (the farm irrigation line class), or the ammonia nitrogen species.}
{COND -- Condenser or condensate (context-dependent stream or equipment shorthand).}
{EPR -- Ethylene propylene rubber: the insulation compound for flexible and medium-voltage cable.}
{PCD -- Pitch circle diameter: the bolt-circle dimension of a flange or terminal plate.}
{XLPE -- Cross-linked polyethylene: the insulation compound for power cable.}
{THHN -- Thermoplastic high-heat nylon-coated: the building-wire insulation designation.}
{PLTC -- Power-limited tray cable: the instrumentation and control cable class.}
{CAPEX -- Capital expenditure.}
{EBM -- Electron beam melting (the metal additive-process class).}
{PK -- The peak (maximum instantaneous) value of a rate or duty.}
{BN -- Building block number (the construction block series identifier).}
{NH -- Nutrient hose (the farm irrigation line class), or the ammonia nitrogen species.}
{COND -- Condenser or condensate (context-dependent stream or equipment shorthand).}
{LH -- Light hazard: the NFPA 13 occupant-hazard classification for areas with low combustible loading.}
{LEO -- Low Earth orbit: the 400 km, 51.6 degree orbital regime of the ISS and station-class platforms.}
{HEICT -- Heikt et al., the perchlorate-discovery study for the Phoenix landing site (NASA_MARS_PERCHLORATE).}
{MSL -- Mars Science Laboratory: the Curiosity rover mission that carried the RAD instrument to Gale crater.}
{RAD -- Radiation Assessment Detector: the instrument on MSL that measured the surface dose rate at Gale crater (NASA_MARS_RAD).}
{PSV -- Pressure safety valve. Relief device; set pressure ≤ MAWP on protected vessels (AQS-ASM-001 study tables).}

{UL -- Underwriters Laboratories. Listing theme on inverters and electrical equipment (e.g. Sol-Ark UL 1741 SB).}


## Membrane and support chemistry (cross-refs)

{AEL -- Anion-exchange layer of a BPM. Drawn orange; faces the anode. OH⁻ leaves into BASE.}

{CEL -- Cation-exchange layer of a BPM. Drawn blue; faces the cathode. H⁺ leaves into ACID.}

{SHE -- Standard hydrogen electrode. ORP probe reference basis (SHE-equivalent).}

{PS -- Polystyrene. Co-polymer base in SEM-Tech PS–PVC ion-exchange membranes.}

{THF -- Tetrahydrofuran. Component of Weld-On 724 class CPVC cement.}

{MEK -- Methyl ethyl ketone. Component of Weld-On 724 class CPVC cement.}

{FAQ -- Frequently asked questions; used here for the published OFL FAQ of SIL International.}

{FRP -- Fiber-reinforced plastic. Induced-draft fan and scrubber duct class on HDR_ACID_GAS.}

{HDPE -- High-density polyethylene. Explicitly wrong for hot Salria anolyte walls.}

{ID fan -- Induced-draft fan. Pulls negative on dust or acid-gas headers after filtration/scrub.}

## General abbreviations

Abbreviations of standards bodies, materials, file formats and general engineering terms. Plant-specific terms are in the sections above.

{ACGIH -- American Conference of Governmental Industrial Hygienists, publisher of threshold limit values for workplace exposure.}

{ACH -- Air changes per hour: ventilation airflow divided by room volume.}

{ACI -- American Concrete Institute, publisher of ACI 318 and other concrete design codes.}

{ANSI -- American National Standards Institute.}

{API -- In a standard number (API 650, API 941), the American Petroleum Institute. In the design tool, application programming interface: the HTTP interface of `design_tool/`.}

{ASCE -- American Society of Civil Engineers, publisher of ASCE 7 (minimum design loads).}

{ASCII -- American Standard Code for Information Interchange, the basic text character set.}

{ASHRAE -- American Society of Heating, Refrigerating and Air-Conditioning Engineers.}

{ASM -- ASM International, publisher of the ASM Handbook series on materials.}

{ASTM -- ASTM International, publisher of material and test standards (formerly the American Society for Testing and Materials).}

{ASU -- Air separation unit: equipment that separates air into oxygen, nitrogen and argon.}

{AWG -- American Wire Gauge, the conductor size system used in NFPA 70.}

{AWS -- American Welding Society, publisher of the AWS D1 structural welding codes.}

{AWWA -- American Water Works Association, publisher of water system standards.}

{BLD -- Building. The series code of the building documents (AQS-BLD-nnn) and the short name of the building CAD work in older records.}

{BLDC -- Brushless direct-current motor: a permanent-magnet motor commutated electronically.}

{BPVC -- Boiler and Pressure Vessel Code, published by ASME.}

{CE -- Conformité Européenne: the European conformity marking on products sold in the European Economic Area.}

{CERN -- European Organization for Nuclear Research, author of the CERN Open Hardware Licence used by this repository.}

{CFR -- Code of Federal Regulations (United States); for example 29 CFR 1910 for workplace safety.}

{CMAA -- Crane Manufacturers Association of America, publisher of CMAA 70, the specification for overhead travelling cranes.}

{CNC -- Computer numerical control: machine tools driven by a stored program.}

{CO -- Carbon monoxide.}

{COP -- Coefficient of performance: heat moved by a heat pump or chiller divided by the work put in.}

{CPU -- Central processing unit; in a PLC, the processor module.}

{CS -- Carbon steel.}

{CSV -- Comma-separated values, a plain-text table format.}

{DI -- Deionized (water). In control documents, also digital input: a controller input channel that reads an on-off signal.}

{DLI -- Daily light integral: photosynthetic light received by a crop per day, in mol/(m² d).}

{DN -- Nominal diameter, the metric pipe size designation of ISO 6708 (DN50 is about NPS 2).}

{DSA -- Dimensionally stable anode: a titanium anode coated with mixed metal oxides.}

{DVS -- Deutscher Verband für Schweißen und verwandte Verfahren (German Welding Society), publisher of the DVS 2207 guidelines for welding thermoplastics.}

{EDC -- Ethylene dichloride (1,2-dichloroethane), the intermediate from which vinyl chloride monomer and then polyvinyl chloride are made.}

{EN -- European Norm: a standard adopted by the European standards bodies (for example EN 1090).}

{EOL -- End of life: the point at which an item is retired and its materials returned to the plant.}

{EPA -- Environmental Protection Agency (United States).}

{EPDM -- Ethylene propylene diene monomer rubber.}

{ERV -- Energy recovery ventilator: a ventilation unit that transfers heat and moisture between exhaust and supply air.}

{EU -- European Union.}

{FKM -- Fluoroelastomer (ASTM D1418 class designation), used for seals in hot or chemical service.}

{FT -- Flow transmitter (instrument tag letters, ISA-5.1).}

{GTAW -- Gas tungsten arc welding.}

{HART -- Highway Addressable Remote Transducer: a digital protocol carried on 4 mA to 20 mA instrument loops.}

{HER -- Hydrogen evolution reaction, the cathode reaction of water electrolysis.}

{HETP -- Height equivalent to a theoretical plate, a measure of packed-column efficiency.}

{HF -- Hydrogen fluoride; in water, hydrofluoric acid.}

{HTU -- Height of a transfer unit, used with NTU to size a packed column.}

{HP -- Heat pump. Used in the GEO sector, where the ground-loop heat pump lifts heat to the Q4 store.}

{HX -- Heat exchanger.}

{IC -- In a motor designation (IC 411), the cooling method code of IEC 60034-6. In chemical analysis, ion chromatography.}

{IEC -- International Electrotechnical Commission.}

{IECC -- International Energy Conservation Code.}

{IIA -- Gas group IIA of IEC 60079-20-1, the least easily ignited group of flammable gases (for example methane and propane); North American Group D.}

{IIC -- Gas group IIC of IEC 60079-20-1, the most easily ignited group of flammable gases (hydrogen and acetylene); hydrogen is North American Group B.}

{GNU -- The GNU Project of the Free Software Foundation, publisher of the GNU General Public License and of GNU FreeFont.}

{GPR -- Ground potential rise, the voltage that the earthing grid reaches relative to remote earth during an earth fault.}

{IEEE -- Institute of Electrical and Electronics Engineers.}

{IFC -- International Fire Code.}

{IPA -- Isopropyl alcohol.}

{IR -- Infrared.}

{ISO -- International Organization for Standardization.}

{KO -- Knock-out (drum or pot): a vessel that separates liquid droplets from a gas stream.}

{KOH -- Potassium hydroxide.}

{LED -- Light-emitting diode.}

{LFS -- Large File Storage: the Git extension that stores the CAD files of this repository.}

{LHV -- Lower heating value of a fuel.}

{LMTD -- Log mean temperature difference, used to size heat exchangers.}

{LRFD -- Load and resistance factor design.}

{LSH -- Level switch, high (instrument tag letters, ISA-5.1).}

{MSW -- Municipal solid waste.}

{MV -- Medium voltage.}

{MVR -- Mechanical vapour recompression: evaporation driven by compressing the vapour it produces.}

{NASA -- National Aeronautics and Space Administration (United States).}

{NEMA -- National Electrical Manufacturers Association.}

{NIOSH -- National Institute for Occupational Safety and Health (United States).}

{NOAA -- National Oceanic and Atmospheric Administration (United States).}

{NPS -- Nominal pipe size, the inch-based pipe size designation of ASME B36.10M.}

{NREL -- National Renewable Energy Laboratory (United States).}

{NSRDB -- National Solar Radiation Database, published by NREL.}

{NTU -- Number of transfer units, used with HTU to size a packed column or an exchanger.}

{OD -- Outside diameter.}

{PBT -- Polybutylene terephthalate.}

{PCB -- Printed circuit board.}

{PDF -- Portable Document Format.}

{PECVD -- Plasma-enhanced chemical vapour deposition.}

{PFA -- Perfluoroalkoxy alkane, a melt-processable fluoropolymer.}

{PIR -- Polyisocyanurate (rigid foam insulation).}

{PLC -- Programmable logic controller.}

{PSA -- Pressure swing adsorption.}

{PSH -- Pressure switch, high (instrument tag letters, ISA-5.1).}

{PSM -- Process safety management, the OSHA rule 29 CFR 1910.119.}

{PT -- Pressure transmitter (instrument tag letters, ISA-5.1).}

{PTFE -- Polytetrafluoroethylene.}

{PVC -- Polyvinyl chloride.}

{QF -- Prefix of the paragraphs of ASME BPVC Section IX that cover the fusing of plastic pipe (for example QF-200, QF-300).}

{QW -- Prefix of the paragraphs of ASME BPVC Section IX that cover welding (for example QW-300, QW-451).}

{QA -- Quality assurance.}

{RF -- Radio frequency.}

{RTD -- Resistance temperature detector, such as a Pt100 element to IEC 60751.}

{SDR -- Standard dimension ratio: pipe outside diameter divided by wall thickness.}

{SDS -- Safety data sheet.}

{SI -- International System of Units.}

{SPOF -- Single point of failure: a part whose failure alone stops a system. The redundancy audit AQS-RED-001 lists them.}

{SMAW -- Shielded metal arc welding.}

{SS -- Stainless steel.}

{STL -- Stereolithography file format: a triangulated surface, used here for unit envelopes and printable parts.}

{SVG -- Scalable Vector Graphics, the drawing format of the generated diagrams.}

{TE -- Temperature element (instrument tag letters, ISA-5.1).}

{TFC -- Thin-film composite (membrane).}

{TFE -- Tetrafluoroethylene, the monomer of PTFE.}

{TMY -- Typical meteorological year: a year of hourly weather data used for energy simulation.}

{TSA -- Temperature swing adsorption.}

{US, USA -- United States.}

{VDF -- Vinylidene fluoride, the monomer of PVDF.}

{VPI -- Vacuum pressure impregnation of motor windings with resin.}

{DIY -- Do it yourself: built by the plant builders from published instructions rather than bought.}

{EAOP -- Electrochemical advanced oxidation process: oxidation of organic matter at an electrode, used here as a low-voltage pretreatment of woody waste.}

{HTTP -- Hypertext Transfer Protocol, used by the design tool's interface.}

{IET -- The Institution of Engineering and Technology (United Kingdom), publisher of the guide to technical report writing cited in DOC_STYLE.md.}

{KSC -- Kennedy Space Center (NASA), publisher of the KSC-DF-107 documentation style guide cited in DOC_STYLE.md.}

{URL -- Uniform resource locator: a web address.}

{BPE -- Boiling point elevation: the rise in boiling point of a solution over that of the pure solvent.}

{CA -- Corrosion allowance: extra wall thickness added to a pressure design for metal lost in service.}

{CMP -- Chemical-mechanical planarization: polishing a wafer flat with an abrasive slurry.}

{CW -- Cooling water.}

{DFW -- Dallas/Fort Worth: the NOAA weather station whose degree-day data are used for heating and cooling.}

{DIN -- Deutsches Institut für Normung, the German standards body.}

{DOT -- The graph description language of Graphviz, one of the published diagram formats.}

{DR -- Dimension ratio of a plastic pipe: outside diameter divided by wall thickness (ASTM D3035).}

{EC -- Electronically commutated, as in "EC motor" or "EC fan motor": a permanent-magnet motor with built-in electronics that commutate it and set its speed. Used here only for the heat-pump condenser fans (AQS-INV-001; A-M-332). The IEC 60034-30-1 efficiency classes (IE1 to IE4) do not apply to EC motors. Not used in this project as an abbreviation for electrical conductivity, which is always written out.}

{EGC -- Equipment grounding conductor (NFPA 70).}

{FLC -- Full-load current of a motor (NFPA 70 article 430).}

{GF -- Georg Fischer, a maker of plastic valves and fittings.}

{ISM -- Induction skull melting: melting in a water-cooled segmented copper crucible, in which a solid skin of the charge protects the melt from the crucible.}

{KI -- Potassium iodide.}

{MAU -- Makeup air unit: conditions the outdoor air that replaces exhaust.}

{MSS -- Manufacturers Standardization Society of the Valve and Fittings Industry, publisher of MSS SP-58 for pipe supports.}

{MVC -- Mechanical vapour compression: evaporation driven by compressing the vapour produced.}

{NMN -- Nomex-Mylar-Nomex: a laminated slot liner for motor windings.}

{PCC -- Point of common coupling: the point where the plant connects to the utility grid, with the lockable utility disconnect (NEC 705.20), overcurrent protection (NEC 705.30) and the bidirectional revenue meter. Interconnection and anti-islanding requirements apply here (NEC 705.40; IEEE 1547-2018).}

{PFRP -- Process to further reduce pathogens: the class A sludge treatment of 40 CFR 503.}

{POE -- Polyolester: a synthetic refrigeration compressor oil.}

{PSG -- Phosphosilicate glass: the phosphorus-doped oxide left on a solar cell after diffusion and removed by etching.}

{PSU -- Power supply unit.}

{SCR -- Silicon-controlled rectifier (thyristor), used for heater power control.}

{SD -- Hydrostatic design stress of a polyethylene tank wall (ASTM D1998).}

{SFP -- Specific fan power: fan electrical power per unit airflow (ISO 16798-3).}

{SRT -- Solids retention time: the mean time solids stay in a digester or reactor.}

{TDS -- Total dissolved solids.}

{TFFN -- A fixture wire type of NFPA 70: thermoplastic insulation with a nylon jacket.}

{TMAH -- Tetramethylammonium hydroxide, a photoresist developer.}

{TS -- Total solids: the dry mass fraction of a sludge or slurry.}

{USBM -- United States Bureau of Mines.}

{VLE -- Vapour-liquid equilibrium.}

{WCB -- A cast carbon steel grade for valve bodies (ASTM A216 Grade WCB).}

{RMIT -- RMIT University, Melbourne (formerly the Royal Melbourne Institute of Technology).}

{GMAW -- Gas metal arc welding.}

{GOX -- Gaseous oxygen.}

{LIN -- Liquid nitrogen.}

{LOX -- Liquid oxygen.}

{NDE -- Nondestructive examination (ASME B31.3 chapter VI; ASME BPVC Section V).}

{PED -- Pressure Equipment Directive: Directive 2014/68/EU of the European Parliament and of the Council on the making available on the market of pressure equipment. Cited where EU conformity is compared with ASME practice.}

{PWHT -- Postweld heat treatment.}

{RT -- Radiographic testing of welds.}

{SCC -- Stress corrosion cracking.}

{VJ -- Vacuum-jacketed (cryogenic pipe with an evacuated outer jacket).}

{BIPV -- Building-integrated photovoltaics: PV modules that form part of the facade or roof.}

{CZ -- Czochralski: the crystal-growth method that pulls a single-crystal silicon ingot from a melt; a CZ puller is the machine that does it (wafer fab).}

{NP -- Not permitted (IBC tables).}

{NS -- Non-sprinklered (IBC tables).}

{CH -- Fat clay (high-plasticity clay), a group of the Unified Soil Classification System (ASTM D2487).}

{CL -- Lean clay (low-plasticity clay), a group of the Unified Soil Classification System (ASTM D2487).}

{MH -- Elastic silt (high-plasticity silt), a group of the Unified Soil Classification System (ASTM D2487).}

{ML -- Silt (low-plasticity silt), a group of the Unified Soil Classification System (ASTM D2487).}

{MCWB -- Mean coincident wet bulb: the average wet-bulb temperature that occurs with the cooling design dry-bulb temperature (ASHRAE Handbook—Fundamentals, climatic design conditions).}

{ABA -- Architectural Barriers Act of 1968 (US): accessibility standards for federally funded facilities.}

{ADA -- Americans with Disabilities Act of 1990 (US): accessibility requirements, with the 2010 ADA Standards for Accessible Design.}

{CWA -- Clean Water Act (US federal water pollution control law, 33 U.S.C. 1251 and following).}

{EPO -- Emergency power-off: a manually operated control that disconnects an energy storage system or equipment (NFPA 855; NEC Article 706).}

{GFCI -- Ground-fault circuit interrupter (NEC 210.8): a device that opens a circuit when current leaks to ground.}

{IPC -- International Plumbing Code (International Code Council).}

{UPC -- Uniform Plumbing Code (IAPMO).}

{UFC -- Uniform Fire Code, the former name of NFPA 1 Fire Code.}

{RMP -- Risk management program: the EPA chemical accident prevention rule, 40 CFR Part 68.}

{PL -- Protection level: the NFPA 400 hazard category equivalent to an IBC high-hazard (H) occupancy group.}

{XP -- Explosion-proof: an enclosure that contains an internal explosion without igniting the surrounding atmosphere (NEC 500.2).}

{FE -- Faradaic efficiency: the share of the charge passed that drives the intended electrode reaction; the same quantity as current efficiency (CE).}

{MPPT -- Maximum power point tracker: the inverter input stage that holds a PV string at the voltage giving the most power.}

{STC -- Standard test conditions for PV modules: 1000 W/m² irradiance, 25 °C cell temperature, air mass 1.5 (IEC 61215).}

{SB -- Supplement SB of UL 1741: the grid-support test requirements that demonstrate conformance with IEEE 1547-2018 (via IEEE 1547.1-2020).}

{TBM -- Tunnel boring machine; in this project, one used to excavate a landfill for feed.}

{OCPD -- Overcurrent protective device: a breaker or fuse that opens a circuit on overload or short circuit (NEC Article 240).}

{NMP -- N-methyl-2-pyrrolidone, a polar solvent used in photoresist stripping}




{AGPL -- GNU Affero General Public License, a copyleft software licence whose terms also cover use over a network}

{ISA -- International Society of Automation; ISA-95 is its standard for the levels of an enterprise and control system hierarchy}

{LOD -- Level of detail: simplified versions of a 3D model shown at a distance}

{LEV -- Local exhaust ventilation: extraction that captures a contaminant at its source, such as a hood}

{DAC -- Direct air capture: removing carbon dioxide from ambient air}

{EFOY -- Product name of the direct methanol fuel cells made by SFC Energy AG}

{SFC -- SFC Energy AG, the maker of the EFOY fuel cells (a company name)}

{GT -- Part of the model name AMETEK Sunpower CryoTel GT, a Stirling cryocooler}

{ESP -- Emergency standby power: a generator rating for supply during an outage of the normal source (ISO 8528-1)}

{PRP -- Prime power: a generator rating for unlimited hours a year at variable load (ISO 8528-1)}

{MTPA -- Metric tonnes per annum}

{NETL -- National Energy Technology Laboratory, a United States Department of Energy laboratory}

{LOPA -- Layer of protection analysis: a semi-quantitative method that checks whether the independent safeguards against a hazard are enough (IEC 61511-3)}

{QMS -- Quality management system, for example one certified to ISO 9001}

{OEM -- Original equipment manufacturer}

{HVDC -- High-voltage direct current}

{LVDC -- Low-voltage direct current}

{SP -- Static pressure, the pressure drop a fan must overcome}

{MTO -- Material take-off: the list of parts and quantities taken from the drawings for purchase}

{NPT -- American National Standard taper pipe thread (ASME B1.20.1)}

{TU -- True union: a valve end connection that can be undone without turning the pipe, as in the Spears TU 2000 valve}

{TT -- Temperature transmitter (instrument tag)}

{EI -- Electrical indicator (instrument tag); here the motor or stack power and voltage readings}

{SR -- Speed recorder (instrument tag)}

{CT -- Conductivity transmitter (instrument tag)}

{DMM -- Digital multimeter}

{LMH -- Litres per square metre per hour, the unit of membrane flux}

{RCD -- Residual-current device, which disconnects a circuit on earth leakage}

{RH -- Relative humidity, the water vapour in air as a percentage of saturation at the same temperature}

{ASR -- Area-specific resistance, the cell resistance per unit electrode area, in ohm cm2}

{HMI -- Human-machine interface, the operator screens of the control system}

{PPFD -- Photosynthetic photon flux density, the plant-usable light reaching a surface, in umol per m2 per s}

{FBR -- Fluidized-bed reactor; here, the granular polysilicon process that is an alternate silicon feedstock}

{RCA -- RCA clean, the standard two-step wet clean for silicon wafers, named for the company that developed it}

{RTA -- Rapid thermal anneal, a short high-temperature wafer heat treatment}

{DOSIS -- Dose Distribution within the ISS, a radiation measurement experiment in the Columbus laboratory of the International Space Station.}

{ECSS -- European Cooperation for Space Standardization, publisher of the European space engineering standards.}

{ESA -- European Space Agency.}

{IAPWS -- International Association for the Properties of Water and Steam.}

{ISRU -- In-situ resource utilization: making supplies from materials found at the site.}

{ISS -- International Space Station.}

{MAE -- Materials Adherence Experiment, the dust-settling instrument on Mars Pathfinder.}

{MOXIE -- Mars Oxygen ISRU Experiment, the solid oxide electrolysis demonstration on the Perseverance rover.}

{NCEI -- National Centers for Environmental Information (United States, part of NOAA).}

{NID -- NASA Interim Directive.}

{SAM -- Sample Analysis at Mars, the gas analysis instrument suite on the Curiosity rover.}

{SMAD -- Space Mission Analysis and Design, the space systems engineering reference series.}

{USAP -- United States Antarctic Program.}

{DNV -- Det Norske Veritas, a classification society that publishes offshore standards and recommended practices.}

{ISPS -- International Ship and Port Facility Security Code of the International Maritime Organization.}

{MARPOL -- International Convention for the Prevention of Pollution from Ships.}

{MODU -- Mobile offshore drilling unit; the IMO MODU Code sets construction and equipment rules for such units.}

{OTEC -- Ocean thermal energy conversion: power from the temperature difference between warm surface and cold deep seawater.}

{SOLAS -- International Convention for the Safety of Life at Sea.}

{TW -- Terawatt, 10^12 W.}
{BIPM -- Bureau International des Poids et Mesures (International Bureau of Weights and Measures).}
{CGPM -- Conférence générale des poids et mesures (General Conference on Weights and Measures).}
{USAF -- United States Air Force.}

## Legal

{CERN-OHL-S-2.0 -- Strongly reciprocal CERN Open Hardware Licence v2. Licence on this design source and on S.E.M core technology.}

{Convey / Source / Product -- CERN-OHL terms. Source is the design (scripts, params, drawings). Product is hardware built from it. Conveying a Product requires conveying the corresponding Source.}
