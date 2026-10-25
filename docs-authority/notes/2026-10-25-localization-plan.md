# Localization plan issued

Date: 2026-10-25. Documents: AQS-PLAN-011, AQS-OQ-001, AQS-PLAN-007.

## Decision

The plant will be designed for more than one locale by making the site an input to the parametric model. AQS-PLAN-011 (`docs-authority/LOCALIZATION_PLAN.md`) records where the site is held today, the Earth-surface conditions fixed in code, a site profile file per locale, unit needs with capability decisions, the design consequences for Death Valley, Antarctica, Mars and low Earth orbit, the build order and the acceptance checks.

## Changes

- AQS-PLAN-011 issued; number from `python3 docs-authority/_doc_register.py --next AQS-PLAN`.
- Tasks X-LOC-01 to X-LOC-10 added to `docs-authority/_task_plan_gen.py`; X-LOC-01 closed with the plan as evidence.
- Owner questions Q-020 to Q-029 added to AQS-OQ-001 with the defaults the work proceeds on.
- Glossary entries added for the abbreviations the plan uses.
- No change to the graph, the drivers or any sizing output.

## Check

`scripts/check_all.sh` passes.
