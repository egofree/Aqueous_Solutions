# Documentation style (practical application)

Applies to engineering notes, sign schedules, handoffs, and new
markdown in this repository. Not a claim of KSC or IET issuance.

## 1. Sources

- KSC-DF-107 Revision F (2017-07-08), Technical Documentation Style
  Guide, Kennedy Space Center.
- IET, *A Guide to Technical Report Writing* (© The IET 2015; box PDF).
- **House style authority:** `cad/DOCUMENTATION_STYLE.md` (**AQS-DOC-001**).
- Compliance theme map: `cad/COMPLIANCE_MATRIX.md` (**AQS-CMP-001**).

KSC-DF-107 governs wording of WARNING / CAUTION / NOTE and general
engineering prose. The IET guide governs report structure when a
stand-alone report is written. Neither document specifies factory
sign geometry; ANSI Z535 header bars are used on the plates.

## 2. Voice and words (KSC §3 and IET)

Write short complete sentences. Prefer active voice. Do not pad.
Shall = requirement. Should = recommendation. Will = statement of
fact. Spell out an abbreviation at first use unless it is an SI unit
next to a value, or a locked plant name from GLOSSARY.md.

Locked plant names stay in the form already used on the PFDs
(LEACH CSTR 1, not “leach CSTR one”). They are names, not
abbreviations of the KSC document-number type.

Units: metric first. A value and its unit do not split across a line.
Example: 12 mm, 70 °C to 85 °C, 150 kg/d.

## 3. Warnings in documents (KSC-DF-107 §3.20)

Place the title immediately after the paragraph it belongs to.

**WARNING**

Critical information. Ignoring it may injure or kill someone.

**CAUTION**

Important information. Ignoring it may damage or destroy equipment.

**NOTE**

Emphasis only. Reduces misinterpretation.

Order if several apply: WARNING, then CAUTION, then NOTE. Keep the
statement on the same page as the title. Do not use DANGER in
running text unless the sign schedule already uses that header.

## 4. Headings and figures (IET)

Decimal headings: 1, 1.1, 1.1.1. Four levels is enough. Figure and
table numbers use the section number (Figure 3.7). Captions are
brief. Do not rely on colour alone to carry meaning.

## 5. Revisions (KSC §5.3, §6)

Record of revisions sits near the top of long notes:

| Rev | Change | Description | Date |
|---|---|---|---|
| — | — | Basic issue | 2026-09-26 |

Revisions are letters (A, B, …). Changes are “Revision A Change 1”.
Do not log drafts.

## 6. Signs versus documents

Face text for every plate is in SIGN_SCHEDULE.md. Safety-sign faces
are four lines: signal word, locked unit name, hazard, instruction.
`labels.py` cuts those lines with Part.makeWireString when Liberation
Sans Bold is installed. If no font is found, the plate stays blank
and the schedule remains the authority.

## 7. What we are not doing

We are not putting a KSC title block or export-control banner on
every markdown file. We are not rewriting GLOSSARY.md into 12-point
Times New Roman. Those rules apply when a formal report is issued.
