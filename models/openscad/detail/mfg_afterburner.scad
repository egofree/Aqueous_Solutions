// AFTERBURNER + burner register + HX-7 takeoff.
include <../params.scad>;
$fn = 32;
module mfg_afterburner() {
    difference() {
        cylinder(h=AB_H, d=AB_D);
        translate([0, 0, 12]) cylinder(h=AB_H-24, d=AB_D-20);
    }
    translate([0, 0, AB_H]) difference() {
        cylinder(h=400, d=AB_D - 40); translate([0,0,-1]) cylinder(h=402, d=AB_D - 60);
    }
    translate([AB_D/2, 0, AB_H*0.6]) rotate([0, 90, 0]) cylinder(h=400, d=180);
    translate([-AB_D/2 - 200, -80, 200]) cube([200, 160, 160]);
    translate([-AB_D/2, 0, 280]) rotate([0, 90, 0]) cylinder(h=80, d=60);
}
mfg_afterburner();
