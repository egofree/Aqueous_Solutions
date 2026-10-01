// NaOH DIGEST + stuffing box + HDR_CAUSTIC vent.
include <../params.scad>;
$fn = 24;
module mfg_digest() {
    difference() {
        cube([DIGEST_L, DIGEST_W, DIGEST_H]);
        translate([WALL, WALL, WALL]) cube([DIGEST_L-2*WALL, DIGEST_W-2*WALL, DIGEST_H]);
    }
    translate([DIGEST_L/2, DIGEST_W/2, WALL]) union() {
        cylinder(h=DIGEST_H + 200, d=40);
        for (z = [200, 600, 1000])
            translate([0, 0, z]) cube([DIGEST_L*0.5, 10, 40], center=true);
        translate([0, 0, DIGEST_H + 40]) cylinder(h=80, d=100);
    }
    translate([DIGEST_L-20, DIGEST_W/2, DIGEST_H-120]) rotate([0, 90, 0]) cylinder(h=80, d=40);
    translate([DIGEST_L*0.3, DIGEST_W/2, DIGEST_H]) cylinder(h=80, d=66);
}
mfg_digest();
