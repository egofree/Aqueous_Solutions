// Wet line assembly: CSTR + feed + fork stubs + EW aisle + harvest + headers.
// Origin: leach outer SW corner. Units mm.
include <params.scad>;
use <leach_cstr.scad>;
use <ew_cell.scad>;

aisle_len = 9 * EW_PITCH;
cell_w = EW_W + 2*WALL;
cell_l = EW_L + 2*WALL;

module ew_aisle() {
    for (i = [0:8])
        translate([AISLE_X0 + i*EW_PITCH, AISLE_Y, AISLE_Z])
            ew_cell();
}

module bund() {
    x0 = AISLE_X0 - BUND_PAD;
    y0 = AISLE_Y - BUND_PAD;
    l = aisle_len + BUND_PAD;
    w = cell_w + 2*BUND_PAD;
    translate([x0, y0, AISLE_Z - EW_FUNNEL_H - EW_VALVE_L - BUND_H])
        cube([l, w, BUND_H]);
    // harvest sump at −X end, drains toward CSTR
    translate([x0 - SUMP_L, y0 + w/2 - SUMP_W/2,
               AISLE_Z - EW_FUNNEL_H - EW_VALVE_L - BUND_H - 80])
        cube([SUMP_L, SUMP_W, SUMP_H]);
}

module liquor_pipe() {
    // schematic: pump on −X wall → run −Y to aisle → +X into EW-1 inlet
    py = WALL + PUMP_Y;
    pz = FLOOR + PUMP_Z;
    // drop from pump toward −Y
    translate([-80, AISLE_Y + cell_w/2, pz])
        rotate([90, 0, 0])
            cylinder(h=py - (AISLE_Y + cell_w/2), d=PUMP_D);
    // run +X to EW-1
    translate([-80, AISLE_Y + cell_w/2, pz])
        rotate([0, 90, 0])
            cylinder(h=AISLE_X0 + 80, d=PUMP_D);
    // riser into EW-1
    translate([AISLE_X0, AISLE_Y + cell_w/2, pz])
        cylinder(h=AISLE_Z + EW_H - 80 - pz, d=PUMP_D);
}

module harvest() {
    // shared VDF past EW-9
    x = AISLE_X0 + aisle_len + 200;
    y = AISLE_Y + cell_w/2;
    z = AISLE_Z - EW_FUNNEL_H;
    translate([x, y, z])
        rotate([0, 90, 0])
            cylinder(h=VDF_L, d=VDF_D);
    // pail under each funnel
    for (i = [0:8])
        translate([
            AISLE_X0 + i*EW_PITCH + cell_l/2 - PAIL_W/2,
            AISLE_Y + cell_w/2 - PAIL_W/2,
            AISLE_Z - EW_FUNNEL_H - EW_VALVE_L - PAIL_W
        ])
            cube([PAIL_W, PAIL_W, PAIL_W]);
}

module gas_headers() {
    x0 = -200;
    len = AISLE_X0 + aisle_len + 800;
    // acid gas — lid takeoff + anode side of aisle
    translate([WALL + CSTR_L*0.80, WALL + CSTR_W*0.20, FLOOR + CSTR_H + WALL])
        cylinder(h=HDR_Z - (FLOOR + CSTR_H), d=GAS_D);
    translate([x0, AISLE_Y - 80, HDR_Z])
        rotate([0, 90, 0])
            cylinder(h=len, d=HDR_D);
    // H2 — cathode side
    translate([x0, AISLE_Y + cell_w + 80, HDR_Z])
        rotate([0, 90, 0])
            cylinder(h=len, d=HDR_D);
    // dust — already a stack on the shredder; long header above mezz
    translate([x0, CSTR_W/2, MEZZ_H + SHRED_H + HOPPER_H + 400])
        rotate([0, 90, 0])
            cylinder(h=MEZZ_L + 400, d=DUST_D);
    // oil vapor — stub only, not tied to acid or H2
    translate([weir_spout_x() + FDEW_L, weir_y(), FLOOR + CSTR_H + 600])
        rotate([0, 90, 0])
            cylinder(h=800, d=HDR_D);
}

leach_cstr();
ew_aisle();
color("olive") bund();
color("deepskyblue") liquor_pipe();
color("lightgray") harvest();
color("green") gas_headers();
