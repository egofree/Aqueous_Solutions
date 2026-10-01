#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""Electrical SLD — graph-bridged (elec/ess edges from plant_flow_graph.json).

Sole topology authority: ``flow_graph/plant_flow_graph.json``.
Layout style remains drawlib/matplotlib. S17 + ESS peers (ZNBR2 / MEOH /
HYDRO) are labeled from graph edges; rates shown only when the graph
supplies them (null stays null). Do not invent streams or nameplates.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import params as P
from drawlib import box, cx, cy, R, L, T, B, arrow, slabel

from flow_graph.pfd_bridge import (  # noqa: E402
    elec_ess_bridge_edges,
    format_rate,
    graph_path,
    load,
)

C_AC = "#b45309"
C_AC_F = "#fff7ed"
C_DC = "#1e3a8a"
C_DC_F = "#dbeafe"
C_PULSE = "#6d28d9"
C_PULSE_F = "#ede9fe"
C_PV = "#15803d"
C_PV_F = "#dcfce7"
C_SW = "#1c1917"
C_PH = "#78716c"  # placeholder peers
C_PH_F = "#f5f5f4"

fig, ax = plt.subplots(figsize=(24.0, 18.0), dpi=140)
ax.set_xlim(0, 120)
ax.set_ylim(0, 90)
ax.set_aspect("equal")
ax.axis("off")
fig.patch.set_facecolor(P.BG)
ax.set_facecolor(P.BG)

g = load()
bridge = elec_ess_bridge_edges(g)
gp = graph_path().name

ax.text(60, 89.0, "SINGLE-LINE  —  480 Y / 277 V   3φ   60 Hz",
        ha="center", va="top", fontsize=18.0, fontweight="bold", color=P.INK)
ax.text(60, 86.9,
        "Grid feed / backfeed left    ·    ATS center    ·    plant loads right    ·    "
        "Sol-Ark 60K + PV + ZnBr2 + H2 BACKUP_GEN + PEM FUEL_CELL + MEOH_FC + HYDRO_SET",
        ha="center", va="top", fontsize=11.0, color=P.MUTED)
ax.text(60, 85.2,
        f"Graph-bridged elec/ess from {gp}  ·  S17 + ESS peers  ·  null rates stay null",
        ha="center", va="top", fontsize=9.0, color=P.MUTED)


def bus(x1, x2, y, color=C_AC, lw=2.6):
    ax.plot([x1, x2], [y, y], color=color, lw=lw, solid_capstyle="butt", zorder=5)


def drop(x, y1, y2, color=C_AC, lw=1.7):
    ax.plot([x, x], [y1, y2], color=color, lw=lw, zorder=5)


def disc(x, y, label=""):
    """Open-square disconnect on a vertical drop."""
    ax.add_patch(Rectangle((x - 0.55, y - 0.55), 1.1, 1.1,
                           facecolor=P.BG, edgecolor=C_SW, lw=1.5, zorder=6))
    ax.plot([x - 0.35, x + 0.35], [y - 0.35, y + 0.35], color=C_SW, lw=1.3, zorder=7)
    if label:
        ax.text(x + 0.85, y, label, ha="left", va="center", fontsize=7.6, color=P.MUTED)


def meter(x, y):
    ax.add_patch(Circle((x, y), 1.15, facecolor=C_AC_F, edgecolor=C_AC, lw=1.5, zorder=6))
    ax.text(x, y, "M", ha="center", va="center", fontsize=9.0, fontweight="bold", color=C_AC, zorder=7)


# ── LEFT: utility ────────────────────────────────────────
poco = box(ax, 2.0, 66.2, 16.5, 7.4, C_AC_F, C_AC, "UTILITY POCO",
           "480 Y / 277 V  3φ\n60 Hz   200 A class", ts=12.2, ss=8.4)
meter(12.5, 63.4)
drop(12.5, 66.2, 64.55)
drop(12.5, 62.25, 60.6)
ud = box(ax, 2.0, 55.4, 16.5, 5.2, C_AC_F, C_AC, "UTILITY DISCO",
         "3-pole  200 A  fused", ts=11.6, ss=8.2)
