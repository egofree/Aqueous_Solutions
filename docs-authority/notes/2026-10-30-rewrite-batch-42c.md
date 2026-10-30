# Rewrite batch 42c: two chlorine sources for the monomer reactors

Date: 2026-10-30

## Change

The owner decision of 2026-10-30 builds both designs of AL_POT_CL2 behind a driver, with the default chosen on the merits. Task X-RTE-AL_POT_CL2 is done.

- The VDF and TFE reactors draw chlorine from CRU and return dilute HCl to it. The driver cru_cl2_source selects where that chlorine comes from.
- HCL_OX, the default: CRU oxidises the returned HCl with the chlorate liquor, so the halogen loop closes inside the plant. The values of the plant do not change. AL_POT_CL2 stands by at its rated case.
- POT: AL_POT_CL2 carries the monomer chlorine from the byproduct chlorine of AL_POT, which the dock exports on IA-CL2-SHIP. The export falls by the same amount, and the HCl returns pass unoxidised to the leach.
- HCL_OX is the default because it turns a plant waste, the returned acid, back into chlorine. On the POT route that acid would reach the leach, and the sodium hydroxide neutralisation would have to absorb it. POT stays built as the backup for an outage of the chlorate finish.
- `flow_graph/param/foundry_poly.py` records the AL_POT chlorine before the draw on IA-CL2-SHIP, so the POT draw is taken from it once per pass. The basis is recorded in A-M-431.
