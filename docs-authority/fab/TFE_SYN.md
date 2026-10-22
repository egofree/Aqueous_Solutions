# TFE_SYN fabrication

Envelope 600 x 600 x 1200 mm (reactor-class study minimum, AQS-DUTY-073; A-M-283). Atmospheric
at the datum; design pressure unevaluated until the unit task 07 relief case issues.

Production route (MFG/FAB, in-house, X-MFG-31):
1. R-22 pyrolysis furnace: Inconel 600 tube in a heated block to 750 C (graph design; ULLMANN_HF
   route chemistry). No silica-bearing packing in contact with the pyrolysis gas.
2. Quench: immediate quench coil, freshwater side, sized per the 0.10 kg/d TFE duty; the
   autopolymerisation hazard tune stays on the ULLMANN_FLUOROPOLY note (wet quench straight out
   of the hot zone; no hold-up volume).
3. Coolers and scrub: Hastelloy C-276 coolers, PTFE-lined scrubber vessel to ACID_POLISH_SCRUB.
4. Heater circuit: 750 C band from the graph duty; interlocks: high temperature, high pressure,
   low quench flow (work order 3).
5. Test: inert pressure hold per AQS-STD-001 sec. 4, then the route trial per AQS-DUTY-073
   sec. 3-4.

Inspect against models/mfg/TFE_SYN/export/tfe_syn.step. Not stamped. Production rate stays 0.0
(feed-blocked, A-M-267: no fluorine source on site, Q-013); design case tfe_kg_d 0.10 with the
per-kg tables in AQS-DUTY-073.
