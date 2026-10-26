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

## Addendum 8: X-LOC-09 Mars design pass — scaling resolves

The Mars profile now resolves. The engineering position changed: a scaling error is a design
requirement, not a finding to record. Each unit the site capabilities cannot carry is eliminated
with a replacement of a different technology, and the replacements are designed units in the graph.

Two systems stay at Mars: the GEO ground loop (regolith is ground contact — GEO_GHEX and GEO_HP
keep running; the earlier eliminations were copied from the LEO profile, where no ground exists)
and the zinc-bromine battery with its closed bromine-regeneration loop (unit_needs.json now carries
a by-unit entry for ZNBR2_BR2_REGEN: a closed electrolytic loop with no atmospheric discharge, not
the scrubber-class vent blanket).

Five locale-replacement units enter the graph as placeholders (stub_activation.py; endpoint 0 at
the Earth reference plant, placed by the locale's scaling actions):

- RAD_PANEL (radiator): 12 kW duty context (A-M-244), rejects at 328 K to a 180 K sky sink at
  emissivity 0.90 (A-M-396, A-M-397); 1.86 m2/kW by the Stefan-Boltzmann law.
- TANK_BLD (press_tank): closed bladder tank, 200 kPa design (A-M-400); replaces CATCH_TANK and
  ROOF_TANK.
- REC_HDR (recovery_header): closed vent and relief recovery to a hold-and-reprocess skid
  (A-M-398); replaces both relief valves, four vent scrubbers, the acid vent scrubber and the flue
  junction.
- CAT_OX (catalytic): waste-gas oxidation on a plant-oxygen bleed at a 450 C bed (A-M-399);
  replaces the air-fired AFTERBURNER.
- E_HEAT (resistance_heater): the N+1 melt trim heat on the grid at the A-M-283 30 kW connected
  duty; replaces the fuel-fired COMB_HEAT.

heat_rejection.py now accepts a rejection level on a registered replacement (the replacement is the
unit that runs at the site); the Mars profile rejects through RAD_PANEL (radiative) and GEO_GHEX
(ground). test_site_power.py gains test_a_level_may_sit_on_a_registered_replacement.

Assumptions A-M-396 through A-M-400 added. SITE_BASIS_MARS.md is Rev B. X-LOC-09's locale run and
the site tests are the remaining proof. X-LOC-10 (LEO, 47 units) uses the same method and is next.

## Addendum 9: X-LOC-09 Mars locale run complete

The Mars locale regenerates end to end: 321 outputs differ from the baseline
under sites/mars/, and the scaling, portfolio and heat-rejection checks pass at
every committed profile (baseline, death_valley, floating_island, antarctic,
mars). Three classes of error surfaced and were fixed at their owners:

1. Process-space physics (A-M-401, site.py p_process_*): physics that live
   inside the plant - dissolved gas in process liquor, the vent-scrubber gas
   side, relief back-pressure, the flue volume - computed at the site ambient
   pressure. At 0.636 kPa the vent-scrubber HCl mole fraction inflated
   160-fold and its NaOH bleed went negative. Enclosed locales now state the
   shell interior (NASA-STD-3001 sea-level equivalent); open-air sites fall
   back to ambient, byte-identical at the baseline. The X-MFG-30 stripping
   column separately sizes on the body vapour space (A-M-106), which the Mars
   run exposed first.
2. The breaker ladder in the one-line diagram stopped at 400 A; it now carries
   the full NEC 240.6(A) standard ratings. The Mars battery charger (390 kW
   over the sol-night stretch) and the 10.7 MWp roof footprint's hall
   conditioning land above it.
3. The motor inventories stopped at the 37 kW IEC ladder top, the 180M frame
   table and the 22 kW IE3 table; they now run to the 630 kW preferred outputs
   with IEC 60072-1 frames to 355L.

X-LOC-09 stays open on its own done-definition remainder: atmosphere intake,
ice extraction, perchlorate removal, the assay feed cases and the
planetary-protection family. X-LOC-10 (LEO) uses the same method next; the
X-LOC-09 units already cover part of its replacement set.

## Addendum 10: X-LOC-10 LEO locale run complete; X-LOC-09 closed

The LEO locale regenerates end to end: 305 outputs under sites/leo/. The
design pass adds the microgravity replacements beside the X-LOC-09 set: sealed
lithium-ion storage (LIO_BAT, A-M-402), wet-oxidation sanitation (WET_OX,
A-M-403), the soilless growth chamber (HYDRO_GROW, A-M-404) and
membrane-distillation water recovery (MEM_DIST, A-M-405). All six profiles
pass the scaling, portfolio and heat-rejection checks; the site tests are
green and the full battery passes.

The LEO run surfaced the remaining external-atmosphere physics (cold-box feed
volume, header and duct gas densities, the ZNBR2 purge air) and the roof-close
boundary where the whole-kW nameplate must fit the roof; each fix is at its
owner and the baseline is byte-identical throughout.

X-LOC-09 closes: the in-situ resource units enter the graph (ICE_EXTRACT,
PERC_REMOVE, ATM_INT; A-M-406 to A-M-408), the Mars feed cases map to the
AQS-ASSAY-001 classes (ground ice, regolith, perchlorate salts), and the
jurisdiction family and basis page carry planetary protection
(AQS-SITE-009 Rev D). X-LOC-12 (the cross-locale comparison) is next; X-LOC-11
keeps the floating-island hull pass.

## Addendum 11: X-LOC-12 cross-locale comparison

SITE_COMPARISON.md (AQS-SITE-011) generates in the pipeline from the committed
profiles and the locale outputs: the scaling actions per locale, the power
portfolios, and the unit sizes that move between locales. The stage runs after
site_power and is staleness-gated like every generated page.

## Addendum 12: X-LOC-11 and X-LOC-12 close; every locale task is done

The floating island closes with the hull pass as code: hull.py proves the
pontoon carries the operating mass with GM and freeboard margin (AQS-SITE-012,
A-M-412 to A-M-414), and the seawater system units (SW_INTAKE, DESAL_RO,
BRIN_RECOVER; A-M-409 to A-M-411) join with the mapped seawater feed case.
X-LOC-12 generates SITE_COMPARISON.md (AQS-SITE-011) in the pipeline across
all six profiles.

Locale board state: X-LOC-07, 08, 09, 10, 11 and 12 all done and ticked with
evidence. The three unit design records for the LEO imported modules
(capillary-gap cells, centrifuges, pumped-loop reactors) stay as named import
paths; designing them in-house is manufacturing-desk work, task by task.

## Addendum 13: FOUNDRY-CA_POT-10/-11 accepted at M3

The grease-Ca electrolysis pot moves from the M2 foundry export to a dedicated
build (models/mfg/CA_POT/ca_pot.py + params.json): three D50 graphite anodes at
250 mm immersion, two cathode plates, the 25 mm2 Cu bus class, DN50 offtake
with a return dip leg, and the N1 Ca-metal tap, N2 brine lance, N3 Cl2 export
and N4 drain per the task-04 schedule. check.json records the acceptance: the
build solid sits inside the 800 x 800 x 1600 envelope, the schedule hardware
overhangs at most 44.5 mm against the 50 mm allowance, and every part is
valid. The cad/stl registry solid is the in-envelope build and the X-PAR-04
gate passes. The 8-sheet drawing set is stamped (AQS-DWG-002) with SVG and PDF.
The task-plan generator's DONE_X set carries the X-LOC-09..12 ticks so the
board and the files agree.

## Addendum 14: FOUNDRY-MG_POT-10 accepted at M3

The Kroll-magnesium recycling pot moves from the M2 foundry export to a
dedicated build (models/mfg/MG_POT/mg_pot.py + params.json): four D50 graphite
anodes at 300 mm immersion, three cathode plates, the 50 mm2 Cu bus class, the
DN80 chlorine offtake (1.4813 kg/d; N2 return and N6 chlorinator feed per the
A-M-280 ruling), and the N1/N5 tap groups, N3/N4 inlets and N7 drain per the
task-04 schedule. check.json records the acceptance: in-envelope build,
schedule hardware within the 50 mm allowance, all parts valid; the X-PAR-04
gate passes on the in-envelope registry solid. The 8-sheet drawing set is
stamped with SVG and PDF. Unit task 11 stays partial per the house convention
(per-part dimension chains open) alongside AL_POT, CAST_LINE and CA_POT.

## Addendum 15: FOUNDRY-MO_CELL-10 and FOUNDRY-CR_CELL-10 accepted at M3

The molybdenum and chromium molten-salt cells move from the M2 foundry export
to dedicated builds (models/mfg/MO_CELL/mo_cell.py, models/mfg/CR_CELL/
cr_cell.py, each with params.json). Each check.json records the acceptance:
in-envelope build solid, schedule hardware within the 50 mm allowance, all
parts valid; the X-PAR-04 gate passes on the in-envelope registry solids. The
8-sheet drawing sets are stamped with SVG and PDF. Unit task 11 keeps the
house partial state (per-part dimension chains open).
