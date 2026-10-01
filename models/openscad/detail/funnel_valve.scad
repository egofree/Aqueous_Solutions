// DN50 harvest valve + slip-on flange. CPVC.
// Buy: Georg Fischer Type 546 DN50 PVC-C FPM.
// Alt: Spears True Union 2000 2" CPVC FKM.
include <../params.scad>;
$fn = 48;

module flange() {
    difference() {
        cylinder(h=16, d=EW_VALVE_D + 48);
        translate([0, 0, -1]) cylinder(h=18, d=EW_VALVE_D);
        for (a = [0:60:300])
            rotate([0, 0, a])
                translate([(EW_VALVE_D + 30)/2, 0, -1])
                    cylinder(h=18, d=10);
    }
}

module valve() {
    flange();
    translate([0, 0, 16])
        difference() {
            cylinder(h=EW_VALVE_L, d=EW_VALVE_D + 2*WALL);
            translate([0, 0, -1])
                cylinder(h=EW_VALVE_L + 2, d=EW_VALVE_D);
        }
    translate([0, 0, 16 + EW_VALVE_L]) flange();
    // handle
    translate([0, 0, 16 + EW_VALVE_L/2])
        rotate([0, 90, 0])
            cylinder(h=80, d=16);
}

valve();
