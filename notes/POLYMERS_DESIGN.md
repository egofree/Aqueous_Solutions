# POLYMERS sector — finished design

Document number: AQS-DES-POLY  
Revision: A  
Date: 2026-10-16  
Authority: graph Rev U, notes/MONOMER_ROUTE.md, notes/DESIGN_RATES.md. Not a PE stamp.  
Rates are design assumptions for a 500 kg/day plant. Not measured.

## Boundary

- `F_RECOVER` is on the digester line (sector DIGESTER). It is not a polymer production unit.  
- Everything from `HF_GEN` through form-factor stock is sector POLYMERS.

## Process

### Fluoropolymer (locked)
Methanol + Cl₂ (CRU) + HF (from F_RECOVER via HF_GEN) → VDF and TFE → POLY_F → PVDF/PTFE.  
Reclaim: regrind for non-pressure parts, or depolymerization back to monomer. Both required.

### Polyolefin
Light cuts from OIL_FRAC + methanol from MEOH_SYNTH → POLY_OLEFIN.  
Route: oligomerize/polymerize C2–C4 fraction to PE/PP-type resin. Exact catalyst is later detail; the carbon source is on-site.  
Product to PELLET (molding stock) and, if required, FILM_CAST.

### Condensation (digester)
BLACK_DIGEST organics → POLY_COND.  
Duty: dry and react digester fatty/organic fraction to a condensation resin (polyester-type) when the organic assay supports it.  
Until that assay exists, POLY_COND is installed but fed at the assumption rate below; it does not block the sector.

## Form factors

| Unit | Product | Typical use |
|------|---------|-------------|
| PELLET | 2–4 mm pellets | MFG molding, general feedstock |
| POWDER_RESIN | <100 µm powder | Linings, coatings, gasket compound |
| FILM_CAST | Sheet/film | Barrier, gasket sheet, fab consumables |
| POLY_STOCK | Staged | To MFG_SHOP, WAFER_FAB, and wet-line lining stock |

## Rates (assumptions)

| Product | Rate | Basis |
|---------|------|-------|
| HF to monomers | 0.5 kg/d | DESIGN_RATES |
| VDF | 0.15 kg/d | DESIGN_RATES |
| TFE | 0.10 kg/d | DESIGN_RATES |
| PVDF resin | 0.14 kg/d | ~90 % yield |
| PTFE resin | 0.09 kg/d | ~90 % yield |
| Polyolefin resin | 2.0 kg/d | MFG housings, farm hardware, non-fluoro parts |
| Condensation resin | 0.5 kg/d | Digester organic assumption; revise when assayed |
| Pellet out | 2.5 kg/d | Polyolefin + part of fluoropolymer |
| Powder out | 0.15 kg/d | Fluoropolymer linings |
| Film out | 0.3 kg/d | Sheet stock |

Total polymer stock ≈ 3 kg/d. Consistent with consumable and replication demand, not a commodity plant.

## Utilities

- Cl₂ from CRU to VDF_SYN and TFE_SYN (edge added). HCl returns to the acid loop.  
- Methanol from MEOH_SYNTH.  
- No external monomer, catalyst carrier, or resin.

## Olefin and condensation

POLY_OLEFIN sized in notes/OIL_POLY_SIZE.md (2 kg/d, 150–250 °C, 1–5 MPa).  
POLY_COND recipe remains open on the digester organic assay.

- POLY_OLEFIN catalyst identity and reactor pressure.  
- POLY_COND recipe once digester organic assay exists.  
- Exact pelletizer and film-die dimensions.

## Graph

Rev U. CRU → VDF_SYN and CRU → TFE_SYN added. Rates above are the design basis.

Stamped against graph Rev AC (closure pass, notes/CLOSURE_PASS.md).
