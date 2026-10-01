// INDUCTION PYROLYZER — shop-level envelope
// Ti Grade 2 shell ~NPS 12. Cast-iron conical auger on Ø50 mm shaft.
// Coils couple to the iron, not the charge. Dry feed. No FR-4.
//
// COTS datums (see manufacturing_bom.xlsx):
//   Drive-end bearing  UCP210  d=50  h=57.2  a=206  e=159  b=60  w=114  M16
//   Discharge          water-cooled bronze bush, not a grease pillow block
//   Shell flanges      ASME B16.5 Cl.150 NPS 12  OD=482.6  BC=431.8  12×Ø25.4
//   Vapor nozzle       ASME B16.5 Cl.150 NPS 3   OD=190.5  BC=152.4  4×Ø19.1
//   Coil tube          Cu 12.7 OD × 1.2 wall, water-cooled
include <../params.scad>;
$fn = 36;

// --- catalogue numbers (mm) ---
SHAFT_D     = 50;
UCP_H       = 57.2;
UCP_A       = 206;
UCP_E       = 159;
UCP_B       = 60;
UCP_W       = 114;
UCP_S1      = 20;
FL12_OD     = 482.6;
FL12_T      = 31.8;
FL12_BC     = 431.8;
FL12_N      = 12;
FL12_HOLE   = 25.4;
FL3_OD      = 190.5;
FL3_T       = 23.9;
FL3_BC      = 152.4;
COIL_TUBE   = 12.7;
COIL_N      = 6;
SHELL_OD    = PYRO_D + 16;     // ~8 mm wall on 320 ID
JACKET_OD   = SHELL_OD + 40;

module ucp210() {
    // Cast housing + insert. Origin at shaft axis.
    translate([-UCP_A/2, -UCP_B/2, -UCP_H])
        difference() {
            union() {
                cube([UCP_A, UCP_B, 21]);
                translate([UCP_A/2, UCP_B/2, 21])
                    cylinder(h=UCP_W-21, d=110);
            }
            translate([UCP_A/2 - UCP_E/2, UCP_B/2, -1])
                cube([UCP_S1, UCP_B, 8], center=true);
            translate([UCP_A/2 + UCP_E/2, UCP_B/2, -1])
                cube([UCP_S1, UCP_B, 8], center=true);
        }
    translate([0, 0, -UCP_H + 21])
        difference() {
            cylinder(h=51.6, d=90);
            translate([0, 0, -1]) cylinder(h=54, d=SHAFT_D);
        }
}

module flange_nps12() {
    difference() {
        cylinder(h=FL12_T, d=FL12_OD);
        translate([0, 0, -1]) cylinder(h=FL12_T+2, d=PYRO_D);
        for (i = [0:FL12_N-1])
            rotate([0, 0, i*360/FL12_N])
                translate([FL12_BC/2, 0, -1])
                    cylinder(h=FL12_T+2, d=FL12_HOLE);
    }
}

module flange_nps3() {
    difference() {
        cylinder(h=FL3_T, d=FL3_OD);
        translate([0, 0, -1]) cylinder(h=FL3_T+2, d=78);
        for (i = [0:3])
            rotate([0, 0, i*90])
                translate([FL3_BC/2, 0, -1])
                    cylinder(h=FL3_T+2, d=19.1);
    }
}

module ti_shell() {
    difference() {
        cylinder(h=PYRO_L, d=SHELL_OD);
        translate([0, 0, -1]) cylinder(h=PYRO_L+2, d=PYRO_D);
    }
    flange_nps12();
    translate([0, 0, PYRO_L - FL12_T]) flange_nps12();
    // vapor takeoff mid-barrel, top
    translate([0, SHELL_OD/2, PYRO_L*0.72])
        rotate([-90, 0, 0]) {
            cylinder(h=80, d=90);
            translate([0, 0, 80]) flange_nps3();
        }
}

