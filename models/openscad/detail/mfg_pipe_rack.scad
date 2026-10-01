// Plant pipe racks. Four gas headers never share a pipe.
// Liquor CPVC on the lowest tier. Oil vapor is a separate spine.
include <../params.scad>;
$fn = 20;

module beam(l, w=80, h=80) { cube([l, w, h]); }

module hanger(h=400) {
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
    else if (axis == "y")
        rotate([-90, 0, 0])
            difference() {
                cylinder(h=l, d=d+8);
                translate([0, 0, -1]) cylinder(h=l+2, d=d);
            }
}

// Wet / EW spine: behind the cells (+Y of aisle), +X from CSTR to EW-9.
module rack_wet(len=9*EW_PITCH + 400) {
    for (x = [0:1500:len-80])
        translate([x, 0, 0]) hanger(2200);
    translate([0, -40, 2200]) beam(len);
    // tiers, lowest liquor, then acid, H2, dust. 200 mm vertical pitch.
    translate([0, 40, 2000]) run_pipe(len, 50);     // CPVC liquor / salt
    translate([0, 40, 2200]) run_pipe(len, GAS_D);  // HDR_ACID_GAS
    translate([0, 40, 2400]) run_pipe(len, GAS_D);  // HDR_H2
    translate([0, 40, 2600]) run_pipe(len, DUST_D); // HDR_DUST (jumper only)
}

// BMED / product spine along +Y of CSTR.
module rack_bmed(len=2200) {
    for (y = [0:1000:len-80])
        translate([0, y, 0]) hanger(1800);
    translate([-40, 0, 1800]) cube([80, len, 80]);
    translate([40, 0, 1600]) run_pipe(len, 40, axis="y"); // NaOH
    translate([40, 0, 1750]) run_pipe(len, 40, axis="y"); // HCl
    translate([40, 0, 1900]) run_pipe(len, 32, axis="y"); // HDR_CAUSTIC
}

// Oil spine. Jacketed oil-vapor only. Not tied to H2 or acid.
module rack_oil(len=PYRO_L + 2000) {
    for (x = [0:1500:len-80])
        translate([x, 0, 0]) hanger(1600);
    translate([0, -40, 1600]) beam(len);
    translate([0, 40, 1500]) run_pipe(len, 80); // HDR_OIL_VAPOR + jacket OD
    translate([0, 40, 1700]) run_pipe(len, 40); // Q2/Q3 condensate
}

module mfg_pipe_rack() {
    rack_wet();
    translate([-400, 2000, 0]) rack_bmed();
    translate([0, -1800, 0]) rack_oil();
}

mfg_pipe_rack();
