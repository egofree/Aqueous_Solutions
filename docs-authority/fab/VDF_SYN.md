# VDF_SYN fabrication

Envelope 600 x 600 x 1200 mm (reactor-class study minimum, AQS-DUTY-073; A-M-283). Atmospheric
at the datum; design pressure unevaluated until the unit task 07 relief case issues.

Production route (MFG/FAB, in-house, X-MFG-31):
1. Chlorination and hydrofluorination reactors: Hastelloy C-276 welded vessels with PTFE-lined
   cooler coupons (duty sec. 3, ULLMANN_FLUOROPOLY route); DN15/25 nozzles per nozzles/VDF_SYN.csv.
2. 142b cracking furnace: nickel cracking tube in a heated block to 650 C, charged with the
   Cr2O3-class catalyst (ULLMANN_FLUOROPOLY); immediate quench side to the scrub.
3. Heater circuits: chlorination 350 C, cracking 650 C bands from the graph design duty 0.5128 kW.
4. Scrub and HCl return: PTFE-lined cooler, dilute HCl return pump module to CRU.
5. Interlocks: high temperature per stage, high pressure, low circulation flow (work order 3).
6. Test: inert pressure hold per AQS-STD-001 sec. 4, then the route trial per AQS-DUTY-073
   sec. 3-4.

Inspect against models/mfg/VDF_SYN/export/vdf_syn.step. Not stamped. Production rate stays 0.0
(feed-blocked, A-M-267: no fluorine source on site, Q-013); design case vdf_kg_d 0.15 with the
per-kg tables in AQS-DUTY-073.
