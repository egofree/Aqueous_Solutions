# Path modules on the frame

Document number: AQS-PATH-001
Revision: A
Date: 2026-10-11
Not a PE stamp.

Each module is a frame from AQS-MOD-001 Rev C plus the process. The script is `models/freecad/process_modules.py`.

Lathe. Dry frame, 1200 × 600 × 800, A500, 100 × 100 × 6. Bed on the top rails. Swing 300 mm, centers 750 mm, 1.1 kW. It cuts the shafts for the next lathe.

Electrowinning. Wet frame, 316L. Plate count is the parameter. EW-1 is 21 plates at 50 mm, rack 1250 mm, frame 1400 mm. Current 2105 A at 200 A/m². Cathode 316L, anode titanium with 0.5 mm PbO₂.

Furnace. Hot frame, A500, 1200 mm. Crucible 200 mm ID, 250 mm tall. Coil 15 turns, 35.5 µH, 7.1 µF at 10 kHz, 10 kW. Melt 50 kg steel in 12.6 h at 40% coupling.

Silicon reduction. Same frame and coil. Charge 0.086 kg silica and 0.034 kg char for 0.04 kg silicon. Energy 0.52 kWh. Off-gas to the afterburner.

Aligner. Clean frame, 6061, 1200 mm. Stage 100 mm, 10 µm, leadscrew cut on the lathe. Dose 200 mJ/cm² at 365 nm.

Electronics bay. Six clean frames at 1400 mm pitch: coat, align, develop, etch, strip, probe. Minimum line 100 µm. First device is a diode.
