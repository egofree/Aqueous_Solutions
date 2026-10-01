// BURNOUT ROTARY + UCP213 trunnions.
include <../params.scad>;
$fn = 32;
module ucp213() {
    translate([-110, -35, -57]) cube([220, 70, 22]);
    difference() { cylinder(h=55, d=120); translate([0,0,-1]) cylinder(h=57, d=65); }
}
module mfg_burnout_rotary() {
    difference() {
        cylinder(h=ROTARY_L, d=ROTARY_D);
        translate([0, 0, -1]) cylinder(h=ROTARY_L+2, d=ROTARY_D-24);
    }
    for (z = [200, ROTARY_L-200])
        translate([0, 0, z]) difference() {
            cylinder(h=40, d=ROTARY_D + 40); translate([0,0,-1]) cylinder(h=42, d=ROTARY_D);
        }
    translate([-ROTARY_D, 0, 200]) rotate([0, 90, 0]) ucp213();
    translate([-ROTARY_D, 0, ROTARY_L-200]) rotate([0, 90, 0]) ucp213();
}
rotate([0, 90, 0]) mfg_burnout_rotary();
