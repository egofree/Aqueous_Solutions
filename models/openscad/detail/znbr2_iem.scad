// ZnBr2 stack IEM frame (CEM, drawn blue). SEM Tech style.
include <../params.scad>;

fw = 400;
fh = 300;
ft = 12;
open_w = 320;
open_h = 220;

module frame() {
    difference() {
        cube([fw, ft, fh]);
        translate([(fw-open_w)/2, -1, (fh-open_h)/2])
            cube([open_w, ft + 2, open_h]);
    }
    color("steelblue")
    translate([(fw-open_w)/2, ft/2 - 2, (fh-open_h)/2])
        cube([open_w, 4, open_h]);
}

frame();
