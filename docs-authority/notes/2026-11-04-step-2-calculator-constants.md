# Step 2: calculator constants moved to drivers

Date: 2026-11-04

The named design constants of the four study calculators now come from
``flow_graph/param/drivers.json`` (read with ``flow_graph.param.drivers.val``):

- ``docs-authority/_rect_ew_sizing.py``: the rectifier channel frame list
  (``rect_channel_frame_sizes_A``), the 1.10 margin (``rect_channel_margin``),
  the 6.0 V channel rating (``rect_channel_rated_V``) and the 200 A/cm2
  busbar density (``rect_busbar_J_A_cm2``, shop rule of AQS-PWR-001).
  Cell voltage, bus drop and efficiency were already drivers.
- ``docs-authority/_ew_sizing.py``: the IA-EW-SHEET collection point
  (``ew_sheet_collection_cell`` = 9). The element table ``EL`` is physical
  data; its molar masses match ``flow_graph.param.constants.M`` exactly and
  the valences have no other table, so it stays in the calculator as a
  candidate for a later constant-home pass.
- ``flow_graph/param/specialty_sizing.py``: the Si draw (``si_kgd``), the PEM
  window (``ely_window_h``, pre-existing), the PEM stack point (``pem_stack_j_A_cm2``,
  ``pem_stack_v_cell_V``, ``pem_stack_cells``), the design-block H2 rate
  (``elyz_h2_design_kg_d``), the DN80 bed radius (``elyz_bed_radius_m``) and
  the baghouse capture-air basis (``baghouse_*``, A-M-458). The Si draw is a
  single driver so that the value stays byte-identical: 3 divided by 0.6
  twice is not the same float as the literal 1.8. The text "1.8 kg/d Si" is
  derived from the value. Envelope lists and text-bonded records keep their
  basis in the adjacent string.
- ``flow_graph/param/stub_activation.py``: the develop-bench duty, the blow
  molder motor class, the electrode-coat booth and cure, the RAD_PANEL duty
  (from the pre-existing ``GEO.orc-train.q_sink_kW``, 12 kW_th, A-M-244
  context), the LIO_BAT storage duty and the ORC feed pump. Rates, envelopes
  and design-record entries keep their issued values; the computed duties
  now read the drivers. The GEO_ORC 12 kW_th context already came from the
  pre-existing ``GEO.orc-train.q_sink_kW`` and ``GEO.orc-train.eta_th``.

Every driver carries a reference key or an A-M register entry. The new
``A-M-466`` registers the Si draw. The new
``flow_graph/param/test_calculator_literals.py`` fails while any of the four
calculators assigns a bare numeric design constant. Generated outputs are
unchanged; ``scripts/check_all.sh --full`` passes with no regeneration diff.

No value disagreement was found. One numeral needs care: the busbar density
200 A/cm2 (AQS-PWR-001) and the EW cathode current density 200 A/m2
(SCHLESINGER2011) share the digits 200 but are different quantities in
different units. The code value governs the busbar; the cathode driver is
untouched.
