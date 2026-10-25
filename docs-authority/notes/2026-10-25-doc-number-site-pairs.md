# Document number and site pairs

Date: 2026-10-25. Documents: AQS-PLAN-011 Rev D, AQS-REG-001 (document register).

## Change

- `docs-authority/_doc_register.py` reads a document number with a locale suffix, for example `AQS-THM-002/MARS`, and registers the number and site pair.
- The new function `pair_problems()` reports a pair claimed twice, a suffix that is not the `site_code` of a locale profile in `flow_graph/param/sites/`, a suffix used for the baseline, a pair whose base number no baseline page claims, and a page under `sites/<site_id>/` without that site's code.
- `flow_graph/test_doc_numbers.py` checks each rule on synthetic pages and checks that site codes are unique.

## Effect

No page carries a suffix yet, so `DOC_REGISTER.md` is unchanged.

## Check

`scripts/check_all.sh --full` passes.
