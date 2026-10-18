"""LEACH_CSTR_1 manufacturing model, AQS-PLAN-006. Values from params.json only."""
import json, math, pathlib, cadquery as cq
H = pathlib.Path(__file__).parent; P = json.load(open(H/"params.json")); A = P["assumptions"]; G = P["graph"]
L, W, HT = G["size_mm"]; z0 = A["header_zone_mm"]["value"]; t = A["wall_mm"]["value"]; tf = A["floor_mm"]["value"]
tl = A["lid_mm"]["value"]; fw = A["lid_flange_w_mm"]["value"]; Wt = W - 2*z0
B = A["belts"]; bd, bh, bw = B["depth_mm"], B["height_mm"], B["web_mm"]
x0s, Lt = bd, L - 2*bd                     # tank body inside the belts on the X ends
box = lambda x, y, z, dx, dy, dz: cq.Workplane().box(dx, dy, dz, centered=False).translate((x, y, z))
cyl = lambda r, h, p, d: cq.Workplane(cq.Plane(origin=p, xDir=(1,0,0) if d!=(1,0,0) else (0,1,0), normal=d)).circle(r).extrude(h)
shell = box(x0s, z0, 0, Lt, Wt, HT-tl).cut(box(x0s+t, z0+t, tf, Lt-2*t, Wt-2*t, HT))
flange = box(x0s, z0, HT-tl-10, Lt, Wt, 10).cut(box(x0s+t+fw, z0+t+fw, HT-tl-10, Lt-2*t-2*fw, Wt-2*t-2*fw, 10))
lid = box(x0s, z0, HT-tl, Lt, Wt, tl)
tank = shell.union(flange).union(lid)
zc = G["nozzle_face_height_mm"]; pitch = A["port_pitch_mm"]["value"]; rh = A["header_od_mm"]["value"]/2
def header(n, y_hdr, y_wall, dns):
    global tank
    span = (n-1)*pitch; xa = L/2 - span/2
    tank = tank.union(cyl(rh, span+2*rh, (xa-rh, y_hdr, zc), (1,0,0)))
    for i in range(n):
        r = (A["port_od_mm_dn20"] if dns[i]==20 else A["port_od_mm_bore_not_calculated"]["value"])/2
        ya, yb = sorted((y_hdr, y_wall)); tank = tank.union(cyl(r, yb-ya, (xa+i*pitch, ya, zc), (0,1,0)))
header(G["inlets"], rh+0.5, z0+t, [20,20]+[25]*(G["inlets"]-2))
header(G["outlets_process"], W-rh-0.5, W-z0-t, [25]*G["outlets_process"])
tank = tank.union(cyl(15, 20, (L-bd-120, W-z0, 450), (0,1,0)))  # IA-E-LEACH cable gland boss, assumption
pb = A["lid_bolt"]["pitch_mm"]; nx = int((Lt-2*t-fw)//pb); ny = int((Wt-2*t-fw)//pb); holes = []
for i in range(nx+1):
    for y in (z0+t+fw/2, W-z0-t-fw/2): holes.append((x0s+t+fw/2+i*(Lt-2*t-fw)/nx, y))
for j in range(1, ny):
    for x in (x0s+t+fw/2, x0s+Lt-t-fw/2): holes.append((x, z0+t+fw/2+j*(Wt-2*t-fw)/ny))
for (x, y) in holes: tank = tank.cut(cyl(6.5, tl+10, (x, y, HT-tl-10), (0,0,1)))
# FRP belts, channel, web on the wall
belts = None
for zb in B["z_mm"]:
    ring = box(0, z0-bd, zb-bh/2, L, Wt+2*bd, bh).cut(box(x0s, z0, zb-bh/2, Lt, Wt, bh))
    ring = ring.cut(box(0, z0-bd, zb-bh/2+bw, L, Wt+2*bd, bh-2*bw).cut(box(x0s-bw, z0-bw, zb-bh/2, Lt+2*bw, Wt+2*bw, bh)))
    belts = ring if belts is None else belts.union(ring)
# HX-5 coil envelope and pads (mass taken from the tube, not the envelope)
cx, cy = L/2, W/2
coil = cq.Workplane().circle(462.5).circle(287.5).extrude(600).translate((cx, cy, tf+100))
for (dx, dy) in ((375,0),(-375,0),(0,375),(0,-375)): coil = coil.union(cyl(30, 100, (cx+dx, cy+dy, tf), (0,0,1)))
# agitator, shaft through the lid, impeller as a 20 mm disc
ag = P["agitator"]
agit = cyl(ag["shaft_od_mm"]/2, HT - ag["impeller_z_mm"], (cx, cy, ag["impeller_z_mm"]), (0,0,1))
agit = agit.union(cyl(ag["D_mm"]/2, 20, (cx, cy, ag["impeller_z_mm"]-10), (0,0,1)))
body = tank.union(belts).union(coil).union(agit)
out = H/"export"; out.mkdir(exist_ok=True)
cq.exporters.export(body, str(out/"leach_cstr_1.step")); body.val().exportStl(str(out/"leach_cstr_1.stl"), 0.3, 0.3, True)
C = P["hx5_coil"]; tube = math.pi/4*(C["tube_od_mm"]**2-(C["tube_od_mm"]-2*C["tube_wall_mm"])**2)*C["tube_length_m"]*1e3
vtank = tank.val().Volume() - agit.intersect(tank).val().Volume()
m = {"CPVC tank": vtank*1e-9*P["material"]["density_kg_m3"]["value"],
     "FRP belts": belts.val().Volume()*1e-9*B["density_kg_m3"],
     "glass coil (tube)": tube*1e-9*2230,
     "PTFE pads": 4*math.pi*30**2*100*1e-9*2200,
     "PVDF agitator (sheath and impeller, solid)": (agit.val().Volume())*1e-9*1780}
print(json.dumps({"solids": len(body.solids().vals()), "lid_bolts": len(holes), "mass_kg": {k: round(v,1) for k,v in m.items()}, "empty_kg": round(sum(m.values()),1)}))
