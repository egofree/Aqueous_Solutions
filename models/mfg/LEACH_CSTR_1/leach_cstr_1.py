"""LEACH_CSTR_1 manufacturing model, AQS-PLAN-006. Values from params.json only."""
import json, math, pathlib, cadquery as cq
H = pathlib.Path(__file__).parent; P = json.load(open(H/"params.json")); A = P["assumptions"]; G = P["graph"]
L, W, HT = G["size_mm"]; z0 = A["header_zone_mm"]["value"]; t = A["wall_mm"]["value"]; tf = A["floor_mm"]["value"]
tl = A["lid_mm"]["value"]; fw = A["lid_flange_w_mm"]["value"]; Wt = W - 2*z0
box = lambda x, y, z, dx, dy, dz: cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))
cyl = lambda r, h, p, d: cq.Workplane(cq.Plane(origin=p, xDir=(1,0,0) if d!=(1,0,0) else (0,1,0), normal=d)).circle(r).extrude(h)
shell = box(0, z0, 0, L, Wt, HT-tl).cut(box(t, z0+t, tf, L-2*t, Wt-2*t, HT))
flange = box(0, z0, HT-tl-10, L, Wt, 10).cut(box(t+fw, z0+t+fw, HT-tl-10, L-2*t-2*fw, Wt-2*t-2*fw, 10))
lid = box(0, z0, HT-tl, L, Wt, tl)
body = shell.union(flange).union(lid)
zc = G["nozzle_face_height_mm"]; pitch = A["port_pitch_mm"]["value"]; rh = A["header_od_mm"]["value"]/2
def header(n, y_hdr, y_wall, dns):
    global body
    span = (n-1)*pitch; x0 = L/2 - span/2
    body = body.union(cyl(rh, span+2*rh, (x0-rh, y_hdr, zc), (1,0,0)))
    for i in range(n):
        r = (A["port_od_mm_dn20"] if dns[i]==20 else A["port_od_mm_bore_not_calculated"]["value"])/2
        ya, yb = sorted((y_hdr, y_wall)); body = body.union(cyl(r, yb-ya, (x0+i*pitch, ya, zc), (0,1,0)))
    return x0
header(G["inlets"], rh+0.5, z0+t, [20,20]+[25]*(G["inlets"]-2))
header(G["outlets_process"], W-rh-0.5, W-z0-t, [25]*G["outlets_process"])
gland = cyl(15, 20, (L-120, W-z0, 300), (0,1,0))  # IA-E-LEACH cable gland boss, assumption
body = body.union(gland)
pb = A["lid_bolt"]["pitch_mm"]; nx = int((L-2*t-fw)//pb); ny = int((Wt-2*t-fw)//pb); holes = []
for i in range(nx+1):
    for y in (z0+t+fw/2, W-z0-t-fw/2): holes.append((t+fw/2+i*(L-2*t-fw)/nx, y))
for j in range(1, ny):
    for x in (t+fw/2, L-t-fw/2): holes.append((x, z0+t+fw/2+j*(Wt-2*t-fw)/ny))
for (x, y) in holes: body = body.cut(cyl(6.5, tl+10, (x, y, HT-tl-10), (0,0,1)))
C = P['hx5_coil']
cx, cy = L/2, W/2
coil = cq.Workplane().circle(462.5).circle(287.5).extrude(600).translate((cx, cy, tf+100))
for (dx, dy) in ((375,0),(-375,0),(0,375),(0,-375)):
    coil = coil.union(cyl(30, 100, (cx+dx, cy+dy, tf), (0,0,1)))
body = body.union(coil)
solid = body.val()
out = H/"export"; out.mkdir(exist_ok=True)
cq.exporters.export(body, str(out/"leach_cstr_1.step")); body.val().exportStl(str(out/"leach_cstr_1.stl"), 0.3, 0.3, True)
vol = solid.Volume(); print(json.dumps({"solids": len(body.solids().vals()), "volume_mm3": round(vol), "mass_kg": round(vol*1e-9*P["material"]["density_kg_m3"]["value"],1), "lid_bolts": len(holes)}))
