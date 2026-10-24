#!/usr/bin/env python3
"""High-fidelity building PFDs from AQS-BLD-001 Rev C + live freecad params.

    python3 flow_graph/exporters/matplotlib/building_stack_pfds.py

Produces:
  building_section_pfd.png   AQS-PFD-BLD-001
  basement_pfd.png           AQS-PFD-BLD-002
  ground_floor_pfd.png       AQS-PFD-BLD-003
  life_floor_pfd.png         AQS-PFD-BLD-004
  roof_water_pfd.png         AQS-PFD-BLD-005
  core_plan_pfd.png          AQS-PFD-BLD-006

Authority: docs-authority/BUILDING_STACK.md, docs-authority/HAZARD_SEPARATION.md, models/freecad/params.py.
Does not invent process equipment lists — massing, levels, cores, fire, tanks only.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from flow_graph.pfd_bridge import graph_path, ia_register_lines, sector_edges  # noqa: E402

import importlib.util
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D
import params as P

_HERE = Path(__file__).resolve().parent
ROOT = _HERE.parent if _HERE.name in ("pfd_scripts", "scripts") else _HERE
OUT_DIR = ROOT / "images" if (ROOT / "images").is_dir() else ROOT


def _load_freecad_params():
    """Import live building geometry from freecad/params.py (mm)."""
    candidates = [
        ROOT / "cad" / "freecad" / "params.py",
        ROOT.parent / "cad" / "freecad" / "params.py",
        ROOT.parent / "models" / "freecad" / "params.py",
        _HERE.parent.parent / "cad" / "freecad" / "params.py",
        # local hub fallback omitted from publish tree
    ]
    for path in candidates:
        if path.is_file():
            spec = importlib.util.spec_from_file_location("aqs_freecad_params", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod, path
    raise FileNotFoundError("freecad/params.py not found for building PFDs")


FP, FP_PATH = _load_freecad_params()


def m(mm):
    """Millimetres → metres (drawing units)."""
    return float(mm) / 1000.0


# ── colours ──────────────────────────────────────────────
C_ROOF = "#bbdefb"
C_LIFE = "#c8e6c9"
C_HAB = "#a5d6a7"
C_FARM = "#81c784"
C_GRADE = "#fff9c4"
C_MFG = "#ffe082"
C_FAB = "#ffecb3"
C_PROC = "#ffccbc"
C_OIL = "#ffcdd2"
C_SCRUB = "#f8bbd0"
C_CRYO = "#e1f5fe"
C_CATCH = "#cfd8dc"
C_HYDRO = "#b0bec5"
C_CORE_L = "#e8eaf6"
C_CORE_P = "#fce4ec"
C_FIRE = "#b71c1c"
C_WATER = "#1565c0"
C_SLAB = "#5d4037"
C_SHAFT = "#6a1b9a"


DOC = {
    "building_section_pfd.png": ("AQS-PFD-BLD-001", "Building section — vertical stack"),
    "basement_pfd.png": ("AQS-PFD-BLD-002", "Basement plan — L-1 process + L-2 catch"),
    "ground_floor_pfd.png": ("AQS-PFD-BLD-003", "Grade plan — L0 dock / MFG / FAB"),
    "life_floor_pfd.png": ("AQS-PFD-BLD-004", "Life plan — HAB ∥ FARM"),
    "roof_water_pfd.png": ("AQS-PFD-BLD-005", "Roof plan — tank / array / terraces"),
    "core_plan_pfd.png": ("AQS-PFD-BLD-006", "Core & shaft plan — CORE_LIFE / CORE_PROCESS"),
}


def scale_note():
    return (
        f"SCALE_M={FP.SCALE_M:g}  ·  plate {m(FP.PLATE_L):.0f}×{m(FP.PLATE_W):.0f} m  ·  "
        f"{FP.CASSETTE_ID}  ·  LIFE_LEVELS={FP.LIFE_LEVELS}  ·  "
        f"BASEMENT_LEVELS={FP.BASEMENT_LEVELS}  ·  bay {m(FP.BAY):.0f} m"
    )


def footer(ax, doc_no, fname):
    ax.text(
        0.01, 0.012,
        f"{doc_no}  ·  AQS-BLD-001 Rev C  ·  AQS-HSE-001  ·  CERN-OHL-S  ·  {fname}",
        transform=ax.transAxes, fontsize=10.1, color=P.MUTED,
    )
    ax.text(
        0.99, 0.012, scale_note(),
        transform=ax.transAxes, fontsize=9.6, color=P.MUTED, ha="right",
    )


def sheet(fname, draw_fn, size=(16, 10), dpi=140):
    doc_no, title = DOC[fname]
    fig, ax = plt.subplots(figsize=size, dpi=dpi)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    draw_fn(ax)
    ax.set_title(
        f"{doc_no}  ·  {title}",
        fontsize=19.4, fontweight="bold", color=P.INK, pad=10,
    )
    footer(ax, doc_no, fname)
    _stamp_building_graph(ax)
    out = OUT_DIR / fname
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close()
    print("wrote", out)
    return out


def rbox(ax, x, y, w, h, fc, ec=None, lw=1.2, z=3, alpha=1.0):
    ec = P.INK if ec is None else ec
    ax.add_patch(Rectangle(
        (x, y), w, h, facecolor=fc, edgecolor=ec,
        linewidth=lw, zorder=z, alpha=alpha,
    ))


def label(ax, x, y, text, size=7, weight="bold", color=None, ha="center", va="center", z=5):
    ax.text(
        x, y, text, ha=ha, va=va, fontsize=size, fontweight=weight,
        color=P.INK if color is None else color, zorder=z, linespacing=1.15,
    )


def fire_mark(ax, x0, y0, x1, y1, text, horizontal=True):
    """Dashed fire-barrier / horizontal-assembly mark."""
    ax.plot(
        [x0, x1], [y0, y1], color=C_FIRE, lw=1.8, ls="--", zorder=6,
    )
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    if horizontal:
        ax.text(mx, my + 0.25, text, ha="center", va="bottom",
                fontsize=9.6, color=C_FIRE, fontweight="bold", zorder=7)
    else:
        ax.text(mx + 0.2, my, text, ha="left", va="center",
                fontsize=9.6, color=C_FIRE, fontweight="bold", zorder=7,
                rotation=90)


# ═══════════════════════════════════════════════════════════
# 1. Building section
# ═══════════════════════════════════════════════════════════
def section(ax):
    """Full vertical stack, top → bottom, live Z datums."""
    plate_l = m(FP.PLATE_L)
    plate_w = m(FP.PLATE_W)  # depth into page — show as width fraction
    # Drawing: X = plan length, Y = world Z (m)
    wall_x0 = 4.0
    wall_x1 = wall_x0 + min(plate_l * 0.55, 28.0)  # foreshortened plate for section
    build_w = wall_x1 - wall_x0
    core_frac = m(FP.CORE_L) / m(FP.PLATE_L)
    core_x0 = wall_x0 + build_w * (m(FP.CORE_X) / m(FP.PLATE_L))
    core_w = build_w * core_frac
    core_mid = core_w / 2

    z_top_tank = m(FP.Z_L2 + FP.ROOF_TANK_H)
    z_bot = m(FP.Z_Lm2) - 1.0
    ax.set_xlim(0, wall_x1 + 14)
    ax.set_ylim(z_bot - 2.5, z_top_tank + 4.5)

    # Grade line
    ax.axhline(0, color="#795548", lw=1.4, ls=":", zorder=1)
    label(ax, wall_x1 + 0.4, 0.15, "GRADE  Z=0 (L0 FFL)", size=6.5,
          weight="normal", color="#795548", ha="left", va="bottom")

    # Level bands (fill between FFL and next soffit / clear)
    # Roof tank plate
    z_l2 = m(FP.Z_L2)
    rbox(ax, wall_x0, z_l2, build_w, m(FP.ROOF_TANK_H), C_ROOF, lw=1.4)
    # Tank vessel inset
    tank_inset = build_w * 0.12
    rbox(ax, wall_x0 + tank_inset, z_l2 + 0.4,
         build_w - 2 * tank_inset, m(FP.ROOF_TANK_H) - 0.8,
         "#90caf9", ec=C_WATER, lw=1.5, z=4)
    label(ax, wall_x0 + build_w / 2, z_l2 + m(FP.ROOF_TANK_H) / 2,
          f"ROOF TANK\n{m(FP.ROOF_TANK_L):.0f}×{m(FP.ROOF_TANK_W):.0f}×{m(FP.ROOF_TANK_H):.0f} m\n"
          f"V ∝ plate · clean tower water",
          size=7)

    # Array canopy above tank
    canopy_y = z_l2 + m(FP.ROOF_TANK_H) + 0.8
    ax.plot(
        [wall_x0 - 0.5, wall_x1 + 0.5],
        [canopy_y + 1.5, canopy_y],
        color="#1565c0", lw=2.2, zorder=5,
    )
    label(ax, wall_x0 + build_w / 2, canopy_y + 2.4,
          f"ARRAY_ROOF  tilt = φ ({FP.SITE_LAT_DEG:.0f}°)  ·  air gap ≥ 0.8 m",
          size=6.5, weight="normal", color=C_WATER)

    # Life floors (discrete)
    for i in range(FP.LIFE_LEVELS - 1, -1, -1):
        z = m(FP.life_z(i))
        h = m(FP.CLEAR_L1)
        rbox(ax, wall_x0, z, build_w / 2, h, C_HAB, lw=1.3)
        rbox(ax, wall_x0 + build_w / 2, z, build_w / 2, h, C_FARM, lw=1.3)
        lvl = f"L1" if FP.LIFE_LEVELS == 1 else f"L1.{i}"
        label(ax, wall_x0 + build_w / 4, z + h / 2,
              f"HABITATION\n{lvl}  clear {h:.1f} m\nR-2", size=6.5)
        label(ax, wall_x0 + 3 * build_w / 4, z + h / 2,
              f"FARM\n{lvl}  clear {h:.1f} m\nF-2", size=6.5)
        # FB_HAB_FARM party wall (outside CORE); FB_HAB_CORE at CORE band
        fire_mark(ax, wall_x0 + build_w / 2, z + 0.3,
                  wall_x0 + build_w / 2, z + h - 0.3,
                  "FB_HAB_FARM 2 h", horizontal=False)
        # CORE band on life: 3 h HAB ↔ recycle (distinct assembly)
        fire_mark(ax, core_x0, z + 0.5,
                  core_x0 + build_w * core_frac, z + 0.5,
                  "FB_HAB_CORE 3 h", horizontal=True)
        # Level label left
        label(ax, wall_x0 - 0.3, z + h / 2, lvl, size=8, ha="right", color=C_FIRE)

    # L0 grade
    z0 = m(FP.Z_L0)
    h0 = m(FP.CLEAR_L0)
    rbox(ax, wall_x0, z0, build_w * 0.35, h0, C_GRADE, lw=1.3)
    rbox(ax, wall_x0 + build_w * 0.35, z0, build_w * 0.325, h0, C_MFG, lw=1.3)
    rbox(ax, wall_x0 + build_w * 0.675, z0, build_w * 0.325, h0, C_FAB, lw=1.3)
    label(ax, wall_x0 + build_w * 0.175, z0 + h0 / 2,
          "DOCK\nreceiving", size=6.5)
    label(ax, wall_x0 + build_w * 0.51, z0 + h0 / 2,
          "MFG SHOP\nF-1", size=6.5)
    label(ax, wall_x0 + build_w * 0.84, z0 + h0 / 2,
          "WAFER FAB\nH-5 analog", size=6.5)
    label(ax, wall_x0 - 0.3, z0 + h0 / 2, "L0", size=8, ha="right", color=C_FIRE)

    # Process basements
    for i in range(FP.BASEMENT_LEVELS):
        z = m(FP.basement_z(i))
        h = m(FP.CLEAR_Lm1)
        rbox(ax, wall_x0, z, build_w * 0.72, h, C_PROC, lw=1.3)
        rbox(ax, wall_x0 + build_w * 0.72, z, build_w * 0.28, h, C_CRYO, lw=1.3)
        if i == 0:
            lab = "L-1"
            prog = "LEACH · EW · BMED · OIL · GLASS · scrub"
        else:
            lab = f"L-1b / B{i+1}"
            prog = f"PROCESS_B{i+1} · wet cassette replica"
        label(ax, wall_x0 + build_w * 0.36, z + h / 2,
              f"PROCESS\n{prog}\nF-1 / H-3 if MAQ", size=6.2)
        cryo_lab = "CRYO" if i == 0 else f"CRYO_B{i+1}"
        label(ax, wall_x0 + build_w * 0.86, z + h / 2,
              f"{cryo_lab}\n2 h room\nNFPA 2/55", size=6.2)
        label(ax, wall_x0 - 0.3, z + h / 2, lab, size=8, ha="right", color=C_FIRE)
        # FB_CRYO_PROCESS
        fire_mark(ax, wall_x0 + build_w * 0.72, z + 0.4,
                  wall_x0 + build_w * 0.72, z + h - 0.4,
                  "FB_CRYO_PROCESS 2 h", horizontal=False)

    # Catch / sub-basement
    z_c = m(FP.Z_Lm2)
    h_c = m(FP.CLEAR_Lm2)
    rbox(ax, wall_x0, z_c, build_w * 0.65, h_c, C_CATCH, lw=1.3)
    rbox(ax, wall_x0 + build_w * 0.65, z_c, build_w * 0.35, h_c, C_HYDRO, lw=1.3)
    label(ax, wall_x0 + build_w * 0.325, z_c + h_c / 2,
          f"CATCH TANK\n{m(FP.CATCH_TANK_L):.0f}×{m(FP.CATCH_TANK_W):.0f}×{m(FP.CATCH_TANK_H):.0f} m\n"
          f"clean lower reservoir", size=6.5)
    label(ax, wall_x0 + build_w * 0.825, z_c + h_c / 2,
          "HYDRO SET\nturbine-pump\n(optional M1)", size=6.2)
    label(ax, wall_x0 - 0.3, z_c + h_c / 2, "L-2", size=8, ha="right", color=C_FIRE)

    # Slab lines + HA marks between levels
    # Collect FFL / soffit interfaces
    interfaces = []
    # roof soffit / life top
    interfaces.append((m(FP.Z_L2), "HA_L2_L1 1 h"))
    # between life floors
    for i in range(FP.LIFE_LEVELS - 1):
        interfaces.append((m(FP.life_z(i + 1)), f"life plate {i}/{i+1}"))
    # life / grade
    interfaces.append((m(FP.Z_L1), "HA_L1_L0 3 h"))
    # grade / uppermost basement
    interfaces.append((m(FP.Z_L0), "HA_L0_Lm1 3 h"))
    # between basements
    for i in range(FP.BASEMENT_LEVELS - 1):
        interfaces.append((m(FP.basement_z(i)), f"process plate B{i+1}/B{i+2}"))
    # lowest process / catch
    interfaces.append((m(FP.basement_z(FP.BASEMENT_LEVELS - 1)), "HA_Lm1_Lm2 2 h"))

    for z, txt in interfaces:
        ax.plot([wall_x0, wall_x1], [z, z], color=C_SLAB, lw=2.0, zorder=5)
        if "HA_" in txt:
            ax.text(wall_x1 + 0.35, z, txt, ha="left", va="center",
                    fontsize=9.6, color=C_FIRE, fontweight="bold")

    # CORE vertical band (split LIFE | PROCESS)
    rbox(ax, core_x0, z_c, core_mid, z_top_tank - z_c,
         C_CORE_L, ec="#283593", lw=1.6, z=4, alpha=0.85)
    rbox(ax, core_x0 + core_mid, z_c, core_mid, z_top_tank - z_c,
         C_CORE_P, ec="#880e4f", lw=1.6, z=4, alpha=0.85)
    label(ax, core_x0 + core_mid / 2, z_l2 + m(FP.ROOF_TANK_H) * 0.15,
          "CORE_LIFE", size=6, color="#283593")
    label(ax, core_x0 + core_mid * 1.5, z_l2 + m(FP.ROOF_TANK_H) * 0.15,
          "CORE_PROC", size=6, color="#880e4f")

    # Penstock (clean) in CORE_LIFE
    ax.plot(
        [core_x0 + core_mid * 0.55, core_x0 + core_mid * 0.55],
        [z_c + 0.5, z_l2 + 0.5],
        color=C_WATER, lw=2.5, zorder=6,
    )
    label(ax, core_x0 + core_mid * 0.55 - 0.15, (z_l2 + z0) / 2,
          "SHAFT_PENSTOCK\nclean only", size=5.5, weight="normal",
          color=C_WATER, ha="right", va="center")

    # H2 shaft in CORE_PROCESS
    ax.plot(
        [core_x0 + core_mid * 1.45, core_x0 + core_mid * 1.45],
        [m(FP.Z_Lm1) + 0.5, z_top_tank + 0.3],
        color=C_FIRE, lw=2.0, ls="-.", zorder=6,
    )
    label(ax, core_x0 + core_mid * 1.45 + 0.2, z_l2 + 2,
          "SHAFT_H2\n→ roof vent", size=5.5, weight="normal",
          color=C_FIRE, ha="left")

    # ZnBr2 outdoor callout
    rbox(ax, wall_x0 - 3.2, -0.2, 2.8, 2.4, "#f3e5f5", lw=1.1)
    label(ax, wall_x0 - 1.8, 1.0, "ZnBr2\noutdoor\nNFPA 855", size=5.8)

    # Datum table
    datums = [
        ("L2 tank top", m(FP.Z_L2 + FP.ROOF_TANK_H)),
        ("L2 FFL", m(FP.Z_L2)),
        ("L1 FFL", m(FP.Z_L1)),
        ("L0 FFL", m(FP.Z_L0)),
        ("L-1 FFL", m(FP.Z_Lm1)),
        ("L-2 FFL", m(FP.Z_Lm2)),
    ]
    ty = z_top_tank + 1.2
    label(ax, wall_x1 + 7.5, ty + 1.8, "World Z datums (m)", size=7.5, ha="center")
    for i, (n, z) in enumerate(datums):
        label(ax, wall_x1 + 4.5, ty - i * 0.85, f"{n}", size=6.2,
              weight="normal", ha="left")
        label(ax, wall_x1 + 11.5, ty - i * 0.85, f"{z:+.1f}", size=6.2,
              weight="normal", ha="right", color=C_WATER)

    label(ax, wall_x0 + build_w / 2, z_bot - 1.6,
          "Vertical order locked: ROOF_TANK → LIFE floors → L0 MFG/FAB → process basements → CATCH_TANK",
          size=6.5, weight="normal", color=P.MUTED)


# ═══════════════════════════════════════════════════════════
# Shared plan helpers
# ═══════════════════════════════════════════════════════════
def plan_frame(ax, title_extra=""):
    pl, pw = m(FP.PLATE_L), m(FP.PLATE_W)
    margin = 4.5
    ax.set_xlim(-margin, pl + margin + 2)
    ax.set_ylim(-margin - 1, pw + margin + 1.5)
    rbox(ax, 0, 0, pl, pw, "#fafafa", lw=2.0, z=1)
    # Bay grid
    for i in range(FP.MODULE_BAYS_X + 1):
        x = i * m(FP.BAY)
        ax.plot([x, x], [0, pw], color="#e0e0e0", lw=0.6, zorder=2)
    for j in range(FP.MODULE_BAYS_Y + 1):
        y = j * m(FP.BAY)
        ax.plot([0, pl], [y, y], color="#e0e0e0", lw=0.6, zorder=2)
    # N arrow
    ax.annotate("", xy=(pl + 2.2, pw - 1), xytext=(pl + 2.2, pw - 4),
                arrowprops=dict(arrowstyle="-|>", color=P.INK, lw=1.3))
    label(ax, pl + 2.2, pw - 0.4, "N", size=8)
    label(ax, pl / 2, pw + 1.2, title_extra, size=7.5, weight="normal", color=P.MUTED)
    return pl, pw


def draw_core(ax, zorder=8):
    cx, cy = m(FP.CORE_X), m(FP.CORE_Y)
    cl, cw = m(FP.CORE_L), m(FP.CORE_W)
    rbox(ax, cx, cy, cl / 2, cw, C_CORE_L, ec="#283593", lw=1.5, z=zorder)
    rbox(ax, cx + cl / 2, cy, cl / 2, cw, C_CORE_P, ec="#880e4f", lw=1.5, z=zorder)
    label(ax, cx + cl / 4, cy + cw / 2, "CORE\nLIFE", size=6.5, color="#283593")
    label(ax, cx + 3 * cl / 4, cy + cw / 2, "CORE\nPROC", size=6.5, color="#880e4f")
    return cx, cy, cl, cw


def perimeter_stairs(ax, pl, pw):
    # STAIR_S1 NW, STAIR_S2 SE — 1.2×2.4 conceptual
    sw, sh = 1.2, 2.4
    rbox(ax, 0.3, pw - sh - 0.3, sw, sh, "#eeeeee", lw=1.0, z=7)
    label(ax, 0.3 + sw / 2, pw - sh / 2 - 0.3, "S1", size=5.5)
    rbox(ax, pl - sw - 0.3, 0.3, sw, sh, "#eeeeee", lw=1.0, z=7)
    label(ax, pl - sw / 2 - 0.3, 0.3 + sh / 2, "S2", size=5.5)


# M1 keep-out masses from BUILDING_STACK §9 (m on 24×18), scaled to live plate
def _xy_scale():
    return m(FP.PLATE_L) / 24.0, m(FP.PLATE_W) / 18.0


def scaled_block(x0, y0, l0, w0):
    sx, sy = _xy_scale()
    return x0 * sx, y0 * sy, l0 * sx, w0 * sy


# ═══════════════════════════════════════════════════════════
# 2. Basement plan
# ═══════════════════════════════════════════════════════════
def basement(ax):
    pl, pw = plan_frame(
        ax,
        f"L-1 process (uppermost) + L-2 catch under  ·  CRYO east of CORE",
    )
    # L-1 process blocks — M1 keep-out sizes at M1 origins (AQS-BLD-001 §9).
    # Plate may grow with SCALE_M; keep-outs do not stretch.
    blocks = [
        (0, 4, 12, 8, "LEACH + EW aisle\n12×8 m keep-out\nF-1 / H-3", C_PROC),
        (12, 4, 8, 6, "BMED / CRU\nprecip\n8×6 m", "#ffe0b2"),
        (0, 12, 10, 6, "OIL + GLASS\n10×6 m\nH-3 vapor", C_OIL),
        (18, 12, 6, 6, "SCRUBBERS\nstack base\n6×6 m", C_SCRUB),
    ]
    for x, y, l, w, lab, fc in blocks:
        if x < pl and y < pw:
            l = min(l, pl - x)
            w = min(w, pw - y)
            rbox(ax, x, y, l, w, fc, lw=1.2, z=3)
            label(ax, x + l / 2, y + w / 2, lab, size=6.2)

    # CRYO live position
    rbox(ax, m(FP.CRYO_X), m(FP.CRYO_Y), m(FP.CRYO_L), m(FP.CRYO_W),
         C_CRYO, ec="#0277bd", lw=1.6, z=4)
    label(ax, m(FP.CRYO_X) + m(FP.CRYO_L) / 2, m(FP.CRYO_Y) + m(FP.CRYO_W) / 2,
          f"CRYO\n{m(FP.CRYO_L):.0f}×{m(FP.CRYO_W):.0f} m\nNFPA 2/55", size=6.5)

    draw_core(ax)
    perimeter_stairs(ax, pl, pw)

    # FB_CRYO_PROCESS along CRYO west face (toward process)
    fire_mark(
        ax, m(FP.CRYO_X), m(FP.CRYO_Y),
        m(FP.CRYO_X), m(FP.CRYO_Y) + m(FP.CRYO_W),
        "FB_CRYO_PROCESS 2 h", horizontal=False,
    )

    # L-2 callouts — live CATCH footprint dashed on plate; hydro keep-out at M1 origin
    ax.add_patch(Rectangle(
        (m(FP.CATCH_TANK_X), m(FP.CATCH_TANK_Y)),
        m(FP.CATCH_TANK_L), m(FP.CATCH_TANK_W),
        fill=False, edgecolor="#455a64", lw=1.4, ls="--", zorder=6,
    ))
    label(ax, m(FP.CATCH_TANK_X) + m(FP.CATCH_TANK_L) / 2,
          m(FP.CATCH_TANK_Y) + m(FP.CATCH_TANK_W) / 2,
          f"L-2 CATCH TANK (under)\n{m(FP.CATCH_TANK_L):.0f}×{m(FP.CATCH_TANK_W):.0f}×{m(FP.CATCH_TANK_H):.0f} m",
          size=6, weight="normal", color="#455a64")
    ax.add_patch(Rectangle(
        (12, 4), 6, 6,
        fill=False, edgecolor="#546e7a", lw=1.2, ls="--", zorder=6,
    ))
    label(ax, 15, 7, "L-2 HYDRO SET\n6×6 m keep-out", size=5.5,
          weight="normal", color="#546e7a")

    if FP.BASEMENT_LEVELS > 1:
        label(ax, pl / 2, -3.2,
              f"NOTE: BASEMENT_LEVELS={FP.BASEMENT_LEVELS} — additional process plates "
              f"(PROCESS_B2 / CRYO_B2) stack below L-1; CATCH remains deepest.",
              size=6.2, weight="normal", color=P.MUTED)

    # Corridor note
    label(ax, pl / 2, pw + 2.4,
          "Corridors along bay grid · STAIR_SERVICE (north) + STAIR_MAINT to L-2 · "
          "no STAIR_P door onto L-1 · hab egress never through H",
          size=6.2, weight="normal", color=P.MUTED)


# ═══════════════════════════════════════════════════════════
# 3. Ground floor
# ═══════════════════════════════════════════════════════════
def ground(ax):
    pl, pw = plan_frame(ax, "L0 GRADE — NORTH dock / MFG / FAB  ·  ZnBr2 west  ·  +Y = N")
    # North dock — live DOCK_* from params (AQS-SITE-001)
    dx, dy = m(FP.DOCK_X), m(FP.DOCK_Y)
    dl, dw = m(FP.DOCK_L), m(FP.DOCK_W)
    rbox(ax, dx, dy, dl, dw, C_GRADE, lw=1.3, z=3)
    label(ax, dx + dl / 2, dy + dw / 2,
          "DOCK + RECEIVING\nnorth / pole-facing\nS-1 / F-1", size=7)
    # Exterior apron north of plate
    apron = m(getattr(FP, "DOCK_APRON_N", 6000))
    rbox(ax, dx, pw, max(dl, 12.0), apron * 0.5, "#cfd8dc", lw=1.0, z=2)
    label(ax, dx + dl / 2, pw + apron * 0.25,
          "DOCK_APRON_N", size=5.5, weight="normal")

    # MFG live
    rbox(ax, m(FP.MFG_X), m(FP.MFG_Y), m(FP.MFG_L), m(FP.MFG_W),
         C_MFG, lw=1.4, z=3)
    label(ax, m(FP.MFG_X) + m(FP.MFG_L) / 2, m(FP.MFG_Y) + m(FP.MFG_W) / 2,
          f"MFG SHOP\n{m(FP.MFG_L):.0f}×{m(FP.MFG_W):.0f} m\nF-1  ·  no Salria", size=7)

    # FAB live
    rbox(ax, m(FP.FAB_X), m(FP.FAB_Y), m(FP.FAB_L), m(FP.FAB_W),
         C_FAB, lw=1.4, z=3)
    label(ax, m(FP.FAB_X) + m(FP.FAB_L) / 2, m(FP.FAB_Y) + m(FP.FAB_W) / 2,
          f"WAFER FAB\n{m(FP.FAB_L):.0f}×{m(FP.FAB_W):.0f} m\nH-5 analog", size=7)

    draw_core(ax)
    perimeter_stairs(ax, pl, pw)

    # North-facing loading door
    door_x0 = dx + (dl - m(FP.DOCK_DOOR_W)) / 2
    door_x1 = door_x0 + m(FP.DOCK_DOOR_W)
    ax.plot([door_x0, door_x1], [pw, pw], color=P.INK, lw=4,
            solid_capstyle="butt", zorder=7)
    label(ax, (door_x0 + door_x1) / 2, pw + 1.2,
          "DOCK_DOOR_N\n(+Y)", size=5.5, weight="normal")

    # SERVICE_ENTRY + STAIR_SERVICE (NW)
    sx, sy = m(FP.SERVICE_ENTRY_X), m(FP.SERVICE_ENTRY_Y)
    sl, sw = m(FP.SERVICE_ENTRY_L), m(FP.SERVICE_ENTRY_W)
    rbox(ax, sx, sy, sl, sw, "#fff3e0", ec="#e65100", lw=1.2, z=4)
    label(ax, sx + sl / 2, sy + sw / 2,
          "SERVICE\nENTRY", size=5.5)
    ssx, ssy = m(FP.STAIR_SERVICE_X), m(FP.STAIR_SERVICE_Y)
    ssl, ssw = m(FP.STAIR_SERVICE_L), m(FP.STAIR_SERVICE_W)
    rbox(ax, ssx, ssy, ssl, ssw, "#ffe0b2", ec="#e65100", lw=1.2, z=4)
    label(ax, ssx + ssl / 2, ssy + ssw / 2,
          "STAIR\nSERVICE\n→ L-1/L-2", size=5.2)

    # ZnBr2 outdoor west of north dock
    rbox(ax, -3.5, dy + 1.0, 3.0, 4.0, "#f3e5f5", ec="#6a1b9a", lw=1.3, z=3)
    label(ax, -2.0, dy + 3.0,
          f"ZnBr2 ESS\noutdoor\n×{FP.ZNBR_COUNT}\nNFPA 855", size=5.8)
    fire_mark(ax, -0.5, dy + 1.0, -0.5, dy + 5.0, "FB_ESS open-air", horizontal=False)

    # POWER yard west, Y-aligned to north dock
    rbox(ax, -3.5, dy - 1.0, 8, 2.8, "#ede7f6", lw=1.1, z=3)
    label(ax, 0.5, dy + 0.4,
          f"POWER YARD (NW)  ·  PV×{FP.PV_COUNT}  ·  rect×{FP.RECT_COUNT}  ·  GEN/FC/GEO",
          size=6, weight="normal")

    label(ax, pl / 2, -4.2,
          "Site north = +Y (AQS-SITE-001).  CRYO on L-1 east of CORE — not L0.  "
          "STAIR_SERVICE = basement secondary egress (not hab sleeping).",
          size=6.2, weight="normal", color=C_FIRE)


# ═══════════════════════════════════════════════════════════
# 4. Life floor
# ═══════════════════════════════════════════════════════════
def life(ax):
    n = FP.LIFE_LEVELS
    pl, pw = plan_frame(
        ax,
        f"LIFE plate  ·  {n} discrete floor(s) HAB∥FARM  ·  clear {m(FP.CLEAR_L1):.1f} m each",
    )
    # HAB west / FARM east — live envelopes
    rbox(ax, m(FP.HAB_X), m(FP.HAB_Y), m(FP.HAB_L), m(FP.HAB_W),
         C_HAB, lw=1.4, z=3)
    label(ax, m(FP.HAB_X) + m(FP.HAB_L) / 2, m(FP.HAB_Y) + m(FP.HAB_W) / 2,
          f"HABITATION\n{m(FP.HAB_L):.0f}×{m(FP.HAB_W):.0f} m\n"
          f"clear {m(FP.HAB_H):.1f} m fit-out\nR-2  ·  dedicated AHU",
          size=7.5)

    rbox(ax, m(FP.FARM_X), m(FP.FARM_Y), m(FP.FARM_L), m(FP.FARM_W),
         C_FARM, lw=1.4, z=3)
    label(ax, m(FP.FARM_X) + m(FP.FARM_L) / 2, m(FP.FARM_Y) + m(FP.FARM_W) / 2,
          f"FARM\n{m(FP.FARM_L):.0f}×{m(FP.FARM_W):.0f} m\n"
          f"clear {m(FP.FARM_H):.1f} m fit-out\nF-2 / U accessory",
          size=7.5)

    # Party wall FB_HAB_FARM (2 h) outside CORE Y-band; FB_HAB_CORE (3 h) on CORE
    hx = m(FP.HAB_X) + m(FP.HAB_L)
    cy0, cy1 = m(FP.CORE_Y), m(FP.CORE_Y) + m(FP.CORE_W)
    fire_mark(ax, hx, 0.4, hx, max(0.4, cy0 - 0.2), "FB_HAB_FARM 2 h", horizontal=False)
    fire_mark(ax, hx, min(pw - 0.4, cy1 + 0.2), hx, pw - 0.4, "FB_HAB_FARM 2 h", horizontal=False)
    # CORE enclosure toward HAB (3 h) — west + south/north faces + centreline band
    cx, cl, cw = m(FP.CORE_X), m(FP.CORE_L), m(FP.CORE_W)
    fire_mark(ax, cx, cy0, cx, cy1, "FB_HAB_CORE 3 h", horizontal=False)
    fire_mark(ax, cx, cy0, cx + cl, cy0, "", horizontal=True)
    fire_mark(ax, cx, cy1, cx + cl, cy1, "", horizontal=True)
    fire_mark(ax, hx, cy0, hx, cy1, "", horizontal=False)

    draw_core(ax)
    perimeter_stairs(ax, pl, pw)

    # Shaft / util callouts
    cx, cy, cl, cw = m(FP.CORE_X), m(FP.CORE_Y), m(FP.CORE_L), m(FP.CORE_W)
    label(ax, cx + cl / 4, cy - 1.2,
          "STAIR_P · ELEV_SVC · SHAFT_UTIL · PENSTOCK",
          size=5.5, weight="normal", color="#283593")
    label(ax, cx + 3 * cl / 4, cy - 1.2,
          "no H2 / acid / oil in life core",
          size=5.5, weight="normal", color="#880e4f")

    label(ax, pl / 2, -3.5,
          "HA_L1_L0 3 h horizontal below this plate  ·  "
          "hab egress lands at grade without walking the basement",
          size=6.5, weight="normal", color=C_FIRE)
    if n > 1:
        label(ax, pl / 2, pw + 2.6,
              f"Sheet shows one typical life plate; LIFE_LEVELS={n} — "
              f"repeat HAB∥FARM pair on each discrete floor (L1.0 … L1.{n-1}).",
              size=6.2, weight="normal", color=P.MUTED)


# ═══════════════════════════════════════════════════════════
# 5. Roof / water
# ═══════════════════════════════════════════════════════════
def roof(ax):
    pl, pw = plan_frame(
        ax,
        f"L2 ROOF — tank / ARRAY_ROOF / H2 contingency (S24) / overflow terraces (N-hemisphere S/E/W)",
    )
    # Tank
    rbox(ax, m(FP.ROOF_TANK_X), m(FP.ROOF_TANK_Y),
         m(FP.ROOF_TANK_L), m(FP.ROOF_TANK_W),
         C_ROOF, ec=C_WATER, lw=1.8, z=3)
    label(ax, m(FP.ROOF_TANK_X) + m(FP.ROOF_TANK_L) / 2,
          m(FP.ROOF_TANK_Y) + m(FP.ROOF_TANK_W) / 2,
          f"ROOF TANK\n{m(FP.ROOF_TANK_L):.0f}×{m(FP.ROOF_TANK_W):.0f}×{m(FP.ROOF_TANK_H):.0f} m\n"
          f"clean tower · fire reserve · S21–S23",
          size=7.5)

    draw_core(ax)

    # H2 vent stub (CORE_PROCESS roof)
    cx, cy, cl, cw = m(FP.CORE_X), m(FP.CORE_Y), m(FP.CORE_L), m(FP.CORE_W)
    rbox(ax, cx + cl / 2 + 0.3, cy + cw - 1.5, 1.2, 1.2, "#ffcdd2", ec=C_FIRE, lw=1.3, z=6)
    label(ax, cx + cl / 2 + 0.9, cy + cw - 0.9, "H2\nvent", size=5.5, color=C_FIRE)

    # Array canopy annotation
    label(ax, pl / 2, pw + 2.5,
          f"ARRAY_ROOF canopy above tank  ·  tilt = {FP.SITE_LAT_DEG:.0f}° S  ·  "
          f"air gap ≥ 0.8 m  ·  not hung from tank wall",
          size=6.5, weight="normal", color=C_WATER)

    # Terraces S / E / W (N-hemisphere); N low yield
    tw = m(FP.TERRACE_WIDTH)
    # South terrace
    rbox(ax, 0, -tw - 0.2, pl, tw, "#dcedc8", ec="#558b2f", lw=1.1, z=2)
    label(ax, pl / 2, -tw / 2 - 0.1, "OVERFLOW_TERRACE_S  (equator-facing)", size=6)
    # East
    rbox(ax, pl + 0.2, 0, tw, pw, "#dcedc8", ec="#558b2f", lw=1.1, z=2)
    label(ax, pl + tw / 2 + 0.2, pw / 2, "TERRACE_E", size=6, weight="normal")
    # West
    rbox(ax, -tw - 0.2, 0, tw, pw, "#dcedc8", ec="#558b2f", lw=1.1, z=2)
    label(ax, -tw / 2 - 0.2, pw / 2, "TERRACE_W", size=6, weight="normal")
    # North note
    label(ax, pl / 2, pw + 0.7, "N facade — low PV yield (N-hemisphere)", size=5.8,
          weight="normal", color=P.MUTED)

    # Drain corners
    for (x, y, n) in [
        (0.5, pw - 0.8, "NW"), (pl - 0.5, pw - 0.8, "NE"),
        (0.5, 0.8, "SW"), (pl - 0.5, 0.8, "SE"),
    ]:
        ax.plot(x, y, "o", color=C_WATER, ms=5, zorder=7)
        label(ax, x, y - 0.9 if y > pw / 2 else y + 0.9,
              f"DRAIN_SEC_{n}", size=5, weight="normal", color=C_WATER)

    # Penstock down
    ax.annotate(
        "", xy=(cx + cl / 4, cy + cw / 2),
        xytext=(cx + cl / 4, cy + cw / 2 + 0.01),
        arrowprops=dict(arrowstyle="-|>", color=C_WATER, lw=1.5),
    )
    label(ax, cx + cl / 4 - 0.3, cy + cw / 2,
          "↓ SHAFT_PENSTOCK\nto CATCH", size=5.5, weight="normal",
          color=C_WATER, ha="right")

    label(ax, pl / 2, -tw - 2.2,
          "Surplus path: ROOF full + ZnBr2 full → OVERFLOW_SPILL → terrace bands (S40) → apron → CATCH (S41).  "
          "Never L-1 process bund.  ZnBr2 remains the electrical battery.",
          size=6.0, weight="normal", color=P.MUTED)
    label(ax, pl / 2, -tw - 3.4,
          "Roof–catch = clean inventory (S21–S23).  Terrace planting / open vs GH = AQS-PFD-TRR-001.  "
          "VCD + remin = HAB-WTR / FAB-UPW — not this plan.",
          size=5.8, weight="normal", color=C_WATER)


# ═══════════════════════════════════════════════════════════
# 6. Core & shaft plan
# ═══════════════════════════════════════════════════════════
def core(ax):
    # Detail of 6×6 m bay — use metres at 1:1 of CORE
    ax.set_xlim(-1.5, 14)
    ax.set_ylim(-2.5, 10)
    # Outer bay
    rbox(ax, 0, 0, 6, 6, "#fafafa", lw=2.0, z=1)
    # Split
    rbox(ax, 0, 0, 3, 6, C_CORE_L, ec="#283593", lw=1.8, z=2)
    rbox(ax, 3, 0, 3, 6, C_CORE_P, ec="#880e4f", lw=1.8, z=2)
    label(ax, 1.5, 5.55, "CORE_LIFE  (2 h room)", size=8, color="#283593")
    label(ax, 4.5, 5.55, "CORE_PROCESS  (2 h room)", size=8, color="#880e4f")

    # CORE_LIFE contents — sizes from BLD §2.1
    # STAIR_P 2.4×4.8
    rbox(ax, 0.15, 0.15, 2.4, 4.8, "#c5cae9", lw=1.2, z=3)
    label(ax, 1.35, 2.55, "STAIR_P\n2.4×4.8\nL2–L0\nno L-1 door", size=6)
    # ELEV_SVC 2.7×3.2 — won't fully fit beside stair in 3 m half;
    # show schematic stacked in remaining strip
    rbox(ax, 0.2, 0.2, 1.1, 1.5, "#9fa8da", lw=1.0, z=4)
    label(ax, 0.75, 0.95, "ELEV\n2.7×3.2\nshaft", size=5)
    # SHAFT_UTIL 1.2×2.4
    rbox(ax, 1.6, 0.2, 1.2, 1.4, "#90caf9", lw=1.0, z=4)
    label(ax, 2.2, 0.9, "UTIL\n1.2×2.4", size=5)
    # SHAFT_PENSTOCK 0.8×0.8
    rbox(ax, 2.0, 4.0, 0.8, 0.8, "#1565c0", lw=1.0, z=4)
    label(ax, 2.4, 4.4, "PEN\n0.8²", size=5, color="white")

    # CORE_PROCESS shafts
    shafts = [
        (3.2, 4.2, "H2", "0.8×0.8\nS24 top vent"),
        (4.2, 4.2, "ACID", "0.8×0.8\nHDR_ACID_GAS"),
        (5.0, 4.2, "OIL", "0.8×0.8\nflue"),
        (3.2, 2.8, "DUST", "riser\nHDR_DUST"),
    ]
    for x, y, name, sub in shafts:
        rbox(ax, x, y, 0.85, 1.1, "#f8bbd0", ec=C_FIRE, lw=1.1, z=4)
        label(ax, x + 0.42, y + 0.55, f"{name}\n{sub}", size=4.8)

    label(ax, 4.5, 1.5,
          "People, H₂, and flue\nnever share a sleeve.\nNo process duct in\nSTAIR_P / ELEV / UTIL / PEN.",
          size=6, weight="normal", color="#880e4f")

    # Perimeter callouts
    label(ax, 7.5, 8.5, "Central 6×6 m structural bay — plate centreline", size=8, ha="left")
    rows = [
        ("STAIR_S1", "NW corner · L1 hab + L0 secondary"),
        ("STAIR_S2", "SE corner · L1 farm + L0 secondary"),
        ("STAIR_MAINT", "1.2×2.4 · L0–L-2 operators · not hab exit"),
        ("STAIR_SERVICE", "2.4×3.6 · L0–L-2 · north service + basement egress"),
        ("SERVICE_ENTRY", "3.6×2.4 · L0 north vestibule · DOCK strip"),
        ("DRAIN_SEC_*", "four corners · exterior · not Salria"),
        ("ELEV_SVC", "freight L-2/L0/L1/L2 · L-1 via rated lobby only"),
    ]
    for i, (a, b) in enumerate(rows):
        label(ax, 7.5, 7.2 - i * 1.05, f"{a}", size=6.5, ha="left", color="#283593")
        label(ax, 7.5, 6.75 - i * 1.05, f"  {b}", size=5.8, weight="normal", ha="left")

    # Orientation
    label(ax, 3, -0.8, "S (equator / terraces)", size=7, weight="normal")
    label(ax, 3, 6.6, "N (dock / SERVICE)  +Y", size=7, weight="normal")
    label(ax, -0.7, 3, "W", size=7, weight="normal")
    label(ax, 6.5, 3, "E", size=7, weight="normal")

    label(ax, 6.5, -1.8,
          "Authority sizes: AQS-BLD-001 §5.1  ·  ratings: AQS-HSE-001 locked barrier table",
          size=6, weight="normal", color=P.MUTED, ha="center")


def _stamp_building_graph(ax):
    """Light building-stack cross-link overlay from plant_flow_graph."""
    edges = sector_edges("building_cross")
    gp = graph_path().name
    lines = ia_register_lines(edges)
    ymin = ax.get_ylim()[0]
    xmin = ax.get_xlim()[0]
    ax.text(xmin + 0.5, ymin + 2.4, f"GRAPH CROSS-LINKS ({gp}) — building stack layout overlay",
            fontsize=10.8, fontweight="bold", color="#1c1917")
    for i, line in enumerate(lines[:8]):
        ax.text(xmin + 0.5, ymin + 1.8 - i * 0.35, line, fontsize=8.4, color="#57534e")
    ax.text(xmin + 0.5, ymin + 1.8 - min(8, len(lines)) * 0.35 - 0.25,
            "Non-process layout: overlay only; DOCK_EXPORT_TBD has no S##.",
            fontsize=8.7, color="#57534e")


def main():
    print(f"freecad params: {FP_PATH}")
    print(scale_note())
    outs = [
        sheet("building_section_pfd.png", section, size=(16, 12)),
        sheet("basement_pfd.png", basement, size=(15, 12)),
        sheet("ground_floor_pfd.png", ground, size=(15, 12)),
        sheet("life_floor_pfd.png", life, size=(15, 12)),
        sheet("roof_water_pfd.png", roof, size=(15, 13)),
        sheet("core_plan_pfd.png", core, size=(12, 9)),
    ]
    print(f"done — {len(outs)} sheets → {OUT_DIR}")


if __name__ == "__main__":
    main()
