// 1.2 SHREDDER — dual-shaft cutters, drive, dust hood DN150.
include <../params.scad>;
$fn = 24;
t = 8;

module cutter(d=180, n=8, thk=20) {
    union() {
        cylinder(h=thk, d=40);
        for (i = [0:n-1])
            rotate([0, 0, i*360/n])
                translate([0, -8, 0])
                    cube([d/2, 16, thk]);
    }
}

module mfg_shredder() {
    // box
    difference() {
        cube([SHRED_L, SHRED_W, SHRED_H]);
        translate([t, t, t])
            cube([SHRED_L - 2*t, SHRED_W - 2*t, SHRED_H]);
        // inlet
        translate([SHRED_L*0.15, SHRED_W*0.15, SHRED_H - 1])
            cube([SHRED_L*0.7, SHRED_W*0.7, t + 2]);
        // outlet to conveyor
        translate([SHRED_L - 1, SHRED_W*0.25, 20])
            cube([t + 2, SHRED_W*0.5, 80]);
    }
    // two shafts + cutters
    for (y = [SHRED_W*0.35, SHRED_W*0.65]) {
        translate([30, y, SHRED_H*0.45])
            rotate([0, 90, 0])
                cylinder(h=SHRED_L - 60, d=36);
        for (x = [80:50:SHRED_L-80])
            translate([x, y, SHRED_H*0.45])
                rotate([0, 90, 0]) cutter();
    }
    // drive
    translate([-160, SHRED_W/2 - 80, 40])
        cube([150, 160, 160]);
    // dust hood + DN150
    difference() {
        translate([-20, -20, SHRED_H - 20])
            cube([SHRED_L + 40, SHRED_W + 40, 160]);
        translate([0, 0, SHRED_H - 21])
            cube([SHRED_L, SHRED_W, 140]);
    }
    translate([SHRED_L/2, SHRED_W/2, SHRED_H + 140])
        difference() {
            cylinder(h=80, d=DUST_D + 16);
            translate([0, 0, -1]) cylinder(h=82, d=DUST_D);
        }
}
mfg_shredder();
