# AQUA_TANK fabrication

Class: fish_tank; sector FARM. Study route. Not stamped.
Envelope: Envelope 2100×1100×1100 mm;
service line: service aquaponic fish tanks, 60 kg standing stock; stock_kg 60; ration_kg_d 0.9; basis A-M-415 (X-FARM-01); ammonia_load fish excrete NH3/N

Internals: issued mfg model BOM (1 internals part row): "2,liner,1,HDPE,2230.4,make,tank class; 2.0 m3 working volume at the 60 kg stock / 30" [models/mfg/AQUA_TANK/bom.csv]
Material: HDPE tank body with a food-grade LDPE aquaculture liner, SS316 hardware above the waterline, CPVC loop fittings. Basis: the tank holds the fish stock in the RAS loop at 26-28 C (graph design; A-M-415): ichthyotoxicity governs the wetted set, so Cu/Zn/brass are excluded outright; the liner is the aquaculture food-contact class over the 2.5 m3 envelope (203.8 kg/d loop). (continues on the duty sheet)

Nozzles: 8 process connections per docs-authority/nozzles/AQUA_TANK.csv

Production route (issued ahead of the CAD build; fabrication does not start before unit
tasks 10-12 close; the section 3 material selections are issued per AQS-STD-006):
1. Assembly route: per the unit duty sheet size line, standard first-stage parts.
2. Working parts per the duty sheet; the part set is the unit task 10-12 deliverables.
3. Connections: nozzle stubs to the schedule; flange faces per AQS-PIP-003 class letters
4. Test: hydrostatic/water-fill and pressure hold per AQS-STD-001 section 4; dry-run only until
    the CAD acceptance (AQS-PLAN-006 M3) and the real BOM land.
