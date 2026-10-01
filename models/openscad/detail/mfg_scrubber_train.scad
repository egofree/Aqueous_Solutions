// 8.1 DEMISTER + ALK SCRUBBER + FAN STACK. Pregnant liquor → CRU.
include <../params.scad>;
$fn = 32;

module mfg_demister() {
    difference() {
        cube([600, 500, 700]);
        translate([12, 12, 12]) cube([576, 476, 680]);
    }
}

module mfg_alk_scrubber() {
    difference() {
        cube([700, 700, 1800]);
        translate([12, 12, 12]) cube([676, 676, 1780]);
    }
    for (z = [200:250:1400])
        translate([50, 50, z]) cube([600, 600, 12]);
}

module mfg_fan_stack() {
    difference() {
        cylinder(h=12000, d=400);
        translate([0, 0, -1]) cylinder(h=12002, d=360);
    }
}

mfg_demister();
translate([800, 0, 0]) mfg_alk_scrubber();
translate([1800, 350, 0]) mfg_fan_stack();
