# QUAIL_CAGE

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 1.902 kg/d. Mass out 1.902 kg/d. Electrical duty 0.0000 kW. In: QUAIL_H2O 0.2 kg/d (quail water); QUAIL_RATION 1.667 kg/d (formulated quail ration); CA_HOPPER 0.035 kg/d (mineral calcium carbonate (free-choice hopper)). Out: QUAIL_EGGS 0.06 kg/d (quail eggs to the food store); QUAIL_DROP 1.75 kg/d (quail droppings to the vermi bin); QUAIL_VAP 0.09167 kg/d (cage evaporation).

2. Size.
- Graph design (AQS-PAR-001 sizing): service coturnix quail cage bank, 20 hens; stock 20; egg_kg_d 0.06; ration_kg_d 0.5; basis A-M-422 (X-FARM-06).

3. Material. Hot-dip galvanised weld-wire cage battery, PP feeders, SS316 nipple waterers. Basis: dry droppings-tray service at the 20-hen Coturnix unit (graph design; A-M-422): HDG weld wire is the cage-battery standard; the only wet points are the nipples, so those alone are stainless Alternative: PVC-coated wire if foot dermatitis ever shows at the cage floor. the droppings tray feeds the vermi bin directly. (X-FARM-06)

4. Nozzles. Schedule at `nozzles/QUAIL_CAGE.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. Loops QUAIL_CAGETE-01 in AQS-CTL-001. What trips is stated on the loop.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
