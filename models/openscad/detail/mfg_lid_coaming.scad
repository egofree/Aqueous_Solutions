// 1.4 / 2.6 Lid drop coaming + M16 bolt ring. No screen.
include <../params.scad>;
$fn = 24;

module mfg_lid_coaming() {
    difference() {
        translate([-20, -20, 0])
            cube([DROP_L + 40, DROP_W + 40, DROP_COAM + WALL]);
        translate([0, 0, -1])
            cube([DROP_L, DROP_W, DROP_COAM + WALL + 2]);
        for (x = [20, DROP_L - 20])
            for (y = [-10, DROP_W + 10])
                translate([x, y, -1]) cylinder(h=WALL + 4, d=16);
        for (y = [20, DROP_W - 20])
            for (x = [-10, DROP_L + 10])
                translate([x, y, -1]) cylinder(h=WALL + 4, d=16);
    }
}
mfg_lid_coaming();
