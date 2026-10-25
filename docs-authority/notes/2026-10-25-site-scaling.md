# Site scaling actions and unit needs

Date: 2026-10-25. Documents: AQS-PLAN-011 Rev H, AQS-SITE-004 (new, generated), AQS-PLAN-007 (X-LOC-05 done).

## Change

- `flow_graph/param/unit_needs.json` gives the environmental needs of each unit class, with unit overrides, and the function of each sector (energy or life support, from the AGENTS.md redundancy list).
- Each profile carries a `capabilities` group (one entry per need) and a `scaling` group (the actions). The baseline provides every capability and applies no action.
- `flow_graph/param/scaling.py` resolves the actions and enforces the rules of AQS-PLAN-011 section 5.4. A locale run checks them before it regenerates.
- Regeneration writes `docs-authority/SITE_SCALING.md` for the selected site.

## Not yet done

The count of sources per energy or life-support function against the redundancy rule needs the source models of X-LOC-06.

## Check

`scripts/check_all.sh --full` passes. The baseline outputs are unchanged apart from the new document and the registers.
