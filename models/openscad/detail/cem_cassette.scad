// EW CEM cassette + gaskets. Import STL into EW cell later.
include <../params.scad>;

gasket = 3;
frame = 12;
l = EW_L - 20;
h = EW_H - 50;

module cassette() {
    // frame
    difference() {
        cube([l, EW_SLOT + 2*frame, h]);
        translate([frame, frame, frame])
            cube([l - 2*frame, EW_SLOT, h - 2*frame]);
    }
    // CEM (blue in PFD)
    color("steelblue")
    translate([frame + 2, frame + (EW_SLOT - EW_MEM_T)/2, frame + 2])
        cube([l - 2*frame - 4, EW_MEM_T, h - 2*frame - 4]);
    // gaskets
    color("dimgray")
    translate([frame, frame - gasket, frame])
        cube([l - 2*frame, gasket, h - 2*frame]);
    color("dimgray")
    translate([frame, frame + EW_SLOT, frame])
        cube([l - 2*frame, gasket, h - 2*frame]);
}

cassette();
