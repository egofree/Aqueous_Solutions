#!/usr/bin/env python3
"""Completion sheet. CONC-ED and the units that were stubs on the trunk."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import params as P
from drawlib import box, cx, R, L, T, B, arrow, slabel, legend_strip

fig, ax = plt.subplots(figsize=(34.0, 26.0), dpi=120)
ax.set_xlim(0, 168)
ax.set_ylim(-8.0, 124)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)

ax.text(84, 122.2, "CONC-ED  ·  SOLIDS LINE  ·  ANION AND METAL COMPLETION",
        ha="center", va="top", fontsize=26, fontweight="bold", color=P.INK)
ax.text(84, 119.2,
        "Duties at the leach design point    2 m³/h at 2 g/L    concentrate 0.17 m³/h at 20 g/L",
        ha="center", va="top", fontsize=15.5, color=P.MUTED)

ax.text(2.0, 116.6, "1   CONC-ED    between the leach pump and EW-1    not an evaporator",
        fontsize=17.2, fontweight="bold", color=P.INK)
coal = box(ax, 2.0, 104.6, 38.0, 9.4, P.C_LE_F, P.C_LEACH, "COALESCER",
           "CPVC    free oil off    no carbon", ts=16.6, ss=12.4)
xf = box(ax, 44.0, 104.6, 40.0, 9.4, P.C_SOL_F, P.C_SOLID, "CROSSFLOW",
         "alumina 0.2 µm    3 m/s\n25 m²    80 L/m²·h\ncake to sink dewater", ts=16.4, ss=12.2)
stk = box(ax, 88.0, 104.6, 42.0, 9.4, P.C_CEM_F, P.C_CEM, "CEM STACK",
          "20 pairs    0.25 m²\nTi / PbO2 anode\npH held under 1.5", ts=16.4, ss=12.2)
ew = box(ax, 134.0, 104.6, 32.0, 9.4, P.C_PROD_F, P.C_PROD, "TO EW-1",
         "0.17 m³/h at 20 g/L\n3.4 kg/h metal\n85 % of the cations", ts=16.2, ss=12.2)
arrow(ax, R(coal), L(xf), P.C_LEACH, lw=1.5)
arrow(ax, R(xf), L(stk), P.C_LEACH, lw=1.5)
arrow(ax, R(stk), L(ew), P.C_PROD, lw=1.5)
dil = box(ax, 88.0, 96.4, 42.0, 6.2, P.C_LE_F, P.C_LEACH, "DILUATE + dP BYPASS",
          "both return to CSTR 1    CIP is BMED HCl only", ts=16.0, ss=12.2)
arrow(ax, B(stk), T(dil), P.C_LEACH, lw=1.3, ls="--")

ax.text(2.0, 93.8, "2   SOLIDS LINE    undissolved sink only",
        fontsize=17.2, fontweight="bold", color=P.INK)
rinse = box(ax, 2.0, 82.2, 30.0, 9.0, P.C_IN_F, P.C_INORG, "RINSE",
            "liquor to regen leach", ts=16.4, ss=12.4)
burn = box(ax, 36.0, 82.2, 32.0, 9.0, P.C_IN_F, P.C_INORG, "BURNOUT",
           "450–550 °C    indirect\njacketed, not the oil pipe", ts=16.0, ss=12.0)
mill = box(ax, 72.0, 82.2, 28.0, 9.0, P.C_IN_F, P.C_INORG, "MILL",
           "dry    under 300 µm", ts=16.4, ss=12.4)
dig = box(ax, 104.0, 82.2, 30.0, 9.0, P.C_LE_F, P.C_LEACH, "DIGEST",
          "80–90 °C    BMED NaOH\nsoda-lime opens", ts=16.0, ss=12.0)
fus = box(ax, 138.0, 82.2, 28.0, 9.0, P.C_HEAT_F, P.C_HEAT, "FUSION",
          "300–500 °C sinter\nquartz recycles", ts=16.0, ss=12.0)
arrow(ax, R(rinse), L(burn), P.C_INORG, lw=1.4)
arrow(ax, R(burn), L(mill), P.C_INORG, lw=1.4)
arrow(ax, R(mill), L(dig), P.C_INORG, lw=1.4)
arrow(ax, R(dig), L(fus), P.C_HEAT, lw=1.3, ls="--")

ax.text(2.0, 79.6, "3   AEM BANK    two feeds    arsenic does not enter",
        fontsize=17.2, fontweight="bold", color=P.INK)
brine = box(ax, 2.0, 66.8, 38.0, 10.2, P.C_LE_F, P.C_LEACH, "POST-POLISH BRINE",
            "raise to pH 9 with BMED NaOH\nborate as B(OH)4−", ts=16.2, ss=12.2)
sil = box(ax, 44.0, 66.8, 36.0, 10.2, P.C_IN_F, P.C_INORG, "DIGEST LIQUOR",
          "already alkaline\nbefore the silica drop", ts=16.2, ss=12.2)
aem = box(ax, 84.0, 66.8, 40.0, 10.2, P.C_AEM_F, P.C_AEM, "AEM STACK",
          "PP frame    anion film\ndiluate to BMED salt", ts=16.2, ss=12.2)
cuts = box(ax, 128.0, 66.8, 38.0, 10.2, P.C_PROD_F, P.C_PROD, "CUTS",
           "B2O3 to the furnace\nphosphate to the farm\nfluoride to the HF cell", ts=15.6, ss=11.8)
arrow(ax, R(brine), L(sil), P.C_LEACH, lw=1.3)
arrow(ax, R(sil), L(aem), P.C_AEM, lw=1.4)
arrow(ax, R(aem), L(cuts), P.C_PROD, lw=1.4)

ax.text(2.0, 64.2, "4   K SPLIT    then N SCRUB",
        fontsize=17.2, fontweight="bold", color=P.INK)
ks = box(ax, 2.0, 52.4, 52.0, 9.2, P.C_LE_F, P.C_LEACH, "K SPLIT",
         "PP crystallizer    5–10 °C\nKCl to the farm    NaCl liquor to BMED", ts=16.6, ss=12.4)
ns = box(ax, 58.0, 52.4, 52.0, 9.2, P.C_SOL_F, P.C_SOLID, "N SCRUB",
         "packed tower    BMED HCl\nNH3 to NH4Cl for the farm\nNOx stays on the alk scrubber", ts=16.2, ss=12.0)
arrow(ax, (28.0, 61.6), T(ks), P.C_LEACH, lw=1.2)

ax.text(2.0, 49.8, "5   PK-5B    batch lot    not a flow cell",
        fontsize=17.2, fontweight="bold", color=P.INK)
dis = box(ax, 2.0, 37.6, 38.0, 9.6, P.C_IN_F, P.C_INORG, "DISSOLVE",
          "oxalate cake in BMED HCl", ts=16.4, ss=12.4)
ds = box(ax, 44.0, 37.6, 40.0, 9.6, P.C_SOL_F, P.C_SOLID, "DOUBLE SULFATE",
         "sulfate from the anion bank\nLa–Ce drops    Nd group stays", ts=16.2, ss=12.2)
ox = box(ax, 88.0, 37.6, 40.0, 9.6, P.C_PROD_F, P.C_PROD, "OXALATE CUTS",
         "stepped pH\nNd/Pr    then Dy/Tb\ncalcine to oxide", ts=16.2, ss=12.2)
arrow(ax, R(dis), L(ds), P.C_INORG, lw=1.4)
arrow(ax, R(ds), L(ox), P.C_PROD, lw=1.4)

ax.text(2.0, 35.0, "6   MOLTEN SALT    three pots and one retort    not a series",
        fontsize=17.2, fontweight="bold", color=P.INK)
al = box(ax, 2.0, 21.4, 39.0, 11.0, P.C_HEAT_F, P.C_HEAT, "Al POT",
         "calcine to alumina\nchar + Cl2 to AlCl3\nelectrolyze near 700 C", ts=15.8, ss=11.8)
mg = box(ax, 44.0, 21.4, 39.0, 11.0, P.C_HEAT_F, P.C_HEAT, "Mg POT",
         "dehydrate under HCl\nanhydrous MgCl2\nelectrolyze near 700 C", ts=15.8, ss=11.8)
ca = box(ax, 86.0, 21.4, 39.0, 11.0, P.C_HEAT_F, P.C_HEAT, "Ca POT",
         "CaCl2 near 800 C\ncontact cathode\nmetal withdrawn as it forms", ts=15.6, ss=11.6)
ree = box(ax, 128.0, 21.4, 38.0, 11.0, P.C_HEAT_F, P.C_HEAT, "REE RETORT",
          "not a pot\noxide + Ca, 900 to 1100 C\nCaO slag back to the Ca feed", ts=15.6, ss=11.6)
arrow(ax, B(ox), T(ree), P.C_PROD, lw=1.25)
arrow(ax, L(ree), R(ca), P.C_HEAT, lw=1.15, ls="--")
slabel(ax, 124.0, 26.8, "Ca metal", P.C_HEAT, size=9.0)

ax.text(2.0, 18.8, "7   SILICON ARC AND BORON RETORT    boron does not enter the arc",
        fontsize=17.2, fontweight="bold", color=P.INK)
gel = box(ax, 2.0, 6.4, 36.0, 10.0, P.C_PROD_F, P.C_PROD, "SILICA GEL",
          "BMED HCl, wash Na+, calcine", ts=16.0, ss=12.0)
arc = box(ax, 42.0, 6.4, 42.0, 10.0, P.C_HEAT_F, P.C_HEAT, "SILICON ARC",
          "gel + char, near 1800 C\nSiO2 + 2C to Si + 2CO\nslag to fusion", ts=15.6, ss=11.8)
sol = box(ax, 88.0, 6.4, 36.0, 10.0, P.C_PROD_F, P.C_PROD, "SOLIDIFY",
          "silicon only\ndrops Fe, Al, Ca\nto fab prep", ts=16.0, ss=12.0)
bor = box(ax, 128.0, 6.4, 38.0, 10.0, P.C_HEAT_F, P.C_HEAT, "BORON RETORT",
          "B2O3 + Mg or Ca, near 850 C\nHCl leach of the oxide\npowder out", ts=15.6, ss=11.6)
arrow(ax, R(gel), L(arc), P.C_PROD, lw=1.4)
arrow(ax, R(arc), L(sol), P.C_PROD, lw=1.4)
arrow(ax, (147.0, 66.8), (147.0, 16.4), P.C_PROD, lw=1.15)
arrow(ax, (147.0, 16.4), T(bor), P.C_PROD, lw=1.15)

ax.text(84.0, 4.6, "Aqueous cells do not make Al, Mg, Ca, Li, Ti, Si, or the rare earths.",
        ha="center", va="bottom", fontsize=13.2, color=P.MUTED)
legend_strip(ax, 2.0, -5.6, w=164.0, include=("streams", "marks", "membranes"))
fig.savefig(P.ROOT / "completion_pfd.png", dpi=120, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", P.ROOT / "completion_pfd.png")
