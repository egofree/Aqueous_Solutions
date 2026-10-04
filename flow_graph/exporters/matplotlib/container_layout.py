#!/usr/bin/env python3
"""Plan view: 40HC wet + 20HC thermal, with segregated air headers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
import params as P
from flow_graph.pfd_bridge import graph_path, ia_register_lines, load, sector_edges  # noqa: E402
from drawlib import box, cx, cy, R, L, T, B, arrow, slabel

C_DUST = "#57534e"
C_ACIDG = "#166534"
C_H2 = "#1e3a8a"
C_NCG = "#b45309"

fig, ax = plt.subplots(figsize=(22.0, 17.2), dpi=140)
ax.set_xlim(0, 100)
ax.set_ylim(0, 78)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)

ax.text(50, 77.2, "CONTAINER LAYOUT  —  40HC WET  +  20HC THERMAL  +  AIR",
        ha="center", va="top", fontsize=27.3, fontweight="bold", color=P.INK)
ax.text(50, 75.35,
        "Four headers, never one   ·   dust ≠ acid gas ≠ H2 ≠ oil vapor   ·   boxes held negative to the yard",
        ha="center", va="top", fontsize=17.1, color=P.MUTED)


def hood(x, y, color):
    ax.add_patch(Polygon([(x - 0.55, y), (x + 0.55, y), (x, y + 0.7)],
                         closed=True, facecolor=color, edgecolor=color, lw=0.6, zorder=7))


def duct(p1, p2, color, lw=1.7):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                connectionstyle="arc3,rad=0",
                                linestyle="-", shrinkA=0.2, shrinkB=0.2),
                zorder=6)


# shells
WET = (7.5, 43.4, 79.0, 16.6)
HOT = (7.5, 24.6, 40.0, 16.2)

ax.add_patch(Rectangle((WET[0], WET[1]), WET[2], WET[3],
                       facecolor="#e7e5e4", edgecolor=P.INK, linewidth=2.3, zorder=1))
ax.add_patch(Rectangle((HOT[0], HOT[1]), HOT[2], HOT[3],
                       facecolor="#e7e5e4", edgecolor=P.INK, linewidth=2.3, zorder=1))

ax.text(WET[0] + WET[2] / 2, WET[1] + WET[3] + 0.45,
        "40HC  WET MODULE    12.03 × 2.35 × 2.70 m    north = cells    south = leach train",
        ha="center", va="bottom", fontsize=16.1, fontweight="bold", color=P.INK)
ax.text(HOT[0] + HOT[2] / 2, HOT[1] - 0.5,
        "20HC  THERMAL MODULE    5.90 × 2.35 × 2.39 m",
        ha="center", va="top", fontsize=16.1, fontweight="bold", color=P.INK)

ax.add_patch(Rectangle((WET[0] + WET[2], WET[1] + 3.0), 0.7, WET[3] - 6.0,
                       facecolor=P.C_SOL_F, edgecolor=P.INK, lw=1.4, zorder=2))
ax.text(WET[0] + WET[2] + 1.3, cy(WET), "DOORS\nFEED", ha="left", va="center",
        fontsize=12.4, fontweight="bold", color=P.C_SOLID)
ax.add_patch(Rectangle((HOT[0] - 0.7, HOT[1] + 3.0), 0.7, HOT[3] - 6.0,
                       facecolor=P.C_OIL_F, edgecolor=P.C_OIL, lw=1.4, zorder=2))
ax.text(HOT[0] - 1.45, cy(HOT), "DOORS\nHOT", ha="right", va="center",
        fontsize=12.4, fontweight="bold", color=P.C_OIL)

# roof duct rail above 40HC
ax.add_patch(Rectangle((7.5, 61.0), 79.0, 3.55,
                       facecolor="#fafaf9", edgecolor=P.C_LEACH, linewidth=1.15,
                       linestyle="--", zorder=1))
ax.text(8.0, 64.2, "ROOF DUCT RAIL  (wet box)    acid-gas header east to yard    H2 header separate    dust header local at doors",
        ha="left", va="bottom", fontsize=12.7, fontweight="bold", color=P.C_LEACH)

ew = box(ax, 8.3, 53.55, 34.0, 5.7, P.C_SOL_F, P.C_SOLID, "EW-1 … EW-9",
         "hood each anode headspace", ts=17.1, ss=11.5)
pk = box(ax, 43.0, 53.55, 14.6, 5.7, P.C_SOL_F, P.C_SOLID, "POLISH BANK",
         "PK-6 / PK-9 sealed lids", ts=16.1, ss=11.2)
bmed = box(ax, 58.3, 53.55, 16.4, 5.7, P.C_LE_F, P.C_LEACH, "BMED + CRU",
           "H2 cathode  ·  Cl2 anode", ts=16.4, ss=11.2)
ph = box(ax, 75.4, 53.55, 10.3, 5.7, P.C_IN_F, P.C_INORG, "P-Al P-Mg\nP-Ca",
         "under BMED NaOH", ts=15.5, ss=10.8)

ax.add_patch(Rectangle((8.3, 51.55), 77.4, 1.85,
                       facecolor="#fafaf9", edgecolor="#d6d3d1", lw=0.8, zorder=2))
ax.text(47.0, 52.45, "0.70 m aisle", ha="center", va="center",
        fontsize=12.4, color=P.MUTED, style="italic")

shred = box(ax, 73.6, 44.4, 12.1, 6.9, P.C_SOL_F, P.C_SOLID, "HOPPER\nSHREDDER",
            "dust hood at throat", ts=16.1, ss=11.2)
l1 = box(ax, 59.2, 44.4, 13.6, 6.9, P.C_LE_F, P.C_LEACH, "LEACH CSTR 1",
         "lid + mist takeoff", ts=16.1, ss=11.2)
l2 = box(ax, 38.6, 44.4, 19.8, 6.9, P.C_LE_F, P.C_LEACH, "LEACH CSTR 2–3 FORK",
         "float weir faces alley", ts=16.1, ss=11.2)
vdf = box(ax, 24.6, 44.4, 13.2, 6.9, P.C_SOL_F, P.C_SOLID, "VDF",
          "drum filter", ts=16.7, ss=11.2)
spl = box(ax, 16.5, 44.4, 7.3, 6.9, P.C_SOL_F, P.C_SOLID, "VIB.\nSPLIT",
          "west train", ts=15.5, ss=10.8)
dig = box(ax, 8.3, 44.4, 7.4, 6.9, P.C_IN_F, P.C_INORG, "NaOH\nDIGEST",
          "caustic mist", ts=15.5, ss=10.8)

arrow(ax, L(shred), R(l1), P.C_SOLID, lw=1.3)
arrow(ax, L(l1), R(l2), P.C_LEACH, lw=1.3)
arrow(ax, L(l2), R(vdf), P.C_LEACH, lw=1.3)
arrow(ax, L(vdf), R(spl), P.C_SOLID, lw=1.15)

# alley
ax.add_patch(Rectangle((7.5, 40.7), 40.0, 2.55,
                       facecolor=P.C_HEAT_F, edgecolor=P.C_HEAT, lw=1.1, linestyle="--", zorder=2))
ax.text(27.5, 41.95, "ALLEY  solids chutes + thermal-oil + NCG duct + acid-gas jumper",
        ha="center", va="center", fontsize=12.7, fontweight="bold", color=P.C_HEAT)

dry = box(ax, 8.3, 32.7, 10.2, 7.2, P.C_OIL_F, P.C_OIL, "DRYER",
          "HX-4  Q3", ts=17.1, ss=11.5)
pyro = box(ax, 19.3, 32.7, 15.0, 7.2, P.C_OIL_F, P.C_OIL, "INDUCTION\nPYROLYZER",
           "pipe on long axis", ts=16.4, ss=11.2)
quen = box(ax, 35.1, 36.5, 11.5, 3.4, P.C_OIL_F, P.C_OIL, "QUENCH", "", ts=15.5)
still = box(ax, 35.1, 32.7, 11.5, 3.5, P.C_OIL_F, P.C_OIL, "STILL", "HX-3", ts=15.5, ss=10.8)
burn = box(ax, 8.3, 25.3, 12.4, 6.7, P.C_IN_F, P.C_INORG, "BURNOUT\nROTARY",
           "off-gas to AB", ts=16.4, ss=11.2)
ab = box(ax, 21.5, 25.3, 11.6, 6.7, P.C_HEAT_F, P.C_HEAT, "AFTERBURNER",
         "own stack  Q1", ts=16.1, ss=11.2)
mill = box(ax, 33.9, 25.3, 12.7, 6.7, P.C_IN_F, P.C_INORG, "MILL",
           "local dust sock", ts=16.7, ss=11.2)

arrow(ax, R(dry), L(pyro), P.C_OIL, lw=1.3)
arrow(ax, R(pyro), L(quen), P.C_OIL, lw=1.2)
arrow(ax, B(quen), T(still), P.C_OIL, lw=1.0)
arrow(ax, R(burn), L(ab), C_NCG, lw=1.25)
arrow(ax, (cx(l2), WET[1]), (cx(dry), HOT[1] + HOT[3]), P.C_OIL, lw=1.45)
arrow(ax, (cx(spl), WET[1]), (cx(burn), HOT[1] + HOT[3]), P.C_INORG, lw=1.45)
arrow(ax, (cx(mill), HOT[1] + HOT[3]), (cx(dig), WET[1]), P.C_INORG, lw=1.15, ls="--")

# ── yard: products + air plant ───────────────────────────
ax.add_patch(Rectangle((50.0, 24.6), 36.5, 16.2,
                       facecolor="#ccfbf1", edgecolor=P.C_PROD, linewidth=1.6, zorder=1))
ax.text(68.25, 40.0, "YARD", ha="center", va="top",
        fontsize=17.7, fontweight="bold", color=P.INK)

met = box(ax, 51.1, 34.55, 8.2, 4.7, P.C_PROD_F, P.C_PROD, "METALS", "", ts=14.9)
oilp = box(ax, 60.0, 34.55, 8.2, 4.7, P.C_OIL_F, P.C_OIL, "OIL CUTS", "", ts=14.9)
hyd = box(ax, 68.9, 34.55, 8.0, 4.7, P.C_PROD_F, P.C_PROD, "SILICATE", "", ts=14.6)
h2t = box(ax, 77.6, 34.55, 7.8, 4.7, P.C_CA_F, P.C_CEM, "H2 / O2",
          "to cryo / FC", ts=14.6, ss=10.8)

dust = box(ax, 51.1, 25.4, 8.4, 8.3, P.C_SOL_F, P.C_SOLID, "BAGHOUSE",
           "shredder +\nmill dust\nrecycle to leach", ts=15.5, ss=11.2)
dem = box(ax, 60.2, 25.4, 8.2, 8.3, P.C_LE_F, P.C_LEACH, "DEMISTER",
          "acid mist\nthen packed\ntower", ts=15.5, ss=11.2)
scr = box(ax, 69.1, 25.4, 9.0, 8.3, P.C_LE_F, P.C_LEACH, "ALK SCRUBBER",
          "NaOH from BMED\nCl2 HCl Br\nliquor → CRU", ts=15.2, ss=10.8)
stk = box(ax, 78.8, 25.4, 6.6, 8.3, P.C_SOL_F, P.C_SOLID, "FAN\nSTACK",
          "wet discharge", ts=15.5, ss=10.8)

pwr = box(ax, 50.0, 19.55, 17.2, 4.5, P.C_HEAT_F, P.C_HEAT, "RECTIFIER / DC BUS",
          "outside both atmospheres", ts=15.5, ss=11.2)
mak = box(ax, 68.0, 19.55, 18.5, 4.5, P.C_IN_F, P.C_INORG, "MAKEUP AIR + Q4 HVAC",
          "filtered inlets opposite the hoods", ts=15.5, ss=11.2)

# ── duct geometry ────────────────────────────────────────
# Acid-gas roof header: hoods on EW, leach, BMED anode, digest → demister
for x in (cx(ew) - 10, cx(ew), cx(ew) + 10, cx(pk), cx(bmed) + 3, cx(l1), cx(l2), cx(dig)):
    hood(x, 61.05, C_ACIDG)
ax.plot([8.3, 85.5], [62.15, 62.15], color=C_ACIDG, lw=2.0, zorder=6)
duct((85.5, 62.15), (85.5, 33.5), C_ACIDG, lw=1.8)
duct((85.5, 33.5), (cx(dem), dem[1] + dem[3]), C_ACIDG, lw=1.8)
arrow(ax, R(dem), L(scr), C_ACIDG, lw=1.3)
arrow(ax, R(scr), L(stk), C_ACIDG, lw=1.3)
slabel(ax, 86.4, 50.0, "acid-gas\nheader", C_ACIDG, ha="left", size=7.4)

# H2 header: BMED cathode only, to H2 tote — does not enter scrubber
hood(cx(bmed) - 3.2, 63.15, C_H2)
ax.plot([cx(bmed) - 3.2, 81.5], [63.85, 63.85], color=C_H2, lw=1.7, zorder=6)
duct((81.5, 63.85), (81.5, 39.3), C_H2, lw=1.5)
duct((81.5, 39.3), T(h2t), C_H2, lw=1.5)
slabel(ax, 82.2, 58.4, "H2", C_H2, ha="left", size=7.4)

# Dust: shredder + mill → baghouse. Not into acid header.
hood(cx(shred), 43.4 + 6.9, C_DUST)
duct((cx(shred), 51.3), (cx(shred), 61.6), C_DUST, lw=1.4)
ax.plot([cx(shred), 51.1], [61.6, 61.6], color=C_DUST, lw=1.4, zorder=6)
duct((51.1, 61.6), (cx(dust), dust[1] + dust[3]), C_DUST, lw=1.5)
hood(cx(mill), mill[1], C_DUST)
duct((cx(mill), mill[1]), (cx(mill), 24.2), C_DUST, lw=1.2)
ax.plot([cx(mill), cx(dust)], [24.2, 24.2], color=C_DUST, lw=1.2, zorder=6)
duct((cx(dust), 24.2), (cx(dust), dust[1]), C_DUST, lw=1.2)
slabel(ax, 54.0, 62.55, "dust", C_DUST, size=7.4)

# NCG: quench → afterburner (already a process line). Roof stack on 20HC only.
hood(cx(quen), quen[1] + quen[3], C_NCG)
duct((cx(quen), quen[1] + quen[3] + 0.15), (cx(ab), ab[1] + ab[3]), C_NCG, lw=1.4)
ax.add_patch(Circle((cx(ab), 24.15), 0.45, facecolor=C_NCG, edgecolor=C_NCG, zorder=7))
slabel(ax, cx(ab), 23.35, "AB→FLUE_CAP", C_NCG, size=7.0)

# makeup air — west wet + south hot, opposite hoods
ax.annotate("", xy=(8.0, 52.45), xytext=(4.6, 52.45),
            arrowprops=dict(arrowstyle="-|>", color=P.C_INORG, lw=1.5))
slabel(ax, 4.5, 53.2, "makeup", P.C_INORG, ha="left", size=7.2)
ax.annotate("", xy=(27.5, 24.6), xytext=(27.5, 21.6),
            arrowprops=dict(arrowstyle="-|>", color=P.C_INORG, lw=1.5))
slabel(ax, 28.2, 21.9, "makeup", P.C_INORG, ha="left", size=7.2)

ax.text(7.5, 18.55, "AIR  —  FOUR HEADERS", fontsize=18.6, fontweight="bold", color=P.INK)
ax.text(7.5, 17.45,
        "1  DUST (grey).  Hopper/shredder throat and mill sock to the yard baghouse. Fines return to LEACH CSTR 1. Never into the packed tower.\n"
        "2  ACID GAS (green).  Lid takeoffs on both leach CSTRs, a hood on every EW / polish anode headspace, BMED anode / CRU Cl2, digest mist.\n"
        "    Roof header runs the length of the 40HC, drops in the yard through a demister into an alkaline packed tower fed with BMED NaOH.\n"
        "    Pregnant scrubber liquor → CRU (S66 via ACID_POLISH). Upset stack residual only — not continuous outdoor dump (AQS-VENT-001).\n"
        "3  H2 (blue).  BMED cathode only. Own header, own tote, onward to the cryo / fuel-cell sheet. H2 does not enter the Cl2 tower.\n"
        "4  OIL VAPOR / NCG (amber).  Quench off-gas and burnout off-gas go to AFTERBURNER and its own roof stack on the 20HC.\n"
        "    That stack is not tied to the wet scrubber. Hydrocarbon class stays inside the 20HC gasket.\n"
        "\n"
        "Both boxes run negative to the yard. Makeup air enters opposite the hoods (west bulkhead of the 40, south wall of the 20).\n"
        "PK-6 Hg and PK-9 radionuclides have welded lids and tap the acid-gas header through a dedicated hose, not a shared headspace.\n"
        "Do not put a common HVAC return across the alley. Heat is HX jumpers; air is not.",
        ha="left", va="top", fontsize=14.7, color=P.MUTED, linespacing=1.22)


# Layout sheet — light graph cross-link overlay (not a process PFD)
_G = load()
_X = sector_edges("container_cross", _G)
_GP = graph_path().name
_reg = ia_register_lines(_X)
ax.text(7.5, 11.2, f"GRAPH CROSS-LINKS ({_GP}) — container layout overlay",
        fontsize=14, fontweight="bold", color=P.INK)
for i, line in enumerate(_reg):
    ax.text(7.5, 10.4 - i * 0.55, line, ha="left", va="top", fontsize=10.2, color=P.MUTED)
ax.text(7.5, 10.4 - len(_reg) * 0.55 - 0.2,
        "Non-process layout sheet: S##/IA from graph only; no invented rates.",
        ha="left", va="top", fontsize=10.8, color=P.MUTED)

ax.text(50.0, 0.35, P.NAMING_FOOT + "    container layout graph overlay", ha="center", va="bottom", fontsize=11.5, color=P.MUTED)

plt.tight_layout(pad=0.25)
out = getattr(P, "OUT_CONTAINER", P.ROOT / "container_layout.png")
fig.savefig(out, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", out)
