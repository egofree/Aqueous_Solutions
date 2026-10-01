// FARM SUMP — S1–S4.
include <../params.scad>;
$fn = 24;
L=2500; W=1800; H=1200; T=12;

module stub(d, l=140) {
    difference() {
        cylinder(h=l, d=d+10);
        translate([0,0,-1]) cylinder(h=l+2, d=d);
    }
}

module mfg_farm_sump() {
    difference() {
        cube([L, W, H]);
        translate([T, T, T]) cube([L-2*T, W-2*T, H]);
    }
    translate([0, W/2, 700]) rotate([0,-90,0]) stub(80); // S1
    translate([L, W/2, 200]) rotate([0,90,0]) stub(50);  // S2 HDR_GREY
    translate([L/2, 0, 1000]) rotate([90,0,0]) stub(25); // S3 UPW
    translate([L/2, W, 700]) rotate([-90,0,0]) stub(20); // S4 dose
}

mfg_farm_sump();
