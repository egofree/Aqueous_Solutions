// FLOAT / SINK DEWATER — vibratory perforated trough.
// Wetted: CPVC deck and pan. Liquor is Salria. Return DN40 PVDF to CSTR 1.
// Not a screen on the shred conveyor. Instance with FDEW_* or SDEW_*.
include <../params.scad>;
$fn = 24;

// Lee Spring / McMaster family isolator (same as shred conveyor)
SPR_D = CONV_SPRING_D;
SPR_H = CONV_SPRING_H;

module dew_deck(len, w, h) {
    t = 8;
    difference() {
        cube([len, w, h]);
        translate([t, t, t]) cube([len - 2*t, w - 2*t, h]);
        // 12 mm holes, 40 mm pitch, open area ~7 %
        for (x = [30:40:len-30])
            for (y = [30:40:w-30])
                translate([x, y, -1]) cylinder(h=t+2, d=12);
    }
    // top flanges
    translate([0, -40, h-8]) cube([len, 40, 8]);
    translate([0, w, h-8]) cube([len, 40, 8]);
}

module dew_pan(w) {
    difference() {
        translate([-60, 10, -70]) cube([280, w-20, 60]);
        translate([-48, 22, -58]) cube([256, w-44, 56]);
    }
    // DN40 PVDF return, slope toward CSTR
    translate([80, w/2, -70])
        rotate([90, 0, 20])
            difference() {
                cylinder(h=220, d=50);
                translate([0, 0, -1]) cylinder(h=222, d=40);
            }
}

module dew_cover(len, w, h) {
    difference() {
        translate([-4, -4, h]) cube([len+8, w+8, 6]);
        translate([len*0.3, w/2, h-1]) cylinder(h=10, d=40); // mist tap
    }
}

module dew_vibrator(len, w) {
    // OLI / Invicta MVE 200/3 class, 0.15 kW
    translate([len*0.4, w+50, 40])
        rotate([90, 0, 0]) cylinder(h=160, d=120);
}

module dew_springs(len, w) {
    for (x = [80, len/3, 2*len/3, len-80])
        for (ys = [-30, w+30])
            translate([x, ys, -SPR_H-70]) {
                cylinder(h=8, d=SPR_D+16);
                translate([0, 0, 8]) cylinder(h=SPR_H, d=SPR_D);
            }
}

module mfg_dewater(len=FDEW_L, w=FDEW_W, h=FDEW_H) {
    dew_deck(len, w, h);
    dew_pan(w);
    dew_cover(len, w, h);
    dew_vibrator(len, w);
    dew_springs(len, w);
}

mfg_dewater();
