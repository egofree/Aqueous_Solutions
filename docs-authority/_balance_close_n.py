#!/usr/bin/env python3
"""Rev N: close the remaining both-sided gaps and retire the relief alias."""
import json
from copy import deepcopy
from pathlib import Path

GRAPH = Path("/tmp/Aqueous_Solutions/flow_graph/plant_flow_graph.json")
NOTE = "AQS-DUTY-012 Rev N. Missing product or return, sized to the neighbor."


def edge(g, sid):
    for e in g["edges"]:
        if e["stream_id"] == sid:
            return e
    raise KeyError(sid)


def add(g, tmpl, sid, frm, to, phase, layers, carries, value, unit):
    e = deepcopy(tmpl)
    e.update(stream_id=sid, from_unit_id=frm, to_unit_id=to, phase=phase,
             layers=layers, carries=carries, presence="present",
             namespace="IA" if sid.startswith("IA") else "S",
             open_boundary=False, notes=None, gap_flags=[])
    e["rate"] = {"value": round(value, 4), "unit": unit, "status": "study", "note": NOTE}
    g["edges"].append(e)


def main():
    g = json.loads(GRAPH.read_text())
    tmpl = edge(g, "S05")

    # plated metal leaves each cell. The liquor drop is the sheet.
    drops = [59.87, 59.89, 22.48, 4.85, 5.02, 5.47, 71.14, 5.05, 61.34]
    for i, drop in enumerate(drops, 1):
        add(g, tmpl, f"IA-EW-MET-{i}", f"EW_{i}", "MFG_SHOP", "S", ["mass"],
            "plated sheet", drop, "kg/d")

    # recycle does not create mass
    rec = edge(g, "IA-REC-01")
    rec["rate"]["value"] = edge(g, "IA-POL-02")["rate"]["value"]
    rec["rate"]["note"] = NOTE + " Recycle out equals polish return. DN80, 0.4 m/s."

    # polish drop is the cake, not a liquor loss
    pol_in = edge(g, "IA-EW-09")["rate"]["value"]
    pol_out = edge(g, "IA-POL-02")["rate"]["value"]
    add(g, tmpl, "IA-POL-CAKE", "POLISH_BANK", "BOUNDARY_EXPORT", "S", ["mass"],
        "polish cake", pol_in - pol_out, "kg/d")

    # flue air in, exhaust out, CO2 credit carries the farm-trim carbon
    flue = edge(g, "S67")["rate"]["value"]
    add(g, tmpl, "IA-AB-AIR", "CRYO_N2", "AFTERBURNER_FLUE", "G", ["mass"],
        "combustion air", flue - 5.8, "kg/d")
    add(g, tmpl, "IA-FLUE-EXH", "FLUE_KO", "BOUNDARY_EXPORT", "G", ["mass"],
        "flue exhaust", flue - edge(g, "S67B")["rate"]["value"], "kg/d")
    edge(g, "S67B")["rate"]["value"] = round(edge(g, "S67B")["rate"]["value"] + 0.554, 4)
    edge(g, "S67B")["rate"]["note"] = NOTE + " Farm-trim carbon included."

    # digest liquor and mill loss
    add(g, tmpl, "IA-DIG-LIQ", "GLASS_DIGEST", "LEACH_CSTR_1", "L", ["mass"],
        "silicate liquor", 118.43, "kg/d")
    add(g, tmpl, "IA-MILL-LOSS", "GLASS_MILL", "BOUNDARY_EXPORT", "S", ["mass"],
        "mill dust", 6.82, "kg/d")

    # shop goods, including the new sheet
    add(g, tmpl, "IA-MFG-OUT", "MFG_SHOP", "BOUNDARY_EXPORT", "S", ["mass"],
        "finished goods", 39.89 + sum(drops), "kg/d")

    # habitation gap is water to grey. Grey sludge rises with it.
    s12 = edge(g, "S12")
    s12["rate"]["value"] = round(s12["rate"]["value"] + 21.38, 4)
    s12["rate"]["note"] = NOTE + " Includes the unedged habitation water."
    edge(g, "IA-GREY-01")["rate"]["value"] = round(edge(g, "IA-GREY-01")["rate"]["value"] + 21.38, 4)

    # bed water and methanol water
    add(g, tmpl, "IA-BED-H2O", "ROOF_TANK", "GROW_BED", "L", ["mass"],
        "irrigation", 16.70, "kg/d")
    add(g, tmpl, "IA-MEOH-H2O", "MEOH_SYNTH", "MEOH_COND", "L", ["mass"],
        "synth water", 2.84, "kg/d")
    add(g, tmpl, "IA-FC-AIR", "CRYO_O2", "MEOH_FC", "G", ["mass"],
        "cell air", 7.50, "kg/d")

    # HX-8 legs are one duty, not two
    hx = edge(g, "IA-HX8")["rate"]["value"] / 2
    for sid in ("HL-HX8-Q4-A", "HL-HX8-Q4-B"):
        edge(g, sid)["rate"]["value"] = round(hx, 4)
        edge(g, sid)["rate"]["note"] = NOTE + " Split of the 4.572 kW cell duty."

    # Q3 cannot supply the leach heater. Electric trim covers the short.
    add(g, tmpl, "IA-Q3A-TRIM", "RECTIFIER", "Q3_A", "electric", ["thermal"],
        "leach heater trim", 10.048, "kW")
    add(g, tmpl, "IA-Q3B-TRIM", "RECTIFIER", "Q3_B", "electric", ["thermal"],
        "leach heater trim", 10.048, "kW")

    # fuel cell at the top of the PEM band, not 60 %
    edge(g, "S51")["rate"]["value"] = 3.46
    edge(g, "S51")["rate"]["note"] = NOTE + " 0.52 of the 6.66 kW LHV. Band is 0.50-0.55."

    # methanol cell to the bottom of its requirement. Synthesis scaled with it.
    edge(g, "S76")["rate"]["value"] = 8.53
    edge(g, "S75")["rate"]["value"] = 8.53
    edge(g, "S74")["rate"]["value"] = 1.60
    edge(g, "S05")["rate"]["value"] = 6.40
    edge(g, "IA-HDR-H2-02")["rate"]["value"] = 6.40
    for sid in ("IA-HDR-H2-01", "IA-HDR-H2-03", "IA-HDR-H2-04"):
        edge(g, sid)["rate"]["value"] = round(6.40 / 3, 4)
    edge(g, "S79")["rate"]["value"] = 0.50
    edge(g, "S79")["rate"]["note"] = NOTE + " Bottom of the 0.5-2 kW band. Fuel 8.53 kg/d."

    # one relief line
    edge(g, "S86")["presence"] = "placeholder"
    edge(g, "S86")["rate"]["note"] = "Retired Rev N. Alias of S56."

    # inverter close at the new fuel-cell and PV figures
    # sources: hydro 0.2917 + znbr 5 + gen 2.5 + fc 3.46 + meoh 0.50 + pv
    # loads: znbr chg 6.6667 + rectifier 12 + farm 5 = 23.6667
    # pv = 23.6667 - (0.2917+5+2.5+3.46+0.50) = 11.915
    edge(g, "IA-PV-01")["rate"]["value"] = 11.915
    edge(g, "IA-PV-01")["rate"]["note"] = NOTE + " Closes the bus at the 0.52 fuel cell."

    g["revision"] = "N"
    g["date"] = "2026-10-09"
    g["notes_rev_n"] = {"doc": "AQS-DUTY-012", "alias_retired": "S86"}
    GRAPH.write_text(json.dumps(g, indent=2) + "\n")
    print("edges", len(g["edges"]))


if __name__ == "__main__":
    main()
