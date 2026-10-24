#!/usr/bin/env python3
"""Schematic Phase D frames from params. Not a FreeCAD viewport capture.

    python3 render_frames.py

Writes models/animation/*.png, a scratch folder that flow_graph/regen_derived.py empties into media/ and then deletes. Token is an 80 mm stand-in. No workers,
flames, mixed headers, or FR-4 on the pyro path.
"""
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import params as P
import animate_shots as A

OUT = Path(__file__).resolve().parent.parent / "animation"
BG = "#f3efe6"
INK = "#1c1917"
MUTED = "#44403c"


def _rect(ax, x, y, w, h, fc, ec, label=None):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec,
                           linewidth=0.8, zorder=2))
    if label:
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=6, color=INK, zorder=3)


def plant_xy(ax):
    t = P.WALL
    _rect(ax, 0, 0, P.CSTR_L + 2 * t, P.CSTR_W + 2 * t, "#dcfce7", "#166534",
          "LEACH CSTR 1")
    weir_x = t + P.CSTR_L
    weir_y = t + (P.CSTR_W - P.WEIR_W) / 2
    _rect(ax, weir_x, weir_y, t + P.WEIR_LIP, P.WEIR_W, "#bbf7d0", "#166534")
    _rect(ax, -P.MEZZ_L, t + (P.CSTR_W - P.HOPPER_W) / 2,
          P.MEZZ_L, P.HOPPER_W, "#e4e4e7", "#3f3f46", "HOPPER")
    for i, metal in enumerate(P.EW_METALS):
        x = P.AISLE_X0 + i * P.EW_PITCH
        _rect(ax, x, P.AISLE_Y, P.EW_L + 2 * t, P.EW_W + 2 * t,
              "#dbeafe", "#1e3a8a", "EW-%d %s" % (i + 1, metal))
    ox = t + P.CSTR_L + t + P.WEIR_LIP + P.FDEW_L + P.STUB_L + 100
    oy = t + (P.CSTR_W - P.WEIR_W) / 2
    _rect(ax, ox, oy, P.DRYER_L, P.DRYER_W, "#ffedd5", "#9a3412", "DRYER")
    _rect(ax, ox + P.DRYER_L + 80, oy, P.PYRO_L, P.DRYER_W,
          "#fed7aa", "#9a3412", "PYRO")
    qx = ox + P.DRYER_L + 80 + P.PYRO_L + 80
    _rect(ax, qx, oy, 800, P.DRYER_W, "#ffedd5", "#9a3412", "QUENCH")
    fx = qx + 900
    _rect(ax, fx, oy, 500, P.DRYER_W, "#ffedd5", "#9a3412", "FRAC")
    _rect(ax, fx + 1200, oy, 400, P.DRYER_W, "#fecaca", "#7f1d1d", "AB")
    ax.set_aspect("equal")
    ax.set_facecolor(BG)
    ax.tick_params(labelsize=6)
    ax.set_xlabel("X mm", fontsize=7)
    ax.set_ylabel("Y mm", fontsize=7)


def plant_xz(ax):
    t = P.WALL
    _rect(ax, 0, 0, P.CSTR_L + 2 * t, P.FLOOR + P.CSTR_H + t,
          "#dcfce7", "#166534", "CSTR")
    _rect(ax, -P.MEZZ_L, P.MEZZ_H, P.MEZZ_L, P.HOPPER_H + P.SHRED_H,
          "#e4e4e7", "#3f3f46", "MEZZ")
    for i in range(9):
        x = P.AISLE_X0 + i * P.EW_PITCH
        _rect(ax, x, P.AISLE_Z - P.EW_FUNNEL_H, P.EW_L,
              P.EW_H + P.EW_FUNNEL_H, "#dbeafe", "#1e3a8a")
    ox = t + P.CSTR_L + t + P.WEIR_LIP + P.FDEW_L + P.STUB_L + 100
    _rect(ax, ox, 0, P.DRYER_L, P.DRYER_H, "#ffedd5", "#9a3412")
    _rect(ax, ox + P.DRYER_L + 80, 240, P.PYRO_L, P.PYRO_D, "#fed7aa", "#9a3412")
    ax.set_aspect("equal")
    ax.set_facecolor(BG)
    ax.tick_params(labelsize=6)
    ax.set_xlabel("X mm", fontsize=7)
    ax.set_ylabel("Z mm", fontsize=7)


def draw_path(ax, pts, color, current=None, plan=True):
    xs = [p[0] for p in pts]
    ys = [p[1] if plan else p[2] for p in pts]
    ax.plot(xs, ys, color=color, lw=1.2, zorder=4)
    if current is not None:
        ax.scatter([current[0]], [current[1] if plan else current[2]],
                   s=40, c=color, zorder=5, edgecolors=INK, linewidths=0.4)


