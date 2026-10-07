#!/usr/bin/env python3
"""Factory wet line — one leach vessel, weir + in-tank auger, funnel EW aisle."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Circle, FancyArrowPatch
import params as P
from drawlib import box, cx, cy, R, L, T, B, arrow, slabel, mem_bar, legend_strip

fig, ax = plt.subplots(figsize=(32.0, 24.0), dpi=140)
ax.set_xlim(0, 164)
ax.set_ylim(-36.0, 118)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)

ax.text(82, 116.6, "DISASSEMBLY LINE",
        ha="center", va="top", fontsize=31, fontweight="bold", color=P.INK)
ax.text(82, 114.55,
        "One leach.  Float to OIL LINE.  Sink solids to SOLIDS LINE.  "
        "Liquor through EW, then REE bleed, then pH-shift.  "
        "Anions leave on the AEM bank.  Metals that will not plate go to molten-salt cells.",
        ha="center", va="top", fontsize=17.1, color=P.MUTED)

# ── gas rail ─────────────────────────────────────────────
ax.add_patch(FancyBboxPatch(
    (2.0, 109.4), 160.0, 4.15,
    boxstyle="round,pad=0.06,rounding_size=0.16",
    facecolor="#f5f5f4", edgecolor=P.C_SOLID, linewidth=1.05, zorder=2,
))
ax.text(82.0, 113.15, "GAS  —  FOUR HEADERS    hall held negative",
        ha="center", va="top", fontsize=17.4, fontweight="bold", color=P.INK)
ax.text(82.0, 111.35,
        "DUST (grey)  shredder throat → baghouse     "
        "ACID GAS (green)  CSTR 1 lid + every EW / PK anode hood → DEMISTER → ALK SCRUBBER     "
        "H2 (blue)  cathode headspace → own tote     "
        "OIL VAPOR stays on OIL LINE",
        ha="center", va="top", fontsize=13.3, color=P.MUTED)


def funnel_cell(x, y, w, h, tag, metal, product):
    ax.add_patch(FancyBboxPatch(
        (x, y + h * 0.36), w, h * 0.64,
        boxstyle="round,pad=0.04,rounding_size=0.10",
        facecolor="#fafaf9", edgecolor=P.INK, linewidth=1.15, zorder=3,
    ))
    ax.text(x + w / 2, y + h - 0.16, f"{tag}  {metal}",
            ha="center", va="top", fontsize=14.3, fontweight="bold", color=P.INK, zorder=5)
    inner_y = y + h * 0.44
    inner_h = h * 0.38
    pad = 0.20
    aw = (w - 2 * pad - 0.40) * 0.34
    ax.add_patch(Rectangle((x + pad, inner_y), aw, inner_h,
                           facecolor=P.C_AN_F, edgecolor=P.C_AN, lw=0.9, zorder=4))
    ax.text(x + pad + aw / 2, inner_y + inner_h / 2, "A",
            ha="center", va="center", fontsize=11.8, fontweight="bold", color=P.C_AN, zorder=5)
    mx = x + pad + aw + 0.05
    mem_bar(ax, mx, inner_y, 0.30, inner_h, "CEM")
    cx0 = mx + 0.36
    cw = x + w - pad - cx0
    ax.add_patch(Rectangle((cx0, inner_y), cw, inner_h,
                           facecolor=P.C_CA_F, edgecolor=P.C_CEM, lw=0.9, zorder=4))
    ax.text(cx0 + cw / 2, inner_y + inner_h / 2, "C",
            ha="center", va="center", fontsize=11.8, fontweight="bold", color=P.C_CEM, zorder=5)
    fy = y + h * 0.36
    ax.add_patch(Polygon(
        [(x + pad, fy), (x + w - pad, fy),
         (x + w / 2 + 0.55, y + 1.20), (x + w / 2 - 0.55, y + 1.20)],
        closed=True, facecolor=P.C_CA_F, edgecolor=P.C_CEM, lw=1.0, zorder=4,
    ))
    ax.add_patch(Rectangle((x + w / 2 - 0.38, y + 0.52), 0.76, 0.68,
                           facecolor="#fafaf9", edgecolor=P.INK, lw=1.05, zorder=5))
    ax.plot([x + w / 2 - 0.22, x + w / 2 + 0.22], [y + 0.86, y + 0.86],
            color=P.INK, lw=1.15, zorder=6)
    ax.text(x + w / 2, y + 0.08, product, ha="center", va="bottom",
            fontsize=10.5, color=P.MUTED, zorder=5)
    return (x, y, w, h)


# ── mezzanine feed ───────────────────────────────────────
ax.text(2.0, 107.55, "1   FEED  (mezzanine)", fontsize=18.6, fontweight="bold", color=P.INK)
hop = box(ax, 2.0, 100.4, 24.0, 6.3, P.C_SOL_F, P.C_SOLID,
          "HOPPER / SHREDDER", "elevated   dust hood at throat", ts=18.9, ss=12.7)
conv = box(ax, 28.5, 100.4, 26.0, 6.3, P.C_SOL_F, P.C_SOLID,
           "VIBRATORY CONVEYOR", "no filter   dumps into CSTR 1", ts=18.6, ss=12.7)
arrow(ax, R(hop), L(conv), P.C_SOLID, lw=1.9)
slabel(ax, 27.25, 107.05, "shred", P.C_SOLID, size=8.2)

# ── LEACH CSTR 1 as one vessel with weir + floor auger ───
tank_x, tank_y, tank_w, tank_h = 57.0, 92.6, 62.0, 14.1
ax.add_patch(FancyBboxPatch(
    (tank_x, tank_y), tank_w, tank_h,
    boxstyle="round,pad=0.10,rounding_size=0.28",
    facecolor=P.C_LE_F, edgecolor=P.C_LEACH, linewidth=1.7, zorder=3,
))
ax.text(tank_x + 28.0, tank_y + tank_h - 0.35, P.NAME["leach1"],
        ha="center", va="top", fontsize=20.8, fontweight="bold", color=P.INK, zorder=5)
ax.text(tank_x + 28.0, tank_y + tank_h - 2.15,
        f"{P.LEACH_CHEM}    {P.LEACH_T}    {P.LEACH_ORP}\n"
        "lidded mixer    acid-gas takeoff    CPVC / PVDF wall",
        ha="center", va="top", fontsize=12.4, color=P.MUTED, zorder=5, linespacing=1.15)

# floor auger drawn inside the tank
ax.add_patch(FancyBboxPatch(
    (tank_x + 2.2, tank_y + 0.7), 36.5, 4.6,
    boxstyle="round,pad=0.04,rounding_size=0.12",
    facecolor=P.C_SOL_F, edgecolor=P.C_SOLID, linewidth=1.15, zorder=4,
))
ax.text(tank_x + 20.45, tank_y + 3.95, "CSTR 3  AUGER   (in floor)",
        ha="center", va="center", fontsize=14.9, fontweight="bold", color=P.INK, zorder=5)
ax.text(tank_x + 20.45, tank_y + 2.15, "injection-molded PVC / FG    lifts sink solids",
        ha="center", va="center", fontsize=11.5, color=P.MUTED, zorder=5)

# weir lip on the right wall of the same tank
ax.add_patch(FancyBboxPatch(
    (tank_x + 41.0, tank_y + 6.6), 19.2, 4.6,
    boxstyle="round,pad=0.04,rounding_size=0.12",
    facecolor=P.C_OIL_F, edgecolor=P.C_OIL, linewidth=1.2, zorder=4,
))
ax.text(tank_x + 50.6, tank_y + 9.85, "CSTR 2  WEIR",
        ha="center", va="center", fontsize=15.5, fontweight="bold", color=P.INK, zorder=5)
ax.text(tank_x + 50.6, tank_y + 8.05, "float overflows here",
        ha="center", va="center", fontsize=11.5, color=P.MUTED, zorder=5)

ax.text(tank_x + tank_w / 2, tank_y + tank_h + 0.35,
        P.NAME["leach_fork"] + "  =  weir + in-tank auger   (one vessel)",
        ha="center", va="bottom", fontsize=14.6, fontweight="bold", color=P.C_LEACH)

leach = (tank_x, tank_y, tank_w, tank_h)
arrow(ax, R(conv), (tank_x, tank_y + tank_h - 2.2), P.C_SOLID, lw=1.9)
slabel(ax, 55.4, 107.2, "drop", P.C_SOLID, size=8.0)

# liquor pump, then CONC-ED, then the aisle. No drum on this path.
pump = box(ax, 2.0, 94.0, 16.4, 5.2, P.C_LE_F, P.C_LEACH,
           "LEACHATE PUMP",
           "CSTR 1 discharge",
           ts=16.1, ss=11.2)
conc = box(ax, 20.0, 94.0, 34.5, 5.2, P.C_LE_F, P.C_LEACH,
           "CONC-ED",
           "0.2 µm · 3 m/s · CEM · Ti/PbO2\n"
           "2 → 0.17 m³/h    pH < 1.5",
           ts=16.1, ss=10.2)
arrow(ax, (tank_x, tank_y + 8.4), R(pump), P.C_LEACH, lw=1.7)
arrow(ax, R(pump), L(conc), P.C_LEACH, lw=1.55)

# ── float / sink handling ────────────────────────────────
ax.text(2.0, 90.9, "2   SOLIDS FORK", fontsize=18.6, fontweight="bold", color=P.INK)
float_dw = box(ax, 121.5, 100.4, 20.0, 6.3, P.C_OIL_F, P.C_OIL,
               "FLOAT DEWATER", "liquor pumped back to CSTR 1", ts=17.1, ss=11.8)
oil = box(ax, 144.0, 100.4, 18.0, 6.3, P.C_OIL_F, P.C_OIL,
          P.NAME["oil"], "gas, naphtha, fuel oil, grease", ts=17.4, ss=12.2)
arrow(ax, (tank_x + tank_w, tank_y + 8.9), L(float_dw), P.C_OIL, lw=1.6)
arrow(ax, R(float_dw), L(oil), P.C_OIL, lw=1.5)
arrow(ax, (float_dw[0], float_dw[1] + 1.2), (tank_x + tank_w, tank_y + 12.4),
      P.C_LEACH, lw=1.15, ls="--")
slabel(ax, 120.6, 99.55, "liquor return", P.C_LEACH, size=7.4)

sink_dw = box(ax, 57.0, 84.4, 28.0, 5.4, P.C_SOL_F, P.C_SOLID,
              "SINK DEWATER", "drain → CSTR 1", ts=17.7, ss=12.1)
split = box(ax, 88.0, 84.4, 31.0, 5.4, P.C_SOL_F, P.C_SOLID,
            P.NAME["screen"], "undissolved sink solids", ts=18, ss=12.1)
glass = box(ax, 122.0, 84.4, 20.0, 5.4, P.C_IN_F, P.C_INORG,
            P.NAME["glass"], "rinse · burnout · fusion · reduce", ts=15.6, ss=11.4)
dense = box(ax, 144.5, 84.4, 17.5, 5.4, P.C_OIL_F, P.C_OIL,
            "DENSE PLASTIC", "jumper → " + P.NAME["oil"], ts=16.1, ss=11.8)
arrow(ax, (tank_x + 20.5, tank_y), T(sink_dw), P.C_SOLID, lw=1.5)
arrow(ax, R(sink_dw), L(split), P.C_SOLID, lw=1.4)
arrow(ax, R(split), L(glass), P.C_INORG, lw=1.4)
arrow(ax, (split[0] + split[2], split[1] + 1.3), L(dense), P.C_OIL, lw=1.35)
arrow(ax, T(dense), B(oil), P.C_OIL, lw=1.25)
arrow(ax, (sink_dw[0] + 6.0, sink_dw[1] + sink_dw[3]),
      (tank_x + 8.0, tank_y), P.C_LEACH, lw=1.1, ls="--")
slabel(ax, 68.0, 90.35, "drain", P.C_LEACH, size=7.4)

# ── EW aisle ─────────────────────────────────────────────
ax.text(2.0, 81.9,
        "3   EW CASCADE    overflow train    metal leaves the funnel    liquor overflows each cell weir into the next",
        fontsize=18.6, fontweight="bold", color=P.INK)

cells_meta = [
    ("EW-1", "Au", "powder, valve"),
    ("EW-2", "Ag", "peel, Ti blank"),
    ("EW-3", "Cu", "peel, 316L"),
    ("EW-4", "Pb", "peel, 316L"),
    ("EW-5", "Sn", "peel, 316L"),
    ("EW-6", "Ni", "peel, Ti blank"),
    ("EW-7", "Fe", "powder, valve"),
    ("EW-8", "Cd", "peel, 316L"),
    ("EW-9", "Zn", "peel, Al blank"),
]
funnels = []
x0, y0, cw, ch = 2.0, 67.6, 15.2, 12.4
for i, (tag, metal, prod) in enumerate(cells_meta):
    f = funnel_cell(x0 + i * 16.0, y0, cw, ch, tag, metal, prod)
    funnels.append(f)
    if i:
        arrow(ax, R(funnels[i - 1]), L(f), P.C_LEACH, lw=1.3)
        slabel(ax, (funnels[i - 1][0] + funnels[i - 1][2] + f[0]) / 2,
               y0 + ch + 0.12, "overflow", P.C_LEACH, size=7.0)

arrow(ax, B(conc), (cx(funnels[0]), funnels[0][1] + funnels[0][3]), P.C_LEACH, lw=1.9)
slabel(ax, 12.5, 92.7, "concentrate → EW-1", P.C_LEACH, size=8.0)
arrow(ax, (cx(conc) + 8.0, conc[1]), (tank_x + 10.0, tank_y), P.C_LEACH, lw=1.05, ls="--")
slabel(ax, 48.2, 93.35, "diluate + dP bypass → CSTR 1", P.C_LEACH, size=7.6)

# sloped bund under the aisle
ax.add_patch(FancyBboxPatch(
    (2.0, 63.6), 146.0, 3.2,
    boxstyle="round,pad=0.04,rounding_size=0.10",
    facecolor="#e7e5e4", edgecolor=P.C_SOLID, linewidth=1.0, zorder=2,
))
ax.text(75.0, 65.2, "SLOPED BUND    valve drips and spills to the harvest sump    liquor back to CSTR 1",
        ha="center", va="center", fontsize=13.3, color=P.MUTED, zorder=4)

bmed = box(ax, 148.5, 67.6, 13.5, 15.6, P.C_LE_F, P.C_LEACH, P.NAME["bmed"],
           "spent liquor\nin\nHCl + NaOH\nout\n" + P.NAME["regen"],
           ts=16.4, ss=11.5)
arrow(ax, R(funnels[-1]), L(bmed), P.C_LEACH, lw=1.35)
slabel(ax, 147.6, 80.7, "spent", P.C_LEACH, size=7.4)

# anode ticks
for f in funnels:
    ax.plot([f[0] + f[2] * 0.22, f[0] + f[2] * 0.22],
            [f[1] + f[3], f[1] + f[3] + 0.55], color=P.C_AN, lw=0.95, zorder=4)
ax.text(75.0, 81.05, "anode hoods → acid-gas header", ha="center", va="bottom",
        fontsize=12.4, color=P.C_AN)

# ── harvest ──────────────────────────────────────────────
ax.text(2.0, 62.05, "4   HARVEST", fontsize=18.6, fontweight="bold", color=P.INK)
man = box(ax, 2.0, 54.2, 72.0, 6.6, P.C_SOL_F, P.C_SOLID,
          "MANUAL / STARTUP",
          "powder: open the valve into a lidded pail    sheet: lift the blank and peel",
          ts=18.0, ss=12.2)
auto = box(ax, 77.0, 54.2, 72.0, 6.6, P.C_PROD_F, P.C_PROD,
           "AUTO  (full scale)",
           "own drum per cell    peel sheets go to melt    melt gas from OIL LINE",
           ts=18.0, ss=12.2)
vdf = box(ax, 2.0, 47.4, 36.0, 5.2, P.C_SOL_F, P.C_SOLID,
          "HARVEST " + P.NAME["vdf"], "shared drum   startup / manual", ts=17.1, ss=12.1)
melt = box(ax, 113.0, 47.4, 36.0, 5.2, P.C_HEAT_F, P.C_HEAT,
           "MELT", "induction or oil-gas    from OIL LINE", ts=17.7, ss=12.1)
met = box(ax, 40.5, 47.4, 70.0, 5.2, P.C_PROD_F, P.C_PROD,
          P.NAME["metals"],
          "powder or peeled sheet    Au Ag Cu Pb Sn Ni Fe Cd Zn", ts=18.0, ss=12.4)
for f in funnels:
    arrow(ax, (f[0] + f[2] / 2, f[1]), (f[0] + f[2] / 2, 66.8), P.C_CEM, lw=0.85)
arrow(ax, (38.0, 63.6), T(man), P.C_SOLID, lw=1.25)
arrow(ax, (113.0, 63.6), T(auto), P.C_PROD, lw=1.25)
arrow(ax, B(man), T(vdf), P.C_SOLID, lw=1.2)
arrow(ax, B(auto), T(melt), P.C_HEAT, lw=1.2)
arrow(ax, R(vdf), L(met), P.C_PROD, lw=1.3)
arrow(ax, L(melt), R(met), P.C_PROD, lw=1.3)

# ── pH shift ─────────────────────────────────────────────
ax.text(2.0, 45.55, "5   REE / Li BLEED  then  pH-SHIFT    bleed is off EW-9 liquor, before P-Al",
        fontsize=18.6, fontweight="bold", color=P.INK)
bleed = box(ax, 2.0, 39.2, 32.0, 5.2, P.C_IN_F, P.C_INORG, "PK-4 / PK-5 BLEED",
            "Li + REE off EW-9   before any hydroxide", ts=17.1, ss=11.8)
p1 = box(ax, 36.5, 39.2, 28.0, 5.2, P.C_IN_F, P.C_INORG, "P-Al   pH 5.0–5.5", "Al(OH)3 cake", ts=17.1, ss=12.1)
p2 = box(ax, 66.8, 39.2, 28.0, 5.2, P.C_IN_F, P.C_INORG, "P-Mg   pH 10.5–11", "Mg(OH)2 cake", ts=17.1, ss=12.1)
p3 = box(ax, 97.0, 39.2, 28.0, 5.2, P.C_IN_F, P.C_INORG, "P-Ca   pH 12–12.5", "Ca(OH)2 / CaCO3", ts=17.1, ss=12.1)
hyd = box(ax, 127.2, 39.2, 34.8, 5.2, P.C_PROD_F, P.C_PROD, P.NAME["hydroxides"],
          "cakes → molten cells", ts=17.7, ss=12.1)
arrow(ax, R(bleed), L(p1), P.C_INORG, lw=1.25)
arrow(ax, R(p1), L(p2), P.C_INORG, lw=1.25)
arrow(ax, R(p2), L(p3), P.C_INORG, lw=1.25)
arrow(ax, R(p3), L(hyd), P.C_PROD, lw=1.4)
arrow(ax, B(bmed), (155.2, 44.4), P.C_LEACH, lw=1.05, ls="--")
slabel(ax, 155.6, 45.7, "NaOH", P.C_LEACH, size=7.4)

# ── polish ───────────────────────────────────────────────
ax.text(2.0, 37.45, P.NAME["polish"] + "   parallel tap    open valve = powder    lid on = closed takeoff",
        fontsize=17.4, fontweight="bold", color=P.INK)
pks = [("PK-1", "Co", "powder, valve"), ("PK-2", "Mn", "powder, valve"),
       ("PK-3", "Cr", "powder, valve"), ("PK-6", "Hg", "lid on, closed valve"),
       ("PK-7", "Tl", "powder, valve"), ("PK-8", "Bi/Sb", "powder, valve"),
       ("PK-9", "rad", "lid on, closed sump"), ("PK-10", "As", "lid on, cold finger")]
pkf = []
for i, (tag, metal, prod) in enumerate(pks):
    pkf.append(funnel_cell(2.0 + i * 16.0, 24.6, 15.2, 11.2, tag, metal, prod))
li = box(ax, 131.5, 27.0, 30.5, 8.8, P.C_IN_F, P.C_INORG,
         "PK-4 Li    PK-5 REE", "bleed already taken   cake to PK-5B", ts=17.1, ss=11.8)
arrow(ax, R(pkf[-1]), L(li), P.C_INORG, lw=1.2)

# ── regen + air ──────────────────────────────────────────
ax.text(2.0, 22.7, "6   REGEN  +  AIR", fontsize=18.6, fontweight="bold", color=P.INK)
scrub = box(ax, 2.0, 16.0, 50.0, 5.6, P.C_SOL_F, P.C_SOLID,
            "DEMISTER + ALK SCRUBBER",
            "acid-gas header   NaOH from BMED   liquor → CRU", ts=17.7, ss=12.4)
regen = box(ax, 55.0, 16.0, 52.0, 5.6, P.C_LE_F, P.C_LEACH, P.NAME["regen"],
            "bund rinse + BMED acid + CRU chlorate  →  CSTR 1", ts=17.7, ss=12.4)
cru = box(ax, 110.0, 16.0, 52.0, 5.6, P.C_AN_F, P.C_AN, P.NAME["cru"],
          "Cl2 + H2 headers stay separate", ts=18.3, ss=12.4)

ax.text(2.0, 13.7, "WHAT EACH BAND DOES", fontsize=18, fontweight="bold", color=P.INK)
ax.text(2.0, 12.35,
        "Shred drops straight into the leach tank. The weir on that tank is the float takeoff. The floor auger is the sink takeoff. Both conveyors drain back into the tank.\n"
        "Pregnant liquor is concentrated, then plated gold through zinc. Lithium and rare earths are bled before the hydroxide cuts, or they end up in the aluminum cake.\n"
        "Gold and iron leave as powder through the funnel valve. Silver, copper, lead, tin, nickel, cadmium, and zinc plate on a blank and peel off. CPVC edge strips stop the deposit wrapping the blank. Silver and nickel peel from titanium. Copper, lead, tin, and cadmium peel from 316L. Zinc peels from aluminum.\n"
        "Polish powder leaves through an open valve. A lid-on cell does not. Mercury amalgam leaves through a closed valve into a bottle. Radionuclide sludge leaves the closed sump. Arsenic is scraped off the cold finger under the lid. None of those three dump into an open pail.",
        ha="left", va="top", fontsize=13.6, color=P.MUTED, linespacing=1.28)

# ── anion bank, split, molten, solids completion ─────────
ax.text(2.0, -1.3, "7   ANIONS  ·  SPLIT  ·  MOLTEN METAL  ·  SOLIDS COMPLETION",
        fontsize=18.6, fontweight="bold", color=P.INK)
aem = box(ax, 2.0, -11.4, 26.0, 8.8, P.C_AEM_F, P.C_AEM, P.NAME["aem"],
          "pH 9. Stack concentrates.\n"
          "F, SO4, P, B cut after\n"
          "diluate → K split\n"
          "arsenic does not enter", ts=15.0, ss=10.4)
ks = box(ax, 30.2, -11.4, 22.0, 8.8, P.C_LE_F, P.C_LEACH, P.NAME["k_split"],
         "PP crystallizer, 5–10 °C\n"
         "KCl → farm\n"
         "NaCl liquor → BMED", ts=15.0, ss=10.4)
ns = box(ax, 54.4, -11.4, 22.0, 8.8, P.C_SOL_F, P.C_SOLID, P.NAME["n_scrub"],
         "packed tower\n"
         "BMED HCl on NH3\n"
         "NH4Cl → farm\n"
         "NOx stays on the scrubber", ts=14.6, ss=10.2)
spl = box(ax, 78.6, -11.4, 26.0, 8.8, P.C_IN_F, P.C_INORG, P.NAME["ree_split"],
          "batch lot, PP\n"
          "double sulfate, then oxalate\n"
          "La–Ce, Nd/Pr, Dy/Tb\n"
          "oxide lots → molten cells", ts=14.8, ss=10.2)
mol = box(ax, 106.8, -11.4, 28.0, 8.8, P.C_HEAT_F, P.C_HEAT, P.NAME["molten"],
          "Al and Mg pots ~700 °C\n"
          "Ca pot ~800 °C, contact cathode\n"
          "REE is a Ca retort, not a pot\n"
          "Cl2 from the pots → CRU", ts=14.4, ss=10.0)
red = box(ax, 137.0, -11.4, 25.0, 8.8, P.C_HEAT_F, P.C_HEAT, P.NAME["reduce"],
          "Si arc: gel + char ~1800 °C\n"
          "B retort: B2O3 + Mg or Ca\n"
          "boron does not enter the arc\n"
          "slag → fusion", ts=14.4, ss=10.0)
arrow(ax, R(aem), L(ks), P.C_AEM, lw=1.2)
arrow(ax, R(spl), L(mol), P.C_HEAT, lw=1.2)
arrow(ax, R(mol), L(red), P.C_HEAT, lw=1.15)
slabel(ax, 149.5, -2.05, "char → furnace", P.C_HEAT, size=7.4)

ax.text(2.0, -13.2,
        "The anion stack concentrates borate, phosphate, sulfate, and fluoride. It does not split them. Calcium hydroxide drops fluoride for the HF cell. Cooling drops sulfate for PK-5B. Phosphate goes to the farm. Borate is calcined to boron oxide. Arsenic does not enter. Diluate goes to the potassium crystallizer, then BMED.\n"
        "PK-5B dissolves the oxalate cake, drops lanthanum and cerium as the double sulfate, and cuts neodymium/praseodymium from dysprosium/terbium. Those oxide lots and the hydroxide cakes go to dry chloride pots.\n"
        "Silica gel is reduced with pyro char. Boron oxide is reduced with calcium or magnesium from those pots. Slag returns to alkali fusion.",
        ha="left", va="top", fontsize=13.2, color=P.MUTED, linespacing=1.28)

plt.tight_layout(pad=0.18)
legend_strip(ax, 2.0, -33.5, w=160.0, include=("streams", "marks"))
out = getattr(P, "OUT_WET", P.ROOT / "wet_line_factory_pfd.png")
fig.savefig(out, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", out)
