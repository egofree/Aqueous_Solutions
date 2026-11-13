"""The electrowinning cell-to-element booking map (AQS-ASSAY-001 table 4.1; owner ruling Q-038, 2026-11-05).

Cells 1 to 9 in cascade order. Cells 1 to 3 and 7 book their own element; the five minor
plateable cells (MINOR_CELLS) share the lumped other_plateable class of the assay table, which
A-M-470 splits evenly across them. The element molar masses are constants.M; the valences are
the chloride-electrowinning charges (USBM_CL_EW). This table is the single source: solver.ew_products
books the deposits from it and docs-authority/_ew_sizing.py rates the cell equipment from it.
The Q-041 arrangement (driver ew_minor_metal_arrangement, A-M-494) is a layout choice downstream
of this map, which stays the element map in both values: under 'merged' the blend books on
MINOR_CELLS[0] and the other four minor cells idle; the booking ledger does not move.
"""

EW_CELLS = {1: ('Au', 3, 'Au'), 2: ('Ag', 1, 'Ag'), 3: ('Cu', 2, 'Cu'),
            4: ('Pb', 2, 'other_plateable'), 5: ('Sn', 2, 'other_plateable'),
            6: ('Ni', 2, 'other_plateable'), 7: ('Fe', 2, 'Fe'),
            8: ('Cd', 2, 'other_plateable'), 9: ('Zn', 2, 'other_plateable')}

MINOR_CELLS = (4, 5, 6, 8, 9)   # the lumped other_plateable class (A-M-470)
