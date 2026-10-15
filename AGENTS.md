# Agent rules

Follow the plan file. Do not keep a second list of exceptions.

## Loop

1. Read the plan. The master task list is `docs-authority/TASK_PLAN.md` (AQS-PLAN-007). The engineering limits and holds are in `docs-authority/PROJECT_PLAN.md`. The close-out record of plan lines is `docs-authority/MASTER_PLAN.md`. Check a task on AQS-PLAN-007 only with a cited file, and rerun `docs-authority/_task_plan_gen.py`. The plan names the authority and the active item.
2. Read only the authority the active item needs. Confirm the item is still the active one.
3. Do that item. Stay inside what it asks.
4. Prove it. Run the check the plan states for that item. The check is on the files, not on the intention.
5. Write the proof back. In the same commit, set the line on the status board and update every page the change made untrue. A revision note moves with a revision. A drawing or a derived file that still names an older revision is marked or regenerated. The next session starts from the files alone.
6. Stop. The item is done when its check passes and the board matches the files. If the check cannot pass, write the missing fact on the board and stop. The next item waits.

## Assumptions

Every new assumption gets an entry in `docs-authority/assumptions_manual.json` in the same commit (value, units, where used, basis, sensitivity, replacing test, task). Run `docs-authority/_assumptions_register.py`; it regenerates AQS-REG-002 and fails on a bad entry.

## Done

Housekeeping is part of the item, not a later pass. A commit that changes the work and leaves the board or a contradicted page behind is not done.

The plan holds the engineering limits. Read them there when the item touches them. Do not copy them into this file.
