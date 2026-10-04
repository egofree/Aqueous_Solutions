#!/usr/bin/env python3
"""Shared PFD style, names, and hardware parameters.

Import this from every diagram script so a name, color, wall spec,
or font change lands on every sheet.
"""

# ── canvas ───────────────────────────────────────────────
BG = "#f3efe6"
INK = "#1c1917"
MUTED = "#44403c"

# ── stream colors (locked across sheets) ─────────────────
C_SOLID, C_SOL_F = "#3f3f46", "#e4e4e7"
C_LEACH, C_LE_F = "#166534", "#dcfce7"
C_OIL, C_OIL_F = "#9a3412", "#ffedd5"
C_INORG, C_IN_F = "#1d4ed8", "#dbeafe"
C_HEAT, C_HEAT_F = "#b45309", "#fff7ed"
C_PROD, C_PROD_F = "#115e59", "#ccfbf1"
C_CEM, C_CEM_F = "#1d4ed8", "#93c5fd"
C_AEM, C_AEM_F = "#c2410c", "#fdba74"
C_AN, C_AN_F = "#9a3412", "#ffedd5"
C_CA, C_CA_F = "#1e3a8a", "#dbeafe"
C_HX, C_HX_F = "#7c2d12", "#fed7aa"

# ── type ─────────────────────────────────────────────────
# Plant sheet is denser; EW sheet is larger. Use these as defaults
# and override per-sheet if a title needs to shout.
FONT_TITLE = 32
FONT_SUBTITLE = 20
FONT_BOX = 24
FONT_BOX_SUB = 18
FONT_LABEL = 14
FONT_FOOT = 13
FONT_LEGEND = 14

# EW sheet runs larger so the whole-image view stays readable
EW_FONT_TITLE = 32.0
EW_FONT_SUBTITLE = 20.0
EW_FONT_BOX = 24.0
EW_FONT_BOX_SUB = 18.0
EW_FONT_CELL = 18.0
EW_FONT_CELL_SUB = 14.0
EW_FONT_FOOT = 14.0

# ── locked unit names (use these strings everywhere) ─────
NAME = {
    "oil": "OIL LINE",
    "glass": "SOLIDS LINE",
    "hopper": "HOPPER",
    "shredder": "SHREDDER",
    "leach1": "LEACH CSTR 1",
    "leach_fork": "LEACH CSTR 2–3    FORK",
    "float": "FLOAT DEWATER",
    "dryer": "DRYER",
    "pyro": "INDUCTION PYROLYZER",
    "quench": "QUENCH / CONDENSER",
    "still": "FRACTIONATOR",
    "cuts": "HYDROCARBON CUTS",
    "ew": "EW CASCADE",
    "afterburner": "AFTERBURNER",
    "bmed": "BMED REGEN",
    "metals": "METALS / ELEMENTS",
    "screen": "VIBRATORY SPLIT",
    "wash": "RINSE + DEWATER",
    "burnout": "BURNOUT ROTARY",
    "mill": "MILL",
    "digest": "NaOH DIGEST",
    "silicate": "SILICATE",
    "hydroxides": "Ca / Al / Mg HYDROXIDES",
    "grit": "CERAMIC GRIT",
    "fusion": "ALKALI FUSION",
    "aem": "AEM BANK",
    "silica": "SiO2 GEL",
    "reduce": "Si / B REDUCE",
    "molten": "MOLTEN-SALT CELLS",
    "ree_split": "PK-5B  REE SPLIT",
    "k_split": "K SPLIT",
    "n_scrub": "N SCRUB",
    "vdf": "VACUUM DRUM FILTER",
    "hx8": "HX-8   EW → Q3",
    "regen": "REGEN LEACH",
    "polish": "POLISH BANK",
    "naphtha": "NAPHTHA / LIGHTS",
    "midcut": "MID DISTILLATE",
    "gasoil": "GAS OIL / WAX",
    "residue": "RESIDUE / HEAVIES",
    "char": "CHAR / ASH",
    "ncg": "NCG",
    "demister": "DEMISTER",
    "oil_feed": "FLOAT + DENSE PLASTIC",
    "cru": "CRU / CHLORATE",
    "salt_feed": "SALT FEED",
    "base_tank": "NaOH PRODUCT",
    "acid_tank": "HCl PRODUCT",
    "polish_hdr": "POLISH HEADER",
    "rad_cell": "PK-9  RADIONUCLIDES",
}

