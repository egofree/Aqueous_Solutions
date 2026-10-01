// 2.1–2.6 LEACH CSTR 1 manufacturing: CPVC shell, weir, trough, mixer, pump.
// Floor auger flight is cstr3_flight.scad — instance separately.
include <../params.scad>;
$fn = 24;

module wall_panel(l, h) {
    difference() {
        cube([l, WALL, h]);
        for (x = [40:150:l-40]) {
            translate([x, -1, 40]) rotate([-90, 0, 0]) cylinder(h=WALL+2, d=10);
            translate([x, -1, h-40]) rotate([-90, 0, 0]) cylinder(h=WALL+2, d=10);
        }
    }
}

module mfg_cstr_shell() {
    // four walls + floor, cement-lap corners (overlap WALL)
    translate([0, 0, 0]) cube([CSTR_L + 2*WALL, CSTR_W + 2*WALL, FLOOR]);
    translate([0, 0, FLOOR]) wall_panel(CSTR_L + 2*WALL, CSTR_H);
    translate([0, CSTR_W + WALL, FLOOR]) wall_panel(CSTR_L + 2*WALL, CSTR_H);
    translate([0, WALL, FLOOR]) rotate([0, 0, 90]) wall_panel(CSTR_W, CSTR_H);
    translate([CSTR_L + 2*WALL, WALL, FLOOR]) rotate([0, 0, 90]) wall_panel(CSTR_W, CSTR_H);
}

module mfg_weir() {
    // adjustable crest plate + spout
    translate([CSTR_L + WALL - 4, WALL + (CSTR_W - WEIR_W)/2, FLOOR + WEIR_CREST])
        cube([WALL + 4, WEIR_W, WEIR_SLOT_H]);
    difference() {
        translate([CSTR_L + 2*WALL, WALL + (CSTR_W - WEIR_W)/2 - WALL,
                   FLOOR + WEIR_CREST - WALL])
            cube([WEIR_LIP, WEIR_W + 2*WALL, WEIR_SLOT_H + WALL + 20]);
        translate([CSTR_L + 2*WALL - 1, WALL + (CSTR_W - WEIR_W)/2,
                   FLOOR + WEIR_CREST])
            cube([WEIR_LIP + 2, WEIR_W, WEIR_SLOT_H + 40]);
    }
}

module mfg_auger_trough() {
    ty = WALL + AUGER_OFFSET_Y - AUGER_TROUGH_W/2;
    difference() {
        translate([WALL + 40, ty, FLOOR])
            cube([CSTR_L - 80, AUGER_TROUGH_W, AUGER_TROUGH_H]);
        translate([WALL + 39, ty + 12, FLOOR + 12])
            cube([CSTR_L - 78, AUGER_TROUGH_W - 24, AUGER_TROUGH_H]);
    }
}

module mfg_mixer() {
    translate([WALL + CSTR_L*0.55, WALL + CSTR_W*0.55, FLOOR + 80])
        union() {
            cylinder(h=CSTR_H + 200, d=36);
            for (z = [120, 400, 700])
                translate([0, 0, z]) cube([400, 12, 40], center=true);
            translate([0, 0, CSTR_H + 80])
                cylinder(h=80, d=90); // stuffing box
        }
}

module mfg_leachate_pump() {
    translate([-220, WALL + 900 - 90, FLOOR + 450 - 90])
        cube([180, 180, 180]);
    translate([0, WALL + 900, FLOOR + 450])
        rotate([0, 90, 0])
            difference() {
                cylinder(h=WALL + 180, d=PUMP_D + 16);
                translate([0, 0, -1]) cylinder(h=WALL + 182, d=PUMP_D);
            }
    translate([WALL, WALL + 900 - 70, FLOOR + 450 - 80])
        difference() {
            cube([STRAINER_L, STRAINER_W, STRAINER_H]);
            translate([12, 12, 12])
                cube([STRAINER_L - 16, STRAINER_W - 24, STRAINER_H - 24]);
        }
}

module mfg_lid() {
    difference() {
        cube([CSTR_L + 2*WALL, CSTR_W + 2*WALL, WALL]);
        translate([WALL + DROP_X, WALL + (CSTR_W - DROP_W)/2, -1])
            cube([DROP_L, DROP_W, WALL + 2]);
        translate([WALL + CSTR_L*0.55, WALL + CSTR_W*0.55, -1])
            cylinder(h=WALL + 2, d=MIXER_D);
        translate([WALL + CSTR_L*0.80, WALL + CSTR_W*0.20, -1])
            cylinder(h=WALL + 2, d=GAS_D);
    }
}

module nozzle(d, l=80) {
    difference() {
        cylinder(h=l, d=d+16);
        translate([0, 0, -1]) cylinder(h=l+2, d=d);
    }
}

module mfg_nozzles() {
    // N5 REGEN LEACH DN40 on +Y
    translate([WALL + CSTR_L*0.20, CSTR_W + 2*WALL, FLOOR + 900])
        rotate([-90, 0, 0]) nozzle(40, 70);
    // N6a / N6b HX-5 on −Y
    translate([WALL + CSTR_L*0.70, 0, FLOOR + 300])
        rotate([90, 0, 0]) nozzle(25, 70);
    translate([WALL + CSTR_L*0.70, 0, FLOOR + 1100])
        rotate([90, 0, 0]) nozzle(25, 70);
    // N8 returns on +X near floor
    translate([CSTR_L + 2*WALL, WALL + (CSTR_W - WEIR_W)/2, FLOOR + 200])
        rotate([0, 90, 0]) nozzle(40, 70);
    translate([CSTR_L + 2*WALL, WALL + AUGER_OFFSET_Y, FLOOR + 200])
        rotate([0, 90, 0]) nozzle(40, 70);
    // N9 drain
    translate([WALL + 80, WALL + 80, 0])
        rotate([180, 0, 0]) nozzle(50, 50);
    // N10 / N11 wells on +Y
    translate([WALL + CSTR_L*0.40, CSTR_W + 2*WALL, FLOOR + 700])
        rotate([-90, 0, 0]) nozzle(20, 50);
    translate([WALL + CSTR_L*0.40, CSTR_W + 2*WALL, FLOOR + 200])
        rotate([-90, 0, 0]) nozzle(20, 50);
    // N12 spare −Y
    translate([WALL + CSTR_L*0.15, 0, FLOOR + 700])
        rotate([90, 0, 0]) nozzle(40, 60);
}

mfg_cstr_shell();
mfg_weir();
mfg_auger_trough();
mfg_mixer();
mfg_leachate_pump();
mfg_nozzles();
translate([0, 0, FLOOR + CSTR_H]) mfg_lid();
