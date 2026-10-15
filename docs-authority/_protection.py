"""AQS-ELEC-006 protection and coordination, and the IEEE 80 touch/step check for AQS-ELEC-005.
Sources are inverter-limited (SOL_ARK_60K). Study values; register A-M entries."""
import json, math, subprocess
import json as _j
_n={n['unit_id']:n for n in _j.load(open('flow_graph/plant_flow_graph.json'))['nodes']}['SOL_ARK_60K']['params']
INV_KW=float(_n.get('kW',60)); V=480.0; KF=2.0          # inverter fault contribution 2 x rated (AQS-ELEC-002 Rev B figure, study)
Irated=INV_KW*1000/(math.sqrt(3)*V); Ifault=KF*Irated
rows=[l.split('|')[1:-1] for l in open('docs-authority/ONE_LINE.md') if l.count('|')==7 and ('480' in l or '208' in l) and not l.startswith('| Bus')]
import re as _re
XF_KVA=float(_re.search(r'T-1 (\d+) kVA',open('docs-authority/ONE_LINE.md').read()).group(1))
fe=[]
for b,u,kw,a,br,bs in rows:
    a=float(a); br=int(br); bus480='480' in b
    If=Ifault if bus480 else min(Ifault*V/208*0.95, XF_KVA*1000/(math.sqrt(3)*208)/0.05)   # through T-1: limited by its 5 % impedance (study)
    inst_tm=5*br                                      # thermal-magnetic low instantaneous 5x (study)
    if inst_tm<=If*0.8: dev,setg='thermal-magnetic, instantaneous 5×',f'{inst_tm:.0f} A'
    else: dev,setg='electronic trip, short-time pickup 1.5×, 0.1 s',f'{1.5*br:.0f} A'
    fe.append(dict(bus=b.strip(),load=u.strip(),A=a,breaker=br,If=If,device=dev,setting=setg))
main=dict(breaker=max(_n.get('sections',{}).get('breaker_A',[0])) or next(b for b in (100,125,150,175,200,225,250,300,350,400,450,500,600,700,800,1000,1200,1600,2000,2500,3000,4000,5000,6000) if b>=1.25*Irated),If=Ifault)
# IEEE 80-2013 touch and step, 50 kg person
G=json.loads(subprocess.run(['python3','docs-authority/_grounding_study.py'],capture_output=True,text=True).stdout); Rg=G['Rg_ohm']
# IEEE 80-2013 mesh and step voltage (eqs 85-94), rectangular grid, rods on the perimeter (Kii=1), 2/0 AWG (d 0.0105 m), h 0.75 m
_d=0.0105; _h=0.75; _D=12.0; _LC=G['ring_m']+G['mesh_m']; _LR=G['rods']*3.0; _A=G['A_m2']; _Lp=G['ring_m']
_n=(2*_LC/_Lp)*math.sqrt(_Lp/(4*math.sqrt(_A))); _Kh=math.sqrt(1+_h)
_Km=1/(2*math.pi)*(math.log(_D**2/(16*_h*_d)+(_D+2*_h)**2/(8*_D*_d)-_h/(4*_d))+1/_Kh*math.log(8/(math.pi*(2*_n-1))))
_Ki=0.644+0.148*_n; _Ks=1/math.pi*(1/(2*_h)+1/(_D+_h)+1/_D*(1-0.5**(_n-2)))
_LM=_LC+(1.55+1.22*(3.0/math.sqrt(2*_A)))*_LR
GPR=Ifault*Rg
Em=50.0*_Km*_Ki*Ifault/_LM; Es=50.0*_Ks*_Ki*Ifault/(0.75*_LC+0.85*_LR)
def Cs(rho,rhos,hs): return 1-0.09*(1-rho/rhos)/(2*hs+0.09)
rho=50.0; ts=0.5
cases={'bare soil':(rho,1.0),'crushed rock 0.1 m, 3000 ohm m':(3000.0,Cs(rho,3000.0,0.1))}
tt={k:dict(touch=(1000+1.5*c*r)*0.116/math.sqrt(ts),step=(1000+6*c*r)*0.116/math.sqrt(ts)) for k,(r,c) in cases.items()}
print(json.dumps(dict(Irated=Irated,Ifault=Ifault,feeders=fe,main=main,Rg=Rg,GPR=GPR,Em=Em,Es=Es,n=_n,ts=ts,tolerable=tt)))
