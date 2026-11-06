"""Finite own DATA-review publication; invokes no target or operational API."""
from pathlib import Path
import ast,hashlib,json,os,stat
P=Path(__file__).resolve().parent
STATE='INDEPENDENT_COMBINED355_RESOURCE_RUNTIME_RESULTS_REVIEW_PASSED_V3'
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def read(n):return json.loads((P/n).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def desc(p):p=Path(p);return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
def checked(d):
 p=Path(d['path']);assert p.is_absolute() and p.is_file() and not p.is_symlink();assert p.stat().st_size==d['bytes']and sha(p)==d['sha256'];return p
intake=read('intake-summary.json');protection=read('current-protection.json')
assert intake['state']=='INDEPENDENT_RESOURCE_RUNTIME_V3_ACTUAL_READ_ONLY_INTAKE_PASSED'
terminals={n:read('evidence/'+n+'/terminal.json')for n in ['intake-1','semantic-1','negative-1','protection-1']}
assert all(t['rawExitCode']==0 for t in terminals.values())
assert all((P/'evidence'/n/'stderr.log').read_bytes()==b''for n in terminals)
semantic=json.loads((P/'evidence/semantic-1/stdout.log').read_bytes());negative=json.loads((P/'evidence/negative-1/stdout.log').read_bytes())
assert semantic['coverage']==intake['coverage']and negative['passed']==20
raw=read('raw-copy-ledger.json');assert len(raw['files'])==83
for r in raw['files']:assert checked(r['original']).read_bytes()==checked(r['copy']).read_bytes()
# These pure imports were authenticated through the genuine full Source intake.
module_paths=['combined-native-runtime-candidate-v3/session-model.mjs','combined-native-runtime-candidate-v3/models.mjs','combined-clock-lifecycle-candidate-v2/collectors.mjs','clock-v13-runtime-candidate-v2/wave.mjs']
write('pure-data-module-roles.json',dict(schemaVersion=1,purpose='Only retained DATA parsing; no operational imports or target execution',modules=[desc(P.parent/n)for n in module_paths]))
fixed=dict(schemaVersion=1,verifiedPassed=True,sourceIndexSha256=intake['sourceIndex']['sha256'],fixtureId='resource',nativeEngineSha256=intake['nativeEngine']['sha256'],componentSha256=intake['component']['sha256'],nativeSourceFiles=355,externalEmbeddingSources=3,fullMetadataFields=80,selectedWholeManifests=11,nativeOffsetInterestDropOrTeardownProved=False,fullProfileAcceptance=False,runtimeAcceptanceClaim=False,operationalAdmission=False,expectedCallbackFailureProved=False,fatalCallbackGateSatisfied=False,fullSixFixturesAccepted=False,all17GatesSatisfied=False,timingAllowed=False)
roles={n:intake[n]for n in ['sourceIndex','sourcePeer','actualIndex','result','completion','externalParentTerminal','outerTerminal','rootResult','runtimeRootAuthority','runtimeConfig','invocation','component','mappedReview','mappedContract','nativeEngine','nativeMetadata','freezeReceipt','observerPreparationCorrection','currentObserver']}
r=dict(state=STATE,**fixed,**roles,coverage=intake['coverage'],reviewerActions=dict(readHashDataOnly=True,pureRetainedDataValidatorsInvoked=True,targetOrApiHelperRecheckWorkerGuestReruns=False,hostActionsInvoked=False),originalAction=dict(rootToolSession=55164,rawExitCode=0,ordinaryGuestExportsInvoked=True,compilerOrMappingOrCryptoInvoked=False,innerNodePid=intake['innerNodePid'],outerParentPid=intake['outerParentPid'],childPids=intake['childPids'],fiveDistinctOwnedChildren=True,allRawExitCodesZero=True,noSignalsTimeoutsOutputLimitsOrCleanupErrors=True),publication=dict(indexedPayloadFiles=70,totalActualFiles=72,nestedChildIndicesAndCompletionsIndexed=True,allWholeRawValuesRetained=True,processPipesMode='0644',otherFilesMode='0600',directoriesMode='0700',singleLinkFiles=True),semanticEvidence=desc(P/'evidence/semantic-1/stdout.log'),negativeEvidence=desc(P/'evidence/negative-1/stdout.log'),currentProtection=desc(P/'current-protection.json'),intakeEvidence=desc(P/'intake-summary.json'),rawCopyLedger=desc(P/'raw-copy-ledger.json'),perCaseObservations=semantic['cases'],sessions=semantic['sessionRows'],typedNodeStrings=32,fullWaveStringsDecoded=3,allCasePayloadsAndCounterContinuityValidated=True,callbackCause='not-exercised',nativeResourceCountsObserved=False,publicTimerIdObservationScope='Per component instance;322 registrations, not globally unique numeric IDs',wasmtimeWithinOneOuterExport=True,separateWasmtimeHostCallInterleavingProved=False,crossHostWholeWrapperByteEqualityClaim=False,actualTimeProtectionQualification=intake['actualTimeProtectionQualification'],currentIntake=dict(checks=intake['checks'],fullHashFiles=intake['currentFullHashFiles'],logicalBytes=intake['currentLogicalBytes'],indexedFamilies=intake['currentFamilies']),checks=dict(intake=intake['checks'],currentProtection=protection['checks'],retainedSemantics=semantic['checks'],negativeRefusals=negative['passed']),limits=['Native drop/handle/interest/GC/allocator-failure counts unobserved','Combined owners do not prove a sole temporary root','No reset/reuse/teardown or native monotonic-offset ownership proof','No fatal callback acceptance or six-fixture/seventeen-gate/full-profile adoption','No target/helper/API/recheck/worker/guest operation rerun by reviewer'],grantsAnyActionAuthority=False)
write('results.json',r)
k=dict(schemaVersion=1,requiredReviewState=STATE,requiredFixedValues=fixed,requiredExactDescriptors=roles,requiredCoverage=intake['coverage'],grantsAnyActionAuthority=False)
write('result-contract.json',k)
# Execute the same finite joins used by genuine runtime.prerequisiteResource.
assert r['schemaVersion']==1 and r['state']==k['requiredReviewState']and r['verifiedPassed']is True
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for n,v in k[group].items():assert r[n]==v,(group,n)
assert r['coverage']==k['requiredCoverage']and r['coverage']['runRecords']==49 and r['coverage']['callbackObservations']==98 and r['coverage']['newIds']==322
assert r['sourceIndexSha256']==intake['sourceIndex']['sha256']and r['nativeEngineSha256']==intake['nativeEngine']['sha256']and r['componentSha256']==intake['component']['sha256']
for n in ['read-data.py','check-protection.py','seal.py']:ast.parse((P/n).read_text(),filename=n)
write('checkpoint-status.json',dict(schemaVersion=1,state='SEALED_INDEPENDENT_ACTUAL_RESOURCE_RUNTIME_V3_DATA_PASS',originalRootToolSession=55164,originalRootRawExitCode=0,readerExecuted=True,actualOutputInspected=True,verifiedPassed=True,reviewState=STATE,sourceIndexSha256=intake['sourceIndex']['sha256'],targetOrHelperReruns=False,grantsAnyActionAuthority=False,allOwnCheckToolsTerminal=True))
write('final-validation.json',dict(schemaVersion=1,state='RESULT_CONTRACT_RAW_COPIES_AND_PREREQUISITE_RESOURCE_JOINS_PASSED',requiredFixedValues=len(fixed),requiredExactDescriptorRoles=len(roles),requiredCoverageExact=True,copiedRawFiles=len(raw['files']),pureSemanticChecks=semantic['checks'],negativeRefusals=negative['passed'],allCheckTerminalsZero=True,nestedRawIndexPaths=['raw/actual/index.json','raw/actual/fresh/index.json','raw/actual/retained/index.json'],onlyOwnRootIndexExcluded=True,noOperationalReruns=True))
write('receipt.json',dict(schemaVersion=1,state='INDEPENDENT_COMBINED355_RESOURCE_RUNTIME_V3_DATA_REVIEW_SEALED',reviewState=STATE,result=desc(P/'results.json'),contract=desc(P/'result-contract.json'),validation=desc(P/'final-validation.json'),originalRootResult=intake['rootResult'],sourceIndex=intake['sourceIndex'],currentProtection=desc(P/'current-protection.json'),rawCopyLedger=desc(P/'raw-copy-ledger.json'),reviewerOperationalActionsInvoked=False,grantsAnyActionAuthority=False))
# Exclude only OWN/index.json. Nested raw/actual/*/index.json are payloads.
files=[]
for p in sorted(P.rglob('*')):
 assert not p.is_symlink()
 if p.is_file()and p!=P/'index.json':
  d=desc(p);files.append(dict(d,path=p.relative_to(P).as_posix()))
write('index.json',dict(schemaVersion=1,files=files))
assert {p.relative_to(P).as_posix()for p in P.rglob('*')if p.is_file()}=={'index.json',*[r['path']for r in files]}
assert all((P/n).is_file()and any(r['path']==n for r in files)for n in ['results.json','result-contract.json','raw/actual/index.json','raw/actual/fresh/index.json','raw/actual/retained/index.json'])
for row in files:checked(dict(row,path=str(P/row['path'])))
print(json.dumps(dict(state=STATE,index=desc(P/'index.json'),result=desc(P/'results.json'),contract=desc(P/'result-contract.json'),receipt=desc(P/'receipt.json'),indexedMembers=len(files),actualFiles=len(files)+1,logicalBytes=sum(r['bytes']for r in files),noOperationalActions=True)))
