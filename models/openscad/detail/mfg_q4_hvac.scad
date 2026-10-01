// HVAC / Q4 condensate skid. Makeup water the BPM splits. To SALT FEED.
include <../params.scad>;
$fn = 24;

module mfg_q4_hvac() {
    difference() {
        cube([500, 500, 700]);
        translate([12, 12, 12]) cube([476, 476, 680]);
    }
    translate([250, 250, 700]) cylinder(h=80, d=50);
    translate([500, 250, 200]) rotate([0, 90, 0])
        difference() {
            cylinder(h=80, d=40);
            translate([0,0,-1]) cylinder(h=82, d=25);
        }
}

mfg_q4_hvac();
