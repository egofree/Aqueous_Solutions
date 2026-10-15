"""Study placement of units with no envelope (X-BLD, AQS-PLACE-STUDY-001).
Footprints are labelled assumptions (A-M register). Packs each unit into its
sector block on a 100 mm grid, 600 mm clear of every placed box on that level.
Writes flow_graph/placement_study.json. Does not edit placement_seed.json."""
import json
SEED='flow_graph/placement_seed.json'; REP='flow_graph/placement_report.json'; G='flow_graph/plant_flow_graph.json'
# Study footprints [x, y, z] mm by category. Assumptions, not measurements.
CAT={'skid':[1200,800,1800],'tank':[2400,1800,1500],'bed':[4800,1200,600],'pen':[3000,2400,2000],
     'room':[3000,3000,2600],'manifold':[600,300,300],'cold_box':[2000,1500,2600],'small_cold':[800,600,1500]}
UNIT={'FISH':'tank','FISH_SUMP':'tank','CLARIFIER':'tank','DUCKWEED':'bed','VEG_BED':'bed','NFIX_BED':'bed',
 'PEANUT':'bed','SUNFLOWER':'bed','CLOVER':'bed','ANIMAL_PEN':'pen','DIGESTER':'tank','COMPOST':'pen',
 'HAB_GALLEY':'room','HAB_MED':'room','HAB_SLEEP':'room','HAB_WASH':'room','HDR_CO2':'manifold','HDR_N2':'manifold',
 'CRYO_ASU':'cold_box','H2_PURIFIER':'small_cold','CRYO_AR':'small_cold','CRYO_HE':'small_cold','CRYO_KR':'small_cold','CRYO_NE':'small_cold','CRYO_XE':'small_cold'}
CLR=600
# Second tier inside a tall block: floor at datum + TIER mm, for beds and skids only (assumption, register).
TIER={'FARM':2250}
# FARM growth for floor-bound water tanks (X-RSZ-05): basement block on L-2 east of HYDRO.
EXTRA=[{'block_id':'FARM_AQ','level':'L-2','origin_mm':[18000,4000],'size_mm':[6000,8000,3500],'source':'X-RSZ-05 study growth','unit_ids':[]}]
# FARM growth on L0 (A-M-154): sized crop beds fill the L1 FARM block, so FARM process skids, pens and overflow move to a 12 x 18 m bay of the
# east extension hall next to the core, 4.5 m clear, on the same column grid as FARM above.
EXTRA.append({'block_id':'FARM_EXT','level':'L0','origin_mm':[24000,0],'size_mm':[12000,18000,4500],'source':'X-PAR-04 study growth in EXT_HALL_E (A-M-154)','unit_ids':[]})
CONTAINER={'FARM_EXT':('L0',24000.0,0.0,96000,108000)}   # the EXT_HALL placeholder box is the hall the bay sits in, not an obstacle
OVERFLOW={'FARM':'FARM_EXT'}
GROW={('FARM','tank'):'FARM_AQ'}
# Units whose sector has no block: placed in the block of their process neighbour (X-PAR acid loop: BMED evaporators).
BLOCK_OF={'EVAP_ACID':'BMED_CRU','EVAP_BASE':'BMED_CRU'}
# X-PAR-04: crop beds take their footprint from the sized area in the graph (GROW_BED params.area_m2, crop_basis.area_m2), laid out as
# rows ROW_W wide and at most ROW_L long (A-M-154); each row is placed like a study unit, so a growing bed shows up as unplaced rows.
ROW_W, ROW_L, ROW_H = 1200, 10800, 600
def bed_area(n):
    p = n.get('params', {}); return p.get('area_m2') or (p.get('crop_basis') or {}).get('area_m2')
def bed_rows(n):
    import math
    a = bed_area(n)*1e6; k = max(1, math.ceil(a/ROW_W/ROW_L)); L = int(math.ceil(a/ROW_W/k/100)*100)
    return [(f"{n['unit_id']}/R{i+1}", [L, ROW_W, ROW_H]) for i in range(k)]
def boxes(seed,rep):
    B={}
    BLK={tuple(b['size_mm'][:2]) for b in seed['blocks']}
    for r in seed['units']+rep.get('moves',[])+rep.get('create_moves',[])+rep.get('apply_moves',[]):
        o,z=r.get('origin_mm'),r.get('size_mm')
        if o and z and len(z)>=2:
            if r['unit_id'] in B and tuple(z[:2]) in BLK: continue   # keep a real envelope over a block-sized placeholder
            B[r['unit_id']]=(r.get('level'),o[0],o[1],z[0],z[1])
            if len(z)>2 and z[2]>2250-CLR: B[r['unit_id']+'#T2']=((r.get('level') or '')+'T2',o[0],o[1],z[0],z[1])
    return B
def hit(a,b,c=CLR):
    return a[1]<b[1]+b[3]+c and b[1]<a[1]+a[3]+c and a[2]<b[2]+b[4]+c and b[2]<a[2]+a[4]+c
