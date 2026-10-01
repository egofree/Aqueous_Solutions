// DRYER — paddle trough, Q3 jacket (HX-4), UCP208 on shaft, condensate to Q4.
include <../params.scad>;
$fn = 24;

module ucp208() {
    translate([-90, -30, -50]) cube([180, 60, 20]);
    difference() {
        cylinder(h=45, d=80);
        translate([0,0,-1]) cylinder(h=47, d=40);
    }
}

module mfg_dryer() {
    difference() {
        cube([DRYER_L, DRYER_W, DRYER_H]);
        translate([12, 12, 12]) cube([DRYER_L-24, DRYER_W-24, DRYER_H]);
    }
    translate([40, DRYER_W/2, DRYER_H*0.4])
        rotate([0, 90, 0]) {
            cylinder(h=DRYER_L-80, d=50);
            for (x = [0:80:DRYER_L-80])
                translate([0, 0, x]) cube([180, 8, 20], center=true);
        }
    translate([-20, -20, 40])
        difference() {
            cube([DRYER_L+40, DRYER_W+40, 200]);
            translate([20, 20, -1]) cube([DRYER_L, DRYER_W, 202]);
        }
    translate([20, DRYER_W/2, DRYER_H*0.4]) rotate([0,90,0]) ucp208();
    translate([DRYER_L-20, DRYER_W/2, DRYER_H*0.4]) rotate([0,90,0]) ucp208();
    translate([DRYER_L/2, 0, 80]) rotate([90,0,0])
        difference() { cylinder(h=60, d=40); translate([0,0,-1]) cylinder(h=62, d=25); }
    translate([DRYER_L/2, DRYER_W, 240]) rotate([-90,0,0])
        difference() { cylinder(h=60, d=40); translate([0,0,-1]) cylinder(h=62, d=25); }
}

mfg_dryer();
