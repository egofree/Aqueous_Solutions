# Rewrite batch 27: standby route STOCK_TO_WIRE_DRAW at its rated case

Date: 2026-10-29

Task X-RTE-STOCK_TO_WIRE_DRAW is done. The route from the METAL_STORE dock buffer to the wire drawer carried no flow. It is a standby feed: the wire drawer normally takes its copper from MET_MELT (S57), and the route brings copper rod from the store when MET_MELT is out of service. The need is clear from first principles, because the drawer needs the same feed whichever route brings it.

## What changed

- New module `flow_graph/param/standby_routes.py`, called from `flow_graph/param/balance.py`. For each standby route it sets the rated rate to the design-day rate of the primary route, the outage to the new driver `standby_outage_d` (the N+1 outage basis of the foundry melt backups, A-M-283), and the extra holding of the source store. The route stays at zero on the design day, so the balance is unchanged.
- `docs-authority/_storage_sizing.py` adds the standby holding of a store to its working volume.
- `docs-authority/_task_plan_gen.py` treats a route with a rated case as finished and lists it as a done X-RTE task with its evidence.
- Assumption A-M-418 records the rule.

## Values

STOCK_TO_WIRE_DRAW is rated at the S57 rate, 6.8389 kg/d, for 2 d, so METAL_STORE holds a further 13.6778 kg of copper rod. The METAL_STORE nominal volume rises from 0.2286 m3 to 0.2372 m3 and the vessel still fits its 800 by 800 by 950 mm envelope. There is no cascade into bus demand, array, storage energy or balance closure: the route carries no energy, and the PV continuous rating stays at 350.0702 kW.
