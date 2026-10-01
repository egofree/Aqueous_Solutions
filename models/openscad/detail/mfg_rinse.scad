// 7.1 RINSE + DEWATER. Liquor to SALT FEED, not sewer.
include <../params.scad>;
$fn = 24;

module mfg_rinse() {
    difference() {
        cube([RINSE_L, 600, 800]);
        translate([10, 10, 10]) cube([RINSE_L-20, 580, 800]);
    }
    translate([40, 300, 0])
        rotate([90, 0, 0]) cylinder(h=100, d=PUMP_D);
}
mfg_rinse();
