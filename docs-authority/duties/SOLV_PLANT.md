# SOLV_PLANT

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.8103 kg/d. Mass out 0.8103 kg/d. Electrical duty 0.0296 kW. In: IA-LITHO-OUT 0.3395 kg/d (spent resist and solvent); IA-SOLV-SPENT 0.1995 kg/d (segregated spent solvent from the bench rinse drain); IA-SOLV-MEOH 0.1443 kg/d (plant methanol for the carbonylation); IA-SOLV-CO 0.1261 kg/d (chlorinator carbon monoxide for the carbonylation); 1 more. Out: IA-SOLV-PLANT 0.5195 kg/d (recovered and new ethanol and acetone to the solvent store); IA-SOLV-BTMS 0.1409 kg/d (still bottoms (resist residue and heavy alcohols) to the light oil cut); IA-SOLV-VENT 0.1499 kg/d (reactor or fermenter off-gas (fuel-gas class export)).

2. Size.
- Graph design (AQS-PAR-001 sizing): route MEOH_CO; bench_kg_d 0.21; spent_kg_d 0.1995; recovered_kg_d 0.1895; make_kg_d 0.02047; acetone_kg_d 0.01024; ethanol_kg_d 0.01024; meoh_kg_d 0.02046; co_kg_d 0.01789; h2_kg_d 0.000995; fw_kg_d 0; stillage_kg_d 0; butanol_kg_d 0; vent_kg_d 0.01887; btms_kg_d 0.009974; product_kg_d 0.21; kw 0.01034; kw_still 0.009443; kw_rx 0.000901.
- Node note: Solvent plant (A-M-428).

3. Material. 316L batch still, reboiler and receivers; Hastelloy C-276 carbonylation autoclave for the iodide-promoted acetic acid step; 316L ketonisation and hydrogenation tube reactors; on the fermentation route, HDPE fermenters, nitrogen-blanketed. Basis: Ethanol and acetone at their boiling points in the still, and acetic acid with an iodide promoter at 150-200 C in the carbonylation (A-M-428, flow_graph/param/solvent.py): stainless steel serves the solvents and the dry reactor gases, while hot acetic acid with iodide needs a nickel-molybdenum alloy (ULLMANN_ACETIC; PERRY9_MAT). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: Zirconium for the carbonylation autoclave if iodide corrosion of C-276 is seen in service. wetted by ethanol, acetone and hot acetic acid with an iodide promoter; iodide pitting of the carbonylation vessel is the corrosion load. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/SOLV_PLANT.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Vent edge IA-SOLV-SPENT and IA-SOLV-PLANT and IA-SOLV-VENT on the graph (to NORTH_DOCK and SOLV_PLANT and WS_SOLV). Atmospheric operation is not claimed beyond this edge. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
