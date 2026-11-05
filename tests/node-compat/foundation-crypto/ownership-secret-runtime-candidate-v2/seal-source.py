"""Own Source finalization only; inert pure/grammar programs, no operational API."""
from pathlib import Path
import ast,hashlib,json,subprocess,time
P=Path(__file__).resolve().parent
assert not(P/'index.json').exists()
def row(p):
    b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(n):return json.loads((P/n).read_text())
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
refs=read('references.json');source=read('source-check-results.json');assert source['protectedFiles']==34094 and source['completeFamilies']==32
node=refs['node'];assert row(Path(node['path']))==node
folder=P/'evidence/final-pure-and-grammar';folder.mkdir()
observations=[]
for name in ['entry.mjs','runtime-body.mjs','loading.mjs','checks.mjs','oracle.mjs','parser-tuple.mjs','test-pure.mjs','test-correction.mjs']:
    argv=[node['path'],'--check',str(P/name)];r=subprocess.run(argv,capture_output=True,timeout=30);(folder/(name+'.grammar.stdout.log')).write_bytes(r.stdout);(folder/(name+'.grammar.stderr.log')).write_bytes(r.stderr)
    observations.append(dict(argv=argv,rawExitCode=r.returncode,kind='grammar-only',source=row(P/name),sourceBodyOrImportsEvaluated=False));assert r.returncode==0 and r.stdout==r.stderr==b''
pure=[]
for name in ['test-pure.mjs','test-correction.mjs']:
    argv=[node['path'],str(P/name)];r=subprocess.run(argv,capture_output=True,timeout=60);(folder/(name+'.stdout.log')).write_bytes(r.stdout);(folder/(name+'.stderr.log')).write_bytes(r.stderr)
    observations.append(dict(argv=argv,rawExitCode=r.returncode,kind='inert-host-pure-and-parser',source=row(P/name),ownerAPIsOrWorkerOrOracleOrGeneratedOrEngineOrGuestInvoked=False));assert r.returncode==0 and r.stderr==b'';pure.append(json.loads(r.stdout))
