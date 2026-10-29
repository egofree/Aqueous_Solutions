# SI_REFINE

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0.4854 kg/d. Mass out 0.4854 kg/d. Electrical duty 0.5659 kW. In: IA-SI-MG 0.2717 kg/d (metallurgical-grade silicon); IA-CL2-SIREF 0.2137 kg/d (chlorine make-up of the chlorosilane loop). Out: IA-SI-PURGE 0.259 kg/d (impurity chlorides and silicon tetrachloride bleed); IA-SI-EG 0.2264 kg/d (electronic-grade silicon for the CZ charge).

2. Size.
- Node note: Electronic-grade silicon refining (A-M-419).
- Sizing calculation pending (unit task 02). The graph node carries no design and no envelope.

3. Material. Nickel 200 hydrochlorinator and trichlorosilane distillation column, dry service; 316L chlorosilane and hydrogen chloride piping kept dry; Siemens bell jar of 316L with a cooled wall and high-purity silicon rods on graphite chucks (or a silicon-lined fluidised bed on the silane route). Basis: Dry chlorosilanes, hydrogen chloride and hydrogen at up to about 300 C in the hydrochlorinator and a cooled wall round rods at about 1100 C (A-M-419, flow_graph/param/si_refine.py): dry hydrogen chloride and chlorosilanes are carried in nickel and stainless steel, and any moisture makes hydrochloric acid, so the loop is kept dry (ULLMANN_HCL; PERRY9_MAT). The product-contact parts are silicon or graphite so the charge stays at electronic grade. Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: Hastelloy C-276 for the purge and condensate lines if moisture ingress cannot be excluded. wetted by dry chlorosilanes; moisture is the corrosion load, controlled by the dry loop. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/SI_REFINE.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
