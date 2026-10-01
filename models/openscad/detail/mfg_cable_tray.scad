// Ladder tray + grounding ring. Tray is not a gas header.
// DC bus and 480 V stay outside both process atmospheres.
include <../params.scad>;
$fn = 16;

TRAY_W = 300;
TRAY_H = 100;
RUNG   = 400;

module ladder(len) {
    cube([len, 8, TRAY_H]);
    translate([0, TRAY_W - 8, 0]) cube([len, 8, TRAY_H]);
    for (x = [0:RUNG:len-20])
        translate([x, 0, TRAY_H - 12]) cube([20, TRAY_W, 12]);
}

module rod(h=2500) {
    cylinder(h=h, d=16);
    translate([0, 0, -400]) cylinder(h=400, d=20); // below grade
}

module ring_bar(l) { cube([l, 30, 6]); }

module mfg_cable_tray() {
    // aisle back-side tray: rectifier → EW hangers, 2.4 m
    translate([0, 0, 2400]) ladder(9*EW_PITCH + 800);
    // drop to rectifier yard (−X)
    translate([0, TRAY_W, 2400])
        rotate([0, 0, 90]) ladder(1800);
    // 480 V tray, electrical yard only
    translate([-2000, 1600, 2400]) ladder(2400);

    // ground ring around CSTR + aisle footprint
    translate([-200, -200, 50]) ring_bar(CSTR_L + 9*EW_PITCH + 800);
    translate([-200, CSTR_W + 400, 50]) ring_bar(CSTR_L + 600);
    translate([-200, -200, 50]) rotate([0, 0, 90]) ring_bar(CSTR_W + 600);
    translate([CSTR_L + 400, -200, 50]) rotate([0, 0, 90]) ring_bar(CSTR_W + 600);

    translate([-200, -200, 50]) rod();
    translate([CSTR_L + 400, -200, 50]) rod();
    translate([-200, CSTR_W + 400, 50]) rod();
    translate([CSTR_L + 400, CSTR_W + 400, 50]) rod();
    // extra rod at rectifier
    translate([-2200, 1600, 50]) rod();
}

mfg_cable_tray();
