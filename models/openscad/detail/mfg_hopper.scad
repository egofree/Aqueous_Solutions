// 1.1 HOPPER — pyramid, flanged outlet to shredder. No screen.
include <../params.scad>;
$fn = 24;
t = 6;

module mfg_hopper() {
    difference() {
        hull() {
            translate([-HOPPER_L/2, -HOPPER_W/2, HOPPER_H])
                cube([HOPPER_L, HOPPER_W, t]);
            translate([-SHRED_L/2 - t, -SHRED_W/2 - t, 0])
                cube([SHRED_L + 2*t, SHRED_W + 2*t, t]);
        }
        hull() {
            translate([-HOPPER_L/2 + t, -HOPPER_W/2 + t, HOPPER_H + 1])
                cube([HOPPER_L - 2*t, HOPPER_W - 2*t, 1]);
            translate([-SHRED_L/2, -SHRED_W/2, -1])
                cube([SHRED_L, SHRED_W, t + 2]);
        }
    }
    // outlet flange
    difference() {
        translate([-SHRED_L/2 - 30, -SHRED_W/2 - 30, -12])
            cube([SHRED_L + 60, SHRED_W + 60, 12]);
        translate([-SHRED_L/2, -SHRED_W/2, -13])
            cube([SHRED_L, SHRED_W, 14]);
        for (x = [-SHRED_L/2 - 15, SHRED_L/2 + 15])
            for (y = [-SHRED_W/2 - 15, SHRED_W/2 + 15])
                translate([x, y, -13]) cylinder(h=14, d=12);
    }
}
mfg_hopper();
