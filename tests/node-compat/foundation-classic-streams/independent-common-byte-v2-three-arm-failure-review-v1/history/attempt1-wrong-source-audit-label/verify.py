#!/usr/bin/env python3
"""Independent stored-data reader. No owner code imports or subprocesses."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from binary_reader import uint, string, sections, core_imports

HERE = Path(__file__).resolve().parent
FAMILY = HERE.parent
SOURCE = FAMILY/'measurement-execution-activated-v2'
OUTPUT = Path('/tmp/starling-node-compat/production-common-byte-correctness-v2')
ROOT = FAMILY/'production-adoption-v1/common-byte-v2-stock-graph-failure-root-results.json'
ROOT_SHA = '9037865a47939c8f2ff30976f5346ce5848113ea55c87c7c5753aed26e6a099f'
SOURCE_SHA = '1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612'
PAIR_SHA = 'f36268516df72ac5b0d5b5ae8fd808d1ce94d40ca364dc533c522fe399b2681e'
REVIEW_SHA = '2bfa334981d1fc63ae05280fcb0c2afb9d8ea22e5e1451ae796d7c756479950e'
seen = {}

def checked(path, digest=None, size=None):
    path = Path(path);before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and not path.is_symlink(), str(path)
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    after=path.lstat()
    assert (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
    row={'path':str(path),'sha256':h.hexdigest(),'bytes':before.st_size}
    assert digest is None or row['sha256']==digest,str(path)
    assert size is None or row['bytes']==size,str(path)
    assert str(path) not in seen or seen[str(path)]==row,str(path)
    seen[str(path)]=row;return row['sha256']

def load(path,digest=None):
    captured=checked(path,digest);raw=Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==captured,str(path)
    return json.loads(raw)

def exact(actual,expected,label):
    assert json.dumps(actual,sort_keys=True,separators=(',',':'),ensure_ascii=True)==json.dumps(expected,sort_keys=True,separators=(',',':'),ensure_ascii=True),label

def indexed(root,digest,count):
    data=load(root/'index.json',digest);assert len(data['files'])==count
    for row in data['files']:
        assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
        checked(root/row['path'],row['sha256'],row['bytes'])
    return data

root=load(ROOT,ROOT_SHA)
assert root['rawOuterExit']==1 and root['wholeFourArmGatePassed'] is False
assert root['timingAllowed'] is root['runtimeAcceptanceClaim'] is root['performanceClaim'] is False
assert root['sourceFamilyIndexSha256']==SOURCE_SHA and len(root['evidence'])==1328
for row in root['evidence']:checked(row['path'],row['sha256'],row['bytes'])
indexed(SOURCE,SOURCE_SHA,35)
source_receipt=load(SOURCE/'source-receipt.json')
assert source_receipt['consumedInputs']==7709 and source_receipt['toolTrees']==2 and source_receipt['toolLinks']==22
assert source_receipt['pairPinsSha256']==PAIR_SHA and source_receipt['rootReviewSha256']==REVIEW_SHA
assert source_receipt['metadataRewritten'] is False
seal=load(SOURCE/'input-freeze.json');assert len(seal['inputs'])==7709
for row in seal['inputs']:
    p=Path(row['path']);checked(p if p.is_absolute() else SOURCE/p,row['sha256'],row['bytes'])
assert len(seal['toolTrees'])==2 and len(seal['toolLinks'])==22
for tree in seal['toolTrees']:
    members=[];base=Path(tree['path'])
    for directory,dirs,files in os.walk(base,followlinks=False):
        for n in sorted(dirs+files):
            p=Path(directory)/n
            kind='symlink' if p.is_symlink() else 'directory' if p.is_dir() else 'file' if p.is_file() else None
            assert kind;members.append({'path':str(p.relative_to(base)),'kind':kind})
        dirs[:]=[n for n in dirs if not(Path(directory)/n).is_symlink()]
    exact(sorted(members,key=lambda row:row['path']),tree['entries'],'tool tree membership')
for link in seal['toolLinks']:
    assert os.readlink(link['path'])==link['linkText']
    assert str(Path(link['path']).resolve(strict=True))==link['resolvedTarget']
pair=load(SOURCE/'reviewed-pair.json',PAIR_SHA)
review=load(SOURCE/'root-pair-review.json',REVIEW_SHA)
activation=load(SOURCE/'activation.json')
assert activation['pairSha256']==PAIR_SHA and activation['rootReviewSha256']==REVIEW_SHA
assert activation['timingAllowed'] is False
freeze_root=Path('/tmp/starling-node-compat/classic-benchmark-trace-v3-artifacts/native-freeze')
frozen=[]
for label in ['benchmark-classic-on','benchmark-classic-off']:
    pin=pair['variants'][label]
    engine=freeze_root/(label+'.engine.wasm');checked(engine,pin['engineSha256'],pin['engineBytes'])
    metadata=load(Path(str(engine)+'.build.json'),pin['metadataSha256'])
    receipt=load(freeze_root/(label+'-freeze-receipt.json'),pin['freezeReceiptSha256'])
    assert len(receipt['copies'])==525
    assert metadata['diagnosticOnly'] is True and metadata['classicStreamsEnabled']==(label=='benchmark-classic-on')
    assert metadata['entropyPolicy']=='off' and metadata['gcStress'] is False and metadata['oomTesting'] is False and metadata['debuggerEnabled'] is False
    assert len(metadata['sourceManifest'])==342 and len(metadata['componentizeSourceManifest'])==3
    for row in receipt['copies']:
        checked(row['path'],row['sha256'],row['bytes'])
        if row['original'] is not None:checked(row['original'],row['sha256'],row['bytes'])
    frozen.append({'label':label,'engineSha256':pin['engineSha256'],'metadataSha256':pin['metadataSha256'],'freezeReceiptSha256':pin['freezeReceiptSha256'],'copies':525,'originals':sum(row['original'] is not None for row in receipt['copies'])})

common=load(SOURCE/'node-common-oracle.json');controls=load(SOURCE/'node-control-oracle.json')
assert len(common['cases'])==8 and len(controls['cases'])==6
oracle=common['cases']+controls['cases']
assert [x['iterations'] for x in oracle]==[1,16]*7
assert all(row['proposedExact'] is True for row in common['cases'])
expected_identity={'defaultGraph':True,'promisesGraph':True,'eventEmitterPrototype':True,'selectedTickType':'function','decoderA':'A','bufferView':True,'bufferSameAsBefore':True,'globalSameAsProvider':True,'beforeBufferType':'function','globalChangedDuringProvider':False}
def probe(value):
    assert value['callbacks']==1 and sorted(value['trace'])==['microtask','selected-tick']
    assert value['queueDepthObserved'] is value['terminalQueueEmptyObserved'] is False

arm_summaries=[]
for arm in ['native-on','canonical-on','canonical-off']:
    directory=OUTPUT/arm;origin=root['completedArmRecords'][arm]
    record=load(directory/'arm-results.partial.json',origin['record']['sha256'])
    assert record['arm']==arm and origin['wholeParentGatePassed'] is False
    assert origin['sourceFamilyIndexSha256']==SOURCE_SHA
    component=Path(record['componentPath']);checked(component,origin['componentSha256'],origin['componentBytes'])
    assert record['componentSha256']==origin['componentSha256']
    before_record=load(directory/'component-record.before-observations.json')
    for key,value in before_record.items():exact(record[key],value,'component pre-observation record '+key)
    graph=load(directory/'bundle-graph.json');exact(graph,record['graph'],'bundle graph')
    checked(directory/'application.bundle.mjs',record['bundleSha256'],graph['bundleBytes'])
    assert graph['stockOptions'] is None and graph['stockSchedulerOverride'] is False
    assert graph['virtualSources']==graph['resolutions']==[]
    assert len(graph['physicalSources'])==(8 if arm.startswith('canonical') else 6)
    assert len(graph['modules'])==len(graph['physicalSources'])
    for row in graph['physicalSources']:checked(row['path'],row['sha256'],row['bytes'])
    assert sorted(row['path'] for row in graph['physicalSources'])==sorted(graph['modules'])
    expected_imports=['node:buffer','node:events','node:string_decoder','starling:test-classic-benchmark']
    if arm=='native-on':expected_imports+=['node:stream','node:stream/promises']
    assert sorted(graph['imports'])==sorted(expected_imports)
    for row in record['transpiledFiles']:checked(directory/row['name'],row['sha256'],row['bytes'])
    assert record['coreFiles']==['common_byte.core.wasm']
    glue=(directory/'common_byte.js').read_text();assert 'common_byte.core.wasm' in glue and 'export function instantiate' in glue
    wit=(directory/'emitted.wit').read_text();assert not re.search(r'\bimport\b',wit)
    expected_wit=['export setup: func(index: u32) -> s32;','export inspect: func(index: u32) -> string;','export batch: func(index: u32, iterations: u32) -> string;','export identity: func() -> string;','export checkpoint-probe: func() -> string;']
    for declaration in expected_wit:assert declaration in wit
    assert len(re.findall(r'\bexport\s+',wit))==5
    exports=[];embedded=[];types=[]
    for kind,payload in sections(component.read_bytes(),bytes.fromhex('0061736d0d000100')):
        if kind==10:
            count,pos=uint(payload,0);assert count==0 and pos==len(payload)
        elif kind==11:
            count,pos=uint(payload,0)
            for _ in range(count):
                assert payload[pos]==0;n,pos=string(payload,pos+1);sort=payload[pos];pos+=1;index,pos=uint(payload,pos);assert payload[pos]==0;pos+=1;exports.append((n,sort))
            assert pos==len(payload)
        elif kind==1:embedded.append(payload)
        elif kind==7:types.append(payload.hex())
    assert sorted(exports)==sorted([(n,1)for n in ['setup','inspect','batch','identity','checkpoint-probe']])
    raw_core=(directory/'common_byte.core.wasm').read_bytes()
    standard=lambda value:[(kind,hashlib.sha256(part).hexdigest())for kind,part in sections(value,bytes.fromhex('0061736d01000000'))if kind!=0]
    assert sum(standard(value)==standard(raw_core)for value in embedded)==1
    decoded_core_imports=core_imports(raw_core)
    assert record['emittedImports']==record['interfaceAudit']['emittedImports']==[]
    assert record['interfaceAudit']['componentSha256']==record['componentSha256']
    assert record['correctnessPassed'] is record['identityPassed'] is record['checkpointProbePassed'] is True
    exact(record['identity'],expected_identity,'identity');probe(record['checkpointProbe'])
    assert record['declaredSchedulerLimits']=={'pendingCallbacks':4096,'argumentsEach':1024,'pendingArgumentValues':65536,'callbacksPerCheckpoint':65536}
    assert record['schedulerBudget']['override'] is record['schedulerBudget']['nativeQueueCountersObserved'] is False
    assert record['schedulerBudget']['cumulativeWorkloadIterationBounds']==[1,16]
    c=record['correctness'];assert c['retainedRotations']==3 and [len(x)for x in c['rounds']]==[14]*3 and len(c['freshRows'])==14 and len(c['wasmtime'])==16
    expected_calls=[('identity',expected_identity),('checkpoint-retained',record['checkpointProbe'])]
    for rotation,rows in enumerate(c['rounds']):
        for case_index,value in enumerate(rows):
            wanted={'calls':rotation*14+case_index+1,'setup':oracle[case_index]['setup'],'result':oracle[case_index]['expected']}
            exact(value,wanted,'retained whole Node result');expected_calls.append(('inspect',wanted))
    expected_calls += [('checkpoint-after',record['checkpointProbe']),('identity',expected_identity),('checkpoint-fresh',record['checkpointProbe'])]
    for case_index,value in enumerate(c['freshRows']):
        wanted={'calls':case_index+1,'setup':oracle[case_index]['setup'],'result':oracle[case_index]['expected']}
        exact(value,wanted,'fresh Jco whole Node result');expected_calls.append(('inspect',wanted))
    assert len(expected_calls)==61
    for call_index,(kind,wanted) in enumerate(expected_calls,1):
        prefix=directory/'calls'/(str(call_index).zfill(4)+'-'+kind)
        exact(json.loads(Path(str(prefix)+'.raw.txt').read_text()),wanted,'Jco raw full JSON')
        exact(load(Path(str(prefix)+'.observed.json')),wanted,'Jco persisted parsed JSON')
    for index,row in enumerate(c['wasmtime']):
        expression='identity()' if index==0 else 'checkpoint-probe()' if index==1 else 'inspect('+str(index-2)+')'
        wanted=expected_identity if index==0 else record['checkpointProbe'] if index==1 else {'calls':1,'setup':oracle[index-2]['setup'],'result':oracle[index-2]['expected']}
        assert row['expression']==expression and row['status']==0 and row['signal'] is None
        terminal=load(row['terminalPath']);assert terminal['status']==0 and terminal['signal'] is terminal['spawnError'] is None
        assert terminal['timedOut'] is terminal['outputLimitExceeded'] is False
        assert terminal['closed'] is terminal['ownedGroupGone'] is terminal['terminalExitZeroObserved'] is True
        assert terminal['args']==['run','--invoke',expression,str(component)]
        for stream in ['stdout','stderr']:
            capture=terminal[stream];checked(capture['path'],capture['sha256'],capture['bytes'])
        assert Path(terminal['stderr']['path']).read_bytes()==b''
        actual=json.loads(json.loads(Path(terminal['stdout']['path']).read_text()))
        exact(actual,wanted,'fresh Wasmtime public CLI double JSON');exact(row['observed'],wanted,'WT arm record JSON')
        exact(load(directory/'calls'/('wt-'+str(index)+'.observed.json')),wanted,'WT saved JSON')
    assert not(directory/'counterexample.json').exists()
    arm_summaries.append({'arm':arm,'originSourceIndexSha256':SOURCE_SHA,'originParentRawExit':1,'recordPath':origin['record']['path'],'recordSha256':origin['record']['sha256'],'componentSha256':record['componentSha256'],'componentBytes':record['componentBytes'],'bundleSha256':record['bundleSha256'],'engineSha256':record['engineSha256'],'engineMetadataSha256':record['engineMetadataSha256'],'retainedRotations':3,'retainedCases':42,'freshJcoCases':14,'freshWasmtimeCases':14,'jcoIdentityAndProbeCalls':5,'freshWasmtimeIdentityAndProbeCalls':2,'totalDurableReturnedObservations':77,'allWholeNodeOracleResultsExact':True,'publicComponentImports':[],'publicExports':exports,'embeddedCoreCount':len(embedded),'rawCoreStandardSectionsMatchOneEmbeddedCore':True,'rawCoreImports':decoded_core_imports,'componentTypes':types})
assert arm_summaries[1]['bundleSha256']==arm_summaries[2]['bundleSha256']

failure=load(OUTPUT/'failure-before-source-audit.json')
assert failure['completedArms']==['native-on','canonical-on','canonical-off']
assert failure['error']=={'name':'TypeError','message':'The "path" argument must be of type string. Received undefined'}
assert list((OUTPUT/'stock-on').iterdir())==[]
assert not (OUTPUT/'correctness-results.json').exists() and not list(OUTPUT.glob('*completion*'))
stock=load(SOURCE/'stock-source-graph.json');assert 'provider' not in stock
assert len(stock['sourceBeforeAfter'])==3
assert {Path(row['path']).name for row in stock['sourceBeforeAfter']}=={'entry.mjs','workload.mjs','stock-provider.mjs'}
for row in stock['sourceBeforeAfter']:checked(row['path'],row['sha256'],row['bytes'])
bundle_source=(SOURCE/'bundle-matched.mjs').read_text()
assert 'dirname(previous.provider)' in bundle_source
driver=(SOURCE/'prepare-correctness.mjs').read_text()
assert driver.index('const bundle=await bundleMatched(')<driver.index("await writeFile(join(directory,'application.bundle.mjs')")<driver.index('selected.componentize(')
assert driver.index("arm-results.partial.json")<driver.index("'correctness-results.json'")
post=load(OUTPUT/'post-operation-source-audit.json');assert post['status']==0 and post['signal'] is None and post['passed'] is True
post_terminal=load(post['terminalPath']);assert post_terminal['terminalExitZeroObserved'] is post_terminal['ownedGroupGone'] is True
assert post_terminal['status']==0 and post_terminal['signal'] is None
for stream in ['stdout','stderr']:
    row=post_terminal[stream];checked(row['path'],row['sha256'],row['bytes'])
assert json.loads(Path(post_terminal['stdout']['path']).read_text())['state']=='EXECUTION_INPUTS_UNCHANGED'
link=root['rootNodeModulesLink'];assert os.readlink(link['path'])==link['linkText'] and str(Path(link['path']).resolve())==link['resolvedTarget']

for row in list(seen.values()):checked(row['path'],row['sha256'],row['bytes'])
result={'schemaVersion':1,'state':'INDEPENDENT_COMMON_BYTE_V2_THREE_COMPLETED_ARMS_AND_PARENT_FAILURE_VERIFIED','rootReceiptSha256':ROOT_SHA,'rootParentRawExit':1,'sourceFamilyIndexSha256':SOURCE_SHA,'sourceFiles':35,'sourceClosureRows':7709,'rootEvidenceFiles':1328,'verifiedPaths':len(seen),'toolTrees':2,'toolLinks':22,'reviewedPairSha256':PAIR_SHA,'rootPairReviewSha256':REVIEW_SHA,'nativeFrozenPairs':frozen,'arms':arm_summaries,'durableReturnedObservations':231,'nodeOracleCases':{'common':8,'controls':6},'stockFailure':{'phase':'host stock graph check before stock artifact persistence/componentization','missingField':'previous.provider','threeOriginalGuestSourceRowsAuthenticated':True,'stockOutputDirectoryEmpty':True,'stockComponentOrGuestEvidence':False,'unretainedInMemoryBundleNotEvidence':True},'postFailureSourceAuditExitCode':0,'globalCompletionOrGateReportExists':False,'wholeParentFourArmGatePassed':False,'timingAllowed':False,'runtimeAcceptanceClaim':False,'performanceClaim':False,'provenancePreservingComposition':{'unaffectedArmsEligibleAsEvidence':True,'invariantRequiringUnaffectedThreeArmsRerunFound':False,'conditions':['Authenticate this failed parent receipt and each original arm record/component path, SHA and source1b801; preserve parent raw exit1 and original bytes.','New stock-only source must declare its distinct amendment/index/output origin; prove guest/provider/workload/oracle semantics and actual native tuples unchanged.','Reverify current source/tool/native/authority closure and whole raw results for all reused arms before composing a NEW report.','Run fresh stock correctness with full14+identity/probe/retained/fresh gates; retain its raw/terminal/closure evidence separately.','A composed result must name per-arm origins and cannot relabel the old parent as successful or infer timing/reuse/root isolation.']},'readerActions':'Only hashes, stored JSON/text/raw result decoding, static public Wasm/component/core parsing and filesystem membership/link reads. No owner helper/test/action imports, artifact verifier, Ninja, bundle, compiler, guest, hosts or timing reruns.','limitations':['Original28counterexamples and narrowHWM+1 common domain remain distinct.','Checkpoint probes do not observe queue depth/emptiness or isolated native roots; configured65536 callbacks/checkpoint was not raised.','Recorded operational packaging durations do not establish a performance comparison.']}
with(HERE/'verified-paths.json').open('x')as out:json.dump(list(seen.values()),out,indent=2);out.write('\n')
with(HERE/'results.json').open('x')as out:json.dump(result,out,indent=2);out.write('\n')
print(json.dumps({'state':result['state'],'verifiedPaths':len(seen),'returnedObservations':231,'wholeParentGatePassed':False}))
