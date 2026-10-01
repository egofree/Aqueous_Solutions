// HARVEST VDF + vacuum pump + cloth wrap. Shared drum for manual mode.
include <../params.scad>;
$fn = 32;

module mfg_harvest_vdf() {
    difference() {
        rotate([0, 90, 0]) cylinder(h=VDF_L, d=VDF_D);
        rotate([0, 90, 0]) translate([0, 0, 12])
            cylinder(h=VDF_L - 24, d=VDF_D - 24);
    }
    rotate([0, 90, 0])
        difference() {
            cylinder(h=VDF_L, d=VDF_D + 8);
            translate([0, 0, -1]) cylinder(h=VDF_L+2, d=VDF_D);
        }
    translate([0, -VDF_D/2 - 20, -VDF_D/4])
        cube([VDF_L, VDF_D + 40, 20]);
    translate([VDF_L/2, 0, VDF_D/2]) cylinder(h=160, d=60);
    translate([VDF_L + 80, -200, 0]) cube([400, 300, 350]);
    translate([VDF_L + 80, -50, 200]) rotate([0, -90, 0]) cylinder(h=80, d=50);
}

module mfg_pail() {
    difference() {
        cube([PAIL_W, PAIL_W, PAIL_W]);
        translate([6, 6, 6]) cube([PAIL_W-12, PAIL_W-12, PAIL_W]);
    }
}

mfg_harvest_vdf();
translate([VDF_L + 100, 400, 0]) mfg_pail();
