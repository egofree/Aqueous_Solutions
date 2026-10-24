#!/usr/bin/env python3
"""Rev M: close the eleven Rev L open balances. Sized to the neighbor draw."""
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]   # repository root
GRAPH = ROOT / "flow_graph/plant_flow_graph.json"

H2_FC = 4.8          # continuous fuel cell, authority
H2_MEOH = 0.94       # continuous methanol synthesis
H2_POOL = H2_FC + H2_MEOH  # 5.74; genset is standby, not a design-day draw
NAOH_MOL = 593.0     # glass digest, AQS-DUTY-010
RESIN_MOL = 0.5      # IA-BMED-02
BASE_MOL = NAOH_MOL + RESIN_MOL
# 20 wt% liquor. Digest takes it. 2 M would demand a water plant the condensate cannot feed.
BASE_SOL = BASE_MOL * 0.040 / 0.20
ACID_MOL = BASE_MOL
ACID_SOL = ACID_MOL * 0.03646 / 0.20
ACID_USERS = 9.2772 + 0.6456
ACID_REGEN = ACID_SOL - ACID_USERS
BRINE = 229.4        # leach bleed, by difference in Rev L, now an edge
BLOWDOWN = 27.3623
WATER_MAKE = (BASE_SOL + ACID_SOL) - (BRINE + BLOWDOWN)
CO2_FOLD = 0.554     # S11 carbon, missing from the DUTY-008 basis
Q4_SURPLUS = 3.3167
PV_AVG = 11.59       # closes the inverter at the rectifier continuous rating
GREY_SLUDGE = 5.5    # 110 in - 104.5 out
ZNBR_BLEED = 8.437


def edge(g, sid):
    for e in g["edges"]:
        if e["stream_id"] == sid:
            return e
    raise KeyError(sid)


def node(g, uid):
    for n in g["nodes"]:
        if n["unit_id"] == uid:
            return n
    raise KeyError(uid)


def set_rate(e, value, unit, note):
    e["rate"] = {"value": round(value, 4), "unit": unit, "status": "study", "note": note}
    e["presence"] = "present"


def clone(template, sid, frm, to, phase, layers, carries, value, unit, note):
    e = deepcopy(template)
    e["stream_id"] = sid
    e["from_unit_id"] = frm
    e["to_unit_id"] = to
    e["phase"] = phase
    e["layers"] = layers
    e["carries"] = carries
    e["presence"] = "present"
    e["namespace"] = "IA" if sid.startswith("IA") else "S"
    e["open_boundary"] = False
    e["notes"] = None
    e["gap_flags"] = []
    set_rate(e, value, unit, note)
    return e


