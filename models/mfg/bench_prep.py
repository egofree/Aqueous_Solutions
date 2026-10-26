"""FLUX_PREP / WAX_PATTERN bench manufacturing models, AQS-PLAN-006 work order
(X-MFG lane, FOUNDRY-FLUX_PREP-10 / FOUNDRY-WAX_PATTERN-10 M3).

Graph revision AC. Study. Not a PE stamp. Reads params.json only.
Shared bench frame (800 x 600, work top at z 900, extraction hood above): the
salt-flux preparation bench (20 L hopper, 0.1 kW mixer) and the wax pattern
injection bench (10 L pot, 0.5 kW injector). Nozzle hardware per each unit's
task-04 schedule. No measured rate is claimed anywhere.

Run: $CADQUERY_PYTHON <this file> [FLUX_PREP|WAX_PATTERN]
"""
import csv, json, math, pathlib, sys
import cadquery as cq

HERE = pathlib.Path(__file__).parent
L, W, H = 800, 600, 1200
TOP = 900.0
DN15, W15 = 10.65, 2.0

def box(x, y, z, dx, dy, dz):
    return cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))

def tube(r_out, r_in, p, axis, ln):
    d = {"X": ((1, 0, 0), (0, 1, 0)), "Y": ((0, 1, 0), (1, 0, 0)), "Z": ((0, 0, 1), (1, 0, 0))}[axis]
    pl = cq.Plane(origin=p, xDir=d[1], normal=d[0])
    return cq.Workplane(pl).circle(r_out).circle(r_in).extrude(ln)

def rod(r, p, axis, ln):
    return tube(r, 0, p, axis, ln)

def bench_frame():
    parts = {}
    frame = None
    for (px, py) in ((0, 0), (L - 50, 0), (0, W - 50), (L - 50, W - 50)):
        q = box(px, py, 0, 50, 50, 850)
        frame = q if frame is None else frame.union(q)
    parts["bench_frame"] = frame
    parts["work_top"] = box(0, 0, 850, L, W, 50)                       # work top z 850..900
    hood = box(150, 100, 1050, 500, 400, 30).union(box(180, 130, 900, 440, 340, 150))
    parts["extraction_hood"] = hood
    parts["vent_stub"] = tube(DN15, DN15 - W15, (400.0, 300.0, 1080.0), "Z", 120)   # vent to the z 1200 datum
    parts["drain_well"] = tube(30.5, DN15, (400, 300, 0), "Z", 50)
    return parts

_LAST_PARTS = None


def build_flux_prep(unit):
    P = json.loads((HERE / unit / "params.json").read_text())
    parts = bench_frame()
    parts["hopper"] = cone = cq.Workplane("XY").circle(150).workplane(offset=250).circle(70).loft(ruled=True).translate((280, 200, 650))
    parts["mixer"] = rod(45.0, (280, 200, 900), "Z", 180).union(rod(12.0, (280, 200, 1080), "Z", 40))
    parts["mix_stage"] = box(430.0, 150.0, 900.0, 180.0, 300.0, 40)
    parts["flux_chute"] = box(690.0, 200.0, 700.0, 60.0, 200.0, 200)   # N1 +X z 600..900
    parts["salt_inlet"] = box(-30.0, 120.0, 130.0, 40.0, 120.0, 60)    # N2 -X z 160
    parts["mgcl2_inlet"] = box(-30.0, 320.0, 130.0, 40.0, 120.0, 60)   # N3 -X z 160
    EXTERNAL = ("flux_chute", "salt_inlet", "mgcl2_inlet")
    rho = {"bench_frame": 7.85e-6, "work_top": 7.85e-6, "extraction_hood": 7.85e-6,
           "vent_stub": 7.85e-6, "drain_well": 7.85e-6, "hopper": 7.85e-6, "mixer": 7.85e-6,
           "mix_stage": 7.85e-6, "flux_chute": 7.85e-6, "salt_inlet": 7.85e-6, "mgcl2_inlet": 7.85e-6}
    bom = [
      ["1", "Bench frame 800 x 600, work top z 850..900", 1, "carbon steel",
       round(parts["bench_frame"].val().Volume() * 7.85e-6, 1) + round(parts["work_top"].val().Volume() * 7.85e-6, 1),
       "make", "WORK_ORDER step 1; AQS-DUTY-072 bench_prep class"],
      ["2", "Extraction hood with the N-vent stub", 1, "carbon steel",
       round(parts["extraction_hood"].val().Volume() * 7.85e-6, 1) + round(parts["vent_stub"].val().Volume() * 7.85e-6, 1),
       "make", "task-04 schedule N5"],
      ["3", "Flux hopper 20 L cone + 0.1 kW mixer stage", 1, "CS + carbon steel",
       round(parts["hopper"].val().Volume() * 7.85e-6 + parts["mixer"].val().Volume() * 8.96e-6 + parts["mix_stage"].val().Volume() * 7.85e-6, 1),
       "make", f"design hopper 20 L, mixer 0.1 kW; {P['design']['salt_kg_d']} kg/d salt batch"],
      ["4", "N1 flux discharge chute +X z 600", 1, "carbon steel", parts["flux_chute"].val().Volume() * 7.85e-6,
       "make", "task-04 schedule N1 (solids, bore not calculated)"],
      ["5", "N2/N3 inlet chutes -X z 160 (digester salts; MgCl2 drag-out from TI_CELL N7)", 2,
       "carbon steel", round((parts["salt_inlet"].val().Volume() + parts["mgcl2_inlet"].val().Volume()) * 7.85e-6, 1),
       "make", "task-04 schedule N2/N3; A-M-284 feedstock ruling"],
      ["6", "N4 drain well", 1, "carbon steel", parts["drain_well"].val().Volume() * 7.85e-6, "make",
       "task-04 schedule N4"],
    ]
    return P, parts, {}, EXTERNAL, rho, bom