drop(12.5, 55.4, 52.9)

# split: GRID port of inverter (bidirectional) and ATS source A
bus(12.5, 28.5, 52.9)
drop(28.5, 52.9, 44.6)
disc(28.5, 46.2, "G")
slabel(ax, 29.5, 50.6, "GRID feed + backfeed", C_AC, ha="left", size=8.2)

bus(12.5, 42.0, 59.6)
drop(12.5, 60.6, 59.6)
drop(42.0, 59.6, 56.4)

# ── CENTER: ATS + Sol-Ark ────────────────────────────────
ats = box(ax, 33.5, 49.6, 17.0, 6.8, P.C_SOL_F, P.C_SOLID, "ATS  200 A",
          "3-pole  480 V\nS1 utility bypass\nS2 Sol-Ark LOAD", ts=12.4, ss=8.2)

sol = box(ax, 22.0, 32.6, 28.4, 12.0, C_PV_F, C_PV, "SOL-ARK  60K-3P-480V",
          "277/480 V  3φ native\n60 kW cont.   72 A out\nGRID / LOAD / GEN  200 A\npassthrough 180 A cont.\nUL 1741 SB  ·  IEEE 1547",
          ts=13.0, ss=8.4)

drop(42.0, 49.6, 44.6)
disc(42.0, 46.2, "L")
arrow(ax, (42.0, 44.6), (42.0, 49.6), C_AC, lw=1.8)
slabel(ax, 43.0, 48.0, "LOAD  →  ATS S2", C_AC, ha="left", size=8.0)

arrow(ax, (28.5, 46.2), (28.5, 44.6), C_AC, lw=1.8)
slabel(ax, 19.2, 45.6, "GRID ↔", C_AC, ha="left", size=8.2)

bus(50.5, 62.0, 53.0)
arrow(ax, R(ats), (62.0, cy(ats)), C_AC, lw=2.2)

# ── RIGHT: plant main + loads ────────────────────────────
main = box(ax, 62.0, 49.6, 16.5, 6.8, C_AC_F, C_AC, "PLANT MAIN",
           "3-pole  200 A\n480 Y / 277 V", ts=12.4, ss=8.2)
arrow(ax, (62.0, cy(ats)), L(main), C_AC, lw=2.2)

# S17 from graph — Sol-Ark / plant bus → rectifier (and plant AC loads)
e17 = bridge.get("S17")
if e17 is not None:
    rate17 = format_rate(e17)
    slabel(ax, 70.2, 58.8, f"S17  {e17.carries or 'power bus'}  ·  {rate17}",
           C_AC, ha="left", size=8.4)
    slabel(ax, 79.0, 48.8, "S17", C_DC, ha="center", size=9.0)

mcc = box(ax, 81.0, 60.4, 36.5, 16.2, C_AC_F, C_AC, "", "")
ax.text(99.25, 75.5, "MCC  —  AC LOADS", ha="center", va="top",
        fontsize=13.2, fontweight="bold", color=C_AC, zorder=4)
ac1 = box(ax, 82.2, 68.6, 10.4, 5.2, C_AC_F, C_AC, "SHREDDER", "7.5 kW", ts=10.6, ss=8.0)
ac2 = box(ax, 93.4, 68.6, 11.2, 5.2, C_AC_F, C_AC, "PUMPS\nAGITATORS", "2.5 kW", ts=10.2, ss=7.8)
ac3 = box(ax, 105.4, 68.6, 11.0, 5.2, C_AC_F, C_AC, "FANS\nSCRUBBER", "3.0 kW", ts=10.2, ss=7.8)
ac4 = box(ax, 82.2, 61.6, 10.4, 5.8, C_AC_F, C_AC, "INDUCTION\n5–20 kHz", "0–25 kW", ts=10.2, ss=7.8)
ac5 = box(ax, 93.4, 61.6, 11.2, 5.8, C_AC_F, C_AC, "VDF MILL\nVIBRATORY", "2.0 kW", ts=10.2, ss=7.8)
ac6 = box(ax, 105.4, 61.6, 11.0, 5.8, C_AC_F, C_AC, "HVAC Q4", "1.5 kW", ts=10.6, ss=8.0)

