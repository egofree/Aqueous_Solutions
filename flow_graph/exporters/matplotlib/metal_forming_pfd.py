#!/usr/bin/env python3
"""AQS-PFD-MFG-MET-001 — metal forming: melt → wire-draw / cold-mill / atomizer.

Authority: AQS-MFG-MET-001, AQS-EQP-MFG-MET-001, MANUFACTURING MetalFab Mermaid,
AQS-EQP-MFG-001 (shop envelope), AQS-STR-001 S57–S63/S71–S72, AQS-VENT-001.
MET_MELT ≠ INDUCTION_PYROLYZER. Ratings TBD.
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


DOC = "AQS-PFD-MFG-MET-001"
FNAME = "metal_forming_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("metal_forming", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(18.5, 12.5)
    S.title_block(
        ax, DOC, "METAL FORMING",
        "PROD_METALS → MET_MELT → WIRE_DRAW / COLD_MILL / GAS_ATOMIZER  ·  "
        "S57–S63  ·  MET_MELT ≠ pyro  ·  L0 MFG_SHOP",
    )

    S.rule(ax, 2, 61.5, 96, 3.2,
           "RULE  ·  MET_MELT = electric induction metal melt (≠ INDUCTION_PYROLYZER).  "
           "MET_AHU → MET_SCRUB/BH (S71–S72) — no HAB return / no free dump.  Q4 via MET_HX_Q4.  kW TBD.")

    ax.text(2, 59.0, "1   FEEDSTOCK  (S08 crib → melt)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    crib = S.unit(ax, 2, 48, 16, 8.0, "PROD_METALS",
                  "S08 crib\nEW / polish metals",
                  fill="#dcfce7", edge="#166534")
    melt = S.unit(ax, 22, 47, 20, 10.0, "MET_MELT",
                  "induction electric\nbillet / charge\n≠ oil-line pyro",
                  fill="#fef3c7", edge="#b45309", ts=17.1, ss=10.8)
    n2 = S.unit(ax, 46, 49, 14, 7.0, "MET_N2_BLANKET",
                "S03 N₂ / Ar opt\natomize + hold",
                fill="#dbeafe", edge="#1e3a8a", ts=14.9, ss=10.5)
    pyro = S.iface(ax, 64, 49, 16, 7.0, "INDUCTION_PYROLYZER",
                   "OIL LINE only\n≠ this sheet",
                   fill="#ffedd5", edge="#9a3412")
    arrow(ax, R(crib), L(melt), S.C_SCRAP, lw=1.6)
    slabel(ax, 14, 57.0, "S08", S.C_SCRAP, size=7.2)
    arrow(ax, R(n2), (melt[0] + melt[2], cy(n2)), S.C_UTIL, lw=1.2, ls="--")
    arrow(ax, L(pyro), (pyro[0] - 1.5, cy(pyro)), S.C_ORG, lw=1.0, ls=":")

    ax.text(2, 44.5, "2   FORMING TRAIN  (S57 feed → products S58–S60)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    draw = S.unit(ax, 2, 30, 18, 10.5, "WIRE_DRAW",
                  "Cu/Al/Fe wire\n0.5–5 mm class\nS58 · duty TBD",
                  fill="#e0f2fe", edge="#0369a1", ts=16.7, ss=10.8)
    mill = S.unit(ax, 26, 30, 20, 10.5, "COLD_MILL",
                  "4HI reversing\nsheet / strip\nS59 · duty TBD",
                  fill="#e0f2fe", edge="#0369a1", ts=16.7, ss=10.8)
    atom = S.unit(ax, 52, 30, 20, 10.5, "GAS_ATOMIZER",
                  "N₂/Ar atomize\nmetal powder\nS60 · kg/h TBD",
                  fill="#e0f2fe", edge="#0369a1", ts=16.7, ss=10.8)
    elec = S.stub(ax, 78, 31, 20, 9.0, "ELECTRODE_FAB",
                  "stub — coating deferred")
    # S57 from melt down to train
    arrow(ax, B(melt), (cx(melt), 42), S.C_SCRAP, lw=1.5)
    arrow(ax, (cx(melt), 42), (cx(draw), 42), S.C_SCRAP, lw=1.5)
    arrow(ax, (cx(draw), 42), T(draw), S.C_SCRAP, lw=1.5)
    arrow(ax, (cx(melt), 42), (cx(mill), 42), S.C_SCRAP, lw=1.5)
    arrow(ax, (cx(mill), 42), T(mill), S.C_SCRAP, lw=1.5)
    arrow(ax, (cx(melt), 42), (cx(atom), 42), S.C_SCRAP, lw=1.5)
    arrow(ax, (cx(atom), 42), T(atom), S.C_SCRAP, lw=1.5)
    slabel(ax, 34, 43.2, "S57", S.C_SCRAP, size=7.4)
    arrow(ax, R(draw), (elec[0], cy(draw)), S.C_PRODUCT, lw=1.1, ls="--")
    arrow(ax, R(mill), (elec[0], cy(mill) - 1), S.C_PRODUCT, lw=1.1, ls="--")

    ax.text(2, 27.5, "3   PRODUCTS  ·  SCRAP  ·  HVAC / Q4",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    wbin = S.unit(ax, 2, 14, 14, 9.0, "MET_WIRE_BIN",
                  "wire hold\nS58",
                  fill="#dcfce7", edge="#166534", ts=15.2, ss=10.5)
    sbin = S.unit(ax, 18, 14, 14, 9.0, "MET_SHEET_BIN",
                  "sheet hold\nS59",
                  fill="#dcfce7", edge="#166534", ts=15.2, ss=10.5)
    pbin = S.unit(ax, 34, 14, 16, 9.0, "MET_POWDER_CRIB",
                  "powder + N₂\nS60 → FAB/RepRap",
                  fill="#dcfce7", edge="#166534", ts=14.9, ss=10.5)
    hop = S.iface(ax, 54, 14, 16, 9.0, "HOPPER",
                  "S61 scrap\nS16 class · no FR-4",
                  fill="#e4e4e7", edge="#3f3f46")
    ahu = S.unit(ax, 74, 18.5, 12, 7.0, "MET_AHU",
                 "aisle exhaust\nS62 → scrub",
                 fill="#ffedd5", edge="#c2410c", ts=14.9, ss=10.5)
    hx = S.unit(ax, 74, 10.5, 12, 7.0, "MET_HX_Q4",
                "warm residual\nS63 → Q4",
                fill="#ffedd5", edge="#c2410c", ts=14.9, ss=10.5)
    scrub = S.unit(ax, 88, 18.5, 12, 7.0, "MET_SCRUB",
                   "fume/mist\nS71 · study Q",
                   fill="#ffedd5", edge="#c2410c", ts=14.6, ss=10.2)
    ret = S.iface(ax, 88, 10.5, 12, 7.0, "S72 returns",
                  "fines→CSTR\norg→OIL",
                  fill="#e4e4e7", edge="#3f3f46")
    arrow(ax, B(draw), T(wbin), S.C_PRODUCT, lw=1.5)
    arrow(ax, B(mill), T(sbin), S.C_PRODUCT, lw=1.5)
    arrow(ax, B(atom), T(pbin), S.C_PRODUCT, lw=1.5)
    slabel(ax, 6, 26.5, "S58", S.C_PRODUCT, size=7.0)
    slabel(ax, 22, 26.5, "S59", S.C_PRODUCT, size=7.0)
    slabel(ax, 40, 26.5, "S60", S.C_PRODUCT, size=7.0)
    arrow(ax, R(wbin), L(hop), S.C_SCRAP, lw=1.2, ls="--")
    arrow(ax, R(sbin), L(hop), S.C_SCRAP, lw=1.2, ls="--")
    arrow(ax, R(pbin), L(hop), S.C_SCRAP, lw=1.2, ls="--")
    slabel(ax, 50, 12.5, "S61", S.C_SCRAP, size=7.0)
    arrow(ax, R(atom), (ahu[0], cy(atom)), S.C_HVAC, lw=1.1, ls=":")
    arrow(ax, (ahu[0], cy(atom)), L(ahu), S.C_HVAC, lw=1.1, ls=":")
    arrow(ax, R(ahu), L(scrub), S.C_HVAC, lw=1.2)
    arrow(ax, B(scrub), T(ret), S.C_SCRAP, lw=1.1, ls="--")
    slabel(ax, 66, 26.0, "S62/S71", S.C_HVAC, size=6.8)
    slabel(ax, 92, 17.2, "S72", S.C_SCRAP, size=6.6)
    arrow(ax, R(mill), (hx[0], cy(hx)), S.C_HVAC, lw=1.0, ls=":")
    slabel(ax, 66, 12.0, "S63", S.C_HVAC, size=6.8)

    S.callout(ax, 2, 2.8, 96, 6.2, "MACHINE / DOC NAMES", [
        "MET_MELT · WIRE_DRAW · COLD_MILL · GAS_ATOMIZER · MET_WIRE_BIN · MET_SHEET_BIN · "
        "MET_POWDER_CRIB · MET_N2_BLANKET · MET_AHU/SCRUB · MET_HX_Q4 · MET_SWARF · ELECTRODE_FAB",
        "AQS-MFG-MET-001 · AQS-EQP-MFG-MET-001 · AQS-EQP-MFG-001 · AQS-GAP-001 §7 item 6",
        "Placement: L0 MFG_SHOP / MFG_FLOOR  ·  SCALE_M=1.0  ·  CERN-OHL-S-2.0  ·  plant.FCStd rebuild for stubs",
    ], fill="#fafaf9", edge="#57534e")

    S.graph_bridge_note(ax, _GP, "S57–S63/S71–S72")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — metal_forming", x=2.0, y=6.8)
    S.footer(ax, DOC, FNAME, "AQS-MFG-MET-001 / AQS-VENT-001 / AQS-STR-001")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
