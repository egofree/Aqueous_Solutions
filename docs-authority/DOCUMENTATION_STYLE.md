# Documentation style — Aqueous house style

Document number: AQS-DOC-001  
Revision: A  
Date: 2026-10-01  
Authority: AQS-AUTH-001. Applies to **authority hub** markdown under
`docs-authority/*.md`, `docs-authority/*.md`, and hub sheets named in AUTHORITY.md
(e.g. `ELECTRICAL.md`). Does **not** mandate a rewrite of root narrative
folders (`01-…`–`09-…`, POWER/, GAS_SYSTEM/, etc.).

| Rev | Change | Description | Date |
|---|---|---|---|
| A | — | House style from KSC-DF-107 Rev F + IET technical report guide | 2026-10-01 |

Licence: CERN-OHL-S-2.0. Not a claim of KSC or IET issuance.

## 1. Purpose

Give every authority document a consistent identity and wording so
readers can trust shall/should language, find scope quickly, and sync
the share tree without fabricating permits or clause text.

## 2. Scope

| In | Out |
|---|---|
| Document number, revision letter, date | KSC title-block / export-control banner on every file |
| Purpose / scope / authority block | Rewriting GLOSSARY into print typography |
| Shall / should / will usage | Changing locked plant unit names |
| Abbreviations; figure/table titles | Root narrative prose folders |
| Record-of-revisions table | Git history as the revision record |

Practical companion (warnings, signs): `docs-authority/DOC_STYLE.md` (kept; points here).

## 3. Source standards (verified copies)

| Standard | Edition | Local copy |
|---|---|---|
| KSC-DF-107, *Technical Documentation Style Guide* | **Revision F, 2017-07-08** | Box: `/workspace/standards/ksc-df-107_rev_f.pdf` (+ `.txt` extract) |
| IET, *A Guide to Technical Report Writing* | **© The IET 2015** (box PDF) | `/workspace/standards/iet_technical_report_writing.pdf` (+ `iet.txt`) |

Older notes that cited “IET 2020-01-16” are superseded by the box PDF
edition above for this house style.

## 4. Document identity (every authority file)

Place near the top, after the title:

```
Document number: AQS-XXX-###
Revision: <letter>
Date: YYYY-MM-DD
```

Then, as applicable: Authority / PFD / Equipment / Streams lines,
licence line, and a **Record of revisions** table (Rev | Change |
Description | Date). Revisions are letters (A, B, …). Do not log drafts.

## 5. Purpose and scope

Authority docs **shall** state:

1. **Purpose** — why the file exists (one short paragraph or §1).
2. **Scope** — what it controls and what it explicitly does not.

IET Law 1: the reader is the most important person. Keep the report
(or note) as short as the reader needs (IET Law 2).

## 6. Shall, should, will (KSC-DF-107 §3.4 theme)

Aligned with KSC wording practice and existing Aqueous DOC_STYLE:

| Word | Use |
|---|---|
| **shall** | Binding design requirement inside Aqueous authority |
| **should** | Recommendation; deviation needs a recorded reason |
| **will** | Statement of fact or expected future action (not a soft shall) |
| **must** | Avoid for requirements; prefer **shall** (KSC preference theme) |

Do not use shall for historical narrative. Do not state code clause
obligations as shall unless a cited edition was verified.

## 7. Abbreviations (KSC §3.5 theme)

Spell out at first use unless:

- SI unit beside a value (12 mm, 70 °C), or
- Locked plant name from `GLOSSARY.md` / PFD tags (LEACH CSTR 1,
  HDR_H2, Sol-Ark, ZnBr2).

Locked names are **names**, not expandable abbreviations.

## 8. Headings, figures, tables (IET)

- Decimal headings preferred for long notes: 1, 1.1, 1.1.1 (≤ four levels).
- Every figure and table **shall** have a number and a brief title
  (e.g. Table 3 — Stream register S64–S72).
- Place the illustration where the reader needs it (IET Law 6).
- Do not rely on colour alone.

## 9. Voice and accuracy

- Prefer active voice and short sentences (KSC §3 / IET §3).
- Metric first; do not split a value from its unit across a line.
- Mark study estimates explicitly; never present them as vendor
  nameplates (AQS-AUD-001 rule).
- WARNING / CAUTION / NOTE callouts follow `docs-authority/DOC_STYLE.md`
  (KSC §3.20 theme).

## 10. Authority hub — worst-offender checklist

When touching an authority file, fix if missing:

- [ ] Document number / Rev / Date
- [ ] Purpose or Scope section
- [ ] Revision table
- [ ] Consistent shall/should
- [ ] Cross-ref to parent AQS-* ID
- [ ] Sync path note (canonical vs share) on long-lived locks

Priority files for Wave 2: FUEL_CELL, CRYO_COLD_BOX, VENT_CLOSURE,
GEOTHERMAL_BACKUP, BUILDING_STACK, STREAM_REGISTER, REMAINING_BLD,
local planning SECTOR_CAPACITY_AUDIT (not published), HAZARD_SEPARATION, SITE_ACCESS, ELECTRICAL,
COMPLIANCE_MATRIX, this file.

## 11. Sync

Canonical in this tree: `docs-authority/DOCUMENTATION_STYLE.md`  
