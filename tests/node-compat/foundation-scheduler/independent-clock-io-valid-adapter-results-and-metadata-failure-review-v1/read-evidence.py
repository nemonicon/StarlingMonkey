"""Read/hash/decode retained DATA only; no owner API/tool/process invocation."""
from pathlib import Path
import hashlib,json,stat
HERE=Path(__file__).resolve().parent;S=HERE.parent
SOURCE=S/'clock-io-valid-adapter-candidate-v1'
OUT=Path('/private/tmp/starling-node-compat/clock-io-valid-adapter-v1')
EXT=Path('/private/tmp/starling-node-compat/clock-io-valid-adapter-v1-external-root')
checks=0;captured={}
def check(v):
    global checks
    assert v;checks+=1
def row(p):
    p=Path(p);a=p.stat();check(p.is_file()and not p.is_symlink());h=hashlib.sha256()
    with p.open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    z=p.stat();key=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns,str(p.resolve()))
    check(key(a)==key(z));r=dict(path=str(p),sha256=h.hexdigest(),bytes=z.st_size)
    if str(p)in captured:check(captured[str(p)]==r)
    captured[str(p)]=r;return r
def verify(r):check(row(r['path'])==r)
def read(r):verify(r);return json.loads(Path(r['path']).read_bytes())
def load(p):return read(row(p))
def family(ix):
    value=read(ix);root=Path(ix['path']).parent;names={'index.json'}
    for r in value['files']:names.add(r['path']);verify(dict(path=str(root/r['path']),sha256=r['sha256'],bytes=r['bytes']))
    check({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names)
    check(not any(p.is_symlink()for p in root.rglob('*')))
def clean(t,code):
    check(t['rawExitCode']==code and t['timeout']is t['forcedCleanup']is False)
    check(t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True)
    for key in ['signals','errors','interruptedSignals','remainingObservedPids']:check(t[key]==[])
    check(t['finalGroups']and all(x['alive']is False for x in t['finalGroups']))
    for key in ['stdout','stderr']:verify(t[key])

root_row=row(S/'clock-io-valid-adapter-v1-root-results.json');check(root_row['sha256']=='e8a9d295cb3b6a98f6f01ee4c4d65a5a5880e72d12a5a594afbbb0697472810d')
report=read(root_row);check(row('/private/tmp/starling-node-compat/clock-io-valid-adapter-v1-root-observer/root-observation.json')['sha256']==root_row['sha256'])
check(report['state']=='ROOT_OBSERVED_CLOCK_IO_VALID_ADAPTER_FAILED_AT_METADATA_V1')
check(report['rootToolObservation']['sessionId']==16422 and report['rootToolObservation']['exitCode']==1)
for key in ['sourceIndex','rootAuthority','rootConfig','invocation','rootStdout','rootStderr','parentObservation','workerResult','workerTerminal']:verify(report[key])
family(report['sourceIndex']);family(report['sourcePeer']['index']);read(report['sourcePeer']['result'])
refs=load(SOURCE/'references.json');authority=read(report['rootAuthority']);config=read(report['rootConfig'])
check(config['rootAuthority']==report['rootAuthority']and config['sourceIndex']==report['sourceIndex'])
check(authority['sourceIndex']==report['sourceIndex']and authority['sourceIndependentReview']==report['sourcePeer'])
check(all(authority[k]is True for k in ['normalizationAllowed','singlePrunerCallAllowed','coreValidationAllowed','metadataWitDecodeAllowed']))
for key in ['adapterPromotionAllowed','defaultPackagerReplacementAllowed','componentAllowed','engineExecutionAllowed','guestAllowed','keyOrCryptoAllowed','nativeBuildAllowed','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']:check(authority[key]is False)
copies=report['retainedEvidenceCopies'];check(len(copies)==35)
for pair in copies:
    verify(pair['original']);verify(pair['retained']);check((pair['original']['sha256'],pair['original']['bytes'])==(pair['retained']['sha256'],pair['retained']['bytes']))
check({p.as_posix()for p in (S/'clock-io-valid-adapter-v1-root-evidence').rglob('*')if p.is_file()}=={r['retained']['path']for r in copies})
phase=read(report['workerResult']);parent=read(report['parentObservation']);worker=read(report['workerTerminal']);clean(worker,1)
check(phase['state']=='CLOCK_IO_VALID_ADAPTER_FAILED_UNACCEPTED_V1'and phase['finalProtectionError']is None and phase['completeOutputClaim']is False)
check(parent['state']=='CLOCK_IO_VALID_ADAPTER_PARENT_FAILED_UNACCEPTED_V1'and parent['workerResult']is None)
check(phase['sourceIndex']==report['sourceIndex']and phase['rootAuthority']==report['rootAuthority'])
check(report['finalProtectionError']is None and report['sourceOrOldArtifactsModified']is False)
root_lines=[json.loads(x)for x in Path(report['rootStdout']['path']).read_text().splitlines()]
worker_lines=[json.loads(x)for x in Path(worker['stdout']['path']).read_text().splitlines()]
check(len(root_lines)==2 and root_lines[0]['timeoutSeconds']==600 and root_lines[1]['completeUnreviewed']is False)
check(root_lines[1]['observation']==report['parentObservation'])
check(len(worker_lines)==4 and [x['timeoutSeconds']for x in worker_lines[:3]]==[300,60,60]and worker_lines[-1]==report['workerResult'])
terminals={};started={}
for label,code in [('pruner',0),('core-validate',0),('metadata-wit',1)]:
    t=read(report['commandTerminals'][label]);clean(t,code);terminals[label]=t;started[label]=load(EXT/label/'started.json')
    check(t['authority']==report['rootAuthority']and started[label]['authority']==report['rootAuthority'])
    check(started[label]['pid']==t['pid']and worker_lines[['pruner','core-validate','metadata-wit'].index(label)]['pid']==t['pid'])
    observed=[load(p)['process']for p in sorted((EXT/label).glob('owned-*.json'))]
    check(observed==t['observedProcesses'])
check(started['pruner']['argv']==[refs['hostPruner']['path'],'prune-clock-adapter-io','--input',str(OUT/'normalized-adapter.wasm'),'--output',str(OUT/'pruned-adapter.wasm')])
check(started['core-validate']['argv']==[refs['node']['path'],str(SOURCE/'validate-core.mjs'),str(OUT/'normalized-adapter.wasm'),str(OUT/'pruned-adapter.wasm'),str(OUT/'core-validation.json')])
check(started['metadata-wit']['argv']==[refs['node']['path'],refs['jcoEntry']['path'],'wit',str(OUT/'embedded-wit-component.wasm')])
check([started[x]['timeoutSeconds']for x in ['pruner','core-validate','metadata-wit']]==[300,60,60])
check(terminals['pruner']['stdout']['bytes']==terminals['pruner']['stderr']['bytes']==terminals['core-validate']['stderr']['bytes']==0)
check(terminals['metadata-wit']['stdout']['bytes']==19 and terminals['metadata-wit']['stderr']['bytes']==1602)
stderr=Path(terminals['metadata-wit']['stderr']['path']).read_text()
check('Unexpected wit package'in stderr and 'crates/wasm-tools-component/src/lib.rs:64:46'in stderr and 'wasm `unreachable` instruction executed'in stderr)
for r in report['actualArtifacts']:verify(r)
by_name={Path(r['path']).name:r for r in report['actualArtifacts']}
check(phase['availableActualFiles']==report['actualArtifacts']and parent['availableActualFiles']==report['actualArtifacts'])
validation=read(by_name['core-validation.json']);audit=read(by_name['structural-audit.json'])
check(validation==json.loads(Path(terminals['core-validate']['stdout']['path']).read_bytes()))
check(validation['normalizedValid']is validation['prunedValid']is True and validation['instantiated']is validation['compiledOrExportsCalled']is False)
check(validation['normalized']==by_name['normalized-adapter.wasm']and validation['pruned']==by_name['pruned-adapter.wasm'])
ns={};exec(compile((HERE/'core_data.py').read_text(),'<independent core DATA decoder>','exec'),ns)
actual_core=ns['compare'](Path(refs['originalAdapter']['path']).read_bytes(),Path(by_name['normalized-adapter.wasm']['path']).read_bytes(),Path(by_name['pruned-adapter.wasm']['path']).read_bytes())
payload=actual_core.pop('metadataPayload');check(payload==Path(by_name['embedded-wit-component.wasm']['path']).read_bytes())
policy=load(SOURCE/'core-policy.json');check(actual_core['convertedImports']==policy['targetImports'])
check(actual_core['functionReferenceMapping']==audit['functionIndexMapping']and actual_core['encodedMetadataSha256']==audit['encodedWitComponentSha256'])
check(actual_core['convertedUnreachableStubs']==audit['convertedTargetImports']==14 and actual_core['retainedFunctionImports']==audit['retainedFunctionImports']==49)
check(actual_core['originalFunctionsCompared']==93 and actual_core['typesCompared']==35 and actual_core['exportsCompared']==52)
for folder in [OUT,EXT]:
    for p in [folder,*folder.rglob('*')]:
        check(not p.is_symlink());s=p.stat();check(stat.S_IMODE(s.st_mode)==(0o700 if p.is_dir()else 0o600))
        if p.is_file():check(s.st_nlink==1);row(p)
original_identity=Path(refs['originalAdapter']['path']).stat();new_ids=[]
for name in ['normalized-adapter.wasm','pruned-adapter.wasm','embedded-wit-component.wasm']:
    s=Path(by_name[name]['path']).stat();check((s.st_dev,s.st_ino)!=(original_identity.st_dev,original_identity.st_ino));new_ids.append((s.st_dev,s.st_ino))
check(len(set(new_ids))==3)
# Full post-phase protection audit against the pre-existing immutable manifest.
inputs=load(SOURCE/'source-inputs.json');check(len(inputs['files'])==24359)
for r in inputs['files']:verify(r)
for ix in inputs['families']:family(ix)
for r in list(captured.values()):
    p=Path(r['path']);check(p.stat().st_size==r['bytes'])
summary=dict(schemaVersion=1,state='INDEPENDENT_CLOCK_IO_VALID_ADAPTER_FAILED_PHASE_DATA_VERIFIED_V1',checks=checks,rootObservation=root_row,sourceIndex=report['sourceIndex'],sourcePeer=report['sourcePeer'],rootAuthority=report['rootAuthority'],rootConfig=report['rootConfig'],workerResult=report['workerResult'],parentObservation=report['parentObservation'],workerTerminal=report['workerTerminal'],commandTerminals=report['commandTerminals'],artifacts=by_name,retainedOriginalCopiesVerified=35,sourceProtectedRowsVerified=24359,fixedFamiliesVerified=9,phaseFiles=len([p for p in OUT.rglob('*')if p.is_file()]),externalFiles=len([p for p in EXT.rglob('*')if p.is_file()]),rootToolObservationOnly=report['rootToolObservation'],actualWorkerExitCode=1,prunerExitCode=0,nodeCoreValidationExitCode=0,metadataExitCode=1,allMonitoredGroupsGone=True,finalProtectionError=None,coreDataAuditPassed=True,metadataDecoded=False,phasePassed=False,adapterAccepted=False,normalizationAndPruningRerun=False,nodeCoreValidationRerun=False,metadataParserRerun=False,applicationEngineOrGuestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False)
(HERE/'core-analysis.json').write_text(json.dumps(actual_core,indent=2)+'\n')
(HERE/'data-audit.json').write_text(json.dumps(summary,indent=2)+'\n')
(HERE/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=list(captured.values()),sourceProtectionManifest=row(SOURCE/'source-inputs.json'),declaredProtectionRowsRehashed=24359),indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items()if k in ['state','checks','retainedOriginalCopiesVerified','sourceProtectedRowsVerified','phaseFiles','externalFiles','actualWorkerExitCode','prunerExitCode','nodeCoreValidationExitCode','metadataExitCode','coreDataAuditPassed','metadataDecoded','phasePassed']}))
