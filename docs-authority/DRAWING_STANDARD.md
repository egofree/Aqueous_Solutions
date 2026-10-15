# Drawing standard and title block

Document number: AQS-DWG-001
Revision: A
Date: 2026-10-15
Authority: AQS-PLAN-007 X-DWG-01. Study. Applied by `docs-authority/_drawings.py`; register AQS-DWG-002 (`DRAWING_REGISTER.md`).

## 1. Basis

Construction jurisdiction is the USA (AQS-STD-003), so drawing practice follows ASME: sheet size and format ASME_Y14_1 (metric sheets per Y14.1M), drawing practices and numbering ASME_Y14_100, revisions ASME_Y14_35, dimensioning and tolerancing ASME_Y14_5. Title-block data fields follow ISO_7200. Flow-diagram symbols follow ISO_10628_2.

## 2. Numbering

| Drawing type | Number | Example |
|---|---|---|
| Flow diagram generated from the graph | AQS-DWG-PFD-<view> | AQS-DWG-PFD-PFD |
| Piping isometric | AQS-ISO-002-<line> | AQS-ISO-002-C29_RECYCLE |
| Motor family assembly | AQS-INV-005-<family> | AQS-INV-005-MF-07 |
| Fabrication model (model-based definition) | AQS-MFG-<unit> | AQS-MFG-MEOH_SYNTH |
| Fabrication drawing (unit task 11) | AQS-FAB-<unit>-<nnn> | AQS-FAB-LEACH_CSTR_1-001 |

One number per drawing; sheets of a multi-sheet drawing share the number (sheet n of m).

## 3. Sheet sizes

Metric A-series per ASME_Y14_1 (Y14.1M): A0 841 x 1189, A1 594 x 841, A2 420 x 594, A3 297 x 420, A4 210 x 297 mm. Isometrics and assemblies A3; fabrication drawings A1 or A2; graph-generated flow diagrams are unbounded SVG (screen and plotter use) with the title block at the lower right of the view box.

## 4. Title block and revision

Fields (ISO_7200): legal owner (Aqueous Solutions), identification number, title, document type, revision index, date of issue, creator, approver, sheet. Approval reads "not approved (study)" until a PE or the owner signs; nothing in this package is a PE stamp.

Revision index: the first 8 hex digits of the SHA-256 of the drawing content without its title block. It changes exactly when the drawing changes, which is the intent of ASME_Y14_35 (every change identified). Issued drawings move to letter revisions (A, B, ...) with a revision history block when the package is released (X-DWG release task); graph-generated diagrams also print the SHA-256 of the graph they were generated from.

## 5. Fabrication drawings

Dimensions and tolerances per ASME_Y14_5; welds per AWS_A2_4 symbols; general tolerance block in the title area; material and finish called out per part. The STEP models in models/mfg are the model-based definition until each unit task 11 issues its sheet.
