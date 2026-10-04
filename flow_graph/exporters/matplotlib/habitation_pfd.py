#!/usr/bin/env python3
"""AQS-PFD-HAB-001 — HABITATION sector process flow.

Authority: doc 07, LIFE_FITOUT_PLAN §2/§5, freecad/habitation.py, STREAM_REGISTER,
AQS-WTR-001. Purification detail on AQS-PFD-HAB-WTR-001 (hab_water_pfd.py).
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drawlib import R, L, T, B, arrow, slabel, cx, cy
import params as P
import sector_style as S

from flow_graph.pfd_bridge import (  # noqa: E402
    edge_callout,
    graph_path,
    ia_register_lines,
    load,
    sector_edge_map,
    sector_edges,
)


DOC = "AQS-PFD-HAB-001"
FNAME = "habitation_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("habitation", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(18.5, 12.5)
    S.title_block(
        ax, DOC, "HABITATION",
        "SLEEP · GALLEY · HAB AIR · HAB WATER / WASTE  ·  L1 west plate  ·  "
        "purification detail → AQS-PFD-HAB-WTR-001",
    )

    S.callout(ax, 2, 61.5, 96, 3.6, "INTERFACES (STREAM_REGISTER)", [
        "IN:  S02 O₂ (HDR_O2)  ·  S01 UPW / S21 roof  ·  S06 Q4 heat  ·  S14 food (FARM)  ·  S26 potable (after remin)",
        "OUT: S04 CO₂ → FARM  ·  S12 grey/black + organics → treat (HAB-WTR) → HDR_GREY / SALT / HOPPER",
        "Forbidden: Q1 flue in hab air  ·  process atmosphere duct  ·  shared HVAC return with recycle aisle.",
    ], fill="#fff7ed", edge="#c2410c")

    # Life rooms row
    sleep = S.unit(ax, 3, 48, 14, 7.0, "SLEEP", "crew berths\nquiet / egress", fill="#ffedd5", edge="#c2410c")
    galley = S.unit(ax, 20, 48, 14, 7.0, "GALLEY", "food prep\nS14 in · organics out", fill="#ffedd5", edge="#c2410c")
    air = S.unit(ax, 37, 48, 16, 7.0, "HAB AIR", "AHU / ERV\nO₂ in · CO₂ out · Q4", fill="#e0f2fe", edge="#0369a1")
    wetrm = S.unit(ax, 56, 48, 14, 7.0, "WETROOM", "toilet + shower\nIBC clearances", fill="#e0f2fe", edge="#0369a1")
    farm_if = S.iface(ax, 74, 48, 16, 7.0, "FARM", "S14 food · S15 O₂\nS04 CO₂ sink", fill="#dcfce7", edge="#166534")

    arrow(ax, R(sleep), L(galley), S.C_HVAC, lw=1.4)
    arrow(ax, R(galley), L(air), S.C_HVAC, lw=1.4)
    arrow(ax, R(air), L(wetrm), S.C_UTIL, lw=1.3)
    arrow(ax, R(farm_if), (farm_if[0] - 0.5, cy(farm_if)), S.C_PRODUCT, lw=1.2)
    arrow(ax, (cx(farm_if), farm_if[1]), (cx(farm_if), 45.2), S.C_PRODUCT, lw=1.3)
    arrow(ax, (cx(farm_if), 45.2), (cx(galley), 45.2), S.C_PRODUCT, lw=1.3)
    arrow(ax, (cx(galley), 45.2), B(galley), S.C_PRODUCT, lw=1.3)
    slabel(ax, 48, 44.0, "S14 food", S.C_PRODUCT, size=7.0)

    S.rule(ax, 3, 43.0, 50, 2.6, "RULE  ·  Q4 only into HAB AIR.  No Q1 flue.  No process H₂ / acid-gas / oil vapor.")

    ax.text(3, 40.5, "WATER BLOCKS  —  detail sheet AQS-PFD-HAB-WTR-001 (hab_water_pfd.py)",
            fontsize=14, fontweight="bold", color=P.INK)

    pot = S.stub(ax, 3, 30.5, 18, 7.5, "POTABLE / REMIN", "S26 → taps · UV\nsee HAB-WTR-001")
    grey = S.stub(ax, 24, 30.5, 18, 7.5, "GREY TREAT", "SCREEN→BIO→MED→S29\nsee HAB-WTR-001")
    black = S.stub(ax, 45, 30.5, 18, 7.5, "BLACK DIGEST", "→ S30 nutrient / salt\nsee HAB-WTR-001")
    hab_w = S.unit(ax, 66, 30.5, 14, 7.5, "HAB WATER", "CAD · POU UV\nS21 / S26 in", fill="#e0f2fe", edge="#0369a1")
    hab_waste = S.unit(ax, 83, 30.5, 14, 7.5, "HAB WASTE", "CAD · S12 collect\n→ GREY / BLACK", fill="#e4e4e7", edge="#3f3f46")

    arrow(ax, R(pot), L(hab_w), S.C_UTIL, lw=1.2, ls="--")
    arrow(ax, R(grey), (grey[0] + grey[2] + 1.5, cy(grey)), S.C_HVAC, lw=1.2, ls="--")
    arrow(ax, (grey[0] + grey[2] + 1.5, cy(grey)), (hab_waste[0] - 1, cy(hab_waste)), S.C_HVAC, lw=1.2, ls="--")
    arrow(ax, R(black), (hab_waste[0] - 1, cy(hab_waste) - 1.2), S.C_ORG, lw=1.2, ls="--")
    arrow(ax, L(hab_waste), (hab_waste[0] - 1, cy(hab_waste)), S.C_SCRAP, lw=1.1)
    arrow(ax, B(wetrm), T(grey), S.C_HVAC, lw=1.2, ls="--")
    slabel(ax, 31, 39.0, "drain", S.C_HVAC, size=6.8)

    # VCD pointer
    vcd = S.iface(ax, 3, 18.5, 28, 7.0, "VCD + ED POLISH",
                  "S13/S29 → VCD → S25 → S01\nDetail: AQS-PFD-HAB-WTR-001",
                  fill="#bae6fd", edge="#0369a1")
    core = S.iface(ax, 35, 18.5, 28, 7.0, "RECYCLE CORE",
                   "S12 / S28 / S30 → SALT / NUTRIENT / HOPPER\nHDR_GREY + HDR_ORG  ·  no sewer",
                   fill="#dcfce7", edge="#166534")
    wtr = S.iface(ax, 66, 18.5, 31, 7.0, "ROOF–CATCH INVENTORY",
                  "S21–S23  ·  AQS-PFD-WTR-001\ninventory ≠ VCD regeneration",
                  fill="#dbeafe", edge="#1d4ed8")
    arrow(ax, B(hab_waste), (cx(hab_waste), 27), S.C_LIQUOR, lw=1.4)
    arrow(ax, (cx(hab_waste), 27), (cx(core), 27), S.C_LIQUOR, lw=1.4)
    arrow(ax, (cx(core), 27), T(core), S.C_LIQUOR, lw=1.4)
    slabel(ax, 78, 27.8, "S12", S.C_LIQUOR, size=7.2)
    arrow(ax, R(vcd), L(core), S.C_UTIL, lw=1.1, ls="--")

    S.callout(ax, 3, 8.5, 94, 7.5, "MACHINE / PROCESS LIST", [
        "SLEEP · GALLEY · HAB_AIR · HAB_WATER · HAB_WASTE · WETROOM_HAB_NW (fitout)",
        "Purification tags (AQS-EQP-HAB-001): GREY_* · BLACK_* · VCD_* · HAB_ED_POLISH · REMIN · POTABLE_TANK · HAB_UV · HAB_BOOST",
        "CAD: freecad/habitation.py + fitout.py. Detail PFD: hab_water_pfd.py. Authority: AQS-WTR-001.",
        "Fire: FB_HAB_FARM 2 h · HA_L1_L0 3 h · egress via STAIR_P / STAIR_S1 (no L-1 walk).",
    ], fill="#fff7ed", edge="#c2410c")

    S.legend(ax, 2.0, 1.0)
    S.graph_bridge_note(ax, _GP, "S02/S12/S14–S15/S21/S26/S78")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — habitation", x=2.0, y=5.2)
    S.footer(ax, DOC, FNAME, "AQS-LIFE-001 / AQS-WTR-001 / AQS-STR-001 / doc 07")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
