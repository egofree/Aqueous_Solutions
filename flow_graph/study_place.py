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
GROW={('FARM','tank'):'FARM_AQ'}
# Units whose sector has no block: placed in the block of their process neighbour (X-PAR acid loop: BMED evaporators).
BLOCK_OF={'EVAP_ACID':'BMED_CRU','EVAP_BASE':'BMED_CRU'}
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
def hit(a,b):
    return a[1]<b[1]+b[3]+CLR and b[1]<a[1]+a[3]+CLR and a[2]<b[2]+b[4]+CLR and b[2]<a[2]+a[4]+CLR
def main():
    seed=json.load(open(SEED)); rep=json.load(open(REP)); g=json.load(open(G))
    blk={b['block_id']:b for b in seed['blocks']+EXTRA}
    B=boxes(seed,rep)
    placed=[v for v in B.values()]
    pos_units=set(B)
    need=[n for n in g['nodes'] if n['unit_id'] not in pos_units and n.get('presence')=='present']
    import runpy
    out=[];fail=[]
    want=set(json.load(open('flow_graph/study_targets.json')))
    for n in sorted(need,key=lambda n:-CAT[UNIT.get(n['unit_id'],'skid')][0]*CAT[UNIT.get(n['unit_id'],'skid')][1]):
        u=n['unit_id']
        if u not in want: continue
        c=UNIT.get(u,'skid'); sz=CAT[c]
        b=blk.get(BLOCK_OF.get(u) or GROW.get((n['sector_id'],c),n['sector_id']))
        if not b: fail.append((u,'no block'));continue
        lv=b['level'];ox,oy=b['origin_mm'][:2];bx,by=b['size_mm'][:2];ok=None
        own=(ox,oy,bx,by)  # block-sized placeholder boxes of this block are not obstacles
        for rot in (sz,[sz[1],sz[0],sz[2]]):
            for y in range(oy,oy+by-rot[1]+1,100):
                for x in range(ox,ox+bx-rot[0]+1,100):
                    cand=(lv,x,y,rot[0],rot[1])
                    if not any(p[0]==lv and p[1:]!=own and hit(cand,p) for p in placed): ok=(cand,rot);break
                if ok:break
            if ok:break
        tier=0
        if not ok and b['block_id'] in TIER and c in ('bed','skid'):
            for rot in (sz,[sz[1],sz[0],sz[2]]):
                for y in range(oy,oy+by-rot[1]+1,100):
                    for x in range(ox,ox+bx-rot[0]+1,100):
                        cand=(lv+'T2',x,y,rot[0],rot[1])
                        if not any(p[0]==lv+'T2' and p[1:]!=own and hit(cand,p) for p in placed): ok=(cand,rot);break
                    if ok:break
                if ok:break
            tier=TIER[b['block_id']]
        if not ok: fail.append((u,b['block_id']));continue
        (lv2,x,y,_,_),rot=ok; placed.append(ok[0])
        if not tier and rot[2]>TIER.get(b['block_id'],1e9)-CLR: placed.append((lv+'T2',x,y,rot[0],rot[1]))
        out.append({'unit_id':u,'level':lv,'block_id':b['block_id'],'origin_mm':[x,y,seed['datums_mm'][lv]+tier],'tier':2 if tier else 1,'size_mm':rot,
          'category':c,'status':'STUDY','source':f"AQS-PLACE-STUDY-001 study footprint '{c}' (assumption); packed in {b['block_id']} 600 mm clear"})
    json.dump({'doc_id':'AQS-PLACE-STUDY-001','status':'STUDY. Not issued placement. Footprints are register assumptions.',
               'categories':CAT,'units':out,'unplaced':fail},open('flow_graph/placement_study.json','w'),indent=2,ensure_ascii=True)
    print(len(out),'placed;',fail)
if __name__=='__main__':main()
