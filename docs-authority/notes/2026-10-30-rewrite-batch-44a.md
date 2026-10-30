# Rewrite batch 44a: the gas and hydrogen routes without flow

Date: 2026-10-30

## Change

Task X-RTE listed seven gas and hydrogen routes that carry no flow. Each is decided by the owner rule of 2026-10-29, and the basis is A-M-434.

### Routes retired

- IA-EW1-H2 and IA-EW2-H2: the cathode hydrogen of EW_1 and EW_2 leaves by Faraday on IA-HDR-H2-01 and IA-HDR-H2-03, so these hood stubs duplicate them.
- IA-FC-EXH: the methanol cell burns its fuel completely on stoichiometric oxygen. Its water leaves on S81 and its carbon dioxide on S82, so no exhaust remains. If the owner sets the cell oxidant above stoichiometric, which is an O2 ownership decision, the excess oxygen needs this route again.
- IA-H2-AIR: H2_DRYER is fed only by header hydrogen, so it has no sweep air to pass. Hood sweep air is kept out of the hydrogen line.
- IA-LEACH-ASU: the leach has no degasser or compressor to send dissolved gas to the cold box, and its closure T5 in `balance.py` solved to zero. T5 now runs only while the route is present.
- S18: the afterburner carbon dioxide reaches the cold box on S67 and S67B through FLUE_KO, so this claim id duplicates them.

### Route left listed

IA-H2P-H2O, the TSA regeneration condensate, would carry real flow. The cathode hydrogen leaves the EW cells saturated with water, and the cathode edges state 2 % water in their composition but carry only the Faraday hydrogen in their rate. Carrying that water is a change to the EW cathode hydrogen, which the owner holds, so the route is listed under X-RTE-HELD with this reason.

## Check

With the six routes retired, the reconciliation fit moves no edge and the unit residuals are unchanged.
