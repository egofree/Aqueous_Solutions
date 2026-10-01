// WET BENCH — W1–W5. No floor drain.
include <../params.scad>;
$fn = 24;
L=2400; W=2600; H=1100; T=12;

module stub(d, l=130) {
    difference() {
        cylinder(h=l, d=d+10);
        translate([0,0,-1]) cylinder(h=l+2, d=d);
    }
}

module mfg_wet_bench() {
    difference() {
        cube([L, W, H]);
        translate([T, T, T]) cube([L-2*T, W-2*T, H-80]);
    }
    translate([0, 400, 900]) rotate([0,-90,0]) stub(25); // W1 UPW
    translate([0, 800, 900]) rotate([0,-90,0]) stub(20); // W2 HCl
    translate([0, 1200, 900]) rotate([0,-90,0]) stub(20); // W3 NaOH
    translate([0, 1600, 900]) rotate([0,-90,0]) stub(15); // W4 N2
    translate([L, W/2, 200]) rotate([0,90,0]) stub(25);   // W5 etch
}

mfg_wet_bench();