AISLE={'FARM':914,'FARM_EXT':914}   # farm rows are walked: NFPA 101 (2024) 7.3.4.1.1 / IBC 2021 1018.5 914 mm clear (as farm_rerow.py, A-M-102)
def main():
    seed=json.load(open(SEED)); rep=json.load(open(REP)); g=json.load(open(G))
    blk={b['block_id']:b for b in seed['blocks']+EXTRA}
    B=boxes(seed,rep)
    placed=[v for v in B.values()]
    pos_units=set(B)
    beds=[n for n in g['nodes'] if n.get('presence')=='present' and n['sector_id']=='FARM' and bed_area(n)]
    for n in beds: B.pop(n['unit_id'],None); B.pop(n['unit_id']+'#T2',None)
    placed=[v for k,v in B.items()]
    need=[n for n in g['nodes'] if n['unit_id'] not in pos_units and n.get('presence')=='present' and not bed_area(n)]
    for n in beds:
        for rid,sz in bed_rows(n): need.append(dict(n, unit_id=rid, _size=sz, _parent=n['unit_id']))
    import runpy
    out=[];fail=[]
    want=set(json.load(open('flow_graph/study_targets.json')))
    SZ=lambda n: n.get('_size') or [int(v) for v in ((n.get('params',{}).get('sizing') or {}).get('size_mm') or n.get('params',{}).get('size_mm') or CAT[UNIT.get(n['unit_id'],'skid')])[:3]]   # sized value first (X-PAR-04)
    for n in sorted(need,key=lambda n:-SZ(n)[0]*SZ(n)[1]):
        u=n['unit_id']
        if u not in want and '_parent' not in n: continue
        c='bed' if '_parent' in n else UNIT.get(u,'skid'); sz=SZ(n)
        b0=blk.get(BLOCK_OF.get(u) or GROW.get((n['sector_id'],c),n['sector_id']))
        if not b0: fail.append((u,'no block'));continue
        for b in [b0]+([blk[OVERFLOW[b0['block_id']]]] if b0['block_id'] in OVERFLOW else []):
            lv=b['level'];ox,oy=b['origin_mm'][:2];bx,by=b['size_mm'][:2];ok=None
            own=(ox,oy,bx,by)  # block-sized placeholder boxes of this block are not obstacles
            for rot in (sz,[sz[1],sz[0],sz[2]]):
                for y in range(oy,oy+by-rot[1]+1,100):
                    for x in range(ox,ox+bx-rot[0]+1,100):
                        cand=(lv,x,y,rot[0],rot[1])
                        if not any(p[0]==lv and p[1:]!=own and p!=CONTAINER.get(b['block_id']) and hit(cand,p,AISLE.get(b['block_id'],CLR)) for p in placed): ok=(cand,rot);break
                    if ok:break
                if ok:break
            tier=0
            if not ok and b['block_id'] in TIER and c in ('bed','skid'):
                for rot in (sz,[sz[1],sz[0],sz[2]]):
                    for y in range(oy,oy+by-rot[1]+1,100):
                        for x in range(ox,ox+bx-rot[0]+1,100):
                            cand=(lv+'T2',x,y,rot[0],rot[1])
                            if not any(p[0]==lv+'T2' and p[1:]!=own and p!=CONTAINER.get(b['block_id']) and hit(cand,p,AISLE.get(b['block_id'],CLR)) for p in placed): ok=(cand,rot);break
                        if ok:break
                    if ok:break
                tier=TIER[b['block_id']]
            if ok: break
        if not ok: fail.append((u,b['block_id']));continue
        (lv2,x,y,_,_),rot=ok; placed.append(ok[0])
        if not tier and rot[2]>TIER.get(b['block_id'],1e9)-CLR: placed.append((lv+'T2',x,y,rot[0],rot[1]))
        out.append({'unit_id':u,'level':lv,'block_id':b['block_id'],'origin_mm':[x,y,seed['datums_mm'][lv]+tier],'tier':2 if tier else 1,'size_mm':rot,
          'category':c,'status':'STUDY','source':(f"row of {n['_parent']} {bed_area(n):.1f} m2 from the graph (A-M-154)" if '_parent' in n else (f"graph size_mm" if (n.get('params',{}).get('sizing') or {}).get('size_mm') or n.get('params',{}).get('size_mm') else f"AQS-PLACE-STUDY-001 study footprint '{c}' (assumption)"))+f"; packed in {b['block_id']} 600 mm clear"})
    json.dump({'doc_id':'AQS-PLACE-STUDY-001','status':'STUDY. Not issued placement. Footprints are register assumptions.',
               'categories':CAT,'units':out,'unplaced':fail},open('flow_graph/placement_study.json','w'),indent=2,ensure_ascii=True)
    print(len(out),'placed;',fail, 'FARM_EXT', blk['FARM_EXT']['size_mm'])
    return fail
if __name__=='__main__':
    # FARM_EXT bay length from need: grow along the hall in 6 m column bays until every unit is placed (A-M-154)
    for L in range(12000, 96001, 6000):
        EXTRA[-1]['size_mm'][0] = L
        if not [f for f in main() if f[1] == 'FARM_EXT']: break
