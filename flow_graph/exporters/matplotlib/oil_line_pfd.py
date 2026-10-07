#!/usr/bin/env python3
"""OIL LINE detail sheet. Wide row layout, same pitch as the disassembly sheet."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import params as P
from drawlib import box, cx, cy, R, L, T, B, arrow, slabel, hx_diamond, legend_strip

fig, ax = plt.subplots(figsize=(34.0, 22.0), dpi=140)
ax.set_xlim(0, 168)
ax.set_ylim(-8.0, 112)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)

ax.text(84, 110.4, "OIL LINE  —  FLOAT · DRY · PYROLYZE · DISTILL",
        ha="center", va="top", fontsize=28, fontweight="bold", color=P.INK)
ax.text(84, 107.6,
        "Leach float and dense-plastic jumper at the head    ·    hydrocarbon cuts at the bottom    ·    NCG to AFTERBURNER",
        ha="center", va="top", fontsize=16.2, color=P.MUTED)

ax.text(2.0, 105.4, "1   FEED", fontsize=17.5, fontweight="bold", color=P.INK)
leach = box(ax, 2.0, 96.6, 50.0, 6.4, P.C_LE_F, P.C_LEACH, P.NAME["leach_fork"],
            "float skim → this sheet", ts=18.2, ss=13.2)
ew = box(ax, 56.0, 96.6, 36.0, 6.4, P.C_SOL_F, P.C_SOLID, P.NAME["ew"],
         "not a feed to this sheet", ts=18.0, ss=13.0)
split = box(ax, 96.0, 96.6, 70.0, 6.4, P.C_SOL_F, P.C_SOLID, P.NAME["screen"],
            "dense plastic jumper → dryer", ts=18.2, ss=13.2)

ax.text(2.0, 94.4, "2   DRY", fontsize=17.5, fontweight="bold", color=P.INK)
flt = box(ax, 2.0, 85.6, 78.0, 6.6, P.C_OIL_F, P.C_OIL, P.NAME["float"],
          "weir / DAF    light plastic · paper · wood · insulation fiber", ts=18.2, ss=13.2)
dry = box(ax, 86.0, 85.6, 64.0, 6.6, P.C_OIL_F, P.C_OIL, P.NAME["dryer"],
          f"paddle / belt    {P.DRYER_T}    condensate → Q4", ts=18.0, ss=13.0)
arrow(ax, B(leach), T(flt), P.C_OIL, lw=1.6)
arrow(ax, B(split), (cx(dry), dry[1] + dry[3]), P.C_OIL, lw=1.5)
arrow(ax, R(flt), L(dry), P.C_OIL, lw=1.6)
h4 = hx_diamond(ax, 160.0, 88.9, "HX-4", P.HX["HX-4"])
arrow(ax, (h4[0] - 1.8, h4[1]), R(dry), P.C_HEAT, lw=1.15, ls="--")

ax.text(2.0, 83.2, "3   PYROLYZER    dry charge    liquor never enters this pipe",
        fontsize=17.5, fontweight="bold", color=P.INK)
ax.add_patch(FancyBboxPatch(
    (2.0, 66.2), 148.0, 14.8,
    boxstyle="round,pad=0.1,rounding_size=0.28",
    facecolor=P.C_OIL_F, edgecolor=P.C_OIL, linewidth=1.5, zorder=2,
))
ax.text(76.0, 79.8, P.NAME["pyro"], ha="center", va="top",
        fontsize=18.5, fontweight="bold", color=P.INK, zorder=4)
ax.text(76.0, 77.9, f"{P.PYRO_T}    coils heat the auger, not the charge    no FR-4 in this pipe",
        ha="center", va="top", fontsize=13.6, color=P.MUTED, zorder=4)
coil = box(ax, 4.2, 67.4, 32.0, 8.6, P.C_HEAT_F, P.C_HEAT, "INDUCTION COILS",
           "outside the Ti shell    couple to the iron auger", ts=16.4, ss=12.4)
shell = box(ax, 40.0, 67.4, 36.0, 8.6, P.C_SOL_F, P.C_SOLID, "Ti OUTER PIPE",
            "Grade 2 shell    not a liquor wall    charge is dry", ts=16.6, ss=12.4)
auger = box(ax, 80.0, 67.4, 40.0, 8.6, P.C_SOL_F, P.C_SOLID, "CAST-IRON AUGER",
            "forced plug flow    fractures polymer → dirty crude", ts=16.4, ss=12.4)
outp = box(ax, 124.0, 67.4, 22.0, 8.6, P.C_OIL_F, P.C_OIL, "OUTLET",
           "smaller bore", ts=16.6, ss=12.4)
arrow(ax, R(coil), L(shell), P.C_HEAT, lw=1.4)
arrow(ax, R(shell), L(auger), P.C_SOLID, lw=1.4)
arrow(ax, R(auger), L(outp), P.C_OIL, lw=1.4)
arrow(ax, B(dry), T(shell), P.C_OIL, lw=1.6)
h1 = hx_diamond(ax, 160.0, 71.7, "HX-1", P.HX["HX-1"])
arrow(ax, R(coil), (h1[0] - 1.8, h1[1]), P.C_HEAT, lw=1.1, ls="--")

ax.text(2.0, 64.0, "4   QUENCH AND STILL", fontsize=17.5, fontweight="bold", color=P.INK)
quen = box(ax, 2.0, 55.2, 52.0, 6.4, P.C_OIL_F, P.C_OIL, P.NAME["quench"],
           "direct oil quench    vapor down    NCG across", ts=17.2, ss=12.8)
dem = box(ax, 58.0, 55.2, 36.0, 6.4, P.C_SOL_F, P.C_SOLID, P.NAME["demister"],
          "mist to the still", ts=17.2, ss=12.8)
ab = box(ax, 98.0, 55.2, 52.0, 6.4, P.C_HEAT_F, P.C_HEAT, P.NAME["afterburner"],
         "NCG + tars    Q1    jackets the solids-line rotary", ts=16.6, ss=12.4)
arrow(ax, B(outp), T(quen), P.C_OIL, lw=1.5)
arrow(ax, R(quen), L(dem), P.C_OIL, lw=1.4)
arrow(ax, R(dem), L(ab), P.C_HEAT, lw=1.3, ls="--")
slabel(ax, 96.0, 58.4, P.NAME["ncg"], P.C_HEAT, size=9.0)
h2 = hx_diamond(ax, 160.0, 58.4, "HX-2", P.HX["HX-2"])
arrow(ax, R(ab), (h2[0] - 1.8, h2[1]), P.C_HEAT, lw=1.1, ls="--")

still = box(ax, 2.0, 42.4, 148.0, 10.4, P.C_OIL_F, P.C_OIL, "", "")
ax.text(76.0, 51.6, P.NAME["still"], ha="center", va="top",
        fontsize=18.2, fontweight="bold", color=P.INK, zorder=5)
ax.text(76.0, 49.7, "continuous packed / tray column    HX-3 reboiler from Q2",
        ha="center", va="top", fontsize=13.6, color=P.MUTED, zorder=5)
nap = box(ax, 6.0, 43.6, 32.0, 5.2, P.C_PROD_F, P.C_PROD, "C5–C10", "naphtha draw", ts=16.4, ss=12.4)
mid = box(ax, 42.0, 43.6, 32.0, 5.2, P.C_PROD_F, P.C_PROD, "C11–C18", "fuel-oil draw", ts=16.4, ss=12.4)
gas = box(ax, 78.0, 43.6, 32.0, 5.2, P.C_PROD_F, P.C_PROD, "C19–C32", "wax draw", ts=16.4, ss=12.4)
res = box(ax, 114.0, 43.6, 32.0, 5.2, P.C_OIL_F, P.C_OIL, "C33+", "bottoms recycle", ts=16.4, ss=12.4)
arrow(ax, B(quen), T(still), P.C_OIL, lw=1.5)
arrow(ax, B(dem), (still[0] + 90, still[1] + still[3]), P.C_OIL, lw=1.3)
h3 = hx_diamond(ax, 160.0, 47.6, "HX-3", P.HX["HX-3"])
arrow(ax, (h3[0] - 1.8, h3[1]), R(still), P.C_HEAT, lw=1.1, ls="--")
arrow(ax, L(res), (4.4, cy(res)), P.C_OIL, lw=1.15, ls="--")
arrow(ax, (4.4, cy(res)), (4.4, cy(coil)), P.C_OIL, lw=1.15, ls="--")
arrow(ax, (4.4, cy(coil)), L(coil), P.C_OIL, lw=1.15, ls="--")
slabel(ax, 6.2, 64.6, "heavies back to the auger", P.C_OIL, ha="left", size=9.0)

ax.text(2.0, 40.2, "5   CUTS    char leaves on its own pipe",
        fontsize=17.5, fontweight="bold", color=P.INK)
p1 = box(ax, 2.0, 26.8, 38.0, 10.8, P.C_PROD_F, P.C_PROD, "NAPHTHA",
         "C5–C10. Fab wash and shop solvent.", ts=16.8, ss=12.6)
p2 = box(ax, 44.0, 26.8, 38.0, 10.8, P.C_PROD_F, P.C_PROD, "FUEL OIL",
         "C11–C18. Burner fuel and quench makeup.", ts=16.8, ss=12.6)
p3 = box(ax, 86.0, 26.8, 36.0, 10.8, P.C_PROD_F, P.C_PROD, "WAX / GREASE",
         "C19–C32. Ca soap kettle. Bearings and shop.", ts=16.8, ss=12.6)
p4 = box(ax, 126.0, 26.8, 40.0, 10.8, P.C_SOL_F, P.C_SOLID, P.NAME["char"],
         "carbon char    not mill feed", ts=16.8, ss=12.6)
arrow(ax, B(nap), T(p1), P.C_PROD, lw=1.4)
arrow(ax, B(mid), T(p2), P.C_PROD, lw=1.4)
arrow(ax, B(gas), T(p3), P.C_PROD, lw=1.4)
arrow(ax, B(res), T(p4), P.C_SOLID, lw=1.3)

red = box(ax, 126.0, 17.6, 40.0, 6.6, P.C_HEAT_F, P.C_HEAT, "Si / B REDUCE",
          "char pipe to the furnace    ash → alkali fusion", ts=16.2, ss=12.0)
arrow(ax, B(p4), T(red), P.C_SOLID, lw=1.45)

ax.text(2.0, 15.2,
        "The charge is dried before it enters. Liquor stays in the leach tank. The titanium shell is there because the pipe is hot, and the cast-iron auger is what the coils heat.\n"
        "Paper, wood, and fiber can ride the float. Circuit board and glass cannot. Those leave at the vibratory split and go to the solids line.\n"
        "Non-condensable gas and tars burn in the afterburner. That flue heats the solids-line rotary through a jacket. The two atmospheres do not mix.\n"
        "Carbon char is the reductant for the silicon furnace. Ash that came over with the float goes to alkali fusion, not back into the auger.",
        ha="left", va="top", fontsize=14.0, color=P.MUTED, linespacing=1.4)

ax.text(84.0, 5.6, "OIL LINE takes the float and the dense plastic.  Cuts leave as liquids.  Char leaves on its own pipe.",
        ha="center", va="bottom", fontsize=13.0, color=P.MUTED)
legend_strip(ax, 2.0, -6.2, w=164.0, include=("streams", "marks"))
fig.savefig(P.OUT_OIL, dpi=130, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", P.OUT_OIL)
