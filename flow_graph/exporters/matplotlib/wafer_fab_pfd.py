#!/usr/bin/env python3
"""AQS-PFD-FAB-001 — WAFER FAB sector process flow.

Authority: doc 03, MANUFACTURING/SILICON_FAB, freecad/wafer_fab.py,
AQS-EQP-FAB-001 Rev B, AQS-EQP-FAB-RGN-001, AQS-WTR-001, STREAM_REGISTER.
Ordered train: CZ forge → cool/anneal → crop/grind → wire/ID saw → edge →
lap/CMP → clean → FAB_PREP / WET_BENCH / FAB_TOOL / ETCH_RETURN.
Fab UPW detail: AQS-PFD-FAB-UPW-001. Reagent forks: AQS-PFD-FAB-RGN-001.
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


DOC = "AQS-PFD-FAB-001"
FNAME = "wafer_fab_pfd.png"


def main():
    _G = load()
    _SEC = sector_edge_map("wafer_fab", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(20.0, 15.5)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 92)
    S.title_block(
        ax, DOC, "WAFER FAB",
        "CZ FORGE → COOL/ANNEAL → CROP/GRIND → WIRE SAW → EDGE → LAP/CMP → CLEAN → "
        "PREP / WET / TOOL  ·  S08 in · S10 return  ·  reagents → FAB-RGN-001",
        y=90.0,
    )

    S.callout(ax, 2, 83.0, 96, 4.2, "INTERFACES (STREAM_REGISTER / AQS-EQP-FAB-RGN-001)", [
        "IN:  S08 Si/metals crib  ·  S27 fab UPW  ·  S09 HCl/NaOH  ·  S31–S38 WS_* reagents  ·  S03 N₂  ·  S36 dopants",
        "OUT: S10 etch → REGEN LEACH  ·  S39 spent slurry/solvent/PR → leach / OIL / HDR_ORG  ·  kerf/grind dust → recycle",
        "Method: M1 crystal forge = Czochralski (doc 03 / SILICON_FAB). FBR = alternate powder path — not drawn as primary.",
    ], fill="#fffbeb", edge="#b45309")

    # --- 1 forge→cut train ---
    ax.text(2, 80.5, "1   CRYSTAL FORGE → CUT TRAIN  (AQS-EQP-FAB-001 Rev B)",
            fontsize=14.7, fontweight="bold", color="#1c1917")
    crib = S.iface(ax, 2, 71.5, 11, 6.5, "CORE CRIB", "S08 Si powder\nmetals / silicate", fill="#dcfce7", edge="#166534")
    charge = S.unit(ax, 15, 71.5, 10, 6.5, "CZ_CHARGE", "boule charge\nprep", fill="#ffedd5", edge="#c2410c")
    puller = S.unit(ax, 27, 71.5, 12, 6.5, "CZ_PULLER", "Czochralski\nmelt → ingot", fill="#fdba74", edge="#c2410c", ts=15.5)
    cool = S.unit(ax, 41, 71.5, 10, 6.5, "INGOT_COOL", "controlled\ncool-down", fill="#ffedd5", edge="#c2410c")
    anneal = S.unit(ax, 53, 71.5, 10, 6.5, "INGOT_ANNEAL", "optional\n800–1200 °C", fill="#ffedd5", edge="#c2410c")
    crop = S.unit(ax, 65, 71.5, 10, 6.5, "CROP_GRIND", "crop seed/tail\nOD grind", fill="#e0f2fe", edge="#0369a1")
    fbr = S.stub(ax, 78, 71.5, 20, 6.5, "FBR (alternate)", "fluidized-bed path\ndoc 03 — not M1 primary")

    for a, b, lab, col in [
        (crib, charge, "S08", S.C_UTIL),
        (charge, puller, "", S.C_SCRAP),
        (puller, cool, "ingot", S.C_SCRAP),
        (cool, anneal, "", S.C_SCRAP),
        (anneal, crop, "", S.C_SCRAP),
    ]:
        arrow(ax, R(a), L(b), col, lw=1.45)
        if lab:
            slabel(ax, (a[0] + a[2] + b[0]) / 2, 78.5, lab, col, size=6.6)

    ax.text(2, 69.0, "2   SAW → EDGE → LAP/CMP → CLEAN → L0 HANDOFF",
            fontsize=14.7, fontweight="bold", color="#1c1917")
    saw = S.unit(ax, 2, 59.5, 14, 7.0, "ID_WIRE_SAW", "multi-wire diamond\n(primary) / ID alt", fill="#e0f2fe", edge="#0369a1")
    edge = S.unit(ax, 18, 59.5, 12, 7.0, "EDGE_PROFILE", "edge grind\n/ profile", fill="#e0f2fe", edge="#0369a1")
    lap = S.unit(ax, 32, 59.5, 14, 7.0, "LAP_CMP", "lap → CMP\nS37 slurry", fill="#bae6fd", edge="#0369a1")
    preclean = S.unit(ax, 48, 59.5, 12, 7.0, "PRE_CLEAN", "UPW rinse\nS27", fill="#e0f2fe", edge="#0369a1")
    prep = S.unit(ax, 62, 59.5, 14, 7.0, "FAB_PREP", "slice / dope\nhandoff (CAD)", fill="#e0f2fe", edge="#0369a1", ts=17.1)
    slurry = S.iface(ax, 78, 59.5, 20, 7.0, "WS_SLURRY", "S37 colloidal silica\nAQS-PFD-FAB-RGN-001", fill="#ffedd5", edge="#9a3412")

    arrow(ax, B(crop), (cx(crop), 68.5), S.C_SCRAP, lw=1.3)
    arrow(ax, (cx(crop), 68.5), (cx(saw), 68.5), S.C_SCRAP, lw=1.3)
    arrow(ax, (cx(saw), 68.5), T(saw), S.C_SCRAP, lw=1.3)
    arrow(ax, R(saw), L(edge), S.C_SCRAP, lw=1.4)
    arrow(ax, R(edge), L(lap), S.C_SCRAP, lw=1.4)
    arrow(ax, R(lap), L(preclean), S.C_SCRAP, lw=1.4)
    arrow(ax, R(preclean), L(prep), S.C_PRODUCT, lw=1.5)
    arrow(ax, L(slurry), R(lap), S.C_OX, lw=1.2, ls="--")
    slabel(ax, 76, 67.2, "S37", S.C_OX, size=6.8)

    # --- 3 L0 tools ---
    ax.text(2, 56.5, "3   L0 TOOL TRAIN  (freecad/wafer_fab.py locked names)",
            fontsize=14.7, fontweight="bold", color="#1c1917")
    wet = S.unit(ax, 2, 45.5, 16, 8.0, "WET_BENCH", "RCA / HF etch / rinse\nS27 + S09 + S31–S35", fill="#e0f2fe", edge="#0369a1")
    tool = S.unit(ax, 22, 45.5, 16, 8.0, "FAB_TOOL", "ox · litho · dope\nmetal · RTA · probe", fill="#e4e4e7", edge="#3f3f46")
    etch_r = S.unit(ax, 42, 45.5, 14, 8.0, "ETCH_RETURN", "HDR_ETCH collect\nclosed", fill="#dcfce7", edge="#166534")
    regen = S.iface(ax, 60, 45.5, 14, 8.0, "REGEN LEACH", "S10 closed\nno sewer", fill="#dcfce7", edge="#166534")
    rgn = S.iface(ax, 78, 45.5, 20, 8.0, "WET SYNTH FORKS", "WS_* detail sheet\nAQS-PFD-FAB-RGN-001", fill="#ffedd5", edge="#9a3412")

    arrow(ax, B(prep), (cx(prep), 55), S.C_PRODUCT, lw=1.3)
    arrow(ax, (cx(prep), 55), (cx(wet), 55), S.C_PRODUCT, lw=1.3)
    arrow(ax, (cx(wet), 55), T(wet), S.C_PRODUCT, lw=1.3)
    arrow(ax, R(wet), L(tool), S.C_SCRAP, lw=1.4)
    arrow(ax, R(wet), (wet[0] + wet[2] + 1.2, cy(wet) - 2), S.C_LIQUOR, lw=1.5)
    arrow(ax, (wet[0] + wet[2] + 1.2, cy(wet) - 2), L(etch_r), S.C_LIQUOR, lw=1.5)
    arrow(ax, R(etch_r), L(regen), S.C_LIQUOR, lw=1.6)
    slabel(ax, 56, 54.0, "S10", S.C_LIQUOR, size=7.2)
    arrow(ax, L(rgn), R(wet), S.C_OX, lw=1.2, ls="--")
    slabel(ax, 74, 54.0, "S31–S38", S.C_OX, size=6.6)

    S.rule(ax, 2, 41.5, 96, 2.6,
           "RULE  ·  Etch never to floor drain.  FR-4 scrap → HOPPER, not pyro.  "
           "No S26 potable in fab UPW or WS_* make-up.  HF → WS_HF_ED only.")

    # --- 4 utilities ---
    ax.text(2, 39.0, "4   UTILITIES  (detail sheets)",
            fontsize=14.7, fontweight="bold", color="#1c1917")
    upw = S.stub(ax, 2, 30.0, 18, 6.5, "FAB UPW POLISH", "FAB-UPW-001 · S27")
    hcl = S.iface(ax, 22, 30.0, 12, 6.5, "HCl/NaOH", "S09 BMED", fill="#ffedd5", edge="#9a3412")
    n2 = S.iface(ax, 36, 30.0, 12, 6.5, "CRYO N2", "S03 purge", fill="#dbeafe", edge="#1d4ed8")
    dope = S.iface(ax, 50, 30.0, 14, 6.5, "WS_DOPE", "S36 cabinets", fill="#ffedd5", edge="#9a3412")
    solv = S.iface(ax, 66, 30.0, 14, 6.5, "WS_SOLV", "S38 flammable", fill="#ffedd5", edge="#9a3412")
    kerf = S.iface(ax, 82, 30.0, 16, 6.5, "KERF / DUST", "→ S08 / leach\n/ baghouse", fill="#e4e4e7", edge="#3f3f46")

    arrow(ax, T(upw), (cx(upw), wet[1]), S.C_UTIL, lw=1.15, ls="--")
    arrow(ax, T(hcl), B(wet), S.C_OX, lw=1.1, ls="--")
    arrow(ax, T(n2), B(tool), S.C_UTIL, lw=1.1, ls="--")
    arrow(ax, T(dope), B(tool), S.C_OX, lw=1.05, ls="--")
    arrow(ax, T(solv), B(tool), S.C_ORG, lw=1.05, ls="--")

    # --- 5 solar branch (detail sheet) ---
    ax.text(2, 27.5, "5   SOLAR-CELL BRANCH  (AQS-PFD-FAB-PV-001 / AQS-EQP-FAB-PV-001)",
            fontsize=14.7, fontweight="bold", color="#1c1917")
    sol = S.iface(ax, 2, 18.5, 22, 6.5, "SOLAR CELL BRANCH",
                  "PV_TEXTURE…PV_IV\nAQS-PFD-FAB-PV-001",
                  fill="#fef3c7", edge="#b45309")
    koh = S.iface(ax, 26, 18.5, 14, 6.5, "WS_KOH", "S35 texture", fill="#fef3c7", edge="#b45309")
    pv = S.iface(ax, 42, 18.5, 16, 6.5, "CELLS → POWER", "campus PV narrative\nPV_COUNT unchanged", fill="#fef3c7", edge="#b45309")
    arrow(ax, (cx(preclean), 18.5 + 6.5), T(sol), S.C_PRODUCT, lw=1.0, ls="--")
    arrow(ax, R(sol), L(koh), S.C_OX, lw=1.0, ls="--")
    arrow(ax, R(koh), L(pv), S.C_PRODUCT, lw=1.0, ls="--")
    ax.text(60, 21.5, "Detail sheet + FreeCAD PV_* envelopes issued Wave 4. kW TBD.",
            fontsize=11.2, color="#78716c", style="italic")

    S.callout(ax, 2, 6.5, 56, 10.5, "MACHINE / PROCESS LIST", [
        "Forge→cut: CZ_CHARGE · CZ_PULLER · INGOT_COOL · INGOT_ANNEAL ·",
        "  CROP_GRIND · ID_WIRE_SAW · EDGE_PROFILE · LAP_CMP · PRE_CLEAN",
        "CAD locked: FAB_PREP · WET_BENCH · FAB_TOOL · ETCH_RETURN",
        "UPW: FAB_UPW_* (FAB-UPW-001)   Reagents: WS_* (FAB-RGN-001)",
        "Detail: cad/process/WAFER_FAB_EQUIPMENT.md Rev B",
        "  + FAB_WET_REAGENTS.md + FAB_WET_INTERFACE.md",
    ], fill="#fffbeb", edge="#b45309")

    S.callout(ax, 60, 6.5, 38, 10.5, "NOTES", [
        "Envelope: WAFER_FAB L0 (AQS-CMP-001).",
        "CZ recommended; FBR alternate stub.",
        "Litho/implant/metal stay inside FAB_TOOL.",
        "Solar detail: AQS-PFD-FAB-PV-001.",
        "EW POLISH BANK ≠ FAB_UPW_* ≠ WS_*.",
    ], fill="#f8fafc", edge="#64748b")

    S.legend(ax, 2.0, 0.6)
    S.graph_bridge_note(ax, _GP, "S03/S36–S39")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — wafer_fab", x=2.0, y=5.2)
    S.footer(ax, DOC, FNAME, "doc 03 / AQS-EQP-FAB-001 / AQS-EQP-FAB-RGN-001 / AQS-STR-001")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