assert pure[0]['checks']==114 and pure[1]['checks']==120 and pure[1]['originalThrowIdentityPreserved']is True
for name in ['check-source.py','external.py','seal-source.py']:ast.parse((P/name).read_text())
write('final-check-observations.json',dict(schemaVersion=1,programs=observations,pure=pure,grammarChecks=8,pureChecks=234,pythonAstFiles=3,sourceModulesImportedInertly=True,pinnedParserImportedOnlyForData=True,ownerAPIsOrRuntimeActionsInvoked=False))
write('source-check-observation.json',dict(schemaVersion=1,actualUnifiedExecSessionId=6597,rawExitCode=0,stdout=row(P/'evidence/source-check.stdout.log'),stderr=row(P/'evidence/source-check.stderr.log'),ownerActionsInvoked=False))
(P/'README.md').write_text("""# Guarded secret355 ordinary runtime v2 Source

SEALED UNREVIEWED SOURCE. This is the thin genuine successor to immutable6afd and independent M1 HOLD339388. It issues no Root/runtime/native action and changes no guest,component,core,fixture,semantic checker,oracle,frame/native metadata or package bytes. Current secret context remains real901/CBF/da258 native355+3/75/11 and actual28bc/c067 twelve-artifact proof. The newly built combined355 native generation with80 raw fields is a separate artifact and is not projected here.

M1 correction: capturedCall still invokes synchronously,records attempted count and retains typed raw before ordinary type/JSON/semantic assertions. When the raw writer fails with Y,the genuine host sequence.captureFailures state retains the actual unmodified Y. An optional host-only onCaptureFailure callback attempts a separate typed diagnostic; callback failure Z is retained in diagnosticFailures without replacing X. If invocation threw X,the function always rethrows ORIGINAL X identity,including null,false,zero,-0,undefined,bigint,string and frozen objects. It never mutates X or introspects its opaque properties. With returned-value+writerY,the original Y is propagated. Successful typed capture+throwX still preserves X exactly.

The worker uses this real callback for capture-write-failure-SEQ.json. Parent and worker failure.json writes use diagnosticWrite,so a persistent writer refusal cannot itself replace an already caught primary exception. Actual writer/diagnostic values stay in trusted host auxiliary state and safe typed envelopes expose only permitted primitive/opaque observations. A failed diagnostic persistence attempt is not claimed retained. If all filesystem writes fail,Y/Z may exist only in host memory until exit; no full object or durable-retention claim is made. The exact original primary throw remains available to outer raw stderr. Independent source/protection or close failures remain separate gates; the external phase must still fail on them.

Capture failure always aborts the session; attempted/written counts remain distinct and no successful completion may contain capture or diagnostic failures. Real full-before/final/failure generated/native/c47/package/Source/output bookends remain unchanged. The c47 record retains its historical41-field frame versus current zero-helper checks,full raw75 fields/native355+3/eleven manifests; no old one-shot helper or callable runs. Full4,934 packaging/tool files and22 links remain in original physical roles. Direct genuine crypto_secret_owner ESM/TLA/core loading,all four guarded cases,three fresh sessions,23 outer strings,20 run records,10 imports,55 sign attempts,50 verify attempts and45 complete successful tags remain exact. No GC,pressure,Wasmtime,other algorithms,unsafe reset,adoption or performance scope is added.

New own entry/external/Root/config/Source-peer/output contexts are v2. The entire6afd family and immutable HOLD/correction are authenticated as DATA before imports; their old files/states never change. The new Source peer requires INDEPENDENT_CRYPTO_OWNER355_SECRET_RUNTIME_SOURCE_REVIEW_PASSED_V2. Root/action/retained-config/actual-runtime slots remain NULL or unissued. Root must separately issue the genuine new phase and own monitor2400/worker600000ms lifecycle; no action is granted here.

Preparation passed133,825 read/hash/Source checks over34,094 declared files/modes,32 complete families and one exact historical donor tree,plus all4,934 package files/22 aliases. Thirteen modules,54 static edges and five explicit dynamic roles remain complete. Exact forward/inverse new Source derivations bind the held v1 bytes,while semantic/oracle/parser/loading copies remain exact. All114 original pure cases still pass. New120 assertions cover nine X kinds across successful/failing diagnostic callbacks,actual Y/Z identity retention,returned-value writer failure,successful raw throw,diagnostic failure-record paths and successful ordinary capture. Eight pinned Node grammar-only checks and three Python AST checks pass. Pure tests import inert host harness/parser modules only; no retained API,recheck,worker,monitor,Node oracle,generated module,engine,guest,key or crypto operation ran. Earlier pure/source observations remain retained.

Source approval is pending independent review. Full actual raw runtime results and native/API/package/source protection still require independent DATA review. Strong application/VM owners are combined; clear is not a finalizer/free/wipe/erasure or isolated-root proof. HMAC success would not test RSA/EC/BIGNUM/allocation faults or establish complete security/runtime acceptance.
""")
write('results.json',dict(schemaVersion=1,state='SECRET355_GUARDED_NORMAL_RUNTIME_SOURCE_READY_UNREVIEWED_V2',sourceOnly=True,sourceReviewPassed=None,parentSourceIndex=refs['parentRuntimeSourceIndex'],heldSourceReview=refs['heldRuntimeSourceReview'],requiredCorrectionContract=refs['requiredCorrectionContract'],entry=row(P/'entry.mjs'),external=row(P/'external.py'),actualArtifactReview=refs['actualArtifactReview'],actualArtifactContract=refs['actualArtifactContract'],component=refs['artifacts']['component'],engine=refs['engine'],metadata=refs['metadata'],freezeReceipt=refs['freezeReceipt'],nativeSourceFiles=355,externalEmbeddingSources=3,fullMetadataFields=75,wholeManifests=11,guardedCases=[0,1,2,3],sessions=['retained','fresh','wrapper'],rawPublicStrings=23,runRecords=20,guestKeyImports=10,guestSignAttempts=55,guestVerifyAttempts=50,fullGuestTags=45,protectedInputs=34094,completeFamilies=32,historicalDonorTrees=1,packageFiles=4934,packageLinks=22,sourceChecks=source['checks'],pureChecks=234,grammarChecks=8,pythonAstChecks=3,originalXIdentityPreservedOnCaptureWriterFailure=True,writerYAndCallbackZRetainedInHostState=True,diagnosticPersistenceNotGuaranteed=True,failedCaptureCanComplete=False,sourceIndependentReview=None,rootAuthority=None,retainedConfig=None,actualRuntimeResults=None,actualRuntimeReview=None,sourceHarnessModulesImportedInertly=True,pinnedParserUsedForStaticData=True,retainedApiOrReturnedRecheckInvoked=False,workerOrMonitorInvoked=False,nodeOracleInvoked=False,generatedModuleImported=False,engineOrGuestOrKeyOrCryptoInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False))
write('source-receipt.json',dict(schemaVersion=1,state='SEALED_SECRET355_NORMAL_RUNTIME_SOURCE_UNREVIEWED_V2',result=row(P/'results.json'),sourceCheck=row(P/'source-check-results.json'),checks=row(P/'final-check-observations.json'),derivations=row(P/'derivations.json'),entry=row(P/'entry.mjs'),sourceIndependentReview=None,rootAuthority=None,actualRuntimeResults=None,ownerActionsInvoked=False))
write('preparation-history.json',dict(schemaVersion=1,state='SOURCE_SEALED_UNREVIEWED_V2',parentSourceIndex=refs['parentRuntimeSourceIndex'],heldSourceReview=refs['heldRuntimeSourceReview'],ownerActionsInvoked=False,sourceOnlyChecksExecuted=True,pureHostHarnessAndParserImportsOnly=True,actualRuntimeAuthority=None,notes=['Original6afd/HOLD immutable. New own host capture/diagnostic state and identity-only exception preservation.','Successive pure tests strengthened explicit didThrow checks for undefined/falsy X. Prior pure-attempt1 retained. No actual owner or runtime action.']))
files=[]
for path in sorted(P.rglob('*')):
    assert not path.is_symlink()
    if path.is_file()and path.name!='index.json':d=row(path);d['path']=path.relative_to(P).as_posix();files.append(d)
write('index.json',dict(schemaVersion=1,files=files))
for d in files:
    actual=row(P/d['path']);assert actual['sha256']==d['sha256']and actual['bytes']==d['bytes']
for n in ['index.json','results.json','source-receipt.json']:print(n,json.dumps(row(P/n)))
print('members',len(files))
