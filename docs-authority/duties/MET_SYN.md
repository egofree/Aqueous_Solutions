# MET_SYN

Standard: AQS-STD-001 Rev A. Graph Rev AC. Study. Not a PE stamp.

1. Basis. Mass in 0 kg/d. Mass out 0 kg/d. Electrical duty 0.2000 kW. In: IA-MEOH-CH3SH 0 kg/d (methanol feed to the methyl-mercaptan synthesis (trace)); IA-H2S-CH3SH 0 kg/d (H2S feed to the methyl-mercaptan synthesis (trace)); IA-NH3-MET 0 kg/d (ammonia feed to the Strecker step (trace)). Out: DL_MET_TO_FEED 0 kg/d (DL-methionine crystals: top-dressed supplement at the point of feeding).

2. Size.
- Sizing study pending (study): throughput_g_d 9; power_kW 0.2; basis bench-scale glass-lined reactor column + reagent feed tanks + crystalliser; the scale is trivial (9 g/d vs the tonne/y industrial class) - the complexity is the three-step sequence, not the throughput.
- Graph design (AQS-PAR-001 sizing): service DL-methionine synthesis (the three-step Strecker route): CH3SH + acrolein -> MMP; MMP + NH3 + HCN -> aminonitrile; hydrolysis -> DL-Met; basis A-M-416 route A close-out (2026-10-28): the no-import-feed rule requires on-site synthesis; TECHTREE poultry.chickens.md: synthetic DL-methionine is the standard supplement class; chemistry step 1: CH3OH + H2S -> CH3SH (K2O/Al2O3, 350 C); step 2: CH3SH + acrolein -> MMP (base-catalysed Michael addition); step 3: MMP + NH3 + HCN -> aminonitrile; hydrolysis -> DL-Met (Strecker); throughput_g_d 9; precursor_chain CH3OH from MEOH_SYNTH; H2S from BLACK_DIGEST; NH3 from WS_AMMONIA; acrolein from the olefin line; HCN from the Andrussow reaction (CH4 + NH3 + O2) at the gram/d scale; product DL-methionine crystals to the FEED_PREP formulation (A-M-426).

3. Material. Borosilicate glass-lined reactor column, PTFE-lined transfer lines, SS304 reagent feed tanks, Hastelloy C crystalliser. Basis: the three-step Strecker carries HCN, acrolein and methanethiol - all aggressive at the reagent class (A-M-416): glass-lined for the reaction column, PTFE for the transfer, Hastelloy C for the acidic hydrolysis/crystallisation Alternative: a tantalum reactor if the HCN service ever shows corrosion at the glass-lining pinholes. the crystalliser is the product-quality bottleneck: DL-Met crystal habit controls the filtration rate. (X-UI-002)

4. Nozzles. Schedule at `nozzles/MET_SYN.csv` (unit task 04): one row per process connection (mass kg/d and heat-loop kW edges), service text matching the edge `carries`. Bore is the AQS-PIP-004 line DN (AQS-PIP-003: the piped bore is the nozzle bore basis); bores are not recalculated here. Elevations are the schedule placeholders pending vessel design (unit tasks 02/06).

5. Instruments. No instrument loop for this unit in AQS-CTL-001 yet (unit task 08). No trip is specified.

6. Relief. Relief case study pending (unit task 07). No set point is claimed on this page. Not to the room.

7. Code. Shop, not stamped (AQS-STD-001 section 7 shop rule). No CAD envelope issued yet.

8. Open items. Material selection pending (unit task 09). No instrument loop yet (unit task 08). Relief case pending (unit task 07). Nozzle elevations are schedule placeholders, not designed elevations (unit tasks 02/06).
