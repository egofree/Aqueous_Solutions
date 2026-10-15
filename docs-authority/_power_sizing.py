"""AQS-ELEC-007 storage and generation sizing from the AQS-ELEC-002 bus demand. Two cases:
bounding (EW at the copper-equivalent current) and reference (EW at the element current). Study values."""
import json, math, subprocess
ol=json.loads(subprocess.run(['python3','docs-authority/_one_line.py'],capture_output=True,text=True,check=True).stdout)
ew=json.loads(subprocess.run(['python3','docs-authority/_ew_sizing.py'],capture_output=True,text=True,check=True).stdout)['total']
rect=json.loads(subprocess.run(['python3','docs-authority/_rect_ew_sizing.py'],capture_output=True,text=True,check=True).stdout)['total']
PSH=5.41; DER=0.80; RT=0.70; NIGHT=14.0; INV=60.0; AUT_CRIT=2.0   # study; PSH from AQS-SITE-002 (NREL PVWatts)
CRIT={'HABITATION':3.0,'CRYO_H2':4.0,'CRYO_ASU':18.0,'GROW_BED':5.0,'controls and instruments':2.0}
ref_rect=ew['I_elem_A']*2.8/0.80/1000
cases={'bounding':ol['demand'],'reference':ol['demand']-rect['Pac_kW']+ref_rect}
out={}
for k,P in cases.items():
    E=P*24                         # flat profile, continuous process (study)
    Edirect=P*(24-NIGHT); Estore=P*NIGHT
    pv=(Edirect+Estore/RT)/(PSH*DER)
    out[k]=dict(P_kW=P,E_kWh_d=E,pv_kWp=pv,store_kWh=Estore,store_kW=P,inverters=math.ceil(P/INV),inv_kW=math.ceil(P/INV)*INV)
crit=sum(CRIT.values())
out['backup']=dict(critical_kW=crit,critical_list=CRIT,gen_kW=math.ceil(crit*1.25/5)*5,autonomy_d=AUT_CRIT,energy_kWh=crit*24*AUT_CRIT)
g=json.load(open('flow_graph/plant_flow_graph.json')); N={n['unit_id']:n for n in g['nodes']}
out['graph']=dict(pv_nameplate_kW=N['PV_ARRAY']['params']['nameplate_kw'],pv_avg_kW=N['PV_ARRAY']['continuous_kw']['value'],
    znbr2_peak_kW=N['ZNBR2']['params']['kW'],znbr2_kWh=N['ZNBR2']['params']['kWh'],inverter_kW=N['SOL_ARK_60K']['params']['kW'])
print(json.dumps(out))
