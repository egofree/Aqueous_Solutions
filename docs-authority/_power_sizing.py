"""AQS-ELEC-007 storage and generation sizing from the AQS-ELEC-002 bus demand. Two cases:
bounding (EW at the copper-equivalent current) and reference (EW at the element current). Study values."""
import json, math, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flow_graph.param import drivers as DR
from flow_graph.param.sizing import power as PW
_d = DR.load()   # X-PAR-03: yield, derate, round trip, night hours from drivers.json
ol=json.loads(subprocess.run(['python3','docs-authority/_one_line.py'],capture_output=True,text=True,check=True).stdout)
ew=json.loads(subprocess.run(['python3','docs-authority/_ew_sizing.py'],capture_output=True,text=True,check=True).stdout)['total']
rect=json.loads(subprocess.run(['python3','docs-authority/_rect_ew_sizing.py'],capture_output=True,text=True,check=True).stdout)['total']
PSH=DR.val(_d,'pv_yield_kWh_kWp_d'); DER=DR.val(_d,'pv_system_derate'); RT=DR.val(_d,'storage_round_trip'); NIGHT=DR.val(_d,'night_hours'); INV=60.0; AUT_CRIT=2.0   # study; PSH from AQS-SITE-002 (NREL PVWatts)
CRIT={'HABITATION':3.0,'CRYO_H2':4.0,'CRYO_ASU':18.0,'GROW_BED':5.0,'controls and instruments':2.0}
ref_rect=ew['I_elem_A']*2.8/0.80/1000
cases={'bounding':ol['demand'],'reference':ol['demand']-rect['Pac_kW']+ref_rect}
from flow_graph.param import solver as SV
roof=SV.roof_close(_d,cases['bounding'])   # X-PAR-07: roof-only PV; extension loads added to both cases
cases={k:P+roof['ext']['total_kW'] for k,P in cases.items()}
out={}
for k,P in cases.items():
    E=P*24                         # flat profile, continuous process (study)
    Edirect=P*(24-NIGHT); Estore=P*NIGHT
    pv=PW.pv_kWp(P,NIGHT,RT,PSH,DER)
    out[k]=dict(P_kW=P,E_kWh_d=E,pv_kWp=pv,store_kWh=Estore,store_kW=P,inverters=math.ceil(P/INV),inv_kW=math.ceil(P/INV)*INV)
out['roof']=roof
crit=sum(CRIT.values())
out['backup']=dict(critical_kW=crit,critical_list=CRIT,gen_kW=math.ceil(crit*1.25/5)*5,autonomy_d=AUT_CRIT,energy_kWh=crit*24*AUT_CRIT)
g=json.load(open('flow_graph/plant_flow_graph.json')); N={n['unit_id']:n for n in g['nodes']}
out['graph']=dict(pv_nameplate_kW=N['PV_ARRAY']['params']['nameplate_kw'],pv_avg_kW=N['PV_ARRAY']['continuous_kw']['value'],
    znbr2_peak_kW=N['ZNBR2']['params']['kW'],znbr2_kWh=N['ZNBR2']['params']['kWh'],inverter_kW=N['SOL_ARK_60K']['params']['kW'])
print(json.dumps(out))
