// LEACH CSTR 1 + CSTR 2 weir + CSTR 3 floor auger.
// One vessel. Open in OpenSCAD or include from assembly_wet.scad.
include <params.scad>;

module box_shell(l, w, h, t, floor_t) {
    difference() {
        cube([l + 2*t, w + 2*t, h + floor_t]);
        translate([t, t, floor_t])
            cube([l, w, h + 1]);
    }
}

module weir_cut() {
    // slot through +X wall, crest at WEIR_CREST above inner floor
    x = WALL + CSTR_L - 1;
    y = WALL + (CSTR_W - WEIR_W) / 2;
    z = FLOOR + WEIR_CREST;
    translate([x, y, z])
        cube([WALL + 2, WEIR_W, WEIR_SLOT_H + 200]);
}

module weir_spout() {
    y = WALL + (CSTR_W - WEIR_W) / 2 - WALL;
    z = FLOOR + WEIR_CREST - WALL;
    translate([WALL + CSTR_L + WALL, y, z])
        difference() {
            cube([WEIR_LIP, WEIR_W + 2*WALL, WEIR_SLOT_H + WALL + 20]);
            translate([-1, WALL, WALL])
                cube([WEIR_LIP + 2, WEIR_W, WEIR_SLOT_H + 40]);
        }
}

module trough() {
    // U-trough bonded to inner floor, along +X
    y0 = WALL + AUGER_OFFSET_Y - AUGER_TROUGH_W/2;
    translate([WALL + 40, y0, FLOOR])
        difference() {
            cube([CSTR_L - 80, AUGER_TROUGH_W, AUGER_TROUGH_H]);
            translate([-1, 12, 12])
                cube([CSTR_L - 78, AUGER_TROUGH_W - 24, AUGER_TROUGH_H]);
        }
}

module flight_helix(length) {
    turns = length / AUGER_PITCH;
    color("gray")
    union() {
        cylinder(h=length, d=AUGER_SHAFT);
        linear_extrude(height=length, twist=360*turns, slices=max(24, turns*12), convexity=8)
            translate([AUGER_D*0.28, 0, 0])
                circle(d=AUGER_D*0.22);
    }
}

module floor_auger() {
    // shaft along trough, then inclined lift out +X wall above crest
    y = WALL + AUGER_OFFSET_Y;
    z = FLOOR + AUGER_TROUGH_H/2;
    translate([WALL + 60, y, z])
        rotate([0, 90, 0])
            flight_helix(CSTR_L - 140);

    // inclined discharge tube + screw
    start = [WALL + CSTR_L - 40, y, z];
    translate(start)
        rotate([0, -AUGER_INCLINE, 0]) {
            translate([0, 0, -10])
                difference() {
                    cylinder(h=700, d=AUGER_D + 24);
                    translate([0, 0, -1])
                        cylinder(h=702, d=AUGER_D + 4);
                }
            rotate([0, 90, 0])
                flight_helix(680);
        }
}

function drop_x() = WALL + DROP_X;
function drop_y() = WALL + (CSTR_W - DROP_W) / 2;

module lid() {
    translate([0, 0, FLOOR + CSTR_H])
        difference() {
            cube([CSTR_L + 2*WALL, CSTR_W + 2*WALL, WALL]);
            translate([drop_x(), drop_y(), -1])
                cube([DROP_L, DROP_W, WALL + 2]);
            translate([WALL + CSTR_L*0.55, WALL + CSTR_W*0.55, -1])
                cylinder(h=WALL + 2, d=MIXER_D);
            translate([WALL + CSTR_L*0.80, WALL + CSTR_W*0.20, -1])
                cylinder(h=WALL + 2, d=GAS_D);
        }
}

module drop_coaming() {
    // raised collar around the locked lid slot — conveyor aims here
    x = drop_x() - 20;
    y = drop_y() - 20;
    z = FLOOR + CSTR_H + WALL;
    difference() {
        translate([x, y, z])
            cube([DROP_L + 40, DROP_W + 40, DROP_COAM]);
        translate([drop_x(), drop_y(), z - 1])
            cube([DROP_L, DROP_W, DROP_COAM + 2]);
    }
}

