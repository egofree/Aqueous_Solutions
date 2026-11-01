# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""Pipe, flange and bolting dimension tables for nozzle hardware DN15 to DN50.

Sources. Outside diameters follow the house table already used by every built model
(`models/mfg/style_builders.py`, DN_OD: the EN-rounded millimetre series 21.3, 26.9, 33.7,
42.4, 48.3, 60.3). Wall thicknesses are ASME B36.19M schedule 10S and ASME B36.10M
schedule 40 millimetre values (the ASME outside-diameter equivalents of the EN series are
26.7, 33.4 and 42.2 at DN20, DN25 and DN32; the difference is in the nominal label, not
the hardware a schedule selection buys). Flange dimensions are ASME B16.5 Class 150
(weld-neck table): flange outside diameter, thickness (raised face included), bolt circle,
bolt count, bolt size, bolt-hole diameter and raised-face diameter. The Class 150 raised
face is 1.6 mm and is included in the tabulated thickness.

These are cited standard dimensions, not design results. A nozzle that carries a stated
process pressure is rated per AQS-STD-001 (110 % rule) by the calling model; this module
only carries the hardware geometry.
"""

# DN -> (od_mm, wall_sch10s_mm, wall_sch40_mm). ASME B36.19M-2004/B36.10M tables.
PIPE = {
    'DN15': (21.3, 2.11, 2.77),
    'DN20': (26.9, 2.11, 2.87),
    'DN25': (33.7, 2.77, 3.38),
    'DN32': (42.4, 2.77, 3.56),
    'DN40': (48.3, 2.77, 3.68),
    'DN50': (60.3, 2.77, 3.91),
}

# DN -> flange data, ASME B16.5 Class 150 (dimensions in mm; raised face included in
# thickness). Bolts are counted in inches on the standard: 1/2 in UNC at DN15-DN40,
# 5/8 in UNC at DN50; the tabulated millimetre bolt size is the conversion.
FLANGE_150 = {
    'DN15': dict(od=88.9, t=11.2, bc=60.3, n_bolts=4, bolt='M12 (1/2 in)', hole=15.9, rf=34.9),
    'DN20': dict(od=98.6, t=12.7, bc=69.9, n_bolts=4, bolt='M12 (1/2 in)', hole=15.9, rf=42.9),
    'DN25': dict(od=108.0, t=14.3, bc=79.4, n_bolts=4, bolt='M12 (1/2 in)', hole=15.9, rf=50.8),
    'DN32': dict(od=117.5, t=15.9, bc=88.9, n_bolts=4, bolt='M12 (1/2 in)', hole=15.9, rf=63.5),
    'DN40': dict(od=127.0, t=17.5, bc=98.6, n_bolts=4, bolt='M12 (1/2 in)', hole=15.9, rf=73.0),
    'DN50': dict(od=152.4, t=19.1, bc=120.7, n_bolts=4, bolt='M16 (5/8 in)', hole=19.1, rf=92.1),
}

RF_HEIGHT = 1.6   # Class 150 raised face, included in the tabulated thickness (B16.5)


def pipe(dn):
    """Return (od_mm, wall_mm) for a DN label at a schedule; sch is 10 or 40."""
    return PIPE[dn]


def pipe_od(dn):
    """Outside diameter in mm for a DN label in the house table."""
    return PIPE[dn][0]


def pipe_wall(dn, sch=40):
    """Wall thickness in mm: schedule 10 (10S) or 40 (40)."""
    return PIPE[dn][1 if sch == 10 else 2]


def flange(dn):
    """ASME B16.5 Class 150 flange dimension dict for a DN label."""
    return dict(FLANGE_150[dn])
