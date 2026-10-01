// 4.3 overflow weir plate + 4.4 anode/cathode hangers.
// Anode: Ti Grade 2 + MMO. Cathode: 316L sheet or bar. Not tank walls.
include <../params.scad>;
$fn = 24;

module overflow_weir() {
    difference() {
        cube([WALL + 4, EW_W * 0.30, 80]);
        translate([WALL, 10, 20]) cube([8, EW_W * 0.30 - 20, 50]);
    }
}

module cathode_hanger() {
    // 316L bar + sheet
    cube([EW_L - 40, 8, 20]);
    translate([0, -2, -EW_H + 80])
        cube([EW_L - 40, 4, EW_H - 80]);
}

module anode_hanger() {
    // Ti bus + MMO plate
    cube([EW_L - 40, 10, 16]);
    translate([0, 2, -EW_H + 80])
        cube([EW_L - 40, 6, EW_H - 100]);
}

overflow_weir();
translate([80, 0, 0]) cathode_hanger();
translate([80, 80, 0]) anode_hanger();