module leachate_pump() {
    // DN80 through −X wall, coarse strainer box on the inside
    cy = WALL + PUMP_Y;
    cz = FLOOR + PUMP_Z;
    // nozzle through wall
    translate([0, cy, cz])
        rotate([0, 90, 0])
            difference() {
                cylinder(h=WALL + 180, d=PUMP_D + 16);
                translate([0, 0, -1])
                    cylinder(h=WALL + 182, d=PUMP_D);
            }
    // internal strainer cage
    translate([WALL, cy - STRAINER_W/2, cz - STRAINER_H/2])
        difference() {
            cube([STRAINER_L, STRAINER_W, STRAINER_H]);
            translate([12, 12, 12])
                cube([STRAINER_L - 16, STRAINER_W - 24, STRAINER_H - 24]);
        }
    // external pump body (schematic)
    translate([-220, cy - 90, cz - 90])
        cube([180, 180, 180]);
}

module mezzanine() {
    translate([-MEZZ_L, 0, MEZZ_H])
        cube([MEZZ_L + 80, CSTR_W + 2*WALL, MEZZ_THK]);
    // two posts
    for (y = [WALL, WALL + CSTR_W])
        translate([-MEZZ_L + 40, y, 0])
            cube([80, 80, MEZZ_H]);
}

module hopper_shredder() {
    // hopper above platform, shredder under it, both −X of the tank
    hx = -MEZZ_L + 80;
    hy = WALL + (CSTR_W - HOPPER_W) / 2;
    hz = MEZZ_H + MEZZ_THK + SHRED_H;
    // hopper (inverted frustum as stacked boxes)
    translate([hx, hy, hz])
        cube([HOPPER_L, HOPPER_W, HOPPER_H]);
    // shredder body
    sx = hx + (HOPPER_L - SHRED_L) / 2;
    sy = WALL + (CSTR_W - SHRED_W) / 2;
    translate([sx, sy, MEZZ_H + MEZZ_THK])
        cube([SHRED_L, SHRED_W, SHRED_H]);
    // dust hood over throat
    translate([sx - 20, sy - 20, MEZZ_H + MEZZ_THK + SHRED_H - 20])
        difference() {
            cube([SHRED_L + 40, SHRED_W + 40, 160]);
            translate([20, 20, -1])
                cube([SHRED_L, SHRED_W, 140]);
        }
    translate([sx + SHRED_L/2, sy + SHRED_W/2, MEZZ_H + MEZZ_THK + SHRED_H + 140])
        cylinder(h=200, d=DUST_D);
}

function weir_spout_x() = WALL + CSTR_L + WALL + WEIR_LIP;
function weir_y() = WALL + (CSTR_W - WEIR_W) / 2;
function lift_end_x() = WALL + CSTR_L - 40 + AUGER_LIFT_L * cos(AUGER_INCLINE);
function lift_end_z() = FLOOR + AUGER_TROUGH_H / 2 + AUGER_LIFT_L * sin(AUGER_INCLINE);

module float_dewater() {
    // deck from weir lip +X; solids end is high so liquor drains back to CSTR 1
    x0 = weir_spout_x();
    y0 = weir_y();
    z0 = FLOOR + WEIR_CREST - 20;
    hull() {
        translate([x0, y0, z0])
            cube([30, FDEW_W, FDEW_H]);
        translate([x0 + FDEW_L - 30, y0, z0 + FDEW_RISE])
            cube([30, FDEW_W, FDEW_H]);
    }
    // drain pan under the near end, pitched into the spout
    translate([x0 - 40, y0 + 20, z0 - 50])
        cube([200, FDEW_W - 40, 40]);
}

