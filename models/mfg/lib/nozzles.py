# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Nozzle hardware builders DN15 to DN50 (AQS-PLAN-006 section 6, T0 item 2): plain stubs,
Class 150 flange stubs and hose barbs, plus the face-placement helper the unit models use.

Geometry only. The bore, the face and the height of every nozzle on a unit come from that
unit's duty section 4 schedule (`docs-authority/nozzles/<UNIT>.csv`); AQS-STD-001 decides
where a connection is flanged (a stated process pressure, rated to 110 %) and where it
stays atmospheric tube or hose. Dimensions inside the stubs come from `lib/dn.py`
(cited standards). The hose-barb profile is a study proportion, not a cited standard: the
barb is finished against the hose supplier print before fabrication (the hoses are
catalogue items, `tables/materials.csv` HOSE_CHEM and HOSE_UTIL rows).

Run with the CadQuery interpreter ($CADQUERY_PYTHON). Solids are in millimetres.
"""
from math import cos, pi, sin

import cadquery as cq

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import dn, step_export

# Shared nozzle-layout constants (F-20261110-09): named, cited values the unit builders
# share instead of inline literals. Both are study layout choices of the CRYO_ASU nozzle
# row spread (2026-11-10 argon rows), kept here so every builder that spreads overflow
# nozzle rows across bed or rack footprints uses the same step and the same edge keep-out.
NOZZLE_ROW_STEP_MM = 90.0    # axial step between overflow nozzle rows on one bed/rack face
BED_EDGE_CLEAR_MM = 30.0     # minimum root keep-out from a bed or rack edge (mm)


def stub(dn_label, length, sch=40, bore_open=True):
    """A plain pipe stub along +Z from the origin plane: set-in weld at z 0, free end up.

    The wall follows the schedule table; the bore is open at both ends so a stub unions
    into a shell without trapping an internal face.
    """
    od, wall = dn.pipe_od(dn_label), dn.pipe_wall(dn_label, sch)
    s = cq.Workplane('XY').circle(od / 2).circle(od / 2 - wall).extrude(length)
    if bore_open:
        s = s.union(cq.Workplane('XY').circle(od / 2 - wall).extrude(length))
    return s


def flange_stub(dn_label, length, sch=40, rating=150):
    """A pipe stub with a Class 150 raised-face flange at the free end (z = length).

    The flange is the B16.5 Class 150 disc: outside diameter, thickness with the 1.6 mm
    raised face on top, and the standard bolt-hole circle and holes. `rating` accepts
    150 only; a joint at any other rating is a named hold in the calling model, not a
    dimension invented here.
    """
    if rating != 150:
        raise ValueError(f'no flange table for Class {rating}; carry it as a named hold')
    f = dn.flange(dn_label)
    od, wall = dn.pipe_od(dn_label), dn.pipe_wall(dn_label, sch)
    disc = (cq.Workplane('XY', origin=(0, 0, length - f['t']))
            .circle(f['od'] / 2).extrude(f['t'] - dn.RF_HEIGHT))
    face = (cq.Workplane('XY', origin=(0, 0, length - dn.RF_HEIGHT))
            .circle(f['rf'] / 2).extrude(dn.RF_HEIGHT))
    s = disc.union(face)
    s = s.union(cq.Workplane('XY').circle(od / 2).extrude(length))
    s = s.cut(cq.Workplane('XY').circle(od / 2 - wall).extrude(length))
    for i in range(f['n_bolts']):
        a = 2 * pi * i / f['n_bolts'] + pi / f['n_bolts']
        x, y = f['bc'] / 2 * cos(a), f['bc'] / 2 * sin(a)
        s = s.cut(cq.Workplane('XY', origin=(x, y, length - f['t']))
                  .circle(f['hole'] / 2).extrude(f['t']))
    return s


def hose_barb(hose_id_mm, length, root_od=None, major_mm=None, ridges=3, sch=40):
    """A hose barb along +Z from the origin plane, ridges up, plain shank at the base.

    The shank follows the DN pipe table so the barb mounts like any other DN15-DN50 stub;
    pass `dn` shank size via `root_od` override if the mount differs. The barb profile is
    a study proportion: ridge major diameter defaults to the hose bore plus 1.5 mm of
    interference per side pair, valley to major minus 1.5 mm. Confirm against the hose
    supplier print before fabrication.
    """
    if major_mm is None:
        major_mm = hose_id_mm + 1.5
    if root_od is None:
        root_od = dn.pipe_od('DN15')
    valley = major_mm - 1.5
    step = (length - 10.0) / max(ridges, 1)
    s = cq.Workplane('XY').circle(root_od / 2).extrude(10.0)          # mounting shank
    z = 10.0
    for i in range(max(ridges, 1)):
        z_ridge = 10.0 + (i + 1) * step
        s = s.union(cq.Workplane('XY', origin=(0, 0, z)).circle(valley / 2)
                    .workplane(offset=z_ridge - z).circle(major_mm / 2).loft(ruled=True))
        z = z_ridge
    s = s.union(cq.Workplane('XY', origin=(0, 0, z)).circle(valley / 2).extrude(2.0))
    return s


def place_on_face(solid, face, height, center_xy, envelope_xyz, outside=False):
    """Move a +Z stub onto a vessel face: 'top', 'bottom', '+X', '-X', '+Y', '-Y'.

    Default: the stub ends flush at the envelope face (the house idiom: hardware stays
    inside the claimed envelope, so the build keeps the bounding box the graph states).
    With `outside=True` the stub root sits on the face and the stub extends outward, for
    assemblies whose declared size includes the nozzle stick-out. `height` is the nozzle
    centreline height on side faces (the duty schedule height_mm) and is ignored for top
    and bottom. `center_xy` is the (x, y) of the vessel axis; `envelope_xyz` is the
    (L, W, H) envelope.
    """
    L, W, H = envelope_xyz
    x, y = center_xy
    bb = solid.val().BoundingBox()
    if face == 'top':
        return solid.translate((x, y, (H - bb.zlen) if not outside else H))
    if face == 'bottom':
        z = bb.zlen if not outside else -bb.zlen
        return solid.rotate((0, 0, 0), (1, 0, 0), 180).translate((x, y, z))
    # side faces: rotate first, then offset by the rotated extent, so `not outside`
    # really ends flush at the face (the pre-rotation bbox y/x extent is the stub
    # diameter, not its length).
    rot = {'+X': solid.rotate((0, 0, 0), (0, 1, 0), 90),
           '-X': solid.rotate((0, 0, 0), (0, 1, 0), -90),
           '+Y': solid.rotate((0, 0, 0), (1, 0, 0), -90),
           '-Y': solid.rotate((0, 0, 0), (1, 0, 0), 90)}[face]
    rb = rot.val().BoundingBox()
    if face == '+X':
        return rot.translate(((L - rb.xlen) if not outside else L, y, height))
    if face == '-X':
        return rot.translate((rb.xlen if not outside else -rb.xlen, y, height))
    if face == '+Y':
        return rot.translate((x, (W - rb.ylen) if not outside else W, height))
    return rot.translate((x, rb.ylen if not outside else -rb.ylen, height))
