// 5.4 / 5.5 Totes, CRU box, SALT FEED, metal bins. PP NaOH, CPVC HCl.
include <../params.scad>;
$fn = 24;

module tote(name_h=TOTE_H) {
    difference() {
        cube([TOTE_L, TOTE_W, name_h]);
        translate([12, 12, 12]) cube([TOTE_L-24, TOTE_W-24, name_h]);
    }
    translate([TOTE_L/2, TOTE_W/2, name_h]) cylinder(h=40, d=80);
}

module bin() {
    difference() {
        cube([170, 300, 400]);
        translate([6, 6, 6]) cube([158, 288, 400]);
    }
}

tote();
translate([TOTE_L + 80, 0, 0]) tote();
translate([0, TOTE_W + 80, 0]) bin();
