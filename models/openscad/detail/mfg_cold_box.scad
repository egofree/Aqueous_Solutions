// COLD BOX — vacuum shell + C1–C6. Not the ZnBr2 Br2 tower.
include <../params.scad>;
$fn = 24;
L=2000; W=2600; H=2600; T=16;

module stub(d, l=140) {
    difference() {
        cylinder(h=l, d=d+10);
        translate([0,0,-1]) cylinder(h=l+2, d=d);
    }
}

module mfg_cold_box() {
    difference() {
        cube([L, W, H]);
        translate([T, T, T]) cube([L-2*T, W-2*T, H-2*T]);
    }
    translate([0, 400, 1800]) rotate([0,-90,0]) stub(25); // C1 H2 in
    translate([0, 900, 1800]) rotate([0,-90,0]) stub(40); // C2 air
    translate([L, 400, 1600]) rotate([0,90,0]) stub(25);  // C3 O2
    translate([L, 900, 1600]) rotate([0,90,0]) stub(25);  // C4 N2
    translate([L, 1400, 1600]) rotate([0,90,0]) stub(40); // C5 CO2
    translate([L, 1900, 1600]) rotate([0,90,0]) stub(25); // C6 H2 out
    translate([L/2, 0, 400]) rotate([90,0,0]) stub(40);   // C7 Q reject
}

mfg_cold_box();
