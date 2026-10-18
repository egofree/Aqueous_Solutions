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
_gc={n['unit_id']:n for n in json.load(open('flow_graph/plant_flow_graph.json'))['nodes']}
CRIT={'HABITATION':3.0,'CRYO_H2':round(_gc['CRYO_H2']['params'].get('compressor_design',{}).get('P_peak_kW',4.0),2),'CRYO_ASU':round(_gc['CRYO_ASU']['continuous_kw']['value'],2),'GROW_BED':5.0,'controls and instruments':2.0}   # CRYO_H2 peak (AQS-DUTY-067) and CRYO_ASU (AQS-DUTY-069) from the graph
ref_rect=ew['I_elem_A']*2.8/0.80/1000
cases={'bounding':ol['demand'],'reference':ol['demand']-rect['Pac_kW']+ref_rect}
from flow_graph.param import solver as SV
_g0=json.load(open('flow_graph/plant_flow_graph.json')); _x=next((n['continuous_kw']['value'] for n in _g0['nodes'] if n['unit_id']=='EXT_HALL' and n.get('continuous_kw')),0.0)
cases={k:P-_x for k,P in cases.items()}   # base demand without the extension; roof_close adds it back
roof=SV.roof_close(_d,cases['bounding'])   # X-PAR-07: roof-only PV; extension loads added to both cases
cases={k:P+roof['ext']['total_kW'] for k,P in cases.items()}
out={}
for k,P in cases.items():
    E=P*24                         # flat profile, continuous process (study)
    Edirect=P*(24-NIGHT); Estore=P*NIGHT
    o=PW.oversized(P,NIGHT,RT,PSH*DR.val(_d,'pv_roof_yield_factor'),DER,DR.val(_d,'pv_oversize_factor'),DR.val(_d,'pv_dc_ac_ratio'),INV)   # D75
    out[k]=dict(P_kW=P,E_kWh_d=E,**o)
out['roof']=roof
crit=sum(CRIT.values())
out['backup']=dict(critical_kW=crit,critical_list=CRIT,gen_kW=math.ceil(crit*1.25/5)*5,autonomy_d=AUT_CRIT,energy_kWh=crit*24*AUT_CRIT)
g=json.load(open('flow_graph/plant_flow_graph.json')); N={n['unit_id']:n for n in g['nodes']}
out['graph']=dict(pv_nameplate_kW=N['PV_ARRAY']['params']['nameplate_kw'],pv_avg_kW=N['PV_ARRAY']['continuous_kw']['value'],
    znbr2_peak_kW=N['ZNBR2']['params']['kW'],znbr2_kWh=N['ZNBR2']['params']['kWh'],inverter_kW=N['SOL_ARK_60K']['params']['kW'])
print(json.dumps(out))
