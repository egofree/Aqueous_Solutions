# One-line

Document number: AQS-ELEC-001  
Revision: A  
Date: 2026-10-17  
Authority: graph Rev AC, notes/POWER_DUTIES.md. Not a PE stamp.  
Checked against Rev AC. Not a measured installation.

## Bus

48 V DC shop/farm bus (AQS-PWR-001). Cell and induction current is the rectifier, not the inverter.

## Sources → LOAD_AGG

| Source | kW | Path |
|--------|---:|------|
| PV_ARRAY | 70 nameplate | SOL_ARK_60K → LOAD_AGG |
| FUEL_CELL | 4 | LOAD_AGG |
| ZNBR2 | 60 class | SOL_ARK_60K ↔ LOAD_AGG |
| BACKUP_GEN | 2.5 | LOAD_AGG, outage only |

## Loads

| Load | kW | Path |
|------|---:|------|
| RECTIFIER | 12 | LOAD_AGG → cells, IND_MELT, VAC_IND, RF_HEAT, OIL_PYRO |
| GEO_HP | 2 draw | LOAD_AGG |
| Farm, hab, fab, cryo | not re-rated | LOAD_AGG |

GEO_ORC and HYDRO_SET are not on this one-line as supplies.

## Notes

Induction batches schedule under the 12 kW rectifier or draw from the bus. No second bus. Detail in notes/POWER_DUTIES.md and notes/LOAD_ROLLUP.md.
