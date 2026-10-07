#!/usr/bin/env python3
"""SOLIDS LINE detail sheet. Wide row layout, same pitch as the disassembly sheet."""
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

ax.text(84, 110.4, "SOLIDS LINE  —  SPLIT · RINSE · BURNOUT · FUSION · DIGEST · REDUCE",
        ha="center", va="top", fontsize=26, fontweight="bold", color=P.INK)
ax.text(84, 107.6,
        "Undissolved sink at the head    ·    Si metal, boron, hydroxides, grit at the bottom    ·    no FR-4 in the oil auger",
        ha="center", va="top", fontsize=16.2, color=P.MUTED)

ax.text(2.0, 105.4, "1   HEAD", fontsize=17.5, fontweight="bold", color=P.INK)
leach = box(ax, 2.0, 96.6, 38.0, 6.4, P.C_LE_F, P.C_LEACH, P.NAME["leach_fork"],
            "undissolved sink → VDF", ts=18.2, ss=13.2)
vdf = box(ax, 44.0, 96.6, 36.0, 6.4, P.C_SOL_F, P.C_SOLID, P.NAME["vdf"],
          "cake to this sheet", ts=18.2, ss=13.2)
scr = box(ax, 84.0, 96.6, 46.0, 6.4, P.C_SOL_F, P.C_SOLID, P.NAME["screen"],
          "glass · ceramic · FR-4 down", ts=18.2, ss=13.2)
oil = box(ax, 134.0, 96.6, 32.0, 6.4, P.C_OIL_F, P.C_OIL, P.NAME["oil"],
          "dense plastic → dryer", ts=18.2, ss=13.2)
arrow(ax, R(leach), L(vdf), P.C_LEACH, lw=1.6)
arrow(ax, R(vdf), L(scr), P.C_SOLID, lw=1.6)
arrow(ax, R(scr), L(oil), P.C_OIL, lw=1.5)
slabel(ax, 131.8, 100.2, "dense plastic", P.C_OIL, size=9.0)

ax.text(2.0, 94.4, "2   RINSE", fontsize=17.5, fontweight="bold", color=P.INK)
wash = box(ax, 2.0, 86.2, 128.0, 6.2, P.C_IN_F, P.C_INORG, P.NAME["wash"],
           "countercurrent    liquor and fines → REGEN LEACH / BMED SALT", ts=18.6, ss=13.4)
arrow(ax, B(scr), T(wash), P.C_INORG, lw=1.7)

ax.text(2.0, 84.0, "3   BURNOUT    atmospheres isolated from the oil auger",
        fontsize=17.5, fontweight="bold", color=P.INK)
ax.add_patch(FancyBboxPatch(
    (2.0, 66.4), 148.0, 15.4,
    boxstyle="round,pad=0.1,rounding_size=0.28",
    facecolor="#eff6ff", edgecolor=P.C_INORG, linewidth=1.5, zorder=2,
))
ax.text(76.0, 80.6, P.NAME["burnout"], ha="center", va="top",
        fontsize=18.5, fontweight="bold", color=P.INK, zorder=4)
ax.text(76.0, 78.7, f"{P.BURNOUT_T}    jacketed by afterburner flue    oil vapor does not enter the rotary",
        ha="center", va="top", fontsize=13.6, color=P.MUTED, zorder=4)
rot = box(ax, 4.2, 67.6, 52.0, 9.0, P.C_IN_F, P.C_INORG, "INDIRECT-FIRED ROTARY",
          "SiC / high-Ni tube    organics and epoxy out    glass and ceramic stay", ts=16.8, ss=12.6)
ab = box(ax, 60.0, 67.6, 42.0, 9.0, P.C_HEAT_F, P.C_HEAT, P.NAME["afterburner"],
         "oil-line NCG + burnout off-gas    Q1 source", ts=16.8, ss=12.6)
jkt = box(ax, 106.0, 67.6, 40.0, 9.0, P.C_HEAT_F, P.C_HEAT, "FLUE JACKET",
          "HX-7    Q2 to the rotary    no mixing", ts=16.8, ss=12.6)
arrow(ax, R(ab), L(jkt), P.C_HEAT, lw=1.5)
arrow(ax, L(jkt), R(rot), P.C_HEAT, lw=1.3, ls="--")
arrow(ax, B(wash), T(rot), P.C_INORG, lw=1.6)
h7 = hx_diamond(ax, 158.0, 72.1, "HX-7", P.HX["HX-7"])
arrow(ax, R(jkt), (h7[0] - 1.8, h7[1]), P.C_HEAT, lw=1.15, ls="--")

ax.text(2.0, 64.2, "4   MILL AND CONDENSATE", fontsize=17.5, fontweight="bold", color=P.INK)
mill = box(ax, 2.0, 55.6, 70.0, 6.4, P.C_IN_F, P.C_INORG, P.NAME["mill"],
           "< 300 µm    dry mill after burnout", ts=18.2, ss=13.2)
bmed = box(ax, 78.0, 55.6, 72.0, 6.4, P.C_LE_F, P.C_LEACH, P.NAME["bmed"],
           "Br- / HCl vapor condensate in    not vented", ts=18.0, ss=13.0)
arrow(ax, B(rot), T(mill), P.C_INORG, lw=1.6)
arrow(ax, R(rot), L(bmed), P.C_LEACH, lw=1.2, ls="--")
slabel(ax, 74.5, 58.6, "Br-", P.C_LEACH, size=9.0)

ax.text(2.0, 53.4, "5   DIGEST    soda-lime opens here    quartz does not",
        fontsize=17.5, fontweight="bold", color=P.INK)
