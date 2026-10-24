#!/usr/bin/env python3
"""AQS-PFD-FRM-001 — FARM sector process flow.

Authority: doc 05, LIFE_FITOUT_PLAN §3, freecad/farm.py, STREAM_REGISTER S01/S03/S04/S06/S07/S11/S13–S15/S20.
Does not invent mass balances. Terrace irrigation: AQS-PFD-TRR-001 / AQS-TRR-001.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from drawlib import R, L, T, B, arrow, slabel, cx, cy
import sector_style as S

from flow_graph.pfd_bridge import (  # noqa: E402
    edge_callout,
    graph_path,
    ia_register_lines,
    load,
    sector_edge_map,
    sector_edges,
)


DOC = "AQS-PFD-FRM-001"
FNAME = "farm_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("farm", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(18.5, 12.5)
    S.title_block(
        ax, DOC, "FARM",
        "FISH TANK → BIOFILTER → GROW BED → FARM SUMP  ·  LED CANOPY  ·  NUTRIENT DOSE  ·  L1 east plate",
    )

    # Utility rail
    S.callout(ax, 2, 61.5, 96, 3.6, "INTERFACES (STREAM_REGISTER)", [
        "IN:  S01 UPW (makeup)  ·  S03 N₂  ·  S04 CO₂  ·  S06 Q4 heat  ·  S07 dose salts  ·  S20 LED DC",
        "OUT: S15 O₂ (HDR_O2)  ·  S13 condensate → polish / salt  ·  S14 food → HAB  ·  S11 plant waste → HOPPER / OIL",
        "Forbidden: HDR_ACID_GAS · HDR_H2 · HDR_OIL_VAPOR · Salria into beds  ·  No process gas header on L1 farm.",
    ], fill="#ecfdf5", edge="#166534")

    # Main aquaponic train
    fish = S.unit(ax, 3, 48, 16, 7.5, "FISH TANK", "aquaculture\nsolids → digest / dose", fill="#dcfce7", edge="#166534")
    bio = S.unit(ax, 24, 48, 16, 7.5, "BIOFILTER", "NH₄ → NO₂ → NO₃\nnitrification", fill="#dcfce7", edge="#166534")
    grow = S.unit(ax, 45, 48, 22, 7.5, "GROW BED", "hydro / media beds\nuptake + photosynth O₂", fill="#bbf7d0", edge="#166534")
    sump = S.unit(ax, 72, 48, 16, 7.5, "FARM SUMP", "loop reservoir\nS13 condensate out", fill="#e0f2fe", edge="#0369a1")

    arrow(ax, R(fish), L(bio), S.C_PRODUCT, lw=1.8)
    slabel(ax, 21.5, 56.2, "liquor", S.C_PRODUCT, size=7.2)
    arrow(ax, R(bio), L(grow), S.C_PRODUCT, lw=1.8)
    arrow(ax, R(grow), L(sump), S.C_UTIL, lw=1.6)
    slabel(ax, 69, 56.2, "return", S.C_UTIL, size=7.2)
    # sump recycle to bio
    arrow(ax, (cx(sump), sump[1]), (cx(sump), 45.5), S.C_UTIL, lw=1.3)
    arrow(ax, (cx(sump), 45.5), (cx(bio), 45.5), S.C_UTIL, lw=1.3)
    arrow(ax, (cx(bio), 45.5), B(bio), S.C_UTIL, lw=1.3)
    slabel(ax, 48, 44.3, "sump recycle", S.C_UTIL, size=7.0)

    # Dose + LED
    dose = S.unit(ax, 24, 35, 16, 6.5, "NUTRIENT DOSE", "S07 struvite / NH₄\nchelates  ·  pH trim", fill="#fef3c7", edge="#b45309")
    led = S.unit(ax, 45, 35, 22, 6.5, "LED CANOPY", "S20 DC bus\nwaste heat → Q4", fill="#fef9c3", edge="#a16207")
    arrow(ax, T(dose), B(bio), S.C_UTIL, lw=1.4)
    slabel(ax, 28, 42.8, "S07", S.C_UTIL, size=7.2)
    arrow(ax, T(led), B(grow), S.C_HVAC, lw=1.4)
    slabel(ax, 56, 42.8, "PPFD", S.C_HVAC, size=7.2)

    # External interfaces
    upw = S.iface(ax, 3, 35, 16, 6.5, "UPW / ROOF", "S01 / S21 makeup\nHDR_UPW", fill="#e0f2fe", edge="#0369a1")
    arrow(ax, R(upw), L(dose), S.C_UTIL, lw=1.3)
    slabel(ax, 20.5, 38.5, "S01", S.C_UTIL, size=7.0)

    hab = S.iface(ax, 72, 35, 16, 6.5, "HABITATION", "S14 food tote\nS15 O₂ co-feed", fill="#ffedd5", edge="#c2410c")
    arrow(ax, R(grow), (grow[0] + grow[2] + 2.5, cy(grow)), S.C_PRODUCT, lw=1.5)
    arrow(ax, (grow[0] + grow[2] + 2.5, cy(grow)), (hab[0] - 1, cy(hab)), S.C_PRODUCT, lw=1.5, ls="--")
    arrow(ax, (hab[0] - 1, cy(hab)), L(hab), S.C_PRODUCT, lw=1.5)
    slabel(ax, 69, 42.5, "S14", S.C_PRODUCT, size=7.2)

    hop = S.iface(ax, 72, 24, 16, 6.0, "HOPPER / OIL", "S11 plant / food\nwaste  ·  HDR_ORG", fill="#e4e4e7", edge="#3f3f46")
    arrow(ax, B(grow), (cx(grow), 30.5), S.C_SCRAP, lw=1.3)
    arrow(ax, (cx(grow), 30.5), (hop[0], cy(hop)), S.C_SCRAP, lw=1.3)
    arrow(ax, (hop[0], cy(hop)), L(hop), S.C_SCRAP, lw=1.3)
    slabel(ax, 62, 31.2, "S11", S.C_SCRAP, size=7.0)

    # Gas interfaces
    gas = S.callout(ax, 3, 24, 37, 6.5, "LIFE GAS (not process headers)", [
        "S04 CO₂ → grow air (CRYO + HAB AIR) — never raw AFTERBURNER flue",
        "S03 N₂ blanketing / purge as needed",
        "S15 photosynthetic O₂ → HDR_O2 (with CRYO O2)",
        "S06 Q4 water only into farm AHU — no Q1 flue",
    ], fill="#e0f2fe", edge="#1d4ed8")

    # Terrace irrigation interface (AQS-TRR-001)
    terr = S.unit(ax, 45, 24, 22, 6.5, "OVERFLOW TERRACE",
                  "S40 clean irrig · S41→CATCH\nopen or GH per AQS-TRR-001",
                  fill="#dcfce7", edge="#166534")
    arrow(ax, (cx(upw), upw[1]), (cx(upw), 30.5), S.C_UTIL, lw=1.1, ls="--")
    arrow(ax, (cx(upw), 30.5), (terr[0], cy(terr)), S.C_UTIL, lw=1.1, ls="--")
    arrow(ax, (terr[0], cy(terr)), L(terr), S.C_UTIL, lw=1.1)
    slabel(ax, 28, 31.0, "S40 surplus (not sump)", S.C_UTIL, size=6.6)
    S.rule(ax, 3, 18.5, 85, 3.2,
           "RULE  ·  No Salria / etch / process H₂ in farm headers.  Dirty liquor never drains uphill into FARM (AQS-BLD-001 §3).  No FARM_SUMP → terrace.")

    S.callout(ax, 3, 8.5, 55, 8.5, "MACHINE / PROCESS LIST (locked CAD names)", [
        "FISH_TANK · BIOFILTER · GROW_BED · FARM_SUMP · NUTRIENT_DOSE · LED_CANOPY",
        "CAD: freecad/farm.py (per life plate). Detail: docs-authority/FARM_EQUIPMENT.md (Rev B)",
        "Nutrient chemistry sheet: AQS-PFD-NUT-001  ·  Terrace: AQS-PFD-TRR-001 / AQS-TRR-001",
        "FreeCAD bed / greenhouse solids = follow-up (not this pass).",
    ], fill="#f0fdf4", edge="#166534")

    S.legend(ax, 2.0, 1.0)
    S.graph_bridge_note(ax, _GP, "S04/S06–S07/S11/S13–S15/S14X/S20")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — farm", x=2.0, y=5.2)
    S.footer(ax, DOC, FNAME)
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
