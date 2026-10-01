// 8.2 BAGHOUSE. Fines return to CSTR 1.
include <../params.scad>;
$fn = 24;

module mfg_baghouse() {
    difference() {
        cube([800, 800, 1600]);
        translate([12, 12, 200]) cube([776, 776, 1380]);
    }
    for (x = [150:160:650])
        for (y = [150:160:650])
            translate([x, y, 200])
                cylinder(h=1200, d=80);
    translate([400, 400, 0])
        cylinder(h=80, d=DUST_D);
}
mfg_baghouse();
