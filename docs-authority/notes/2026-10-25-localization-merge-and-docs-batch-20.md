# Localization merge, README note and documentation batch 20

Date: 2026-10-25. Scope: main after the docs-rewrite and localization branch merges; no graph topology change.

## Branch merges

- `origin/docs-rewrite` (20 commits, batches 1-19 of the documentation rewrite) merged to main; the single conflict was the generated derived-revisions register, resolved by regeneration. The two untracked working pages in the `docs-authority/` root were moved to `docs-authority/internal/` per the repository rule that agent-only material stays there; this also closed the last failing document-map check.
- `origin/localization` (28 commits, X-LOC-01 to X-LOC-06) merged to main. Their thirteen new open questions entered the register as Q-021 to Q-032; the documentation batch's own Q-020 kept its number and the localization batch's colliding Q-020 was renumbered Q-033, with the citing page updated. The full pipeline was regenerated after the merge; the baseline output moves stay within the recorded small deltas, and the reconciliation gate reports no move outside tolerance.

## Documentation batch 20 (all on main)

CO2_HEADER_DUTY (Rev D, updated to graph Rev AC through the extended header study; setpoint question recorded as Q-033), CAMPUS_PLAN (Rev C), CRYO_COLD_BOX (Rev D), ASME_CODE_INTENT (Rev D, through `_asme_class.py`), BALANCE_RECONCILIATION (Rev E, through `balance.py`; section renumbering chased into `closure_tf.py` and assumptions A-M-120/A-M-123). Glossary additions in the same changes: SG, PQ, BH, AUD. Fixed in passing: the assumptions-register scan crashed on any model `params.json` whose `assumptions` entry is a list; the CAST_LINE file was converted to the keyed form and the register runs again.

## README

Section 2.4 describes the site-profile system and the locale studies in progress; the status section points at it. The task plan now names the evidence for X-LOC-06 (`SITE_POWER.md`) instead of an empty evidence cell.

## Checks

`scripts/check_all.sh --full` run on the merged tree before this push: tests, staleness, authority contract, citations, documentation style, and the double full regeneration of the committed tree that must change nothing.

## Addendum: branch unification and X-LOC-07 (Death Valley)

The repository is single-branch: the docs-rewrite, localization and
public-release-prep refs were fully contained in main and were deleted on the
origin so the lanes cannot diverge again.

X-LOC-07 (Death Valley) started: the profile
`flow_graph/param/sites/death_valley.json` (Furnace Creek climate record,
groundwater make-up with reverse osmosis, evaporative low-grade rejection
charged against the water balance, PV primary), interim bounding values as
assumptions A-M-385 to A-M-387, the site basis page AQS-SITE-006, and the first
locale run (270 outputs under sites/death_valley/, untracked and regenerable;
tracking them broke the single-document gates and they are now ignored). The
bound site drivers carried baseline-specific units text; the text is neutral at
the driver and each profile now describes its own site. The locale run closes
the mass balance and reports coverage 1.09; its design check carries one
finding, QC-09 (site H2 receiver rack holds 17.406 kg against the 19 kg Q-004
basis), and the groundwater intake unit is not yet in the graph. X-LOC-07 stays
open on the board until those two close.

## Addendum 2: X-LOC-07 close-out items

QC-09 resolved: the design check compares the receiver rack against the graph's
sized hydrogen store (17 kg, AQS-ELEC-007 / X-PAR-12) instead of the superseded
19 kg constant, and passes at both sites. The groundwater intake unit GW_INTAKE
entered the graph through the standard new-unit induction (tree leaf, envelope
STL, instrument loops FT/PT/CT, duty sheet with issued section 3 selections,
sizing sweep document, P&ID, task chain; the tree test count pins grew by one).
Its make-up edge to ROOF_TANK books the difference of the water cycle and solves
to zero at the baseline. Named next item for the Death Valley lane: the profile
does not yet carry air-moisture design values, so the condensate model still
books the baseline 67.44 kg/d harvest at the site; when humidity binds, the
harvest falls and the intake picks up the deficit.

## Addendum 3: correction of the site-water mechanism; task X-LOC-13 scoped

