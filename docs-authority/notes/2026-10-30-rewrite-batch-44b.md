# Rewrite batch 44b: the polymer and foundry routes without flow

Date: 2026-10-30

## Change

Task X-RTE listed ten polymer and foundry routes that carry no flow. Each is decided by the owner rule of 2026-10-29, and the basis is A-M-435.

### Two olefin feeds

MEOH_TO_OLEFIN is a valid second design for the polyolefin feed, so both designs are built, selectable by the new driver olefin_feed_route.

- NAPHTHA, the default, oligomerises the C5-C10 cut drawn at the tank on IA-C5-POLY. It is the default on the merits: the cut is surplus that the plant ships, and the route needs no hydrogen.
- MTO converts plant methanol, CH3OH -> (CH2) + H2O over SAPO-34, with the by-product hydrocarbons recycled (TIAN2015). The methanol is drawn from MEOH_TANK, like the other methanol users, and the reaction water goes to MEOH_COND on the new route IA-MTO-H2O. MTO gives purer ethylene and propylene, but it spends methanol made from electrolytic hydrogen.

The routes of the feed not selected carry their rated rates. For the 0.294 kg/d of resin, MTO draws 0.672 kg/d of methanol and makes 0.378 kg/d of water. Both modes were run: the balance closes in each, and the fit moves no edge.

### Rated and waiting routes

- CUT-1-OUT carries 94.8 kg/d rated when the hydrogen store is empty in an outage and BACKUP_GEN burns the C5-C10 cut. That is the 189.6 kg cut reserve of `backup_fuel.py` over crit_autonomy_d. The generator rating is unchanged.
- POLISH_TO_LI waits on the lithium tenor of the polish liquor, which sets the lithium that LI_RECOVER can take for the LI grease thickener. It is listed under X-RTE-ASSAY.

### Routes retired

- DIGEST_TO_POLY: POLY_COND has no product route, so digester organics sent to it could go nowhere.
- GLASS_MILL_TO_DIGEST: the milled solids reach GLASS_DIGEST through GLASS_BURNOUT.
- SHELL_TO_GLASS: the reusable spent shell is reclaimed as stucco on IA-SHELL-RECLAIM, and GLASS_DIGEST has no free capacity for the fines (A-M-267).
- WAX_TO_OIL: the drainable wax returns to the patterns, and the wax left in the shell burns in place in the burnout.
- OIL_TO_OLEFIN: the olefin feed is drawn as naphtha at the cut tank, so a fractionator draw duplicates it.
- POLYF_TO_PELLET: the fluoropolymers go to FILM_CAST and POWDER_RESIN (A-M-289), and PELLET is the polyolefin line.
- SALT_TO_FLUX: SALT_FEED has no feed, and the flux is the Kroll salt drag-out.

## Check

The reconciliation fit moves no edge, the unit residuals are unchanged, and the recovery inventory raises no flag.
