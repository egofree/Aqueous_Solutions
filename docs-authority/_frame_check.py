"""AQS-BLD-016 building frame member check (X-BLD-01, A-M-207). The 6 m grid of AQS-MOD-002 / params.py (PLATE_L x PLATE_W, BAY) is
framed in welded steel (ASTM A992 plate, Fy 345 MPa): box columns at every grid node, secondary beams at 3 m, girders on the grid,
concentric X-braced bays for the lateral load. Member sizes are found from need: the smallest welded section that passes AISC 360-22.
Gravity: slab self-weight (SLAB_THK) + equipment and water from AQS-BLD-013 per level + ASCE 7 Table 4.3-1 live by occupancy.
Combinations (ASCE 7-22 2.3.1): 1.4(D+F) and 1.2(D+F) + 1.6L. Lateral: the larger of the AQS-BLD-014 seismic and wind shears on two
braced lines per direction, two braced bays per line, tension-only diagonals. Run after _struct_loads.py and _water_tower.py."""
import json, math, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(R); sys.path.insert(0, R); sys.path.insert(0, os.path.join(R, 'models/freecad'))
from flow_graph.param.refs import cite
from flow_graph.param import site as SITE   # apparent gravity from the site profile
from flow_graph.param import drivers as DR   # U4b: frame check literals single-sourced from drivers.json (A-M-207)
_d = DR.load(); v = lambda k: DR.val(_d, k)
for k in ('AISC360_22', 'ASTM_A992', 'ASCE7_22'): cite(k)
import params as P
from flow_graph.param import water_tower as WT
# Site gate (X-LOC-11): on a floating site the plant is a hull. The slab, foundations and
# brace-to-slab basis of this check do not exist there; structure follows the class rules
# (AQS-PLAN-011 section 10.2) and the frame member check re-enters with the hull design pass.
_prof = SITE.load_profile()
_caps = {k for k, e in (_prof['groups'].get('capabilities', {}).get('entries') or {}).items() if e['value'] is True}
if 'ground_contact' not in _caps:
    md = ['# Building frame member check', '', 'Document number: AQS-BLD-016', 'Revision: B', 'Date: 2026-10-25', '',
          '| Rev | Description | Date |', '|---|---|---|', '| A | First issue | 2026-10-16 |',
          '| B | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No load or section changed. | 2026-10-25 |', '',
          '## 1. Purpose and scope', '',
          'This page states the welded-steel frame member check for the land building: box columns, secondary beams, girders and concentric X-braced bays on the 6 m grid, sized from need to AISC 360-22.',
          '', '## 2. Superseded at this site', '',
          'At this site the plant is a hull: there is no slab, no foundations and no brace-to-slab load path, so this check has no basis here. Hull structure, stability and freeboard follow the class rules (AQS-PLAN-011 section 10.2) and are the hull design pass (task X-LOC-11 remainder).',
          '', '## 3. Land check', '',
          'The land check of record is the baseline copy of this page at the repository root; this site copy states only the supersession.']
    open('docs-authority/FRAME_CHECK.md', 'w').write('\n'.join(md) + '\n')
    print('frame check superseded at this site (hull); land check unchanged at the root')
    sys.exit(0)
E_ = 200e3; FY = v('MFG.tools-metal-forming-train.hall-services.fc_Fy_MPa'); G_C = 24.0                                   # MPa; concrete kN/m3
BAY = P.BAY/1000; Lp, Wp = P.PLATE_L/1000, P.PLATE_W/1000; A_pl = Lp*Wp; nx, ny = round(Lp/BAY), round(Wp/BAY)
LIVE = v('MFG.tools-metal-forming-train.hall-services.fc_live_loads_kPa')   # kPa: light manufacturing 125 psf, assembly/corridors 100 psf, water storeys (F), roof 20 psf
z0 = P.HYDRO_RES_Z0/1000; clr = P.HYDRO_RES_CLEAR/1000
Z = {'L-2': P.basement_z(1)/1000, 'L-1': P.basement_z(0)/1000, 'L0': P.Z_L0/1000, 'L1': P.Z_L1/1000, 'L2': P.Z_L2/1000, 'R1': z0, 'R2': z0 + clr, 'R3': z0 + 2*clr, 'ROOF': P.Z_ROOF/1000}
SL = {}
for line in open('docs-authority/STRUCT_LOADS.md'):
    c = [x.strip() for x in line.split('|')]
    if len(c) > 8 and c[1] in Z:
        try: SL[c[1]] = dict(foot=float(c[3]), op=float(c[5]))
        except ValueError: pass
