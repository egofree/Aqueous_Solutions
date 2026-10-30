# Rewrite batch 42b: magnesium alloying of the aluminium line

Date: 2026-10-30

## Change

The owner decision of 2026-10-30 gives MG_POT_TO_IND flow as magnesium alloying for the aluminium line, with the magnesium sourced recovery first and recorded in the recovery inventory. Task X-RTE-MG_POT_TO_IND is done.

- The cast aluminium line is alloyed to the A356 class, set by the driver al_mg_alloy_wt. The alloy magnesium stays in the aluminium as it goes round the shop-scrap loop, so it is recovered with the scrap. MG_POT makes up only the share that oxidises to the dross in each remelt, set by al_mg_melt_loss_frac.
- The magnesium chloride salt flux was lost with the dross to the leach. It is now recovered from the dross salt cake by water leach and evaporation and returns to MG_POT on IA-FLUX-SALT-REC, set by flux_salt_recovery_frac. The dock CaCl2-MgCl2 brine, a mining-waste stream, covers only the shortfall and falls.
- The chlorine freed by the alloy magnesium leaves on IA-CL2-MG-SHIP with the pot chlorine class, because the Kroll chlorinator already takes its full draw.
- MG_POT has a magnesium record in the recovery inventory. The record names the remelt oxide and the salt left in the washed cake as unrecovered, with the basis.
- The reference ASM_V15_AL is added. The basis is recorded in A-M-430.

## Values

| Quantity | Before | After |
|---|---|---|
| MG_POT_TO_IND, alloy magnesium | 0 | 0.0056 kg/d |
| IA-FLUX-SALT-REC, salt recovered from the dross | none | 0.0318 kg/d |
| IA-MGCL2-MU, dock brine | 0.0398 kg/d | 0.0299 kg/d |
| IA-CL2-MG-SHIP, chlorine to the dock | none | 0.0163 kg/d |
| FOUNDRY_SLAG_TO_LEACH | 0.3565 kg/d | 0.3302 kg/d |
