#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""PUMPED_HYDRO + DOCK dedicated sheet — graph-bridged units/edges only.

Sole topology authority: ``flow_graph/plant_flow_graph.json``.
Units: HYDRO_SET, ROOF_TANK, CATCH_TANK, NORTH_DOCK, BOUNDARY_EXPORT.
Streams from graph: S21/S22/S23, IA-ESS-HYDRO-*, DOCK_EXPORT_TBD.
DOCK_EXPORT_TBD labeled TBD only — no fake S##. Null rates stay null.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import params as P
from drawlib import box, cx, cy, R, L, T, B, arrow, slabel

from flow_graph.pfd_bridge import (  # noqa: E402
    claim_label,
    edge_callout,
    format_rate,
    graph_path,
    hydro_dock_bridge_edges,
    load,
    node_by_id,
)

OUT = Path(__file__).resolve().parent.parent / "hydro_dock_pfd.png"

C_W = "#1d4ed8"
C_W_F = "#dbeafe"
C_PH = "#78716c"
C_PH_F = "#f5f5f4"
C_DK = "#334155"
C_DK_F = "#e2e8f0"
C_TB = "#546e7a"
C_TB_F = "#eceff1"


def _node_sub(uid: str, g, fallback: str) -> str:
    n = node_by_id(uid, g)
    if n is None:
        return fallback + "\n(missing from graph)"
    gap = n.diagram_gap or ""
    pres = n.presence.value if hasattr(n.presence, "value") else str(n.presence)
    lines = [f"sector {n.sector_id}", f"presence {pres}"]
    if gap:
        lines.append(gap[:48])
    return "\n".join(lines)