module sink_dewater() {
    x0 = lift_end_x();
    y0 = WALL + AUGER_OFFSET_Y - SDEW_W / 2;
    z0 = lift_end_z() - 20;
    translate([x0, y0, z0])
        cube([SDEW_L, SDEW_W, SDEW_H]);
    // drain back toward the tank
    translate([x0 - 80, y0 + 20, z0 - 40])
        cube([120, SDEW_W - 40, 30]);
}

module vibratory_split() {
    x0 = lift_end_x() + SDEW_L;
    y0 = WALL + AUGER_OFFSET_Y - SPLIT_W / 2;
    z0 = lift_end_z() - 20;
    translate([x0, y0, z0])
        cube([SPLIT_L, SPLIT_W, SPLIT_H]);
}

module oil_line_stub() {
    // float solids + dense-plastic jumper land here
    xf = weir_spout_x() + FDEW_L;
    yf = weir_y() + (FDEW_W - STUB_W) / 2;
    zf = FLOOR + WEIR_CREST - 20 + FDEW_RISE - 40;
    translate([xf, yf, zf])
        cube([STUB_L, STUB_W, STUB_H]);
    // jumper from split
    xs = lift_end_x() + SDEW_L + SPLIT_L;
    ys = WALL + AUGER_OFFSET_Y + 40;
    zs = lift_end_z();
    hull() {
        translate([xs - 20, ys, zs])
            cube([20, 80, 60]);
        translate([xf, yf + STUB_W/2 - 40, zf + 40])
            cube([20, 80, 60]);
    }
}

module glass_stub() {
    x0 = lift_end_x() + SDEW_L + SPLIT_L;
    y0 = WALL + AUGER_OFFSET_Y - SPLIT_W / 2 - STUB_W - 20;
    z0 = lift_end_z() - 20;
    translate([x0, y0, z0])
        cube([STUB_L, STUB_W, STUB_H]);
}

module vibratory_conveyor() {
    // trough from shredder discharge to lid slot. No screen.
    sx = -MEZZ_L + 80 + (HOPPER_L - SHRED_L) / 2 + SHRED_L;
    sy = drop_y() + (DROP_W - CONV_W) / 2;
    sz = MEZZ_H + MEZZ_THK + 80;
    ex = drop_x();
    ez = FLOOR + CSTR_H + WALL + DROP_COAM;
    len = ex - sx;
    // simple sloped trough
    hull() {
        translate([sx, sy, sz])
            cube([20, CONV_W, CONV_H]);
        translate([ex - 20, sy, ez])
            cube([20, CONV_W, CONV_H]);
    }
}

module mixer_shaft() {
    translate([WALL + CSTR_L*0.55, WALL + CSTR_W*0.55, FLOOR + 80])
        union() {
            cylinder(h=CSTR_H + 200, d=36);
            for (z = [120, 420, 720])
                translate([0, 0, z])
                    cube([CSTR_W*0.35, 8, 40], center=true);
        }
}

module pump_wall_bore() {
    cy = WALL + PUMP_Y;
    cz = FLOOR + PUMP_Z;
    translate([-1, cy, cz])
        rotate([0, 90, 0])
            cylinder(h=WALL + 4, d=PUMP_D);
}

module leach_cstr() {
    color("lightgreen")
    difference() {
        box_shell(CSTR_L, CSTR_W, CSTR_H, WALL, FLOOR);
        weir_cut();
        pump_wall_bore();
    }
    color("orange") weir_spout();
    color("lightgray") trough();
    color("dimgray") floor_auger();
    color("lightgreen") lid();
    color("lightgreen") drop_coaming();
    color("silver") mixer_shaft();
    color("steelblue") leachate_pump();
    color("gainsboro") mezzanine();
    color("slategray") hopper_shredder();
    color("dimgray") vibratory_conveyor();
    color("orange") float_dewater();
    color("gray") sink_dewater();
    color("gray") vibratory_split();
    color("sandybrown") oil_line_stub();
    color("steelblue") glass_stub();
}

leach_cstr();
