// 4.5 Bund lining + sump + grate. CPVC liner on CS bund.
include <../params.scad>;
$fn = 24;
aisle_len = 9 * EW_PITCH;
cell_w = EW_W + 2*WALL;

module mfg_ew_bund() {
    difference() {
        cube([aisle_len + 2*BUND_PAD, cell_w + 2*BUND_PAD, BUND_H]);
        translate([12, 12, 12])
            cube([aisle_len + 2*BUND_PAD - 24, cell_w + 2*BUND_PAD - 24, BUND_H]);
    }
    translate([-SUMP_L, (cell_w + 2*BUND_PAD)/2 - SUMP_W/2, -80])
        difference() {
            cube([SUMP_L, SUMP_W, SUMP_H]);
            translate([12, 12, 12]) cube([SUMP_L - 24, SUMP_W - 24, SUMP_H]);
        }
    // FRP grate panels
    for (x = [20:200:aisle_len])
        translate([x, 20, BUND_H - 8])
            cube([180, cell_w + 2*BUND_PAD - 40, 8]);
}
mfg_ew_bund();
