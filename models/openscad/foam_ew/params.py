"""1:3 foam-board EW cascade. Keep in lockstep with params.scad."""

SCALE = 1.0 / 3.0

# Plant cell (mm), then scaled and snapped to whole mm.
PLANT_L = 600
PLANT_W = 420
PLANT_H = 650
PLANT_FUNNEL_H = 220
PLANT_PITCH = 750
PLANT_BUND_H = 150
PLANT_BUND_PAD = 250

T = 6  # sheet thickness
TAB = 12  # glue tab
KERF = 2  # nest gap

ID_L = round(PLANT_L * SCALE)  # 200
ID_W = round(PLANT_W * SCALE)  # 140
ID_H = round(PLANT_H * SCALE)  # 217
FUNNEL_H = round(PLANT_FUNNEL_H * SCALE)  # 73
PITCH = round(PLANT_PITCH * SCALE)  # 250
BUND_H = round(PLANT_BUND_H * SCALE)  # 50
BUND_PAD = 40  # tighter than scaled 83 — table mockup

THROAT = 16  # drain hole
SLOT = T  # CEM gap = one sheet
RIB_H = ID_H - 20
RIB_L = ID_L - 20

OD_L = ID_L + 2 * T  # 212
OD_W = ID_W + 2 * T  # 152

N_CELLS = 9
METALS = ("Au", "Ag", "Cu", "Pb", "Sn", "Ni", "Fe", "Cd", "Zn")

SHEET_W = 1219  # 4 ft
SHEET_L = 2438  # 8 ft
MARGIN = 15

AISLE_LEN = N_CELLS * PITCH
AISLE_W = OD_W + 2 * BUND_PAD