WATER = {'R1', 'R2', 'R3'}
lev = [k for k in sorted(Z, key=Z.get) if k != 'L-2']                # L-2 (catch tank) bears on the raft, X-BLD-03
q = {}
for k in lev:
    s = SL.get(k, dict(foot=0, op=0)); qe = s['op']/max(A_pl, s['foot']) if s['op'] else 0.0
    D = P.SLAB_THK/1000*G_C + (0 if k in WATER else qe); F = qe if k in WATER else 0.0; L = LIVE[k]
    q[k] = dict(D=D, F=F, L=L, qu=max(1.4*(D + F), 1.2*(D + F) + 1.6*L), qL=L + F)   # deflection under live + water
def box(Pu, KL):
    for b in range(150, 1500, 10):
        t = max(10, math.ceil(b/30)); A = (b*b - (b - 2*t)**2); I = (b**4 - (b - 2*t)**4)/12; r = math.sqrt(I/A)
        lam = KL*1000/r; Fe = math.pi**2*E_/lam**2; Fcr = 0.658**(FY/Fe)*FY if lam <= 4.71*math.sqrt(E_/FY) else 0.877*Fe
        if 0.9*Fcr*A/1000 >= Pu: return dict(b=b, t=t, A=A, KLr=lam, phiPn=0.9*Fcr*A/1000, kg_m=A*7.85e-3)
def ibeam(Mu, wL, Lm, Lim=360):
    for d in range(200, 2000, 10):
        bf, tf, tw = d/2, max(8, math.ceil(d/30)), max(6, math.ceil(d/60))
        Zx = bf*tf*(d - tf) + tw*(d - 2*tf)**2/4; Ix = (bf*d**3 - (bf - tw)*(d - 2*tf)**3)/12
        dl = 5*wL*(Lm*1000)**4/(384*E_*Ix) if wL else 0          # wL in N/mm
        if 0.9*FY*Zx/1e6 >= Mu and dl <= Lm*1000/Lim: return dict(d=d, bf=bf, tf=tf, tw=tw, phiMn=0.9*FY*Zx/1e6, defl_mm=dl, kg_m=(2*bf*tf + (d - 2*tf)*tw)*7.85e-3)
beams = []
for k in lev:
    w = q[k]['qu']*BAY/2; Mu = w*BAY**2/8; sb = ibeam(Mu, q[k]['qL']*BAY/2, BAY)
    Pg = w*BAY; Mg = Pg*BAY/4 + 1.2*(sb['kg_m']*SITE.g()*1e-3)*BAY**2/8; gd = ibeam(Mg, q[k]['qL']*BAY/2*2*0.8, BAY)
    beams.append((k, q[k], Mu, sb, Mg, gd))
cols = []; acc = {'interior': 0.0, 'edge': 0.0, 'corner': 0.0}; TR = {'interior': BAY*BAY, 'edge': BAY*BAY/2, 'corner': BAY*BAY/4}
for i, k in enumerate(reversed(lev)):
    for c in acc: acc[c] += q[k]['qu']*TR[c]
    below = list(reversed(lev))[i + 1] if i + 1 < len(lev) else 'L-2'; KL = Z[k] - Z[below]
    cols.append((k, KL, {c: (acc[c], box(acc[c], KL)) for c in acc}))
