"""AQS-ELEC-004. EW rectifier (RECT-EW) rated at the bounding-case current of AQS-DUTY-051.
Converted to the parametric library (X-PAR-03): cell voltage, bus drop and efficiency from
flow_graph/param/drivers.json (USBM_CL_EW chloride EW basis); channel sizing from sizing.power."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flow_graph.param import drivers as DR
from flow_graph.param.sizing import power as PW
_d = DR.load()
ew=json.loads(subprocess.run([sys.executable,'docs-authority/_ew_sizing.py'],capture_output=True,text=True,check=True).stdout)['rows']
STD=DR.val(_d,'rect_channel_frame_sizes_A')   # channel frame sizes, A (A-M-044)
MARGIN=DR.val(_d,'rect_channel_margin'); VRATED=DR.val(_d,'rect_channel_rated_V'); JBAR=DR.val(_d,'rect_busbar_J_A_cm2')   # A-M-041/042; JBAR from AQS-PWR-001
VCELL=DR.val(_d,'ew_cell_voltage_V'); VDROP=DR.val(_d,'ew_bus_drop_V'); EFF=DR.val(_d,'rect_efficiency')
rows=[]
for r in ew:
    c=PW.rectifier_channel(r['I_A'],VCELL,VDROP,EFF,STD,MARGIN,VRATED)
    rows.append(dict(cell=r['cell'],I_A=r['I_A'],**c,bar_cm2=c['rated_A']/JBAR))
T={k:sum(x[k] for x in rows) for k in ('I_A','rated_A','rated_kW','Pdc_kW','Pac_kW')}
if __name__=='__main__': print(json.dumps(dict(rows=rows,total=T,basis=dict(V_cell=VCELL,V_drop=VDROP,eff=EFF)),indent=1))
