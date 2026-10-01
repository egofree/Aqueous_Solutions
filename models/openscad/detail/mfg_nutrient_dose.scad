// NUTRIENT DOSE — day tank + D2/D3.
include <../params.scad>;
$fn = 24;
L=1600; W=1400; H=1400; T=10;

module stub(d, l=120) {
    difference() {
        cylinder(h=l, d=d+8);
        translate([0,0,-1]) cylinder(h=l+2, d=d);
    }
}

module mfg_nutrient_dose() {
    difference() {
        cube([L, W, H]);
        translate([T, T, T]) cube([L-2*T, W-2*T, H]);
    }
    translate([L/2, L>0 ? 0 : 0, H-80]) cube([400, 400, 80]); // D1 tote pad
    translate([L, W/2, 200]) rotate([0,90,0]) stub(20);        // D2
    translate([0, W/2, 1100]) rotate([0,-90,0]) stub(15);      // D3
}

mfg_nutrient_dose();
