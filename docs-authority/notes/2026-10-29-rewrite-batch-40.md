# Rewrite batch 40: bench solvent made on site, recovery first

Date: 2026-10-29

## Change

Owner decisions t59u and t61u: the plant imports nothing except waste or raw ore, and it recovers before it makes. The bench ethanol and acetone came from the dock on IA-SOLV-MU. Task X-RTE-IMPORT-IA-SOLV-MU is done, and IA-SOLV-MU is retired.

- The new module `flow_graph/param/solvent.py` adds the unit SOLV_PLANT in the FAB reagent train. WET_BENCH collects most of its solvent in a segregated spent-solvent drain (IA-SOLV-SPENT), and a batch still returns most of that, redistilled, to WS_SOLV on IA-SOLV-PLANT. The still bottoms go to the light oil cut at OIL_FRAC (IA-SOLV-BTMS). The spent etch S10 falls by the solvent drawn off.
- Only the shortfall is made new, on one of two routes selected by the driver solv_route:
  - MEOH_CO, the default: plant methanol (IA-SOLV-MEOH) is carbonylated to acetic acid with the chlorinator CO of TI_CELL (IA-SOLV-CO), which was exported at the dock as fuel gas. Part of the acid is ketonised to acetone, and the rest is hydrogenated to ethanol with header hydrogen (IA-SOLV-H2). The off-gas leaves at the dock with the fuel-gas class export, as the chlorinator CO did (IA-SOLV-VENT). The afterburner was not used, because its oxygen is held.
  - FERMENT: galley food waste (IA-SOLV-FW) feeds an acetone-butanol-ethanol fermentation and a yeast fermentation. The stillage returns to BLACK_DIGEST.
- MEOH_CO is the default because it takes a waste gas and a plant product in small amounts. FERMENT would take most of the galley waste from the digester.
- The unit is added to the system tree, the materials selection, the instrument index and the sizing coverage. AQS-PAR-001 is at revision G, with section 7.3 and Table 7.5. The references ULLMANN_ACETIC and PHAM2013 are added.
- The basis is recorded in A-M-428. The recovery-first check now has no pending import.

## Values

| Quantity | Before | After |
|---|---|---|
| IA-SOLV-MU, solvent from the dock | 0.2100 kg/d | retired |
| IA-SOLV-SPENT, spent solvent to the still | none | 0.1995 kg/d |
| Solvent recovered by the still | none | 0.1895 kg/d |
| Solvent made new (MEOH_CO) | none | 0.0205 kg/d |
| IA-SOLV-CO, chlorinator CO taken | none | 0.0179 kg/d |
| IA-KROLL-CO, CO export | 0.6295 kg/d | 0.6116 kg/d |
| SOLV_PLANT load | none | 0.0103 kW |
| Galley waste FERMENT would take | none | 0.98 kg/d of 1.18 kg/d |