d1 = box(ax, 2.0, 42.2, 42.0, 8.8, P.C_LE_F, P.C_LEACH, "NaOH FEED",
         f"from BMED BASE    wall {P.WALL['bmed_base']}", ts=17.4, ss=12.8)
d2 = box(ax, 48.0, 42.2, 46.0, 8.8, P.C_IN_F, P.C_INORG, "DIGESTOR",
         "stirred PP or Ni    80–90 °C    BMED NaOH", ts=17.4, ss=12.8)
d3 = box(ax, 98.0, 42.2, 42.0, 8.8, P.C_SOL_F, P.C_SOLID, "FILTER",
         "silicate liquor versus grit cake", ts=17.4, ss=12.8)
arrow(ax, R(d1), L(d2), P.C_LEACH, lw=1.5)
arrow(ax, R(d2), L(d3), P.C_INORG, lw=1.5)
arrow(ax, B(mill), T(d2), P.C_INORG, lw=1.5)
h6 = hx_diamond(ax, 158.0, 46.6, "HX-6", P.HX["HX-6"])
arrow(ax, (h6[0] - 1.8, h6[1]), R(d3), P.C_HEAT, lw=1.15, ls="--")

ax.text(2.0, 39.8, "6   FUSION · AEM · GEL · REDUCE    char is a pipe, not a mill feed",
        fontsize=17.5, fontweight="bold", color=P.INK)
fus = box(ax, 2.0, 26.6, 36.0, 10.6, P.C_HEAT_F, P.C_HEAT, P.NAME["fusion"],
          "NaOH / Na2CO3 sinter\n300–500 °C\nquartz returns to digest", ts=16.4, ss=12.2)
aem = box(ax, 42.0, 26.6, 36.0, 10.6, P.C_AEM_F, P.C_AEM, P.NAME["aem"],
          "pH 9 concentrate\nF, SO4, P, B cut after\narsenic does not enter", ts=16.0, ss=11.6)
sil = box(ax, 82.0, 26.6, 36.0, 10.6, P.C_PROD_F, P.C_PROD, P.NAME["silica"],
          "BMED HCl\nwash Na+\ncalcine", ts=16.4, ss=12.2)
red = box(ax, 122.0, 26.6, 44.0, 10.6, P.C_HEAT_F, P.C_HEAT, P.NAME["reduce"],
          "Si arc ~1800 °C, gel + char\nB retort ~850 °C, not in the arc\nslag back to fusion", ts=16.0, ss=11.8)
arrow(ax, R(aem), L(sil), P.C_AEM, lw=1.4)
arrow(ax, R(sil), L(red), P.C_PROD, lw=1.4)
arrow(ax, B(d3), T(aem), P.C_INORG, lw=1.4)
arrow(ax, L(fus), (20.0, 42.2), P.C_HEAT, lw=1.15, ls="--")
slabel(ax, 16.5, 41.0, "quartz returns", P.C_HEAT, size=9.0)
char = box(ax, 122.0, 38.4, 44.0, 3.6, P.C_SOL_F, P.C_SOLID, "PYRO CHAR",
           "from OIL LINE    reductant    not mill feed", ts=15.4, ss=11.6)
arrow(ax, B(char), T(red), P.C_SOLID, lw=1.45)

ax.text(2.0, 24.6, "7   PRODUCTS", fontsize=17.5, fontweight="bold", color=P.INK)
hyd = box(ax, 2.0, 12.2, 38.0, 9.6, P.C_PROD_F, P.C_PROD, P.NAME["hydroxides"],
          "from the digest filter    to molten-salt cells", ts=16.4, ss=12.4)
grit = box(ax, 44.0, 12.2, 36.0, 9.6, P.C_SOL_F, P.C_SOLID, P.NAME["grit"],
           "alumina, SiC, zircon    undigested, still feedstock", ts=16.2, ss=12.2)
sim = box(ax, 84.0, 12.2, 34.0, 9.6, P.C_PROD_F, P.C_PROD, "Si METAL  /  B",
          "from the arc furnace    to wafer-fab prep", ts=16.4, ss=12.4)
arrow(ax, B(aem), T(hyd), P.C_INORG, lw=1.25)
arrow(ax, B(sil), T(grit), P.C_SOLID, lw=1.2)
arrow(ax, B(red), (cx(sim), sim[1] + sim[3]), P.C_PROD, lw=1.3)

ax.text(2.0, 10.0,
        "Soda-lime glass dissolves in BMED sodium hydroxide at 80–90 °C. Quartz, feldspar, and olivine do not, so they recycle through the alkali fusion and come back to the digest.\n"
        "The anion stack concentrates the digest liquor before the silica drop. Fluoride, sulfate, phosphate, and borate are cut after the stack. Boron oxide goes to the retort, not the arc.\n"
        "Carbon char from the oil line is the reductant in the arc furnace. Slag goes back to fusion. Rinse liquor goes to regen leach. Bromide condensate goes to BMED.",
        ha="left", va="top", fontsize=14.0, color=P.MUTED, linespacing=1.4)

ax.text(84.0, 3.2, "SOLIDS LINE takes the undissolved sink.  Plastic leaves at the split.  Glass becomes silicate, silica, then silicon.",
        ha="center", va="bottom", fontsize=13.0, color=P.MUTED)
legend_strip(ax, 2.0, -5.8, w=164.0, include=("streams", "marks"))
fig.savefig(P.OUT_GLASS, dpi=130, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", P.OUT_GLASS)
