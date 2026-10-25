# Heat rejection modes and storage coverage

Date: 2026-10-25. Documents: AQS-PLAN-011 Rev J, AQS-SITE-005, AQS-PLAN-007 (X-LOC-06 done).

## Change

- Each profile carries a `heat_rejection` group: per level of the heat ladder, the unit, its mode and the graph parameter that gives its duty.
- `flow_graph/param/heat_rejection.py` checks each mode against the site capabilities. A radiative level is sized by the Stefan-Boltzmann law, with the constant from CODATA 2018; its emissivity and sink temperature are profile entries. A heat pump level states its lift and the Carnot bound on its coefficient of performance. Every heat rejection unit that remains after the scaling actions needs a level.
- Each storage entry in the power portfolio names the graph parameter that gives its stored energy. `docs-authority/SITE_POWER.md` compares the total with the energy the worst stretch draws at the plant demand, and lists the heat rejection modes.
- The CODATA 2018 reference now carries the Stefan-Boltzmann constant.

## Decision taken

X-LOC-06 is marked done. Sizing a primary source other than PV in the power sizing moves to the first locale that selects one; until then the power sizing stops on such a portfolio.

## Check

`scripts/check_all.sh --full` passes. Baseline outputs are unchanged apart from the power document and the registers.
