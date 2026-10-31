# 2026-10-30 — The baseline becomes location-neutral; the cost price basis is decided

## Owner decisions recorded

1. **The baseline is location-neutral** (re-frames X-BAS-03 and AQS-SITE-002): the plant is a
   system of engineering buildable at a location of the engineer's choice. The baseline carries
   no location; each site value is the **strictest value across the localization set**
   (`flow_graph/param/sites/`), carried from the governing site with its published source.
   Location enters as an input of the site design tool: a site design replaces every bounding
   value with the location's published value and the model re-solves. Seismic is the one
   per-site input: the spectral shape changes the foundation method (presumptive versus
   engineered), not a scalar size, so the baseline carries its study-site value.
2. **Q-012 closed, option (b)**: the cost estimate prices material mass x published commodity
   prices x a fabrication factor. Method issued as AQS-PRO-003
   (`docs-authority/COST_ESTIMATE.md`); the price references registered
   (`USGS_MCS_2025`, `LME_CASH`, `CEPCI`, `TOWLER_SINNOTT`). X-PRO-03 and X-BAS-03 leave the
   owner-gated list; X-ELS-08 stays (the Wenner test needs a parcel).

## What changed

- The baseline profile (`flow_graph/param/sites/baseline.json`) and the drivers now carry the
  bounding set: cooling design 47.4 °C (death_valley), heating design −9.4 °C (death_valley),
  basic wind 70 m/s (floating_island, Saffir-Simpson 5), seismic per-site (study 0.107 g),
  snow 0.24 kPa and PV yield 5.41 kWh/kWp d (the baseline's own values are already the set's
  strictest). Every value names its governing site and source, and the site design tool's
  replacement is stated per value.
- AQS-SITE-002 Rev C (`docs-authority/SITE_BASIS.md`) restated on the same rule, with the
  former DFW study-site values superseded as the basis (they remain in the assumptions history
  and this page's git record).
- The foundation check re-ran under the bounding experiment: at the death_valley seismic
  (SDS 0.5 g) the presumptive-clay mat fails overturning bearing and thickening makes it worse
  (the added weight raises net toe pressure) - which is exactly why seismic is a per-site input
  that changes the foundation method. The finding is recorded here; a 0.5 g site design carries
  an engineered foundation (piles or soil improvement) in its own re-solve.
- Q-034 added: the antarctic site's polar night (24 h night, yield 1.0) cannot be bounded by
  the daily-cycle solar architecture; default is that the polar site is a different technology
  class carrying its own power-portfolio replacements, as leo and mars already do.
- New assumption-registry injury found and recorded, not silently patched: the value fields of
  the assumption entries A-M-131..A-M-226 (96 entries) all carry the A-M-131 motor-family text
  regardless of their (correct) titles and statement fields - a mass overwrite from an earlier
  era. The wind bounding change touches a driver whose register cites this injured region.
  Repair needs per-entry recovery (the statement fields survive for most entries; git history
  has the rest); it is its own work item (proposed X-GOV task).

## Verification

`python3 -m flow_graph.param.regen` green; `pytest flow_graph/` 204 passed / 1 skipped
(including the site-profile identity gate: the baseline profile resolves to `drivers.json`
exactly, entry for entry). `scripts/check_all.sh` clean. The task plan regenerates with
X-BAS-03 and X-PRO-03 as desk tasks and the owner-gated table empty.

## Follow-up close-outs (same day)

- **X-BAS-03 closed.** The remaining named lookups landed: the bounding station normals are the
  Furnace Creek record (USC00042319, WRCC: HDD65 1251 F-d, CDD65 5264 F-d, annual mean 75.9 F,
  1961-1990 normals), so the envelope coefficients bound to the governing site
  (`ext_dTh_K` 1.904 K, `ext_dTc_K` 8.012 K, `ext_dT_mean_K` 9.916 K, ref `NOAA_WRCC_DV`). The
  IECC envelope values are already the set's strictest (the baseline's zone 3 governs over the
  hotter sites' zones 1-2) and say so. Seismic stays per-site by the recorded rule. Evidence:
  `docs-authority/SITE_BASIS.md` Rev C and the drivers.
- **The four hab-room nozzle tasks closed** (HAB-COMMON_AREA-04, HAB-MEDICAL-04,
  HAB-REC_DAYROOM-04, HAB-SLEEP_QUARTERS-04): the rooms carry no piped process connections, so
  the nozzle-schedule rule closes them with the no-file note, as FORGE and the other
  connectionless machines already are.

Desk P1 is now empty and desk P2 holds only the gated items (X-END-02's named holds, X-PRO-03's
mass dependency) and the localization program's own tasks (X-LOC-01/02).

## Internals dispositions (unit task 06, desk P3)

The internals register pass closed 28 of the 38 open task-06 items with real
issued bases, via an explicit disposition table in `docs-authority/_internals.py`
(each carrying its own evidence artifact - the family sizing doc, the mfg BOM,
or the unit's own AQS-SIZE sheet):

- the eight heat batteries on the AQS-DUTY-008 sec. 14 internals (medium,
  thermosyphon steps, cross-ties); the CRYO_CO2/H2/O2 tube banks as
  none-with-basis (pressurised banks, open volume); AQUA_UV, BIOFILTER,
  FEED_PREP, MET_SYN, MEOH_FC, VCD_TRAIN, BMED_UPW_POLISH, H2_DRYER on their
  issued designs; HF_GEN, OIL_PYRO, POLY_FIBER, MEOH_FERM, BLACK_DIGEST on
  their mfg models; RES_HEAT, SINTER, SI_REDUCE on the element-array and charge
  bases; FLOAT_SINK as the water-bath separator.

Ten remain honestly open with the specific missing data named per unit (the
BAGHOUSE capture-air volume, the CRU contacting stages, the two Q4 recovery
coils' design temperatures, the OIL_FRAC column internals, the OIL_DRYER
media, the N2 receiver bank, the FUEL_CELL stack design, the GREY_TREAT stage
design, the ZNBR2 stack gated on X-MFG-41). Desk P3 falls 38 -> 10.

Also recorded: a DONE_X set-literal injury repaired (X-LOC-01/X-LOC-02 had been
silently reopened by a lost comma) and X-LOC-02's loader clause verified.
