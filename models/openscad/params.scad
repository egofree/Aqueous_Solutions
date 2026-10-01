// Shared millimetre parameters. Keep in lockstep with freecad/params.py.
// Module scale: 150 kg/day wet train. Walls are CPVC sheet, not metal.

$fn = 36;

WALL        = 12;     // CPVC sheet thickness
FLOOR       = 16;     // floor plate (trough sits on this)

// LEACH CSTR 1 — inside liquor box
CSTR_L      = 2000;
CSTR_W      = 1200;
CSTR_H      = 1400;   // liquid + freeboard
FREEBOARD   = 200;

// CSTR 2 weir (same vessel, +X wall)
WEIR_W      = 450;
WEIR_CREST  = CSTR_H - FREEBOARD;   // from inner floor
WEIR_SLOT_H = 80;
WEIR_LIP    = 120;    // external spout projection

// CSTR 3 floor auger — injection-molded PVC / FG
AUGER_D     = 140;    // flight OD
AUGER_SHAFT = 40;
AUGER_PITCH = 110;
AUGER_TROUGH_W = 180;
AUGER_TROUGH_H = 110;
AUGER_OFFSET_Y = 280; // trough centreline from inner -Y wall
AUGER_INCLINE  = 28;  // deg, lifts out of liquor toward +X

// mixer / nozzles (lid)
MIXER_D     = 50;
GAS_D       = 80;     // acid-gas takeoff
DROP_X      = 80;     // inner-X of shred drop slot
DROP_L      = 400;
DROP_W      = 250;
DROP_COAM   = 80;     // raised coaming around the slot

// LEACHATE PUMP / coarse strainer — −X wall, opposite the weir
PUMP_D      = 80;     // DN80
PUMP_Z      = 450;    // centreline above inner floor (submerged)
PUMP_Y      = 900;    // centreline from inner −Y (away from auger)
STRAINER_L  = 180;
STRAINER_W  = 140;
STRAINER_H  = 160;

// mezzanine feed train
MEZZ_H      = 2200;   // platform top above tank outer floor
MEZZ_L      = 1600;   // platform length in −X
MEZZ_THK    = 12;
HOPPER_L    = 700;
HOPPER_W    = 600;
HOPPER_H    = 800;
SHRED_L     = 500;
SHRED_W     = 500;
SHRED_H     = 450;
CONV_W      = 240;
CONV_H      = 120;
CONV_PLATE  = 6;      // trough plate
CONV_FLANGE = 40;
CONV_SPRING_D = 50;
CONV_SPRING_H = 80;
CONV_BOLT   = 10;     // M10 clearance
CONV_LEN    = 1800;   // default standalone length; plant instance is computed
DUST_D      = 150;    // dust-hood outlet to DUST header
AUGER_LIFT_L = 700;

// dewater belts + split (Phase A 4–6)
FDEW_L      = 1800;
FDEW_W      = 450;
FDEW_H      = 80;
FDEW_RISE   = 120;    // solids end higher so liquor runs back to weir
SDEW_L      = 1400;
SDEW_W      = 220;
SDEW_H      = 80;
SPLIT_L     = 600;
SPLIT_W     = 500;
SPLIT_H     = 400;
STUB_L      = 400;
STUB_W      = 300;
STUB_H      = 250;

// EW funnel cell
EW_L        = 600;    // along aisle (overflow direction)
EW_W        = 420;    // anode-cathode depth
EW_H        = 650;    // rectangular body
EW_FUNNEL_H = 220;
EW_VALVE_D  = 50;
EW_VALVE_L  = 60;
EW_MEM_T    = 4;      // CEM
EW_SLOT     = 10;     // membrane cassette slot
EW_PITCH    = 750;    // aisle spacing, centre to centre
AISLE_X0    = 200;
AISLE_Y     = -(EW_W + 2*WALL) - 400;
AISLE_Z     = 400;
BUND_H      = 150;
BUND_PAD    = 250;
SUMP_L      = 400;
SUMP_W      = 400;
SUMP_H      = 300;
VDF_D       = 700;
VDF_L       = 900;
PAIL_W      = 180;
HDR_D       = 80;
HDR_Z       = 1400;
PYRO_D      = 320;
PYRO_L      = 2800;

// Campus envelopes — lockstep with freecad/params.py
FARM_X=12000; FARM_Y=8000; FARM_L=12000; FARM_W=8000; FARM_H=4500;
FAB_X=12000;  FAB_Y=-6000; FAB_L=8000;   FAB_W=6000;  FAB_H=4000;
HAB_X=-8000;  HAB_Y=8000;  HAB_L=8000;   HAB_W=6000;  HAB_H=3200;
CRYO_X=-6000; CRYO_Y=-4000; CRYO_L=4000; CRYO_W=3000; CRYO_H=3000;
MFG_X=2000;   MFG_Y=9000;  MFG_L=6000;   MFG_W=4000;  MFG_H=3500;

LIFE_Z_GREY=900; LIFE_Z_UPW=1100; LIFE_Z_ETCH=1300;
LIFE_Z_O2=2800; LIFE_Z_N2=3000; LIFE_Z_CO2=3200;
LIFE_D_GREY=50; LIFE_D_UPW=40; LIFE_D_ETCH=32;
LIFE_D_GAS=25; LIFE_D_CO2=40;
