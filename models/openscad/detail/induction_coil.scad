// Single induction ring that sits on the Ti pyro shell. Repeat along PYRO_L.
include <../params.scad>;
$fn = 64;

coil_id = PYRO_D + 20;
coil_od = coil_id + 40;
coil_h  = 50;

module coil() {
    difference() {
        cylinder(h=coil_h, d=coil_od);
        translate([0, 0, -1]) cylinder(h=coil_h + 2, d=coil_id);
        translate([coil_od/2 - 8, 0, coil_h/2])
            cube([20, 8, coil_h + 2], center=true);
    }
}

coil();
