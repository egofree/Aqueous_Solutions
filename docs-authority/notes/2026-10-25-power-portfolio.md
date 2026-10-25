# Power portfolio and function redundancy

Date: 2026-10-25. Documents: AQS-PLAN-011 Rev I, AQS-SITE-005 (new, generated), AQS-PLAN-007 (X-LOC-06, part).

## Change

- Each profile carries a `power_portfolio` group: sources with role, unit and basis; storage; the worst stretch; the oversize factor, which binds `pv_oversize_factor`.
- `flow_graph/param/portfolio.py` solves the daily balance through the worst stretch for any mix of primary sources. The PV correction it gives is passed to the roof closure and the power sizing; it is exactly 1 at the baseline, so no baseline value changes.
- `flow_graph/param/redundancy.json` lists the source units of every energy and life-support function. After the scaling actions each function keeps at least two. An import path does not count, following the owner's rule that an energy or life-support unit is eliminated only with a replacement of a different technology. The units listed there are energy or life-support units for the scaling rules.
- Regeneration writes `docs-authority/SITE_POWER.md` for the selected site. A locale run checks the portfolio and redundancy rules first.

## Defaults used

The source lists per function are the reference plant's and wait for the owner's confirmation, with the energy and life-support sectors (open decision 3).

## Not yet done

Sizing primary sources other than PV in the power sizing; heat rejection modes and radiator sizing; a stretch longer than a day.

## Check

`scripts/check_all.sh --full` passes. Baseline outputs are unchanged apart from the new document, the scaling table's function column and the registers.
