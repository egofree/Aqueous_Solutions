// True helix flight for CSTR 3. Replaces the FreeCAD paddle proxy.
include <../params.scad>;
$fn = 24;

module flight(length) {
    turns = length / AUGER_PITCH;
    union() {
        cylinder(h=length, d=AUGER_SHAFT);
        linear_extrude(height=length, twist=360*turns, slices=max(24, turns*12), convexity=8)
            translate([AUGER_D*0.28, 0, 0])
                circle(d=AUGER_D*0.22);
    }
}

flight(CSTR_L - 140);
