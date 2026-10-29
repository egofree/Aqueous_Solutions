# SPDX-License-Identifier: CERN-OHL-S-2.0
"""Table 12.1 of the localization plan (AQS-PLAN-011) agrees with the task plan (AQS-PLAN-007).

Every X-LOC task in TASK_PLAN.md has one row in Table 12.1, and the row's status
starts with "done" exactly when the task plan ticks the task.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_build_order_status_matches_task_plan():
    plan = (ROOT / "docs-authority" / "TASK_PLAN.md").read_text(encoding="utf-8")
    loc = (ROOT / "docs-authority" / "LOCALIZATION_PLAN.md").read_text(encoding="utf-8")
    ticked = {t: box == "x" for box, t in re.findall(r"^- \[( |x)\] \*\*(X-LOC-\d+)\*\*", plan, flags=re.M)}
    table = loc[loc.index("Table 12.1."):loc.index("## 13.")]
    rows = {t: st.strip() for t, st in re.findall(r"^\| (X-LOC-\d+) \|[^|]*\|[^|]*\|([^|]*)\|$", table, flags=re.M)}
    assert ticked, "no X-LOC task found in TASK_PLAN.md"
    assert set(rows) == set(ticked), f"tasks missing from Table 12.1: {sorted(set(ticked) - set(rows))}; rows with no task: {sorted(set(rows) - set(ticked))}"
    wrong = [t for t in ticked if rows[t].startswith("done") != ticked[t]]
    assert not wrong, f"Table 12.1 status disagrees with the task plan for {wrong}"
