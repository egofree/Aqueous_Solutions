// Four locked headers plus a caustic branch. Atmospheres do not mix.
//
// HDR_DUST      negative at hoods (baghouse fan). Fines to CSTR 1.
// HDR_ACID_GAS  negative at CSTR lid + EW anode hoods. HCl / Cl2 / acid mist.
//               Demister → packed NaOH scrubber → ID FRP fan → stack.
//               Pregnant liquor to CRU. Not sewer.
// HDR_H2        negative at cathode hoods, flame arrestor, dryer, stack or fuel.
//               Isolated from oil vapor and acid gas.
// HDR_OIL_VAPOR negative at pyro nozzle → quench → NCG to AFTERBURNER (forced).
//               Not into rotary atmosphere. HX-7 is a jacket, not a duct tee.
// HDR_CAUSTIC   NaOH mist from DIGEST + BMED BASE. Water / dilute-HCl scrubber.
//               Liquor to SALT FEED. Do not dump caustic mist into HDR_ACID_GAS.
// Br2 scrubber stays on the ZnBr2 skid.
include <../params.scad>;
$fn = 28;

module pipe(d, l, axis="z") {
    difference() {
        if (axis=="z") cylinder(h=l, d=d+8);
        if (axis=="x") rotate([0,90,0]) cylinder(h=l, d=d+8);
        if (axis=="y") rotate([-90,0,0]) cylinder(h=l, d=d+8);
        if (axis=="z") translate([0,0,-1]) cylinder(h=l+2, d=d);
        if (axis=="x") rotate([0,90,0]) translate([0,0,-1]) cylinder(h=l+2, d=d);
        if (axis=="y") rotate([-90,0,0]) translate([0,0,-1]) cylinder(h=l+2, d=d);
    }
}

// --- HDR_DUST (induced draft) ---
module baghouse() {
    difference() {
        cube([800, 800, 1600]);
        translate([12, 12, 200]) cube([776, 776, 1380]);
    }
    for (x = [160:160:640])
        for (y = [160:160:640])
            translate([x, y, 220]) cylinder(h=1200, d=80);
    translate([400, 400, 0]) pipe(DUST_D, 80);          // hopper suction in
    translate([400, 800, 1400]) rotate([-90,0,0]) pipe(200, 200); // fan inlet
}

module dust_fan() {
    // FRP ID fan after bags, discharges clean air
    translate([0, 0, 80]) cylinder(h=200, d=360);
    translate([0, 0, 0]) cylinder(h=80, d=200);
}

// --- HDR_ACID_GAS (induced draft, alkaline scrub) ---
module demister() {
    difference() {
        cube([600, 500, 700]);
        translate([12, 12, 12]) cube([576, 476, 680]);
    }
    translate([300, 0, 200]) rotate([90,0,0]) pipe(GAS_D, 80);
    translate([300, 500, 550]) rotate([-90,0,0]) pipe(GAS_D, 80);
}

module packed_alk_scrubber() {
    // PP / FRP tower, 50 mm saddles, NaOH from BMED BASE
    difference() {
        cylinder(h=1800, d=700);
        translate([0, 0, 12]) cylinder(h=1780, d=676);
    }
    for (z = [250:200:1400])
        translate([0, 0, z])
            difference() {
                cylinder(h=10, d=660);
                cylinder(h=10, d=80);
            }
    // lean NaOH in, pregnant out to CRU
    translate([350, 0, 1600]) rotate([0,90,0]) pipe(40, 120);
    translate([350, 0, 80]) rotate([0,90,0]) pipe(40, 120);
    translate([0, 0, 1800]) pipe(GAS_D, 80); // gas out to fan
}

module acid_id_fan() {
    // FRP, downstream of scrubber, pulls the whole acid-gas header negative
    cylinder(h=280, d=400);
    translate([200, 0, 140]) rotate([0,90,0]) pipe(200, 200);
}

module stack(h=3200, d=360) {
    difference() {
        cylinder(h=h, d=d+16);
        translate([0, 0, -1]) cylinder(h=h+2, d=d);
    }
}

// --- HDR_H2 ---
module flame_arrestor() {
    // DN80 deflagration arrestor, cathode header
    difference() {
        union() {
            cylinder(h=40, d=140);
            translate([0, 0, 40]) cylinder(h=120, d=110);
            translate([0, 0, 160]) cylinder(h=40, d=140);
        }
        translate([0, 0, -1]) cylinder(h=202, d=GAS_D);
    }
}

module h2_dryer() {
    difference() {
        cube([700, 500, 900]);
        translate([12, 12, 12]) cube([676, 476, 880]);
    }
    translate([80, 250, 200]) rotate([0,90,0]) pipe(GAS_D, 80);
    translate([620, 250, 700]) rotate([0,90,0]) pipe(GAS_D, 80);
}

// --- HDR_CAUSTIC (separate from acid-gas) ---
module caustic_scrubber() {
    // Water + BMED ACID trim. Liquor to SALT FEED.
    difference() {
        cylinder(h=1400, d=500);
        translate([0, 0, 12]) cylinder(h=1380, d=476);
    }
    translate([250, 0, 1200]) rotate([0,90,0]) pipe(32, 100);
    translate([250, 0, 80]) rotate([0,90,0]) pipe(32, 100);
}

// --- HDR_OIL_VAPOR ---
module ncg_knockout() {
    difference() {
        cylinder(h=900, d=400);
        translate([0, 0, 12]) cylinder(h=880, d=376);
    }
}

module mfg_gas_handling() {
    // row 1: dust
    baghouse();
    translate([1000, 400, 1400]) dust_fan();
    translate([1400, 400, 0]) stack(h=8000, d=250);  // dust, AQS-GAS-003

    // row 2: acid gas
    translate([0, 1200, 0]) {
        demister();
        translate([900, 250, 0]) packed_alk_scrubber();
        translate([1500, 250, 1600]) acid_id_fan();
        translate([1900, 250, 0]) stack(h=12000, d=360); // acid, AQS-GAS-003
    }

    // row 3: hydrogen
    translate([0, 2400, 0]) {
        flame_arrestor();
        translate([300, -250, 0]) h2_dryer();
        translate([1200, 0, 0]) stack(h=8000, d=250);   // H2, AQS-GAS-003
    }

    // row 4: caustic
    translate([0, 3400, 0]) {
        caustic_scrubber();
        translate([600, 0, 0]) stack(h=6000, d=160);
    }

    // row 5: oil vapor NCG knockout (afterburner is a separate unit)
    translate([800, 3400, 0]) ncg_knockout();
}

mfg_gas_handling();
