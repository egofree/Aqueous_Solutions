// Life-header racks. Do not union with mfg_pipe_rack process spines.
include <../params.scad>;
$fn = 18;

module hanger(h) {
    cube([40, 40, h]);
    translate([-20, -20, h]) cube([80, 80, 12]);
}

module run_pipe(l, d, axis="x") {
    if (axis == "x")
        rotate([0, 90, 0])
            difference() {
                cylinder(h=l, d=d+8);
                translate([0, 0, -1]) cylinder(h=l+2, d=d);
            }
    else
        rotate([-90, 0, 0])
            difference() {
                cylinder(h=l, d=d+8);
                translate([0, 0, -1]) cylinder(h=l+2, d=d);
            }
}

module life_tiers(len, axis="x") {
    translate([0, 40, LIFE_Z_GREY]) run_pipe(len, LIFE_D_GREY, axis);
    translate([0, 40, LIFE_Z_UPW])  run_pipe(len, LIFE_D_UPW, axis);
    translate([0, 40, LIFE_Z_ETCH]) run_pipe(len, LIFE_D_ETCH, axis);
    translate([0, 40, LIFE_Z_O2])   run_pipe(len, LIFE_D_GAS, axis);
    translate([0, 40, LIFE_Z_N2])   run_pipe(len, LIFE_D_GAS, axis);
    translate([0, 40, LIFE_Z_CO2])  run_pipe(len, LIFE_D_CO2, axis);
}

module rack_life_n(len=32000) {
    for (x = [0:2500:len-80]) translate([x, 0, 0]) hanger(LIFE_Z_CO2);
    translate([0, -40, LIFE_Z_CO2]) cube([len, 80, 80]);
    life_tiers(len);
}

module rack_life_s(len=26000) {
    for (x = [0:2500:len-80]) translate([x, 0, 0]) hanger(LIFE_Z_CO2);
    translate([0, -40, LIFE_Z_CO2]) cube([len, 80, 80]);
    life_tiers(len);
}

module rack_life_ns(len=20000) {
    for (y = [0:2500:len-80]) translate([0, y, 0]) hanger(LIFE_Z_CO2);
    translate([-40, 0, LIFE_Z_CO2]) cube([80, len, 80]);
    life_tiers(len, axis="y");
}

module mfg_life_rack() {
    rack_life_n();
    translate([2000, -10300, 0]) rack_life_s();
    translate([6000, -11800, 0]) rack_life_ns();
    translate([19800, -13800, 0]) rack_life_ns();
}

mfg_life_rack();