Two unpushed commits that booked an evaporative spray charge inside
`balance.physics()` were discarded before they reached the origin: the work
expanded past its task (a new boundary node, runtime edge creation and a
second water-closure path) and is replaced by a scoped task, X-LOC-13, with
the design-pass requirement stated (ordering between the heat solve and the
mass closure; baseline output unchanged). The record also corrects a wrong
mechanism claim this lane made on AQS-SITE-006: the air-handler condensate
harvest is indoor-air recovery (greenhouse and habitation vapour), so it does
not depend on outdoor humidity and does not fall at a dry site; the intake
solves to 0 kg/d in the present run because no site water deficit is booked
yet, and the deficit that does belong to this profile is the evaporative
rejection charge of X-LOC-13.

## Addendum 4: X-LOC-13 built; X-LOC-07 (Death Valley) done

The evaporative rejection water charge is built as designed. The graph gains
the ATMOS bookkeeping boundary and the IA-DC-SPRAY / IA-DC-EVAP edge pair at
zero; `balance.physics()` books the charge where the site's low-grade rejection
mode is evaporative: spray = rejected kW x 86400 s x 1000 W/kW / 2.454 MJ per kg
(NIST_WEBBOOK), the evaporated fraction leaves to ATMOS, and GW_INTAKE
closes the roof-tank balance by difference. Design-pass answer on ordering:
every write_graph_heat sizing stage precedes balance_report in the
regeneration manifest, so the mass closure reads final heat-edge rates and no
iteration is needed. GW_INTAKE and ATMOS joined the boundary-meter exemption
set (in does not equal out by design). Baseline solved values are unchanged
(the edges book zero at air-rejection sites); the tree count pins follow the
new leaf. The Death Valley run books 255.257 kg/d (the 7.25 kW rejected duty)
end to end, and AQS-SITE-006 Rev B records it. X-LOC-07 and X-LOC-13 are
ticked with evidence.

## Addendum 5: X-LOC-11 first pass (floating island)

The floating-island profile is in: tropical moored platform (Q-030/Q-031),
seawater as coolant, water source and mineral feed (Millero composition; RO
desalination at the least-energy basis), a motion envelope as interim assumption
A-M-388, Category 5 survival wind on the moorings, the marine code family, and
the scaling actions (pumped hydro and the ground loop eliminated with recorded
different-technology replacements; DRY_COOLER duplicated as the seawater
rejection pair). The locale run closes with no design-check failures. Two real
findings are recorded: the building class no longer claims ground contact as a
site service (bearing is structural - the hull deck per class rules at sea), and
the worst-stretch storage coverage is exactly 1.00 with no margin. X-LOC-11
stays open on its named remainder: the hull design pass (mass, centre of
gravity, stability, freeboard, motion-coupled sizing checks), the seawater
intake/desalination/mineral-recovery units, and the assay feed case. A
gitignore regression that silently ignored flow_graph/param/sites/ was found and
fixed (pattern anchored to the repo root).

## Addendum 6: LEO locale findings; mfg model solid-wall audit

The LEO locale profile correctly identifies that 47 units cannot operate in
microgravity (no buoyant separation, no free surfaces, no convective cooling,
no atmospheric venting, no oxidant). Elimination actions with import paths or
different-technology replacements are recorded for every flagged unit. The
three site-test failures are this genuine finding, not a bug; they close when
the X-LOC-10 replacement units join the graph.

The five mfg models that export non-watertight STLs (FILM_CAST, POLY_F,
POWDER_RESIN, SHELL_BURNOUT, TI_CELL) have 2 to 9 bodies that were not
boolean-unioned before export. The fix is the build-and-union approach that
CAST_LINE and AL_POT use. Each needs a per-unit engineering check that the
union is valid.

## Addendum 7: mfg model solid-wall audit result

Five manufacturing models export multi-body compounds that were not
boolean-unioned before STL export: FILM_CAST (7 bodies), POLY_F (9),
POWDER_RESIN (5), SHELL_BURNOUT (4), TI_CELL (2). These are legacy outputs
from the X-MFG-31 batch; they have no per-unit build scripts in
models/mfg/<UNIT>/. They will be rebuilt with the build-and-union convention
when their units reach the desk P4 M3 acceptance pass. The remaining 59 mfg
export STLs are watertight solids. The cad/stl registry (168 files) is fully
solid after the tray-geometry fix.
