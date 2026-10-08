# Glossary

Locked names are in SMALL CAPS as they appear on the drawings. Do not invent synonyms.

Each entry is `{term -- definition}`. Acronyms used in the plant flow graph, design-tool UI, PFDs/MFD/EFD layers, sector taxonomy, and authority docs are listed here with expansion and plant role. No invented rates or nameplates.

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

{Leach / Salria -- Oxidative chloride leach: HCl + NaClO₃, 70–85 °C, ORP > 1.5 V, pH ≈ 0. Dissolves metals. Doubles as the float–sink medium.}

{MMO -- Mixed-metal oxide anode coating, IrO₂–Ta₂O₅ on Ti Grade 2. The coating is the chemical barrier. The titanium substrate is not a tank wall.}

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

{S89 -- HDR_CO2 → GROW_BED, 11.616 kg/d CO₂ enrichment dose through the FARM AHU, 3.0 bar a, DN15 316L. Only consumer of HDR_CO2. CO₂ only: no tee to HDR_O2, hab air, the HAB return or the dock. AQS-DUTY-009.}

{CO₂ enrichment -- Farm air held at 1000 ppm in the 16 h photoperiod. GROW_BED fixes S04 (1.109 kg/d); the S89 carbon leaves with farm exhaust air. Use, not sequestration.}

{CO2-rich cut -- S67B. FLUE_KO VSA product, ≥ 90 mol % CO2, dry. N2, O2, and NOx are rejected at FLUE_KO. Not raw flue. The only CRYO_CO2 credit for afterburner carbon; S18 carries none since Rev J.}

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

{CAD -- Computer-aided design. FreeCAD solids, campus placement, and parametric envelopes under AGENT_CAD_PROTOCOL / FREECAD_PROTOCOL. Topology authority remains the typed plant flow graph.}

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

{WET -- Process sector: L-1 leach / EW / BMED / CRU / polish wet line. Primary mass recycle.}

{OIL -- Process sector: dryer → pyro → fractionator hydrocarbon cuts; afterburner flue to CRYO.}

{GLASS -- Process sector: rinse → burnout → mill → NaOH digest; silicate / ceramic products.}

{GAS -- Process sector: scrub / demister / baghouse / stacks; acid-gas and dust returns. Secondary utility/header role for HDR_*.}

{FAB -- Process sector: wafer fab, UPW, wet-bench reagents, solar-cell stub. Goods surplus path.}

{MFG -- Process sector: shop, polymer line, metal forming (MET folded under MFG). Goods surplus path.}

{NUT -- Process sector: nutrient dose (P-Al/Mg/Ca and BMED salts → farm). Distinct from REMIN potable dose.}

{FARM -- Life-support sector: grow beds / aquaculture / LED; food surplus. CAD name FARM (alias FRM).}

{HAB -- Life-support sector: habitation, galley, sleep, grey/black return; crew load driver.}

{CRYO -- Utility sector: cold box and O₂/N₂/CO₂/H₂ receivers; H₂ normal path S64. Alias CRY.}

{WTR -- Utility sector: roof/catch tanks, VCD / REMIN / UPW polish, grey treat (AQS-WTR-001).}

{TRR -- Utility sector: terrace overflow / irrigation; optional greenhouse envelopes. Not required for loop closure.}

{ELEC -- Utility sector: Sol-Ark / ATS / RECT / MCC distribution hub. Distinct from ELEC_PV.}

{ELEC_PV -- Energy Production (Electrical): PV array / roof array generation.}

{GEO -- Utility sector (study): ground heat exchanger and heat pump to Q4; optional GEO_ORC electric stub.}

{DOCK -- Export / dock sector: north dock and freight elevators for surplus goods export.}

{MET -- Metal forming capability folded under MFG (not a separate sector_id).}

{CORE -- Building distribution (cores, shafts, stairs). Not a mass–energy sector toggle.}

## Water and life support

{UPW -- Ultrapure water. Plant HDR_UPW / S01 class (< 1 µS/cm post-ED polish); fab further polishes to S27. Pre-remin water serves farm/fab; drinking uses REMIN.}

{VCD -- Vapor-compression distillation. Regenerates clean distillate from condensate and treated grey (VCD_HX → EVAP → COMP → COND). Kept from SLINGSHOT into the building stack; study stub rates may be null.}

{REMIN -- Remineralization. Doses Ca²⁺ / Mg²⁺ / K⁺ (and related) from core salt inventory into drinking water (S26). For potable only — not farm nutrient dose S07.}

{ED -- Electrodialysis. Hab/UPW polish stage (HAB_ED_POLISH / UPW POLISH) toward S01 conductivity claim; BMED middle chamber may assist, not as a second wet-line stack.}

{EDI -- Electrodeionization. Optional fab UPW polish peer to mixed-bed IX on FAB_UPW_IX.}

{IX -- Ion exchange. Mixed-bed polish on the fab UPW train.}

{UF -- Ultrafiltration. Particulate / colloidal barrier on FAB_UPW_UF.}

{NF -- Nanofiltration. Potable integrity check class after remin (with UF/UV).}

{UV -- Ultraviolet disinfection / TOC destruction on potable finish and fab UPW.}

{TOC -- Total organic carbon. Fab rinse target class on UPW.}

{MED -- Membrane electrodialysis (grey stage GREY_MED). Root-07 multi-effect distillation narrative is adapted; VCD remains primary distillate regenerator.}

{RPZ -- Reduced-pressure-zone backflow preventer. Required theme on HDR_UPW at potable taps.}

{HEPA -- High-efficiency particulate air filtration. Life / clean-space filtration theme (TEXTILES_HEPA and related).}

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

