# Rewrite batch 34: sodium hydroxide made on site, recovery first

Date: 2026-10-29

## Change

Owner decisions t59u and t61u: the plant imports nothing except waste or raw ore, and every element is recovered from waste before any ore is taken. The sodium hydroxide make-up came from the dock as flake on stream IA-NAOH-MU. It is now made on site by a new unit, NAOH_PLANT, in the acid-base regeneration train of the DIGESTER sector. Task X-RTE-IMPORT-IA-NAOH-MU is done, and IA-NAOH-MU is retired.

- `flow_graph/param/caustic.py` sizes the unit from the make-up of the NaOH balance in `flow_graph/param/solver.py`. It is called from `flow_graph/param/write_graph.py`. The mass and element balances of the unit are asserted in the code.
- **Recovery first:** the make-up sodium leaves the leach as sodium chloride. Membrane chlor-alkali cells recover the fraction `na_purge_recycle_frac` of that salt on the new stream IA-NA-RECYCLE. The rest is bled to the dock on IA-NA-PURGE to carry the impurities out. IA-NA-PURGE now carries the sodium chloride mass, one NaCl per NaOH, where it used to carry a mass equal to the make-up.
- **Ore top-up:** only that shortfall comes from ore. The driver `naoh_route` selects one of two technologies:
  - CAUSTICIZE, the default, calcines trona ore to soda ash and causticises it with lime, with a recalcining electric lime kiln and limestone ore as lime make-up.
  - CHLOR_ALKALI re-saturates the cell brine with halite ore.
  - The streams of the route not selected are retired.
- **Cell byproducts:**
  - The cell chlorine is shipped at the dock on IA-NAOH-CL2-SHIP, alongside the existing chlorine exports.
  - The cell hydrogen goes to the H2 header on IA-NAOH-H2, as the electrowinning cells' hydrogen does. The H2 dryer grows to match, and its envelope file was regenerated.
- **Evaporator load:** the liquor reaches EVAP_BASE at its mixed strength on IA-NAOH-LIQ, and the evaporator removes its water. `solver.evap` now carries the water of a make-up liquor. The driver `naoh_makeup_form` (anhydrous flake) is retired, and the strength comes from `caustic.product_wt()`.
- **New stream names:** the first draft reused the stream name IA-CA-CL2-SHIP, which already belongs to the CA_POT chlorine export. The new streams now use the NAOH prefix, and the code asserts that a new stream does not take an existing name.
- **Paperwork:**
  - The new drivers and the basis are recorded in A-M-422, with the new reference ULLMANN_NAOH.
  - PARAMETRIC_MODEL (AQS-PAR-001) is at revision D, with a new section 7.1 that compares both routes.
  - The unit has a system-tree entry, a material selection, instrument loops and sizing coverage.

## Owner choices left open

1. **Top-up technology:** on CAUSTICIZE, the kiln shell losses dominate the load of the small top-up, while CHLOR_ALKALI makes it in the cells that recover the purge salt. Table 7.1 of AQS-PAR-001 compares both routes.
2. **Hydrogen placement:** the cell hydrogen joins the H2 header, which touches the held hydrogen and oxygen ownership questions.

## Values

| Quantity | Before | After |
|---|---|---|
| IA-NAOH-MU, NaOH flake from the dock | 4.3936 kg/d | retired |
| IA-NAOH-LIQ, liquor to EVAP_BASE | none | 16.7507 kg/d |
| IA-NA-RECYCLE, purge salt recovered | none | 5.7779 kg/d |
| IA-NA-PURGE, purge salt bled | 4.3936 kg/d | 0.6420 kg/d |
| IA-TRONA-MU, trona ore | none | 0.9196 kg/d |
| IA-LIMESTONE-MU, limestone ore | none | 0.0289 kg/d |
| IA-NAOH-CL2-SHIP, chlorine shipped | none | 3.5050 kg/d |
| IA-NAOH-H2, hydrogen to the header | none | 0.0997 kg/d |
| NAOH_PLANT electrical load | none | 1.1935 kW |
| EVAP_BASE electrical load | 1.328 kW | 1.349 kW |
| PV continuous rating | 352.3096 kW | 353.877 kW |
| ZNBR2 battery | 218.4826 kW | 220.0536 kW |
