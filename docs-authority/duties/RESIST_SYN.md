# RESIST_SYN

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 1.567 kg/d. Mass out 1.567 kg/d. Electrical duty 0.0037 kW. In: IA-RESIST-BZ 1.005 kg/d (C5-C10 cut to the benzene extraction); IA-RESIST-NAPH 0.3664 kg/d (C11-C18 cut to the naphthalene extraction); IA-RESIST-MEOH 0.005938 kg/d (plant methanol for the formaldehyde); IA-RESIST-NH3 0.001314 kg/d (ammonia for the nitrous acid and the ester scavenger); 6 more. Out: IA-RESIST-RAFF 1.35 kg/d (aromatic-extraction raffinate back to the fractionator); IA-RESIST-VENT 0.08414 kg/d (oxidation off-gas: nitrogen, unused oxygen and carbon dioxide); IA-RESIST-HCL 0.000938 kg/d (phosgenation HCl to the chlorate finish); IA-RESIST-BRINE 0.01135 kg/d (reaction water, acid water and ammonium chloride); 1 more.

2. Size.
- Graph design (AQS-PAR-001 sizing): route DNQ_NOVOLAC; starts_d 5; coats_d 40; resist_kg_d 0.12; solids_kg_d 0.03; daa_kg_d 0.09; rinse_kg_d 0.2195; novolac_kg_d 0.02403; dnq_kg_d 0.006; bz_cut_kg_d 1.005; naph_cut_kg_d 0.3664; benzene_kg_d 0.01809; naphthalene_kg_d 0.003297; raff_kg_d 1.35; meoh_kg_d 0.005938; nh3_kg_d 0.001314; h2_kg_d 0.0001037; co_kg_d 0.0007206; cl2_kg_d 0.001824; acid_kg_d 0.002575; acetone_kg_d 0.09; air_kg_d 0.09256; vent_kg_d 0.08414; hcl_kg_d 0.000938; brine_kg_d 0.01135; kw 0.003656.
- Node note: Photoresist synthesis (A-M-432).

3. Material. Glass-lined steel batch reactors for the oxychlorination, nitrosation, diazotisation and esterification; 316L for the formaldehyde and ammonia oxidisers, the novolac kettle and the solvent steps; Monel 400 for the dry phosgene and chlorine lines. Basis: Wet HCl, nitrous acid and sulfuric acid at up to 100 C in the naphthol and diazonaphthoquinone steps, and phenol, formaldehyde and acetone in the novolac and formulation steps (A-M-432, flow_graph/param/fab_resist.py): glass lining serves the wet acid chlorides, stainless steel the organics and the dry gases, and nickel-copper alloy the dry chlorine and phosgene (PERRY9_MAT). Selection per AQS-STD-002 with the duty section 2 environment (X-MAT-22). Alternative: Hastelloy C-276 reactors if the glass lining is chipped in service. wetted by hot wet HCl, nitrous and sulfuric acids, phenol and acetone; chloride attack of any bare stainless steel is the corrosion load. (X-MAT-22)

4. Nozzles. Schedule at `nozzles/RESIST_SYN.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Vent edge IA-RESIST-ACET and IA-RESIST-VENT on the graph (to ATMOS and RESIST_SYN). Atmospheric operation is not claimed beyond this edge. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Sizing calculation pending (unit task 02). Material selection pending (unit task 09). No instrument loop yet (unit task 08). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
