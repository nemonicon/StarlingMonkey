"""Thin reversible SOURCE correction and pure DATA tests; no owner helpers."""
from pathlib import Path
import ast,hashlib,json,os
import collector
HERE=Path(__file__).resolve().parent;K=HERE.parent;OLD=K/'ownership-gc-candidate-v1'
inputs={}
def descriptor(p):
    p=Path(p);before=p.stat();h=hashlib.sha256();assert p.is_file()and not p.is_symlink()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    after=p.stat();assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns)
    d=dict(path=str(p.resolve()),sha256=h.hexdigest(),bytes=before.st_size);inputs[d['path']]=d;return d
def load(p):descriptor(p);return json.loads(Path(p).read_bytes())
def write(name,v,raw=False):
    with(HERE/name).open('xb')as f:f.write(v if raw else(json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
def family(p,digest):
    ix=descriptor(p/'index.json');assert ix['sha256']==digest
    v=load(p/'index.json')
    for r in v['files']:
        d=descriptor(p/r['path']);assert d['sha256']==r['sha256']and d['bytes']==r['bytes']
    assert {f.relative_to(p).as_posix()for f in p.rglob('*')if f.is_file()}=={r['path']for r in v['files']}|{'index.json'}
    return ix
old_index=family(OLD,'3b6f04806a8990e99dbda0a1292bbb559801f99f2d21b7b57e5fa6020fa03dcf')
hold_root=K/'independent-ownership-gc-source-review-v1';hold_index=family(hold_root,'2ac980be8bb846a880888622d85ec0bf46273eaff425b4de8babff6e0553d597');hold=load(hold_root/'required-correction-contract.json');assert descriptor(hold_root/'required-correction-contract.json')['sha256']=='00c50d60567ac2bde32f2ea32efec66f824ecee22ed3478614c92d7884255349'
native_index=family(K/'ownership-gc-native-candidate-v1','2fbc01ad04c38057b65a26f33c7afa8683022ee62c020202b9c64ac7105a605a')
guest=(OLD/'guest.GC.UNEXECUTED.mjs').read_text();edits=[]
def replace(before,after):
    global guest
    assert guest.count(before)==1;guest=guest.replace(before,after);edits.append(dict(before=before,after=after,count=1))
replace('const pressureRecords=[];',"const pressureRecords=[];let pressureRequests=0;\nfunction gcObservation(scope,recordsStart=0,requestsStart=0){return{version:'public-buffer-gc-pressure-v1',scope,publicGcPressureRequested:pressureRequests>requestsStart,publicGcPressureRequests:pressureRequests-requestsStart,publicGcPressureRecords:pressureRecords.length-recordsStart,entropyRequested:false,actualNativeGcCountObserved:false,strongApplicationOwnersCombined:true,isolatedTemporaryRootsProved:false,finalizerFreeWipeObserved:false};}")
replace('function pressure(phase){', 'function pressure(phase){pressureRequests++;')
replace('export async function run(caseId){\n count.runCalls++;', 'export async function run(caseId){\n const pressureStart=pressureRecords.length,pressureRequestsStart=pressureRequests;count.runCalls++;')
replace('gcOrEntropyRequested:false',"gcObservation:gcObservation('this-run',pressureStart,pressureRequestsStart)")
replace('semanticFailureNotNativeTrapProof:true',"gcObservation:gcObservation('this-run',pressureStart,pressureRequestsStart),semanticFailureNotNativeTrapProof:true")
replace("schemaVersion:1,kind:'crypto-owner-within-export-gc-validation-v1',pressure:","schemaVersion:2,kind:'crypto-owner-within-export-gc-validation-v2',gcObservation:gcObservation('outer-validate'),pressure:")
assert 'gcOrEntropyRequested'not in guest and guest.count('pressureRequests++;')==1 and guest.count("pressure('")==4
write('guest.GC.UNEXECUTED.mjs',guest.encode(),True)
write('correction-derivations.json',dict(schemaVersion=1,source=descriptor(OLD/'guest.GC.UNEXECUTED.mjs'),afterimage='guest.GC.UNEXECUTED.mjs',edits=edits,oldGcOrEntropyRequestedFieldRemoved=True,noDirectOnlyReinterpretation=True,countsTrackSourceRequestsNotNativeGcCollections=True))
old_deriv=load(OLD/'guest-derivations.json');back=guest
for e in reversed(edits):assert back.count(e['after'])==1;back=back.replace(e['after'],e['before'])
assert back==(OLD/'guest.GC.UNEXECUTED.mjs').read_text()
for e in reversed(old_deriv['edits']):assert back.count(e['after'])==1;back=back.replace(e['after'],e['before'])
assert back==Path(old_deriv['source']['path']).read_text();descriptor(old_deriv['source']['path'])
normal_path=K/'independent-ownership-wasmtime-v1-results-review-v1/expected-complete-record.json';normal=load(normal_path)
accepted_index=load(normal_path.parent/'index.json');r=next(r for r in accepted_index['files']if r['path']==normal_path.name);assert descriptor(normal_path)['sha256']==r['sha256'];assert descriptor(normal_path.parent/'index.json')['sha256']=='d1e3f9f1edb723efc1fc6bead20c8e7cbfc9a06845ea2bc1bdb8235c2a6f357b'
model=collector.expected(normal);write('expected-complete-gc-record.json',model)
tests=0
def check(v):
    global tests
    assert v;tests+=1
def reject(v):
    global tests
    try:collector.validate(v,model)
    except AssertionError:tests+=1;return
    raise AssertionError('negative record accepted')
check(collector.validate(model,model));check([r['gcObservation']['publicGcPressureRecords']for r in model['records']]==[4,4,8,0]);check(model['gcObservation']['publicGcPressureRequested']is True)
for mutation in ['old-field','outer-false','run3-blanket-true','entropy-true','actual-gc-count','truncated-hex','wrong-phase','missing-record','counter-change','tag-change','unknown-field']:
    v=json.loads(json.dumps(model))
    if mutation=='old-field':v['records'][0]['gcOrEntropyRequested']=False
    elif mutation=='outer-false':v['gcObservation']['publicGcPressureRequested']=False
    elif mutation=='run3-blanket-true':v['records'][3]['gcObservation']['publicGcPressureRequested']=True
    elif mutation=='entropy-true':v['gcObservation']['entropyRequested']=True
    elif mutation=='actual-gc-count':v['gcObservation']['actualNativeGcCountObserved']=True
    elif mutation=='truncated-hex':v['pressure']['records'][0]['decodedHex']=v['pressure']['records'][0]['decodedHex'][:-2]
    elif mutation=='wrong-phase':v['pressure']['records'][0]['phase']='wrong'
    elif mutation=='missing-record':v['pressure']['records'].pop()
    elif mutation=='counter-change':v['after']['counters']['signCalls']+=1
    elif mutation=='tag-change':v['records'][0]['result']['operations']['firstSignatureHex']='00'*32
    else:v['unexpected']=True
    reject(v)
for delta in [4,4,8,0]:
    observed=collector.observation('this-run',delta,delta);check(observed['publicGcPressureRequested']is(delta>0));check(observed['entropyRequested']is False);check(observed['actualNativeGcCountObserved']is False)
partial=collector.observation('this-run',1,0);check(partial['publicGcPressureRequested']is True and partial['publicGcPressureRecords']==0)
for old,new in zip(normal['records'],model['records']):
    old=json.loads(json.dumps(old));old.pop('gcOrEntropyRequested');new=json.loads(json.dumps(new));new.pop('gcObservation');check(old==new)
check(len(model['pressure']['records'])==16);check(sum(collector.DELTAS)==16)
for name in ['prepare.py','collector.py']:ast.parse((HERE/name).read_text());tests+=1
contract=load(OLD/'follow-on-contract.json');contract.update(state='UNEXECUTED_CRYPTO_OWNER355_ISOLATED_GC_SOURCE_PROPOSAL_V2',guestObservationSchemaVersion=2,outerKind='crypto-owner-within-export-gc-validation-v2',gcObservationVersion=collector.VERSION,oldGcOrEntropyRequestedFieldForbidden=True,perRunPressureRequests=[4,4,8,0],perRunPressureRecords=[4,4,8,0],perRunPublicGcPressureRequested=[True,True,True,False],outerPublicGcPressureRequested=True,outerPublicGcPressureRequests=16,outerPublicGcPressureRecords=16,entropyRequested=False,actualNativeGcCountObserved=False,requestsCountBeforeBufferCall=True,failedRunObservationRetained=True,wholeExpectedRecord='expected-complete-gc-record.json',collector='collector.py',nativeSourceSuccessor=native_index,heldSourceIndex=old_index,holdReviewIndex=hold_index)
contract['requiredUnimplementedGates']=['Independent review of this corrected guest/proposal and whole collector model','Independent review of isolated native source2fbc + external Root controller','Actual isolated native build/freeze/bootstrap + complete independent native proof and new GC-only pins','Separate component source/selected Buffer composition and actual artifact reviews','New explicit Root GC export authority + complete raw typed collector','Only then bounded actual strongly held-key GC fixture and independent result review']
contract['requiredSourcePeer']=dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_GC_SOURCE_REVIEW_PASSED_V2',sourceIndexSha256=None,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False)
write('follow-on-contract.json',contract)
write('inherited-source.json',dict(schemaVersion=1,heldSourceIndex=old_index,holdReviewIndex=hold_index,requiredCorrectionContract=descriptor(hold_root/'required-correction-contract.json'),nativeSourceIndex=native_index,originalGuest=old_deriv['source'],publicWit=descriptor(OLD/'public-abi.wit'),originalGuestEdits=8,newExactEdits=len(edits),acceptedNormalExpectedRecord=descriptor(normal_path),normalProtection=descriptor(OLD/'normal-protection.json'),noOldSourceModified=True,noNativeSourceOrPinOrAuthorityAdopted=True))
for inherited in [OLD/'input-freeze.json',K/'ownership-gc-native-candidate-v1/input-freeze.json']:
    for r in load(inherited)['files']:
        d=descriptor(r['path']);assert d['sha256']==r['sha256']and d['bytes']==r['bytes']
for r in list(inputs.values()):assert descriptor(r['path'])==r
write('input-freeze.json',dict(schemaVersion=1,files=list(inputs.values()),allFinallyRehashed=True,sourceOnly=True))
write('pure-results.json',dict(schemaVersion=1,state='GC_OBSERVATION_V2_PURE_DATA_AND_EXACT_REVERSALS_PASSED',checks=tests,oldGuestEditsReversed=8,newGuestEditsReversed=len(edits),perRunPressureRequests=[4,4,8,0],outerPressureRequests=16,expectedCompleteRecords=1,actualGcRecords=0,actualNativeGcCountObserved=False,ownerActionsInvoked=False))
print(json.dumps(dict(state='GC_GUEST_V2_SOURCE_PREPARED_UNREVIEWED',pureChecks=tests,oldExactEdits=8,newExactEdits=len(edits),sourceInputSpellings=len(inputs),actionsInvoked=False)))
