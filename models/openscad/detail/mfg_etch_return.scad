// ETCH RETURN — closed tank. E3 is local vent, not HDR_ACID_GAS.
include <../params.scad>;
$fn = 24;
L=2400; W=1400; H=1600; T=12;

module stub(d, l=130) {
    difference() {
        cylinder(h=l, d=d+10);
        translate([0,0,-1]) cylinder(h=l+2, d=d);
    }
}

module mfg_etch_return() {
    difference() {
        cube([L, W, H]);
        translate([T, T, T]) cube([L-2*T, W-2*T, H]);
    }
    translate([0, W/2, 1200]) rotate([0,-90,0]) stub(25); // E1
    translate([L, W/2, 200]) rotate([0,90,0]) stub(25);   // E2 REGEN LEACH
    translate([L/2, W/2, H]) stub(25, 180);               // E3 local
}

mfg_etch_return();