def main() -> None:
    g = load()
    br = hydro_dock_bridge_edges(g)
    gp = graph_path().name

    fig, ax = plt.subplots(figsize=(18.0, 14.0), dpi=140)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 78)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(P.BG)
    ax.set_facecolor(P.BG)

    ax.text(50, 76.5, "PUMPED HYDRO  +  NORTH DOCK",
            ha="center", va="top", fontsize=17.0, fontweight="bold", color=P.INK)
    ax.text(50, 74.2,
            "Dedicated coverage from plant_flow_graph.json  ·  "
            "inventory cycle peers S22/S23  ·  DOCK_EXPORT_TBD (no fake S##)",
            ha="center", va="top", fontsize=9.4, color=P.MUTED)
    ax.text(50, 72.4,
            f"Graph-bridged from {gp}  ·  null rates stay null  ·  placeholders visible",
            ha="center", va="top", fontsize=8.6, color=P.MUTED)

    # ── PUMPED_HYDRO column ───────────────────────────────
    ax.add_patch(FancyBboxPatch(
        (2.0, 28.0), 54.0, 42.0,
        boxstyle="round,pad=0.14,rounding_size=0.28",
        facecolor="#eff6ff", edgecolor=C_W, linewidth=1.5, zorder=1,
    ))
    ax.text(29.0, 68.8, "PUMPED_HYDRO  /  WTR inventory",
            ha="center", va="top", fontsize=12.4, fontweight="bold", color=C_W, zorder=4)

    roof = box(ax, 16.0, 58.5, 26.0, 7.5, C_W_F, C_W, "ROOF_TANK",
               _node_sub("ROOF_TANK", g, "upper reservoir"), ts=12.2, ss=7.6)
    catch = box(ax, 16.0, 36.5, 26.0, 7.5, C_W_F, C_W, "CATCH_TANK",
                _node_sub("CATCH_TANK", g, "lower reservoir"), ts=12.2, ss=7.6)
    hydro = box(ax, 4.0, 46.5, 10.5, 9.0, C_PH_F, C_PH, "HYDRO_SET",
                _node_sub("HYDRO_SET", g, "turbine-pump"), ts=10.4, ss=6.8)

    e22 = br.get("S22_PENSTOCK")
    e23 = br.get("S23_PUMP")
    e_chg = br.get("HYDRO_CHG")
    e_dis = br.get("HYDRO_DIS")
    e_el = br.get("HYDRO_ELEC")
    e21 = br.get("S21_ROOF_HAB")

    # penstock down / pump up
    arrow(ax, B(roof), T(catch), C_W, lw=2.0)
    if e22 is not None:
        slabel(ax, 43.5, 52.0, edge_callout(e22), C_W, ha="left", size=7.6)
        slabel(ax, 43.5, 50.6, "penstock ↓", C_W, ha="left", size=7.0)
    arrow(ax, (roof[0] + 2.0, roof[1]), (catch[0] + 2.0, catch[1] + catch[3]),
          C_W, lw=1.5, ls="--")
    if e23 is not None:
        slabel(ax, 14.5, 52.0, edge_callout(e23), C_W, ha="right", size=7.6)
        slabel(ax, 14.5, 50.6, "pump ↑", C_W, ha="right", size=7.0)

    # ESS inventory aliases (peers S22/S23 — not invented rates)
    if e_dis is not None:
        slabel(ax, 29.0, 55.6, f"ESS {edge_callout(e_dis)}", C_PH, size=6.8)
    if e_chg is not None:
        slabel(ax, 29.0, 34.9, f"ESS {edge_callout(e_chg)}", C_PH, size=6.8)

    # hydro electrical to bus (placeholder)
    bus = box(ax, 40.0, 46.5, 14.0, 9.0, C_PH_F, C_PH, "SOL_ARK_60K",
              "elec peer\n(see SLD)", ts=10.2, ss=7.2)
    arrow(ax, R(hydro), L(bus), C_PH, lw=1.4, ls="--")
    if e_el is not None:
        slabel(ax, 33.5, 56.2, edge_callout(e_el), C_PH, size=6.8)
        slabel(ax, 33.5, 55.0, "placeholder · rate null", C_PH, size=6.4)

    # S21 roof → habitation (boundary of this sheet)
    hab = box(ax, 40.0, 58.5, 14.0, 7.5, "#ecfdf5", P.C_LEACH, "HABITATION",
              "clean tower\n(S21)", ts=10.2, ss=7.2)
    arrow(ax, R(roof), L(hab), C_W, lw=1.4)
    if e21 is not None:
        slabel(ax, 36.5, 67.0, edge_callout(e21), C_W, size=7.0)

    ax.text(4.0, 33.2,
            "Inventory cycle only — continuous kW not invented.\n"
            "IA-ESS-HYDRO-CHG/DIS peer S23/S22 (rate null kg/d).\n"
            "IA-ESS-HYDRO-ELEC is placeholder on SLD; no nameplate kW here.",
            ha="left", va="top", fontsize=7.6, color=P.MUTED, linespacing=1.2, zorder=4)

    # ── DOCK column ───────────────────────────────────────
    ax.add_patch(FancyBboxPatch(
        (58.5, 28.0), 39.5, 42.0,
        boxstyle="round,pad=0.14,rounding_size=0.28",
        facecolor="#f8fafc", edgecolor=C_DK, linewidth=1.5, zorder=1,
    ))
    ax.text(78.25, 68.8, "DOCK  /  NORTH_DOCK",
            ha="center", va="top", fontsize=12.4, fontweight="bold", color=C_DK, zorder=4)

    dock = box(ax, 64.0, 50.0, 28.0, 10.0, C_DK_F, C_DK, "NORTH_DOCK",
               _node_sub("NORTH_DOCK", g, "site north bay"), ts=12.4, ss=7.4)
    bnd = box(ax, 64.0, 34.0, 28.0, 9.0, C_TB_F, C_TB, "BOUNDARY_EXPORT",
              _node_sub("BOUNDARY_EXPORT", g, "campus export"), ts=11.6, ss=7.2)

    e_dock = br.get("DOCK_EXPORT")
    arrow(ax, B(dock), T(bnd), C_TB, lw=1.8, ls="--")
    if e_dock is not None:
        # Explicit TBD — never invent S##
        lab = f"{e_dock.stream_id}  ·  {claim_label(e_dock)}"
        slabel(ax, 78.0, 47.2, lab, C_TB, size=8.2)
        slabel(ax, 78.0, 45.8, format_rate(e_dock), C_TB, size=7.4)
        carries = e_dock.carries or "goods / freight"
        slabel(ax, 78.0, 44.4, carries, C_TB, size=7.0)

    ax.text(60.5, 33.0,
            "DOCK_EXPORT_TBD is namespace=TBD.\n"
            "No inter-block S## issued (audit §7.1).\n"
            "Campus/ground_floor still show footprint.",
            ha="left", va="top", fontsize=7.6, color=P.MUTED, linespacing=1.2, zorder=4)

    # ── register ──────────────────────────────────────────
    ax.text(2.0, 25.5, "GRAPH EDGES ON THIS SHEET", fontsize=11.0, fontweight="bold", color=P.INK)
    y = 23.5
    for key in ("S21_ROOF_HAB", "S22_PENSTOCK", "S23_PUMP",
                "HYDRO_CHG", "HYDRO_DIS", "HYDRO_ELEC", "DOCK_EXPORT"):
        e = br.get(key)
        if e is None:
            ax.text(2.0, y, f"{key}  ·  missing from graph", fontsize=7.4, color="#b71c1c")
        else:
            route = f"{e.from_unit_id} → {e.to_unit_id}"
            ax.text(2.0, y,
                    f"{e.stream_id}  {route}  ·  {format_rate(e)}  ·  {claim_label(e)}"
                    + (f"  ·  {e.carries}" if e.carries else ""),
                    fontsize=7.2, color=P.MUTED)
        y -= 1.35

    ax.text(2.0, 12.5, "HONEST GAPS", fontsize=11.0, fontweight="bold", color=P.INK)
    ax.text(2.0, 11.2,
            "• HYDRO elec rate null — no invented kW / nameplate.\n"
            "• DOCK export has no S## — DOCK_EXPORT_TBD only.\n"
            "• Continuous pumped-hydro duty remains a study (AQS-ESS-001); this sheet shows topology + peers only.\n"
            "• Campus water_cycle_pfd still covers roof–catch inventory narrative; this sheet is the dedicated HYDRO+DOCK bridge.",
            ha="left", va="top", fontsize=8.0, color=P.MUTED, linespacing=1.25)

    ax.text(50.0, 0.6, P.NAMING_FOOT + "    PUMPED_HYDRO    DOCK    graph-bridged",
            ha="center", va="bottom", fontsize=7.4, color=P.MUTED)

    plt.tight_layout(pad=0.25)
    fig.savefig(OUT, dpi=140, facecolor=fig.get_facecolor(), bbox_inches="tight")
    print("wrote", OUT)
    print("bridged:", ", ".join(sorted(br.keys())))


if __name__ == "__main__":
    main()
