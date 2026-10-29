# Rewrite batch 30: retired routes leave the line list and the isometric sheets

Date: 2026-10-29

Owner decision: anything truly obsolete is eliminated, without losing anything of value. A route set to presence retired on the graph has no line to build, so its line-list row, its route and its isometric sheet are obsolete. Until now the line list read every edge whatever its presence, so retired routes kept their rows and sheets.

## What changed

- `docs-authority/_line_list.py` skips routes whose presence is retired. The isometric routes, the sheets, the supports, the pipe inventory, the piping and instrument sheets, the unit bills of materials and the controller listing follow it through the regenerator.
- `docs-authority/_iso_sheets.py` removes a sheet whose line is no longer on the line list, so the sheet set follows the graph instead of keeping stale files.
- `docs-authority/retired_names.json` records each removed sheet.

No content decision of the held isometric drawing index is touched: only rows and files of retired routes go.

## Sheets removed

| Sheet | Why the route is retired | Cited elsewhere |
|---|---|---|
| Sheet of UPW_TO_FAB | It duplicates IA-UPW-FAB from the same polisher (batch 29). | Only the generated drawing register, which follows. |
| Sheet of S36 | Its note names the live path that replaced it (batch 25). | Only the generated drawing register. |
| Sheet of S39B | Its note names the live path that replaced it (batch 25). | Only the generated drawing register. |
| Sheet of HL-HX8-Q3-A | Dead since heat-ladder revision J, superseded by the Q4 cross-ties (owner rulings 2026-10-18). | Only the generated drawing register. |
| Sheet of HL-HX8-Q3-B | As HL-HX8-Q3-A. | Only the generated drawing register. |

The other routes retired in batch 25 (MO_CELL_RAFFINATE, EW9_LIQUOR_TO_MO, EW_METALS_TO_IND) and SF-LITHO_STUB had no sheet, because one of their ends has no position; they now leave the line list as well.

## Values

The sheet set drops from 266 to 261 sheets. Pipe falls from 4,602 m to 4,500 m, elbows from 761 to 746, flanges from 532 to 522 and joints from 2,445 to 2,394. The graph does not change, so the bus demand, the array, the storage and the balance closure do not move.