def main():
    g = json.loads(GRAPH.read_text())
    tmpl = edge(g, "S05")
    note = "AQS-DUTY-011 Rev M. Sized to the continuous neighbor draw."

    # one dryer product. S64 is the same pipe as S05.
    s64 = edge(g, "S64")
    s64["presence"] = "placeholder"
    s64["rate"]["note"] = "Retired Rev M. Alias of S05. One dryer, one product."
    set_rate(edge(g, "S05"), H2_POOL, "kg/d", note + " FC 4.8 + MeOH 0.94. Genset not on the design day.")
    set_rate(edge(g, "IA-HDR-H2-02"), H2_POOL, "kg/d", note + " Dryer inlet equals the pool.")
    share = H2_POOL / 3
    for sid in ("IA-HDR-H2-01", "IA-HDR-H2-03", "IA-HDR-H2-04"):
        set_rate(edge(g, sid), share, "kg/d", note + " Hood share of the 5.74 kg/d pool.")
    edge(g, "S45")["rate"] = {
        "value": 0.0, "unit": "kg/d", "status": "study",
        "note": note + " Standby. Not a design-day draw. Fuel cell and MeOH take the pool.",
    }
    set_rate(edge(g, "S49"), H2_FC, "kg/d", note + " Continuous fuel cell.")
    set_rate(edge(g, "S74"), H2_MEOH, "kg/d", note + " Continuous methanol synthesis.")

    # grey water lands on the treatment tank
    s12 = edge(g, "S12")
    s12["to_unit_id"] = "GREY_TREAT"
    set_rate(s12, 110.0, "kg/d", note + " Retargeted off NUTRIENT_DOSE.")
    g["edges"].append(clone(
        tmpl, "IA-GREY-01", "GREY_TREAT", "LEACH_CSTR_1", "S/L", ["mass"],
        "grey sludge", GREY_SLUDGE, "kg/d", note + " 110 in, 104.5 treated out.",
    ))

    # CRU is chlorate only. Acid and base are sized to the digest, as 20 wt% liquor.
    # 2 M would need a water plant the condensate cannot feed.
    edge(g, "IA-BMED-03")["from_unit_id"] = "LEACH_CSTR_1"
    edge(g, "IA-BMED-04")["from_unit_id"] = "LEACH_CSTR_1"
    set_rate(edge(g, "IA-BMED-03"), ACID_SOL, "kg/d",
             note + " 593.5 mol/d HCl as 20 wt%. Brine from the leach bleed.")
    set_rate(edge(g, "IA-BMED-04"), BASE_SOL, "kg/d",
             note + " 593.5 mol/d NaOH as 20 wt%. Digest takes 593 mol/d.")
    g["edges"].append(clone(
        tmpl, "IA-CRU-01", "CRU", "LEACH_CSTR_1", "L", ["mass"],
        "sodium chlorate liquor", BLOWDOWN, "kg/d",
        note + " CRU re-scoped to chlorate. Closes on S66.",
    ))
    g["edges"].append(clone(
        tmpl, "IA-ACID-01", "BMED_ACID", "LEACH_CSTR_1", "L", ["mass"],
        "regen HCl, 20 wt%", ACID_REGEN, "kg/d",
        note + " Acid not taken by the wet bench or the resin exchange.",
    ))
    g["edges"].append(clone(
        tmpl, "IA-BASE-01", "BMED_BASE", "GLASS_DIGEST", "L", ["mass"],
        "digest NaOH, 20 wt%", BASE_SOL - 0.27, "kg/d",
        note + " 593 mol/d. Resin exchange keeps IA-BMED-02.",
    ))

    # UPW short 7.2 kg/d. Raise distillate to the polish outlet.
    set_rate(edge(g, "S25"), 168.22, "kg/d", note + " Matches polish outlets. VCD feed raised.")
    vcd = node(g, "VCD_TRAIN")
    vcd.setdefault("params", {})["feed_m3_d"] = 0.187

    # Q4 surplus to a dry cooler. Not an ORC. 3.3 kW is below a useful expander.
    g["edges"].append(clone(
        tmpl, "HL-Q4-REJ", "Q4_BUS", "GEO_ORC", "thermal", ["energy"],
        "Q4 surplus heat", Q4_SURPLUS, "kW",
        note + " Dry-cooler duty. ORC is not justified at 3.3 kW.",
    ))

    # inverter: continuous rectifier, farm load in the right direction, PV closes the bus
    s20 = edge(g, "S20")
    s20["from_unit_id"] = "SOL_ARK_60K"
    s20["to_unit_id"] = "GROW_BED"
    set_rate(s20, 5.0, "kW", note + " Direction reversed. Power flows to the farm.")
    set_rate(edge(g, "S17"), 12.0, "kW", note + " Rectifier continuous rating, not the 50 kW peak.")
    g["edges"].append(clone(
        tmpl, "IA-PV-01", "PV_ARRAY", "SOL_ARK_60K", "electric", ["energy"],
        "PV daily average", PV_AVG, "kW",
        note + " Closes the bus at the continuous loads. Peak is a separate rating.",
    ))

    # zinc-bromine water accumulation
    g["edges"].append(clone(
        tmpl, "IA-ZNBR-BD", "ZNBR2", "GREY_TREAT", "L", ["mass"],
        "electrolyte bleed", ZNBR_BLEED, "kg/d",
        note + " Purge-air water and NaOH make-up. Stops the accumulation.",
    ))

    # afterburner carbon into the header the farm already takes
    s85 = edge(g, "S85")
    set_rate(s85, s85["rate"]["value"] + CO2_FOLD, "kg/d", note + " S11 carbon folded in.")
    s89 = edge(g, "S89")
    set_rate(s89, s89["rate"]["value"] + CO2_FOLD, "kg/d", note + " Header passes the folded carbon to the beds.")

    g["revision"] = "M"
    g["date"] = "2026-10-09"
    g["notes_rev_m"] = {
        "doc": "AQS-DUTY-011",
        "retired": ["S64 alias of S05"],
        "retarget": ["S12 to GREY_TREAT", "S20 reversed"],
        "added": ["IA-GREY-01", "IA-CRU-01", "IA-ACID-01", "IA-BASE-01", "HL-Q4-REJ", "IA-PV-01", "IA-ZNBR-BD"],
        "h2_pool_kg_d": H2_POOL,
        "bmed_mol_d": BASE_MOL,
    }
    GRAPH.write_text(json.dumps(g, indent=2) + "\n")
    print("wrote", GRAPH, "edges", len(g["edges"]))


if __name__ == "__main__":
    main()
