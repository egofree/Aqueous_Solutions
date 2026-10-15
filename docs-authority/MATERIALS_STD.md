# Materials standard

Document number: AQS-STD-002
Revision: A
Date: 2026-10-15
Authority: graph Rev BH. Study. Not a PE stamp. Feed basis AQS-ASSAY-001 Rev C. Referenced from AQS-PLAN-007 section X-MAT.

| Rev | Description | Date |
| --- | --- | --- |
| A | First issue. Owner rule: chlor-alkali and acid-regen systems are PVC; no metal wetted part where oxidizing or reducing conditions exist. First audit of every present unit. | 2026-10-15 |

## 1. Rules

M1. Compatibility decides every material choice. A material is named only with the stream it touches. A duty sheet section 3 that names a material without its stream is not complete.

M2. Everything in the chlor-alkali and acid-regen systems is PVC. This covers the leach, the CRU oxidant loop, BMED acid and base, the polish bank, the recycle loop, the float/sink and class-treat liquors, salt feed, the acid and alkaline scrubbers, and every tank, header, pipe, and nozzle on those liquors.

M3. No metal container or wetted part where oxidizing or reducing conditions exist. Oxidizing: chlorate or hypochlorite liquor, anolyte, nitric, peroxide, Cl₂, Br₂, O₂ wet. Reducing: catholyte, anaerobic digestion, fermentation, wet H₂. A metal part in these services is a violation unless rule M6 names it.

M4. Fasteners, supports, and frames in the head space of these vessels are non-metallic, or are metal outside the wetted and vapor zone and isolated from it.

M5. Thermoplastic limits. PVC-U to 60 °C. CPVC to 93 °C. These two limits are assumptions from published PVC-U and CPVC data, not measured in this plant. Above 60 °C the choice is CPVC. Above 93 °C the case is flagged and held; the alternative is a higher-rated thermoplastic or a lined part, never bare metal in M3 service. Temperature is taken from the graph; where the graph has none, the duty says so.

M6. Electrochemistry. Metal is allowed where it is the electrode: EW cathodes and anodes, CRU and BMED electrodes, fuel-cell and flow-battery stacks. Each such metal is listed on its duty with its potential role. Required with it:
- Galvanic couples. No two dissimilar metals in one electrolyte unless that couple is the cell. No metal bolt through a metal electrode into a different metal.
- Stray current. Every pipe and header between cells at different potential is non-metallic, with a stated electrolyte path length. Rectifier busbars are isolated from the frame. The frame is grounded on its own path, not through the liquor.
- Anodic dissolution. Every electrode carries a dissolution or coating-loss basis, or the item is held.
- Hydrogen embrittlement. Metal in wet H₂ or at a cathode is austenitic stainless or titanium only where the H₂ partial pressure and temperature are stated; titanium at a cathode is held for hydriding. Carbon and high-strength steel are not used in H₂ service.

M7. Metal is permitted where no polymer survives: cryogenic service, pyrolysis and melt hot faces, dry O₂ (polymers ignite), and dry hydrocarbon. Each such unit states which of these applies.

## 2. Audit, 2026-10-15

Every present unit's section 3 was read against M1 to M7.

Fixed in this pass (clear violations, section 3 rewritten, no rate change):
- PVC-U, acid-regen and leach liquors (M2): BMED_ACID, BMED_BASE, POLISH_BANK, CONTINUOUS_RECYCLE, CRU, FLOAT_SINK, S13_CLASS_TREAT, SALT_FEED. LEACH_CSTR_1 is changed with its model.
- PVC-U, oxidizing or reducing wet service (M3): WS_KOH, WS_PHOS, WS_AMMONIA, WS_HF_ED, WET_BENCH, GREY_TREAT, BLACK_DIGEST, MEOH_FERM.
- PVC-U scrubbers (M2, M3): ACID_POLISH_SCRUB, ALK_SCRUBBER, NOX_SCRUB, MET_SCRUB.
- PVC-U or HDPE water tanks (M1): CATCH_TANK, ROOF_TANK, REMIN.
- Glass or PVC-U, 316L removed (M3): ACETOX, ACEX, ALD, BUCL, FORM, GLYOXAL, IMID, MEAM, QUAT.
- LEACH_CSTR_1 tank PVC-U; the 316L / CPVC conflict with AQS-NZ-001 is resolved for PVC.

Flagged on temperature (M5):
- LEACH_CSTR_1, HL-Q3-A/B-HX5 ports. Q3 supply 95 °C on the graph exceeds PVC-U and the CPVC limit. CPVC is the thermoplastic alternative. Held.

Ambiguous, not changed (each is a TASK_PLAN X-MAT-06 item):
- EW_1 to EW_9. 316L cathode, Ti/PbO₂ anode, PVC/FRP tank. Electrodes allowed under M6; dissolution and stray-current basis missing.
- HX8. Titanium plates in EW aisle liquor. Ti in reducing chloride liquor is a hydriding and crevice risk. Non-metallic exchanger not evaluated.
- ZNBR2_BR2_REGEN. 316L shell with wet Br₂. Violates M3. PVC is poor in wet Br₂; PVDF or glass not evaluated.
- GLASS_DIGEST. 316L, digest liquor not characterized; may be HF or alkali.
- WS_NITRIC, WS_PEROX. Strong oxidizers. PVC limit depends on concentration, not on the graph.
- WS_SOLV, WS_DOPE, WS_SLURRY. Solvent and dopant compatibility not stated.
- ETOH_STILL, BUOH_STILL. 316L for boiling solvent; fermentation broth may be reducing and acidic. Temperature exceeds PVC.
- VCD_TRAIN, FAB_UPW_TANK, HDR_UPW, BMED_UPW_POLISH. UPW and distillation; PVC leaching and temperature not stated.
- HDR_H2, RELIEF_H2, H2_DRYER. 316L in H₂. M6 embrittlement basis needed.
- HDR_O2. 316L. Dry O₂ is an M7 metal service; wet O₂ is not stated.
- FLUE_KO, BAGHOUSE, AFTERBURNER_FLUE. Hot flue with acid condensate. M7 vs M3 depends on temperature not on the graph.
- Q1_A to Q4_B, GEO_*, CURTAIL, HEAT_SINK, Q4_BUS, MET_HX_Q4, CRYO_HX_Q4, HYDRO_SET, TERRACE_IRRIG, NUTRIENT_DOSE. Water loops in 316L; no redox service stated. Q1/Q2 temperatures exceed thermoplastics.
- MEOH_SYNTH, MEOH_TANK, MEOH_COND. Methanol; reducing synthesis gas. M6/M7 basis needed.
- OIL sector (carbon steel). Pyrolysis is reducing but hot. M7 applies to the hot face; cut tanks and condensers need a stated temperature.
- MFG units with "316L where wet". Wet service not named.

Compliant as written: CRYO sector (M7 cryogenic), MET_MELT and SIC_FURNACE (M7 hot face), electrical nodes and stacks with no wetted alloy (M6 for the stacks), farm and habitation units already HDPE or PVC.
