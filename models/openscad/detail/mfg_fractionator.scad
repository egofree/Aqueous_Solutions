// FRACTIONATOR + cut tanks + HX-3 reboiler stub.
include <../params.scad>;
$fn = 32;
module mfg_fractionator() {
    difference() {
        cylinder(h=FRAC_H, d=FRAC_D);
        translate([0, 0, 12]) cylinder(h=FRAC_H-24, d=FRAC_D-16);
    }
    for (z = [400:200:FRAC_H-400])
        translate([0, 0, z]) difference() {
            cylinder(h=8, d=FRAC_D-18); cylinder(h=8, d=80);
        }
}
module cut_tank() {
    difference() { cube([600, 300, 700]); translate([8,8,8]) cube([584,284,700]); }
}
module reboiler() {
    translate([-200, -150, 80]) difference() {
        cube([180, 300, 400]); translate([12,12,12]) cube([156,276,376]);
    }
}
mfg_fractionator();
reboiler();
for (i = [0:3]) translate([FRAC_D/2 + 80, i*350, 0]) cut_tank();
