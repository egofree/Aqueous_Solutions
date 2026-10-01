// QUENCH — sprays, coil, NCG knockout to AFTERBURNER.
include <../params.scad>;
$fn = 24;
module mfg_quench() {
    difference() {
        cube([800, DRYER_W, 1200]);
        translate([12, 12, 12]) cube([776, DRYER_W-24, 1180]);
    }
    for (y = [80:120:DRYER_W-80])
        translate([200, y, 1000]) rotate([90, 0, 0]) cylinder(h=20, d=18);
    translate([100, DRYER_W/2, 200]) rotate([0, 90, 0]) cylinder(h=600, d=40);
    translate([400, DRYER_W/2, 1200])
        difference() { cylinder(h=200, d=80); translate([0,0,-1]) cylinder(h=202, d=60); }
    translate([80, DRYER_W/2, 40]) rotate([0, 90, 0]) cylinder(h=80, d=50);
    translate([900, DRYER_W/2, 0])
        difference() { cylinder(h=900, d=400); translate([0,0,12]) cylinder(h=880, d=376); }
}
mfg_quench();
