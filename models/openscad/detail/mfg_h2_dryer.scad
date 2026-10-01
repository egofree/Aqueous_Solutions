// 8.3 H2_DRYER + stack. Not tied to oil vapor.
include <../params.scad>;
$fn = 32;

module mfg_h2_dryer() {
    difference() {
        cube([700, 500, 900]);
        translate([12, 12, 12]) cube([676, 476, 880]);
    }
    translate([900, 250, 0])
        difference() {
            cylinder(h=2400, d=250);
            translate([0, 0, -1]) cylinder(h=2402, d=220);
        }
}
mfg_h2_dryer();
