// 8.4 RECTIFIER, ATS, SOL-ARK, ZnBr2 stack + tanks + Br2 scrubber.
include <../params.scad>;
$fn = 24;

module cabinet(l, w, h) {
    difference() {
        cube([l, w, h]);
        translate([20, 20, 40]) cube([l-40, w-40, h-60]);
    }
}

module mfg_electrical() {
    cabinet(RECT_L, RECT_W, RECT_H);
    translate([RECT_L + 100, 0, 0]) cabinet(600, RECT_W, 1600);
    translate([RECT_L + 800, 0, 0]) cabinet(SOLARK_L, SOLARK_W, SOLARK_H);
    translate([0, RECT_W + 200, 0]) {
        cabinet(ZNBR_L, ZNBR_W, ZNBR_H);
        translate([0, ZNBR_W + 80, 0])
            difference() {
                cube([700, 700, 1200]);
                translate([12, 12, 12]) cube([676, 676, 1180]);
            }
        translate([800, ZNBR_W + 80, 0])
            difference() {
                cube([700, 700, 1200]);
                translate([12, 12, 12]) cube([676, 676, 1180]);
            }
        translate([ZNBR_L + 80, 0, 0])
            difference() {
                cube([500, 500, 1400]);
                translate([12, 12, 12]) cube([476, 476, 1380]);
            }
    }
}
mfg_electrical();