def build_wax_pattern(unit):
    P = json.loads((HERE / unit / "params.json").read_text())
    parts = bench_frame()
    parts["wax_pot"] = tube(110.0, 98.0, (280.0, 300.0, 700.0), "Z", 200)          # 10 L pot
    parts["injector_head"] = rod(60.0, (280.0, 300.0, 900.0), "Z", 160)
    parts["pattern_table"] = box(430.0, 150.0, 900.0, 220.0, 300.0, 40)
    parts["condensate_trap"] = box(-30.0, 120.0, 130.0, 40.0, 120.0, 60)           # N2 -X z 160
    parts["makeup_hopper"] = box(-30.0, 320.0, 130.0, 40.0, 120.0, 60)             # N3 -X z 160
    parts["pattern_chute"] = box(690.0, 200.0, 700.0, 60.0, 200.0, 200)            # N1 +X z 600..900
    EXTERNAL = ("pattern_chute", "condensate_trap", "makeup_hopper")
    rho = {"bench_frame": 7.85e-6, "work_top": 7.85e-6, "extraction_hood": 7.85e-6,
           "vent_stub": 7.85e-6, "drain_well": 7.85e-6, "wax_pot": 7.85e-6, "injector_head": 7.85e-6,
           "pattern_table": 7.85e-6, "condensate_trap": 7.85e-6, "makeup_hopper": 7.85e-6,
           "pattern_chute": 7.85e-6}
    bom = [
      ["1", "Bench frame 800 x 600, work top z 850..900", 1, "carbon steel",
       round(parts["bench_frame"].val().Volume() * 7.85e-6 + parts["work_top"].val().Volume() * 7.85e-6, 1),
       "make", "WORK_ORDER step 1; AQS-DUTY-072 bench_prep class"],
      ["2", "Extraction hood with the N5 vent stub", 1, "carbon steel",
       round(parts["extraction_hood"].val().Volume() * 7.85e-6 + parts["vent_stub"].val().Volume() * 7.85e-6, 1),
       "make", "task-04 schedule N5"],
      ["3", f"Wax pot 10 L with the 0.5 kW injector head", 1, "CS + heater class",
       round(parts["wax_pot"].val().Volume() * 7.85e-6 + parts["injector_head"].val().Volume() * 7.85e-6, 1),
       "make", f"design pot 10 L, injector 0.5 kW; {P['design']['wax_kg_d']} kg/d wax"],
      ["4", "Pattern table 220 x 300 x 40", 1, "carbon steel", parts["pattern_table"].val().Volume() * 7.85e-6,
       "make", "WO step 3"],
      ["5", "N1 pattern discharge chute +X z 600", 1, "carbon steel",
       parts["pattern_chute"].val().Volume() * 7.85e-6, "make", "task-04 schedule N1 (solids, bore not calculated)"],
      ["6", "N2 condensate-reclaim trap -X z 160", 1, "carbon steel", parts["condensate_trap"].val().Volume() * 7.85e-6,
       "make", "task-04 schedule N2"],
      ["7", "N3 make-up hopper -X z 160 (petro-wax class import, A-M-284)", 1, "carbon steel",
       parts["makeup_hopper"].val().Volume() * 7.85e-6, "make", "task-04 schedule N3"],
      ["8", "N4 drain well", 1, "carbon steel", parts["drain_well"].val().Volume() * 7.85e-6, "make",
       "task-04 schedule N4"],
    ]
    return P, parts, {}, EXTERNAL, rho, bom

