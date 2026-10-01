// One BMED repeating unit: BASE | CEM | SALT | AEM | ACID, BPM at the ends.
include <../params.scad>;

ch = 400;
cw = 300;
gap = 8;
mem = 4;

module plate(c) color(c) cube([mem, cw, ch]);

module unit() {
    x = 0;
    color("lightgray") cube([20, cw, ch]);                 // cathode end
    translate([24, 0, 0]) plate("steelblue");              // BPM CEL toward cathode
    translate([24+mem, 0, 0]) color("orange") cube([mem, cw, ch]); // BPM AEL
    translate([40, 0, 0]) color("ivory") cube([80, cw, ch]); // BASE
    translate([124, 0, 0]) plate("steelblue");             // CEM
    translate([132, 0, 0]) color("beige") cube([80, cw, ch]); // SALT
    translate([216, 0, 0]) plate("orange");                 // AEM
    translate([224, 0, 0]) color("honeydew") cube([80, cw, ch]); // ACID
    translate([308, 0, 0]) color("orange") cube([mem, cw, ch]);
    translate([308+mem, 0, 0]) plate("steelblue");         // BPM, CEL toward next cathode
    translate([320, 0, 0]) color("lightgray") cube([20, cw, ch]);
}

unit();
