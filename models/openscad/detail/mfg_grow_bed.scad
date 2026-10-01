// GROW BED — trough + G1–G4. G5 is a chute, not a pipe.
include <../params.scad>;
$fn = 24;
L=5600; W=5000; H=400; T=10;

module stub(d, l=140) {
    difference() {
        cylinder(h=l, d=d+10);
        translate([0,0,-1]) cylinder(h=l+2, d=d);
    }
}

module mfg_grow_bed() {
    difference() {
        cube([L, W, H]);
        translate([T, T, T]) cube([L-2*T, W-2*T, H]);
    }
    translate([0, W/2, 200]) rotate([0,-90,0]) stub(80); // G1
    translate([L, W/2, 80]) rotate([0,90,0]) stub(50);   // G2
    translate([L/2, 0, 300]) rotate([90,0,0]) stub(25);  // G3 CO2
    translate([L/2, W, 300]) rotate([-90,0,0]) stub(25); // G4 O2
    translate([L-400, W-80, H]) cube([300, 200, 80]);    // G5 chute lip
}

mfg_grow_bed();
