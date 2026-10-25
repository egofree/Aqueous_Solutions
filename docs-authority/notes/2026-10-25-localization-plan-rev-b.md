# Localization plan revision B

Date: 2026-10-25. Documents: AQS-PLAN-011 Rev B, AQS-OQ-001, AQS-PLAN-007.

## Decision

Each plant is built to suit its site, with systems specified for the local power and resource availability. The full single-building plant is the reference ideal, not a build target. Every sector and unit may be sized up, sized down, duplicated, replaced or eliminated; eliminating a function needs an import path or a replacement of a different technology. Power sources are chosen per site, and the oversize rule applies per site to the worst stretch. A floating island is added as a model locale.

## Changes

- AQS-PLAN-011 Rev B: section 5 replaced by the scaling model and the power portfolio; section 10 (floating island) added; gaps, build order, checks and questions updated.
- Q-024 closed by the owner decision above; Q-030 and Q-031 added for the floating island.
- Tasks X-LOC-05 to X-LOC-12 revised or added in `docs-authority/_task_plan_gen.py`.
- Glossary entries added for the marine abbreviations.

## Check

`scripts/check_all.sh` passes.
