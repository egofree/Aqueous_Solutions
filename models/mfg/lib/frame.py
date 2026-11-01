# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright 2026 Mike Matthews.
"""AQS-MOD-002 bay frame members and the load rule (frame standard for the shop).

The standard (`docs-authority/FRAME_SYSTEM.md`, AQS-MOD-002 Rev D) defines the parameter
set, not one size: L, W, H, tube section, wall, material class, carried process mass, and
the fixed interfaces. The weld pattern is fixed: four posts, top rectangle, bottom
rectangle, feet. One size is not the standard; a bay is built from the parameter set.

Load rule of the standard: design load is the process mass times 2; deflection limit is
L/240 on the top rails; a section that fails the limit goes up one size (the sizes in use
are ordered in SECTION_LADDER). The deflection check is the simply supported rail that
`models/freecad/frame.py` carries (E = 200 GPa steel); this module ports it to CadQuery
so a unit model in `models/mfg` can carry its own frame solid.

Interfaces, fixed (they do not scale): the power connector sits on the -X face 200 mm up;
the fluid couplers sit on the +X face 300 mm up; feet are 10 mm plate at the four
corners; the lift points are the top corners.

Run with the CadQuery interpreter ($CADQUERY_PYTHON). Solids are in millimetres.
"""
import cadquery as cq

# AQS-MOD-002 section 3: material by service class
SERVICE_MATERIAL = {
    'dry': 'ASTM A500',
    'wet': '316L tube',
    'hot': 'A500 (with a heat shield; the structure is not the crucible)',
    'cold': '316L',
    'farm': 'HDPE or painted A500 (no weld on HDPE; timber is allowed)',
    'clean': '6061 aluminium',
}

# AQS-MOD-002 section 4: sizes in use. (L, W, H, section, wall, service)
SIZES_IN_USE = [
    (1200, 600, 800, 100, 6, 'dry'),      # lathe, mill, welder bays
    (1400, 600, 800, 100, 6, 'wet'),      # EW-1, EW-2, EW-7, EW-9
    (800, 600, 800, 80, 5, 'wet'),        # EW-4 to EW-6, EW-8
    (1200, 600, 800, 100, 6, 'hot'),      # furnace, silicon
    (1200, 600, 800, 80, 5, 'clean'),     # aligner
    (600, 600, 800, 80, 5, 'cold'),       # cold-box base (tower is pipe, not this frame)
    (2000, 1000, 400, 80, 5, 'farm'),     # farm bed (HDPE rail)
]

# section mass, kg/m, square tube (AQS-MOD-002 section 5 and models/freecad/frame.py)
SECTION_MASS = {(80, 5): 11.0, (100, 6): 17.0, (120, 8): 27.0}

# the ladder the load rule climbs when a section fails the deflection limit
SECTION_LADDER = [(80, 5), (100, 6), (120, 8)]

POWER_CONNECTOR = ('-X', 200.0)   # face, mm up
FLUID_COUPLERS = ('+X', 300.0)    # face, mm up
FEET_T = 10.0                     # foot plate thickness


def deflection(L, section, wall, load_kg):
    """Simply supported top rail, one rail carrying the design load.

    Returns (deflection_mm, limit_mm, ok). I for a square tube; E = 200 GPa steel; the
    design load is the process mass times 2 (AQS-MOD-002 section 5).
    """
    E = 200000.0   # N/mm2
    outer, inner = float(section), float(section) - 2.0 * float(wall)
    I = (outer ** 4 - inner ** 4) / 12.0
    w = (2.0 * load_kg * 9810.0) / 1000.0   # design load x g, N, on one rail
    d = w * float(L) ** 3 / (48.0 * E * I)
    limit = float(L) / 240.0
    return d, limit, d <= limit


def section_for(L, load_kg, base=(100, 6)):
    """The section for a bay: the base machine-bay section (AQS-MOD-002 section 4) unless
    the design load pushes the top rail past L/240, when it goes up one ladder step."""
    ladder = SECTION_LADDER[SECTION_LADDER.index(base):] if base in SECTION_LADDER else SECTION_LADDER
    for section, wall in ladder:
        if deflection(L, section, wall, load_kg)[2]:
            return section, wall
    return SECTION_LADDER[-1]


def frame_members(L, W, H, section=100, wall=6):
    """The fixed weld pattern as one solid: four posts, top and bottom rectangles.

    The wall is recorded in the call, not cut. The result spans exactly L x W x H, so a
    frame solid pins a unit model to its envelope the way the plinth frames do.
    """
    posts = []
    for x in (0.0, L - section):
        for y in (0.0, W - section):
            posts.append(cq.Workplane('XY', origin=(x, y, 0)).box(section, section, H, centered=False))
    rails = []
    for z in (0.0, H - section):
        rails.append(cq.Workplane('XY', origin=(0, 0, z)).box(L, section, section, centered=False))
        rails.append(cq.Workplane('XY', origin=(0, W - section, z)).box(L, section, section, centered=False))
        rails.append(cq.Workplane('XY', origin=(0, 0, z)).box(section, W, section, centered=False))
        rails.append(cq.Workplane('XY', origin=(L - section, 0, z)).box(section, W, section, centered=False))
    body = posts[0]
    for s in posts[1:] + rails:
        body = body.union(s)
    return body


def feet(L, W, section=100):
    """Four 10 mm foot plates at the corners (fixed interface, does not scale)."""
    f = []
    for x, sx in ((0.0, 1.0), (L - section, -1.0)):
        for y, sy in ((0.0, 1.0), (W - section, -1.0)):
            f.append(cq.Workplane('XY', origin=(x, y, -FEET_T)).box(section, section, FEET_T, centered=False))
    return f


def interface_points(L, W, H, section=100):
    """The fixed interface positions: (power connector, fluid couplers) as (face, x, y, z)."""
    return {
        'power_connector': ('-X', 0.0, W / 2.0, POWER_CONNECTOR[1]),
        'fluid_couplers': ('+X', L, W / 2.0, FLUID_COUPLERS[1]),
        'lift_points': [(x, y, H) for x in (0.0, L) for y in (0.0, W)],
    }


def steel_mass(L, W, H, section=100, wall=6):
    """Frame steel mass in kg: tube length times the section mass (AQS-MOD-002 section 5)."""
    length = 4 * H + 4 * L + 4 * W   # mm of tube in the fixed pattern
    return SECTION_MASS.get((section, wall), 0.0) * length / 1000.0
