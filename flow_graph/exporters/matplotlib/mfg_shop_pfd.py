#!/usr/bin/env python3
"""AQS-PFD-MFG-001 — MFG SHOP sector process flow.

Authority: MANUFACTURING overview, Precious Plastic kit (link-only), freecad/mfg_shop.py,
STREAM_REGISTER S08/S16. Massing-level named machines — not shop drawings.
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


DOC = "AQS-PFD-MFG-001"
FNAME = "mfg_shop_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("mfg_shop", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(18.5, 12.5)
    S.title_block(
        ax, DOC, "MFG SHOP",
        "Precious Plastic–class polymer + metals crib/CNC  ·  forming → AQS-PFD-MFG-MET-001  ·  S08/S16  ·  L0",
    )

    S.callout(ax, 2, 61.5, 96, 3.6, "INTERFACES", [
        "IN:  S08 METALS / ELEMENTS + SILICATE from core crib  ·  polymer feedstock (float densified / sorted plastic)",
        "OUT: S16 scrap → HOPPER (no FR-4 to pyro)  ·  parts to FAB / FARM / HAB  ·  S20 electrical load",
        "Reference: Precious Plastic V4 kit (link-only — see DEPENDENCIES.md). Not bundled.",
    ], fill="#fffbeb", edge="#a16207")

    # Feeds
    metals = S.iface(ax, 2, 49, 16, 7.5, "METALS / ELEMENTS", "S08 crib\nSi Al Cu Fe …", fill="#dcfce7", edge="#166534")
    sil = S.iface(ax, 2, 38, 16, 7.5, "SILICATE", "media / slurry\nglass branch", fill="#dbeafe", edge="#1d4ed8")
    poly = S.iface(ax, 2, 27, 16, 7.5, "POLYMER FEED", "sorted plastic\nfloat densified", fill="#ffedd5", edge="#9a3412")

    # Precious Plastic class line
    ax.text(22, 58.5, "POLYMER LINE  (Precious Plastic–class envelope)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    shred = S.unit(ax, 22, 49, 13, 7.5, "SHREDDER", "PP kit shredder\nflake", fill="#e4e4e7", edge="#3f3f46")
    wash = S.unit(ax, 38, 49, 12, 7.5, "WASH / DRY", "rinse · spin\ngrey → HDR_GREY", fill="#e0f2fe", edge="#0369a1")
    extr = S.unit(ax, 53, 49, 13, 7.5, "EXTRUSION", "beam / sheet\nfilament option", fill="#ffedd5", edge="#c2410c")
    inj = S.unit(ax, 69, 49, 13, 7.5, "INJECTION", "clamp press\nparts", fill="#ffedd5", edge="#c2410c")
    sheet = S.unit(ax, 85, 49, 12, 7.5, "SHEETPRESS", "compression\npanels", fill="#ffedd5", edge="#c2410c")

    arrow(ax, R(poly), (poly[0] + poly[2] + 1.5, cy(poly)), S.C_ORG, lw=1.3)
    arrow(ax, (poly[0] + poly[2] + 1.5, cy(poly)), (cx(shred), cy(poly)), S.C_ORG, lw=1.3)
    arrow(ax, (cx(shred), cy(poly)), B(shred), S.C_ORG, lw=1.3)
    arrow(ax, R(shred), L(wash), S.C_SCRAP, lw=1.5)
    arrow(ax, R(wash), L(extr), S.C_ORG, lw=1.5)
    arrow(ax, R(extr), L(inj), S.C_ORG, lw=1.4)
    arrow(ax, R(inj), L(sheet), S.C_ORG, lw=1.4)

    # Metals / CNC floor
    ax.text(22, 45.5, "METALS + PRECISION  (forming detail: AQS-PFD-MFG-MET-001)",
            fontsize=14.3, fontweight="bold", color="#1c1917")
    crib = S.unit(ax, 22, 34, 14, 8.0, "MFG CRIB", "S08 stock\nfasteners / bar", fill="#dcfce7", edge="#166534")
    cnc = S.unit(ax, 40, 34, 14, 8.0, "CNC / MILL", "lab 5-axis class\nRepRap FDM/SLA", fill="#e4e4e7", edge="#3f3f46")
    weld = S.unit(ax, 58, 34, 14, 8.0, "WELD / ASSY", "fixture · join\npump housings", fill="#e4e4e7", edge="#3f3f46")
    floor = S.unit(ax, 76, 34, 20, 8.0, "MFG FLOOR", "cassette bay\nfab/farm/hab parts", fill="#fef3c7", edge="#a16207")

    arrow(ax, R(metals), (metals[0] + metals[2] + 1.5, cy(metals)), S.C_LIQUOR, lw=1.4)
    arrow(ax, (metals[0] + metals[2] + 1.5, cy(metals)), (cx(crib), cy(metals)), S.C_LIQUOR, lw=1.4)
    arrow(ax, (cx(crib), cy(metals)), T(crib), S.C_LIQUOR, lw=1.4)
    slabel(ax, 14, 47.5, "S08", S.C_LIQUOR, size=7.2)
    arrow(ax, R(sil), (sil[0] + sil[2] + 1.5, cy(sil)), S.C_UTIL, lw=1.2)
    arrow(ax, (sil[0] + sil[2] + 1.5, cy(sil)), (cx(floor) - 10, cy(sil)), S.C_UTIL, lw=1.2)
    arrow(ax, R(crib), L(cnc), S.C_SCRAP, lw=1.4)
    arrow(ax, R(cnc), L(weld), S.C_SCRAP, lw=1.3)
    arrow(ax, R(weld), L(floor), S.C_PRODUCT, lw=1.4)
    arrow(ax, B(sheet), (cx(sheet), cy(floor)), S.C_PRODUCT, lw=1.2, ls="--")
    arrow(ax, (cx(sheet), cy(floor)), R(floor), S.C_PRODUCT, lw=1.2, ls="--")

    # Scrap path
    hop = S.iface(ax, 76, 22, 20, 7.0, "HOPPER", "S16 scrap return\nmetal / polymer", fill="#e4e4e7", edge="#3f3f46")
    pyro = S.iface(ax, 40, 22, 20, 7.0, "INDUCTION PYROLYZER", "OIL LINE only\nno FR-4", fill="#ffedd5", edge="#9a3412")
    arrow(ax, B(floor), T(hop), S.C_SCRAP, lw=1.5)
    slabel(ax, 86, 30.5, "S16", S.C_SCRAP, size=7.2)
    S.rule(ax, 2, 16.5, 70, 3.0,
           "RULE  ·  FR-4 scrap → HOPPER only.  Never into INDUCTION PYROLYZER.  Br₂ stays on ZnBr2 — not CRU.")

    S.callout(ax, 2, 8.0, 70, 7.0, "MACHINE / PROCESS LIST", [
        "CAD envelope: MFG_SHOP · MFG_CRIB · MFG_FLOOR (freecad/mfg_shop.py)",
        "Polymer (PP-class): SHREDDER · WASH/DRY · EXTRUSION · INJECTION · SHEETPRESS / COMPRESSION",
        "Metals: crib · CNC/MILL · WELD/ASSY  ·  forming detail: AQS-PFD-MFG-MET-001 (wire/cold-mill/atomizer · S57–S63)",
        "Detail: cad/process/MFG_SHOP_EQUIPMENT.md + METAL_FORMING_EQUIPMENT.md",
    ], fill="#fffbeb", edge="#a16207")

    S.legend(ax, 2.0, 1.0)
    S.graph_bridge_note(ax, _GP, "S08/S16/S58–S61")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — mfg_shop", x=2.0, y=5.2)
    S.footer(ax, DOC, FNAME, "MANUFACTURING / AQS-STR-001 / DEPENDENCIES.md")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
