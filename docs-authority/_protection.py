"""AQS-ELEC-006 protection and coordination, and the IEEE 80 touch/step check for AQS-ELEC-005.
Sources are inverter-limited (SOL_ARK_60K). Study values; register A-M entries."""
import json, math, subprocess
import json as _j
_n={n['unit_id']:n for n in _j.load(open('flow_graph/plant_flow_graph.json'))['nodes']}['SOL_ARK_60K']['params']
INV_KW=float(_n.get('kW',60)); V=480.0; KF=2.0          # inverter fault contribution 2 x rated (AQS-ELEC-002 Rev B figure, study)
Irated=INV_KW*1000/(math.sqrt(3)*V); Ifault=KF*Irated
rows=[l.split('|')[1:-1] for l in open('docs-authority/ONE_LINE.md') if l.count('|')==7 and ('480' in l or '208' in l) and not l.startswith('| Bus')]
fe=[]
for b,u,kw,a,br,bs in rows:
    a=float(a); br=int(br); bus480='480' in b
    If=Ifault if bus480 else Ifault*V/208*0.95       # through T-1, 5 % impedance drop ignored beyond 0.95 (study)
    inst_tm=5*br                                      # thermal-magnetic low instantaneous 5x (study)
    if inst_tm<=If*0.8: dev,setg='thermal-magnetic, instantaneous 5×',f'{inst_tm:.0f} A'
    else: dev,setg='electronic trip, short-time pickup 1.5×, 0.1 s',f'{1.5*br:.0f} A'
    fe.append(dict(bus=b.strip(),load=u.strip(),A=a,breaker=br,If=If,device=dev,setting=setg))
main=dict(breaker=next(b for b in (100,125,150,175,200,225,250,300,350,400,450,500,600,700,800) if b>=1.25*Irated),If=Ifault)
# IEEE 80-2013 touch and step, 50 kg person
Rg=json.loads(subprocess.run(['python3','docs-authority/_grounding_study.py'],capture_output=True,text=True).stdout)['Rg_ohm']
GPR=Ifault*Rg
def Cs(rho,rhos,hs): return 1-0.09*(1-rho/rhos)/(2*hs+0.09)
rho=50.0; ts=0.5
cases={'bare soil':(rho,1.0),'crushed rock 0.1 m, 3000 ohm m':(3000.0,Cs(rho,3000.0,0.1))}
tt={k:dict(touch=(1000+1.5*c*r)*0.116/math.sqrt(ts),step=(1000+6*c*r)*0.116/math.sqrt(ts)) for k,(r,c) in cases.items()}
print(json.dumps(dict(Irated=Irated,Ifault=Ifault,feeders=fe,main=main,Rg=Rg,GPR=GPR,ts=ts,tolerable=tt)))
