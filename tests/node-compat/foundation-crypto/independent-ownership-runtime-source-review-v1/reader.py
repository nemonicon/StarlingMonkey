"""Independent source/hash/pure-data review. No author module is imported."""
import ast,hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent;K=P.parent;D=K/'ownership-runtime-candidate-v1'
SHA='4cb0d2c37de4ed4406611e6f5cc415934043d98eb4e5f6512461d55bad349dea'
inputs={};checks=[]
def need(v,m):
 if not v:raise AssertionError(m)
 checks.append(m)
def row(p):
 p=Path(p);h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b);n+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=n)
def verify(r,role):
 p=Path(r['path']);a=p.stat();need(p.is_file()and not p.is_symlink(),'ordinary input '+str(p));actual=row(p);b=p.stat()
 need(all(actual[k]==r[k]for k in ['path','sha256','bytes']),'exact input '+str(p))
 need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns),'stable input '+str(p))
 if str(p)in inputs:need(all(inputs[str(p)][k]==r[k]for k in ['path','sha256','bytes']),'consistent shared input');inputs[str(p)]['roles'].add(role)
 else:inputs[str(p)]={**actual,'roles':{role}}
 return actual
def data(r,role):verify(r,role);return json.loads(Path(r['path']).read_bytes())
def local(n):need(isinstance(n,str)and n and not n.startswith('/')and '\\'not in n and '\0'not in n and all(s not in ['', '.', '..']for s in n.split('/')),'finite local name');return n
def index(desc,count=None):
 value=data(desc,'finite-index');need(value['schemaVersion']==1 and isinstance(value['files'],list),'finite indexed source')
 if count is not None:need(len(value['files'])==count,'exact indexed members '+str(count))
 names=set();rows=[]
 for r in value['files']:
  n=local(r['path']);need(n not in names,'unique indexed member');names.add(n);rr=dict(path=str(Path(desc['path']).parent/n),sha256=r['sha256'],bytes=r['bytes']);verify(rr,'indexed-member');rows.append(rr)
 return value,rows
def save(name,v):(P/name).write_text(json.dumps(v,indent=2)+'\n')
ix=row(D/'index.json');need(ix['sha256']==SHA and ix['bytes']==3510,'exact source index')
source,source_rows=index(ix,22)
need({str(p.relative_to(D))for p in D.rglob('*')if p.is_file()}=={r['path']for r in source['files']}|{'index.json','source-receipt.json'},'exact members plus unconsumed postseal receipt')
freeze=data(next(r for r in source_rows if r['path'].endswith('/input-freeze.json')),'original-context-preparation')
need(len(freeze['files'])==13247 and len({r['path']for r in freeze['files']})==13247,'13247 unique original-context references')
for r in freeze['files']:verify(r,'complete-source-native-tool-artifact-reference')
refs=json.loads((D/'references.json').read_bytes());proof_ix,proof_rows=index(refs['actualArtifactReview']['index'],17)
proof=data(refs['actualArtifactReview']['result'],'actual-component-review')
contract=data(refs['actualArtifactContract'],'actual-whole-artifact-contract')
need(sum(r==refs['actualArtifactContract']for r in proof_rows)==1,'actual contract indexed exactly once')
need(proof['state']=='INDEPENDENT_CRYPTO_OWNER355_COMPONENT_V3_ARTIFACT_REVIEW_PASSED_V1'and proof['verifiedPassed']is True and
 proof['componentSourceIndexSha256']==refs['componentSourceIndex']['sha256']and proof['componentSha256']=='842f82e8ae330580bee2d160880b5a3a35aac7c9baf357938814ecf2237a149d'and
 proof['generatedModuleImported']is False and proof['keyOperationsInvoked']is False,'actual construction/static-ABI proof is not key/runtime evidence')
