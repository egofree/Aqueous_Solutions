"""AQS-ELEC-004. EW rectifier (RECT-EW) rated at the bounding-case current of AQS-DUTY-051."""
import json, subprocess, math
ew=json.loads(subprocess.run(['python3','docs-authority/_ew_sizing.py'],capture_output=True,text=True,check=True).stdout)['rows']
STD=[250,500,1000,1500,2000,2500,3000,4000]   # channel frame sizes, A (study)
MARGIN=1.10; VCELL=2.5; VDROP=0.3; VRATED=6.0; EFF=0.80; JBAR=200.0   # study values; JBAR from AQS-PWR-001
rows=[]
for r in ew:
    need=r['I_A']*MARGIN; rate=next(s for s in STD if s>=need)
    Pdc=r['I_A']*(VCELL+VDROP)/1000
    rows.append(dict(cell=r['cell'],I_A=r['I_A'],need_A=need,rated_A=rate,rated_kW=rate*VRATED/1000,Pdc_kW=Pdc,Pac_kW=Pdc/EFF,bar_cm2=rate/JBAR))
T={k:sum(x[k] for x in rows) for k in ('I_A','rated_A','rated_kW','Pdc_kW','Pac_kW')}
if __name__=='__main__': print(json.dumps(dict(rows=rows,total=T),indent=1))
