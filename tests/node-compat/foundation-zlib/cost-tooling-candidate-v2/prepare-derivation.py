"""Source-only parent preservation and exact text derivations, not publication."""
import difflib,hashlib,json,stat
from pathlib import Path
HERE=Path(__file__).parent.resolve();PARENT=HERE.with_name('cost-tooling-candidate-v1');PEER=HERE.parent/'independent-cost-tooling-source-review-v1'
def h(raw):return hashlib.sha256(raw).hexdigest()
def write(name,value):
    p=HERE/name
    with p.open('x')as f:json.dump(value,f,indent=2);f.write('\n')
raw=(PARENT/'index.json').read_bytes();assert h(raw)=='f5f13bfa0256a3e89d87827ea40d12dfbf617a23c304ba3b8335167c02bc3049';index=json.loads(raw)
changed=[];unchanged=[]
for r in index['files']:
    before=(PARENT/r['path']).read_bytes();assert h(before)==r['sha256']and len(before)==r['bytes'];p=HERE/r['path']
    if not p.exists():continue
    after=p.read_bytes()
    if after==before:unchanged.append(r['path'])
    elif len(before)<300000 and len(after)<300000:
        delta=list(difflib.ndiff(before.decode().splitlines(keepends=True),after.decode().splitlines(keepends=True)))
        assert ''.join(difflib.restore(delta,1)).encode()==before and ''.join(difflib.restore(delta,2)).encode()==after
        changed.append({'path':r['path'],'beforeSha256':h(before),'afterSha256':h(after),'exactForwardAndReverse':True,'ndiff':delta})
write('source-deltas.json',{'schemaVersion':1,'state':'EXACT_SOURCE_TEXT_AFTERIMAGES_NOT_NATIVE_PROJECTION','parentIndexSha256':h(raw),'files':changed,'unchangedCopiedSourceMembers':unchanged})
peer_raw=(PEER/'index.json').read_bytes();assert h(peer_raw)=='2d7b6465e216aee069aba85c5ee70cec39da002050587272c74f92ed5bd98660';peer_ix=json.loads(peer_raw);plan=json.loads((HERE/'publication-plan.json').read_text());proof_inputs=[]
for r in peer_ix['files']+[{'path':'index.json','sha256':h(peer_raw),'bytes':len(peer_raw)}]:
    src=PEER/r['path'];data=src.read_bytes();assert h(data)==r['sha256']and len(data)==r['bytes'];p=HERE/'image/parent-tooling-HOLD'/r['path'];p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(data)
    proof_inputs.append({'path':str(src.resolve()),'sha256':r['sha256'],'bytes':r['bytes']});plan['objects'].append({'source':str(p.resolve()),'destination':'metadata/parent-tooling-HOLD/'+r['path'],'sha256':r['sha256'],'bytes':r['bytes'],'mode':stat.S_IMODE(p.stat().st_mode),'role':'historical-parent-source-HOLD-not-current-admission'})
plan['historicalToolingSourceHoldIndexSha256']=h(raw);plan['historicalToolingSourceHoldReviewIndexSha256']=h(peer_raw);plan['context']['historicalToolingSourceHoldIndexSha256']=h(raw)
(HERE/'publication-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
write('parent-hold-inputs.json',{'schemaVersion':1,'files':proof_inputs,'state':'IMMUTABLE_PARENT_HOLD_PRESERVED','sourceActionsExecuted':False})
write('correction-scope.json',{'schemaVersion':1,'state':'COST_TOOLING_SOURCE_CORRECTIONS_UNREVIEWED','parentSourceIndexSha256':h(raw),'parentHoldReviewIndexSha256':h(peer_raw),'closedBySourceAfterimages':['COST-TOOL-M1','COST-TOOL-M2'],'corrections':['Reject all four pinned Rolldown NAPI_RS provider switches before loaders','Capture caller-owned descriptor primitives synchronously before awaits and return authenticated Root action SHA','Fresh source/oracle namespaces v2; own source-plan paths rebased, immutable native350/guestv2/tool input bytes unchanged'],'nativeMetadataProjection':False,'actionsInvoked':False,'runtimeAcceptanceClaim':False})
print(json.dumps({'parentFilesRehashed':len(index['files']),'exactTextReversals':len(changed),'unchangedSourceMembers':len(unchanged),'holdProofFiles':len(proof_inputs),'actions':False}))
