#!/usr/bin/env python3
"""Stored public data only; no owner imports, tools or target execution."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from binary_reader import sections,uint,string,core_imports

HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
SOURCE=FAMILY/'measurement-execution-activated-v2'
COLLECTOR=FAMILY/'measurement-stock-composition-candidate-v1'
STOCK=Path('/tmp/starling-node-compat/production-common-byte-stock-only-v1')
COMPOSE=Path('/tmp/starling-node-compat/production-common-byte-composition-v1')
SOURCE_SHA='1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612'
COLLECTOR_SHA='257e3800c86c3d2eb2af9cdebc3ee0421f97b947166e853bb70dc95a188033da'
PAIR_SHA='f36268516df72ac5b0d5b5ae8fd808d1ce94d40ca364dc533c522fe399b2681e'
STOCK_ROOT=FAMILY/'production-adoption-v1/common-byte-stock-only-root-results-v1.json'
STOCK_ROOT_SHA='c211db87c982ed8ae42a8929d8af1dba7149c9f39531dc333ec71ef52d750976'
COMPOSE_ROOT=FAMILY/'production-adoption-v1/common-byte-composition-root-results-v1.json'
COMPOSE_ROOT_SHA='ef860821e3765fc2a1bf137c526c00dea86c93599c12bbeea7d36407cd94d090'
OLD=FAMILY/'independent-common-byte-v2-three-arm-failure-review-v1'
OLD_SHA='bf9fa2a619a92fe6e84b63df8a7650276aa2b13b5d41205835563051b5c3d2ef'
seen={}

def checked(path,digest=None,size=None):
    path=Path(path);before=path.lstat();assert stat.S_ISREG(before.st_mode)and not path.is_symlink(),str(path)
    h=hashlib.sha256()
    with path.open('rb')as src:
        for block in iter(lambda:src.read(1024*1024),b''):h.update(block)
    after=path.lstat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
    row={'path':str(path),'sha256':h.hexdigest(),'bytes':before.st_size}
    assert digest is None or row['sha256']==digest,str(path)
    assert size is None or row['bytes']==size,str(path)
    assert str(path)not in seen or seen[str(path)]==row,str(path)
    seen[str(path)]=row;return row['sha256']

def load(path,digest=None,size=None):
    digest=checked(path,digest,size);raw=Path(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
    return json.loads(raw)

def exact(a,b,label):
    # Type-sensitive recursive equality without formatting or duplicating traces.
    assert type(a)is type(b),label+' type'
    if isinstance(a,dict):
        assert set(a)==set(b),label+' keys'
        for k in a:exact(a[k],b[k],label+'/'+k)
    elif isinstance(a,list):
        assert len(a)==len(b),label+' length'
        for i,(x,y)in enumerate(zip(a,b)):exact(x,y,label+'/'+str(i))
    else:assert a==b,label

def index(root,digest,count):
    d=load(root/'index.json',digest);assert len(d['files'])==count
    for row in d['files']:
        assert not Path(row['path']).is_absolute()and '..'not in Path(row['path']).parts
        checked(root/row['path'],row['sha256'],row['bytes'])
    return d

def descriptor(row):return load(row['path'],row['sha256'],row['bytes'])
def tuple_of(record):return{k:record[k]for k in['arm','componentPath','componentSha256','componentBytes','enginePath','engineSha256','engineMetadataSha256','modulePath','bundleSha256','transpiledFiles','coreFiles']}

index(SOURCE,SOURCE_SHA,35);index(COLLECTOR,COLLECTOR_SHA,20);index(OLD,OLD_SHA,16)
old_result=load(OLD/'results.json','dbcc5fe7b6fe87595499c423119477567ab8fd794f38d04f3aeb203b88e95d19')
assert old_result['durableReturnedObservations']==231 and old_result['wholeParentFourArmGatePassed']is False
old_paths=load(OLD/'verified-paths.json');assert len(old_paths)==9679
for row in old_paths:checked(row['path'],row['sha256'],row['bytes'])
seal=load(SOURCE/'input-freeze.json');assert len(seal['inputs'])==7709
for row in seal['inputs']:
    p=Path(row['path']);checked(p if p.is_absolute()else SOURCE/p,row['sha256'],row['bytes'])
assert len(seal['toolTrees'])==2 and len(seal['toolLinks'])==22
for tree in seal['toolTrees']:
    entries=[];base=Path(tree['path'])
    for directory,dirs,files in os.walk(base,followlinks=False):
        for name in sorted(dirs+files):
            p=Path(directory)/name;kind='symlink'if p.is_symlink()else'directory'if p.is_dir()else'file'if p.is_file()else None
            assert kind;entries.append({'path':str(p.relative_to(base)),'kind':kind})
        dirs[:]=[name for name in dirs if not(Path(directory)/name).is_symlink()]
    exact(sorted(entries,key=lambda x:x['path']),tree['entries'],'tool members')
for link in seal['toolLinks']:
    assert os.readlink(link['path'])==link['linkText']and str(Path(link['path']).resolve())==link['resolvedTarget']

stock_root=load(STOCK_ROOT,STOCK_ROOT_SHA);compose_root=load(COMPOSE_ROOT,COMPOSE_ROOT_SHA)
for root,kind in[(stock_root,'ROOT_STOCK_ONLY_COMMON_BYTE_CORRECTNESS_TERMINAL_ZERO_V1'),(compose_root,'ROOT_COMMON_BYTE_COMPOSITION_TERMINAL_ZERO_V1')]:
    assert root['state']==kind and root['rawOuterExit']==0
    assert root['collectorSourceIndexSha256']==COLLECTOR_SHA and root['guestSourceFamilyIndexSha256']==SOURCE_SHA and root['pairPinsSha256']==PAIR_SHA
    assert root['runtimeAcceptanceClaim']is root['timingAllowed']is root['performanceClaim']is False
    for k in['result','completion','terminal','stdout','stderr']:checked(root[k]['path'],root[k]['sha256'],root[k]['bytes'])
stock_complete=descriptor(stock_root['completion']);assert len(stock_complete['outputs'])==446 and len(stock_complete['links'])==1
assert stock_complete['state']=='STOCK_ONLY_OUTPUTS_SEALED_EXTERNAL_EXIT_ZERO_REQUIRED'and stock_complete['requiresIndependentRawOuterExitZero']is True
exact(stock_complete['result'],stock_root['result'],'stock result binding')
for row in stock_complete['outputs']:checked(row['path'],row['sha256'],row['bytes'])
module_link=stock_complete['links'][0]
assert module_link['path']==str(STOCK/'node_modules')and os.readlink(module_link['path'])==module_link['linkText']
assert str(Path(module_link['path']).resolve())==module_link['resolvedTarget']==str(Path(module_link['linkText']).resolve())
stock_report=descriptor(stock_root['result']);assert stock_report['state']=='ACTUAL_COMMON_BYTE_STOCK_ONLY_CORRECTNESS_PASSED'and len(stock_report['records'])==1
assert stock_report['guestSourceFamilyIndexSha256']==SOURCE_SHA and stock_report['collectorSourceIndexSha256']==COLLECTOR_SHA and stock_report['pairPinsSha256']==PAIR_SHA
assert stock_report['commonCases']==8 and stock_report['controlCases']==6 and stock_report['failedParentRawOuterExit']==1
r=stock_report['records'][0];assert r['arm']=='stock-on'and r['correctnessPassed']is r['identityPassed']is r['checkpointProbePassed']is True
pair=load(SOURCE/'reviewed-pair.json',PAIR_SHA);on=pair['variants']['benchmark-classic-on']
assert r['engineSha256']==on['engineSha256']and r['engineMetadataSha256']==on['metadataSha256']
checked(r['enginePath'],on['engineSha256'],on['engineBytes']);checked(r['enginePath']+'.build.json',on['metadataSha256'])
checked(r['componentPath'],r['componentSha256'],r['componentBytes'])
directory=Path(r['modulePath']).parent
for row in r['transpiledFiles']:checked(directory/row['name'],row['sha256'],row['bytes'])
assert r['coreFiles']==['common_byte.core.wasm']and 'common_byte.core.wasm'in(directory/'common_byte.js').read_text()
wit=(directory/'emitted.wit').read_text();assert not re.search(r'\bimport\b',wit)
for declaration in['export setup: func(index: u32) -> s32;','export inspect: func(index: u32) -> string;','export batch: func(index: u32, iterations: u32) -> string;','export identity: func() -> string;','export checkpoint-probe: func() -> string;']:assert declaration in wit
assert len(re.findall(r'\bexport\s+',wit))==5
exports=[];embedded=[];types=[]
for kind,payload in sections(Path(r['componentPath']).read_bytes(),bytes.fromhex('0061736d0d000100')):
    if kind==10:count,pos=uint(payload,0);assert count==0 and pos==len(payload)
    elif kind==11:
        count,pos=uint(payload,0)
        for _ in range(count):
            assert payload[pos]==0;n,pos=string(payload,pos+1);sort=payload[pos];pos+=1;target,pos=uint(payload,pos);assert payload[pos]==0;pos+=1;exports.append((n,sort))
        assert pos==len(payload)
    elif kind==1:embedded.append(payload)
    elif kind==7:types.append(payload.hex())
assert sorted(exports)==sorted((n,1)for n in['setup','inspect','batch','identity','checkpoint-probe'])
assert types==['01400105696e64657879007a','01400105696e646578790073','01400205696e646578790a697465726174696f6e73790073','0140000073']
core=(directory/'common_byte.core.wasm').read_bytes();assert core_imports(core)==[]
standard=lambda raw:[(kind,hashlib.sha256(value).hexdigest())for kind,value in sections(raw,bytes.fromhex('0061736d01000000'))if kind!=0]
assert sum(standard(x)==standard(core)for x in embedded)==1
assert r['emittedImports']==r['interfaceAudit']['emittedImports']==[]and r['interfaceAudit']['componentSha256']==r['componentSha256']
graph=load(directory/'bundle-graph.json');exact(graph,r['graph'],'stock graph record');assert len(graph['modules'])==105 and len(graph['physicalSources'])==73 and len(graph['virtualSources'])==15
checked(directory/'application.bundle.mjs',r['bundleSha256'],graph['bundleBytes'])
previous=load(SOURCE/'stock-source-graph.json');assert 'provider'not in previous and len(previous['sourceBeforeAfter'])==3
old_own={row['path']for row in previous['sourceBeforeAfter']};prior=[x for x in previous['modules']if x not in old_own];assert len(prior)==99
new_own=[str(SOURCE/name)for name in['guest.mjs','capture-before.mjs','workload.mjs','control-workload.mjs','protocol.mjs','stock-provider.mjs']]
exact(graph['modules'],sorted(prior+new_own),'99 unchanged prior plus6 original guest')
exact(sorted(graph['virtualSources'],key=lambda x:x['id']),sorted(previous['virtualSources'],key=lambda x:x['id']),'virtual stock source')
for row in graph['physicalSources']:checked(row['path'],row['sha256'],row['bytes'])
for row in previous['physicalSources']:checked(row['path'],row['sha256'],row['bytes'])
edges=[x for x in graph['resolutions']if x['request']=='process/'and'/readable-stream/lib/'in(x['importer']or'')]
assert len(edges)==7 and all(x['result']==previous['scheduler']for x in edges)
assert sum(x.endswith('/stream/scheduler.js')for x in graph['modules'])==1
assert graph['stockOptions']=={}and graph['stockSchedulerOverride']is False and graph['imports']==[]
assert r['packager']['build']['jcoVersion']=='1.40.0'

oracle=load(SOURCE/'node-common-oracle.json')['cases']+load(SOURCE/'node-control-oracle.json')['cases'];assert len(oracle)==14
identity={'defaultGraph':True,'promisesGraph':True,'eventEmitterPrototype':True,'selectedTickType':'function','decoderA':'A','bufferView':True,'bufferSameAsBefore':False,'globalSameAsProvider':True,'beforeBufferType':'function','globalChangedDuringProvider':True}
exact(r['identity'],identity,'stock own Buffer identity')
probe=r['checkpointProbe'];assert probe['callbacks']==1 and sorted(probe['trace'])==['microtask','selected-tick']and probe['queueDepthObserved']is probe['terminalQueueEmptyObserved']is False
c=r['correctness'];assert c['retainedRotations']==3 and [len(x)for x in c['rounds']]==[14]*3 and len(c['freshRows'])==14 and len(c['wasmtime'])==16
calls=[('identity',identity),('checkpoint-retained',probe)]
for rotation,rows in enumerate(c['rounds']):
    for i,value in enumerate(rows):
        expected={'calls':rotation*14+i+1,'setup':oracle[i]['setup'],'result':oracle[i]['expected']};exact(value,expected,'retained Node result');calls.append(('inspect',expected))
calls += [('checkpoint-after',probe),('identity',identity),('checkpoint-fresh',probe)]
for i,value in enumerate(c['freshRows']):
    expected={'calls':i+1,'setup':oracle[i]['setup'],'result':oracle[i]['expected']};exact(value,expected,'freshJco Node result');calls.append(('inspect',expected))
assert len(calls)==61
for n,(kind,expected)in enumerate(calls,1):
    prefix=directory/'calls'/(str(n).zfill(4)+'-'+kind);exact(load(str(prefix)+'.observed.json'),expected,'saved Jco observation');exact(json.loads(Path(str(prefix)+'.raw.txt').read_text()),expected,'raw Jco result')
for i,row in enumerate(c['wasmtime']):
    expression='identity()'if i==0 else'checkpoint-probe()'if i==1 else'inspect('+str(i-2)+')'
    expected=identity if i==0 else probe if i==1 else{'calls':1,'setup':oracle[i-2]['setup'],'result':oracle[i-2]['expected']}
    exact(row['observed'],expected,'recordedWT Node result');assert row['expression']==expression and row['status']==0 and row['signal']is None
    terminal=load(row['terminalPath']);assert terminal['status']==0 and terminal['signal']is terminal['spawnError']is None and terminal['timedOut']is terminal['outputLimitExceeded']is False
    assert terminal['closed']is terminal['ownedGroupGone']is terminal['terminalExitZeroObserved']is True
    assert terminal['args']==['run','--invoke',expression,r['componentPath']]
    for stream in['stdout','stderr']:x=terminal[stream];checked(x['path'],x['sha256'],x['bytes'])
    assert Path(terminal['stderr']['path']).read_bytes()==b''
    exact(json.loads(json.loads(Path(terminal['stdout']['path']).read_text())),expected,'raw public WT doubleJSON')
    exact(load(directory/'calls'/('wt-'+str(i)+'.observed.json')),expected,'saved WT observation')
assert r['declaredSchedulerLimits']=={'pendingCallbacks':4096,'argumentsEach':1024,'pendingArgumentValues':65536,'callbacksPerCheckpoint':65536}
assert r['schedulerBudget']['override']is r['schedulerBudget']['nativeQueueCountersObserved']is False
assert r['schedulerBudget']['cumulativeWorkloadIterationBounds']==[1,16]
post=load(STOCK/'post-operation-source-audit.json');assert post['passed']is True and post['status']==0 and post['signal']is None and post['originalFailure']is None
post_t=load(post['terminalPath']);assert post_t['terminalExitZeroObserved']is post_t['ownedGroupGone']is True

composition=descriptor(compose_root['result']);complete=descriptor(compose_root['completion'])
assert complete['state']=='COMPOSITION_REPORT_SEALED_EXTERNAL_EXIT_ZERO_REQUIRED'and complete['oldParentRawExit']==1 and complete['requiresIndependentRawOuterExitZero']is True
exact(complete['result'],compose_root['result'],'composition complete result')
assert composition['state']=='COMPOSED_COMMON_BYTE_FOUR_ARM_CORRECTNESS_EVIDENCE'and composition['collectorSourceIndexSha256']==COLLECTOR_SHA and composition['pairPinsSha256']==PAIR_SHA
assert [x['record']['arm']for x in composition['records']]==['native-on','canonical-on','canonical-off','stock-on']
for k in['controlsSubtracted','unaffectedThreeArmsRerun','timingAllowed','runtimeAcceptanceClaim','performanceClaim','queueEmptyProof','rootIsolationProof','cppStateMachineClaim']:assert composition[k]is False
assert composition['commonCases']==8 and composition['controlCases']==6 and composition['original28CounterexamplesPreserved']is True
assert composition['failedParent']['rawOuterExit']==1 and composition['failedParent']['wholeParentGatePassed']is False
failure=load(composition['failedParent']['receiptPath'],composition['failedParent']['receiptSha256']);assert failure['rawOuterExit']==1 and failure['wholeFourArmGatePassed']is False
for i,row in enumerate(composition['records']):
    origin=row['origin'];assert origin['guestSourceFamilyIndexSha256']==SOURCE_SHA
    if i<3:
        assert origin['originalParentRawOuterExit']==1 and origin['wholeOriginalParentGatePassed']is False
        original=failure['completedArmRecords'][row['record']['arm']]['record'];assert original=={'path':origin['recordPath'],'sha256':origin['recordSha256'],'bytes':origin['recordBytes']}
        exact(load(origin['recordPath'],origin['recordSha256'],origin['recordBytes']),row['record'],'unchanged old arm record')
    else:
        assert origin['rawOuterExit']==0 and origin['collectorSourceIndexSha256']==COLLECTOR_SHA
        assert origin['recordPath']==stock_root['result']['path']and origin['recordSha256']==stock_root['result']['sha256']
        exact(row['record'],r,'new stock record exact')
        exact(origin['stockRootReceipt'],{'path':str(STOCK_ROOT),'sha256':STOCK_ROOT_SHA},'stock Root origin')
exact(compose_root['origins'],[x['origin']for x in composition['records']],'Root recorded origins')
for root,script in[(stock_root,'run-stock-only.mjs'),(compose_root,'compose.mjs')]:
    terminal=descriptor(root['terminal']);assert terminal['returncode']==0
    checked(terminal['command'][0],'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0')
    assert terminal['command'][1]==str(COLLECTOR/script)and terminal['command'][2]==COLLECTOR_SHA
    assert terminal['command'][3:5]==[stock_report['reviewedThreeArmAuthority']['path'],stock_report['reviewedThreeArmAuthority']['sha256']]
    if script=='compose.mjs':assert terminal['command'][5:]==[str(STOCK_ROOT),STOCK_ROOT_SHA,str(COMPOSE)]
for row in list(seen.values()):checked(row['path'],row['sha256'],row['bytes'])

stock_proof={'schemaVersion':1,'state':'INDEPENDENT_COMMON_BYTE_STOCK_ONLY_CORRECTNESS_VERIFIED_V1','stockReportSha256':stock_root['result']['sha256'],'stockRootReceiptSha256':STOCK_ROOT_SHA,'guestSourceFamilyIndexSha256':SOURCE_SHA,'collectorSourceIndexSha256':COLLECTOR_SHA,'pairPinsSha256':PAIR_SHA,'rawStockOuterExit':0,'verifiedPassed':True,'timingAllowed':False,'performanceClaim':False,'componentTuple':tuple_of(r)}
composition_proof={'schemaVersion':1,'state':'INDEPENDENT_COMPOSED_COMMON_BYTE_CORRECTNESS_VERIFIED_V1','compositionReportSha256':compose_root['result']['sha256'],'guestSourceFamilyIndexSha256':SOURCE_SHA,'collectorSourceIndexSha256':COLLECTOR_SHA,'pairPinsSha256':PAIR_SHA,'rawCompositionOuterExit':0,'verifiedPassed':True,'timingAllowed':False,'performanceClaim':False,'origins':[{'arm':x['record']['arm'],**x['origin']}for x in composition['records']],'componentTuples':[tuple_of(x['record'])for x in composition['records']]}
summary={'schemaVersion':1,'state':'INDEPENDENT_COMMON_BYTE_STOCK_AND_PROVENANCE_COMPOSITION_ACTUAL_RESULTS_VERIFIED','stockRootReceiptSha256':STOCK_ROOT_SHA,'compositionRootReceiptSha256':COMPOSE_ROOT_SHA,'pathsVerified':len(seen),'stockCompletionRegularFiles':446,'stockOutputLinks':1,'freshStockDurableObservations':77,'preservedOldDurableObservations':231,'composedDurableObservations':308,'wholeNodeOracleResultsExact':True,'cases':{'common':8,'rawControls':6},'stockGraph':{'modules':105,'unchangedPriorModules':99,'originalGuestModules':6,'physical':73,'virtual':15,'processEdges':7,'defaultOptions':{},'schedulerModified':False},'stockPublicComponentImports':[],'stockTypedExports':exports,'stockRawCoreImports':[],'stockRawCoreMatchesEmbeddedCore':True,'oldParentRawExit':1,'wholeOldParentPassed':False,'unaffectedArmsRerun':False,'sourceFamilyIndexSha256':SOURCE_SHA,'supplementalCollectorIndexSha256':COLLECTOR_SHA,'twoActualProofStatesEmittedFromReadCompleteEvidence':True,'timingAllowed':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'limitations':['Narrow HWM-plus-one byte/control domain;28 original counterexamples retained.','Stock has its own Buffer/EE/SD/queueMicrotask scheduler/provider; no provider/scheduler normalization.','Checkpoint probes do not observe native queue depth/emptiness or isolated ownership.','No timing/native/guest/host/tool actions rerun; no performance or complete Node/Streams claim.']}
for name,value in[('stock-result.json',stock_proof),('composition-result.json',composition_proof),('results.json',summary),('verified-paths.json',list(seen.values()))]:
    with(HERE/name).open('x')as out:json.dump(value,out,indent=2);out.write('\n')
print(json.dumps({'state':summary['state'],'paths':len(seen),'durableObservations':308,'timingAllowed':False}))
