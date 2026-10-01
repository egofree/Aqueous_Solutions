// 5.1 pH-shift tanks P-Al / P-Mg / P-Ca. PP or CPVC, agitator, NaOH drop.
include <../params.scad>;
$fn = 24;

module mfg_precip() {
    difference() {
        cube([P_TANK_L, P_TANK_W, P_TANK_H]);
        translate([WALL, WALL, WALL])
            cube([P_TANK_L-2*WALL, P_TANK_W-2*WALL, P_TANK_H]);
    }
    translate([P_TANK_L/2, P_TANK_W/2, WALL])
        union() {
            cylinder(h=P_TANK_H + 200, d=30);
            for (z = [150, 400])
                translate([0, 0, z]) cube([P_TANK_L*0.6, 8, 30], center=true);
        }
    translate([P_TANK_L - 40, P_TANK_W/2, P_TANK_H - 80])
        rotate([0, 90, 0]) cylinder(h=80, d=25); // NaOH drop
}
mfg_precip();
