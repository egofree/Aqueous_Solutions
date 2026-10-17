# Glass, gas, and cryo — item 5

Document number: AQS-DUTY-GGC  
Revision: A  
Date: 2026-10-17  
Authority: graph Rev Y. Not a PE stamp.  
Rates are design assumptions.

## Paths closed

| Path | Route | Status |
|------|-------|--------|
| Ceramic shell | SHELL_BREAK → GLASS_MILL → GLASS_DIGEST | Present since Rev P |
| Pyro char | OIL_PYRO → SI_REDUCE | Added Rev Y. 3 kg/d assumption |

SI_REDUCE is in sector GLASS. It is the silicon/boron reduction duty. Char is the carbon source. No open char stream.

## Gas duties — new loads

| Load | Source | Destination | Rate (assumption) |
|------|--------|-------------|-------------------|
| Cl₂ from pots and Kroll | AL_POT, MG_POT, TI_CELL | CRU | Net zero on the Cl₂ loop (KROLL_BALANCE). CRU already receives these. |
| HCl from monomer | VDF_SYN, TFE_SYN | Acid loop / BMED | <1 kg/d. Returns with the existing HCl CIP path. |
| HF | HF_GEN | VDF_SYN, TFE_SYN | 0.5 kg/d. Contained. No atmospheric release. |
| NCG | NCG_HEADER | AFTERBURNER | 2 kg/d. CO₂ from afterburner to CRYO_CO2 (edge S18 present). |
| Anode gas from MO/CR cells | MO_CELL, CR_CELL | CRU | Edged. Rate unset until assay. |

No new scrubber is required for these loads. Existing ALK_SCRUBBER and ACID_POLISH_SCRUB cover upsets. HF stays in the monomer train.

## Cryo duties — incremental

| Stream | To | Incremental load |
|--------|----|------------------|
| Afterburner CO₂ | CRYO_CO2 | From 2 kg/d NCG. Small vs plant CO₂. |
| H₂ from EW / pots | HDR_H2 → CRYO_H2 | Unchanged by this item. |
| O₂ | HDR_O2 → CRYO_O2 | Unchanged. |
| N₂ | CRYO_N2 | Unchanged. Cover gas for foundry is a draw, not a new source. |

Cryo units are not resized. The NCG-derived CO₂ is within the existing CRYO_CO2 duty.

## Open

- SI_REDUCE furnace type and kW (arc vs induction).  
- Anode-gas rate from MO_CELL and CR_CELL (assay).  
- Exact HCl return edge from VDF/TFE to BMED (implied; not a new unit).
