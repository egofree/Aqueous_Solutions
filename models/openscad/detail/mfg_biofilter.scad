// BIOFILTER — media bed, B1–B3.
include <../params.scad>;
$fn = 24;
L=2000; W=2500; H=1800; T=12;

module stub(d, l=140) {
    difference() {
        cylinder(h=l, d=d+10);
        translate([0,0,-1]) cylinder(h=l+2, d=d);
    }
}

module mfg_biofilter() {
    difference() {
        cube([L, W, H]);
        translate([T, T, T]) cube([L-2*T, W-2*T, H]);
    }
    translate([0, W/2, 1400]) rotate([0,-90,0]) stub(80); // B1
    translate([L, W/2, 1400]) rotate([0,90,0]) stub(80);  // B2
    translate([L/2, 0, 80]) rotate([90,0,0]) stub(40);    // B3
    translate([T+40, T+40, 400]) cube([L-2*T-80, W-2*T-80, 40]); // media floor
}

mfg_biofilter();
