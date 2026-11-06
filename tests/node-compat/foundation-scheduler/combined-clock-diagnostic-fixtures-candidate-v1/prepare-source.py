"""Compact Source cataloguing only; writes this family, invokes no owner API."""
from pathlib import Path
import hashlib,json
OWN=Path(__file__).resolve().parent;S=OWN.parent;DIAG=S/'combined-clock-diagnostics-candidate-v1';LIFE=S/'combined-clock-lifecycle-candidate-v2'
def desc(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert desc(DIAG/'index.json')['sha256']=='7aed33ec02b9024fb96ded8e77924a27ce7d54bf36102a5fd561a3e88f731e52'
files={}
def add(p):r=desc(p);files[r['path']]=r;return r
def family(p):
 ix=add(p/'index.json');v=json.loads((p/'index.json').read_bytes());names={'index.json'}
 for r in v['files']:
  n=r['path'];assert not n.startswith('/')and all(x not in('','.','..')for x in n.split('/'))and n not in names;names.add(n);d=add(p/n);assert d['sha256']==r['sha256']and d['bytes']==r['bytes']
 assert{q.relative_to(p).as_posix()for q in p.rglob('*')if q.is_file()}==names and not any(q.is_symlink()for q in p.rglob('*'));return ix
families=[family(DIAG),family(LIFE)]
syntax=S/'combined-clock-diagnostics-sdk-builtin-retry-v1';syntax_refs=dict(index=add(syntax/'index.json'),result=add(syntax/'results.json'))
# Actual parent frozen source origins for offset/performance; no native execution.
inventory=json.loads((DIAG/'proposed-source-inventory.json').read_bytes());origins={r['path']:r for r in inventory['native']}
extra={}
for name in ['runtime/js.cpp','builtins/web/performance.cpp','include/extension-api.h','include/host_api.h','CMakeLists.txt']:
 if name in origins:
  r=origins[name];d=r.get('origin')or r.get('source')or r.get('original')or r.get('after')
  if isinstance(d,dict)and'path'in d:extra[name]=add(d['path']);assert extra[name]==d
refs=dict(schemaVersion=1,diagnosticSourceIndex=families[0],lifecycleFixtureSourceIndex=families[1],syntaxOnlySummary=syntax_refs,actualNativeSourceOrigins=extra,node=dict(path='/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node',sha256='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0',bytes=108619024),scope='Two complete Source families plus SDK syntax summary descriptors and finite actual native origins; no recursive SDK/proof closure, no native/tool runtime validation')
files[refs['node']['path']]=refs['node'];save('references.json',refs);save('input-hashes.json',dict(schemaVersion=1,files=sorted(files.values(),key=lambda r:r['path']),families=families,scope=refs['scope']))
caps=['wasi:clocks/wall-clock@0.2.10','wasi:clocks/monotonic-clock@0.2.10','wasi:io/poll@0.2.10']
rows=[]
for name,wit,exports,builtin in [('resource-observed','resource.wit',[('inspect',[]),('run',['u32']),('validate',[]),('snapshot',[])],['node:buffer','starling:test-clock-lifecycle']),('clock-observed','scalar.wit',[('run',[]),('snapshot',[])],['starling:test-clock-lifecycle']),('survivor-observed','scalar.wit',[('run',[]),('snapshot',[])],['starling:test-clock-lifecycle'])]:
 rows.append(dict(id=name,source=desc(OWN/'fixtures'/f'{name}.mjs'),wit=desc(OWN/'fixtures'/wit),worldName='validation',exports=[dict(name=n,arguments=a,result='string')for n,a in exports],expectedNativeResidualImports=builtin,selectedInterfaces=caps,disableFeatures=['stdio','random','http','fetch-event'],sameComponentObserverRequired=True,initDiagnosticSnapshotCalled=False,ordinaryCallsRequireNewRootAuthority=True))
save('fixture-catalogue.json',dict(schemaVersion=1,state='UNCOMPILED_UNEXECUTED_PRIVATE_DIAGNOSTIC_FIXTURE_SOURCE_V1',diagnosticSourceIndex=refs['diagnosticSourceIndex'],distinctFromHashHmac357=True,current355HasPrivateObserver=False,fixtures=rows,allInvalidQueueFixture=None,nativeOffsetFixture=None))
save('source-plan.json',dict(schemaVersion=1,state='UNEXECUTED_SOURCE_PLAN_NOT_COMPONENT_OR_NATIVE_EVIDENCE_V1',nativeModule='starling:test-clock-lifecycle',actualPrivateExports=['snapshot'],requiredDiagnosticFlags=['NODE_COMPAT_LIFECYCLE_DIAGNOSTICS','ENABLE_BUILTIN_DIAGNOSTICS_CLOCK_LIFECYCLE'],flagsDefaultOff=True,diagnosticNativeInventory=dict(parent355=355,retained351=351,afterimages4=4,newPaths2=2,proposed357=357,externalEmbedding=3),hashHmac357NotInterchangeable=True,currentNative355NotInterchangeable=True,publicWholeManifests=11,privateSpecifierBundlerAdmission=None,newMetadataProducer=None,newNativeAdmission=None,newNativeBuild=None,newDiagnosticNativeSourcePeer=None,newActualNativeArtifact=None,newActualComponentArtifact=None,actualFunctionIndexMap=None,sourceReview=None,rootAuthority=None,runtimeResults=None,selectedInterfaces=caps,caseNativeExpectedCounts=[dict(construct=c,acquire=a,run=r,cancel=x)for c,a,r,x in [(2,2,2,0),(2,2,1,1),(2,4,4,0),(3,3,2,1),(2,2,2,0),(2,2,2,0),(33,33,1,32)]],wholeSevenExpected=dict(timerConstruct=46,timerAcquire=48,queueDetachRun=14,queueDetachCancel=34),expectationsAreSourceCoupledNotObserved=True,resourceRetainedSchedule=dict(rotations=3,initialExports=['inspect'],perCaseExports=['run(caseId)','snapshot()'],caseOrder=[0,1,2,3,4,5,6],nativeLeaseRowsPerRotation=48,maxNativeLeaseRows=144),resourceFreshWrapperSchedule=dict(outerExport='validate()',nextExport='snapshot()',nativeLeaseRows=48),fixedNativeLedgerLimit=512,stickyOverflowOrIncompleteMustFail=True,rawReturnsAndTerminalMustBeDurableBeforeValidation=True,withinExportCannotObserveItsOwnPostCall=True,allInvalidNativeSetupAvailable=False,nativeOffsetExportAvailable=False,hostStoreDeathObservable=False,cachedImmediateDropImplemented=False,fatalFinalNativeSnapshotAvailable=False,fullLifecycleGateAccepted=False,publicProfilePromotion=False))
save('future-gates.json',dict(schemaVersion=1,state='UNISSUED_SOURCE_AND_ACTION_GATES_V1',sourcePeer=None,rootAuthority=None,diagnosticNativeIntegration=None,diagnosticNativeBuild=None,actualNativeArtifact=None,privateBundlePolicy=None,actualComponent=None,actualMappedArtifact=None,runtimeAuthority=None,actualRuntimeResults=None,allInvalidSetupAndSettlementApi=None,nativeClockOffsetReadOnlyApi=None,hostStoreDisposalObservation=None,adoptionAuthority=None))
print(json.dumps(dict(state='COMPACT_SOURCE_REFERENCES_PREPARED',inputFiles=len(files),fullSourceFamilies=len(families),fixtureCount=len(rows),allActionsFalse=True)))
