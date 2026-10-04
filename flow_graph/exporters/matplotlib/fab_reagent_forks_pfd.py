#!/usr/bin/env python3
"""AQS-PFD-FAB-RGN-001 — Fab wet-reagent synth forks from wet line.

Authority: AQS-EQP-FAB-RGN-001, AQS-EQP-FAB-001, AQS-PFD-WET-001,
doc 03, SILICON_FAB overview, STREAM_REGISTER S09 / S31–S39.
Existing BMED/CRU sources vs NEW WS_* forks. No invented rates.
SEM-Tech / IEM = link-only (DEPENDENCIES.md).
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


DOC = "AQS-PFD-FAB-RGN-001"
FNAME = "fab_reagent_forks_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("fab_reagent", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(20.0, 15.0)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 90)
    S.title_block(
        ax, DOC, "FAB WET-REAGENT FORKS",
        "BMED / CRU existing  ·  NEW WS_* synth modules  ·  S31–S39 qualitative  ·  "
        "feeds WET_BENCH / FAB_TOOL / LAP_CMP",
        y=88.0,
    )

    S.callout(ax, 2, 81.0, 96, 4.0, "SCOPE", [
        "Map fab acids, bases, oxidizers, dopants, slurry, solvents to wet-line sources.",
        "NEW = dedicated synth fork issued this pass (AQS-EQP-FAB-RGN-001). Not FreeCAD solids yet.",
        "Returns: S10 etch + S39 spent slurry/solvent/PR → REGEN LEACH / OIL / HDR_ORG. No sewer.",
    ], fill="#fffbeb", edge="#b45309")

    # existing
    ax.text(2, 78.5, "1   EXISTING WET-LINE SOURCES  (no new fork)",
            fontsize=14.7, fontweight="bold", color="#1c1917")
    bmed = S.iface(ax, 2, 69.0, 14, 7.0, "BMED REGEN", "acid / base split", fill="#dcfce7", edge="#166534")
    hcl = S.unit(ax, 18, 69.0, 12, 7.0, "HCl PRODUCT", "S09 → bench", fill="#ffedd5", edge="#9a3412")
    naoh = S.unit(ax, 32, 69.0, 12, 7.0, "NaOH PRODUCT", "S09 → bench", fill="#ffedd5", edge="#9a3412")
    cru = S.iface(ax, 46, 69.0, 14, 7.0, "CRU", "chlorate / Cl₂\npath · Salria", fill="#ffedd5", edge="#9a3412")
    metals = S.iface(ax, 62, 69.0, 14, 7.0, "PROD_METALS", "S08 crib Si/metals", fill="#dcfce7", edge="#166534")
    upw = S.iface(ax, 78, 69.0, 20, 7.0, "FAB UPW / S27", "FAB-UPW-001\n> 18 MΩ·cm", fill="#e0f2fe", edge="#0369a1")

    arrow(ax, R(bmed), L(hcl), S.C_LIQUOR, lw=1.3)
    arrow(ax, R(hcl), L(naoh), S.C_LIQUOR, lw=1.2)
    arrow(ax, R(bmed), (bmed[0] + bmed[2] / 2, 68), S.C_OX, lw=1.0, ls="--")
    # cru link visual
    arrow(ax, (cx(bmed), 68), (cx(cru), 68), S.C_OX, lw=1.0, ls="--")
    arrow(ax, (cx(cru), 68), T(cru), S.C_OX, lw=1.0, ls="--")

    # NEW forks
    ax.text(2, 66.5, "2   NEW SYNTH FORKS  (issued module IDs — AQS-EQP-FAB-RGN-001)",
            fontsize=14.7, fontweight="bold", color="#1c1917")

    forks = [
        (2, "WS_HF_ED", "HF (aq)\nfluoride ED", "S31", "#fecaca", "#b91c1c"),
        (15.5, "WS_PEROX", "H₂O₂\nRCA SC-1/2", "S32", "#fef3c7", "#b45309"),
        (29, "WS_AMMONIA", "NH₄OH\nRCA SC-1", "S33", "#fef3c7", "#b45309"),
        (42.5, "WS_NITRIC", "HNO₃\netch", "S34", "#fef3c7", "#b45309"),
        (56, "WS_PHOS", "H₃PO₄\netch", "S34", "#fef3c7", "#b45309"),
        (69.5, "WS_KOH", "KOH\nclean/texture", "S35", "#fef3c7", "#b45309"),
    ]
    boxes = []
    for x, title, sub, sid, fill, edge in forks:
        b = S.unit(ax, x, 56.5, 12.5, 7.5, title, sub, fill=fill, edge=edge, ts=14.3, ss=10.2)
        boxes.append((b, sid))
        ax.text(x + 6.25, 55.6, "NEW", ha="center", va="top", fontsize=9.6,
                fontweight="bold", color="#b91c1c")

    ax.text(2, 53.5, "3   DOPANT / SLURRY / SOLVENT FORKS",
            fontsize=14.7, fontweight="bold", color="#1c1917")
    dope = S.unit(ax, 2, 43.5, 18, 7.5, "WS_DOPE", "B/P/As concentrate\n+ BBr₃/POCl₃ cabinets", fill="#fecaca", edge="#b91c1c", ts=15.5)
    slurry = S.unit(ax, 23, 43.5, 18, 7.5, "WS_SLURRY", "colloidal silica\nglass silicate + UPW", fill="#fef3c7", edge="#b45309", ts=15.5)
    solv = S.unit(ax, 44, 43.5, 18, 7.5, "WS_SOLV", "IPA / acetone / NMP\noil-line recover", fill="#fef3c7", edge="#b45309", ts=15.5)
    glass = S.iface(ax, 66, 43.5, 14, 7.5, "GLASS LINE", "silicate make-up", fill="#dbeafe", edge="#1d4ed8")
    oil = S.iface(ax, 82, 43.5, 16, 7.5, "OIL LINE", "organics recover\nstub", fill="#ffedd5", edge="#9a3412")
    ax.text(11, 42.6, "NEW", ha="center", fontsize=9.6, fontweight="bold", color="#b91c1c")
    ax.text(32, 42.6, "NEW", ha="center", fontsize=9.6, fontweight="bold", color="#b91c1c")
    ax.text(53, 42.6, "NEW", ha="center", fontsize=9.6, fontweight="bold", color="#b91c1c")

    arrow(ax, R(glass), L(slurry), S.C_UTIL, lw=1.15, ls="--")
    arrow(ax, L(oil), R(solv), S.C_ORG, lw=1.15, ls="--")
    arrow(ax, T(cru), (cx(cru), 52.5), S.C_OX, lw=1.0, ls="--")
    # CRU to dope
    arrow(ax, (cx(cru), 52.5), (cx(dope), 52.5), S.C_OX, lw=1.0, ls="--")
    arrow(ax, (cx(dope), 52.5), T(dope), S.C_OX, lw=1.0, ls="--")
    slabel(ax, 40, 53.0, "CRU migrate", S.C_OX, size=6.2)

    # consumers
    ax.text(2, 40.5, "4   FAB CONSUMERS  (L0)",
            fontsize=14.7, fontweight="bold", color="#1c1917")
    wet = S.unit(ax, 2, 30.0, 20, 8.0, "WET_BENCH", "RCA · HF · etch\nS09 + S31–S35 + S27", fill="#e0f2fe", edge="#0369a1")
    lap = S.unit(ax, 26, 30.0, 16, 8.0, "LAP_CMP", "S37 slurry", fill="#bae6fd", edge="#0369a1")
    tool = S.unit(ax, 46, 30.0, 18, 8.0, "FAB_TOOL", "S36 dopants · S38 solv\nox / litho / metal", fill="#e4e4e7", edge="#3f3f46")
    solar = S.iface(ax, 68, 30.0, 14, 8.0, "PV_TEXTURE", "S35 KOH\nFAB-PV-001", fill="#fef3c7", edge="#b45309")
    etch = S.iface(ax, 84, 30.0, 14, 8.0, "ETCH RETURN", "S10 + S39\n→ REGEN / OIL", fill="#dcfce7", edge="#166534")

    # arrows from forks to wet
    for b, sid in boxes:
        arrow(ax, B(b), (cx(b), 39.5), S.C_OX, lw=0.9, ls="--")
        arrow(ax, (cx(b), 39.5), (cx(wet), 39.5), S.C_OX, lw=0.85, ls="--")
    arrow(ax, (cx(wet), 39.5), T(wet), S.C_OX, lw=0.9, ls="--")
    arrow(ax, B(slurry), T(lap), S.C_UTIL, lw=1.2)
    slabel(ax, 34, 39.8, "S37", S.C_UTIL, size=6.6)
    arrow(ax, B(dope), (cx(dope), 39.5), S.C_OX, lw=1.1)
    arrow(ax, (cx(dope), 39.5), (cx(tool), 39.5), S.C_OX, lw=1.1)
    arrow(ax, (cx(tool), 39.5), T(tool), S.C_OX, lw=1.1)
    slabel(ax, 40, 40.0, "S36", S.C_OX, size=6.6)
    arrow(ax, B(solv), (cx(solv), 39.2), S.C_ORG, lw=1.05)
    arrow(ax, (cx(solv), 39.2), (tool[0] + tool[2] - 2, 39.2), S.C_ORG, lw=1.05)
    arrow(ax, (tool[0] + tool[2] - 2, 39.2), T(tool), S.C_ORG, lw=1.05)
    slabel(ax, 58, 38.5, "S38", S.C_ORG, size=6.4)
    arrow(ax, R(wet), L(etch), S.C_LIQUOR, lw=1.3, ls="--")
    arrow(ax, R(lap), (lap[0] + lap[2] + 2, cy(etch)), S.C_LIQUOR, lw=1.1, ls="--")
    arrow(ax, (lap[0] + lap[2] + 2, cy(etch)), L(etch), S.C_LIQUOR, lw=1.1, ls="--")
    slabel(ax, 78, 38.5, "S10/S39", S.C_LIQUOR, size=6.6)
    arrow(ax, R(boxes[-1][0]), (boxes[-1][0][0] + boxes[-1][0][2] + 1, cy(boxes[-1][0])), S.C_OX, lw=0.9, ls="--")
    # KOH to solar
    arrow(ax, (cx(boxes[-1][0]), 39.5), (cx(solar), 39.5), S.C_OX, lw=0.9, ls="--")
    arrow(ax, (cx(solar), 39.5), T(solar), S.C_OX, lw=0.9, ls="--")
    slabel(ax, 72, 40.0, "S35", S.C_OX, size=6.4)

    S.rule(ax, 2, 26.0, 96, 2.5,
           "RULE  ·  No S26 potable in WS_* make-up.  HF only via WS_HF_ED.  "
           "Dopant cabinets never tee hab AHU.  SEM-Tech/IEM = link-only.")

    S.callout(ax, 2, 8.0, 58, 16.0, "MODULE ID INDEX", [
        "EXISTING: HCl_PRODUCT · NaOH_PRODUCT · CRU · PROD_METALS · FAB_UPW_*",
        "NEW: WS_HF_ED · WS_PEROX · WS_AMMONIA · WS_NITRIC · WS_PHOS · WS_KOH",
        "NEW: WS_DOPE · WS_SLURRY · WS_SOLV",
        "Streams: S09 (existing) · S31–S39 (this sheet) · S10/S27/S08",
        "Authority: cad/process/FAB_WET_REAGENTS.md",
        "Interface: cad/FAB_WET_INTERFACE.md",
        "Parent fab train: AQS-PFD-FAB-001 · Wet factory: AQS-PFD-WET-001",
    ], fill="#fffbeb", edge="#b45309")

    S.callout(ax, 62, 8.0, 36, 16.0, "CLAIMED RETURNS (AQS-VENT-001)", [
        "Forward S31–S38; spent → S10/S39",
        "→ REGEN LEACH / OIL / HDR_ORG.",
        "WS_HF_ED: on-site fluoride ED regen.",
        "WS_DOPE → CRU migration; slurry → glass.",
        "Seed drums TBD (perox/NH3/NOx/KOH/solv).",
        "Mass rates TBD — not invented.",
        "Solar KOH = Partial stub (equip next).",
        "No sewer / outdoor dump as end state.",
    ], fill="#fff3e0", edge="#e65100")

    S.legend(ax, 2.0, 0.5)
    S.graph_bridge_note(ax, _GP, "S31–S37")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — fab_reagent", x=2.0, y=5.2)
    S.footer(ax, DOC, FNAME, "AQS-EQP-FAB-RGN-001 / AQS-VENT-001 / AQS-STR-001")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
