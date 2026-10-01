#!/usr/bin/env python3
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""Mass-flow claim sheet — graph-bridged for MeOH S73–S82 + DOCK_EXPORT_TBD.

Sole topology authority: ``flow_graph/plant_flow_graph.json``.
Keeps AQS-MF-001 claim blocks for S01–S72. MeOH S73–S82 and DOCK_EXPORT_TBD
are drawn from the graph (rates/claim_status only when present; no fake S##).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
import params as P

from flow_graph.pfd_bridge import (  # noqa: E402
    claim_label,
    dock_export_edge,
    format_rate,
    graph_path,
    load,
    meoh_mass_claim_edges,
)

OUT = Path(__file__).resolve().parent.parent / "mass_flow_pfd.png"

CLOSED = "#1b5e20"
CLAIMED = "#e65100"
PARTIAL = "#e65100"
OPEN = "#b71c1c"
TBD = "#546e7a"
TBD_F = "#eceff1"
INK = P.INK


def block(ax, x, y, w, h, title, sub, fill, edge):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.2",
        facecolor=fill, edgecolor=edge, linewidth=1.4, zorder=3))
    ax.text(x + w / 2, y + h * 0.62, title, ha="center", va="center",
            fontsize=8.0, fontweight="bold", color=INK, zorder=4)
    ax.text(x + w / 2, y + h * 0.28, sub, ha="center", va="center",
            fontsize=6.2, color=P.MUTED, zorder=4)


def _edge_color(label: str):
    low = (label or "").lower()
    if "closed" in low and "partial" not in low and "claimed" not in low:
        return "#e8f5e9", CLOSED
    if "tbd" in low or label == "—" or label == "placeholder":
        return TBD_F, TBD
    return "#fff3e0", PARTIAL


