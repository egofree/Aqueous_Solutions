# Rewrite batch 46c: fuel route for the fuel-fired melt backup

Task X-RTE-COMB-HEAT-FUEL is closed (A-M-438). COMB_HEAT, the fuel-fired melt backup of IND_MELT, had no fuel route, and its off-gas route was retired in batch 43. It is kept rather than retired, because it is the one melt path that does not depend on the electrical supply of IND_MELT and its electric alternate RF_HEAT, so it adds real redundancy.

Its rated case is IND_MELT and RF_HEAT both out for the standby outage. COMB_HEAT then melts the design-day charge of IND_MELT. The heat into the metal is the IND_MELT melt energy times the coil efficiency, and the fuel is that heat over the efficiency of a fuel-fired crucible furnace and the heating value of the fuel. The new module `flow_graph/param/comb_heat.py` builds four routes, each zero on the design day and rated by `standby_routes.py`:

- IA-C5-COMB carries the C5-C10 cut from PROD_C5_C10, the default fuel.
- IA-MEOH-COMB carries plant methanol from MEOH_TANK, the alternative selected by comb_heat_fuel.
- IA-COMB-O2 carries the combustion oxygen of the air, with its excess.
- COMB_OFFGAS, restored from retirement, takes the carbon dioxide, water and excess oxygen to MET_SCRUB.

The store of the selected fuel holds the rated fuel for the outage. The chlorinator carbon monoxide was evaluated and is not a valid fuel for this duty. The chlorination makes under a kilogram a day, most of it already drawn by SOLV_PLANT and RESIST_SYN, against a rated need of tens of kilograms a day. Both fuel modes were checked, and the balance fit moves no rate.
