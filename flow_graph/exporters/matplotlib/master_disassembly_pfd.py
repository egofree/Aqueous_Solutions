#!/usr/bin/env python3
"""Disassembly line. One arrow per stream, labeled, in the gap."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon
import params as P
from drawlib import box, cx, cy, R, L, T, B, mem_bar

fig, ax = plt.subplots(figsize=(62, 42), dpi=90)
ax.set_xlim(0, 560)
ax.set_ylim(0, 364)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)

CL2 = "#be123c"


def flow(pts, color, text):
    ax.plot([p[0] for p in pts], [p[1] for p in pts],
            color=color, lw=3.2, solid_capstyle="butt", zorder=8)
    ax.annotate("", xy=pts[-1], xytext=pts[-2],
                arrowprops=dict(arrowstyle="-|>", color=color, lw=3.2,
                                mutation_scale=18), zorder=9)
    best, span = 0, -1
    for i in range(len(pts) - 1):
        d = abs(pts[i + 1][0] - pts[i][0]) + abs(pts[i + 1][1] - pts[i][1])
        if d > span:
            best, span = i, d
    x = (pts[best][0] + pts[best + 1][0]) / 2
    y = (pts[best][1] + pts[best + 1][1]) / 2 + 2.2
    ax.text(x, y, text, ha="center", va="bottom", fontsize=10.4,
            color=color, fontweight="bold", zorder=10,
            bbox=dict(boxstyle="round,pad=0.1", fc="#f3efe6", ec="none"))


def unit(x, y, w, h, fill, edge, title, sub):
    return box(ax, x, y, w, h, fill, edge, title, sub, ts=13.2, ss=10.6)


def cell(x, y, w, h, tag, duty):
    ax.add_patch(FancyBboxPatch(
        (x, y + h * 0.32), w, h * 0.68,
        boxstyle="round,pad=0.04,rounding_size=0.1",
        facecolor="#fafaf9", edgecolor=P.INK, lw=1.2, zorder=3))
    ax.text(x + w / 2, y + h - 0.5, tag, ha="center", va="top",
            fontsize=11.6, fontweight="bold", color=P.INK, zorder=5)
    iy, ih, pad = y + h * 0.40, h * 0.32, 0.35
    aw = (w - 2 * pad) * 0.26
    ax.add_patch(Rectangle((x + pad, iy), aw, ih, facecolor=P.C_AN_F,
                           edgecolor=P.C_AN, lw=0.8, zorder=4))
    mem_bar(ax, x + pad + aw + 0.12, iy, 0.32, ih, "CEM")
    cx0 = x + pad + aw + 0.52
    ax.add_patch(Rectangle((cx0, iy), x + w - pad - cx0, ih, facecolor=P.C_CA_F,
                           edgecolor=P.C_CEM, lw=0.8, zorder=4))
    ax.add_patch(Polygon(
        [(x + 0.6, y + h * 0.32), (x + w - 0.6, y + h * 0.32),
         (x + w / 2 + 0.6, y + 1.4), (x + w / 2 - 0.6, y + 1.4)],
        closed=True, facecolor=P.C_CA_F, edgecolor=P.C_CEM, lw=0.8, zorder=4))
    ax.text(x + w / 2, y + 0.2, duty, ha="center", va="bottom",
            fontsize=9.6, color=P.MUTED, zorder=5)
    return (x, y, w, h)


ax.text(280, 354, "DISASSEMBLY LINE", ha="center", va="top",
        fontsize=24, fontweight="bold", color=P.INK)

tx, ty, tw, th = 160, 300, 160, 34
ax.add_patch(FancyBboxPatch((tx, ty), tw, th, boxstyle="round,pad=0.12,rounding_size=0.4",
                            facecolor=P.C_LE_F, edgecolor=P.C_LEACH, lw=1.8, zorder=3))
ax.text(tx + 74, ty + th - 1.4, "LEACH CSTR 1", ha="center", va="top",
        fontsize=16, fontweight="bold", color=P.INK, zorder=5)
ax.text(tx + 74, ty + th - 6, "HCl + NaClO3, 70–85 °C, ORP > 1.5 V",
        ha="center", va="top", fontsize=11, color=P.MUTED, zorder=5)
ax.add_patch(FancyBboxPatch((tx + 4, ty + 2), 78, 8, boxstyle="round,pad=0.04,rounding_size=0.15",
                            facecolor=P.C_SOL_F, edgecolor=P.C_SOLID, lw=1.1, zorder=4))
ax.text(tx + 43, ty + 6, "CSTR 3 AUGER  in the floor", ha="center", va="center",
        fontsize=11.4, fontweight="bold", color=P.INK, zorder=5)
ax.add_patch(FancyBboxPatch((tx + 104, ty + 18), 50, 8, boxstyle="round,pad=0.04,rounding_size=0.15",
                            facecolor=P.C_OIL_F, edgecolor=P.C_OIL, lw=1.1, zorder=4))
ax.text(tx + 129, ty + 22, "CSTR 2 WEIR", ha="center", va="center",
        fontsize=11.4, fontweight="bold", color=P.INK, zorder=5)
leach = (tx, ty, tw, th)
hop = unit(178, 340, 120, 10, P.C_SOL_F, P.C_SOLID, "HOPPER / SHREDDER", "no filter. Drops into the tank.")
flow([B(hop), (cx(hop), ty + th)], P.C_SOLID, "shred")

# oil branch, clear of the electrowinning row
flt = unit(430, 308, 58, 16, P.C_OIL_F, P.C_OIL, "FLOAT DEWATER", "liquor back to the tank")
dry = unit(496, 308, 56, 16, P.C_OIL_F, P.C_OIL, "DRYER", "80–120 °C")
pyro = unit(496, 284, 56, 18, P.C_OIL_F, P.C_OIL, "PYROLYZER", "400–600 °C")
quen = unit(496, 262, 56, 16, P.C_OIL_F, P.C_OIL, "QUENCH", "C5+ condenses")
still = unit(496, 238, 56, 18, P.C_OIL_F, P.C_OIL, "FRACTIONATOR", "three draws")
ab = unit(430, 262, 58, 16, P.C_HEAT_F, P.C_HEAT, "AFTERBURNER", "burns C1–C4")
naph = unit(430, 214, 40, 16, P.C_PROD_F, P.C_PROD, "NAPHTHA", "C5–C10")
mid = unit(474, 214, 40, 16, P.C_PROD_F, P.C_PROD, "FUEL OIL", "C11–C18")
wax = unit(518, 214, 34, 16, P.C_PROD_F, P.C_PROD, "WAX", "C19–C32")
char = unit(496, 190, 56, 16, P.C_SOL_F, P.C_SOLID, "CHAR", "to the silicon arc")
flow([(tx + tw, ty + 22), L(flt)], P.C_OIL, "float")
flow([R(flt), L(dry)], P.C_OIL, "organics")
flow([B(dry), T(pyro)], P.C_OIL, "dry charge")
flow([B(pyro), T(quen)], P.C_OIL, "vapor")
flow([B(quen), T(still)], P.C_OIL, "oil")
flow([L(quen), R(ab)], P.C_HEAT, "C1–C4")
flow([L(still), (cx(naph), 232), T(naph)], P.C_PROD, "C5–C10")
flow([B(still), T(mid)], P.C_PROD, "C11–C18")
flow([R(still), (cx(wax), 232), T(wax)], P.C_PROD, "C19–C32")
flow([B(pyro), (cx(pyro), 206), (cx(char), 206), T(char)], P.C_SOLID, "char")

# sink branch
sdw = unit(8, 300, 64, 16, P.C_SOL_F, P.C_SOLID, "SINK DEWATER", "liquor to the tank")
spl = unit(8, 276, 64, 16, P.C_SOL_F, P.C_SOLID, "VIBRATORY SPLIT", "plastic off mineral")
plast = unit(80, 276, 58, 16, P.C_OIL_F, P.C_OIL, "DENSE PLASTIC", "joins the dryer")
rin = unit(8, 252, 64, 16, P.C_IN_F, P.C_INORG, "RINSE", "liquor to regen leach")
burn = unit(8, 228, 64, 16, P.C_IN_F, P.C_INORG, "BURNOUT", "450–550 °C")
mill = unit(8, 204, 64, 16, P.C_IN_F, P.C_INORG, "MILL", "under 300 µm")
dig = unit(8, 178, 64, 18, P.C_LE_F, P.C_LEACH, "NaOH DIGEST", "80–90 °C")
fus = unit(80, 178, 58, 18, P.C_HEAT_F, P.C_HEAT, "FUSION", "quartz returns")
gel = unit(8, 154, 64, 16, P.C_PROD_F, P.C_PROD, "SiO2 GEL", "HCl drop, calcine")
flow([(tx, ty + 6), R(sdw)], P.C_SOLID, "sink")
flow([B(sdw), T(spl)], P.C_SOLID, "solids")
flow([R(spl), L(plast)], P.C_OIL, "plastic")
flow([B(spl), T(rin)], P.C_INORG, "mineral")
flow([B(rin), T(burn)], P.C_INORG, "rinsed")
flow([B(burn), T(mill)], P.C_INORG, "burned")
flow([B(mill), T(dig)], P.C_INORG, "powder")
flow([R(dig), L(fus)], P.C_HEAT, "quartz")
flow([B(dig), T(gel)], P.C_PROD, "silicate")
flow([R(plast), (148, cy(plast)), (148, 337), (548, 337), (548, cy(dry)), R(dry)], P.C_OIL, "plastic")

# liquor, then one electrowinning row
pump = unit(168, 276, 40, 14, P.C_LE_F, P.C_LEACH, "PUMP", "tank discharge")
coal = unit(214, 276, 48, 14, P.C_LE_F, P.C_LEACH, "COALESCER", "free oil off")
xf = unit(268, 276, 52, 14, P.C_SOL_F, P.C_SOLID, "CROSSFLOW", "0.2 µm, 25 m²")
cem = unit(168, 254, 152, 16, P.C_CEM_F, P.C_CEM, "CEM STACK", "cations to ~20 g/L. Diluate to the tank.")
flow([(cx(leach), ty), T(pump)], P.C_LEACH, "liquor")
flow([R(pump), L(coal)], P.C_LEACH, "liquor")
flow([R(coal), L(xf)], P.C_LEACH, "liquor")
flow([B(xf), (cx(xf), 270), (cx(cem), 270), T(cem)], P.C_LEACH, "filtrate")
flow([T(coal), (cx(coal), 292), (420, 292), (420, cy(flt)), L(flt)], P.C_OIL, "free oil")

ew = []
for i, (tag, duty) in enumerate([
    ("EW-1 Au", "powder"), ("EW-2 Ag", "Ti peel"), ("EW-3 Cu", "316L"),
    ("EW-4 Pb", "316L"), ("EW-5 Sn", "316L"), ("EW-6 Ni", "Ti peel"),
    ("EW-7 Fe", "powder"), ("EW-8 Cd", "316L"), ("EW-9 Zn", "Al peel"),
]):
    ew.append(cell(156 + i * 28, 214, 26, 32, tag, duty))
    if i:
        flow([R(ew[i - 1]), L(ew[i])], P.C_PROD, "")
flow([B(cem), T(ew[0])], P.C_PROD, "concentrate")

bleed = unit(156, 188, 78, 16, P.C_IN_F, P.C_INORG, "PK-4 / PK-5 BLEED", "before any hydroxide")
pal = unit(242, 188, 40, 16, P.C_IN_F, P.C_INORG, "P-Al", "pH 5.0–5.5")
pmg = unit(288, 188, 40, 16, P.C_IN_F, P.C_INORG, "P-Mg", "pH 10.5–11")
pca = unit(334, 188, 40, 16, P.C_IN_F, P.C_INORG, "P-Ca", "pH 12–12.5")
flow([B(ew[8]), (cx(ew[8]), 206), (cx(bleed), 206), T(bleed)], P.C_INORG, "EW-9 liquor")
flow([R(bleed), L(pal)], P.C_INORG, "liquor")
flow([R(pal), L(pmg)], P.C_INORG, "liquor")
flow([R(pmg), L(pca)], P.C_INORG, "liquor")

brine = unit(156, 162, 78, 16, P.C_LE_F, P.C_LEACH, "pH 9 TANK", "borate as B(OH)4−")
aem = unit(242, 162, 78, 16, P.C_AEM_F, P.C_AEM, "AEM STACK", "anions into one concentrate")
fl = unit(328, 162, 46, 16, P.C_PROD_F, P.C_PROD, "FLUORIDE", "CaF2 to the HF cell")
su = unit(156, 136, 56, 16, P.C_PROD_F, P.C_PROD, "SULFATE", "Na2SO4 to PK-5B")
ph = unit(220, 136, 56, 16, P.C_PROD_F, P.C_PROD, "PHOSPHATE", "to the farm")
bo = unit(284, 136, 56, 16, P.C_PROD_F, P.C_PROD, "BORATE", "calcine to B2O3")
flow([B(bleed), T(brine)], P.C_LEACH, "spent brine")
flow([R(brine), L(aem)], P.C_AEM, "pH 9")
flow([R(aem), L(fl)], P.C_PROD, "concentrate")
flow([B(aem), (cx(aem), 152), (cx(su), 152), T(su)], P.C_PROD, "after F")
flow([R(su), L(ph)], P.C_PROD, "liquor")
flow([R(ph), L(bo)], P.C_PROD, "liquor")
flow([R(dig), (78, cy(dig)), (78, cy(aem)), L(aem)], P.C_INORG, "digest liquor")

ks = unit(80, 136, 64, 16, P.C_LE_F, P.C_LEACH, "K SPLIT", "5–10 °C. KCl out.")
bmed = unit(80, 112, 64, 16, P.C_LE_F, P.C_LEACH, "BMED", "HCl and NaOH")
regen = unit(80, 88, 64, 16, P.C_LE_F, P.C_LEACH, "REGEN LEACH", "HCl + NaClO3")
cru = unit(152, 88, 58, 16, P.C_AN_F, P.C_AN, "CRU", "Cl2 + NaOH")
flow([L(aem), (236, cy(aem)), (236, 154), (148, 154), R(ks)], P.C_LEACH, "diluate")
flow([B(ks), T(bmed)], P.C_LEACH, "NaCl")
flow([B(bmed), T(regen)], P.C_LEACH, "HCl")
flow([R(regen), L(cru)], CL2, "NaOH")
flow([L(regen), (2, cy(regen)), (2, 350), (tx, 350), (tx, ty + th)], P.C_LEACH, "acid return")

scrub = unit(80, 228, 64, 16, P.C_SOL_F, P.C_SOLID, "N SCRUB", "HCl takes NH3")
flow([R(burn), L(scrub)], P.C_HEAT, "burnout gas")
flow([R(pyro), (552, cy(pyro)), (552, 52), (72, 52), (72, cy(scrub)), L(scrub)], P.C_OIL, "pyro gas")

al = unit(242, 88, 42, 16, P.C_HEAT_F, P.C_HEAT, "Al POT", "700 °C")
mg = unit(290, 88, 42, 16, P.C_HEAT_F, P.C_HEAT, "Mg POT", "700 °C")
ca = unit(338, 88, 42, 16, P.C_HEAT_F, P.C_HEAT, "Ca POT", "800 °C")
arc = unit(8, 112, 64, 16, P.C_HEAT_F, P.C_HEAT, "Si ARC", "gel + char")
bret = unit(348, 112, 58, 16, P.C_HEAT_F, P.C_HEAT, "B RETORT", "B2O3 + metal")
flow([B(pca), (cx(pca), 108), (cx(al), 108), T(al)], P.C_PROD, "hydroxide")
flow([B(gel), T(arc)], P.C_PROD, "silica")
flow([R(char), (558, cy(char)), (558, 44), (cx(arc), 44), T(arc)], P.C_SOLID, "char")
flow([B(bo), (cx(bo), 128), (cx(bret), 128), T(bret)], P.C_PROD, "B2O3")
flow([B(al), (cx(al), 80), (cx(cru), 80), B(cru)], CL2, "Cl2")

ax.text(8, 22, "STREAMS", fontsize=13, fontweight="bold", color=P.INK)
key = [
    (P.C_SOLID, "solid"), (P.C_LEACH, "liquor / acid"), (P.C_OIL, "oil / organic"),
    (P.C_INORG, "utility"), (P.C_HEAT, "heat / flue"), (P.C_PROD, "product"),
    (CL2, "chlorine"), (P.C_AEM, "anion cut"),
]
for i, (col, name) in enumerate(key):
    x = 8 + i * 64
    ax.plot([x, x + 12], [14, 14], color=col, lw=5.0, solid_capstyle="butt", zorder=8)
    ax.text(x + 14, 14, name, fontsize=12, color=P.INK, va="center")

out = P.ROOT / "master_disassembly_pfd.png"
fig.savefig(out, dpi=90, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", out)
