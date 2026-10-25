# Gravity and air density from the site profile in every module

Date: 2026-10-25. Documents: AQS-PLAN-011 Rev F, AQS-OQ-001 (Q-032 closed), AQS-PLAN-007 (X-LOC-03 done), A-M-384.

## Decision

Q-032 closed by the owner: hard-coded values are a gap and the sizing must be parametric. Every module that used the rounded gravity 9.81 m/s² now reads the profile gravity. The baseline profile keeps standard gravity and the standard atmosphere, flagged for verification.

## Change

- Reactor, evaporator, heat battery, geothermal loop, house and vent scrubber, energy storage, pumped hydro, nutrient dosing and motor sizing, the FreeCAD frame model, and the foundation, frame, busbar, fire, hydro siting, water tower and design check calculators read gravity through `flow_graph/param/site.py`.
- The air density drivers for the gas headers, the sanitation superficials and the zinc-bromine purge are replaced by temperature drivers (A-M-384). `site.air_density()` computes the density from the profile pressure and the dry air molar mass (U.S. Standard Atmosphere 1976) with the CODATA 2018 gas constant.
- `flow_graph/param/test_site_constants.py` fails on any gravity literal in model code and on any driver holding an air density.

## Effect on the baseline

Outputs that depend on gravity change by the ratio of 9.80665 to 9.81, and outputs that used the rounded air densities change by the difference between those and the ideal gas value. The regenerated graph, duty sheets, load list, structural and foundation documents, drawings and inventories record the new values. No topology changed.

## Found while doing this

- The former purge air density driver cited A-M-135, which is a motor model assumption; the replacement temperature driver cites A-M-384.
- The foundation calculator enters concrete as a unit weight in kN/m³, which holds Earth gravity. It should become a density times the profile gravity; this needs a cited concrete density and changes foundation outputs, so it is left for a later step.

## Check

`scripts/check_all.sh --full` passes.
