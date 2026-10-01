// HAB WASTE — J1 liquor. J2 is a chute.
include <../params.scad>;
$fn = 24;
L=2000; W=1600; H=1600; T=10;

module stub(d, l=120) {
    difference() {
        cylinder(h=l, d=d+8);
        translate([0,0,-1]) cylinder(h=l+2, d=d);
    }
}

module mfg_hab_waste() {
    difference() {
        cube([L, W, H]);
        translate([T, T, T]) cube([L-2*T, W-2*T, H]);
    }
    translate([L, W/2, 200]) rotate([0,90,0]) stub(40); // J1
    translate([L-350, W-60, H-40]) cube([280, 180, 60]); // J2 lip
}

mfg_hab_waste();
