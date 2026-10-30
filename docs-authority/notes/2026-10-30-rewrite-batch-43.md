# Rewrite batch 43: the standby and return route sets

Date: 2026-10-30

## Change

Task X-RTE grouped the present mass routes that carry no flow into a standby set and a return set. Each route is now decided by the owner rule of 2026-10-29: it gets a rated case, it gets real flow, or it is retired. The basis is A-M-433.

### Standby routes given a rated case

Each route stays at zero on the design day and carries the rated rate in the case that puts it in service, on the pattern of A-M-418.

| Route | Rated rate | Case |
|---|---|---|
| CAST_TO_EXTRUDE, EXTRUDE_TO_STOCK | 3.0 kg/d, the CAST_TO_ROLL rate | ROLL is out and the cast-line billet is extruded |
| VAC_IND_TI, VAC_TO_INV | 0.5 kg/d, the METALS_TO_IND_MELT rate | IND_MELT is out and the titanium is skull-melted and poured to the investment line |
| TI_CELL_CL2_TO_CRU | 1.4813 kg/d, the IA-CL2-MG-TI rate | the Kroll chlorinator is out while MG_POT runs down |
| MO_CELL_ANODE_GAS_TO_CRU | 0.0693 kg/d, 1.5 Cl2 per Mo | the carbochlorination step is out while the cell runs down |
| IA-ESS-HYDRO-DIS, IA-ESS-HYDRO-CHG | the 2700 m3 upper reservoir in one day | ZNBR2 is lost, then the reservoir is pumped back on PV surplus |
| IA-DC-SPRAY, IA-DC-EVAP | 422.5 kg/d, the 12 kW rated duty on evaporation | the site rejection mode is evaporative |
| IA-NIT-VENT | 0.37 kg/d of air | API 2000 out-breathing of the nitric tank for a whole day |

### Return given real flow

CAST_SCRAP_TO_IND was held at zero as a campaign event. The gates and risers of a permanent-mold pour are cut from every casting, so the return is a daily flow. The new driver cast_gating_return_frac, 0.15 of the pour (ASM_V15_PM), gives 0.53 kg/d. IND_MELT_TO_CAST rises to 3.53 kg/d, and the melt energy and heats of IND_MELT include the return. The copper stock to ROLL stays 3.0 kg/d.

### Routes retired

- DRAW_TO_STOCK: DRAW has no feed, and the MFG wire drawer makes the wire on S57.
- SINTER_TO_STOCK: SINTER has no feed, and the atomiser powder goes to MFG_SHOP, its only consumer.
- ATOM_TO_STOCK: a powder stock route duplicates S60.
- COMB_OFFGAS: COMB_HEAT has no fuel route, so it can make no off-gas. A fuel route for this fuel-fired alternate is the new task X-RTE-COMB-HEAT-FUEL.
- VAC_IND_TO_VAC_CAST: VAC_CAST has no product route, and the vacuum titanium melt pours to INV_CAST.
- IA-N2-RET: AIR_RECEIVER feeds the air and nitrogen header and holds its pressure, so the header never returns gas to the cold box.

### Routes left listed

- The float-sink grit routes to TI_CELL, MO_CELL and CR_CELL and the three cell slag returns wait on the dense-grit assay (Q-037, A-M-427). They are listed as X-RTE-ASSAY.
- IA-O2-RET and IA-CO2-RET are in areas the owner holds: O2 ownership and the greenhouse gas routes. They are listed as X-RTE-HELD.

## Values

| Quantity | Before | After |
|---|---|---|
| CAST_SCRAP_TO_IND | 0 | 0.5294 kg/d |
| IND_MELT_TO_CAST | 3.0 kg/d | 3.5294 kg/d |
| Standby routes with a rated case | 2 | 15 |
| Routes retired in this batch | none | 6 |
