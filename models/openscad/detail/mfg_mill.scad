// MILL jar + media.
include <../params.scad>;
$fn = 32;
module mfg_mill() {
    difference() {
        cube([MILL_L, 600, 900]);
        translate([12, 12, 12]) cube([MILL_L-24, 576, 880]);
    }
    translate([MILL_L/2, 300, 400]) rotate([0, 90, 0])
        difference() { cylinder(h=240, d=350, center=true); }
}
mfg_mill();
