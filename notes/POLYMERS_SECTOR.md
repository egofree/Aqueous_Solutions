# POLYMERS sector

Document number: AQS-DUTY-POLY  
Revision: A  
Date: 2026-10-16  
Authority: graph Rev S. Not a PE stamp.  
Rates are design assumptions where stated; otherwise unset.

## Purpose

Produce polymer feedstock in defined form factors for other sectors. Encompasses the fluoropolymer train and other polymer production. Inputs from the Oil Line and the digester. No external resin.

## Sector boundary

F_RECOVER is on the digester line (sector DIGESTER), not in polymer production. It concentrates fluoride and sends it to HF_GEN. All polymerization and form-factor units remain in POLYMERS.

| Unit | Role |
|------|------|
| F_RECOVER | DIGESTER (not POLYMERS) | Fluoride recovery on the digester line. Feeds HF_GEN. |
| HF_GEN | Aqueous HF |
| VDF_SYN | VDF monomer (methanol–Cl₂–HF route) |
| TFE_SYN | TFE monomer (same route) |
| POLY_F | PVDF/PTFE polymerization + reclaim |
| POLY_OLEFIN | Polyolefin from oil-line light cuts + methanol |
| POLY_COND | Condensation polymer from digester organics (duty reserved) |
| PELLET | Pellet form factor |
| POWDER_RESIN | Powder form factor (linings, coatings) |
| FILM_CAST | Film/sheet form factor |
| POLY_STOCK | Staged output to other sectors |

## Inputs

| From | Sector | To | Carries |
|------|--------|----|---------|
| (fluoride streams) | DIGESTER | F_RECOVER | Fluoride concentrate |
| MEOH_SYNTH | MEOH | VDF_SYN / TFE_SYN / POLY_OLEFIN | Methanol |
| CRU | DIGESTER | VDF_SYN / TFE_SYN | Chlorine |
| OIL_FRAC | OIL | POLY_OLEFIN | Light cuts |
| BLACK_DIGEST | WTR | POLY_COND | Digester organics |

## Outputs (form factors)

| Form | From | To | Use |
|------|------|----|-----|
| Pellet | PELLET → POLY_STOCK | MFG_SHOP, WAFER_FAB | Molding, general feedstock |
| Powder | POWDER_RESIN → POLY_STOCK | MFG, wet linings | Coatings, gaskets, linings |
| Film | FILM_CAST → POLY_STOCK | MFG, FAB | Sheet, barrier, gasket stock |
| Reclaim | POLY_F internal | POLY_F | Regrind / depoly of scrap |

## Rates (assumptions, from prior notes)

- PVDF 0.14 kg/d, PTFE 0.09 kg/d (DESIGN_RATES).  
- Polyolefin: not yet rated; sized later to MFG/FAB demand.  
- Digester-to-POLY_COND: duty reserved; rate unset until digester organic assay exists.

Finished design: notes/POLYMERS_DESIGN.md. Graph Rev U. Rates are design assumptions (polyolefin 2.0 kg/d, condensation 0.5 kg/d, fluoropolymer per DESIGN_RATES).
