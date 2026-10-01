#!/usr/bin/env python3
"""AQS-PFD-NUT-001 — Nutrient / N-P cycle process flow.

Authority: doc 05, STREAM_REGISTER S07/S12/S13, wet-line P-Al/P-Mg/P-Ca, freecad farm NUTRIENT_DOSE.
Companion to AQS-PFD-FRM-001. No Salria into grow beds.
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


DOC = "AQS-PFD-NUT-001"
FNAME = "nutrient_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("nutrient", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(18.5, 12.5)
    S.title_block(
        ax, DOC, "NUTRIENT / N-P CYCLE",
        "P-Al / P-Mg / P-Ca cakes + BMED salts + HAB S12 → NUTRIENT DOSE → GROW BED  ·  aquaponic N loop",
    )

    S.rule(ax, 2, 61.5, 96, 3.2,
           "RULE  ·  No Salria into GROW BED.  No Li / REE electrowinning for fertilizer.  Al Mg Ca are precipitated, not electrowon.")

    # Precip train from wet line
    ax.text(2, 59.0, "1   PRECIPITATION CAKES  (wet line §5 — qualitative; cite AQS-STR-001 S07)",
            fontsize=9.2, fontweight="bold", color="#1c1917")
    pal = S.unit(ax, 2, 48, 14, 7.5, "P-Al", "pH 5.0–5.5\nAl(OH)₃ cake", fill="#dbeafe", edge="#1d4ed8")
    pmg = S.unit(ax, 19, 48, 14, 7.5, "P-Mg", "pH 10.5–11\nMg(OH)₂ / struvite", fill="#dbeafe", edge="#1d4ed8")
    pca = S.unit(ax, 36, 48, 14, 7.5, "P-Ca", "pH 12–12.5\nCa(OH)₂ / CaCO₃", fill="#dbeafe", edge="#1d4ed8")
    arrow(ax, R(pal), L(pmg), S.C_UTIL, lw=1.3)
    arrow(ax, R(pmg), L(pca), S.C_UTIL, lw=1.3)

    bmed = S.unit(ax, 54, 48, 16, 7.5, "BMED SALTS", "NH₄ / Na residual\nchelating stock", fill="#dcfce7", edge="#166534")
    hab = S.iface(ax, 74, 48, 16, 7.5, "HAB WASTE", "S12 liquor\nHDR_GREY path", fill="#ffedd5", edge="#c2410c")

    # Dose hub
    ax.text(2, 45.0, "2   DOSE HUB  →  FARM LOOP",
            fontsize=9.2, fontweight="bold", color="#1c1917")
    dose = S.unit(ax, 28, 32, 22, 9.0, "NUTRIENT DOSE",
                  "struvite · NH₄ · chelates\npH trim · tote / dose line\nCAD: NUTRIENT_DOSE",
                  fill="#fef3c7", edge="#b45309", ts=11.5, ss=7.6)
    arrow(ax, B(pca), (cx(pca), 44), S.C_UTIL, lw=1.4)
    arrow(ax, (cx(pca), 44), (cx(dose), 44), S.C_UTIL, lw=1.4)
    arrow(ax, (cx(dose), 44), T(dose), S.C_UTIL, lw=1.4)
    slabel(ax, 48, 45.5, "S07", S.C_UTIL, size=7.4)
    arrow(ax, B(bmed), (cx(bmed), 42.5), S.C_LIQUOR, lw=1.3)
    arrow(ax, (cx(bmed), 42.5), (dose[0] + dose[2], cy(dose) + 2), S.C_LIQUOR, lw=1.3)
    arrow(ax, B(hab), (cx(hab), 42.5), S.C_HVAC, lw=1.3)
    arrow(ax, (cx(hab), 42.5), (dose[0] + dose[2], cy(dose)), S.C_HVAC, lw=1.3)
    slabel(ax, 80, 45.5, "S12", S.C_HVAC, size=7.2)

    # Aquaponic N loop
    fish = S.unit(ax, 2, 32, 16, 9.0, "FISH TANK", "NH₄ source\nsolids → digest", fill="#dcfce7", edge="#166534")
    bio = S.unit(ax, 2, 19, 16, 8.0, "BIOFILTER", "NH₄ → NO₃\nnitrification", fill="#dcfce7", edge="#166534")
    grow = S.unit(ax, 54, 32, 22, 9.0, "GROW BED", "uptake N-P-K\nCa Mg micros", fill="#bbf7d0", edge="#166534")
    sump = S.unit(ax, 80, 32, 16, 9.0, "FARM SUMP", "loop + S13\ncondensate out", fill="#e0f2fe", edge="#0369a1")

    arrow(ax, B(fish), T(bio), S.C_PRODUCT, lw=1.5)
    arrow(ax, R(bio), (bio[0] + bio[2] + 8, cy(bio)), S.C_PRODUCT, lw=1.4)
    arrow(ax, (bio[0] + bio[2] + 8, cy(bio)), (cx(grow), cy(bio)), S.C_PRODUCT, lw=1.4)
    arrow(ax, (cx(grow), cy(bio)), B(grow), S.C_PRODUCT, lw=1.4)
    arrow(ax, R(dose), L(grow), S.C_PRODUCT, lw=1.7)
    slabel(ax, 51, 37.5, "dose", S.C_PRODUCT, size=7.2)
    arrow(ax, R(grow), L(sump), S.C_UTIL, lw=1.4)
    arrow(ax, B(sump), (cx(sump), 27), S.C_UTIL, lw=1.2)
    arrow(ax, (cx(sump), 27), (cx(fish), 27), S.C_UTIL, lw=1.2)
    arrow(ax, (cx(fish), 27), B(fish), S.C_UTIL, lw=1.2)
    slabel(ax, 42, 25.5, "sump recycle", S.C_UTIL, size=6.8)

    # Condensate / salt
    salt = S.iface(ax, 54, 19, 22, 8.0, "SALT FEED / UPW POLISH",
                   "S13 condensate return\nexcess salts → brine", fill="#e0f2fe", edge="#0369a1")
    arrow(ax, B(sump), (cx(sump), 27), S.C_UTIL, lw=1.0)
    arrow(ax, (cx(sump), cy(salt)), L(salt), S.C_UTIL, lw=1.2, ls="--")
    slabel(ax, 78, 24.5, "S13", S.C_UTIL, size=7.0)

    S.callout(ax, 2, 8.0, 50, 8.0, "MACHINE / PROCESS LIST", [
        "Dose: NUTRIENT_DOSE (freecad/farm.py)",
        "Precip: P-Al · P-Mg · P-Ca (wet_line_factory_pfd)",
        "Loop: FISH_TANK · BIOFILTER · GROW_BED · FARM_SUMP",
        "Detail: cad/process/NUTRIENT_DOSE.md (Rev B)",
        "Companion: AQS-PFD-FRM-001 · terrace fertigation: AQS-PFD-TRR-001",
    ], fill="#f0fdf4", edge="#166534")

    S.callout(ax, 54, 8.0, 42, 8.0, "QUALITATIVE ONLY", [
        "No invented kg/d balances on this sheet.",
        "Cite MASS_FLOW / STREAM_REGISTER statuses.",
        "S07/S12/S13 Closed · S42 Claimed if GH fertigation.",
        "Open terrace uses S40 (clean) — not S07. See AQS-PFD-TRR-001.",
    ], fill="#f8fafc", edge="#64748b")

    S.legend(ax, 2.0, 1.0)
    S.graph_bridge_note(ax, _GP, "S07/S12/S30")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — nutrient", x=2.0, y=5.2)
    S.footer(ax, DOC, FNAME, "doc 05 / AQS-STR-001 / AQS-MF-001")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
