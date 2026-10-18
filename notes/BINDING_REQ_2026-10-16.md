# Binding requirements — fluoropolymers, critical metals, cost basis

Document number: AQS-REQ-001  
Revision: A  
Date: 2026-10-16  
Authority: user decisions 2026-10-16. Not a PE stamp.

## Q-011 Fluoropolymers

Plant must synthesize PVDF and PTFE (and related fluoropolymers used in the plant) from scratch and reclaim scrap for reuse. External supply is not permitted.

Required process units (names provisional):

- F-RECOVER: fluoride recovery from leach, solids-line grit, and spent HF streams. Feeds WS_HF_ED.
- HF-GEN: aqueous HF generation (existing WS_HF_ED duty, now mandatory).
- VDF-SYN / TFE-SYN: monomer synthesis from HF + carbon sources already recovered (pyro char, methanol, or CO).
- POLY-F: suspension or emulsion polymerization to PVDF/PTFE resin. Reclaim path: mechanical regrind for non-pressure parts, or controlled depolymerization back to monomer.
- All wet walls, valves, CONC housings, and seals that currently wait on POL-VCM or FKM now wait on this train instead of external resin.

Status: not designed. Core functionality.

## Q-013 Critical metals

Plant must produce every essential material on-site. No exceptions for Cr, Mo, Ti, or the stainless grades that require them.

Required additions:

- TI-CELL: titanium metal from ilmenite/rutile grit. Molten-salt or Kroll-type duty. Feeds pyrolyzer shell, anode mesh, and any Ti parts.
- MO-CELL: molybdenum recovery (existing PK-Mo). Feeds 316L and any Mo-bearing alloys.
- CR-CELL: chromium recovery from stainless scrap or chromite. Not aqueous electrowinning. Feeds 304/316 grades.
- Stainless production itself is in scope once the alloy elements are available. Flammable-liquid tanks currently sized as 304L must either wait on CR-CELL + MO-CELL or be re-specified to a plant-makeable carbon steel with a compatible lining, subject to NFPA 30 and the fluoropolymer train.

Status: TI-CELL and PK-Mo already listed as blockers in HANDOFF_2026-10-04.md. CR-CELL is new. All are core.

## Q-012 Cost basis

Cost estimates use researched values only. Every numerical assumption is entered on the master assumptions list (currently ASSUMPTIONS sheet in plant2_bom.xlsx or its successor) with a citation or measurement note. Published curves and weight × commodity factors are not defaults.

## Immediate layout items carried forward

Six storage tanks outgrew the space drawn for them. Plant model must read tank volumes from design data before the next clash check. Flammable-tank material decision is gated on the CR/MO routes above.

## Current status (2026-10-16)

- Assays deferred to later work (notes/ASSAY_TI_MO.md). Literature ranges in notes/LIT_ASSAY.md.  
- Kroll Cl₂/Mg placeholder balance complete (notes/KROLL_BALANCE.md). Net zero if Mg pot has spare capacity. Not a design rate.  
- CR_CELL duty locked (notes/CR_CELL_DUTY.md). Molten-salt primary.  
- POLYMERS sector (graph Rev S). Fluoropolymer train plus other polymer production. Feeds from Oil Line and digester. Form factors to MFG/FAB. notes/POLYMERS_SECTOR.md.  
- Carbide train: not added as baseline. See notes/CARBIDE_AND_ECF.md.

- Assays named missing: notes/ASSAY_TI_MO.md (dense-grit Ti/Fe; EW_9 Mo + Zn/Fe/Ni).  
- Kroll placeholder balance (not a design rate): notes/KROLL_BALANCE.md. Net Cl₂ and Mg zero if the existing Mg pot has spare capacity.  
- CR_CELL duty locked: notes/CR_CELL_DUTY.md (molten-salt primary).  
- Rates remain unset. loops_closed remains false.

plant_flow_graph.json revision J (2026-10-16): TI_CELL (Kroll primary) and MO_CELL (molten-salt primary) locked. Cl₂ and anode-gas returns to CRU added. Rates unset. loops_closed remains false.

Duties: notes/TI_MO_DUTIES.md Rev B. Selection: notes/TI_MO_SELECTION.md.

plant_flow_graph.json revision I (2026-10-16): F_RECOVER, HF_GEN, VDF_SYN, TFE_SYN, POLY_F, CR_CELL, TI_CELL, MO_CELL present. Placeholder mass edges added. Rates not set. loops_closed remains false.

Duties: notes/TI_MO_DUTIES.md (TI_CELL Kroll or FFC; MO_CELL precipitation + H₂ reduction).

ASSUMPTIONS sheet in plant2_bom.xlsx records the three binding constraints.
