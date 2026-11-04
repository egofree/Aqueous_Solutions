# 2026-11-03 BMED design energy moved to the 2 M SEC (physics-audit F-5)

The BMED solver took its design energy from the triplet voltage `max(V_model, V_pilot)` =
1.671 V, which is 1.40 kWh/kg NaOH - the EDBM_PILOT_2023 seawater-brine class (about
0.5-1 M product) - while the plant books a 2 M product (`bmed_product_molarity` 2.0,
product wt fractions at 2 M). The repo's own source quotes the concentration-honest
number: EDBM_WHEY_2021 gives 6.7 kWh/kg to produce 2 M acid or base, and A-M-170 already
said "energy stays on the 2 M SEC". The solver itself computed and published the honest
figure as a comparison (`kW_whey_2M` 26.93 kW) while booking the stale 5.63 kW. Fixed at
the transfer function (`flow_graph/param/solver.py bmed()`); A-M-171 restated.

## Numbers (before -> after)

| Quantity | Before | After |
| --- | --- | --- |
| Design SEC | 1.40 kWh/kg NaOH (pilot voltage basis) | 6.7 kWh/kg at the 2 M product (EDBM_WHEY_2021) |
| BMED_ACID / S17-BMED | 5.6267 kW | 26.93 kW |
| Plant demand P (bounding) | 218.33 kW | moves +21.3 kW (regenerated) |
| PV / storage chain | scaled to the old P | re-solves through roof_close / power() |

The voltage model and the pilot SEC stay on the graph as model data at their own
concentration; the misfit comparator now names the 2 M basis (EDBM_WHEY_2021).

## Changed files

- `flow_graph/param/solver.py`: `bmed()` SEC from the driver `bmed_sec_kWh_per_kg_base`;
  `kW_model_brine` replaces the `kW_whey_2M` comparison key; check() comparator restated.
- `flow_graph/param/write_graph.py` process(): BMED_ACID kW note names the 2 M source and
  the F-5 basis.
- `flow_graph/param/report.py`: PARAMETRIC_MODEL.md section 4a text restated.
- `docs-authority/assumptions_manual.json`: A-M-171 restated (value, basis, sensitivity,
  verification); ASSUMPTIONS_REGISTER.md regenerated.
- `docs-authority/ELECTRICAL.md`: the stale BMED paragraph (2.06 kWh/kg / 6.22 kW) now
  names the basis and the graph values instead of dead numbers.