SHOT_GROUPS = [
    ("D1", "D1 shred drop — no pre-leach screen",
     [("D1_shred_drop", "#166534")]),
    ("D2", "D2 float / sink / grit — oil vs glass fork",
     [("D2_float", "#9a3412"), ("D2_sink", "#1d4ed8"), ("D2_grit", "#44403c")]),
    ("D3", "D3 EW overflow Au→Zn",
     [("D3_ew_overflow", "#1e3a8a")]),
    ("D4", "D4 harvest EW-1 + EW-6 Fe — bund stays closed",
     [("D4_powder", "#115e59"), ("D4_fe", "#44403c")]),
    ("D5", "D5 dryer → Ti pyro pipe → quench — no FR-4",
     [("D5_pyro", "#9a3412")]),
    ("D6", "D6 cuts + C29 recycle + NCG to AFTERBURNER",
     [("D6_cuts", "#9a3412"), ("D6_c29_recycle", "#b45309"),
      ("D6_ncg", "#7f1d1d")]),
]


def storyboard(tag, title, tracks):
    n = 6
    fig, axes = plt.subplots(2, 3, figsize=(14, 8.4),
                             facecolor=BG)
    fig.suptitle(title, fontsize=13, fontweight="bold", color=INK)
    paths = A.shots()
    for i, ax in enumerate(axes.flat):
        plant_xy(ax)
        u = i / (n - 1)
        for name, color in tracks:
            pts = paths[name]
            frames = max(2, A.DURATION_S.get(name, 4) * A.FPS)
            series = A.lerp_path(pts, frames)
            idx = min(int(u * (len(series) - 1)), len(series) - 1)
            draw_path(ax, pts, color, current=series[idx], plan=True)
        ax.set_title("t = %.1f / panel %d" % (u * max(A.DURATION_S.get(n, 0) for n, _ in tracks), i + 1),
                     fontsize=8)
    fig.text(0.01, 0.01,
             "AQS-ANM-001 schematic. Token 80 mm. Not a FreeCAD GUI capture.",
             fontsize=7, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    path = OUT / ("%s.png" % tag)
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print("wrote", path)


def overview():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), facecolor=BG)
    fig.suptitle("Phase D token paths — plan and elevation",
                 fontsize=14, fontweight="bold", color=INK)
    plant_xy(ax1)
    plant_xz(ax2)
    paths = A.shots()
    colors = {
        "D1_shred_drop": "#166534",
        "D2_float": "#9a3412",
        "D2_sink": "#1d4ed8",
        "D2_grit": "#44403c",
        "D3_ew_overflow": "#1e3a8a",
        "D4_powder": "#115e59",
        "D5_pyro": "#c2410c",
        "D6_cuts": "#9a3412",
        "D6_c29_recycle": "#b45309",
        "D6_ncg": "#7f1d1d",
    }
    for name, pts in paths.items():
        c = colors.get(name, "#78716c")
        draw_path(ax1, pts, c, plan=True)
        draw_path(ax2, pts, c, plan=False)
        ax1.text(pts[-1][0], pts[-1][1], name, fontsize=5, color=c)
    ax1.set_title("plan X–Y", fontsize=9)
    ax2.set_title("elevation X–Z", fontsize=9)
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))
    path = OUT / "D0_overview.png"
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print("wrote", path)


def campus():
    fig, ax = plt.subplots(figsize=(12, 8), facecolor=BG)
    fig.suptitle("Phase F keep-outs vs recycle aisle",
                 fontsize=14, fontweight="bold", color=INK)
    _rect(ax, 0, 0, 2200, 1224, "#dcfce7", "#166534", "CSTR")
    _rect(ax, 200, P.AISLE_Y, 9 * P.EW_PITCH, P.EW_W + 24, "#dbeafe", "#1e3a8a",
          "EW AISLE")
    _rect(ax, 12000, 8000, 12000, 8000, "#ccfbf1", "#115e59", "FARM")
    _rect(ax, 12000, -6000, 8000, 6000, "#e0e7ff", "#3730a3", "WAFER_FAB")
    _rect(ax, -8000, 8000, 8000, 6000, "#fef3c7", "#92400e", "HABITATION")
    _rect(ax, -6000, -4000, 4000, 3000, "#e0f2fe", "#075985", "CRYO")
    ax.set_aspect("equal")
    ax.set_facecolor(BG)
    ax.set_xlim(-9000, 25000)
    ax.set_ylim(-7000, 17000)
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")
    ax.text(-8500, -6500,
            "AQS-PHF-001 envelopes. Process headers stay on the recycle aisle.",
            fontsize=7, color=MUTED)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.92, bottom=0.08)
    path = OUT / "F0_campus.png"
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print("wrote", path)


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    overview()
    campus()
    for tag, title, tracks in SHOT_GROUPS:
        storyboard(tag, title, tracks)


if __name__ == "__main__" or any(Path(a).name == Path(__file__).name for a in sys.argv):
    build()