need(refs['artifacts']==contract['artifacts']==contract['requiredArtifacts']==proof['artifacts'],'whole actual12-name artifact tuple unchanged')
need(all(proof[k]==v for k,v in contract['requiredFixedValues'].items()),'entire actual artifact fixed-value contract consistent')
for r in refs['artifacts'].values():verify(r,'actual-loading-artifact')
need(refs['engine']==refs['artifacts']['engine']and refs['engine']['sha256']=='36bd850895a11af8ffaefdb8296630222c4ad4652a0e58f45ce0ec23c1bebc05'and refs['engine']['bytes']==10002820,'genuine guard355 normal engine relation')
need(contract['nativeContexts']==dict(configuredSourceRoot='/private/tmp/starling-node-compat/crypto-owner-source-v2',sourceRoot='/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze/source'),'exact original configured/frozen spellings remain')
need(contract['runtimeBackendProof']==dict(verified=False,version=None,vernum=None),'backend proof remains false/null/null')
verify(refs['node'],'pinned-Node22');verify(refs['guestSource'],'unchanged-sealed-guest')
guest=Path(refs['guestSource']['path']).read_text()

# This inspects finite literal imports, not a general JavaScript parser.
graph=[];visited=set();by={r['path']:r for r in freeze['files']};own={r['path']for r in source_rows}
def source_graph(path):
 path=path.resolve()
 if str(path)in visited:return
 visited.add(str(path));need(str(path)in own or str(path)in by,'physical import belongs to immutable source/closure '+str(path))
 for spec in re.findall(r'(?:from\s*|import\s*)[\'\"]([^\'\"]+)[\'\"]',path.read_text()):
  if spec.startswith('.'):
   target=(path.parent/spec).resolve();graph.append(dict(source=str(path),specifier=spec,target=str(target)));source_graph(target)
for path in D.glob('*.mjs'):source_graph(path)
text={n:(D/n).read_text()for n in ['guard.mjs','loading.mjs','run.mjs','worker.mjs','checks.mjs','oracle.mjs']}
guard=text['guard.mjs'];loading=text['loading.mjs'];parent=text['run.mjs'];worker=text['worker.mjs'];check=text['checks.mjs'];oracle=text['oracle.mjs']
for token in ["INDEPENDENT_CRYPTO_OWNER355_RUNTIME_SOURCE_REVIEW_PASSED_V1",'peer.data.sourceIndexSha256===sourceSha','peer.data.sourceOnly===true','peer.data.sourceReviewPassed===true','peer.data.ownerActionsInvoked===false',
 'Object.values(refs.artifacts)','for(const row of all)','await artifact.recheck()','await own.recheck()','await peer.recheck()','await streamHash(refs.node)']:
 need(token in guard,'guard exact peer/private full recheck clause '+token)
need(guard.index('const configRow=descriptor(input)')<guard.index('await regular(configRow)')and 'deepFreeze(JSON.parse(await regular(rootRow)))'in guard,'private primitive/Root captures before asynchronous following')
need('cryptoOwnerBootstrapPreflight('not in guard and 'componentPreflight('not in guard and 'selectedManifestsForEngine('not in guard,'no bootstrap/old selector call in runtime admission')
need('equal(contract.artifacts,refs.artifacts)'in guard and 'Object.values(refs.artifacts)'in guard,'full existing artifact contract equality and rehash')
for token in ["ns!==null&&typeof ns==='object'&&Object.getPrototypeOf(ns)===null",'Object.getOwnPropertyNames(ns).sort()',"!Object.hasOwn(ns,'then')",'typeof ns[name]','Reflect.ownKeys(u).length===0']:
 need(token in loading,'exact namespace clause '+token)
