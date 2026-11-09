# Audit findings

Quality Control and Nightly Audit Engineer write audit results here so OpenCode
sessions and Grok Bots share one on-disk source of truth.

## Layout

- Dated audit reports: `AUDIT_YYYY-MM-DD_<source>.md` (for example
  `AUDIT_2026-11-08_qc.md` or `AUDIT_2026-11-08_nightly.md`).
- Running open list: `OPEN_FINDINGS.md`.

## Finding identifiers

Each finding uses an id of the form `F-YYYYMMDD-NN` (calendar day of the audit,
two-digit sequence within that day). Keep the id stable when the finding moves
from open to fixed to closed.

## Open findings table

`OPEN_FINDINGS.md` lists every finding that is not yet closed. Columns:

| Column | Meaning |
| --- | --- |
| id | `F-YYYYMMDD-NN` |
| severity | critical, high, medium, or low |
| file | Path relative to the repository root, or `n/a` |
| description | One or two sentences stating the defect |
| status | `open`, `fixed` (with commit hash), or `closed` |

## Lifecycle

1. An audit adds rows with status `open` and writes the dated audit file.
2. A fixing session reads `OPEN_FINDINGS.md` before starting work, applies the
   fix, and sets status to `fixed` with the commit hash that contains the fix.
3. Quality Control verifies the fix and sets status to `closed`, or reopens it
   with a short note if the fix is incomplete.
4. When a session finishes or is blocked on a finding, it calls the OpenCode
   tool `report_status` and includes the finding ids.
