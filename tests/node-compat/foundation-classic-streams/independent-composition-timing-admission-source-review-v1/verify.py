#!/usr/bin/env python3
"""Independent source/hash reader; no owner imports or subprocesses."""
import ast
import hashlib
import json
from pathlib import Path
import stat
import sys

HERE=Path(__file__).resolve().parent
FAMILY=HERE.parent
OWNER=FAMILY/'measurement-composition-timing-admission-amendment-v1'
PARENT=FAMILY/'measurement-execution-activated-v2'
PARENT_SHA='1b801439258792c19b9cbc2527d04940c35fb0750f4c26b82a30df6802407612'
COLLECTOR=FAMILY/'measurement-stock-composition-candidate-v1'
COLLECTOR_SHA='257e3800c86c3d2eb2af9cdebc3ee0421f97b947166e853bb70dc95a188033da'
PAIR_SHA='f36268516df72ac5b0d5b5ae8fd808d1ce94d40ca364dc533c522fe399b2681e'
seen={}

def checked(path,digest=None,size=None):
    path=Path(path);before=path.lstat()
    assert stat.S_ISREG(before.st_mode)and not path.is_symlink(),str(path)
    h=hashlib.sha256()
    with path.open('rb')as src:
        for block in iter(lambda:src.read(1024*1024),b''):h.update(block)
    after=path.lstat()
    assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),str(path)
    row={'path':str(path),'sha256':h.hexdigest(),'bytes':before.st_size}
    assert digest is None or row['sha256']==digest,str(path)
    assert size is None or row['bytes']==size,str(path)
    assert str(path)not in seen or seen[str(path)]==row
    seen[str(path)]=row;return row['sha256']

def load(path,digest=None):
    digest=checked(path,digest);raw=Path(path).read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
    return json.loads(raw)

def indexed(root,digest,count=None):
    value=load(root/'index.json',digest)
    assert count is None or len(value['files'])==count
    names=set()
    for row in value['files']:
        assert row['path']not in names and not Path(row['path']).is_absolute()and '..'not in Path(row['path']).parts
        names.add(row['path']);checked(root/row['path'],row['sha256'],row['bytes'])
    return value

def derivation(name):
    d=load(OWNER/(name+'.proof.json'));before_path=Path(d['beforePath'])
    checked(before_path,d['beforeSha256']);checked(OWNER/name,d['afterSha256'])
    before=before_path.read_text();after=(OWNER/name).read_text();value=before
    for row in d['edits']:
        assert value.count(row['old'])==row['count'];value=value.replace(row['old'],row['new'],row['count'])
    assert value==after
    for row in reversed(d['edits']):
        assert value.count(row['new'])==row['count'];value=value.replace(row['new'],row['old'],row['count'])
    assert value==before
    return len(d['edits'])

assert len(sys.argv)==2
OWNER_SHA=sys.argv[1];assert len(OWNER_SHA)==64 and all(x in'0123456789abcdef'for x in OWNER_SHA)
own=indexed(OWNER,OWNER_SHA);indexed(PARENT,PARENT_SHA,35);indexed(COLLECTOR,COLLECTOR_SHA,20)
manifest=load(OWNER/'input-freeze.json');paths=set()
for row in manifest['inputs']:
    p=Path(row['path']);p=p if p.is_absolute()else OWNER/p
    assert str(p)not in paths;paths.add(str(p));checked(p,row['sha256'],row['bytes'])
edits={name:derivation(name)for name in['phase.mjs','measure-body.mjs','audit-body.mjs']}
before=(PARENT/'measure.mjs').read_text();after=(OWNER/'measure-body.mjs').read_text()
worker=lambda text:text[text.index('if(worker){'):text.index('}else{\n const on=')]
pilots=lambda text:text[text.index('  for(const comparison of comparisons)'):text.index(' }catch(error){failure=error;')]
assert worker(before)==worker(after)and pilots(before)==pilots(after)
identity=load(OWNER/'timing-body-identity.json')
assert identity['bothByteIdenticalToParent']is True
assert hashlib.sha256(worker(before).encode()).hexdigest()==identity['workerBodySha256']
assert len(worker(before).encode())==identity['workerBodyBytes']
assert hashlib.sha256(pilots(before).encode()).hexdigest()==identity['pilotAndSamplingLoopSha256']
assert len(pilots(before).encode())==identity['pilotAndSamplingLoopBytes']
assert identity['protocolChanged']is identity['deadlinePolicyChanged']is identity['calibrationOrSampleCountsChanged']is False
for name in['measure.mjs','audit-inputs.mjs']:
    text=(OWNER/name).read_text()
    assert text.index('await check(here,ownSha)')<text.index("await import('./")
    assert PARENT_SHA in text and COLLECTOR_SHA in text
    assert text.index('await check(resolve(')<text.index("await import('./")
