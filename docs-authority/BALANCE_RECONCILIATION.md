# Mass balance reconciliation

Document number: AQS-PAR-003
Revision: E
Date: 2026-10-25

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. | 2026-10-15 |
| B | Owner: no fudge. X-SAF-10 imbalance (IA-TERR-VAP / IA-O2-RET, 2.824 kg/d) traced and fixed by transfer functions T1-T5; reconciled moves within measurement tolerance. | 2026-10-15 |
| C | X-PAR-11 T6: grow-bed photosynthetic O2 on S87; leach dissolved gas under the Henry bound; CO2 edges carry CO2. | 2026-10-15 |
| D | Owner ruling D-DOCK 2026-10-19: NORTH_DOCK is the inter-plant trade boundary (closure-exempt; ledger reported as a trade statement, section 1a). The three real closures: AFTERBURNER flue = burner mass balance on the restored combustion-air path; NOX_SCRUB gas outlet by difference to the cold box (BH routing, D-AIR) with the cold-box N2 surplus exported at the dock; CRYO_H2 closed by sizing the electrolyser to the pool draws net of the EW Faraday cathode credit (H2 side governs, A-M-272). R10c closes the remaining reported residuals on their stated bases (A-M-274). Product buffer stores added for food / metal / plant air (A-M-270). Test trio green. | 2026-10-19 |
| E | Rewritten to the documentation style guide (AQS-DOC-002): purpose and scope first, revision record in order, table titles. No method, rate or result changed. | 2026-10-25 |

## 1. Purpose and scope

This page records how the plant mass balance is reconciled. The method is minimum weighted least squares on the held study rates (NARASIMHAN2000); transfer-function and stoichiometric edges stay at their set rates. The generator is `flow_graph/param/balance.py`; authority AQS-PLAN-007 X-PAR-02. It runs in every full regeneration and the reconciliation gate fails on a move outside measurement tolerance.

## 2. Root cause and physics fix

X-SAF-10 corrected the peroxide cell feed from 3.0 kg/d O2 to 0.176 kg/d O2 (Faraday) plus 2.824 kg/d make-up water from ROOF_TANK, and took that water off S40. It did not propagate: TERRACE_IRRIG still transpired 40 kg/d on 37.176 kg/d irrigation, and the cold box still made 2.824 kg/d O2 that nothing drew. Revision A reconciled the two by least squares (IA-TERR-VAP -2.824, IA-O2-RET +2.824) and smeared small moves over 361 edges. Hypothesis tested: missing photosynthetic O2 from the terrace. Rejected for this cut: the terrace has no CO2 supply and no harvest edge, so net CO2 + H2O -> CH2O + O2 fixation there is zero (TAIZ2015), and the sign is wrong (the terrace was short water, the header long O2). Fix: Revision A moves withdrawn; T1-T5 in balance.physics. X-PAR-11 (T6): GROW_BED fixes the 19.0 kg/d CO2 dosed to it (S04 + S89); its photosynthetic O2, 32/44 x CO2 at PQ 1.0, leaves on S87 to CRYO_O2 instead of the trim lump; the trim, compost and nutrient surplus pass the difference; the cold box extracts that much less O2 and the leach dissolved-gas edge falls with it, now asserted under the Henry-law bound (SANDER2015). CO2 edges carry CO2 composition. Verification: T-PAR-02 (A-M-123).

Mass edges 435; held by a transfer function or stoichiometry 406; reconciled 29. Units 152.
Before: 4 units out of balance (sum of residuals 0.002 kg/d). After: max unit residual 7.18e-04 kg/d. Negative rates after reconciliation: 0.

## 3. Units out of balance before reconciliation

Boundary meters are exempt from unit closure: RELIEF_H2 / RELIEF_CRYO / BOUNDARY_EXPORT (relief and export meters) and, since owner ruling D-DOCK (2026-10-19), NORTH_DOCK (the inter-plant trade boundary — its ledger is the trade statement in section 3a).

Table 3.1. Unit residual before reconciliation

| Unit | In - out, kg/d |
| --- | --- |
| BLOW_MOLD | -0.0004 |
| COLD_MILL | -0.0007 |
| VCD_TRAIN | -0.0004 |
| ZNBR2 | -0.0004 |

## 1a. Dock trade statement (owner ruling D-DOCK, 2026-10-19)

NORTH_DOCK is the inter-plant trade boundary, not a balance-constrained sector: imports of arbitrary feedstock (landfill reclaim, mining waste, lunar regolith class) and exports of surplus products to other plants. Its ledger is reported here and on the node (`params.trade_statement`); the unit is exempt from the closure test with the other boundary meters.

