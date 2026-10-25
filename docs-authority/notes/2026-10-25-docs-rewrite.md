# 2026-10-25 — documentation rewrite to AQS-DOC-002

This record covers the rewrite of pages under `docs-authority/` to the documentation style guide (AQS-DOC-002). The progress of the rewrite, page by page, is tracked in `docs-authority/REWRITE_TODO.md` (AQS-DOC-003). No graph, driver, rate or topology change is made by this work.

## Batch 1

- `DOC_REGISTER.md` (AQS-REG-001) Rev C: purpose and scope added and the rules rewritten, in the generator `docs-authority/_doc_register.py`. The generator now cuts a part qualifier at the end of its first sentence, so that entries such as `AQS-INV-005 sheet MF-01` no longer show part of the following sentence.
- `PROJECT_PLAN.md` (AQS-PLAN-005) Rev C: rewritten in full. The phases, limits and values are unchanged. The hard-coded count of duty pages was removed.
- `TASK_PLAN.md` (AQS-PLAN-007) Rev C: sections 1 to 6 rewritten in `docs-authority/_task_plan_gen.py`. The list of next tasks is now generated from the triage tags of the open cross-cutting tasks. The hand-kept list and the progress record that had accumulated in that section are kept, as written, in Appendix A.
- `OPEN_QUESTIONS.md` (AQS-OQ-001) Rev B: purpose and scope added. The question rows are unchanged.
- `REWRITE_TODO.md` (AQS-DOC-003): new page, number from `_doc_register.py --next AQS-DOC`.
- `GLOSSARY.md`: BLD added.
- `README.md` (documentation map): the row for `DOCUMENTATION_STYLE.md`, which was merged into `DOC_STYLE.md` on 2026-10-24 and no longer exists, was removed.
