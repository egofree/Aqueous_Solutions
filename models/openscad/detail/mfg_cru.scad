// CRU — chlorate finish hold. Alkali-tower liquor (NaCl + NaClO) held
// hot and alkaline until 3 NaClO → 2 NaCl + NaClO3. Then + BMED HCl
// is REGEN LEACH to N5 on CSTR 1.
// Wall CPVC or PVDF. Not PP. Vent to HDR_ACID_GAS. Liquor never to sewer.
include <../params.scad>;
$fn = 28;

CRU_L = 900;
CRU_W = 800;
CRU_H = 1200;

module cru_shell() {
    difference() {
        cube([CRU_L, CRU_W, CRU_H]);
        translate([WALL, WALL, WALL])
            cube([CRU_L-2*WALL, CRU_W-2*WALL, CRU_H]);
    }
}

module cru_jacket() {
    // Q3 / electric pad — keep 70-80 C for disproportionation
    translate([-20, -20, 80])
        difference() {
            cube([CRU_L+40, CRU_W+40, 400]);
            translate([20, 20, -1]) cube([CRU_L, CRU_W, 402]);
        }
}

module cru_agitator() {
    translate([CRU_L/2, CRU_W/2, WALL])
        union() {
            cylinder(h=CRU_H + 180, d=30);
            for (z = [200, 500, 800])
                translate([0, 0, z]) cube([CRU_L*0.55, 8, 30], center=true);
            translate([0, 0, CRU_H + 40]) cylinder(h=70, d=80);
        }
}

module cru_nozzles() {
    // in from alkali sump DN40
    translate([0, CRU_W/2, CRU_H-150])
        rotate([0, -90, 0])
            difference() { cylinder(h=80, d=56); translate([0,0,-1]) cylinder(h=82, d=40); }
    // out to N5 / REGEN LEACH DN40
    translate([CRU_L, CRU_W/2, 150])
        rotate([0, 90, 0])
            difference() { cylinder(h=80, d=56); translate([0,0,-1]) cylinder(h=82, d=40); }
    // BMED HCl trim DN25
    translate([CRU_L*0.3, 0, CRU_H-200])
        rotate([90, 0, 0])
            difference() { cylinder(h=70, d=40); translate([0,0,-1]) cylinder(h=72, d=25); }
    // vent DN50 to HDR_ACID_GAS
    translate([CRU_L*0.7, CRU_W/2, CRU_H])
        difference() { cylinder(h=80, d=66); translate([0,0,-1]) cylinder(h=82, d=50); }
}

module mfg_cru() {
    cru_shell();
    cru_jacket();
    cru_agitator();
    cru_nozzles();
}

mfg_cru();