BUILDERS = {"FLUX_PREP": build_flux_prep, "WAX_PATTERN": build_wax_pattern}

def build_and_export(unit):
    UNIT = unit
    P, parts, inv, EXTERNAL, rho, bom = BUILDERS[unit](unit)
    _LAST_PARTS = parts
    globals()["_LAST_PARTS"] = parts
    globals()["P"] = P
    asm = cq.Assembly(name=unit)
    for k, v in parts.items():
        asm.add(v, name=k)
    out = HERE / unit / "export"; out.mkdir(parents=True, exist_ok=True)
    asm.export(str(out / f"{unit.lower()}.step"))
    body = None
    for k, v in parts.items():
        body = v if body is None else body.union(v)
    cap_solid = body.val()
    cap_solid.exportStl(str(out / f"{unit.lower()}.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
    in_env = None
    for k, v in parts.items():
        if k in EXTERNAL:
            continue
        in_env = v if in_env is None else in_env.union(v)
    in_env_solid = in_env.val()
    in_env_solid.exportStl(str(out / f"{unit.lower()}_in_envelope.stl"), tolerance=0.4, angularTolerance=0.4, ascii=True)
    in_env_solid.scale(0.001).exportStl(str(HERE.parents[1] / "cad" / "stl" / f"{unit}.stl"),
                                        tolerance=0.0005, angularTolerance=0.4, ascii=True)
    ALL = list(parts.values())
    sb = cq.Compound.makeCompound([parts["bench_frame"].val()]).BoundingBox()
    tb_ = cq.Compound.makeCompound([v.val() for v in ALL]).BoundingBox()
    slack = 50.0
    inside_shell = bool(sb.xmin >= -1 and sb.xmax <= L + 1 and sb.ymin >= -1 and sb.ymax <= W + 1
                        and sb.zmin >= -1 and sb.zmax <= H + 1)
    overhang = {"-X": round(-tb_.xmin, 1), "+X": round(tb_.xmax - L, 1),
                "-Y": round(-tb_.ymin, 1), "+Y": round(tb_.ymax - W, 1)}
    overhang_ok = all(v <= slack + 1 for v in overhang.values())
    valid = all(v.val().isValid() for v in ALL)
    mass = {k: round(v.val().Volume() * rho[k], 1) for k, v in parts.items()}
    report = {
        "bench_bbox_mm": [round(sb.xlen, 1), round(sb.ylen, 1), round(sb.zlen, 1)],
        "inside_size_mm_shell": inside_shell,
        "connection_overhang_mm": overhang,
        "overhang_allowance_mm": slack,
        "overhang_ok": overhang_ok,
        "cad_stl_scope": "in-envelope build solid, metres (EXTERNAL parts excluded: " + ", ".join(EXTERNAL) + ")",
        "external_parts": list(EXTERNAL),
        "cap_solids": len(cap_solid.Solids()),
        "all_parts_valid": valid,
        "part_mass_kg": mass,
        "cadquery": "2.8.0",
    }
    (HERE / unit / "bom.csv").write_text(
        "item,description,qty,material,mass_kg,make_or_buy,basis\n" +
        "".join(",".join(str(c) for c in r[:4]) + f",{r[4]},{r[5]},\"{r[6]}\"\n" for r in bom))
    (HERE / unit / "fasteners.csv").write_text(
        'item,size,grade,qty,location,basis\n'
        '1,M10 anchor,ISO 898-1 8.8,4,bench to slab,study\n')
    (HERE / unit / "WORK_ORDER.md").write_text(
        f"# Work order {unit}\n\nAuthority: AQS-DUTY-072 (X-MFG lane). LIVE unit - bench_prep class.\n\n"
        f"1. Fabricate the bench frame and work top; set on anchors.\n"
        f"2. Mount the extraction hood and the vent stub; prove the draft.\n"
        f"3. Fit the unit hardware per bom.csv; align to the task-04 nozzle positions.\n"
        f"4. Fit the N-drain and utility stubs.\n"
        f"5. Test: dry run of the hardware, then the first service batch.\n"
        f"6. Inspect against models/mfg/{unit}/export/{unit.lower()}.step; record dimensions on the traveller.\n")
    (HERE / unit / "check.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    print(json.dumps(build_and_export(sys.argv[1] if len(sys.argv) > 1 else "FLUX_PREP")))