r = P.HYDRO if hasattr(P, 'HYDRO') else None; sw = WT.seismic_wind(r, P.PLATE_L, P.PLATE_W); V = max(sw['V_seis_kN'], sw['F_wind_kN'])
Vline = V/2; th = math.atan2(clr, BAY); T = Vline/2/math.cos(th); Abr = T*1000/(0.9*FY); bb = math.ceil(math.sqrt(Abr/0.15)/10)*10   # square box, A ~ 4 b t at t = b/26
md = ['# Building frame member check', '', 'Document number: AQS-BLD-016', 'Revision: B', 'Date: 2026-10-25',
      'Authority: AQS-PLAN-007 task X-BLD-01; assumption A-M-207. Generated by `docs-authority/_frame_check.py`; do not edit this page by hand. Study; this page is not stamped by a Professional Engineer (PE).', '',
      '| Rev | Description | Date |', '|---|---|---|', '| A | First issue | 2026-10-16 |',
      '| B | Purpose and scope added; text rewritten to the documentation style guide (AQS-DOC-002). No load or section changed. | 2026-10-25 |', '',
      '## 1. Purpose and scope', '',
      'The plant building is a steel frame of beams and columns carrying concrete floor slabs, with water reservoirs on the upper levels. This page '
      'sizes the members of the frame: it gives the factored floor loads of each level, the secondary beams and girders of each floor, the columns '
      'of each storey, and the bracing that resists wind and earthquake.', '',
      '## 2. Basis', '',
      f'The plan grid is {nx} by {ny} bays of {BAY:.0f} m, giving a plate of {Lp:.0f} x {Wp:.0f} m with {(nx+1)*(ny+1)} columns. All members are welded sections made from ASTM A992 plate with a yield strength (Fy) of {FY:.0f} MPa. The floor slab braces the top flange of the beams, so the unbraced length of the beams (Lb) is zero. Members are checked to AISC 360-22 sections E3 (compression), F2 (flexure) and D2 (tension), and loads are combined to ASCE 7-22 section 2.3.1.', '',
      '## 3. Floor loads', '',
      'Table 3.1 gives the loads on each level in kPa: D is the dead load, F the load of contained water, L the live load, and wu the factored load used for design.', '',
      'Table 3.1. Floor loads (kPa)', '',
      '| Level | z m | D | F (water) | L | wu |', '|---|---|---|---|---|---|'] + [f"| {k} | {Z[k]:.1f} | {q[k]['D']:.2f} | {q[k]['F']:.2f} | {q[k]['L']:.2f} | {q[k]['qu']:.2f} |" for k in lev]
md += ['', '## 4. Beams', '', f'Table 4.1 gives the beams of each floor, which span {BAY:.0f} m. Mu is the factored bending moment, and phiMn is the design bending strength of the girder. The section is given as depth d, flange width bf, flange thickness tf and web thickness tw. The deflection under live load and water is compared with the limit of span/360.', '',
       'Table 4.1. Beams', '',
       '| Level | Secondary Mu kNm | Secondary d x bf x tf x tw mm | Girder Mu kNm | Girder d x bf x tf x tw mm | Girder phiMn | Live + water deflection mm |', '|---|---|---|---|---|---|---|']
md += [f"| {k} | {Mu:.0f} | {s['d']} x {s['bf']:.0f} x {s['tf']} x {s['tw']} | {Mg:.0f} | {g['d']} x {g['bf']:.0f} x {g['tf']} x {g['tw']} | {g['phiMn']:.0f} | {g['defl_mm']:.1f} (L/360 = {BAY*1000/360:.1f}) |" for k, qq, Mu, s, Mg, g in beams]
md += ['', '## 5. Columns', '', 'Table 5.1 gives the columns of the storey below each level, for interior, edge and corner positions. Each column is a welded square box of side b and wall thickness t. KL is the effective length, Pu the factored axial load, and KL/r the slenderness ratio.', '',
       'Table 5.1. Columns', '',
       '| Level | KL m | Interior Pu kN | Interior b x t | Edge Pu | Edge b x t | Corner Pu | Corner b x t |', '|---|---|---|---|---|---|---|---|']
md += [f"| {k} | {KL:.1f} | " + ' | '.join(f"{d[c][0]:.0f} | {d[c][1]['b']} x {d[c][1]['t']} (KL/r {d[c][1]['KLr']:.0f})" for c in ('interior', 'edge', 'corner')) + ' |' for k, KL, d in cols]
md += ['', '## 6. Lateral bracing', '', f"The design base shear is {V:.0f} kN, governed by {'earthquake' if sw['V_seis_kN'] >= sw['F_wind_kN'] else 'wind'} (AQS-BLD-014). There are two braced lines in each direction, with two braced bays in each line. The diagonals act in tension only and are set at {math.degrees(th):.0f} degrees. Each diagonal carries a tension T of {T:.0f} kN and needs an area of at least {Abr:.0f} mm2 (AISC 360-22 D2), which a welded box of about {bb} mm provides. The overturning load on the columns of the braced bays is carried forward to task X-BLD-03.", '',
       '## 7. Result', '',
       'Every member in Tables 4.1 and 5.1 has a section that passes its check. The reservoir storeys govern the column sizes, and the columns step down in size above R3. All sections are sized here and welded from plate; none is taken from a catalogue of rolled sections.']
open('docs-authority/FRAME_CHECK.md', 'w').write('\n'.join(md) + '\n')
json.dump(dict(cols=[(k, KL, {c: [d[c][0], d[c][1]] for c in d}) for k, KL, d in cols], V_kN=V, brace_T_kN=T), open('docs-authority/inventory/FRAME_CHECK.json', 'w'), indent=1)
print(V, T, cols[-1][2]['interior'])
