# Review of the farm design-tool placement branch: work items and reasons (2026-11-04)

This record gives the reason and the evidence for each work item X-QA-04 to X-QA-17 in
`docs-authority/TASK_PLAN.md` (AQS-PLAN-007). The task plan states the acceptance test of each.
Figures quoted here were read from the tree at commit ed34d002 and will go stale; the graph and
the generated pages govern.

## X-QA-04. Electrowinning deposits computed from the feed assay

The cascade is sized on `DIGESTER.ew-cascade-train.ew_s08_deposits_kg_d` in `drivers.json`.
Those rows are the cathode deposits booked on S08, whose edge note cites a 150 kg/d wet-feed
audit. They are not computed from IA-FEED-01. At the 102.68 kg/d design feed the largest
plateable fraction of any case in the assay envelope gives about 36 kg/d of plateable metal,
while the rows sum to 42 kg/d. Five rows (Pb, Sn, Ni, Cd, Zn) carry the same value, an equal
division of one lumped figure. The cell currents follow Faraday's law correctly from those
rows; the error is in the rate basis, not in the arithmetic. The cascade is also sized at the
reference point while AGENTS.md (Sizing) requires the bounding case of the assay envelope.
`flow_graph/param/test_ew_deposit_basis.py` records the defect as an expected failure.

## X-QA-05. Low-duty electrowinning cells

At the present basis EW_1 (gold) draws about 0.13 A and EW_2 (silver) about 0.3 A. Even at the
bounding case of the envelope the two cells stay near or below 1 A. The products of EW_4, EW_5,
EW_6, EW_8 and EW_9 are blended to powder downstream, so their separation gains nothing at
present. Neither design is clearly better: a selective cascade keeps the option of pure
products, a merged cascade removes cells that run at a small fraction of one cathode. Both are
to be sized and offered as a driver-selected option. The uncommitted regeneration of the nine
EW models at the present basis is kept in a local stash and not committed, because it would
issue one-cathode cells on a basis that X-QA-04 changes, and because its bus bar sections
were not recalculated from the new currents.

## X-QA-06. Rectifier channels sized from current

`docs-authority/_rect_ew_sizing.py` holds the channel frame list (smallest 250 A), a 1.10 margin
and a 6.0 V channel rating as literals. The smallest frame sets every small channel, and the
nameplate is several times the electrowinning load.

## X-QA-07 and X-QA-08. Standby generator rating and open questions

`drivers.json` holds `backup_gen_rated_kW` = 40.0, based on a 32 kW critical list. The live list
from `backup_fuel.critical_list()` sums to about 14.6 kW, which the AQS-ELEC-007 rule (125
percent, 5 kW steps) rates at 20 kW. Q-038, Q-039 and Q-040 are not recorded as closed. The
generator stays dual-fuel, hydrogen first.

## X-QA-09. Provenance check compares values

The provenance tests added in ed34d002 compare unit identifiers only. See the limits section of
`docs-authority/notes/2026-11-04-parametric-provenance.md`.

## X-QA-10. Builders take counts from the graph

The ZNBR2 builder asserts 47 modules while the graph carries 36, so the committed ZNBR2 model
does not match the graph and the builder cannot run at the present graph. The H2O_ELYZ builder
asserts a fixed cell count and bed lengths; the VCD_TRAIN builder fixes the working volume.

## X-QA-11 and X-QA-12. Dock imports and the shop export

Water for the leach (IA-H2O-MU), reagents and oxide feeds enter at NORTH_DOCK. Only raw feed
and waste may enter the plant. IA-GOODS-SHIP is closed by difference in
`flow_graph/param/balance.py`, so its rate is whatever closes the shop balance.

## X-QA-13. Wetted metal in the acid and base regeneration line

BMED_ACID and BMED_BASE carry 316L/Ni end plates and 316L tie rods; EVAP_ACID has a lined carbon
steel shell. The design rule for the chlor-alkali and acid-regeneration systems is PVC with
materials chosen by chemical and electrochemical compatibility.

## X-QA-14 to X-QA-16. Repository and page hygiene

STEP files and large drawing SVGs are tracked as ordinary Git objects; `.gitattributes` routes
only `*.FCStd` and `*.stl` to LFS. Several graph nodes (BACKUP_GEN, BMED_ACID, BMED_BASE, FUEL_CELL and the WS_ reagent
totes) carry a size note in which one sentence repeats; the writer that appended it no longer exists. CHECKS.md and EW_MODULE.md still state
electrowinning figures that AQS-DUTY-051 superseded.

## X-QA-17. Proposal: simpler regeneration provenance

The present mechanism decides whether a derived file is current from Git commit order: a file is
current if it was committed after the last graph commit. A regeneration that produces identical
bytes cannot create a commit, so the pipeline writes a receipt listing the files and patterns
it regenerated without change, and the staleness check accepts those. The receipt changes with
every graph change and must be committed with it; a run that fails to converge drops entries
and can mark many healthy files stale at once (recorded in
`notes/regen_vouch_redesign_2026-11-03.md`); and the check depends on commit history, so its
result changes when commits are reordered.

Proposed replacement:

1. Each generator records, in one provenance manifest, the SHA-256 of the inputs it read (the
   graph, the drivers and its own source) for each file it writes.
2. A file is current when the recorded input hashes equal the hashes of the present inputs.
   This is computed on demand and needs no commit order.
3. The full-regeneration idempotency check (`scripts/check_all.sh --full`) remains the proof
   that the committed outputs are what the generators produce.
4. The receipt lists and the commit-order rule are removed once the manifest covers every stage.
