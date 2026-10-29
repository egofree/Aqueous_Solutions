# Localization tracker brought in line with the task plan and the locale runs

Date: 2026-10-29. Documents: AQS-PLAN-011 Rev K, AQS-PLAN-007, AQS-SITE-006 Rev C, AQS-SITE-007 Rev B, AQS-SITE-008 Rev B, AQS-SITE-009 Rev E, AQS-SITE-010 Rev C.

## Evidence

Each locale was regenerated with `python3 -m flow_graph.param.regen --site <site_id>` on 2026-10-29 (Antarctic, Death Valley, floating island, Mars and low Earth orbit). Every run completed. Every site design check passed, except Death Valley, which failed on the GW_INTAKE balance until the design check stopped balancing intake units (`2026-10-29-design-check-intakes.md`); the rerun passes.

## Change

- AQS-PLAN-011 Table 12.1 had X-LOC-07, X-LOC-08, X-LOC-10, X-LOC-11 and X-LOC-12 open while the task plan ticked them, and had no row for X-LOC-13. It now lists every X-LOC task with the task plan status and the run evidence, and `flow_graph/test_localization_plan.py` fails when the two disagree. Sections 2 and 13 no longer call the site profiles future work.
- X-LOC-11 is reopened in `docs-authority/_task_plan_gen.py`: the hull check passes, but the seawater intake and desalination units stay placeholders in the floating-island profile and no mineral-recovery unit exists, which the task's Done-when requires.
- X-LOC-09 cites `docs-authority/SITE_BASIS_MARS.md` as its evidence; the task plan printed `None`.
- The Antarctic page no longer says its locale run is blocked. The Mars page revision line matches its record of revisions. Hand-written output counts on the Mars, low Earth orbit and floating-island pages are replaced by the file that reports them.
