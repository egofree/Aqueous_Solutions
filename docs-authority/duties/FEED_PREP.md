# FEED_PREP

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 43.92 kg/d. Mass out 43.92 kg/d. Electrical duty 0.6000 kW. In: DUCK_FORM 43.38 kg/d (fresh duckweed to formulation (layers + quail + reserve draw)); EGGSHELL_RET 0.06 kg/d (baked crushed eggshell return (38 g Ca/d)); LARVAE_FRESH 0.479 kg/d (fresh larvae to the formulation drier). Out: LAYER_FEED 4.168 kg/d (formulated layer ration); QUAIL_RATION 1.667 kg/d (formulated quail ration); DUCK_STORE 0.5 kg/d (dried duckweed to the dry reserve); FORM_REJECT 0.06667 kg/d (screenings/fines back to the larvae bin); 3 more.

2. Size.
- Sizing study pending (study): throughput_kg_d 2.54; basis A-M-426 driver arithmetic.
- Graph design (AQS-PAR-001 sizing): service ration formulation: duckweed + larvae meal + recycled eggshell; HP drier on the storage draw only; basis A-M-426; A-M-416 (no imported grain); TECHTREE insect-farming (black-soldier-fly meal milling class); fresh_first fish and ducks eat the harvest wet; drying serves only the A-M-270 dry-reserve draw (0.5 kg/d); methionine the binding supplement (~9 g/d DL-met equivalent at 4-crew; TECHTREE poultry.chickens: synthetic DL-methionine is the standard supplement class); ca_source recycled eggshell 38 g Ca/d + BSFL Ca 5-8 % (TECHTREE insect-farming) + mineral CaCO3 top-up ~1.5-2 kg/month from the site mineral line (TECHTREE poultry.chickens: crushed limestone free-choice class); food_safety larvae meal routes to POULTRY ONLY, never to the fish: manure-fed larvae are the pathogen bridge the aquaponic produce path must not carry (TECHTREE agriculture.aquaponics food-safety note).

3. Material. SS304 contact surfaces and mixing troughs, PP feed bins, quartz-sleeve drier ducting; no copper-bearing alloys on any feed path. Basis: food-contact sanitation class for the animal ration line (A-M-426): 304 at the chloride-light service, PP bins resist the wet duckweed; Cu is excluded from every feed path outright Alternative: SS316 where the eggshell grinding dust ever shows pitting. the reject stream returns to the BSFL bin, so the contact surfaces serve both feeds. (X-FARM-10)

4. Nozzles. Schedule at `nozzles/FEED_PREP.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops FEED_PREPPSH-01, FEED_PREPPT-01, FEED_PREPTE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet. Manufacturing model `models/mfg/FEED_PREP/draw_feed_prep.py` (AQS-PLAN-006).

8. Open items. Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
