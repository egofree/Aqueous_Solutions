# Foam-board EW cascade (1:3)

AQS-FOAM-001. Nine funnel cells on a bund, cut from 4×8 ft × 6 mm
expanded (foam-core) PVC. Duty: wet Salria coupon at bench temperature.
Plant wet wall remains solid CPVC sheet (70–85 °C).

```
python3 generate.py
```

| File | What |
|---|---|
| `DECISIONS.md` | Scale, sheet, joint |
| `params.py` / `params.scad` | One number set |
| `CUT_LIST.md` | Buy + glue order |
| `cut_list.csv` | Same table |
| `aisle.png` | Plan of EW-1…9 |
| `cell_unfold.png` | One-cell net |
| `nest_sheet_1.png` `nest_sheet_2.png` | 4×8 nests |
| `foam_cascade.scad` | Assembled 3D (operator OpenSCAD) |

Buy **two** 4×8 × 6 mm sheets. Change `SCALE` or `T` only in `params.py`
and `params.scad`, then rerun the generator.

This folder is the only copy. `generate.py` writes `CUT_LIST.md` and
`cut_list.csv` here. Copies that used to sit in `docs-authority/` and `tables/`
were removed on 2026-10-24; they are in git history.