# ── heat ladder ──────────────────────────────────────────
HEAT = {
    "Q1": {"label": "Q1    400–800 °C",
           "sub": "induction auger wall\npyrolysis vapor\nafterburner flue\nHX-1  ·  HX-2"},
    "Q2": {"label": "Q2    150–250 °C",
           "sub": "thermal-oil / steam loop\nHX-3 still reboiler\nHX-7 burnout jacket"},
    "Q3": {"label": "Q3    80–120 °C",
           "sub": "HX-4 dryer\nHX-5 leach CSTRs\nHX-6 digest   ·   HX-8 EW"},
    "Q4": {"label": "Q4    < 80 °C",
           "sub": "still condenser reject\nrinse water  ·  BMED feed\nHVAC / boiler makeup"},
}

HX = {
    "HX-1": "pyro wall",
    "HX-2": "flue → oil",
    "HX-3": "reboiler",
    "HX-4": "dryer Q3",
    "HX-5": "leach Q3",
    "HX-6": "digest Q3",
    "HX-7": "burnout Q2",
    "HX-8": "EW → Q3",
}

# ── walls (polymer — not titanium) ───────────────────────
WALL = {
    "anolyte": "CPVC or PVDF",
    "ew_early": "CPVC or PVDF",       # EW-1 Au, EW-2 Ag
    "ew_mid": "CPVC sheet",           # EW-3..8
    "ew_zn": "CPVC or PVDF",
    "leach": "CPVC or PVDF",
    "bmed_acid": "CPVC or PVDF",
    "bmed_base": "PP",
    "bmed_salt": "PP / CPVC",
    "p_al": "CPVC or PP",
    "p_mg": "PP",
    "p_ca": "PP",
    "polish": "CPVC",
}

CEMENT = "Weld-On 724 or equal (CPVC chemical-resistant). THF/MEK/cyclohexanone. Welds PVC and CPVC only — not PE, PP, or PVDF."

# ── EW aisle ─────────────────────────────────────────────
# tag, metal, E°, anode, cathode, wall key, product
EW_CELLS = [
    ("EW-1", "Au", "+1.50 V", "Ti Gr.2 / IrO2–Ta2O5\nMMO", "Ti Gr.2 blank", "ew_early", "powder"),
    ("EW-2", "Ag", "+0.80 V", "Ti Gr.2 / MMO", "Ti Gr.2 blank", "ew_early", "sheet / powder"),
    ("EW-3", "Cu", "+0.34 V", "Ti Gr.2 / MMO", "316L starter sheet", "ew_mid", "sheet"),
    ("EW-4", "Pb", "–0.13 V", "Ti Gr.2 / MMO", "316L sheet", "ew_mid", "sheet"),
    ("EW-5", "Sn", "–0.14 V", "Ti Gr.2 / MMO", "316L sheet", "ew_mid", "sheet / powder"),
    ("EW-6", "Ni", "–0.25 V", "Ti Gr.2 / MMO", "Ti Gr.2 blank", "ew_mid", "sheet"),
    ("EW-7", "Fe", "–0.44 V", "Ti Gr.2 / MMO", "316L or graphite", "ew_mid", "powder"),
    ("EW-8", "Cd", "–0.40 V", "Ti Gr.2 / MMO", "316L sheet", "ew_mid", "sheet"),
    ("EW-9", "Zn", "–0.76 V", "Ti Gr.2 / MMO", "Ti or Al starter", "ew_zn", "sheet"),
]

PH_SHIFT = [
    ("P-Al    pH 5.0–5.5", "Al(OH)3   filter cake", "p_al"),
    ("P-Mg    pH 10.5–11", "Mg(OH)2   filter cake", "p_mg"),
    ("P-Ca    pH 12–12.5", "Ca(OH)2 / CaCO3   cake", "p_ca"),
]

ANODE = "Ti Gr.2 / IrO2–Ta2O5 MMO"
BMED_CATHODE = "Ni / 316L"