rect = box(ax, 81.0, 32.6, 36.5, 24.4, C_DC_F, C_DC, "", "")
ax.text(99.25, 56.0, "RECTIFIER SKID  —  DC PROCESS", ha="center", va="top",
        fontsize=13.0, fontweight="bold", color=C_DC, zorder=4)
r1 = box(ax, 82.2, 47.4, 10.6, 7.2, C_DC_F, C_DC, "RECT-EW",
         "0–36 V DC\n0–250 A\nsteady / PR", ts=10.8, ss=7.8)
r2 = box(ax, 93.6, 47.4, 10.6, 7.2, C_DC_F, C_DC, "RECT-BMED",
         "0–80 V DC\n0–120 A\nsteady only", ts=10.6, ss=7.8)
r3 = box(ax, 105.0, 47.4, 11.2, 7.2, C_PULSE_F, C_PULSE, "RECT-PK",
         "0–12 V DC\n0–40 A avg\npulsed", ts=10.6, ss=7.8)
ew = box(ax, 82.2, 33.8, 16.6, 12.2, C_DC_F, C_DC, "EW STRING",
         "EW-1 … EW-9 series\n80–180 A\n~20–28 V stack\nCu PR · Ni/Fe/Zn pulse",
         ts=11.4, ss=8.2)
pk = box(ax, 99.6, 40.4, 16.6, 5.6, C_PULSE_F, C_PULSE, "POLISH BANK",
         "2–8 V   2–15 A   20–40 % duty", ts=10.6, ss=7.8)
bmed = box(ax, 99.6, 33.8, 16.6, 5.8, C_DC_F, C_DC, "BMED + CRU",
           "36–80 V   50–100 A steady", ts=10.6, ss=7.8)

drop(78.5, cy(main), 68.4)
bus(78.5, 81.0, 68.4)
arrow(ax, (80.6, 68.4), (81.0, 68.4), C_AC, lw=1.8)
drop(78.5, cy(main), 44.8)
bus(78.5, 81.0, 44.8)
arrow(ax, (80.6, 44.8), (81.0, 44.8), C_AC, lw=1.8)

arrow(ax, B(r1), T(ew), C_DC, lw=1.3)
arrow(ax, B(r2), T(bmed), C_DC, lw=1.3)
arrow(ax, B(r3), T(pk), C_PULSE, lw=1.3)

# ── BOTTOM LEFT: PV + battery ────────────────────────────
pv = box(ax, 2.0, 32.6, 17.6, 12.0, C_PV_F, C_PV, "PV ARRAY",
         "ground mount\n~70 kW STC\n4 MPPT  150–850 V\nmax 78 kW STC in",
         ts=12.4, ss=8.4)
arrow(ax, R(pv), L(sol), C_PV, lw=1.8)
slabel(ax, 20.0, 39.4, "PV DC", C_PV, size=8.2)

batt = box(ax, 2.0, 16.6, 28.4, 13.2, C_DC_F, C_DC, "ZnBr2  FLOW BATTERY",
           "SEM Tech CEM / AEM stack\n~600 V nom.   160–700 V window\n~120 kWh usable   60 kW\n2 × 50 A battery ports\nBMS gateway → CAN",
           ts=12.6, ss=8.4)
zn = box(ax, 32.0, 23.4, 18.4, 6.4, C_DC_F, C_DC, "Zn anolyte tank",
         "Zn(II) / Zn plate on charge", ts=10.6, ss=7.8)
br = box(ax, 32.0, 16.6, 18.4, 6.0, C_PULSE_F, C_PULSE, "Br catholyte tank",
         "Br- / Br2 complexed", ts=10.6, ss=7.8)
arrow(ax, R(batt), L(zn), C_DC, lw=1.1)
arrow(ax, R(batt), L(br), C_PULSE, lw=1.1)

