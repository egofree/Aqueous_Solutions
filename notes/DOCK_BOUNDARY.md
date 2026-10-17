# Dock and boundary — item 9

Document number: AQS-BOUND-001  
Revision: A  
Date: 2026-10-17  
Authority: graph Rev AA, binding requirements. Not a PE stamp.  
Intake composition is not measured. Named as missing where it is.

## Intake (NORTH_DOCK)

Allowed after startup:

| Intake | Spec | Rate (assumption) | Notes |
|--------|------|-------------------|-------|
| Mineral feedstock | Any source: landfill, e-waste, tailings, industrial waste, regolith | 500 kg/d design basis | Composition not measured. Assay is plan line 1.1. |
| Energy | Solar (PV_ARRAY), geothermal (GEO_HP / GEO_ORC) | Per notes/POWER_DUTIES.md | No fuel import. |
| Air | Ambient, for cryo N₂/O₂ makeup and combustion air to afterburner | As required | Not a process feedstock. |
| People / food seed | Habitation startup only | — | Not a steady import. |

Not allowed as steady import:

- Fluoropolymer resin, monomers, or HF.  
- Cr, Mo, Ti metal or stainless that the plant is required to make.  
- Li grease, Ca grease, solvents, acids, bases.  
- Fertilizer.

Startup inventory (first fill of crucibles, anodes, seed wafers) is a one-time exception and is listed on the assumptions sheet, not as a dock duty.

## Export (BOUNDARY_EXPORT)

| Export | From | Notes |
|--------|------|-------|
| Finished goods | MFG_SHOP / STOCK_OUT / POLY_STOCK via dock | The product. Mass leaves; matching intake is the mineral feed. |
| None other by design | — | No process waste, no spent resin, no slag, no shell, no char. |

Existing edges S08G (GLASS_DIGEST → BOUNDARY_EXPORT) and S14X (GROW_BED → BOUNDARY_EXPORT) are surplus or product only. They are not waste. If a stream on those edges is not a product, it is rerouted internally; it does not become an export duty.

## Dock units

| Unit | Duty |
|------|------|
| NORTH_DOCK | Receiving. Mineral feed in. Freight only. |
| BOUNDARY_EXPORT | Product out. No process waste. |

## Open

- Measured composition of the 500 kg/d mineral feed (plan 1.1).  
- Which finished-good SKUs leave on BOUNDARY_EXPORT (not listed; mass only).

Stamped against graph Rev AC (closure pass, notes/CLOSURE_PASS.md).
