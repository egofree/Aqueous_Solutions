"""AQS-DUTY-051. EW_1 to EW_9 cell sizing from the graph harvest edges.
Basis: IA-EW-MET-n is a copper-equivalent sheet rate (AQS-ASSAY-001 section 4), so the bounding current is
I = m / (M_Cu/(2F) * 86400) / FE. Element current from the S08 deposits (AQS-ASSAY-001 section 5) is shown for
comparison. Study values are labeled and are in AQS-REG-002."""
import json, math
F=96485.0; MCU=63.546
g=json.load(open('flow_graph/plant_flow_graph.json')); R={e['stream_id']:e['rate']['value'] for e in g['edges']}
EL={1:('Au',196.97,3,0.0063),2:('Ag',107.87,1,0.0251),3:('Cu',63.546,2,8.7841),4:('Pb',207.2,2,0.7111),5:('Sn',118.71,2,0.7111),
    6:('Ni',58.693,2,0.7111),7:('Fe',55.845,2,29.629),8:('Cd',112.41,2,0.7111),9:('Zn',65.38,2,0.7111)}
FE=1.0           # bounding: copper-equivalent edge already is the sheet mass; current efficiency held at 1.0 (study)
J=200.0          # A/m2 cathode, study (AQS-EW-MOD-001)
PH,PW=0.42,0.60  # immersed plate height x width, m (AQS-EW-MOD-001)
AP=2*PH*PW       # both faces
PITCH=0.100      # cathode to cathode, anode between, m (50 mm cathode-anode, AQS-EW-MOD-001)
V=2.5            # cell voltage, study (graph EW_1 cell_voltage_V)
WALL=0.010; END=0.075; SIDE=0.050; SUMP=0.150; TOP=0.100; FB=0.080
rows=[]
for n in range(1,10):
    m=R[f'IA-EW-MET-{n}']+(R['IA-EW-SHEET'] if n==9 else 0); el,M,z,dep=EL[n]   # EW_9 also books IA-EW-SHEET
    I=m/(MCU/(2*F)*86400)/FE*1000
    Iel=dep*1000/(M/(z*F)*86400)
    Nc=max(1,math.ceil(I/(J*AP))); j=I/(Nc*AP)
    Li=Nc*PITCH+2*END; Wi=PW+2*SIDE; Hi=SUMP+PH+TOP+FB
    Lo,Wo,Ho=[round((x+2*WALL)*1000) for x in (Li,Wi)]+[round((Hi+WALL)*1000)]
    Vl=Li*Wi*(SUMP+PH+TOP); Q=R[[e['stream_id'] for e in g['edges'] if e['to_unit_id']==f'EW_{n}' and e['stream_id'].startswith('IA-EW')][0]]/1100
    rows.append(dict(cell=f'EW_{n}',metal=el,edge_kg_d=m,I_A=I,I_elem_A=Iel,cathodes=Nc,anodes=Nc+1,j_A_m2=j,
        size_mm=[Lo,Wo,Ho],V_liq_m3=Vl,tau_min=Vl/Q*1440,P_kW=I*V/1000))
tot=dict(I_A=sum(r['I_A'] for r in rows),I_elem_A=sum(r['I_elem_A'] for r in rows),P_kW=sum(r['P_kW'] for r in rows))
if __name__=='__main__':
    print(json.dumps(dict(rows=rows,total=tot),indent=1))
