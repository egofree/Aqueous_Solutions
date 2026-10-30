# Rewrite batch 33: sulfuric acid made on site

Date: 2026-10-29

## Change

Owner decision t59u: the plant imports nothing except waste or raw ore. The 98 wt% sulfuric acid for the HF kiln was imported at the dock on stream IA-H2SO4-MU. It is now made on site by a new unit, ACID_PLANT, in the fluoropolymer train of the POLYMERS sector. Task X-RTE-IMPORT-IA-H2SO4-MU is done, and IA-H2SO4-MU is retired.

- `flow_graph/param/sulfuric.py` sizes the unit from the acid demand of HF_GEN in `flow_graph/param/fluoro_train.py`, which calls it. The mass balance of the unit is asserted in the code.
- Both routes end in the contact process. Sulfur dioxide is oxidised on a vanadium catalyst with the oxygen of the process air from ATMOS, and the trioxide is absorbed in well water from GW_INTAKE (ULLMANN_H2SO4).
- The driver `h2so4_route` selects the source of the sulfur dioxide, with two routes of different technology:
  - GYPSUM_LOOP, the default, reduces the anhydrite cake of HF_GEN with plant char from OIL_PYRO in a small electrically heated kiln. The sulfur the kiln does not recover is made up with native sulfur, a raw ore taken at the dock. The lime residue leaves at the dock as a byproduct.
  - SULFUR_ORE burns native sulfur ore only. The cake kiln and its streams are retired, and the cake leaves at the dock as before.
- The streams of the route not selected are marked retired, so no route without flow is left on the graph.
- The only feedstock taken at the dock is native sulfur, a raw ore (stream IA-SULFUR-MU).
- The new drivers and the reaction heat are recorded in A-M-421. The POLYMERS line sizing page is at revision C, with a new section 4.1 that compares both routes.
- The new unit has a system-tree entry, a material selection, instrument loops and sizing coverage.

## Owner choice left open

The cake kiln is rated for continuous duty, so the shell loss of the hot tube is most of its load. Running it in campaigns from a cake store would cut that load. The choice between GYPSUM_LOOP and SULFUR_ORE, and between continuous and campaign duty, is left to the owner. Both are a driver change.

## Values

| Quantity | Before | After |
|---|---|---|
| IA-H2SO4-MU, acid from the dock | 0.4038 kg/d | retired |
| IA-H2SO4-ACID, acid from ACID_PLANT | none | 0.4038 kg/d |
| IA-GYPSUM-SHIP, cake to the dock | 0.5756 kg/d | retired on GYPSUM_LOOP |
| IA-SULFUR-MU, native sulfur ore | none | 0.0185 kg/d |
| CHAR_TO_ACID, plant char | none | 0.0244 kg/d |
| IA-LIME-SHIP, lime residue byproduct | none | 0.2987 kg/d |
| IA-CHAR, shop char by difference | 4.8613 kg/d | 4.8369 kg/d |
| ACID_PLANT electrical load | none | 0.9654 kW |
| PV continuous rating | 351.3442 kW | 352.3096 kW |
| ZNBR2 battery | 217.5226 kW | 218.4826 kW |
