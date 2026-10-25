# Earth-surface constants read from the site profile

Date: 2026-10-25. Documents: AQS-PLAN-011 Rev E, AQS-OQ-001 (Q-032), AQS-PLAN-007 (task X-LOC-03, partly done).

## Change

- The baseline profile carries the gravity group (standard gravity, CGPM 1901) and the atmosphere group (standard atmosphere, CGPM 1954; dry air composition, U.S. Standard Atmosphere 1976; breathable, vent sink and oxidant flags). Both groups now carry entries at every site.
- `flow_graph/param/site.py` gives `g()`, `p_atm_Pa()`, `p_atm_kPa()` and `air_fraction()`.
- These modules read gravity from the profile: `sizing/tank.py`, `_storage_sizing.py`, `_struct_loads.py` and the liquid head in `write_graph.py`.
- These modules read the external pressure from the profile: the gauge-to-absolute steps in `pressure_nodes.py`, `fire.py`, `evap_design.py`, `_fire.py` and `_relief_register.py`; the feed volume in `cold_box.py`; the flue volume in `write_graph.py`; the scrubber operating pressure in `sizing/scrubber.py`; the oxygen and nitrogen partial pressures in `balance.py`.
- `flow_graph/param/test_site_constants.py` fails on a new standard gravity, standard pressure or air composition literal in model code, lists the two pressure literals that stay with their reasons, and keeps the list of modules using 9.81 m/s² from growing.

## Not yet done

The modules using the rounded gravity 9.81 m/s² wait for Q-032. The air densities held as drivers are not yet derived from the profile. X-LOC-03 stays open.

## Baseline

The profile values equal the literals they replace, so a full regeneration changes no numeric output. The reference lists gain the three new sources.

## Check

`scripts/check_all.sh --full` passes.
