# Fluoropolymer train duties

Document number: AQS-DUTY-FP  
Revision: A  
Date: 2026-10-16  
Authority: binding requirements 2026-10-16, graph Rev K. Not a PE stamp.  
Rates not set. loops_closed remains false.

## Purpose

Synthesize PVDF and PTFE (and related fluoropolymers used in the plant) from scratch and reclaim scrap. External resin supply is closed. Binding requirement.

## Units (all present on graph)

| Unit | Role |
|------|------|
| F_RECOVER | Fluoride recovery from leach, solids grit, and spent HF streams |
| HF_GEN | Aqueous HF generation (existing WS_HF_ED duty, now mandatory) |
| VDF_SYN | Vinylidene fluoride monomer |
| TFE_SYN | Tetrafluoroethylene monomer |
| POLY_F | Polymerization to PVDF/PTFE with reclaim path |

## Chemistry (locked at concept level)

1. **F_RECOVER.**  
   Fluoride is collected from leach off-gas scrub liquor, solids-line grit (if present), and any spent HF. Concentrated as a fluoride salt or dilute HF. Feed to HF_GEN.

2. **HF_GEN.**  
   Aqueous HF from the recovered fluoride. Existing WS_HF_ED concept. Product is aqueous HF to the monomer units and to any direct HF users (wet bench, glass line).

3. **VDF_SYN.**  
   Vinylidene fluoride from HF + a recovered carbon source (pyro char, methanol, or CO). Typical industrial route is chlorination/dehydrochlorination or related; exact path is not yet selected. Product to POLY_F.

4. **TFE_SYN.**  
   Tetrafluoroethylene from HF + recovered carbon. Same carbon-source constraint. Product to POLY_F.

5. **POLY_F.**  
   Suspension or emulsion polymerization to PVDF (from VDF) and PTFE (from TFE).  
   Reclaim: mechanical regrind of scrap for non-pressure parts, or controlled depolymerization back to monomer. Both paths are required.

## Returns

- Spent acid and salt from HF_GEN and polymerization → BMED or leach as appropriate.  
- Unreacted monomer → recycle to POLY_F.  
- Regrind or depolymerized scrap → POLY_F or monomer units.

## Graph edges (existing placeholders)

- F_RECOVER → HF_GEN (fluoride concentrate)  
- HF_GEN → VDF_SYN (aqueous HF)  
- HF_GEN → TFE_SYN (aqueous HF)  
- VDF_SYN → POLY_F (VDF)  
- TFE_SYN → POLY_F (TFE)

No rates. No assay on fluoride feed.

## Monomer route (locked)

See notes/MONOMER_ROUTE.md.  
Both VDF and TFE: methanol → chloromethanes → hydrofluorination → monomer.  
Closes on methanol, CRU chlorine, and HF_GEN. HCl returns to the acid loop.  
Vessel envelopes: notes/VESSEL_ENVELOPES.md.

- Exact monomer synthesis route (chlorocarbon vs. other).  
- Polymerization initiator, surfactant, and reactor type.  
- Depolymerization conditions and yield.  
- Vessel envelopes, nozzle schedules, containment class for HF and TFE.  
- Fluoride mass balance against leach and solids-line feeds.

## Sector

F_RECOVER is in sector DIGESTER (digester line). HF_GEN, VDF_SYN, TFE_SYN, POLY_F remain in sector POLYMERS. Graph Rev T. See notes/POLYMERS_SECTOR.md.

Concept duties locked. Rates and route selection are later work. External fluoropolymer supply remains closed.
