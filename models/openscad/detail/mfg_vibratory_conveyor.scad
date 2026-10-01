// VIBRATORY CONVEYOR shred → lid slot.
// Dry-ish feed: CS frame, UHMW liner. No screen. Dust hood DN150 → HDR_DUST (suction).
include <../params.scad>;
$fn = 24;

module trough(len) {
    w = CONV_W; h = CONV_H; t = CONV_PLATE;
    difference() {
        union() {
            translate([0, -w/2 - t, -t]) cube([len, w + 2*t, t]);
            translate([0, -w/2 - t, -t]) cube([len, t, h + t]);
            translate([0, w/2, -t]) cube([len, t, h + t]);
            translate([0, -w/2 - t - CONV_FLANGE, h - t])
                cube([len, CONV_FLANGE, t]);
            translate([0, w/2 + t, h - t])
                cube([len, CONV_FLANGE, t]);
        }
        for (x = [40:150:len-40]) {
            translate([x, -w/2 - t - CONV_FLANGE/2, h - t - 1])
                cylinder(h=t+2, d=CONV_BOLT);
            translate([x, w/2 + t + CONV_FLANGE/2, h - t - 1])
                cylinder(h=t+2, d=CONV_BOLT);
        }
    }
}

module liner(len) {
    translate([2, -CONV_W/2 + 1, 0.5])
        cube([len - 4, CONV_W - 2, 8]);
}

module inlet_chute() {
    difference() {
        translate([-120, -SHRED_W/2, 0])
            cube([120, SHRED_W, SHRED_H*0.4]);
        translate([-110, -SHRED_W/2 + 10, 10])
            cube([110, SHRED_W - 20, SHRED_H*0.4]);
    }
}

module discharge_spout(len) {
    difference() {
        translate([len - 20, -DROP_W/2 - 10, -40])
            cube([80, DROP_W + 20, CONV_H + 50]);
        translate([len - 15, -DROP_W/2, -35])
            cube([70, DROP_W, CONV_H + 60]);
    }
}

module spring_isolator() {
    union() {
        cylinder(h=8, d=CONV_SPRING_D + 16);
        translate([0, 0, 8]) cylinder(h=CONV_SPRING_H, d=CONV_SPRING_D);
        translate([0, 0, 8 + CONV_SPRING_H])
            cylinder(h=8, d=CONV_SPRING_D + 16);
        translate([0, 0, -20]) cylinder(h=20, d=16);
    }
}

module frame(len) {
    union() {
        translate([0, -CONV_W/2 - 80, -CONV_SPRING_H - 40])
            cube([len, 50, 8]);
        translate([0, CONV_W/2 + 30, -CONV_SPRING_H - 40])
            cube([len, 50, 8]);
        for (x = [80, len - 80])
            for (ys = [-CONV_W/2 - 55, CONV_W/2 + 55])
                translate([x, ys, -CONV_SPRING_H - 200])
                    cube([40, 40, 160]);
    }
}

module drive_motor(len) {
    // OLI MVE 200/3 class unbalanced motor
    translate([len*0.35, CONV_W/2 + CONV_PLATE + 10, 20])
        union() {
            rotate([90, 0, 0]) cylinder(h=180, d=140);
            translate([0, -20, 0])
                rotate([90, 0, 0]) cylinder(h=20, d=90);
        }
}

module dust_hood(len) {
    // suction to HDR_DUST. Header is negative. Do not tee into acid-gas.
    difference() {
        translate([len*0.15, -CONV_W/2 - 20, CONV_H])
            cube([len*0.5, CONV_W + 40, 80]);
        translate([len*0.15 + 8, -CONV_W/2 - 8, CONV_H - 1])
            cube([len*0.5 - 16, CONV_W + 16, 70]);
    }
    translate([len*0.4, 0, CONV_H + 80])
        difference() {
            cylinder(h=100, d=DUST_D + 12);
            translate([0, 0, -1]) cylinder(h=102, d=DUST_D);
        }
}

module mfg_vibratory_conveyor(len=CONV_LEN) {
    trough(len);
    liner(len);
    inlet_chute();
    discharge_spout(len);
    frame(len);
    drive_motor(len);
    dust_hood(len);
    for (x = [100, len/3, 2*len/3, len - 100])
        for (ys = [-CONV_W/2 - 40, CONV_W/2 + 40])
            translate([x, ys, -CONV_SPRING_H - 8])
                spring_isolator();
}

mfg_vibratory_conveyor();