module conical_auger() {
    // Ø80 → Ø50 shaft nose; flights 0.82 D → 0.55 D
    union() {
        cylinder(h=PYRO_L + 180, d=SHAFT_D);
        translate([0, 0, 40])
            cylinder(h=120, d1=80, d2=SHAFT_D);
        for (i = [0:18:PYRO_L-20]) {
            od = 0.82*PYRO_D - 0.27*PYRO_D*(i/PYRO_L);
            rotate([0, 0, i/180*360])
                translate([SHAFT_D/2 - 2, -8, i])
                    cube([od/2 - SHAFT_D/2, 16, 22]);
        }
    }
}

module coil_turn(z) {
    translate([0, 0, z])
        difference() {
            cylinder(h=COIL_TUBE + 4, d=SHELL_OD + 28);
            translate([0, 0, -1])
                cylinder(h=COIL_TUBE + 6, d=SHELL_OD + 6);
            translate([SHELL_OD/2 + 4, -3, -1])
                cube([20, 6, COIL_TUBE + 6]);
        }
}

module coil_bus() {
    // two copper buses along +Y
    translate([SHELL_OD/2 + 20, 8, 80])
        cube([12, 8, PYRO_L - 160]);
    translate([SHELL_OD/2 + 20, -16, 80])
        cube([12, 8, PYRO_L - 160]);
}

module insulation_jacket() {
    difference() {
        cylinder(h=PYRO_L - 80, d=JACKET_OD + 30);
        translate([0, 0, -1]) cylinder(h=PYRO_L - 78, d=JACKET_OD);
        // coil window
        translate([0, 0, 40])
            cylinder(h=PYRO_L - 160, d=JACKET_OD + 32);
    }
}

module hx_coil_cooler() {
    // plate-frame stand-in, Q3 reject from coil water
    translate([SHELL_OD/2 + 80, -150, PYRO_L*0.35])
        difference() {
            cube([220, 300, 400]);
            translate([12, 12, 12]) cube([196, 276, 376]);
        }
}

module hx_vapor_jacket() {
    // jacketed NPS 3 run toward quench (HX on vapor line)
    translate([0, SHELL_OD/2 + 80 + FL3_T, PYRO_L*0.72])
        rotate([-90, 0, 0])
            difference() {
                cylinder(h=400, d=130);
                translate([0, 0, -1]) cylinder(h=402, d=90);
            }
}

module cooled_bush() {
    // discharge: bronze bush + water jacket (not UCP)
    difference() {
        union() {
            cylinder(h=90, d=120);
            translate([-70, -70, 0]) cube([140, 140, 20]);
        }
        translate([0, 0, -1]) cylinder(h=92, d=SHAFT_D + 1);
        translate([50, 0, 45]) rotate([0, 90, 0]) cylinder(h=40, d=12);
    }
}

module saddle() {
    difference() {
        translate([-100, -100, 0]) cube([200, 200, UCP_H + SHELL_OD/2]);
        translate([0, 0, UCP_H + SHELL_OD/2])
            rotate([0, 90, 0])
                cylinder(h=220, d=SHELL_OD + 8, center=true);
        // UCP bolt pattern on top of pedestal if used as rest
    }
}

module drive() {
    // helical gearmotor envelope
    translate([-280, -100, -UCP_H - 20])
        cube([220, 200, 180]);
    translate([-60, 0, 0])
        rotate([0, 90, 0]) cylinder(h=80, d=28);
}

module mfg_induction_pyrolyzer() {
    rotate([0, 90, 0]) {
        ti_shell();
        conical_auger();
        for (i = [0:COIL_N-1])
            coil_turn(200 + i * ((PYRO_L - 400) / (COIL_N - 1)));
        coil_bus();
        translate([0, 0, 40]) insulation_jacket();
        hx_vapor_jacket();
        translate([0, 0, -40]) ucp210();
        translate([0, 0, PYRO_L + 20]) cooled_bush();
    }
    translate([220, 0, -(UCP_H + SHELL_OD/2)]) saddle();
    translate([PYRO_L - 220, 0, -(UCP_H + SHELL_OD/2)]) saddle();
    translate([0, 0, 0]) drive();
    rotate([0, 90, 0]) hx_coil_cooler();
}

mfg_induction_pyrolyzer();
