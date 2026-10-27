# AQUA_UV

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.0400 kW. In: AQUA_NUT 0 kg/d (nitrified water to the optional sanitizer (NO3- passes; sloughed cells die in food-safety mode)). Out: AQUA_SAN 0 kg/d (sanitized loop water to the growbeds (food-safety/contingency mode)).

2. Size.
- Sizing study pending (study): loop_kg_d 40; basis A-M-415 loop rate.
- Graph design (AQS-PAR-001 sizing): service optional UV-C 254 nm loop sanitizer between the biofilter and the growbeds; AQUA_BYPASS normally engaged; basis A-M-428; A-M-427 (food-safety mode); TECHTREE agriculture.aquaponics (produce food-safety note); why_it_works the nitrifying biofilm lives on the moving-bed media: post-media sterilization passes the nitrates and kills only sloughed/free cells; modes normal = bypassed (growbed rhizosphere needs its microbial feed); food-safety mode = inline (A-M-427 greens/harvest); contamination response = inline; ozone_contingency deep-clean with ozone fed from CRYO_O2, fish isolated, never in-line live: residual ozone is lethal to gills and biofilm; dose_class 254 nm, 30-100 mJ/cm2 class for the loop flow; the 40 kg/d loop is trivial flow for a 0.04 kW lamp; failure_mode lamp depletion or sleeve fouling: dose decays silently - the X-FARM-12 validation test is periodic, not one-shot.

3. Material. SS304 reactor tube with a quartz UV sleeve, PP loop fittings, EPDM gasket class. Basis: loop-water service at aquaponic temperature (A-M-428): 304 tube with the lamp isolated behind quartz; the unit is normally bypassed, so wetted-time is intermittent Alternative: 316L tube if the loop ever runs saline (it does not at the freshwater class). quartz sleeve fouling is the maintenance item - the dose validation (X-FARM-12) covers it. (X-FARM-12)

4. Nozzles. Schedule at `nozzles/AQUA_UV.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops AQUA_UVFIT-01, AQUA_UVPT-01, AQUA_UVTE-01, AQUA_UVUVT-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
