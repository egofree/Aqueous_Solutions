// 5.6 MELT — induction or oil-gas fired pot. Fuel from OIL LINE / afterburner gas.
include <../params.scad>;
$fn = 32;

module mfg_melt() {
    difference() {
        cube([800, 800, 1200]);
        translate([40, 40, 80]) cube([720, 720, 1120]);
    }
    translate([400, 400, 80])
        difference() {
            cylinder(h=700, d=500);
            translate([0, 0, 20]) cylinder(h=700, d=420);
        }
}
mfg_melt();
