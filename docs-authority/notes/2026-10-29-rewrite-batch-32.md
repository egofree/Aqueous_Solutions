# Rewrite batch 32: water as a natural resource; carbon reductant from plant char

Date: 2026-10-29

## Water make-up

Owner decision: water make-up is a natural resource, like air. The import check in `docs-authority/_task_plan_gen.py` now allows water make-up, so task X-RTE-IMPORT-IA-H2O-MU drops off the list. The water balance stays on the graph unchanged. The baseline site profile (`flow_graph/param/sites/baseline.json`) now lists its water sources: the groundwater well GW_INTAKE and the delivered make-up water at the dock. This group was previously marked pending.

## Carbon reductant

Tasks X-RTE-IMPORT-IA-C-TI, X-RTE-IMPORT-IA-C-MO and X-RTE-IMPORT-IA-C-CR are done, as one grouped task X-RTE-IMPORT-CARBON. The Ti, Mo and Cr chlorinators used to take imported petcoke-class carbon. They now take pyrolysis char from OIL_PYRO, which already makes a char surplus that goes to the shop.

- `flow_graph/param/foundry_poly.py` sets each char draw to the carbon need of the cell divided by the new driver `char_fixed_C_frac` (0.85, A-M-420).
- The volatiles and ash of the char leave with the chlorinator gas, so the gas edges, which are set by difference, rise by the same amount.
- No second technology is offered, because the plant has only one carbon source of this duty class; a digester or methanol route would not give a solid reductant.

| Stream | Before | After |
|---|---|---|
| IA-C-TI (from NORTH_DOCK, now from OIL_PYRO) | 0.2509 kg/d | 0.2952 kg/d |
| IA-C-MO | 0.0117 kg/d | 0.0138 kg/d |
| IA-C-CR | 0.0866 kg/d | 0.1019 kg/d |
| IA-CHAR, shop char by difference | 5.2722 kg/d | 4.8613 kg/d |
| IA-KROLL-CO | 0.5852 kg/d | 0.6295 kg/d |
| IA-MO-VENT | 0.0430 kg/d | 0.0451 kg/d |
| IA-CR-VENT | 0.2020 kg/d | 0.2173 kg/d |

There is no cascade into bus demand, array, storage or balance closure: the char moves between solid routes, and the PV continuous rating stays at 351.3442 kW.
