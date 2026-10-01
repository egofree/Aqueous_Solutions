// Funnel-bottom EW / PK cell. A | CEM | C. Instance along +X.
include <params.scad>;

module ew_body() {
    t = WALL;
    l = EW_L; w = EW_W; h = EW_H;
    difference() {
        cube([l + 2*t, w + 2*t, h + t]);
        translate([t, t, t])
            cube([l, w, h + 1]);
    }
}

module ew_funnel() {
    t = WALL;
    top_l = EW_L + 2*t;
    top_w = EW_W + 2*t;
    bot = EW_VALVE_D + 2*t;
    // outer funnel
    difference() {
        hull() {
            translate([0, 0, 0])
                cube([top_l, top_w, 1]);
            translate([(top_l - bot)/2, (top_w - bot)/2, -EW_FUNNEL_H])
                cube([bot, bot, 1]);
        }
        hull() {
            translate([t, t, 1.05])
                cube([EW_L, EW_W, 1]);
            translate([(top_l - EW_VALVE_D)/2, (top_w - EW_VALVE_D)/2, -EW_FUNNEL_H + 1])
                cube([EW_VALVE_D, EW_VALVE_D, 1]);
        }
    }
    // valve stub
    translate([top_l/2, top_w/2, -EW_FUNNEL_H - EW_VALVE_L])
        difference() {
            cylinder(h=EW_VALVE_L + 2, d=EW_VALVE_D + 2*t);
            translate([0, 0, -1])
                cylinder(h=EW_VALVE_L + 4, d=EW_VALVE_D);
        }
}

module cem_cassette() {
    // slot on the Y mid-plane (A toward -Y, C toward +Y)
    t = WALL;
    x = t + 8;
    y = t + EW_W/2 - EW_SLOT/2;
    translate([x, y, t + 20])
        cube([EW_L - 16, EW_SLOT, EW_H - 40]);
    // CEM plate in the slot
    color("steelblue")
    translate([x + 2, y + (EW_SLOT - EW_MEM_T)/2, t + 24])
        cube([EW_L - 20, EW_MEM_T, EW_H - 50]);
}

module overflow_weir() {
    // liquor overflows +X wall into the next cell
    t = WALL;
    translate([t + EW_L - 1, t + EW_W*0.55, t + EW_H - 70])
        cube([t + 2, EW_W*0.30, 80]);
}

module ew_cell() {
    color("whitesmoke")
    difference() {
        union() {
            translate([0, 0, 0]) ew_body();
            ew_funnel();
        }
        overflow_weir();
        // cassette pocket through the floor of the body so the plate seats
        translate([WALL + 8, WALL + EW_W/2 - EW_SLOT/2, WALL - 1])
            cube([EW_L - 16, EW_SLOT, EW_H]);
    }
    cem_cassette();
}

ew_cell();
