"""Independent retained-data/source failure audit; no owner functions/actions."""
import hashlib,json,stat
from pathlib import Path
P=Path(__file__).resolve().parent
Z=P.parent
C=Z/'cost-jco-control-correctness-candidate-v1'
PEER=Z/'independent-cost-jco-control-source-review-v1'
D=Z/'cost-jco-correctness-candidate-v2'
OUT=Path('/private/tmp/starling-node-compat/zlib-cost-jco-control-correctness-v1')
seen={}
def need(v,m):
 if not v:raise AssertionError(m)
def row(p,e=None):
 p=Path(p);s=p.lstat();need(stat.S_ISREG(s.st_mode),'ordinary file '+str(p));h=hashlib.sha256()
 with p.open('rb')as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 r=dict(path=str(p),sha256=h.hexdigest(),bytes=s.st_size)
 if e:need(all(r[k]==e[k]for k in ('sha256','bytes')),'exact tuple '+str(p))
 seen[str(p)]=r;return r
def data(p):return json.loads(Path(p).read_bytes())
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
def indexed(root,pin):
 need(row(root/'index.json')['sha256']==pin,'exact index');ix=data(root/'index.json')
 for r in ix['files']:row(root/r['path'],r)
 return ix
def main():
 root_path=Z/'cost-jco-control-v1-failure-root-results.json';root_row=row(root_path,dict(sha256='1e1b07e4def91bafca436817e46c2d430d581cb46d04289e2af935803b956a38',bytes=3411));root=data(root_path)
 for key in ['actualTerminal','externalLaunchSource','rootAuthority','config','controlSourceIndex','failure']:
  r=root[key];row(r['path'],r)
 for r in root['independentSourceReview'].values():row(r['path'],r)
 for r in root['partialFiles']:row(r['path'],r)
 indexed(C,'ad0d651fdb8653a8a708514131bad52cf8cc05b657c6cefd92604aca3c3f7a23')
 indexed(PEER,'d6f72a454fd7c8def6042827eb3a139312bb89a996db1d32e224d24e2467bb58')
 donor=indexed(D,'d2516c934df3fa8f3ecd58b187cc2bc0f28fab996ab97ada0854e4988d9befeb')
 terminal=data(root['actualTerminal']['path']);need(terminal['pid']==91129 and terminal['rawExitCode']==1 and terminal['timeout']is False and terminal['deadlineSeconds']==2700,'Root retained parent1/no timeout, not observed by reviewer')
 for key in ['stdout','stderr']:r=terminal[key];row(r['path'],r)
 need(Path(terminal['stdout']['path']).stat().st_size==0,'actual parent stdout empty')
 error=Path(terminal['stderr']['path']).read_text();need(len(error.encode())==1052 and 'ENOENT'in error and "lstat '"+str(OUT/'processes')+"'"in error,'exact1052-byte processes ENOENT diagnostic')
 need('at async ordinary ('in error and 'durable-host.mjs:13:21'in error and 'durable-host.mjs:43:56'in error and 'run.mjs:23:17'in error,'exact caller/callee stack attribution')
 config=data(root['config']['path']);authority=data(root['rootAuthority']['path'])
 need(config['controlSourceIndexSha256']==authority['controlSourceIndexSha256']=='ad0d651fdb8653a8a708514131bad52cf8cc05b657c6cefd92604aca3c3f7a23'and config['rootAction']==root['rootAuthority'],'actual exact source/config/Root authority crossbinding')
 need(authority['actionAllowed']is True and authority['ordinaryGuestControlCallsAllowed']is True and authority['codecCallsAllowed']is False,'actual permission existed; actual execution still failed before controls')
 need(authority['sourceIndependentReview']==root['independentSourceReview'],'old source PASS exact authority input, not actual execution pass')
 expected={str(Path(r['path']).relative_to(OUT))for r in root['partialFiles']};need(expected=={'failure.json','descriptors/native-on.json'},'exact two declared partial files')
 actual=set();directories=[]
 for p in OUT.rglob('*'):
  need(not p.is_symlink(),'no partial symlink')
  if p.is_file():actual.add(str(p.relative_to(OUT)));row(p)
  elif p.is_dir():directories.append(str(p.relative_to(OUT)));need(stat.S_IMODE(p.stat().st_mode)==0o700,'owned partial directory mode700')
  else:raise AssertionError('non-ordinary partial member')
 need(actual==expected and set(directories)=={'jobs','descriptors'},'exact partial physical membership')
 need(not(OUT/'processes').exists()and not(OUT/'jobs/native-on').exists(),'no process-log directory or worker output root')
 for n in ['results.json','index.json','completion.json']:need(not(OUT/n).exists(),'no parent final '+n)
 failure=data(OUT/'failure.json');need(failure==dict(schemaVersion=1,state='CONTROL_ACTION_FAILED_NOT_ACCEPTED',thrownType='object',partialRawOutputsRetained=True,completedOrigins=[],postFailureSourceAuditPassed=True,timingAllowed=False),'full exact failure record, no completed origins')
 child=data(OUT/'descriptors/native-on.json');need(child['state']=='PARENT_AUDITED_UNTIMED_ZLIB_CONTROL_WORKER_V1'and child['arm']=='native-on'and child['controlSourceIndexSha256']==config['controlSourceIndexSha256'],'first arm descriptor retained but not launched')
 need(child['parentOutputRoot']==str(OUT)and child['outputRoot']==str(OUT/'jobs/native-on')and len(child['criticalFiles'])==530,'actual intended private output/context and530 source rows')
 for r in child['criticalFiles']:row(r['path'],r)
 for key in ['oracle','cases']:row(child[key]['path'],child[key])
 for key,r in child['artifact'].items():
  if isinstance(r,dict):row(r['path'],r)
 contract=data(Z/'independent-cost-jco-correctness-v3-results-review-v1/result-contract.json')
 need(child['artifact']['component']==contract['requiredComponents']['native-on']and child['oracle']==contract['requiredExactDescriptors']['oracle'],'descriptor reuses actual reviewed component/oracle tuple; not new runtime evidence')
 parent=(C/'run.mjs').read_text();host=(D/'durable-host.mjs').read_text();admit=(C/'admission.mjs').read_text()
 need("await mkdir(join(output.root,'jobs'),{mode:0o700})"in parent and "mkdir(join(output.root,'processes')"not in parent,'actual parent creates jobs only')
 need(parent.index('await controlPreflight(options)')<parent.index('await admitted.recheck()')<parent.index('await DurableOutput.create(')<parent.index("write('descriptors/'")<parent.index('await runOwnedCommand('),'descriptor creation follows successful read-only prior admission/recheck and precedes lifecycle helper')
 ordinary=host[host.index('async function ordinary('):host.index('export async function persistFile(')]
 need('let current=dirname(target)'in ordinary and 'await lstat(current)'in ordinary and 'mkdir('not in ordinary,'actual helper requires ordinary existing ancestor, does not make directory')
 need(host.index("stdoutPath=await ordinary(output,prefix+'.stdout.txt')")<host.index('await persistFile({output,write,path:launchPath')<host.index('child=spawn('),'missingdir fails before any owned launch record or spawn')
 need("prefix=join(output,'processes',name)"in host and "await correctnessPreflight("in admit and "rootAction:completed.oldAuthority"in admit,'genuine existing lifecycle and read-only preflight path, no authority rewrite')
 need(parent.index('await runOwnedCommand(')<parent.index('const workerRoot=value.outputRoot')<parent.index('origins.push('),'no completed origin or worker read reachable after this failure')
 need("try{await admitted.recheck();sourceAudit=true;}catch{}"in parent and 'postFailureSourceAuditPassed:sourceAudit'in parent,'actual failure true audit field means read-only source/artifact recheck, not guest success')
 launch_source=Path(root['externalLaunchSource']['path']).read_text();need('desc(node)'in launch_source and 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'in launch_source,'Root launch authenticates pinned Node before parent call')
 need(row(terminal['argv'][0])['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0','actual current pinned Node bytes, not executed by reviewer')
 correction=dict(schemaVersion=1,state='REQUIRED_FRESH_CONTROL_SOURCE_DIRECTORY_CORRECTION_CONTRACT',finding='COST-CONTROL-PARENT-DIRECTORY-M1',oldSourceIndexSha256=config['controlSourceIndexSha256'],oldSourcePeerIndexSha256=root['independentSourceReview']['index']['sha256'],
  requiredSourceDelta='Inside the new exclusive owned parent output, create processes as an ordinary0700 directory before calling the unchanged runOwnedCommand, alongside jobs. Do not bypass or weaken ordinary() or durable lifecycle checks.',
  requiredLineage=['Fresh immutable versioned source/afterimage and exact reversible changes.','Fresh output namespace, config and action-specific Root authority; never resume/reuse failed v1 output.','Original guest/provider/native/components/oracle/case payloads, control ranges/counters/counts, typed raw-before-assert path and immutable old228 schedule unchanged.','Retain all v1 source/authority/partial/raw/failure/source-review packets.'],
  requiredRegression='Source/data proof plus separately authorized tiny benign owned-child missingdir-fail/prepared-dir-success regression, exercising the genuine durable-host helper and writer. Old failure before launch/spawn, new raw0+clean-owned-group+launch/pipes/terminal/file membership must be explicit. It is not a guest/control result.',
  correctionSourceIndex=None,correctionIndependentPeer=None,newRootActionAuthority=None,newOutputRoot=None,reviewerMayRunRegression=False,guestControlOrCodecRuntimeEvidenceRequiredAfterSourceApproval=True,
  unsafeAlternativeRejected='No recursive arbitrary-path creation inside the general helper, fabricated terminal, swallowed ENOENT, old-output reuse, metadata projection or pass relabelling.')
 result=dict(schemaVersion=1,state='INDEPENDENT_ZLIB_COST_JCO_CONTROL_V1_PRE_WORKER_FAILURE_VERIFIED',failureAuditPassed=True,rootFailureReceipt=root_row,
  rootReportedProcess=dict(sessionId=54743,pid=terminal['pid'],rawExitCode=1,timeout=False,elapsedSeconds=terminal['elapsedSeconds'],observedByThisReader=False),
  sourceIndexSha256=config['controlSourceIndexSha256'],sourcePeerIndexSha256=root['independentSourceReview']['index']['sha256'],finding='COST-CONTROL-PARENT-DIRECTORY-M1',
  actualPartialFiles=sorted(actual),actualPartialDirectories=sorted(directories),privateDescriptorCriticalRowsRehashed=530,completedOrigins=[],postFailureReadOnlySourceAuditPassed=True,
  readOnlyPriorPreflightHelpersExecuted=True,ownedWorkersLaunched=0,ownedLaunchRecordsCreated=0,generatedGuestModulesImported=0,guestControlsExecuted=0,guestCodecCallsExecuted=0,newControlResultsOrCompletionPublished=False,
  failureCause='Parent omits processes0700; inherited durable-host ordinary() lstat of processes fails at the first native-on stdout-path validation before launch record or spawn.',
  priorSourceReviewQualification='The old d6f SOURCE PASS missed this caller/callee directory precondition. It remains immutable; no runtime readiness/control success is inferred from it.',
  contraryFieldQualifications=['parentAuditedActualComponents=true is retained descriptor provenance after genuine preflight, not proof of a worker/module/control call.','partialRawOutputsRetained=true covers the bytes actually obtained; there were no guest returns to retain.','postFailureSourceAuditPassed=true reports the genuine read-only recheck, not control success.','Root permitted new guest controls, but no new worker/control call was reached.'],
  priorCompletedCorrectnessOrWasmtimeProofInvalidated=False,reviewerReadHashSourceOnly=True,ownerTestsHelpersGuardsLoadersPreflightNodeWorkersGuestsCodecsNativeOrHostsExecutedByReviewer=False,
  uniqueFilesRehashed=len(seen),correctionRequired=True,operationalAdmission=False,runtimeAcceptanceClaim=False,timingAllowed=False)
 write('required-correction-contract.json',correction);write('rehashed-inputs.json',[seen[k]for k in sorted(seen)]);write('results.json',result)
 print(json.dumps(dict(state=result['state'],files=len(seen),partialFiles=len(actual),workers=0)))
if __name__=='__main__':main()