need(loading.index('Object.getOwnPropertyNames(ns).sort()')<loading.index('typeof ns[name]'),'unknown/then names refuse before export value reads')
need(loading.index('await auditLoading(admitted.artifacts)')<loading.index('await admitted.recheck()')<loading.index('await import(pathToFileURL(captured.rows.glue.path))'),'captured source/ABI/parser and complete proof recheck before direct generated import')
for token in ["'./crypto_owner.core.wasm'",'base.object.meta?.name===\'import\'',"awaits[0].name==='$init'","parse(new TextDecoder('utf-8'",'publicJSExports(ast)','parsePublicWit(','parsePublicDts(','checkTranspileMetadata(']:need(token in loading,'actual captured source protocol clause '+token)
need('namespace[name](...args)'in loading and 'instantiate('not in loading and 'WebAssembly.Memory'not in loading,'real direct namespace calls; no guessed instantiate/private memory API')
need("Number.isSafeInteger(args[0])&&args[0]>=0&&args[0]<4&&!Object.is(args[0],-0)"in loading,'scalar run0..3 integer-only and no coercion')
need(parent.index('await runtimePreflight(descriptor(config))')<parent.index('DurableOutput.create')<parent.index('await nodeOracle()'),'full source/native/artifact/Root gate before outputs and host oracle')
need(parent.index("out.write('node-oracle.json'")<parent.index('checkOracle(oracle)')<parent.index('await runOwnedCommand'),'complete host oracle retained/check before guest workers')
need(parent.index("mkdir(join(out.root,'processes')")<parent.index('await runOwnedCommand'),'processes0700 prepared before owned collector')
need("['retained','fresh','wrapper']"in parent and 'timeoutMs:frame.workerTimeoutMs,maxOutputBytes:16*1024*1024'in parent and 'checkOwnedTerminal(terminal)'in parent,'finite fresh owned worker schedule/deadline/full terminal gate')
need(worker.index('await runtimePreflight(descriptor(config))')<worker.index('await loadSession(frame)'),'worker repeats authority/source/native/artifact admission before loading')
capture=worker.index("kind:'return',returnedType:typeof value")
need(capture<worker.index("need(typeof value==='string'")<worker.index('return JSON.parse(value)'),'whole primitive return captured before type/length/JSON assertions')
need("kind:'throw',thrownType:typeof error"in worker and "{opaque:true,fullOpaqueValueClaim:false}"in worker,'honest throw and nonstring opaque records; no coercion')
need("value.length<=2*1024*1024"in worker and 'asyncGuestScalarObservedAsOrdinaryString:true'in worker,'ordinary bounded scalar strings required; no forced await of guessed result type')
need('value=session.invoke(name,args)'in worker and 'await session.invoke'not in worker,'invoke result type is observed rather than normalized')
need('await session.recheck();await frame.recheck();await out.recheck()'in worker and 'await frame.recheck();await out.recheck()'in parent,'full end audits before successful output')
need("['inspectCalls','runCalls','clearCalls','validateCalls','keyImportsAttempted','keyImportsFulfilled','signCalls','verifyCalls']"in check and 'equal(r.counters,expected)'in check,'complete public counters checked')
for token in ['r.firstSignatureHex===EXPECTED','r.secondSignatureHex===EXPECTED','r.firstSignatureHex===oracle.tagHex',"'a5'.repeat(8)+'4869205468657265'+'a5'.repeat(8)","'a5'.repeat(8)+EXPECTED+'a5'.repeat(8)",'byteOffset:8,byteLength:8,backingBytes:24',"Object.keys(a).sort(),['hash','length','name']",'wanted)\',\'Complete ordered operation observations','native-promise-rejection','uniqueNativeErrorCauseInferred===false']:
 if token=="wanted)','Complete ordered operation observations":token="equal(rows.map(v=>v.operation+':'+v.phase),wanted)"
 need(token in check,'full public semantics/counterexample clause '+token)
need("for(let id=0;id<4;id++)"in guest and "for(let id=0;id<4;id++)"in check,'same ordered0..3 wrapper cases')
need("check(rawKey!==null,'valid raw-key positive control must precede prototype probes')"in guest,'new-artifact prototype probes require positive raw control')
need("for(let rotation=0;rotation<(scenario==='retained'?3:1);rotation++)for(let id=0;id<4;id++)"in worker,'all rotations preserve positive controls before prototype refusal')
need("createHmac('sha256',raw).update(message).digest('hex')"in oracle and "for(const format of ['raw','jwk'])"in oracle,'future host oracle exact HMAC and raw/JWK WebCrypto paths; not executed')
need("v.tagHex===EXPECTED"in oracle and "k.tagHex===EXPECTED"in oracle and "k.valid===true&&k.invalid===false"in oracle,'future host oracle full known-answer/valid/tampered comparison')
tag=re.search("EXPECTED='([a-f0-9]+)'",check).group(1);need(len(bytes.fromhex(tag))==32 and "EXPECTED='"+tag+"'"in guest,'same complete32-byte constant in checker and unchanged guest')