# ESS charge/discharge labels from graph (IA-* — rates null)
e_chg = bridge.get("ZNBR2_CHG")
e_dis = bridge.get("ZNBR2_DIS")
if e_chg is not None:
    slabel(ax, 16.2, 30.6, f"{e_chg.stream_id} charge  ·  {format_rate(e_chg)}",
           C_DC, ha="center", size=7.2)
if e_dis is not None:
    slabel(ax, 16.2, 15.4, f"{e_dis.stream_id} discharge  ·  {format_rate(e_dis)}",
           C_DC, ha="center", size=7.2)

ax.plot([16.2, 16.2], [29.8, 30.4], color=C_DC, lw=1.8, zorder=5)
ax.plot([16.2, 48.2], [30.4, 30.4], color=C_DC, lw=1.8, zorder=5)
ax.plot([48.2, 48.2], [30.4, 32.6], color=C_DC, lw=1.8, zorder=5)
arrow(ax, (48.2, 32.2), (48.2, 32.6), C_DC, lw=1.8)
slabel(ax, 30.0, 31.15, "BATT DC  160-700 V", C_DC, size=8.2)

# GEN port — from graph S47 when present
e47 = bridge.get("S47_GEN")
gen_rate = format_rate(e47) if e47 else "kW TBD"
gen_sub = f"H2 AC\n{gen_rate}\nS45 fuel\nS47→GEN"
gen = box(ax, 51.5, 34.0, 10.0, 10.2, C_AC_F, C_AC, "BACKUP_GEN",
          gen_sub, ts=10.4, ss=7.4)
arrow(ax, L(gen), (50.4, cy(gen)), C_AC, lw=1.8)
slabel(ax, 51.7, 45.0, "GEN port", C_AC, ha="left", size=7.8)
ax.text(51.5, 32.6, "AQS-PWR-001 · diesel contingency only",
        ha="left", va="top", fontsize=7.2, color=P.MUTED)

# PEM fuel cell — graph S51
e51 = bridge.get("S51_FC")
fc_rate = format_rate(e51) if e51 else "kW TBD"
fc = box(ax, 51.5, 20.8, 16.5, 10.0, C_DC_F, C_DC, "FUEL_CELL",
         f"PEM H2+O2\n{fc_rate}\nS49/S50 fuel\nS51→BATT DC",
         ts=10.4, ss=7.4)
ax.plot([59.75, 59.75], [30.8, 30.4], color=C_DC, lw=1.6, zorder=5)
arrow(ax, (59.75, 30.8), (59.75, 30.4), C_DC, lw=1.6)
slabel(ax, 61.0, 26.0, "FC_DCDC → BATT", C_DC, ha="left", size=7.6)
ax.text(51.5, 19.4, "AQS-FC-001 · ≠ GEN · heat→Q4 (S53)",
        ha="left", va="top", fontsize=7.2, color=P.MUTED)

# ── Graph-bridged ESS peers: MEOH_FC (S79) + HYDRO_SET ────
e79 = bridge.get("S79_MEOH_FC")
e_hydro = bridge.get("HYDRO_ELEC")
e48 = bridge.get("S48_GEO_ORC")

meoh_rate = format_rate(e79) if e79 else "rate null"
meoh = box(ax, 69.5, 20.8, 16.5, 10.0, C_DC_F, C_DC, "MEOH_FC",
           f"IEM MeOH FC\n{meoh_rate}\nS76 fuel (ess)\nS79→BATT DC",
           ts=10.4, ss=7.4)
# MEOH_FC into BATT DC horizontal at y=30.4
ax.plot([77.75, 77.75], [30.8, 30.4], color=C_DC, lw=1.6, zorder=5)
arrow(ax, (77.75, 30.8), (77.75, 30.4), C_DC, lw=1.6)
slabel(ax, 79.0, 26.0, "S79 MEOH_DCDC → BATT", C_DC, ha="left", size=7.6)
ax.text(69.5, 19.4, "AQS-MeOH-001 · ESS peer · heat→Q4 (S80)",
        ha="left", va="top", fontsize=7.2, color=P.MUTED)

