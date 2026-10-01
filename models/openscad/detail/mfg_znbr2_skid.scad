// ZnBr2 yard skid: zinc tank (PP), bromine tank (PVDF), stack envelope,
// Br2 packed tower. Own liquor. Shared BMED NaOH supply only.
include <../params.scad>;
$fn = 28;

module tank(l, w, h) {
    difference() {
        cube([l, w, h]);
        translate([12, 12, 12]) cube([l-24, w-24, h]);
    }
}

module br2_tower() {
    difference() {
        cylinder(h=1500, d=200);
        translate([0, 0, 12]) cylinder(h=1480, d=176);
    }
    for (z = [200:200:1200])
        translate([0, 0, z])
            difference() {
                cylinder(h=8, d=170);
                cylinder(h=8, d=40);
            }
}

module mfg_znbr2_skid() {
    tank(700, 700, 1200);                 // zinc PP
    translate([800, 0, 0]) tank(700, 700, 1200); // bromine PVDF
    translate([0, 800, 0]) cube([ZNBR_L, ZNBR_W-800, ZNBR_H]); // stack mass
    translate([1700, 350, 0]) br2_tower();
    translate([400, 350, 1200]) cylinder(h=80, d=60); // vent zinc → H2
    translate([1150, 350, 1200]) cylinder(h=80, d=60); // vent Br → tower
}

mfg_znbr2_skid();
