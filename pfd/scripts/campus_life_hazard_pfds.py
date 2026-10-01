#!/usr/bin/env python3
"""High-fidelity campus / hazard / life overview PFDs.

    python3 pfd_scripts/campus_life_hazard_pfds.py

Sheets:
  campus_pfd.png              AQS-PFD-CMP-001
  hazard_separation_pfd.png   AQS-PFD-HSE-001
  life_headers_pfd.png        AQS-PFD-PIP-002
  life_gas_pfd.png            AQS-PFD-GAS-001
  water_cycle_pfd.png         AQS-PFD-WTR-001

Authority: AQS-BLD-001, AQS-HSE-001, AQS-CMP-001, AQS-PIP-002, live freecad params.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.util
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
from flow_graph.pfd_bridge import graph_path, ia_register_lines, load, sector_edges  # noqa: E402
import params as P

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent if _HERE.name in ("pfd_scripts", "scripts") else _HERE
OUT_DIR = ROOT / "images" if (ROOT / "images").is_dir() else ROOT


def _load_freecad_params():
    candidates = [
        ROOT / "cad" / "freecad" / "params.py",
        ROOT.parent / "cad" / "freecad" / "params.py",
        ROOT.parent / "models" / "freecad" / "params.py",
        Path("/home/user/dev/Aqueous/Diagrams/aqueous_diagrams/cad/freecad/params.py"),
    ]
    for path in candidates:
        if path.is_file():
            spec = importlib.util.spec_from_file_location("aqs_freecad_params_cmp", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod, path
    raise FileNotFoundError("freecad/params.py not found")


FP, FP_PATH = _load_freecad_params()


def m(mm):
    return float(mm) / 1000.0


C_FIRE = "#b71c1c"
C_WATER = "#1565c0"
C_ROOF = "#bbdefb"
C_LIFE = "#c8e6c9"
C_HAB = "#a5d6a7"
C_FARM = "#81c784"
C_GRADE = "#fff9c4"
C_MFG = "#ffe082"
C_FAB = "#ffecb3"
C_PROC = "#ffccbc"
C_CRYO = "#e1f5fe"
C_CATCH = "#cfd8dc"
C_CORE_L = "#e8eaf6"
C_CORE_P = "#fce4ec"
C_TERR = "#dcedc8"
C_ESS = "#f3e5f5"


DOC = {
    "campus_pfd.png": ("AQS-PFD-CMP-001", "Campus site — footprint / yard / terraces / water path"),
    "hazard_separation_pfd.png": ("AQS-PFD-HSE-001", "Hazard separation — FB_* / HA_* assemblies"),
    "life_headers_pfd.png": ("AQS-PFD-PIP-002", "Life headers — L1 rack tiers"),
    "life_gas_pfd.png": ("AQS-PFD-GAS-001", "Life gas — O2 / N2 / CO2 vs process H2"),
    "water_cycle_pfd.png": ("AQS-PFD-WTR-001", "Roof–catch inventory + VCD regeneration pointer"),
}


def scale_note():
    return (
        f"SCALE_M={FP.SCALE_M:g}  ·  {m(FP.PLATE_L):.0f}×{m(FP.PLATE_W):.0f} m  ·  "
        f"{FP.CASSETTE_ID}  ·  LIFE={FP.LIFE_LEVELS}  ·  BASEMENT={FP.BASEMENT_LEVELS}"
    )


def footer(ax, doc_no, fname):
    ax.text(0.01, 0.012,
            f"{doc_no}  ·  AQS-BLD-001 / AQS-HSE-001  ·  CERN-OHL-S  ·  {fname}",
            transform=ax.transAxes, fontsize=6.5, color=P.MUTED)
    ax.text(0.99, 0.012, scale_note(),
            transform=ax.transAxes, fontsize=6.2, color=P.MUTED, ha="right")


def save(fname, draw_fn, size=(15, 11), dpi=140):
    doc_no, title = DOC[fname]
    fig, ax = plt.subplots(figsize=size, dpi=dpi)
    ax.axis("off")
    ax.set_aspect("equal")
    fig.patch.set_facecolor("white")
    draw_fn(ax)
    ax.set_title(f"{doc_no}  ·  {title}",
                 fontsize=12.5, fontweight="bold", color=P.INK, pad=10)
    footer(ax, doc_no, fname)
    _stamp_graph_cross(ax)
    out = OUT_DIR / fname
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close()
    print("wrote", out)
    return out


def rbox(ax, x, y, w, h, fc, ec=None, lw=1.2, z=3, alpha=1.0, ls="-"):
    ax.add_patch(Rectangle(
        (x, y), w, h, facecolor=fc, edgecolor=P.INK if ec is None else ec,
        linewidth=lw, zorder=z, alpha=alpha, linestyle=ls,
    ))


def label(ax, x, y, text, size=7, weight="bold", color=None, ha="center", va="center"):
    ax.text(x, y, text, ha=ha, va=va, fontsize=size, fontweight=weight,
            color=P.INK if color is None else color, zorder=5, linespacing=1.12)


def arrow(ax, x1, y1, x2, y2, color, lw=1.5):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw),
                zorder=4)


# ═══════════════════════════════════════════════════════════
# Campus site
# ═══════════════════════════════════════════════════════════
def campus(ax):
    pl, pw = m(FP.PLATE_L), m(FP.PLATE_W)
    tw = m(FP.TERRACE_RUN) * 0.45  # show terrace run at campus scale
    margin = tw + 6
    ax.set_xlim(-margin - 4, pl + margin + 8)
    ax.set_ylim(-margin - 6, pw + margin + 4)

    # Terraces S/E/W
    rbox(ax, -tw * 0.3, -tw, pl + tw * 0.6, tw, C_TERR, ec="#558b2f", lw=1.0, z=1)
    label(ax, pl / 2, -tw / 2, "OVERFLOW_TERRACE_S", size=6)
    rbox(ax, pl, -tw * 0.2, tw, pw + tw * 0.4, C_TERR, ec="#558b2f", lw=1.0, z=1)
    label(ax, pl + tw / 2, pw / 2, "TERRACE_E", size=6, weight="normal")
    rbox(ax, -tw, -tw * 0.2, tw, pw + tw * 0.4, C_TERR, ec="#558b2f", lw=1.0, z=1)
    label(ax, -tw / 2, pw / 2, "TERRACE_W", size=6, weight="normal")

    # Building footprint
    rbox(ax, 0, 0, pl, pw, "#eceff1", lw=2.2, z=2)
    label(ax, pl / 2, pw + 1.6,
          f"MODULE PLATE  {pl:.0f}×{pw:.0f} m  ·  {FP.MODULE_BAYS_X}×{FP.MODULE_BAYS_Y} bays",
          size=8)

    # Stacked program as plan overlays (not flat Phase F) — show dominant L0 + L1 split
    rbox(ax, m(FP.HAB_X), m(FP.HAB_Y), m(FP.HAB_L), m(FP.HAB_W),
         C_HAB, lw=1.2, z=3, alpha=0.9)
    label(ax, m(FP.HAB_X) + m(FP.HAB_L) / 2, m(FP.HAB_Y) + m(FP.HAB_W) * 0.7,
          "HAB L1\nR-2", size=7)
    rbox(ax, m(FP.FARM_X), m(FP.FARM_Y), m(FP.FARM_L), m(FP.FARM_W),
         C_FARM, lw=1.2, z=3, alpha=0.9)
    label(ax, m(FP.FARM_X) + m(FP.FARM_L) / 2, m(FP.FARM_Y) + m(FP.FARM_W) * 0.7,
          "FARM L1\nF-2", size=7)

    rbox(ax, m(FP.MFG_X), m(FP.MFG_Y), m(FP.MFG_L), m(FP.MFG_W),
         C_MFG, lw=1.2, z=4, alpha=0.85)
    label(ax, m(FP.MFG_X) + m(FP.MFG_L) / 2, m(FP.MFG_Y) + m(FP.MFG_W) / 2,
          "MFG L0", size=7)
    rbox(ax, m(FP.FAB_X), m(FP.FAB_Y), m(FP.FAB_L), m(FP.FAB_W),
         C_FAB, lw=1.2, z=4, alpha=0.85)
    label(ax, m(FP.FAB_X) + m(FP.FAB_L) / 2, m(FP.FAB_Y) + m(FP.FAB_W) / 2,
          "FAB L0", size=7)

    # North dock (AQS-SITE-001) — west-north bay + apron
    if hasattr(FP, "DOCK_X"):
        rbox(ax, m(FP.DOCK_X), m(FP.DOCK_Y), m(FP.DOCK_L), m(FP.DOCK_W),
             C_GRADE, lw=1.3, z=4, alpha=0.9)
        label(ax, m(FP.DOCK_X) + m(FP.DOCK_L) / 2,
              m(FP.DOCK_Y) + m(FP.DOCK_W) / 2,
              "DOCK L0\nN / +Y", size=6.5)
        apron = m(getattr(FP, "DOCK_APRON_N", 6000))
        rbox(ax, m(FP.DOCK_X), pw, max(m(FP.DOCK_L), 12.0), min(apron, 4.0),
             "#cfd8dc", lw=1.0, z=3)
        label(ax, m(FP.DOCK_X) + m(FP.DOCK_L) / 2, pw + min(apron, 4.0) / 2,
              "APRON_N", size=5.5, weight="normal")
        # SERVICE_ENTRY mark
        rbox(ax, m(FP.SERVICE_ENTRY_X), m(FP.SERVICE_ENTRY_Y),
             m(FP.SERVICE_ENTRY_L), m(FP.SERVICE_ENTRY_W),
             "#fff3e0", ec="#e65100", lw=1.1, z=5)
        label(ax, m(FP.SERVICE_ENTRY_X) + m(FP.SERVICE_ENTRY_L) / 2,
              m(FP.SERVICE_ENTRY_Y) + m(FP.SERVICE_ENTRY_W) / 2,
              "SVC", size=5)

    # Core
    rbox(ax, m(FP.CORE_X), m(FP.CORE_Y), m(FP.CORE_L) / 2, m(FP.CORE_W),
         C_CORE_L, ec="#283593", lw=1.4, z=5)
    rbox(ax, m(FP.CORE_X) + m(FP.CORE_L) / 2, m(FP.CORE_Y),
         m(FP.CORE_L) / 2, m(FP.CORE_W),
         C_CORE_P, ec="#880e4f", lw=1.4, z=5)
    label(ax, m(FP.CORE_X) + m(FP.CORE_L) / 2, m(FP.CORE_Y) + m(FP.CORE_W) / 2,
          "CORE", size=6)

    # Roof tank footprint dashed
    rbox(ax, m(FP.ROOF_TANK_X), m(FP.ROOF_TANK_Y),
         m(FP.ROOF_TANK_L), m(FP.ROOF_TANK_W),
         C_ROOF, ec=C_WATER, lw=1.5, z=6, alpha=0.55, ls="--")
    label(ax, m(FP.ROOF_TANK_X) + m(FP.ROOF_TANK_L) / 2,
          m(FP.ROOF_TANK_Y) + m(FP.ROOF_TANK_W) / 2,
          "ROOF TANK L2", size=6.5, color=C_WATER)

    # Catch under (dashed footprint)
    ax.add_patch(Rectangle(
        (m(FP.CATCH_TANK_X), m(FP.CATCH_TANK_Y)),
        m(FP.CATCH_TANK_L), m(FP.CATCH_TANK_W),
        fill=False, edgecolor="#455a64", lw=1.4, ls="--", zorder=6,
    ))
    label(ax, m(FP.CATCH_TANK_X) + m(FP.CATCH_TANK_L) / 2,
          m(FP.CATCH_TANK_Y) + m(FP.CATCH_TANK_W) / 2,
          "CATCH L-2 (under)", size=6, weight="normal", color="#455a64")

    # Electrical / ZnBr2 yard west of north dock
    yard_y = m(getattr(FP, "DOCK_Y", 10000))
    rbox(ax, -tw - 5.5, yard_y, 5, 8, C_ESS, ec="#6a1b9a", lw=1.4, z=3)
    label(ax, -tw - 3, yard_y + 4,
          f"ELECTRICAL YARD (NW)\nZnBr2 ×{FP.ZNBR_COUNT}\nPV ×{FP.PV_COUNT}\nrect ×{FP.RECT_COUNT}\n"
          f"GEN/FC/GEO + CLEAR/KO\nNFPA 855 / AQS-SITE-001",
          size=6)

    # Water path annotation
    cx = m(FP.CORE_X) + m(FP.CORE_L) / 4
    cy = m(FP.CORE_Y) + m(FP.CORE_W) / 2
    arrow(ax, m(FP.ROOF_TANK_X) + m(FP.ROOF_TANK_L) / 2,
          m(FP.ROOF_TANK_Y) + 1, cx, cy + 1, C_WATER, lw=1.8)
    label(ax, (m(FP.ROOF_TANK_X) + cx) / 2 + 2, cy + 3,
          "S21/S22 penstock\nclean water ↓", size=5.8, weight="normal", color=C_WATER)
    arrow(ax, cx, cy - 1,
          m(FP.CATCH_TANK_X) + 3, m(FP.CATCH_TANK_Y) + m(FP.CATCH_TANK_W) / 2,
          C_WATER, lw=1.8)
    # Overflow to terrace
    arrow(ax, m(FP.ROOF_TANK_X) + m(FP.ROOF_TANK_L) / 2,
          m(FP.ROOF_TANK_Y),
          pl / 2, -tw / 2, "#558b2f", lw=1.3)
    label(ax, pl * 0.7, -tw * 0.15,
          "S40 irrig → bands\nS41 drain → CATCH\n(AQS-TRR-001)",
          size=5.5, weight="normal", color="#33691e")

    # CRYO callout (basement — not grade)
    label(ax, m(FP.CRYO_X) + m(FP.CRYO_L) / 2, m(FP.CRYO_Y) - 1.5,
          "CRYO on L-1 (below) east of CORE", size=5.8, weight="normal", color="#0277bd")

    # N arrow
    ax.annotate("", xy=(pl + tw + 3, pw - 1), xytext=(pl + tw + 3, pw - 4),
                arrowprops=dict(arrowstyle="-|>", color=P.INK, lw=1.2))
    label(ax, pl + tw + 3, pw - 0.4, "N", size=8)

    label(ax, pl / 2, -tw - 3.5,
          "Not a flat Phase-F campus: vertical stack per AQS-BLD-001 Rev D.  "
          "Site north = +Y.  North dock + SERVICE_ENTRY / STAIR_SERVICE (AQS-SITE-001).",
          size=6.2, weight="normal", color=P.MUTED)


# ═══════════════════════════════════════════════════════════
# Hazard separation overlay (spatial + ratings)
# ═══════════════════════════════════════════════════════════
def hazard(ax):
    """Section-style overlay of FB_* / HA_* with ratings called out."""
    ax.set_xlim(0, 42)
    ax.set_ylim(-2, 30)

    # Mini section of the stack
    x0, w = 3, 18
    levels = [
        (22, 4.5, "L2 ROOF TANK", C_ROOF),
        (17, 5, "L1 HAB | FARM", C_LIFE),
        (11, 6, "L0 DOCK / MFG / FAB", C_GRADE),
        (5, 6, "L-1 PROCESS | CRYO", C_PROC),
        (0.5, 4.5, "L-2 CATCH | HYDRO", C_CATCH),
    ]
    for y, h, lab, fc in levels:
        rbox(ax, x0, y, w, h, fc, lw=1.3, z=2)
        label(ax, x0 + w / 2, y + h / 2, lab, size=7)

    # HAB|FARM split on L1 (2 h outside CORE); CORE band = FB_HAB_CORE 3 h
    ax.plot([x0 + w / 2, x0 + w / 2], [17.2, 18.4], color=C_FIRE, lw=2, ls="--", zorder=6)
    ax.plot([x0 + w / 2, x0 + w / 2], [20.5, 21.7], color=C_FIRE, lw=2, ls="--", zorder=6)
    label(ax, x0 + w / 2 + 0.15, 17.6, "FB_HAB_FARM\n2 h", size=5.0, color=C_FIRE, ha="left")
    # CORE band on L1 highlighted as 3 h HAB↔recycle
    ax.plot([x0 + 7, x0 + 11], [18.8, 18.8], color=C_FIRE, lw=2.4, ls="-", zorder=7)
    label(ax, x0 + 11.2, 19.0, "FB_HAB_CORE 3 h", size=5.0, color=C_FIRE, ha="left")

    # CRYO split on L-1
    ax.plot([x0 + w * 0.72, x0 + w * 0.72], [5.3, 10.7], color=C_FIRE, lw=2, ls="--", zorder=6)
    label(ax, x0 + w * 0.72 + 0.15, 8, "FB_CRYO_PROCESS\n2 h", size=5.5, color=C_FIRE, ha="left")

    # Core band
    rbox(ax, x0 + 7, 0.5, 4, 26, C_CORE_L, ec="#283593", lw=1.2, z=3, alpha=0.55)
    label(ax, x0 + 9, 26.8, "CORE", size=6, color="#283593")

    # Horizontal assemblies
    ha = [
        (22, "HA_L2_L1  1 h"),
        (17, "HA_L1_L0  3 h"),
        (11, "HA_L0_Lm1  3 h"),
        (5, "HA_Lm1_Lm2  2 h"),
    ]
    for y, txt in ha:
        ax.plot([x0, x0 + w], [y, y], color=C_FIRE, lw=2.0, ls="--", zorder=5)
        label(ax, x0 + w + 0.4, y, txt, size=6.5, color=C_FIRE, ha="left")

    # Rating table (right)
    label(ax, 32, 28.5, "Locked barrier objects (AQS-HSE-001)", size=8, ha="center")
    rows = [
        ("FB_HAB_CORE", "3 h", "HAB ↔ recycle / oil"),
        ("FB_HAB_FARM", "2 h", "HAB ↔ FARM"),
        ("FB_FAB_CORE", "2 h", "WAFER_FAB ↔ recycle"),
        ("FB_CRYO", "2 h", "CRYO ↔ occupied"),
        ("FB_CRYO_PROCESS", "2 h", "L-1 aisle ↔ CRYO"),
        ("FB_ESS", "2 h / open", "ZnBr2 ↔ occupied"),
        ("HA_L1_L0", "3 h", "LIFE ↔ GRADE"),
        ("HA_L0_Lm1", "3 h", "GRADE ↔ BASEMENT"),
        ("HA_Lm1_Lm2", "2 h", "BASEMENT ↔ CATCH"),
        ("SHAFT_H2/ACID/OIL", "2 h", "dedicated; no hab"),
        ("CORE_LIFE", "2 h room", "stair / elev / util / pen"),
        ("CORE_PROCESS", "2 h room", "H2 / acid / oil / dust"),
    ]
    y = 26.5
    for name, rating, btwn in rows:
        rbox(ax, 24.5, y - 0.85, 16, 1.7, "#ffebee", ec=C_FIRE, lw=0.9, z=2)
        label(ax, 25, y, name, size=6, ha="left", color=C_FIRE)
        label(ax, 33.2, y, rating, size=6, ha="center")
        label(ax, 40, y, btwn, size=5.5, weight="normal", ha="right")
        y -= 2.0

    label(ax, 12, -1.2,
          "Plant standard ≥ IBC Table 508.4 (R over H-3): 3 h HAB↔basement, NFPA 13 throughout.",
          size=6.2, weight="normal", color=P.MUTED)


# ═══════════════════════════════════════════════════════════
# Life headers
# ═══════════════════════════════════════════════════════════
def life_hdr(ax):
    ax.set_xlim(0, 36)
    ax.set_ylim(0, 22)
    label(ax, 18, 20.5, "Life-header rack tiers (mm above life FFL) — AQS-PIP-002",
          size=9, weight="normal")

    tiers = [
        (18, "HDR_CO2", 3200, 40, "316", "raw AFTERBURNER flue", "#8d6e63"),
        (15, "HDR_N2", 3000, 25, "316", "process headers", "#78909c"),
        (12, "HDR_O2", 2800, 25, "316", "HDR_H2, acid gas", "#66bb6a"),
        (8, "HDR_ETCH", 1300, 32, "PVDF", "sewer, HDR_GREY, farm beds", "#ab47bc"),
        (5, "HDR_UPW", 1100, 40, "PP-R / PVDF", "leach, grey, etch", "#42a5f5"),
        (2, "HDR_GREY", 900, 50, "PP", "Salria, etch", "#90a4ae"),
    ]
    # Elevation scale
    rbox(ax, 2, 1.5, 1.2, 17, "#eceff1", lw=1.0, z=1)
    for y, name, z_mm, od, mat, forbid, fc in tiers:
        rbox(ax, 4, y, 14, 2.4, fc, lw=1.2, z=3, alpha=0.45)
        label(ax, 11, y + 1.5, name, size=8, ha="center")
        label(ax, 11, y + 0.55,
              f"Z = +{z_mm} mm  ·  OD {od} mm  ·  {mat}",
              size=6, weight="normal")
        label(ax, 20, y + 1.2, f"Forbidden tee: {forbid}",
              size=5.8, weight="normal", ha="left", color=C_FIRE)
        ax.plot([2.6], [1.5 + (z_mm / 3200) * 17], "o", color=P.INK, ms=4, zorder=5)

    label(ax, 11, 0.6,
          "HDR_ORG is tote / conveyor — not on this pipe rack.  "
          "Process gas racks stay on the wet aisle (separate elevations).",
          size=6, weight="normal", color=P.MUTED)


# ═══════════════════════════════════════════════════════════
# Life gas
# ═══════════════════════════════════════════════════════════
def life_gas(ax):
    ax.set_xlim(0, 40)
    ax.set_ylim(0, 22)

    rbox(ax, 2, 14, 10, 5.5, C_CRYO, ec="#0277bd", lw=1.4)
    label(ax, 7, 17.5, "CRYO (L-1)", size=8)
    label(ax, 7, 15.8, "CRYO_O2 · CRYO_N2\nCRYO_CO2 · CRYO_H2", size=6, weight="normal")

    rbox(ax, 16, 15, 8, 4, "#e8f5e9", lw=1.2)
    label(ax, 20, 17, "HDR_O2", size=8, color="#2e7d32")
    label(ax, 20, 15.8, "→ HAB AIR", size=6, weight="normal")

    rbox(ax, 26, 15, 8, 4, "#eceff1", lw=1.2)
    label(ax, 30, 17, "HDR_N2", size=8)
    label(ax, 30, 15.8, "→ FAB / FARM", size=6, weight="normal")

    rbox(ax, 16, 9, 8, 4, "#efebe9", lw=1.2)
    label(ax, 20, 11, "HDR_CO2", size=8, color="#5d4037")
    label(ax, 20, 9.8, "→ FARM", size=6, weight="normal")

    rbox(ax, 26, 9, 8, 4, C_HAB, lw=1.2)
    label(ax, 30, 11, "HAB AIR", size=8)
    label(ax, 30, 9.8, "dedicated AHU\nQ4 water only", size=6, weight="normal")

    rbox(ax, 2, 7, 10, 5, C_FARM, lw=1.2)
    label(ax, 7, 10, "GROW O2 (S15)", size=7.5)
    label(ax, 7, 8.5, "farm canopy → HDR_O2", size=6, weight="normal")

    # H2 forbidden path
    rbox(ax, 2, 1, 16, 4.5, "#ffcdd2", ec=C_FIRE, lw=1.8)
    label(ax, 10, 3.8, "PROCESS H₂ PATH — NOT life gas", size=8, color=C_FIRE)
    label(ax, 10, 2.2,
          "EW cathode → HDR_H2 → dryer → S64 CRYO_H2 → GEN/FC; S24 roof contingency only\n"
          "No tee into HDR_O2.  Separate cryo product tags.  25 ft ignition rule.",
          size=6, weight="normal", color=C_FIRE)

    arrow(ax, 12, 16.5, 16, 17, "#2e7d32")
    arrow(ax, 12, 16, 16, 11, "#5d4037")
    arrow(ax, 12, 15.5, 16, 16.5, "#546e7a")

    label(ax, 28, 5,
          "ZnBr2 Br₂ → regen S69 (≠ CRU). Acid-gas → ALK+POLISH→CRU. Flue→S67 CRYO. AQS-VENT-001.",
          size=6.2, weight="normal", color=C_FIRE)


# ═══════════════════════════════════════════════════════════
# Water cycle
# ═══════════════════════════════════════════════════════════
def water(ax):
    """Roof–catch inventory (this sheet) + regeneration pointers (HAB-WTR / FAB-UPW).

    Roof–catch ≠ VCD regeneration (AQS-WTR-001 §0 / §7). Both appear.
    """
    ax.set_xlim(0, 46)
    ax.set_ylim(0, 28)

    # ── Inventory column (center) ──
    rbox(ax, 16, 20, 14, 5.2, C_ROOF, ec=C_WATER, lw=1.6)
    label(ax, 23, 23.5, "ROOF TANK (L2)", size=9)
    label(ax, 23, 21.6, "S21 gravity · fire reserve\nclean tower water only",
          size=6.3, weight="normal")

    rbox(ax, 18, 12.5, 10, 4.2, "#90caf9", ec=C_WATER, lw=1.4)
    label(ax, 23, 15.2, "SHAFT_PENSTOCK", size=8, color=C_WATER)
    label(ax, 23, 13.6, "S22 / S23 · clean only\nnot process drain",
          size=5.8, weight="normal")

    rbox(ax, 16, 4.5, 14, 5.0, C_CATCH, ec="#455a64", lw=1.6)
    label(ax, 23, 7.8, "CATCH TANK (L-2)", size=9)
    label(ax, 23, 6.0, "lower reservoir · not a process sump\nhydro turbine-pump optional",
          size=6.0, weight="normal")

    arrow(ax, 23, 20, 23, 16.7, C_WATER, lw=2)
    arrow(ax, 23, 12.5, 23, 9.5, C_WATER, lw=2)

    # ── Regeneration (left) — pointer to detail sheets ──
    rbox(ax, 1.5, 18.5, 12, 6.5, "#e3f2fd", ec=C_WATER, lw=1.3)
    label(ax, 7.5, 23.5, "VCD REGENERATION", size=7.5)
    label(ax, 7.5, 21.5, "S13 / S29 → VCD → S25\nED polish → S01 / REMIN\nAQS-PFD-HAB-WTR-001",
          size=5.8, weight="normal")
    arrow(ax, 13.5, 21.5, 16, 21.5, C_WATER, lw=1.4)

    rbox(ax, 1.5, 11.0, 12, 5.5, "#bbdefb", ec=C_WATER, lw=1.2)
    label(ax, 7.5, 14.8, "UPW POLISH / S01", size=7.2)
    label(ax, 7.5, 12.8, "pre-remin HDR_UPW\n→ farm / fab / hab",
          size=5.8, weight="normal")
    arrow(ax, 13.5, 13.5, 18, 13.5, C_WATER, lw=1.2)

    rbox(ax, 1.5, 4.5, 12, 5.0, "#fff8e1", ec="#f9a825", lw=1.2)
    label(ax, 7.5, 7.8, "FAB UPW (S27)", size=7.2)
    label(ax, 7.5, 6.0, "pre-remin polish\nAQS-PFD-FAB-UPW-001",
          size=5.8, weight="normal")

    # ── Dirty / overflow (right) ──
    rbox(ax, 32.5, 20, 11.5, 5.2, C_TERR, ec="#558b2f", lw=1.2)
    label(ax, 38.25, 23.5, "OVERFLOW", size=7.5)
    label(ax, 38.25, 21.6, "S40 → TERRACE\nS41 → CATCH\nAQS-PFD-TRR-001",
          size=5.6, weight="normal")
    arrow(ax, 30, 22.5, 32.5, 22.5, "#558b2f")

    rbox(ax, 32.5, 12.5, 11.5, 5.5, "#b0bec5", lw=1.2)
    label(ax, 38.25, 16.2, "HDR_GREY", size=7.5)
    label(ax, 38.25, 14.2, "S12 collect\n→ GREY treat (HAB-WTR)\nS13 → VCD_FEED",
          size=5.6, weight="normal")

    rbox(ax, 32.5, 4.5, 11.5, 5.0, "#ffcdd2", ec=C_FIRE, lw=1.2)
    label(ax, 38.25, 7.8, "NOT MIXED", size=7.2, color=C_FIRE)
    label(ax, 38.25, 6.0, "Salria · etch · sewer\nnever into roof–catch",
          size=5.6, weight="normal", color=C_FIRE)

    label(ax, 23, 2.2,
          "INVENTORY (this sheet) ≠ REGENERATION (HAB-WTR / FAB-UPW).  "
          "Both required — AQS-WTR-001.",
          size=6.4, weight="bold", color=C_WATER)
    label(ax, 23, 0.7,
          "Loop water never mixes with Salria, grey, or etch.  "
          "Tank overflow → CATCH or HDR_GREY — never L-1 bund.",
          size=6.0, weight="normal", color=C_FIRE)


def _stamp_graph_cross(ax, sector_key="campus_cross"):
    """Light S##/IA overlay from plant_flow_graph (layout sheets)."""
    try:
        edges = sector_edges(sector_key)
        gp = graph_path().name
        lines = ia_register_lines(edges)
    except Exception as exc:  # noqa: BLE001 — show honest failure on sheet
        ax.text(0.5, 0.5, f"graph overlay unavailable: {exc}", fontsize=7, color="red")
        return
    ymin = ax.get_ylim()[0]
    xmin = ax.get_xlim()[0]
    ax.text(xmin + 0.5, ymin + 2.2, f"GRAPH CROSS-LINKS ({gp}) — campus/life layout overlay",
            fontsize=7.0, fontweight="bold", color="#1c1917")
    for i, line in enumerate(lines[:8]):
        ax.text(xmin + 0.5, ymin + 1.6 - i * 0.35, line, fontsize=5.4, color="#57534e")


def main():
    print(f"freecad params: {FP_PATH}")
    print(scale_note())
    save("campus_pfd.png", campus, size=(16, 13))
    save("hazard_separation_pfd.png", hazard, size=(15, 12))
    save("life_headers_pfd.png", life_hdr, size=(13, 9))
    save("life_gas_pfd.png", life_gas, size=(13, 9))
    save("water_cycle_pfd.png", water, size=(14, 10))
    print(f"done → {OUT_DIR}")


if __name__ == "__main__":
    main()
