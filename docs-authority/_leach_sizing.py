"""AQS-DUTY-050. LEACH_CSTR_1 sizing: liquor, residence, agitator, CPVC wall and FRP belts.
Study values are labeled; each is in AQS-REG-002."""
import json, math
g=json.load(open('flow_graph/plant_flow_graph.json'))
R={e['stream_id']:e['rate']['value'] for e in g['edges']}
S={}
# geometry (model): envelope 2000 x 1200 x 1400; header zone 60 per Y face; belt depth 43 per face
L,W,H=2000,1200,1400; z0=60; bd=56; t=16; tf=16; tl=12
Li=L-2*bd-2*t; Wi=W-2*z0-2*t; hl=1100           # liquid level, study
rho=1100                                         # liquor density, study
V=Li*Wi*hl*1e-9; Q=R['IA-EW-04']/rho
S.update(inner_mm=[Li,Wi],level_mm=hl,V_work_m3=V,Q_m3_d=Q,tau_h=V/Q*24)
# agitator: 4-blade 45 deg pitched turbine, study
Np,D,N=1.27,0.45,150/60
P=Np*rho*N**3*D**5; De=math.sqrt(4*Li*Wi/math.pi)*1e-3
S.update(imp_D_m=D,N_rpm=N*60,Np=Np,P_shaft_W=P,P_V_W_m3=P/V,D_over_Deq=D/De,tip_m_s=math.pi*D*N,motor_kW=0.75)
# wall: panels between FRP belts, long plate simply supported, beta 0.75 (Roark, a/b > 3)
belts=[300,560,900]; bh=203
edges=[0]+[z for b in belts for z in (b-bh/2,b+bh/2)]+[hl]
spans=[(edges[i],edges[i+1]) for i in range(0,len(edges)-1,2)]
sall=2000*6.895e-3*0.22                          # CPVC HDS 2000 psi x 0.22 at 85 C (study derating)
rows=[]
for a,b in spans:
    q=rho*9.81*(hl-a)*1e-9                  # MPa at panel bottom
    s=0.75*q*(b-a)**2/t**2; rows.append((a,b,q*1e3,s))
S.update(cpvc_allow_MPa=sall,panels=rows,panel_max_MPa=max(r[3] for r in rows))
# belt: FRP channel C203x56x6.4, simply supported over the 2000 mm face (corners ignored)
tw=6.4; Ix=tw*bh**3/12+2*((bd-tw)*tw)*(bh/2-tw/2)**2; Sx=Ix/(bh/2)
trib_lo=(belts[0]-bh/2)/2; zb=belts[0]; trib_hi=(belts[0]+belts[1])/2
q=rho*9.81*(hl-trib_lo)*1e-9                     # N/mm2 at floor, conservative over tributary
w=q*(trib_hi-trib_lo); M=w*L**2/8; sb=M/Sx; E=17200; d=5*w*L**4/(384*E*Ix)
S.update(belt_w_N_mm=w,belt_Sx_mm3=Sx,belt_sigma_MPa=sb,belt_allow_MPa=50,belt_defl_mm=d,belt_L_over_d=L/d)
# panel deflection, CPVC creep modulus 700 MPa (study)
a,b,qk,_=rows[0]; dp=0.142*(qk*1e-3)*(b-a)**4/(700*t**3); S['panel_defl_mm']=dp
# hydrostatic at floor
S['p_floor_kPa']=rho*9.81*hl*1e-6
if __name__=='__main__':
    print(json.dumps(S,indent=1,default=float))