# tag, target, E° or mode, anode, cathode/method, product
# Parallel bank after EW-9 + pH-shift. Low tenor. Not a second E° aisle.
POLISH_CELLS = [
    ("PK-1", "Co", "E° –0.28 V", "Ti Gr.2 / MMO", "316L sheet", "powder / sheet"),
    ("PK-2", "Mn", "metal or MnO2", "Ti Gr.2 / MMO", "Ti blank or MMO anode", "powder / MnO2"),
    ("PK-3", "Cr", "Cr(III) CEM", "Ti Gr.2 / MMO", "316L or Cr(OH)3 precip", "powder / cake"),
    ("PK-4", "Li", "not aqueous EW", "—", "CEM concentrate → Li2CO3 / Li3PO4", "carbonate / phosphate"),
    ("PK-5", "REE", "not aqueous EW", "—", "bleed before P-Al   oxalate cake → PK-5B", "cake to split"),
    ("PK-6", "Hg", "E° +0.85 V", "Ti Gr.2 / MMO", "Ti / graphite, sealed", "amalgam / metal"),
    ("PK-7", "Tl", "E° –0.34 V", "Ti Gr.2 / MMO", "316L or iodide precip", "powder / cake"),
    ("PK-8", "Bi / Sb", "E° +0.32 / +0.15", "Ti Gr.2 / MMO", "316L sheet", "powder"),
    ("PK-9", "U / Th / Ra / Po", "sealed CEM", "Ti Gr.2 / MMO", "Ti blank, isolated sump", "sludge → grit vitrify"),
]

# ── leach ────────────────────────────────────────────────
LEACH_T = "70–85 °C"
LEACH_ORP = "ORP > 1.5 V"
LEACH_CHEM = "HCl + NaClO3"

# ── pyro ─────────────────────────────────────────────────
PYRO_T = "400–600 °C"
PYRO_HW = "Ti shell  ·  cast-iron conical auger\ncoils heat the auger"
DRYER_T = "80–120 °C"
BURNOUT_T = "450–550 °C air / steam"
DIGEST_T = "80–90 °C"

# ── footer ───────────────────────────────────────────────
NAMING_FOOT = (
    "NAMING locked     LEACH CSTR 2–3 FORK    VACUUM DRUM FILTER    "
    "VIBRATORY SPLIT    BMED REGEN    HX-8 EW → Q3    METALS / ELEMENTS    "
    "Ca / Al / Mg HYDROXIDES    REGEN LEACH    OIL LINE    GLASS / CERAMIC BRANCH"
)

RULES_FOOT = (
    "RULES    Float organics → oil line.    Sink metals → EW.    "
    "Glass / ceramic / FR-4 → rinse · burnout · alkali.    "
    "No FR-4 in the Ti/iron auger.    "
    "Burnout jacketed by afterburner flue — atmospheres stay separate.    "
    "Pyro down → dryer waits; leach/digest idle on EW heat."
)

# ── output paths ─────────────────────────────────────────
from pathlib import Path

# Write next to the generators. If this file lives in a pfd_scripts/
# subfolder, PNGs go one level up (the project folder). If the user
# copied everything into one directory (e.g. ~/dev/Aqueous/Diagrams),
# PNGs land in that same directory. Never hard-code /home/workdir.
_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent if _HERE.name == "pfd_scripts" else _HERE
ROOT.mkdir(parents=True, exist_ok=True)

OUT_PLANT = ROOT / "continuous_recycling_pfd.png"
OUT_EW = ROOT / "ew_cascade_pfd.png"
OUT_OIL = ROOT / "oil_line_pfd.png"
OUT_GLASS = ROOT / "glass_ceramic_pfd.png"
OUT_BMED = ROOT / "bmed_regen_pfd.png"
OUT_POLISH = ROOT / "polish_bank_pfd.png"
OUT_CONTAINER = ROOT / "container_layout.png"
OUT_ELEC = ROOT / "electrical_sld.png"
OUT_BATTERY = ROOT / "znbr2_flow_pfd.png"
OUT_HYDRO_DOCK = ROOT / "hydro_dock_pfd.png"
OUT_WET = ROOT / "wet_line_factory_pfd.png"
