# Missing assays — TI_CELL and MO_CELL

Document number: AQS-ASSAY-TI-MO  
Revision: A  
Date: 2026-10-16  
Authority: graph Rev J, notes/TI_MO_DUTIES.md Rev B. Not a PE stamp.  
No rate is written until the named measurement is on the edge or this page still lists it as missing.

## FLOAT_SINK dense grit → TI_CELL

Edge: `FLOAT_SINK_GRIT_TO_TI`  
Missing measurement: elemental assay of the dense grit fraction (mass fraction Ti, Fe, and residual Si/Al/other).  
Required before any kg/d rate: Ti grade (as TiO₂ or FeTiO₃ equivalent) and Fe content.  
Status: missing. No composition is on the edge.

## EW_9 liquor → MO_CELL

Edge: `EW9_LIQUOR_TO_MO`  
Missing measurement: molybdenum concentration (mg/L or g/L) plus residual Zn, Fe, and Ni in the post-EW liquor.  
Required before any kg/d rate: Mo tenor and the three residuals that affect selectivity.  
Status: missing. No composition is on the edge.

## Disposition

Deferred to later work (2026-10-16). Literature ranges in notes/LIT_ASSAY.md may be used as referenced assumptions only. No plant measurement exists. Rates remain unset until this line is reopened.

See notes/LIT_ASSAY.md. Ilmenite/rutile and chromite commercial ranges are cited there and may be used only as referenced assumptions. No usable literature Mo tenor was found for the EW_9 liquor; that measurement remains missing.

A placeholder stoichiometric balance may be calculated for closure logic (see notes/KROLL_BALANCE.md). It is not a design rate. The edges remain open until the assays above are measured or explicitly carried as open measurements on the status board.
