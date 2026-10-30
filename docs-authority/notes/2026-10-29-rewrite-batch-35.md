# Rewrite batch 35: recovery first for every element

Date: 2026-10-29

## Rule

Owner decision t61u: the sodium rule applies to every element. The plant recovers each element it needs from waste and byproduct streams anywhere on the graph first. Raw ore at the dock only tops up the shortfall left after recovery, and the code sizes that top-up. The rule is now in AGENTS.md, in a new section on on-site production and recovery first, and is recorded as A-M-423.

## Inventory and check

- Each transfer function that takes an ore stamps a recovery record on its unit. The record gives the element, its use, the need, the amount recovered from waste and its source streams, the ore streams, and each unrecovered loss with its basis and whether it is recoverable.
- `flow_graph/param/recovery.py` reads the records and the graph and flags any of the following:
  - a dock input that is not a listed raw ore, water, waste or pending import;
  - a raw ore with no record;
  - an ore input above the shortfall, computed from the graph rate, the mineral formula and the ore purity;
  - a loss marked recoverable while ore is taken;
  - a waste outflow of an ore element that no record recovers or declares.
- `flow_graph/param/test_recovery_first.py` fails on any flag. It also checks that an ore above the shortfall and an undeclared waste outflow are caught.
- PARAMETRIC_MODEL (AQS-PAR-001) revision E carries the generated inventory in section 7.2.

## Elements revisited

- **Sodium:** done in batch 34. The leach purge salt is recovered in the chlor-alkali cells, and trona ore covers only the bleed.
- **Sulfur:** the acid-plant kiln used to reduce only the anhydrite of the HF kiln cake. The cake also carries the free acid of the stoichiometric excess, which the kiln now reduces too, so the kiln recovers the fraction caso4_dec_frac of all the acid sulfur. Sulfur ore falls from 0.0185 to 0.0129 kg/d. The SULFUR_ORE route recovers nothing, so the check flags it while it is selected (Q-034). POLYMERS_LINE is at revision D.
- **Calcium:** the causticiser lime make-up now comes from the lime in the acid-plant residue (new stream IA-LIME-TO-NAOH) before any limestone ore. Limestone ore falls to zero, and that stream is retired.
- **Fluorine:** the F_RECOVER concentrate covers most of the HF need first; fluorspar covers the rest and the HF kiln non-conversion.
- **Silicon:** the investment shell is reclaimed first, and foundry silica covers the spent-shell export. The arc-furnace quartz has no waste source, because the plant silica wastes are fines rather than lump quartz.
- **Titanium, molybdenum and chromium:** no waste stream on the graph carries these metals. The leach grit is the expected source once the AQS-ASSAY-TI-MO assay lands (Q-037).
- **Carbon** is not taken as ore: the char comes from OIL_PYRO.

## Dock raw-ore inputs

IA-CAF2-MU (fluorspar), IA-TIO2-MU (rutile), IA-MOO3-MU (molybdenite concentrate as MoO3), IA-CR2O3-MU (chromite), IA-QUARTZ-MU (quartz), IA-SILICA-MU (foundry silica), IA-SULFUR-MU (native sulfur) and IA-TRONA-MU (trona). IA-LIMESTONE-MU and IA-HALITE-MU are retired at the present route settings. The mining-waste inputs are AlCl3 and the CaCl2 and MgCl2 brines. Solvent and wax remain pending imports, X-RTE-IMPORT-IA-SOLV-MU and X-RTE-IMPORT-IA-WAX-MU.

## Open questions

Q-034 to Q-037 are added to OPEN_QUESTIONS (AQS-OQ-001, revision C): the acid route and kiln duty, the caustic top-up technology, the chlor-alkali hydrogen placement, and the Ti, Mo and Cr grit source.

## Values

| Quantity | Before | After |
|---|---|---|
| IA-SULFUR-MU, sulfur ore | 0.0185 kg/d | 0.0129 kg/d |
| CHAR_TO_ACID, char to the cake kiln | 0.0244 kg/d | 0.0257 kg/d |
| IA-CHAR, shop char by difference | 4.8369 kg/d | 4.8356 kg/d |
| IA-LIME-TO-NAOH, residue lime to the causticiser | none | 0.0224 kg/d |
| IA-LIMESTONE-MU, limestone ore | 0.0289 kg/d | retired |
| IA-LIME-SHIP, residue to the dock | 0.2987 kg/d | 0.2594 kg/d |
| ACID_PLANT electrical load | 0.9654 kW | 0.9660 kW |
| NAOH_PLANT electrical load | 1.1935 kW | 1.1929 kW |
| PV continuous rating | 353.877 kW | 353.877 kW |