phase=(OWNER/'phase.mjs').read_text();admission=(OWNER/'admission.mjs').read_text()
assert 'ROOT_REVIEWED_COMPOSED_COMMON_BYTE_MEASUREMENT_INPUTS_V2'in phase
assert "value.timingAdmissionSourceIndexSha256"in phase and PARENT_SHA in phase and COLLECTOR_SHA in phase and PAIR_SHA in phase
assert "ROOT_EXPLICIT_SINGLE_MEASUREMENT_WINDOW"in phase
for name in['actualCorrectness','freshFull20And14','freshReplay','freshHttpBothHosts']:assert name in phase and name in after
assert "await auditComposedCorrectness(phase,ownSha)"in after
assert "for(const {record} of correctness.records)"in after
assert "collectWorker(join(admissionHere,'measure.mjs')"in after
assert "collectWorker(join(admissionHere,'audit-inputs.mjs')"in after
for guard in["process.version,'v22.14.0'",'process.execArgv,[]',"NODE_COMPAT_COMMON_BYTE_TIMING_APPROVED,'1'",'NODE_OPTIONS','NODE_PATH']:
    assert guard in after
for state in['INDEPENDENT_COMPOSED_COMMON_BYTE_CORRECTNESS_VERIFIED_V1','INDEPENDENT_COMMON_BYTE_STOCK_ONLY_CORRECTNESS_VERIFIED_V1']:
    assert state in admission
for binding in['value.compositionReportSha256,reportSha','value.stockReportSha256,row.origin.recordSha256','value.stockRootReceiptSha256,report.newStockRootReceipt.sha256','value.componentTuples,report.records.map','value.componentTuple,componentTuple(row.record)','value.origins,report.records.map','value.rawCompositionOuterExit,0','value.rawStockOuterExit,0']:
    assert binding in admission
assert 'Proof result must be indexed exactly once'in admission
assert 'await indexed(dirname(indexRow.path),indexRow.sha256)'in admission
assert 'stockRoot.result.sha256,report.records[3].origin.recordSha256'in admission
assert "for(const name of ['terminal','completion','stdout','stderr','independentProofIndex','independentProofResult','stockIndependentProofIndex','stockIndependentProofResult'])"in admission
assert 'rawOuterExit:1' in (COLLECTOR/'compose.mjs').read_text()
future=load(OWNER/'future-measurement-phase.json')
assert future['state']=='UNCONFIGURED_COMPOSED_COMMON_BYTE_TIMING_PHASE_V2'
assert future['timingAllowed']is False and future['timingAdmissionSourceIndexSha256']is None
assert future['sourceFamilyIndexSha256']==PARENT_SHA and future['collectorSourceIndexSha256']==COLLECTOR_SHA
ast_count=0
for p in OWNER.glob('*.py'):ast.parse(p.read_text());ast_count+=1
for row in list(seen.values()):checked(row['path'],row['sha256'],row['bytes'])
result={'schemaVersion':1,'state':'INDEPENDENT_COMPOSITION_TIMING_ADMISSION_SOURCE_REVIEW_PASSED_NOT_TIMING_AUTHORIZATION','ownerIndexSha256':OWNER_SHA,'ownerFiles':len(own['files']),'ownerInputRows':len(paths),'pathsIndependentlyVerified':len(seen),'parentSourceIndexSha256':PARENT_SHA,'collectorSourceIndexSha256':COLLECTOR_SHA,'pairSha256':PAIR_SHA,'reversibleSourceAfterimages':edits,'workerBodyByteIdenticalToParent':True,'pilotCalibrationAndSampleLoopsByteIdenticalToParent':True,'sampleCountsDeadlinesProtocolProviderWorkloadOracleUnchanged':True,'wrappersAuthenticateBeforeDynamicBodyImport':True,'separateStockAndCompositionActualProofSchemasRequired':True,'proofIndicesRehashAllMembersAndBindResultExactlyOnce':True,'proofReportOriginsFullComponentTuplesSourcePairAndRawZeroBound':True,'oldThreeRecordsAndFailedParentRawOnePreserved':True,'futurePhaseUnconfigured':True,'actualProofsOrPhaseIssuedByReader':False,'timingAuthorized':False,'runtimeAcceptanceOrPerformanceClaim':False,'concreteSourceBlockers':[],'independentASTParses':ast_count,'readerActions':'Regular-file hashes, JSON/text inspection, exact forward/reverse reconstruction, body identity and AST parsing only. No owner imports/helpers/tests/Node/preflight/native verifier/bundle/guest/host/timing actions.'}
with(HERE/'verified-paths.json').open('x')as out:json.dump(list(seen.values()),out,indent=2);out.write('\n')
with(HERE/'results.json').open('x')as out:json.dump(result,out,indent=2);out.write('\n')
print(json.dumps({'state':result['state'],'paths':len(seen),'ownerFiles':len(own['files'])}))
