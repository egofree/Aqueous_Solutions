// VIBRATORY SPLIT — after SINK DEWATER only.
// Dense plastic → OIL LINE stub. Grit / FR-4 / glass → GLASS / CERAMIC stub.
// Wetted CPVC. Dust cover taps HDR_DUST (negative). No FR-4 to pyro.
include <../params.scad>;
$fn = 24;

module mfg_vibratory_split() {
    difference() {
        cube([SPLIT_L, SPLIT_W, SPLIT_H]);
        translate([8, 8, 8])
            cube([SPLIT_L-16, SPLIT_W-16, SPLIT_H]);
        translate([SPLIT_L-1, 20, 40]) cube([12, 160, 120]);
        translate([SPLIT_L-1, SPLIT_W-180, 40]) cube([12, 160, 120]);
    }
    translate([SPLIT_L, 20, 20]) cube([STUB_L, 160, 80]);
    translate([SPLIT_L, SPLIT_W-180, 20]) cube([STUB_L, 160, 80]);
    translate([10, 10, SPLIT_H-12]) cube([SPLIT_L-20, SPLIT_W-20, 8]);
    translate([SPLIT_L/2, SPLIT_W/2, SPLIT_H])
        difference() {
            cylinder(h=80, d=DUST_D);
            translate([0, 0, -1]) cylinder(h=82, d=DUST_D-16);
        }
    for (x = [60, SPLIT_L-60])
        for (y = [40, SPLIT_W-40])
            translate([x, y, -CONV_SPRING_H])
                cylinder(h=CONV_SPRING_H, d=CONV_SPRING_D);
    translate([SPLIT_L*0.4, SPLIT_W+40, 50])
        rotate([90, 0, 0]) cylinder(h=140, d=110);
}

mfg_vibratory_split();
