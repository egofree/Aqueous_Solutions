# Power duties — item 8

Document number: AQS-DUTY-PWR  
Revision: A  
Date: 2026-10-17  
Authority: graph Rev Z, notes/LOAD_ROLLUP.md. Not a PE stamp.  
Duties below are the design basis. Study values already on some nodes are retained as the source of the numbers.

## Load to cover

From notes/LOAD_ROLLUP.md: new process loads average ~20 kW, peak ~67 kW if every batch overlaps. Rest of plant (EW, cryo, farm, hab, fab) is not re-rated here. Power train is sized to cover the new loads with margin and to keep the existing study ratings.

## One duty each

| Unit | Sector | Rated duty | Role |
|------|--------|------------|------|
| PV_ARRAY | ELEC | 70 kW nameplate | Daytime source. Not continuous average. |
| FUEL_CELL | ELEC | 4 kW continuous | H₂/O₂ baseload and night cover. |
| BACKUP_GEN | ELEC | 2.5 kW | H₂ genset. Outage only. Not normal supply. |
| ZNBR2 | ELEC | 60 kW / study energy | Shift energy. Charge from PV; discharge to LOAD_AGG. |
| GEO_HP | GEO | 2 kW electrical draw | Lifts heat to Q4. Not a power source. |
| GEO_ORC | GEO | 0–2 kW_e | Only if surplus heat exists. Not in the base sum. |
| HYDRO_SET | PUMPED_HYDRO | Study only | Ideal store << ZnBr₂. Not in the base sum. Scale-up path documented; not rated as supply. |
| RECTIFIER | ELEC | 12 kW | DC to cells and induction. Foundry batches schedule under this or accept a short peak from the bus. |
| LOAD_AGG | ELEC | — | Aggregates PV, fuel cell, ZnBr₂, rectifier. |
| SOL_ARK_60K | ELEC | Inverter/charger | Ties PV and ZnBr₂. |

## Balance (design)

| Source | kW | Notes |
|--------|---:|-------|
| PV nameplate | 70 | Day |
| Fuel cell | 4 | Continuous |
| ZnBr₂ discharge | up to 60 | Shift |
| Backup gen | 2.5 | Outage only |
| **Firm without PV** | **4** | Fuel cell only, plus storage |
| New process average | ~20 | Covered by PV + storage, not by fuel cell alone |

GEO_ORC and HYDRO_SET are not counted in the firm number. Backup gen is not counted in normal supply.

## Tie to rollup

IND_MELT 25, VAC_IND 15, RF_HEAT 5, OIL_PYRO 15, polymers 5, grease 2. Schedule so induction batches do not all stack on the 12 kW rectifier; overflow comes from the DC bus via LOAD_AGG. No new bus.

## Open

- Measured PV yield at the site.  
- Fuel-cell H₂ consumption vs cryo/EW H₂ balance.  
- Whether rectifier is raised above 12 kW or batches stay scheduled.

Stamped against graph Rev AC (closure pass, notes/CLOSURE_PASS.md).
