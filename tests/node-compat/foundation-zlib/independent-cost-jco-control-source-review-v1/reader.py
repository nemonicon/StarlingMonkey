"""Independent read/hash/source-data inspection; never import owner modules."""
import difflib
import hashlib
import json
import re
import stat
from pathlib import Path

P=Path(__file__).resolve().parent
Z=P.parent
C=Z/'cost-jco-control-correctness-candidate-v1'
D=Z/'cost-jco-correctness-candidate-v2'
V=Z/'cost-jco-correctness-candidate-v3'
R=Z/'independent-cost-jco-correctness-v3-results-review-v1'
G=Z/'cost-guest-oracle-candidate-v2'
PIN='ad0d651fdb8653a8a708514131bad52cf8cc05b657c6cefd92604aca3c3f7a23'
seen={};checks=[]
def need(value,message):
 if not value:raise AssertionError(message)
 checks.append(message)
def row(path,expected=None):
 path=Path(path);s=path.lstat();need(stat.S_ISREG(s.st_mode),'Ordinary file '+str(path));h=hashlib.sha256()
 with path.open('rb')as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 value=dict(path=str(path),sha256=h.hexdigest(),bytes=s.st_size)
 if expected:need(all(value[k]==expected[k]for k in ('sha256','bytes')),'Exact tuple '+str(path))
 seen[str(path)]=value;return value
def data(path):return json.loads(Path(path).read_bytes())
def write(name,value):(P/name).write_text(json.dumps(value,indent=2)+'\n')
def indexed(root,pin):
 need(row(root/'index.json')['sha256']==pin,'Exact source/proof index '+str(root));ix=data(root/'index.json')
 need(len(ix['files'])==len({r['path']for r in ix['files']}),'Unique finite indexed members')
 for r in ix['files']:
  need(not Path(r['path']).is_absolute()and all(p not in ('','.','..')for p in r['path'].split('/')),'Safe indexed member')
  row(root/r['path'],r)
 return ix
