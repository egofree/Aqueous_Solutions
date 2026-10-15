"""EXPANDER manufacturing model, AQS-PLAN-006 work order W1.

Graph Rev BH. Study. Not a PE stamp. Reads params.json only.
Values marked 'assumptions' in params.json are not on the graph.
Placement frame: x along 600 mm, y along 400 mm, z up, origin at the
envelope corner. Inlet on -Y, outlet on +Y, relief on +Z (AQS-PLAN-005 Rev C nozzle rule).
"""
import json, math, csv, pathlib
import cadquery as cq

HERE = pathlib.Path(__file__).parent
P = json.loads((HERE / "params.json").read_text())
A = P["assumptions"]
L, W, H = P["size_mm"]
bore, stroke = P["cylinder"]["bore_mm"], P["cylinder"]["stroke_mm"]

parts = {}
tb = A["baseplate_t_mm"]
parts["baseplate"] = cq.Workplane("XY").box(L, W, tb, centered=False)
for x in (30, L - 30):
    for y in (30, W - 30):
        parts["baseplate"] = parts["baseplate"].cut(
            cq.Workplane("XY").center(x, y).circle(7).extrude(tb))  # M12 anchor holes

cx, cy, cz = A["crankcase_mm"]
x0, y0 = 60, (W - cy) / 2
parts["crankcase"] = (cq.Workplane("XY").box(cx, cy, cz, centered=False)
                      .translate((x0, y0, tb)).faces(">Z").shell(-8))

wall = A["cylinder_wall_mm"]
cyl_len = stroke + 60
cyl_od = bore + 2 * wall
ccx, ccy, ccz0 = x0 + cx / 2, W / 2, tb + cz
parts["cylinder"] = (cq.Workplane("XY").circle(cyl_od / 2).circle(bore / 2)
                     .extrude(cyl_len).translate((ccx, ccy, ccz0)))
head_z = ccz0 + cyl_len
parts["head"] = (cq.Workplane("XY").rect(cyl_od + 40, cyl_od + 40).extrude(20)
                 .translate((ccx, ccy, head_z)))
for dx in (-1, 1):
    for dy in (-1, 1):
        parts["head"] = parts["head"].cut(cq.Workplane("XY")
            .center(ccx + dx * (cyl_od / 2 + 10), ccy + dy * (cyl_od / 2 + 10))
            .circle(4.5).extrude(20).translate((0, 0, head_z)))  # M8 head bolts
parts["piston"] = (cq.Workplane("XY").circle(bore / 2 - 0.5).extrude(40)
                   .translate((ccx, ccy, ccz0 + 10)))

fd, ft = A["flywheel_d_mm"], A["flywheel_t_mm"]
parts["flywheel"] = (cq.Workplane("YZ").circle(fd / 2).extrude(ft)
                     .translate((x0 + cx + 20, W / 2, tb + cz / 2)))
parts["shaft"] = (cq.Workplane("YZ").circle(15).extrude(cx + 80)
                  .translate((x0 - 10, W / 2, tb + cz / 2)))

od = A["DN15_OD_mm"]; sl = A["nozzle_stub_len_mm"]
nz = {n["tag"]: n for n in P["nozzles"]}
zN = nz["N1"]["height_mm"]
parts["N1_inlet"] = (cq.Workplane("XZ").circle(od / 2).circle(od / 2 - 2.77).extrude(-sl)
                     .translate((ccx, 0, zN)))
parts["N2_outlet"] = (cq.Workplane("XZ").circle(od / 2).circle(od / 2 - 2.77).extrude(sl)
                      .translate((ccx, W, zN)))
# side manifolds from the head to each nozzle (pipe, DN15)
for tag, y1 in (("N1_line", 0), ("N2_line", W)):
    y_start, y_end = sorted((ccy, y1))
    parts[tag] = (cq.Workplane("XZ").circle(od / 2).extrude(-(y_end - y_start))
                  .translate((ccx + cyl_od / 2 + 20, y_start, zN)))
rb = P["relief_mm"]
parts["PSV_boss"] = (cq.Workplane("XY").circle(12).circle(rb / 2).extrude(H - head_z - 20)
                     .translate((ccx, ccy, head_z + 20)))

asm = cq.Assembly(name="EXPANDER")
for k, v in parts.items():
    asm.add(v, name=k)
out = HERE / "export"; out.mkdir(exist_ok=True)
asm.export(str(out / "expander.step"))
comp = cq.Compound.makeCompound([v.val() for v in parts.values()])
comp.exportStl(str(out / "expander.stl"), tolerance=0.5, angularTolerance=0.5, ascii=True)

# acceptance checks that run on files
bb = cq.Compound.makeCompound([v.val() for v in parts.values()]).BoundingBox()
report = {"bbox_mm": [round(bb.xmin, 1), round(bb.ymin, 1), round(bb.zmin, 1), round(bb.xmax, 1), round(bb.ymax, 1), round(bb.zmax, 1)],
          "inside_size_mm": bool(bb.xmin >= -1 - sl and bb.xmax <= L + 1 and bb.ymin >= -sl - 1 and bb.ymax <= W + sl + 1 and bb.zmax <= H + 1)}
# A-P wall check, thin shell, internal pressure. P as gauge, conservative: 550 kPa.
Pm = P["design_kPa"] / 1000.0; S = A["allowable_stress_MPa"]
t_req = Pm * (bore / 2) / (S - 0.6 * Pm)
report["wall_required_mm"] = round(t_req, 3); report["wall_drawn_mm"] = wall
rho = 7.99e-6  # 316L kg/mm3, handbook
rows = []
for k, v in parts.items():
    rows.append([k, 1, P["material"], round(v.val().Volume() * rho, 2), "make"])
with open(HERE / "bom.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["part", "qty", "material", "mass_kg", "make_or_buy"]); w.writerows(rows)
(HERE / "check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
