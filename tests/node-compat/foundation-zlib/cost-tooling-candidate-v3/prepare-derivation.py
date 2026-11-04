"""Source-only M3 correction provenance; no original permission is modified."""
import difflib,hashlib,json,stat
from pathlib import Path
HERE=Path(__file__).parent.resolve();PARENT=HERE.with_name('cost-tooling-candidate-v2');PEER=HERE.parent/'independent-cost-source-publication-v2-failure-review-v1'
def h(raw):return hashlib.sha256(raw).hexdigest()
def write(name,value):
    with(HERE/name).open('x')as f:json.dump(value,f,indent=2);f.write('\n')
raw=(PARENT/'index.json').read_bytes();assert h(raw)=='6793721e6781bf045825f2a1c83108f97136f682fdae4d725ece4c31c750891b';index=json.loads(raw);changed=[];unchanged=[]
for r in index['files']:
    before=(PARENT/r['path']).read_bytes();assert h(before)==r['sha256']and len(before)==r['bytes'];p=HERE/r['path']
    if not p.exists():continue
    after=p.read_bytes()
    if before==after:unchanged.append(r['path'])
    elif len(before)<300000 and len(after)<300000:
        delta=list(difflib.ndiff(before.decode().splitlines(keepends=True),after.decode().splitlines(keepends=True)))
        assert ''.join(difflib.restore(delta,1)).encode()==before and ''.join(difflib.restore(delta,2)).encode()==after
        changed.append({'path':r['path'],'beforeSha256':h(before),'afterSha256':h(after),'exactForwardAndReverse':True,'ndiff':delta})
write('source-deltas.json',{'schemaVersion':1,'state':'EXACT_M3_SOURCE_PERMISSION_CORRECTION','parentIndexSha256':h(raw),'files':changed,'unchangedCopiedSourceMembers':unchanged})
peer_raw=(PEER/'index.json').read_bytes();assert h(peer_raw)=='064b8d4415f6444291db78f485a4b9052c691c90a3818a761a887473e2fa5bd5';peer=json.loads(peer_raw);plan=json.loads((HERE/'publication-plan.json').read_text());inputs=[]
for r in peer['files']+[{'path':'index.json','sha256':h(peer_raw),'bytes':len(peer_raw)}]:
    src=PEER/r['path'];data=src.read_bytes();assert h(data)==r['sha256']and len(data)==r['bytes'];p=HERE/'image/parent-publication-M3-failure'/r['path'];p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(data)
    inputs.append({'path':str(src.resolve()),'sha256':r['sha256'],'bytes':r['bytes']});plan['objects'].append({'source':str(p.resolve()),'destination':'metadata/parent-publication-M3-failure/'+r['path'],'sha256':r['sha256'],'bytes':r['bytes'],'sourceMode':stat.S_IMODE(p.stat().st_mode),'outputMode':stat.S_IMODE(p.stat().st_mode),'role':'historical-parent-M3-precopy-failure-not-current-admission'})
for number,r in enumerate(json.loads((PEER/'source-references.json').read_text())['files'][:7]):
    src=Path(r['path']);data=src.read_bytes();assert h(data)==r['sha256']and len(data)==r['bytes'];p=HERE/'image/parent-publication-M3-failure/raw'/('record-'+str(number)+'.data');p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb')as f:f.write(data)
    inputs.append(r);plan['objects'].append({'source':str(p.resolve()),'destination':'metadata/parent-publication-M3-failure/raw/'+p.name,'sha256':r['sha256'],'bytes':r['bytes'],'sourceMode':stat.S_IMODE(p.stat().st_mode),'outputMode':stat.S_IMODE(p.stat().st_mode),'role':'historical-parent-M3-precopy-failure-not-current-admission'})
plan['copyPermissionSchemaVersion']=2;plan['historicalToolingV2IndexSha256']=h(raw);plan['historicalPublicationM3FailurePeerIndexSha256']=h(peer_raw)
for r in plan['objects']:
    if 'mode'in r:
        r['sourceMode']=r.pop('mode');r['outputMode']=r['sourceMode']
(HERE/'publication-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
write('parent-hold-inputs.json',{'schemaVersion':1,'state':'ACTUAL_M3_PRECOPY_FAILURE_PRESERVED','files':inputs,'rootFailureReceiptSha256':'072dafb208503a2f3b45d69f0230abb3d4104240e2c02962c6d83c00be789457','sourcePermissionChanges':False,'rootActualSourcePublicationExitCode':1,'targetCreated':False,'codecActions':False})
write('correction-scope.json',{'schemaVersion':1,'state':'SOURCE_PERMISSION_ROLE_CORRECTION_UNREVIEWED','parentSourceIndexSha256':h(raw),'failurePeerIndexSha256':h(peer_raw),'correction':'Separate authenticated sourceMode from desired outputMode; copied .mode remains actual destination inventory mode; preserve both roles','actualFailedCapsules':20,'baseSourceModeDrift':0,'originalSourcesChmodded':False,'allNativeGuestCorpusAndToolPayloadBytesUnchanged':True,'actionsInvoked':False,'runtimeAcceptanceClaim':False})
print(json.dumps({'parentFilesRehashed':len(index['files']),'exactTextReversals':len(changed),'unchangedSourceMembers':len(unchanged),'failureProofFiles':len(inputs),'actions':False}))
