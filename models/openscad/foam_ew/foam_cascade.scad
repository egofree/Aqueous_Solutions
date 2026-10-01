// Assembled 1:3 foam-board EW cascade. Operator OpenSCAD.
// Flat patterns and nest come from generate.py, not from this file.
include <params.scad>;

module wall_box() {
    difference() {
        cube([OD_L, OD_W, T + ID_H]);
        translate([T, T, T]) cube([ID_L, ID_W, ID_H + 1]);
        // overflow notch +X, cathode side of mid
        translate([OD_L - T - 1, T + ID_W*0.55, T + ID_H - 25])
            cube([T + 2, ID_W*0.30, 26]);
        // CEM slot
        translate([T + 10, T + ID_W/2 - SLOT/2, T])
            cube([ID_L - 20, SLOT, ID_H + 1]);
    }
}

module funnel() {
    top_l = OD_L; top_w = OD_W; bot = THROAT + 2*T;
    difference() {
        hull() {
            cube([top_l, top_w, 1]);
            translate([(top_l-bot)/2, (top_w-bot)/2, -FUNNEL_H])
                cube([bot, bot, 1]);
        }
        hull() {
            translate([T, T, 1.05]) cube([ID_L, ID_W, 1]);
            translate([(top_l-THROAT)/2, (top_w-THROAT)/2, -FUNNEL_H-1])
                cube([THROAT, THROAT, 1]);
        }
    }
}

module rib() {
    cube([ID_L - 20, T, ID_H - 20]);
}

module cell() {
    color("#f4f1ea") wall_box();
    color("#e7e2d6") funnel();
    color("#93c5fd")
        translate([T + 10, T + ID_W/2 - SLOT/2 - T, T + 10]) rib();
    color("#fdba74")
        translate([T + 10, T + ID_W/2 + SLOT/2, T + 10]) rib();
}

module bund() {
    L = N_CELLS * PITCH + 2*T;
    W = AISLE_W + 2*T;
    difference() {
        cube([L, W, T + BUND_H]);
        translate([T, T, T]) cube([L - 2*T, W - 2*T, BUND_H + 1]);
    }
}

AISLE_W = OD_W + 2*BUND_PAD;

translate([-T, -BUND_PAD - T, -FUNNEL_H - T - BUND_H])
    color("#d6d3d1") bund();

for (i = [0:N_CELLS-1])
    translate([i * PITCH, 0, 0]) cell();
