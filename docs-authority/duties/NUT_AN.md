# NUT_AN

Standard: AQS-STD-001 Rev A. Graph Rev AD. Study. Not a PE stamp.

1. Basis. Mass in 4.107 kg/d. Mass out 4.107 kg/d. Electrical duty 0.0600 kW. In: IA-NUT-NH3 0.2305 kg/d (ammonia liquor to the nitrate skid (Ostwald feed and the neutralization base)); IA-NUT-O2 0.4331 kg/d (plant oxygen for the ammonia oxidation); IA-NUT-H2O 3.443 kg/d (dilution water to the dosing strength). Out: NUT_AQUA 4.087 kg/d (ammonium-nitrate nutrient solution to the raceway (on-site skid, X-QA-11)); IA-NUT-VENT 0.01991 kg/d (unconverted slip to the NOx scrubber (its nitrate liquor feeds NUTRIENT_DOSE)).

2. Size.
- Graph design (AQS-PAR-001 sizing): gap_N_kg_d 0.1839; an_kg_d 0.5255; dose_kg_d 4.087; nh3_kg_d 0.2305; o2_kg_d 0.4331; rxn_h2o_kg_d 0.1183; dil_kg_d 3.443; vent_kg_d 0.01991; kw 0.06.
- Node note: Ammonium-nitrate nutrient skid (A-M-497).

3. Material. 310S reactor tube and hot-bed hardware around the platinum gauze catalyst bed on the dry NH3/O2 oxidation side, the gas held above the acid dew point to the absorption sump, with a dielectric break to the wet train; PVC-U ammonia and dilution-water legs; PVDF (P3) absorption and neutralization vessel, dosing pump and product leg on the ammonium-nitrate side; FKM gaskets. Basis: Ostwald-class oxidation of plant ammonia with plant oxygen, the acid neutralized back with ammonia to the dosing strength (graph design; A-M-497): the bed runs hot and dry, so the reactor tube takes the house 310S hot-face class of the issued COMB_HEAT burner tube (M7 dry hot gas held above the acid dew point; the case is stated per M7 and isolated from any electrolyte per M6); the wet train is nitric at the absorption class, an M3 oxidizing service with no metal wetted part - PVC-U legs and PVDF absorber and pump per section 5 (nitric at no more than 2 M). Selection per AQS-STD-002 with the duty section 2 environment (X-QA-11). Alternative: nickel-alloy (Alloy 600 class) reactor tube if the bed duty moves above the 310S class; borosilicate glass 3.3 absorption if the nitrate liquor ever concentrates past the PVDF class (M5: glass or a lined part, never bare metal). the unconverted slip vents to NOX_SCRUB on the issued scrubber family and its nitrate liquor stays a booked nutrient; the gauze change-out is a unit task 12 work order; no corrosion allowance claimed - no measured rate. (X-QA-11)

4. Nozzles. Schedule at `nozzles/NUT_AN.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Vent edge IA-NUT-VENT on the graph (to NOX_SCRUB). Atmospheric operation is not claimed beyond this edge. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