def main():
 own=indexed(C,PIN);need(len(own['files'])==25,'25 final new source/evidence files')
 prep=data(C/'input-freeze.json');need(len(prep['files'])==159 and prep['runtimeActionSeal']is False and prep['relocationOfOriginalPreparationContextsAllowed']is False,'159 original-context source refs, not runtime or relocated seal')
 for r in prep['files']:row(r['path'],r)
 prior=indexed(V,'0124b94f28b20cea7d85c8e7a2619a33099ee98ed56d4920dd5d5749da28cb8c')
 donor=indexed(D,'d2516c934df3fa8f3ecd58b187cc2bc0f28fab996ab97ada0854e4988d9befeb')
 indexed(G,'ebe8fa901a3516358539c0458b09cad822308f9a3b0c76db33015ff378a8eae8')
 review=indexed(R,'e03bb0db65f6009e86a6d55e4553e820d143c702128976efc5ef47e092548083')
 prerequisite=data(C/'prerequisites.json')
 for d in [prerequisite['correctnessSource'],prerequisite['donorSource'],*prerequisite['review'].values()]:row(d['path'],d)
 contract=data(R/'result-contract.json');need(row(R/'result-contract.json')['sha256']=='25411f2ecb278c1eeda7b27a0aafa47b29cc3d9a53221a327e9e5c94002936f1','Exact254 complete previous result contract')
 result=data(R/'results.json')
 for k,v in contract['requiredFixedValues'].items():need(result[k]==v,'Unchanged actual prior fixed value '+k)
 for k,v in contract['requiredCoverage'].items():need(result['coverage'][k]==v,'Unchanged actual prior full coverage '+k)
 need(result['executedControlWorkloads']is False and result['controlOperations']==0 and result['coverage']['totalOwnedWorkers']==228,'Actual old228 pass has zero controls; not reused as new control execution')
 need(contract['requiredExactDescriptors']['rootAuthority']['sha256']=='235d391b7f730899d0b8f5be31247c100d9d997f6796042f15f86ed8af07daf6','Genuine unchanged prior235d Root authority')
 # Required exact records are data prerequisites; the full old output closure
 # is revalidated by the future genuine guard, not executed here.
 for k,d in contract['requiredExactDescriptors'].items():
  row(d['path'],d);need(result[k]==d,'Prior exact descriptor remains contract-bound '+k)
 for arm,d in contract['requiredComponents'].items():row(d['path'],d)
 old_authority=data(contract['requiredExactDescriptors']['rootAuthority']['path'])
 need(old_authority['state']=='ROOT_REVIEWED_ZLIB_COST_JCO_CORRECTNESS_V3'and old_authority['action']=='untimed-jco-correctness','Actual old action state preserved, never changed into control authority')

 derivation=data(C/'source-derivations.json');need(len(derivation['files'])==2 and sum(len(r['edits'])for r in derivation['files'])==10,'Exactly two afterimages/ten recorded reversals')
 patch=''
 for r in derivation['files']:
  before=Path(r['origin']).read_text();after=(C/r['path']).read_text();current=before
  need(hashlib.sha256(before.encode()).hexdigest()==r['beforeSha256']and hashlib.sha256(after.encode()).hexdigest()==r['afterSha256'],'Actual loader/collector before and after hashes')
  for e in r['edits']:
   offsets=[m.start()for m in re.finditer(re.escape(e['old']),current)];need(offsets==e['beforeOffsetsAtEdit']and len(offsets)==e['count'],'Exact forward occurrence offsets');current=current.replace(e['old'],e['new'])
  need(current==after,'Whole exact forward source derivation '+r['path'])
  for e in reversed(r['edits']):
   shift=0;positions=[]
   for offset in e['beforeOffsetsAtEdit']:positions.append(offset+shift);shift+=len(e['new'])-len(e['old'])
   for offset in reversed(positions):need(current[offset:offset+len(e['new'])]==e['new'],'Exact reverse recorded slice');current=current[:offset]+e['old']+current[offset+len(e['new']):]
  need(current==before,'Whole source reversal to actual immutable donor '+r['path'])
  patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+Path(r['origin']).name,tofile='b/'+r['path']))
 need(patch.encode()==(C/'control-only.UNAPPLIED.patch').read_bytes(),'Unapplied patch equals actual ten edits')

 admit=(C/'admission.mjs').read_text();parent=(C/'run.mjs').read_text();worker=(C/'worker.mjs').read_text();loader=(C/'loading.mjs').read_text();collector=(C/'collector.mjs').read_text()
 transport=(D/'transport.mjs').read_text();durable=(D/'durable.mjs').read_text();host=(D/'durable-host.mjs').read_text();prior_admit=(V/'admission.mjs').read_text()
 need(admit.index('authorityModel(authority,sourceSha)')<admit.index('await sourceIndex(')<admit.index("await indexed(authority.sourceIndependentReview")<admit.index('await completedProof(')<admit.index("await import('../cost-jco-correctness-candidate-v3/admission.mjs')")<admit.index('await correctnessPreflight('),'New authority/own/prior/donor/peer/completed proof before genuine prior guard')
 need("rootAction:completed.oldAuthority"in admit and "rootRow=descriptor(rootAction)"in admit and "peer.data.controlSourceIndexSha256===sourceSha"in admit,'Separate control authority; prior genuine Root proof not rewritten')
 need("Object.entries(contract.requiredFixedValues)"in admit and "Object.entries(contract.requiredCoverage)"in admit and "Object.entries(contract.requiredExactDescriptors)"in admit,'All prior contract fixed/coverage/exact descriptor requirements checked')
 need("for(const item of actualIndex.files)"in admit and "for(const row of outputRows)await regular(row"in admit and "await completed.recheck();await frame.recheck()"in admit,'Whole completed output inventory hashed and final source/native/frame rechecks implemented')
 need("same(frame.frames[arm].artifact.component,completed.contract.requiredComponents[arm])"in admit and "same(frame.oracle,completed.contract.requiredExactDescriptors.oracle)"in admit,'Same actual reviewed component/oracle tuples, not replacement provider/native')
 need("criticalFiles:Object.freeze([...own.rows,...frame.criticalSourceFiles,rootRow])"in admit and "criticalSourceFiles:Object.freeze([...own.rows,...parents.flatMap(p=>p.rows)])"in prior_admit,'Worker critical tuple includes exact new code and inherited actual parent modules/data')
 need(any(r['path']=='cases.json'for r in donor['files']),'Original cases.json physically indexed in inherited worker critical tuple')
 need("const admitted=await controlPreflight(options)"in parent and parent.index('await controlPreflight(options)')<parent.index('await DurableOutput.create(admitted.outputRoot)'),'No output before complete control preflight')
 need("for(const arm of ARMS)"in parent and "args:[join(HERE,'worker.mjs'),JSON.stringify(input)]"in parent and "timeoutMs:600000,maxOutputBytes:16*1024*1024"in parent,'Exactly three fresh serial owned arm workers, fixed600s/16MiB bounds')
 need("await disk(2*1024**3)"in parent and "await disk(800*1024**2)"in parent,'Operational2GiB and800MiB disk guards')
 need(parent.index('for(const path of registered)')<parent.index('checkOwned(status)') and "await persistFile({output,write,path:terminalPath"in host,'Raw terminal/pipes durable before parent terminal predicates')
 need("spawn(executable,args,{detached:true"in host and "process.kill(-pid"in host and "process.removeListener('SIGTERM'"in host and 'bounded-reap'in host,'Inherited owned-session bounded timeout/group cleanup, no unrelated process search')
 need("await mkdir(path,{mode:0o700})"in durable and 'constants.O_EXCL|constants.O_NOFOLLOW'in durable and "await fd.sync()"in durable,'Exclusive0700 owned output, individual exclusive nofollow synced writes')
 need("need(v.outputRoot===v.parentOutputRoot+'/jobs/'+v.arm"in worker and "local===item.path&&!names.has(local)"in parent,'Exact owned arm roots and no aliases/other-worker reused index rows')
 need("await regular(NODE,{maxBytes:128*1024*1024})"in worker and "await realpath(process.execPath)===NODE.path"in worker and "!key.startsWith('NAPI_RS_')"in worker,'Pinned plain Node executable and no binding/loader overrides')
 need(worker.index('await recheck();')<worker.index('await DurableOutput.create(v.outputRoot)')<worker.index('session=await loadControlSession(v.artifact)'),'Private critical/oracle/cases proof before fresh output and generated module load')
 need(transport.index("const raw=await write(name+'-raw.json'")<transport.index("need(typeof value==='string'")<transport.index('parsed=JSON.parse(value)'),'Full typed raw return persisted before type/JSON/semantic assertions')
 need("await write(name+'-throw.json'"in transport and "kind:'opaque',propertiesRead:false"in transport,'Throws/unexpected opaque values retained without property reads')
 need("await write(name+'-counterexample.json'"in transport and "throw new Error('ERR_COST_JCO_CORRECTNESS: exact mismatch"in transport,'Actual/expected mismatch data saved before compact error')
 need("for(let index=0;index<30;index++)"in worker and "for(const base of[30,60,90])for(let repeat=0;repeat<2;repeat++)"in worker and "await call('checkpoint',[]"in worker,'Actual30 setup/control×3 adjacent pair/checkpoint schedule')
 need(2+30*(1+3*2+1)==242 and 30*3*2==180 and 3*242==726 and 3*180==540,'Independent schedule arithmetic242/180 perarm and726/540 total')
 need("['identity','setup','batch','checkpoint'].includes(name)"in loader and "args[0]>=30&&args[0]<120&&args[1]===1"in loader and "args[0]<30"in loader,'Finite control-only loader surface, setup0..29/batch30..119/N1; primary codec batches refused')
 need("Number.isSafeInteger(value)&&value>=0&&value<=0xffffffff&&!Object.is(value,-0)"in loader and "args.length===arity[name]"in loader,'Exact typed u32 scalar/arity, no coercion or negative-zero fallback')
 need("['component','glue','core','dts','wit','transpileMetadata','packageJson']"in loader and "await regular(parserRow)"in loader and "validatePackageBytes"in loader,'Unchanged actual seven artifact descriptors, parser identity and ESM package boundary')
 need("await import(pathToFileURL(rows.glue.path).href)"in loader and "./codec_cost.core.wasm"in loader and "topLevelInitializationAwaited:true"in loader,'Actual relative core ESM/TLA loading, not invented instantiate API')
 need("await recheck();"in loader and "await session.recheck();await recheck();await output.recheck()"in worker,'Loader artifact checks before/after import and final worker audits')
 need("counts.codecCalls===0&&counts.controlOperations===180"in worker and "counts.publicFunctionEntries===242"in worker and "records.length===242"in worker,'Final actual observable raw/counter/cardinality assertions')
 need("thrownType:typeof error"in worker and "postFailureSourceAuditPassed:sourceAudit"in worker and "postFailureSourceAuditPassed:sourceAudit"in parent,'Failure partial data retained and source/artifact audit attempted; no failed-session resume')

 guest=(G/'runtime.mjs').read_text();controls=(G/'controls.mjs').read_text();contract_source=(G/'contract.mjs').read_text();start=guest.index("if(selected.kind!=='codec')");end=guest.index('\n  let aggregateFNV',start);branch=guest[start:end]
 need('controlOperations++'in branch and 'controls[selected.kind](active.window.input)'in branch and 'invoke('not in branch and 'provider.methods'not in branch,'Actual unchanged guest control branch avoids provider invoke and increments control counter')
 need('primary:cases[index%30]'in contract_source and "index<30?'codec':index<60?'consumeInput':index<90?'copyInputAndConsume':'harnessNoCodec'"in contract_source,'Actual exact control ID modulo30/kind mapping')
 need("const copied=Buffer.from(input)"in controls and 'fnv:consumeFNV1a(copied),copies:1,codecCalls:0'in controls and 'tag:2166136261,copies:0,codecCalls:0'in controls,'Source-coupled copy/consume/harness results; not heap inspection')
 prepare=guest[guest.index(' function prepare('):guest.index(' function setup(')]
 need('fixtureBytes('in prepare and 'stageRecord(found)'in prepare and 'invoke('not in prepare and 'provider.methods'not in prepare,'All30 setups copy raw or pre-reviewed encoded bytes without codec decoding')
 need("const primary=index%30"in collector and "wanted.controlOperations++"in collector and "this.#active?.row.index===primary"in collector,'Collector ties every control to exact active setup and advances only control/batch entries')
 need("bytesConsumed:input.length,fnv:consumeFNV1a(input)"in collector and "declaredInputBytes:input.length,tag:2166136261"in collector and "this.#prior=null"in collector,'Exact result/FNV/length and expected retained-state checks')
 need('matchesSetupFNV:true,sentinelsUnchanged:true'in collector and 'no independent guest-heap byte read'in worker and 'internalCopyOwnershipInspected:false'in worker,'Checkpoint/copy limits explicitly remain reported source-coupled evidence')
 scope=data(C/'scope.json');need(scope['perArmRawReturns']==242 and scope['totalRawReturns']==726 and scope['totalControlOperations']==540 and scope['totalDistinctArmControlCases']==270,'Declared fixed counts match actual source schedule')
 need(scope['controlRootAuthority']is None and scope['controlSourcePeer']is None and scope['actualControlsExecutedByPreparation']==0,'New action/source slots remain null and actual preparation controls0')
 template=data(C/'root-authority.template.json');need(template['actionAllowed']is False and template['controlSourceIndexSha256']is None and template['sourceIndependentReview']is None and template['ordinaryGuestControlCallsAllowed']is False,'Checked-in Root action template refuses; new source/peer authority absent')
 for k in ['codecCallsAllowed','nodeCodecCallsAllowed','observeStageValidateAllowed','wasmtimeAllowed','pilotOrTimingAllowed','operationalAdmission','runtimeAcceptanceClaim','metadataProjection']:need(template[k]is False,'Closed future scope flag '+k)
 source_evidence=data(C/'evidence/source-results.json');pure=data(C/'evidence/pure-results.json');syntax=data(C/'evidence/syntax-results.json')
 need(source_evidence['checks']==206 and pure['checks']==127,'Authenticated owner206 data/127 pure checks, not rerun by reader')
 need(syntax['passed']is True and syntax['checks']==7 and len(syntax['nodeRows'])==6 and all(r['rawExitCode']==0 and '--check'in r['command']for r in syntax['nodeRows'])and syntax['pythonAstParseOnly']is True and syntax['guestWorkerProviderCodecOrOwnerActions']is False,'Stored7 parse-only checks, not module/worker actions')
 need(not Path('/private/tmp/starling-node-compat/zlib-cost-jco-control-correctness-v1').exists(),'Future owned output absent at source inspection')
 # Capture the actual new local module edges as source/data, without importing.
 edges=[]
 for name in ['admission.mjs','run.mjs','worker.mjs','loading.mjs','collector.mjs']:
  text=(C/name).read_text()
  for spec in re.findall(r"(?:from\s+|import\s*\()(['\"])([^'\"]+)\1",text):
   target=spec[1]
   if target.startswith('.'):
    resolved=(C/target).resolve();need(resolved.is_file(),'Actual new literal loader/helper path exists '+target);row(resolved);edges.append(dict(fromFile=name,specifier=target,resolvedPath=str(resolved)))
 result_out=dict(schemaVersion=1,state='INDEPENDENT_ZLIB_COST_JCO_CONTROL_SOURCE_REVIEW_PASSED_V1',controlSourceIndexSha256=PIN,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,
  indexedSourceFilesRehashed=25,originalInputRowsRehashed=159,uniqueInputsRehashed=len(seen),priorSourceIndexSha256=prerequisite['correctnessSource']['sha256'],donorSourceIndexSha256=prerequisite['donorSource']['sha256'],
  priorFullCorrectnessReviewIndexSha256=prerequisite['review']['index']['sha256'],priorFullCorrectnessResultSha256=prerequisite['review']['result']['sha256'],priorFullCorrectnessContractSha256=prerequisite['review']['contract']['sha256'],priorGenuineRootAuthoritySha256=contract['requiredExactDescriptors']['rootAuthority']['sha256'],
  priorFullCorrectnessReviewFilesRehashed=len(review['files']),priorControlOperations=0,prior228WorkersReusedAsNewControls=False,originalGuestProviderNativeComponentAndOldWorkerSourcesUnmodified=True,exactAfterimages=2,exactRecordedReversals=10,
  futureSchedule=dict(arms=['native-on','fflate-on','fflate-off'],freshOwnedSessions=3,setupCasesPerArm=30,controlRanges=[[30,59],[60,89],[90,119]],operationsPerBatch=1,adjacentRepetitions=2,rawReturnsPerArm=242,controlOperationsPerArm=180,totalRawReturns=726,totalControlOperations=540,distinctArmControlCases=270,expectedCodecCalls=0),
  intendedEvidence='Actual control-only public return/state/counter checks over existing reviewed components. No completed actual control result is claimed by source review.',
  evidenceLimits=scope['evidenceLimits'],rawBeforeTypeJsonAndSemanticAssertions=True,ownedDeadlineMs=600000,maxPipeBytes=16777216,startDiskBytes=2147483648,perWorkerDiskBytes=838860800,
  completePriorNativeToolArtifactPreflightReusedReadOnlyWithGenuineAuthority=True,completePriorOutputRecheckImplementedNotInvokedByReviewer=True,newPhysicalModuleEdges=len(edges),
  ownerEvidence=dict(pureChecks=127,dataChecks=206,syntaxRecords=syntax,actualControlActionsInvoked=False,peerReranAnyOwnerChecks=False),
  futureRootActionAuthority=None,futureSourcePeerAuthority=None,actualWorkerOrComponentControlsExecuted=False,ordinaryCodecExecuted=False,wasmtimeExecuted=False,pilotTimingAllowed=False,operationalAdmission=False,runtimeAcceptanceClaim=False,
  limitations=['Source-only; actual three fresh sessions and all726 raw returns remain unexecuted.','600s per worker and disk/pipe guards are finite operational bounds, not adequate-time/space guarantees.','Reported FNV/sentinels/copy count do not establish full private guest heap or internal copy ownership.','Old full correctness is a prerequisite, not evidence that the new controls ran.','Old350 cost components/natives remain distinct from later355/crypto native artifacts.'])
 write('rehashed-inputs.json',[seen[k]for k in sorted(seen)]);write('literal-module-edges.json',edges);write('static-checks.json',dict(passed=True,checks=len(checks),details=checks,ownerModulesImportedOrExecuted=False));write('results.json',result_out)
 print(json.dumps(dict(state=result_out['state'],uniqueInputs=len(seen),checks=len(checks),moduleEdges=len(edges))))
if __name__=='__main__':main()
