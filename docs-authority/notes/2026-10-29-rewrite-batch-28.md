# Rewrite batch 28: standby route IND_TO_ATOM at its rated case

Date: 2026-10-29

Task X-RTE-IND_TO_ATOM is done. The route from the foundry melt IND_MELT to the gas atomiser carried no flow. It is a standby feed: the atomiser normally takes its charge from MET_MELT (IA-MELT-ATOM), and this route pours the charge from IND_MELT when MET_MELT is out of service. The atomiser needs the same charge whichever furnace pours it, so the need is clear from first principles.

## What changed

- `flow_graph/param/standby_routes.py` gains the IND_TO_ATOM row. A route drawn from a melt furnace records the furnace heats a day on the design day and in the outage. The furnace rating does not change, because each heat is the same charge.
- Assumption A-M-418 is extended to this route.

## Values

IND_TO_ATOM is rated at the IA-MELT-ATOM rate, 3.555954 kg/d, for an outage of 2 d. IND_MELT then melts its own charge of 37.0139 kg/d plus the atomiser charge in 10 kg heats, so it runs 5 heats a day in the outage instead of 4. One heat takes about 5.3 kWh (21.249 kWh/d over 4 heats), which is well inside a day at the 15 kW peak. The extra heat replaces the melt energy of MET_MELT, which is out, so there is no cascade into bus demand, array, storage or balance closure on the design day.