hydro_rate = format_rate(e_hydro) if e_hydro else "rate null"
hydro_sid = e_hydro.stream_id if e_hydro else "IA-ESS-HYDRO-ELEC"
hydro = box(ax, 88.5, 20.8, 16.5, 10.0, C_PH_F, C_PH, "HYDRO_SET",
            f"turbine-pump\n{hydro_rate}\n{hydro_sid}\n→ Sol-Ark (placeholder)",
            ts=10.4, ss=7.4)
# dashed AC couple toward Sol-Ark / plant (placeholder — no invented kW)
ax.plot([88.5, 50.4], [25.8, 38.0], color=C_PH, lw=1.2, ls="--", zorder=4)
slabel(ax, 70.0, 33.0, f"{hydro_sid} (placeholder)", C_PH, ha="center", size=7.2)
ax.text(88.5, 19.4, "PUMPED_HYDRO · see hydro_dock_pfd · kW not invented",
        ha="left", va="top", fontsize=7.2, color=P.MUTED)

# GEO_ORC stub from graph (placeholder presence)
if e48 is not None:
    orc_rate = format_rate(e48)
    orc = box(ax, 107.0, 22.0, 11.0, 8.0, C_PH_F, C_PH, "GEO_ORC",
              f"S48 stub\n{orc_rate}\nAC couple TBD",
              ts=9.8, ss=7.0)
    ax.plot([107.0, 50.4], [26.0, 40.0], color=C_PH, lw=1.0, ls=":", zorder=3)
    slabel(ax, 90.0, 36.5, "S48 placeholder", C_PH, ha="center", size=6.8)

# ── notes ────────────────────────────────────────────────
ax.text(2.0, 12.8, "INTERCONNECT + GRAPH BRIDGE", fontsize=12.4, fontweight="bold", color=P.INK)
ax.text(2.0, 11.6,
        "Sol-Ark GRID is bidirectional: import on deficit, export (backfeed) when PV + battery\n"
        "exceed plant load and the POCO agreement allows sell. Utility disco is service-rated.\n"
        "ATS S1 is a mechanical bypass so the MCC can run on raw utility with the inverter isolated\n"
        "for service. ATS S2 is Sol-Ark LOAD (islanded 480 Y / 277 V, 15 ms internal transfer).\n"
        "Do not close S1 and S2 together. Break-before-make. Neutral and ground per 480 Y scheme.\n"
        "\n"
        "S17 (graph): power bus Sol-Ark → RECTIFIER / plant loads — labeled on this sheet.\n"
        "ESS peers (graph): ZnBr2 IA-ESS-ZNBR2-CHG/DIS; MEOH_FC S79; HYDRO_SET IA-ESS-HYDRO-ELEC\n"
        "(placeholder, rate null). GEO_ORC S48 remains placeholder (kW TBD — not invented).\n"
        "One 60K covers the module (peak ~50 kW, average 12–22 kW). ZnBr2 ~600 V / CAN BMS.\n"
        "FUEL_CELL (PEM) and MEOH_FC couple via DCDC into BATT DC; FC ≠ GEN ≠ MEOH_FC.\n"
        "GEN port feeds BACKUP_GEN (plant H2). Diesel = contingency only.",
        ha="left", va="top", fontsize=9.0, color=P.MUTED, linespacing=1.22)

ax.text(2.0, 1.8, "Amber = AC 480 V 3φ.    Blue = DC.    Violet = pulsed DC or Br loop.    "
        "Green = PV / Sol-Ark.    Grey dashed = graph placeholder peer.",
        fontsize=9.0, color=P.MUTED)
ax.text(60.0, 0.45, P.NAMING_FOOT, ha="center", va="bottom", fontsize=7.4, color=P.MUTED)

plt.tight_layout(pad=0.25)
out = getattr(P, "OUT_ELEC", P.ROOT / "electrical_sld.png")
fig.savefig(out, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
print("wrote", out)
print("bridged:", ", ".join(sorted(bridge.keys())))
