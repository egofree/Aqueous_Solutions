# ACID_PLANT

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.7724 kg/d. Mass out 0.7724 kg/d. Electrical duty 0.2061 kW. In: IA-SULFUR-MU 0.01294 kg/d (native sulfur (raw ore) for the acid plant); IA-GYPSUM-REGEN 0.5756 kg/d (HF kiln anhydrite cake to the sulfur-recovery kiln); CHAR_TO_ACID 0.02566 kg/d (plant pyrolysis char reductant for the cake kiln); IA-ACID-O2 0.07746 kg/d (oxygen of the process air (sulfur burning and SO2 oxidation)); 1 more. Out: IA-ACID-CO2 0.08687 kg/d (carbon dioxide and water vapour of the cake kiln); IA-LIME-SHIP 0.2817 kg/d (cake-kiln residue (lime, unreacted anhydrite and fluorspar) beyond the NAOH_PLANT lime make-up); IA-H2SO4-ACID 0.4038 kg/d (98 wt% sulfuric acid to the HF kiln); IA-LIME-TO-PCA 3.8e-05 kg/d (cake-kiln lime residue to the slaker).

2. Size.
- Node note: Sulfuric acid plant (A-M-421).
- Sizing calculation pending (unit task 02). The graph node carries no design and no envelope.

3. Material. Cake kiln tube of Inconel 600 with an alumina lining and mineral-wool insulation; sulfur burner and converter shell of aluminised carbon steel with vanadium catalyst beds; absorber and product acid tank of carbon steel with PTFE-lined nozzles; dilution cooler of high-silicon iron. Basis: Hot sulfur dioxide and trioxide gas, dry, up to about 1150 C in the cake kiln and about 600 C in the converter, and 98 wt% sulfuric acid near ambient (A-M-421, flow_graph/param/sulfuric.py): strong acid above 93 wt% is carried in carbon steel at low velocity, while hot or dilute acid needs high-silicon iron, alloy or PTFE lining (ULLMANN_H2SO4; PERRY9_MAT). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: Alloy 20 or PTFE-lined steel for the absorber if the acid strength falls below 93 wt% in service. wetted by 98 wt% sulfuric acid and dry sulfur oxides; dilution below 93 wt% is the corrosion load, held by the absorber control. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/ACID_PLANT.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