# Pure schedule arithmetic, not a crypto or guest call.
def schedule(rotations,wrapper=False):
 counters=dict(inspectCalls=1,runCalls=0,clearCalls=0,validateCalls=int(wrapper),keyImportsAttempted=0,keyImportsFulfilled=0,signCalls=0,verifyCalls=0)
 steps=[]
 for rotation in range(rotations):
  for case in range(4):
   counters['runCalls']+=1
   if case<2:
    counters['keyImportsAttempted']+=1;counters['keyImportsFulfilled']+=1;counters['signCalls']+=2;counters['verifyCalls']+=2
   elif case==2:counters['signCalls']+=4;counters['verifyCalls']+=4
   else:counters['signCalls']+=3;counters['verifyCalls']+=2
   steps.append(dict(rotation=rotation,caseId=case,counters=dict(counters),expectedRawRetained=True,expectedJwkRetained=case!=0 or counters['keyImportsFulfilled']>1))
 counters['clearCalls']+=1;counters['inspectCalls']+=1
 return dict(publicStringReturns=1 if wrapper else 3+4*rotations,runRecords=4*rotations,finalCounters=counters,steps=steps)
schedules=dict(retained=schedule(3),fresh=schedule(1),wrapper=schedule(1,True))
totals=dict(publicStringReturns=sum(s['publicStringReturns']for s in schedules.values()),runRecords=sum(s['runRecords']for s in schedules.values()),
 guestKeyImports=sum(s['finalCounters']['keyImportsFulfilled']for s in schedules.values()),guestSignAttempts=sum(s['finalCounters']['signCalls']for s in schedules.values()),guestVerifyAttempts=sum(s['finalCounters']['verifyCalls']for s in schedules.values()))
