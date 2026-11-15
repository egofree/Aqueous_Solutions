# X-QA-11 dock-import round — 2026-11-15

Working note; the X-QA-11 evidence for the task plan's consolidation pass.

## What landed

The remaining pending dock imports of the recovery gate (`flow_graph/param/recovery.py`
PENDING, task X-QA-11) retired on on-site routes, the X-QA-19 way: sized first, registered,
then the import removed. Six pending entries left the table. Per import:

1. **IA-CACL2-MU / IA-MGCL2-MU** (CaCl2/MgCl2 brine make-up of the foundry pots, A-M-284):
   recovered on site by BRINE_CRYS (`flow_graph/param/salt_recovery.py`), an agitated flash
   crystallizer on a 2 kg/d leach-liquor side-stream (`brine_crys_feed_kg_d`), feeding the pots
   at the unchanged rates (CaCl2 0.116115 kg/d, MgCl2 0.039782 kg/d) and returning the mother
   liquor to the leach. Basis (A-M-496): the MgCl2 make-up is the Kroll drag-out cycling
   flux -> melt -> slag -> leach; the Ca ends the day as CaCl2 in the dross and liquor; the HCl
   leach also dissolves the feed's silicate-oxide class, so the liquor carries the make-up
   many times over. Heater load driver `brine_crys_kW` 0.07 kW.
2. **NUT_AQUA / NUT_AQUA_BED** (raceway/bed mineral nitrate, A-M-430): the dose is computed
   from the crop uptake at the registered N classes (`FARM.duckweed.dm_N_wt` 5.5 %,
   `FARM.classes.bed_greens_dm_frac` 5 %) less the fish-loop return
   (`FARM.aquaponics.fish_N_return_g_d` 13.5 g/d), and made on the NUT_AN ammonium-nitrate skid
   (`flow_graph/param/nitrate_route.py`, net 2 NH3 + 2 O2 -> NH4NO3 + H2O, Ostwald class,
   selectivity driver 0.97, slip to NOX_SCRUB). NUT_AQUA re-points to the skid at the computed
   dose; NUT_AQUA_BED retires because the fish return covers the bed uptake and the loop passes
   the beds before the raceway (A-M-497).
3. **IA-WAX-MU** (pattern wax, A-M-286): the 0.2 kg/d make-up draws from the plant C19-C28 cut
   tank on IA-WAX-CUT and the draw nets off IA-C19-SHIP in ess_tf.py; the dock import retires
   (A-M-498).
4. **IA-FEED-MU** (feedstock make-up, A-M-460): re-classed raw_ore on the characterized lot
   (recovery.py ORE, element Fe at `feed_fe_assay_frac` 0.25, AQS-ASSAY-001 sections 3/7) with
   a recovery record on HOPPER that recovers the feed iron first from the loop receipts
   (A-M-499).

## The last two (same day, follow-up round)

7. **CA_HOPPER** (livestock CaCO3 grit, 0.035 kg/d): the galley shell return
   (EGGSHELL_RET, baked crushed eggshell, ~38 g Ca/d basis) splits at FEED_PREP -
   SHELL_GRIT 0.035 kg/d feeds the free-choice quail hopper, the balance stays in the
   layer-mash shell share inside the A-M-426 in-class Ca margin (A-M-501). The dock
   mineral line CA_HOPPER retires.
8. **FR_FINISH** (phosphorus-FR textile finish, 0.0017 kg/d compound): the fab
   phosphorus line's H3PO4 (WS_PHOS product S34B) neutralized with the ammonia line -
   H3PO4 + 2 NH3 -> (NH4)2HPO4 at the A-M-225 pick-up, mass-exact on the element-mass
   table; the draws ride IA-FR-P (0.001261 kg/d) and IA-FR-NH3 (0.000438 kg/d) and the
   dock reagent line FR_FINISH retires (A-M-502). At locales without the phosphorus or
   ammonia line the textile runs unfinished and the demand retires with the line.

The PENDING table stands empty. The mars O2-ledger case landed in o2_close the same
round: the NFPA 110 exercise rides the FUEL_CELL replacement at locales that eliminate
BACKUP_GEN (A-M-500), the electrolyser sizes to the net new-O2 demand at airless
locales, and the preserved mars postmortem worktree's balance gate passes at
+0.0004 kg/d closing residual (was HDR_O2 -0.9873 kg/d pre-reconcile).

## Wiring

- `foundry_poly.py` (Rev C) owns the brine route call, the wax pair and the HOPPER record.
- `farm_balance.py` calls `nitrate_route.tf` and computes the dose; NUT_AN's ammonia, oxygen
  and water draws re-settle through the existing by-difference owners (IA-NH3-SRC in
  balance.physics R10c, S83 in o2_close from CRYO_O2 direct draws, IA-GW-MAKEUP for ROOF_TANK).
- New drivers registered in `drivers.json`; assumptions A-M-496..A-M-499 appended and A-M-430
  revised; `docs-authority/_assumptions_register.py` re-run green (491 curated).
- Gate target: `python3 -m flow_graph.param.recovery` -> `flags: []`, no pending entry of the
  six retired classes, and `flow_graph/param/test_recovery_first.py` green.

Full regeneration and the derived documents (BALANCE_RECONCILIATION, INSTALL_SEQUENCE,
ISO_ROUTES, the views) are the consolidation pass.
