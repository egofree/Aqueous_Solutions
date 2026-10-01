// HAB WATER — A1–A3 split.
include <../params.scad>;
$fn = 24;
L=2000; W=1600; H=1600; T=10;

module stub(d, l=120) {
    difference() {
        cylinder(h=l, d=d+8);
        translate([0,0,-1]) cylinder(h=l+2, d=d);
    }
}

module mfg_hab_water() {
    difference() {
        cube([L, W, H]);
        translate([T, T, T]) cube([L-2*T, W-2*T, H]);
    }
    translate([0, W/2, 1200]) rotate([0,-90,0]) stub(25); // A1
    translate([L, W/2, 200]) rotate([0,90,0]) stub(40);   // A2 grey
    translate([L/2, W, 1000]) rotate([-90,0,0]) stub(20); // A3
}

mfg_hab_water();