{DMFC -- Direct methanol fuel cell. MeOH discharge path; IEM-based preferred over conventional packaging. Distinct from PEM H₂ FC.}

{IEM -- Ion-exchange membrane. Generic SEM-Tech membrane family (CEM/AEM style) used on EW, BMED, ZnBr₂, and MeOH FC paths.}

{FC -- Fuel cell. Sector FUEL_CELL (PEM) or MEOH_FC discharge; electrical offtake to BATT DC, not GEN.}

{PV -- Photovoltaic. Roof/yard array generation (ELEC_PV).}

{ATS -- Automatic transfer switch. Selects utility vs Sol-Ark LOAD for plant main; service bypass path.}

{MCC -- Motor control center. Plant AC distribution after ATS.}

{RECT -- Rectifier skid. Process DC for EW / BMED / polish (RECT-EW, RECT-BMED, RECT-PK).}

{DC -- Direct current. BATT bus, rectifiers, FC/MeOH DCDC offtakes.}

{AC -- Alternating current. Utility, Sol-Ark LOAD/GEN, MCC, ORC couple stubs.}

{GEN -- Sol-Ark generator AC port. BACKUP_GEN (H₂ genset) only — not FC or RECT hard-tee.}

{BATT -- Sol-Ark battery DC window. ZnBr₂ and fuel-cell DCDC peers land here.}

{HSE -- Health, safety, and environment. Hazard separation and fire-area authority (AQS-HSE-001).}

## Compliance and codes

{AHJ -- Authority Having Jurisdiction. Local building/fire official whose edition and amendments govern permits; design docs are not a PE stamp.}

{MAQ -- Maximum Allowable Quantity. Code inventory cap for hazardous materials (oxidizers, H₂, flammables) before occupancy upgrade.}

{MAWP -- Maximum Allowable Working Pressure. Vessel/piping design pressure; relief set ≤ MAWP (study values in AQS-ASM-001 until PE/AHJ).}

{PE -- Professional Engineer. Stamp/permit role; architecture docs state Compliant-intent or study until PE confirmation.}

{NFPA -- National Fire Protection Association. Fire/H₂/ESS/oxidizer themes (e.g. NFPA 2, 13, 30, 55, 400, 855).}

{NEC -- National Electrical Code. Service, disconnect, and working-space themes.}

{ASME -- American Society of Mechanical Engineers. Vessel and B31.3 piping class sheets (AQS-ASM-001).}

{IBC -- International Building Code. Occupancy and construction overlays with NFPA/HSE.}

{OSHA -- Occupational Safety and Health Administration. Egress, LOTO, and workplace themes.}

{LOTO -- Lockout/tagout. Energy isolation for rectifiers, shredder, pyro, melt, Sol-Ark.}

{WEEE -- Waste electrical and electronic equipment. Primary wet-line feed class for RECT-EW sizing theme.}

{SPDX -- Software Package Data Exchange. Licence identifier convention (CERN-OHL-S-2.0).}

{OSE -- Open Source Ecology. Upstream GVCS / Civilization Starter Kit reference map (AQS-REF-CSK-001); not bundled into the tree.}

{CSK -- Civilization Starter Kit. OSE documentation set for a subset of GVCS machines.}

{GVCS -- Global Village Construction Set. OSE catalogue of industrial machines mapped as coverage/study/candidate against Aqueous sectors.}


{M1 -- Module / plant baseline at SCALE_M = 1.0. Layout and study duties reference M1; do not copy legacy campus kW claims onto M1 without evidence.}

{BMS -- Battery management system. ZnBr₂ / ESS charge–discharge inhibit and Sol-Ark gateway theme.}

{SOC -- State of charge. ESS energy state from amp-hours and chemistry indicators (e.g. ORP on ZnBr₂).}

{LEL -- Lower explosive limit. H₂ headspace trip theme on zinc-tank / H₂ headers.}

{LFL -- Lower flammable limit. NFPA 69 explosion-prevention theme (H₂ < 25% LFL class).}

{PSV -- Pressure safety valve. Relief device; set pressure ≤ MAWP on protected vessels (AQS-ASM-001 study tables).}

{UL -- Underwriters Laboratories. Listing theme on inverters and electrical equipment (e.g. Sol-Ark UL 1741 SB).}


## Membrane and support chemistry (cross-refs)

{AEL -- Anion-exchange layer of a BPM. Drawn orange; faces the anode. OH⁻ leaves into BASE.}

{CEL -- Cation-exchange layer of a BPM. Drawn blue; faces the cathode. H⁺ leaves into ACID.}

{SHE -- Standard hydrogen electrode. ORP probe reference basis (SHE-equivalent).}

{PS -- Polystyrene. Co-polymer base in SEM-Tech PS–PVC ion-exchange membranes.}

{THF -- Tetrahydrofuran. Component of Weld-On 724 class CPVC cement.}

{MEK -- Methyl ethyl ketone. Component of Weld-On 724 class CPVC cement.}

{FRP -- Fiber-reinforced plastic. Induced-draft fan and scrubber duct class on HDR_ACID_GAS.}

{HDPE -- High-density polyethylene. Explicitly wrong for hot Salria anolyte walls.}

{ID fan -- Induced-draft fan. Pulls negative on dust or acid-gas headers after filtration/scrub.}

## Legal

{CERN-OHL-S-2.0 -- Strongly reciprocal CERN Open Hardware Licence v2. Licence on this design source and on S.E.M core technology.}

{Convey / Source / Product -- CERN-OHL terms. Source is the design (scripts, params, drawings). Product is hardware built from it. Conveying a Product requires conveying the corresponding Source.}
