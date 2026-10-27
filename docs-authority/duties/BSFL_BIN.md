# BSFL_BIN

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 8.215 kg/d. Mass out 8.215 kg/d. Electrical duty 0.0000 kW. In: CHICK_MANURE 3.208 kg/d (poultry manure to the larvae bin); FISH_SLUDGE 3 kg/d (fish sludge to the larvae bin); GALLEY_BIO 0.5 kg/d (galley biowaste to the larvae bin); DUCK_MANURE 1.44 kg/d (duck manure to the larvae bin); 1 more. Out: FRASS 0.4929 kg/d (frass compost to the solids line); BSFL_VAP 7.243 kg/d (bin respiration/evaporation); LARVAE_FRESH 0.479 kg/d (fresh larvae to the formulation drier).

2. Size.
- Graph design (AQS-PAR-001 sizing): service BSFL larvae composting bin; feedstock_kg_d 1.43; larvae_kg_d 0.114; frass_kg_d 0.357; basis A-M-418 (X-FARM-03); organisms Hermetia illucens (black soldier fly) larvae: 5 instars, 14-18 d at 25-30 C; adults do not feed or bite; conversion 1.4-2.0 kg wet biowaste per kg fresh larvae (TECHTREE insect-farming); substrate moisture 65-75 %; heat the larvae mass generates metabolic heat (the bin self-heats; above 40 C kills the larvae).

3. Material. HDPE tray bin, PP larval self-harvest ramp, SS316 mesh screen; no metal below the substrate line. Basis: substrate goes pH 4-6 under frass acids at 65-75 % moisture with self-heating toward 40 C (graph design; A-M-418): wet acid compost pits zinc and plate steel, HDPE/PP are inert across the whole range Alternative: FRP tray if bin scaling raises wall temperatures past the HDPE class. larvae harvest is by self-separation up the ramp; the mesh is the pupa screen. (X-FARM-03)

4. Nozzles. Schedule at `nozzles/BSFL_BIN.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops BSFL_BINTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