def main():
    g = load()
    meoh = {e.stream_id: e for e in meoh_mass_claim_edges(g)}
    dock = dock_export_edge(g)
    gp = graph_path().name

    fig, ax = plt.subplots(figsize=(18, 16), dpi=140)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 94)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(50, 92, "AQS-MF-001  Mass-flow claim status", ha="center",
            fontsize=16, fontweight="bold", color=INK)
    ax.text(50, 89.5,
            f"Closed / Partial / Claimed  ·  S01–S72 + MeOH S73–S82 (graph) + DOCK_EXPORT_TBD  ·  "
            f"no free outdoor dump  ·  {gp}",
            ha="center", fontsize=8.2, color=P.MUTED)

    for i, (c, lab) in enumerate((
        (CLOSED, "Closed"), (PARTIAL, "Partial / Claimed"),
        (OPEN, "Closure required (path named)"), (TBD, "TBD / null claim (graph)"))):
        ax.add_patch(Rectangle((3 + i * 24, 86.2), 1.2, 1.2, facecolor=c, edgecolor=INK))
        ax.text(5 + i * 24, 86.8, lab, va="center", fontsize=7.2, color=INK)

    # Row 1 — closed life / water / H2 partial
    block(ax, 3, 74, 28, 9.5, "LIFE + UPW", "S01–S04 S06 S12–S15\nClosed", "#e8f5e9", CLOSED)
    block(ax, 36, 74, 28, 9.5, "ROOF ↔ CATCH", "S21–S23 penstock\nClosed clean water", "#e3f2fd", CLOSED)
    block(ax, 69, 74, 28, 9.5, "H₂ → CRYO_H2", "S64 normal; S24 contingency\nPartial (GEN S45 + FC S49)", "#fff3e0", PARTIAL)

    # Row 2
    block(ax, 3, 62, 28, 9.5, "ETCH / GREY / ORG", "S10–S13 S16 S39\nClosed returns", "#e8f5e9", CLOSED)
    block(ax, 36, 62, 28, 9.5, "BMED / CRU / EW", "liquor cascade\nClosed + Claimed", "#fff3e0", CLAIMED)
    block(ax, 69, 62, 28, 9.5, "ACID POLISH→CRU", "S65–S66 scrub+regen\nPartial / Claimed", "#fff3e0", PARTIAL)

    # Row 3
    block(ax, 3, 50, 28, 9.5, "BAGHOUSE → CSTR", "S19 fines\nClosed", "#e8f5e9", CLOSED)
    block(ax, 36, 50, 28, 9.5, "SCRUBBER → CRU", "alkali + polish liquor\nClaimed (S66)", "#fff3e0", CLAIMED)
    block(ax, 69, 50, 28, 9.5, "AFTERBURNER→CRYO", "destroy + S67 flue-cap\nPartial / Claimed", "#fff3e0", PARTIAL)

    # Row 4
    block(ax, 3, 38, 28, 9.5, "METALS / NUTRIENT", "S07 S08 S14 S57–S61\nClosed crib / tote", "#e8f5e9", CLOSED)
    block(ax, 36, 38, 28, 9.5, "CRYO FEED / AHU", "S18/S67 + S70 AHU\nPartial (S56 residual)", "#fff3e0", PARTIAL)
    block(ax, 69, 38, 28, 9.5, "Br₂ REGEN S69", "tower + regen→pos.\nPartial / Claimed", "#fff3e0", PARTIAL)

    # Row 5 — MET, WS, ORC
    block(ax, 3, 26, 28, 9.5, "MET_SCRUB S71–S72", "AHU → scrub/BH returns\nPartial / Claimed", "#fff3e0", PARTIAL)
    block(ax, 36, 26, 28, 9.5, "WS_* FORKS", "S31–S38; spent S10/S39\nClaimed (synth/seed TBD)", "#fff3e0", CLAIMED)
    block(ax, 69, 26, 28, 9.5, "ORC ELECTRIC S48", "GEO_ORC → Sol-Ark AC\nClaimed stub · kW TBD", "#fff3e0", CLAIMED)

    # Row 6 — MeOH from graph (S73–S82)
    # Group by MASS_FLOW §6 narrative without inventing Closed for unlisted claims.
    def meoh_line(sid: str) -> str:
        e = meoh.get(sid)
        if e is None:
            return f"{sid} missing from graph"
        cl = claim_label(e)
        # MASS_FLOW §6 supplies Partial (S78) / Claimed (S82) language when
        # the MF table has no per-stream claim_status row (ends S72).
        if cl == "—" and sid == "S78":
            cl = "Partial (MF §6 biogenic)"
        if cl == "—" and sid == "S82":
            cl = "Claimed (MF §6 CO₂)"
        return f"{sid} {format_rate(e)} · {cl}"

    feed_ids = ["S73", "S74"]
    prod_ids = ["S75", "S76", "S77"]
    ret_ids = ["S78", "S79", "S80", "S81", "S82"]

    feed_sub = "CO₂/H₂ → MEOH_SYNTH\n" + "\n".join(meoh_line(s) for s in feed_ids)
    prod_sub = "synth / tank / fuel\n" + "\n".join(meoh_line(s) for s in prod_ids)
    ret_sub = "ferment / FC / returns\n" + "\n".join(meoh_line(s) for s in ret_ids)

    block(ax, 3, 12, 28, 12.0, "MeOH FEED S73–S74", feed_sub, "#fff3e0", PARTIAL)
    block(ax, 36, 12, 28, 12.0, "MeOH PROD S75–S77", prod_sub, "#fff3e0", PARTIAL)
    block(ax, 69, 12, 28, 12.0, "MeOH FC/RET S78–S82", ret_sub, "#fff3e0", PARTIAL)

    # Row 7 — DOCK_EXPORT_TBD only (no invented S##)
    if dock is not None:
        dock_sub = (
            f"{dock.stream_id}  ·  ns={dock.namespace}\n"
            f"{dock.carries or 'goods / freight'}\n"
            f"{format_rate(dock)}  ·  {claim_label(dock)}\n"
            "no invented S##"
        )
        fill, edge = _edge_color(claim_label(dock))
        block(ax, 3, 2.2, 45, 8.0, "DOCK EXPORT (TBD)", dock_sub, fill, edge)
    else:
        block(ax, 3, 2.2, 45, 8.0, "DOCK EXPORT (TBD)",
              "DOCK_EXPORT_TBD missing from graph", TBD_F, TBD)

    ax.text(72, 6.0,
            "Authority: AQS-VENT-001 + AQS-MF-001 + AQS-STR-001\n"
            "MeOH/DOCK blocks read flow_graph only\n"
            "Detail: cad/MASS_FLOW.md · Sheet: AQS-PFD-VENT-001",
            ha="left", va="center", fontsize=6.8, color=P.MUTED)

    fig.tight_layout()
    fig.savefig(OUT, bbox_inches="tight", facecolor="white")
    plt.close()
    print("wrote", OUT)
    print("meoh streams on sheet:", ", ".join(sorted(meoh.keys())))
    print("dock:", dock.stream_id if dock else None)


if __name__ == "__main__":
    main()
