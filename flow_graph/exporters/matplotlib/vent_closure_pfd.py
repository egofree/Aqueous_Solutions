#!/usr/bin/env python3
"""AQS-PFD-VENT-001 — Vent / stack closure overview (scrub+regen or CRYO).

Authority: AQS-VENT-001, AQS-EQP-VENT-001, AQS-STR-001 S64–S72, AQS-MF-001.
No free outdoor dump as design intent. Contingency vents = emergency upset only.
Duties / Nm³/h / kW = TBD — do not invent nameplates. SCALE_M = 1.0.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from matplotlib.patches import FancyBboxPatch, Rectangle
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

from drawlib import arrow, slabel, cx, cy, R, L, T, B

DOC = "AQS-PFD-VENT-001"
FNAME = "vent_closure_pfd.png"

CLOSED = "#1b5e20"
PARTIAL = "#e65100"
CLAIMED = "#e65100"
INK = P.INK


def status_chip(ax, x, y, w, h, text, color):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
        facecolor="#fff8e1" if color == PARTIAL else "#e8f5e9",
        edgecolor=color, linewidth=1.3, zorder=4))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=10.2, fontweight="bold", color=color, zorder=5)


def main():
    _G = load()
    _SEC = sector_edge_map("vent", _G)
    _GP = graph_path().name
    _REG = ia_register_lines(_SEC.values())
    fig, ax = S.new_fig(18.5, 13.5)
    S.title_block(
        ax, DOC, "VENT / STACK CLOSURE",
        "Former outdoor dumps → scrub+regen or CRYO  ·  S64–S72  ·  "
        "contingency vents = upset only  ·  AQS-VENT-001",
    )

    S.rule(ax, 2, 64.5, 96, 3.0,
           "LOCK  ·  No outdoor free dump as design intent.  "
           "Toxic/acid/Cl₂/Br₂ → dedicated scrub+regen.  Condensable (H₂/CO₂/boil-off) → CRYO.  "
           "Upset stacks labeled contingency only.")

    # Legend
    for i, (c, lab) in enumerate((
        (CLOSED, "Closed"), (PARTIAL, "Partial (named path)"), (CLAIMED, "Claimed architecture"))):
        ax.add_patch(Rectangle((4 + i * 22, 61.6), 1.1, 1.1, facecolor=c, edgecolor=INK, zorder=4))
        ax.text(6 + i * 22, 62.15, lab, va="center", fontsize=11.2, color=INK)

    # ── Row 1: six former opens ──
    ax.text(2, 60.0, "1   FORMER OPEN PATHS  (must be Closed or Partial with named return)",
            fontsize=14, fontweight="bold", color=INK)

    # H2
    h2d = S.unit(ax, 2, 49.5, 12, 8.0, "H2_DRYER", "S05 dried\narrestor",
                 fill="#dbeafe", edge="#1e3a8a", ts=14.3, ss=9.9)
    cryo_h = S.unit(ax, 16, 49.5, 12, 8.0, "CRYO_H2", "S64 hold\n≠ HDR_H2",
                    fill="#dbeafe", edge="#1e3a8a", ts=14.3, ss=9.9)
    gen = S.iface(ax, 30, 53.5, 10, 4.5, "GEN S45", "kW TBD", fill="#fef3c7", edge="#b45309")
    fc = S.iface(ax, 30, 48.5, 10, 4.5, "FC S49", "kW TBD", fill="#dbeafe", edge="#1e3a8a")
    s24 = S.iface(ax, 42, 49.5, 10, 8.0, "S24 CONTING.", "roof relief\nONLY", fill="#fee2e2", edge="#b91c1c")
    arrow(ax, R(h2d), L(cryo_h), S.C_H2, lw=1.5)
    arrow(ax, R(cryo_h), L(gen), S.C_H2, lw=1.2)
    arrow(ax, R(cryo_h), L(fc), S.C_H2, lw=1.2)
    arrow(ax, R(cryo_h), L(s24), S.C_H2, lw=1.0, ls=":")
    slabel(ax, 14.5, 58.2, "S64", S.C_H2, size=6.8)
    status_chip(ax, 2, 46.8, 50, 2.0, "H₂  ·  Partial  ·  S64→CRYO_H2→S45/S49; S24 contingency", PARTIAL)

    # Acid polish
    alk = S.unit(ax, 54, 49.5, 14, 8.0, "ALK_SCRUBBER", "DEMISTER+\nlean NaOH",
                 fill="#dcfce7", edge="#166534", ts=14, ss=9.9)
    pol = S.unit(ax, 70, 49.5, 14, 8.0, "ACID_POLISH", "S65 polish\npack stub",
                 fill="#fff7ed", edge="#c2410c", ts=14, ss=9.9)
    cru = S.iface(ax, 86, 49.5, 12, 8.0, "CRU S66", "liquor regen\nSCRUBBER_TO_CRU",
                  fill="#ffedd5", edge="#9a3412")
    arrow(ax, R(alk), L(pol), S.C_OX, lw=1.4)
    arrow(ax, R(pol), L(cru), S.C_LIQUOR, lw=1.4)
    slabel(ax, 68, 58.2, "S65", S.C_OX, size=6.6)
    slabel(ax, 84, 58.2, "S66", S.C_LIQUOR, size=6.6)
    status_chip(ax, 54, 46.8, 44, 2.0, "Acid-gas  ·  Partial/Claimed  ·  polish→CRU; upset stack AHJ only", PARTIAL)

    # ── Row 2: flue + Br2 ──
    ax.text(2, 44.5, "2   AFTERBURNER FLUE  ·  ZnBr₂ Br₂",
            fontsize=14, fontweight="bold", color=INK)

    ab = S.unit(ax, 2, 34.0, 14, 8.0, "AFTERBURNER", "NCG destroy\nQ1 heat stays",
                fill="#fff7ed", edge="#b45309", ts=14, ss=9.9)
    flue = S.unit(ax, 18, 34.0, 14, 8.0, "FLUE_CAP", "S67 / S67B\n→ CRYO_CO2",
                  fill="#ffedd5", edge="#9a3412", ts=14, ss=9.9)
    co2 = S.iface(ax, 34, 34.0, 12, 8.0, "CRYO_CO2", "→ S04 FARM\nS68 condens.",
                  fill="#ffedd5", edge="#c2410c")
    arrow(ax, R(ab), L(flue), S.C_HVAC, lw=1.4)
    arrow(ax, R(flue), L(co2), S.C_ORG, lw=1.4)
    slabel(ax, 16.5, 42.8, "S67", S.C_ORG, size=6.6)
    status_chip(ax, 2, 31.3, 44, 2.0, "Flue  ·  Partial/Claimed  ·  destroy + capture; not free dump", PARTIAL)

    brsc = S.unit(ax, 54, 34.0, 16, 8.0, "Br₂ TOWER", "PVDF pack\noutdoor skid OK",
                  fill="#ede9fe", edge="#6d28d9", ts=14, ss=9.9)
    regen = S.unit(ax, 72, 34.0, 14, 8.0, "ZNBR2_REGEN", "ORP hold\nBr⁻ return",
                   fill="#ede9fe", edge="#6d28d9", ts=14, ss=9.9)
    pos = S.iface(ax, 88, 34.0, 10, 8.0, "POS TANK", "S69\n≠ CRU",
                  fill="#ede9fe", edge="#6d28d9")
    arrow(ax, R(brsc), L(regen), "#6d28d9", lw=1.4)
    arrow(ax, R(regen), L(pos), "#6d28d9", lw=1.4)
    slabel(ax, 86, 42.8, "S69", "#6d28d9", size=6.6)
    status_chip(ax, 54, 31.3, 44, 2.0, "Br₂  ·  Partial/Claimed  ·  regen→pos. tank; never CRU", PARTIAL)

    # ── Row 3: CRYO AHU + MET ──
    ax.text(2, 29.0, "3   CRYO_AHU  ·  MET_AHU",
            fontsize=14, fontweight="bold", color=INK)

    ahu = S.unit(ax, 2, 18.5, 14, 8.0, "CRYO_AHU", "NFPA 2/55\nroom air",
                 fill="#e0f2fe", edge="#0369a1", ts=14, ss=9.9)
    cond = S.unit(ax, 18, 18.5, 14, 8.0, "CRYO_AHU_COND", "condensable KO\nS70 → COLD_BOX",
                  fill="#e0f2fe", edge="#0369a1", ts=13.6, ss=9.6)
    s56 = S.iface(ax, 34, 18.5, 12, 8.0, "S56 residual", "non-cond.\ncontingency",
                  fill="#fee2e2", edge="#b91c1c")
    arrow(ax, R(ahu), L(cond), S.C_UTIL, lw=1.4)
    arrow(ax, R(cond), L(s56), S.C_UTIL, lw=1.0, ls=":")
    slabel(ax, 16.5, 27.3, "S70", S.C_UTIL, size=6.6)
    status_chip(ax, 2, 15.8, 44, 2.0, "CRYO_AHU  ·  Partial  ·  S70 condensables; S56 residual only", PARTIAL)

    met_a = S.unit(ax, 54, 18.5, 14, 8.0, "MET_AHU", "aisle capture\nS62 / S71",
                   fill="#ffedd5", edge="#c2410c", ts=14, ss=9.9)
    met_s = S.unit(ax, 70, 18.5, 14, 8.0, "MET_SCRUB", "+ baghouse\nfume / mist",
                   fill="#ffedd5", edge="#c2410c", ts=14, ss=9.9)
    ret = S.iface(ax, 86, 18.5, 12, 8.0, "S72 returns", "fines→CSTR\nmist→OIL/ORG",
                  fill="#dcfce7", edge="#166534")
    arrow(ax, R(met_a), L(met_s), S.C_HVAC, lw=1.4)
    arrow(ax, R(met_s), L(ret), S.C_SCRAP, lw=1.4)
    slabel(ax, 68, 27.3, "S71", S.C_HVAC, size=6.6)
    status_chip(ax, 54, 15.8, 44, 2.0, "MET_AHU  ·  Partial/Claimed  ·  scrub/BH; never HAB return", PARTIAL)

    # ── Row 4: claimed-incomplete ──
    ax.text(2, 13.5, "4   CLAIMED-INCOMPLETE  (architecture named; no invented kW/Nm³/h)",
            fontsize=14, fontweight="bold", color=INK)

    S.callout(ax, 2, 2.5, 23, 9.5, "H₂ → GEN / FC", [
        "S64 → CRYO_H2 → S45 + S49",
        "Partial — MAQ / continuous kW TBD",
        "S24 dark in normal operation",
    ], fill="#fff3e0", edge=PARTIAL)
    S.callout(ax, 27, 2.5, 23, 9.5, "CO₂ CAPTURE", [
        "S67 / S67B → CRYO_CO2 → S04",
        "Claimed — capture η / duty TBD",
        "Destruction upstream remains",
    ], fill="#fff3e0", edge=CLAIMED)
    S.callout(ax, 52, 2.5, 23, 9.5, "WS_* FORKS", [
        "S31–S38 forward; S10/S39 return",
        "Claimed — synth vs seed TBD",
        "HF ED regen on WS_HF_ED",
    ], fill="#fff3e0", edge=CLAIMED)
    S.callout(ax, 77, 2.5, 21, 9.5, "ORC ELECTRIC", [
        "GEO_ORC → S48 → Sol-Ark AC",
        "Claimed stub — rating TBD",
        "Do not invent kW on M1",
    ], fill="#fff3e0", edge=CLAIMED)

    S.graph_bridge_note(ax, _GP, "S19/S56/S62/S65–S66/S71")
    # overlay a few callouts where stream IDs already appear on-sheet
    for _i, (_sid, _e) in enumerate(sorted(_SEC.items())[:6]):
        pass  # register below; arrow callouts stay honest to drawn labels
    S.graph_register(ax, _REG, f"GRAPH {_GP} — vent", x=2.0, y=6.8)
    S.footer(ax, DOC, FNAME, "AQS-VENT-001 / AQS-EQP-VENT-001 / AQS-STR-001 / AQS-MF-001")
    S.save(fig, FNAME)


if __name__ == "__main__":
    main()