need(totals==dict(publicStringReturns=23,runRecords=20,guestKeyImports=10,guestSignAttempts=55,guestVerifyAttempts=50),'independent complete schedule totals')
need(schedules['wrapper']['finalCounters']==dict(inspectCalls=2,runCalls=4,clearCalls=1,validateCalls=1,keyImportsAttempted=2,keyImportsFulfilled=2,signCalls=11,verifyCalls=10),'wrapper literal final counters reconstructed')
template=json.loads((D/'future-root-authority.template.json').read_bytes())
need(template['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_NORMAL_RUNTIME_V1'and template['sourceIndexSha256']is None and template['normalRuntimeAllowed']is False and template['nodeOracleAllowed']is False and template['sourceIndependentReview']is None,'future action/source peer remain NULL/false')
for name in ['gcAllowed','oomAllowed','resetAllowed','otherVariantsAllowed','wasmtimeAllowed','timingAllowed','operationalAdmission','runtimeAcceptanceClaim']:need(template[name]is False,'no extra action authority '+name)
need(template['actualArtifactReview']==refs['actualArtifactReview']and template['actualArtifactContract']==refs['actualArtifactContract'],'historical artifact facts are exact separate authority inputs')
need(not Path(template['outputRoot']).exists(),'runtime output absent at source review')
for p in D.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
pure=json.loads((D/'evidence/pure.stdout.log').read_bytes());stored=json.loads((D/'evidence/source.stdout.log').read_bytes());syntax=json.loads((D/'evidence/syntax.json').read_bytes())
need(pure['checks']==61 and pure['generatedModuleImported']is False and pure['guestOrNodeKeyHmacOperationsInvoked']is False,'stored61 pure/captured-source outcomes are data only')
need(stored['checks']==13274 and stored['inputRows']==13247,'stored source checks authentic counts')
need(len(syntax['modules'])==7 and all(r['rawExitCode']==0 for r in syntax['modules'])and syntax['pythonAstParsed']is True,'stored7JS/1Python parse-only outcomes')
save('rehashed-inputs.json',dict(schemaVersion=1,files=[dict(r,roles=sorted(r['roles']))for r in sorted(inputs.values(),key=lambda r:r['path'])],ownerActionsInvoked=False))
save('schedule-and-boundaries.json',dict(schemaVersion=1,schedules=schedules,totals=totals,literalImportEdges=graph,actualLocalModules=len(visited),
 sourceOnly=True,guestOrNodeOracleInvoked=False,completeRawBeforeTypeJsonSemanticChecks=True,
 ordinaryStringCodeUnitLimit=2097152,durableIndividualFileByteLimit=67108864,ownedWorkerTimeoutMs=600000,ownedPipeByteLimit=16777216,
 notes=['Return strings are retained before the2MiB scalar assertion, subject to the existing64MiB individual durable-file bound; writes fail closed rather than clip.',
 'Host Node oracle is a separate test oracle. Workers use the identical full known-answer constant; parent separately checks actual host values before launching workers.',
 'Expected refusal errors are checked as bounded native-Promise TypeErrors, not as complete Node message or conversion-order parity.',
 'The source has no internal overall-parent deadline; a Root external controller must bound the complete parent/oracle/three-worker action.',
 'The source only declares application-reference release; no collector/finalizer/private heap/zeroization proof is inferred.']))
save('results.json',dict(schemaVersion=1,state='INDEPENDENT_CRYPTO_OWNER355_RUNTIME_SOURCE_REVIEW_PASSED_V1',sourceIndexSha256=SHA,
 sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,sourceIdentityAndClosureVerified=True,sourceMembers=22,preparationRowsRehashed=13247,
 uniqueInputsRehashed=len(inputs),actualArtifactReviewIndexSha256=refs['actualArtifactReview']['index']['sha256'],actualArtifactContractSha256=refs['actualArtifactContract']['sha256'],
 actualComponentSha256=refs['artifacts']['component']['sha256'],nativeEngineSha256=refs['engine']['sha256'],nativeSourceFiles=355,
 entireActualArtifactTupleUnchanged=True,configuredFrozenOriginalContextsPreserved=True,noMetadataOrSourceProjection=True,
 actualLiteralModuleGraphClosed=True,ordinaryScalarSchedule=totals,positiveControlsBeforePrototypeGuardCases=True,
 exactActualEsmTlaSourceProtocol=True,completeReturnCaptureBeforeAssertions=True,typedThrowOpaqueAndStringBoundaries=True,
 exactCountersWindowsTagsOrderAndStateAssertions=True,hostOraclePinnedNodeKnownAnswerAndWebCryptoSourceOnly=True,
 ownerPureChecksAuthenticatedAsData=61,ownerSourceChecksAuthenticatedAsData=13274,ownerJsParseChecksAuthenticatedAsData=7,ownerPythonParseChecksAuthenticatedAsData=1,
 ownerTestsOrGenuineLoadingOracleWorkerPreflightRunNormalInvoked=False,reviewerReadHashPureDataPythonAstOnly=True,
 generatedModuleImported=False,keyOrHmacOrCryptoOperationsInvoked=False,workerOrGuestOrNativeOrHostActionsInvoked=False,
 rootRuntimeAuthority=None,actualRuntimeResults=None,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False,
 concreteBlockers=[],sourceChecks=len(checks),limitations=[
 'Source-only peer permits a separate new normal-only Root decision; no action approval is issued.',
 'The source requires ordinary returned strings without awaiting or normalizing the generated invoke result. Actual async guest scalar behavior is still unproved.',
 'The parent has no internal overall action/oracle deadline. A separately bounded external Root controller is required, in addition to each600s owned-worker bound.',
 'Complete captures are subject to the existing64MiB individual durable-file ceiling; the ordinary scalar acceptance limit is2MiB code units. Capture/write failure cannot publish a pass.',
 'All counts are source-coupled public fixture counters and independent pure arithmetic, not runtime observations or global native tracing.',
 'Prototype/ordinary-invalid checks are native-Promise TypeError requirements, not all Node error message/conversion-order parity.',
 'Clear releases application holders only. No wipe/free/finalizer/private copy/isolated rooting/GC/allocator safety proof or other-algorithm/performance claim is made.',
 'Literal import graph checks are finite pinned-source inspection, not a general JavaScript parser claim.',
 'The author postseal source-receipt.json is unindexed advisory data and is not imported or consumed by the runtime guard.']))
print(json.dumps(dict(state='INDEPENDENT_CRYPTO_OWNER355_RUNTIME_SOURCE_REVIEW_PASSED_V1',members=22,refs=13247,uniqueInputs=len(inputs),checks=len(checks))))