| Direction | Edge | Commodity | kg/d |
| --- | --- | --- | --- |
| export | IA-BURNOUT-VENT | dewax/burnout off-gas (burned wax + stea | 0.2 |
| export | IA-C11-SHIP | C11-C18 surplus shipped | 1.512 |
| export | IA-C19-SHIP | C19-C28 surplus shipped | 2.218 |
| export | IA-C5-SHIP | C5-C10 product shipped | 7.131 |
| export | IA-CA-CL2-SHIP | chlorine byproduct export (water-treatme | 0.097 |
| export | IA-CL2-SHIP | chlorine byproduct export (water-treatme | 39.419 |
| export | IA-CR-VENT | chlorinator CO (fuel-gas class export) | 0.202 |
| export | IA-GYPSUM-SHIP | fluorgypsum (anhydrite) cake byproduct | 0.576 |
| export | IA-KROLL-CO | chlorinator CO (fuel-gas class export) | 0.585 |
| export | IA-MEOH-SHIP | methanol shipped at the dock | 28.029 |
| export | IA-METAL-SHIP | surplus foundry metal export (pot-line p | 10.812 |
| export | IA-MO-VENT | chlorinator CO2 (vent class) | 0.043 |
| export | IA-N2-VENT | nitrogen vent | 3.1 |
| export | IA-NA-PURGE | sodium salt purge equal to the make-up m | 4.394 |
| export | IA-O2-SHIP | O2 cylinders shipped at the dock | 22.884 |
| export | IA-SHELL-EXPORT | spent foundry silica (solids return clas | 1.0 |
| import | IA-ALCL3-MU | anhydrous AlCl3 feed (mining-waste chlor | 49.419 |
| import | IA-C-CR | carbon reductant (petcoke/char class) | 0.087 |
| import | IA-C-MO | carbon reductant (petcoke/char class) | 0.012 |
| import | IA-C-TI | carbon reductant (petcoke/char class) | 0.251 |
| import | IA-CACL2-MU | CaCl2 brine concentrate (mining-waste cl | 0.152 |
| import | IA-CAF2-MU | fluorspar make-up, acid-spar class >= 97 | 0.326 |
| import | IA-CR2O3-MU | Cr2O3-equivalent chromite concentrate (d | 0.365 |
| import | IA-H2O-MU | water make-up for H and O leaving as pro | 64.413 |
| import | IA-H2SO4-MU | 98 wt% sulfuric acid make-up | 0.404 |
| import | IA-MGCL2-MU | CaCl2-MgCl2 brine concentrate (mining-wa | 0.04 |
| import | IA-MOO3-MU | MoO3-equivalent concentrate (dock import | 0.094 |
| import | IA-NAOH-MU | purchased NaOH flake make-up | 4.394 |
| import | IA-SILICA-MU | foundry silica (flour/stucco/binder make | 1.0 |
| import | IA-SOLV-MU | solvent resupply (ethanol and acetone) | 0.21 |
| import | IA-TIO2-MU | TiO2-equivalent rutile concentrate (dock | 0.834 |
| import | IA-WAX-MU | pattern wax make-up (petro-wax class imp | 0.2 |

**Net trade: +0.001 kg/d** (exports 122.202 - imports 122.201); dock ledger residual +0.002 kg/d (reported, exempt per D-DOCK).

## 4. Moves outside measurement tolerance (2 % of the rate, 1 g/d floor); must be empty

Table 4.1. Reconciled moves outside tolerance

| Edge | From | To | Held study rate | Reconciled | Change |
| --- | --- | --- | --- | --- | --- |

## 5. All reconciled changes above 0.1 g/d

Table 5.1. Reconciled changes

| Edge | Held | Reconciled | Change, % |
| --- | --- | --- | --- |

## 6. Held stoichiometric edges

Table 6.1. Stoichiometric edges

| Edge | Basis |
| --- | --- |
| S49 | H2 to the fuel cell (load) |
| S50 | O2 = 8 x H2 by mass |
| S02 | crew O2 0.84 kg/p.d |
| IA-FC-AIR | MEOH_FC oxidant |
| IA-AC-O2 | acetic acid oxidation |
| IA-O2-NIT | nitric acid |
| IA-GLX-O2 | net one O2 per acetaldehyde via NO recycle (X-PAR-13) |
| IA-FORM-O2 | one O2 per methanol at 10/10 mol% (X-SAF-11) |
| IA-FORM-N2 | FORM N2 diluent |
| IA-FORM-TAIL | FORM tail gas |
| IA-AB-AIR | afterburner dilution air less FORM N2 |
| IA-H2O2-SRC | Faraday at the cell current |
| S14 | crew food |
| S21 | crew water |
| IA-WASH | wash water |

## 5. Transfer functions for the study edges (closure layer complete)

29 study edges: 25 closure transfer functions (rate = balance of the named unit, solved in elimination order) and 4 design inputs (independent rates with their stated basis; each is replaced when its unit sizing task issues a calculation). Re-derivation of every closure from the inputs reproduces the graph to 8.3e-12 kg/d.

| Edge | Role | Closes unit | Rate kg/d | Basis |
| --- | --- | --- | --- | --- |
| CRU_TO_VDF | closure | CRU | 0.3322 | Cl2 to VDF: 2 Cl2 per VDF from the CRU chlorate finish on the returned dilute HCl (halogen |
| FILM_TO_STOCK | closure | FILM_CAST | 0.1400 | PVDF cast film/sheet to stock (A-M-289). |
| F_RECOVER_TO_HF_GEN | closure | F_RECOVER | 1.5200 | Fluoride concentrate to the kiln = leach fluoride 1.500 (IA-HF-SRC) + POLY_F off-spec recl |
| HF_GEN_TO_VDF | closure | HF_GEN | 0.0937 | Aqueous HF to VDF: 0.15 kg/d VDF x 2 HF/VDF (2 CH3OH + 2 Cl2 + 2 HF -> CH2=CF2 + 4 HCl + 2 |
| IA-COAT-OUT | closure | ELECTRODE_COAT | 0.0200 | Coated anode back to EW-1. Net zero. |
| IA-CRU-01 | closure | LEACH_CSTR_1 | 27.5100 | CRU liquor re-solved on the unit balance: S66 27.3720 + dilute HCl returns 0.7537 - Cl2 dr |
| IA-EW-SHEET | closure | EW_9 | 13.9889 | AQS-DUTY-019. No vent. Goods and gases return. |
| IA-LITHO-CARRY | closure | LITHO_COAT | 0.9875 | Resist/solvent carry coat -> develop at the fab issue rate (the coated wafers ride the too |
| IA-MILL-LOSS | closure | GLASS_MILL | 6.8200 | AQS-DUTY-012 Rev N. Missing product or return, sized to the neighbor. |
| IA-OIL-03 | closure | NCG_HEADER | 5.0000 | AQS-DUTY-010: NCG C1-C4 = DUTY-008 afterburner fuel (CO2 15.0 / 3.002) |
| IA-WIRE-LOSS | closure | WIRE_DRAW | 0.4400 | AQS-DUTY-012 Rev N. |
| NCG_TO_AB | closure | AFTERBURNER | 5.0000 | AQS-DUTY-010: = IA-OIL-03 (header pass-through) |
| POLYF_TO_POWDER | closure | POWDER_RESIN | 0.0900 | PTFE resin to the powder line: 0.10 kg/d TFE -> 0.09 kg/d at the ~90 % yield of the AQS-RA |
| POWDER_TO_STOCK | closure | POLY_STOCK | 0.0900 | PTFE fine powder to stock (A-M-289). |
| S07 | closure | NUTRIENT_DOSE | 2.5000 | Study BMED salt / nutrient dose mid-band (AQS-EQP-NUT-001 / AQS-AUD-001 §4.6) — not tote s |
| S11 | closure | GROW_BED | 0.8000 | Study farm/galley organics return order ~fraction of S14 (AQS-AUD-001 §12) |
| S32 | closure | WS_PEROX | 3.0000 | AQS-DUTY-010: AUD s13 band 1-5 L/d at 3 of 1-5 starts, dilute 1.0 kg/L | value restored fr |
| S38 | closure | WET_BENCH | 0.0060 | AQS-DUTY-010: ST-LITHO-01 resist waste 6 g/d |
| S57 | closure | MET_MELT | 6.8389 | AQS-DUTY-010: Cu deposit 8.784 x 0.5 to wire, less melt fume 0.3% | value restored from gr |
| S71 | closure | MET_AHU | 20458.3200 | AQS-DUTY-010: MET LEV 720.0 m3/h (VENT_SCRUB 2.4 band 540-900 mid) at 1.184 kg/m3 Converte |
| S72B | closure | MET_SCRUB | 0.0158 | AQS-DUTY-010: lubricant mist 2.0 g/kg formed x 7.89 kg/d |
| S76 | closure | MEOH_FC | 5.0000 | Matches mid Source-A synth ~2–8 kg/d MeOH (AQS-MeOH-001); fuel to MEOH_FC |
| S77 | closure | MEOH_FERM | 0.0146 | AQS-DUTY-010: VS 0.0486 kg/d x 0.3 Nm3 CH4/kg VS -> MeOH at 70% | value restored from grap |
| TFE_TO_POLY_F | closure | TFE_SYN | 0.1000 | TFE monomer to polymerization (AQS-RATE-FP-MET; A-M-289). |
| VDF_TO_POLY_F | closure | VDF_SYN | 0.1500 | VDF monomer to polymerization (AQS-RATE-FP-MET; A-M-289). |
| CRU_TO_TFE | input | - | 0.2836 | Cl2 to TFE: 4 Cl2 per TFE from the CRU chlorate finish (AQS-SEL-FP; A-M-289). |
| HF_GEN_TO_TFE | input | - | 0.0800 | Aqueous HF to TFE: 0.10 kg/d TFE x 4 HF/TFE (R-22 route; AQS-SEL-FP, ULLMANN_FLUOROPOLY). |
| IA-COAT-IN | input | - | 0.0200 | Daily average of a batch recoat. Returns on IA-COAT-OUT. Does not consume the EW nickel de |
| IA-MEOH-REST | input | - | 1.2800 | AQS-DUTY-016. Each waste has a user. Each chemical has a source. |
