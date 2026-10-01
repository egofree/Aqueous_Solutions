// FISH TANK — PP shell + F1–F4. Not a Salria vessel.
include <../params.scad>;
$fn = 24;
L=3500; W=2500; H=1800; T=12;

module stub(d, l=140) {
    difference() {
        cylinder(h=l, d=d+10);
        translate([0,0,-1]) cylinder(h=l+2, d=d);
    }
}

module mfg_fish_tank() {
    difference() {
        cube([L, W, H]);
        translate([T, T, T]) cube([L-2*T, W-2*T, H]);
    }
    // F1 overflow +X
    translate([L, W/2, H-250]) rotate([0,90,0]) stub(80);
    // F2 drain +X low
    translate([L, W/2-400, 120]) rotate([0,90,0]) stub(50);
    // F3 UPW −X
    translate([0, W/2, 1400]) rotate([0,-90,0]) stub(25);
    // F4 air −Y
    translate([400, 0, 400]) rotate([90,0,0]) stub(15);
}

mfg_fish_tank();
