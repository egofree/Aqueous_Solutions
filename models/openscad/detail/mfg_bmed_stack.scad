// BMED stack — eight 3-compartment repeating units. Chlorate is not made here.
include <../params.scad>;
ch = 400; cw = 300; mem = 4; N_UNITS = 8; PITCH = 340;

module plate(c) color(c) cube([mem, cw, ch]);

module unit() {
    color("lightgray") cube([20, cw, ch]);
    translate([24, 0, 0]) plate("steelblue");
    translate([24+mem, 0, 0]) color("orange") cube([mem, cw, ch]);
    translate([40, 0, 0]) color("ivory") cube([80, cw, ch]);
    translate([124, 0, 0]) plate("steelblue");
    translate([132, 0, 0]) color("beige") cube([80, cw, ch]);
    translate([216, 0, 0]) plate("orange");
    translate([224, 0, 0]) color("honeydew") cube([80, cw, ch]);
    translate([308, 0, 0]) color("orange") cube([mem, cw, ch]);
    translate([308+mem, 0, 0]) plate("steelblue");
    translate([320, 0, 0]) color("lightgray") cube([20, cw, ch]);
}

module mfg_bmed_stack() {
    for (i = [0:N_UNITS-1]) translate([i * PITCH, 0, 200]) unit();
    translate([-30, -20, 180]) cube([N_UNITS*PITCH + 60, 20, 440]);
    translate([-30, 300, 180]) cube([N_UNITS*PITCH + 60, 20, 440]);
    translate([-40, 40, 560]) cube([N_UNITS*PITCH + 80, 40, 40]);
    translate([-40, 130, 560]) cube([N_UNITS*PITCH + 80, 40, 40]);
    translate([-40, 220, 560]) cube([N_UNITS*PITCH + 80, 40, 40]);
}

mfg_bmed_stack();
