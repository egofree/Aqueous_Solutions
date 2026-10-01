// One EW cell fit-out: CEM slot, hangers, anode hood, cathode hood, harvest valve.
// Valve SKU: GF 546 Pro V 163 546 357V (DN50 PVC-C FKM vented ASTM).
// Alt: Spears TU 2000 2 in CPVC FKM vented.
// Anode hood → HDR_ACID_GAS. Cathode hood → HDR_H2. Do not common the two.
include <../params.scad>;
$fn = 28;

module overflow_weir() {
    difference() {
        cube([WALL + 4, EW_W * 0.30, 80]);
        translate([WALL, 10, 20]) cube([8, EW_W * 0.30 - 20, 50]);
    }
}

module cathode_hanger() {
    cube([EW_L - 40, 8, 20]);
    translate([0, -2, -EW_H + 80]) cube([EW_L - 40, 4, EW_H - 80]);
}

module anode_hanger() {
    cube([EW_L - 40, 10, 16]);
    translate([0, 2, -EW_H + 80]) cube([EW_L - 40, 6, EW_H - 100]);
}

module anode_hood() {
    // +Y half of cell, suction DN50
    difference() {
        translate([20, EW_W/2 + 10, EW_H - 40])
            cube([EW_L - 40, EW_W/2 - 20, 80]);
        translate([28, EW_W/2 + 18, EW_H - 41])
            cube([EW_L - 56, EW_W/2 - 36, 70]);
    }
    translate([EW_L/2, EW_W - 20, EW_H + 40])
        rotate([-90, 0, 0])
            difference() {
                cylinder(h=70, d=66);
                translate([0, 0, -1]) cylinder(h=72, d=50);
            }
}

module cathode_hood() {
    difference() {
        translate([20, 10, EW_H - 40])
            cube([EW_L - 40, EW_W/2 - 20, 80]);
        translate([28, 18, EW_H - 41])
            cube([EW_L - 56, EW_W/2 - 36, 70]);
    }
    translate([EW_L/2, 20, EW_H + 40])
        rotate([90, 0, 0])
            difference() {
                cylinder(h=70, d=66);
                translate([0, 0, -1]) cylinder(h=72, d=50);
            }
}

module harvest_valve_546() {
    // GF Type 546 envelope, DN50
    union() {
        cylinder(h=16, d=98);
        translate([0, 0, 16]) cylinder(h=EW_VALVE_L, d=EW_VALVE_D + 2*WALL);
        translate([0, 0, 16 + EW_VALVE_L]) cylinder(h=16, d=98);
        translate([0, 0, 16 + EW_VALVE_L/2])
            rotate([0, 90, 0]) cylinder(h=90, d=18);
    }
}

module mfg_ew_fitout() {
    overflow_weir();
    translate([20, EW_W/2 - EW_SLOT - 20, EW_H - 20]) cathode_hanger();
    translate([20, EW_W/2 + 20, EW_H - 20]) anode_hanger();
    anode_hood();
    cathode_hood();
    translate([EW_L/2, EW_W/2, -EW_FUNNEL_H - EW_VALVE_L])
        harvest_valve_546();
}

mfg_ew_fitout();
