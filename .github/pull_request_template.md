## What this changes

<!-- One or two sentences. Name the TASK_PLAN item(s) (e.g. X-PAR-02, FOUNDRY-AL_POT-11) or the issue. -->

## Evidence

<!-- The file(s) that prove the change: calculation, generated document, test. -->

## Checklist

- [ ] `scripts/check_all.sh --full` passes on my machine (tests, staleness, authority contract, citations, documentation style, full regeneration)
- [ ] Generated files were regenerated, not hand-edited
- [ ] New numbers cite a reference registered in `flow_graph/param/refs.py` or an entry in `docs-authority/assumptions_manual.json`
- [ ] TASK_PLAN regenerated if a task closed (`python3 docs-authority/_task_plan_gen.py`)
- [ ] New or changed text, including generator templates, follows [docs-authority/DOC_STYLE.md](../docs-authority/DOC_STYLE.md)
- [ ] No secrets, personal data, machine-specific paths, or agent scratch files added
- [ ] I agree that this contribution is made under CERN-OHL-S-2.0 (see CONTRIBUTING.md)
