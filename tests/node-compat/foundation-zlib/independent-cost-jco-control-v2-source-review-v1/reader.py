"""Read/hash/source and retained benign-data review only. No owner imports."""
import difflib,hashlib,json,re,stat
from pathlib import Path
P=Path(__file__).resolve().parent;Z=P.parent
C=Z/'cost-jco-control-correctness-candidate-v2';D=Z/'cost-jco-control-correctness-candidate-v1'
H=Z/'independent-cost-jco-control-v1-failure-review-v1';S=Z/'independent-cost-jco-control-source-review-v1'
PIN='3b56608315d48d92dd8b72c9e7c73a3c179d0d2fefb9555a79cd216be45d1ff1'
seen={};checks=[]
def need(v,m):
 if not v:raise AssertionError(m)
 checks.append(m)
def row(p,e=None):
 p=Path(p);s=p.lstat();need(stat.S_ISREG(s.st_mode),'ordinary file '+str(p));h=hashlib.sha256()
 with p.open('rb')as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 d=dict(path=str(p),sha256=h.hexdigest(),bytes=s.st_size)
 if e:need(all(d[k]==e[k]for k in ('sha256','bytes')),'exact tuple '+str(p))
 seen[str(p)]=d;return d
def data(p):return json.loads(Path(p).read_bytes())
def write(n,d):(P/n).write_text(json.dumps(d,indent=2)+'\n')
def indexed(base,pin):
 need(row(base/'index.json')['sha256']==pin,'exact index '+str(base));d=data(base/'index.json')
 for r in d['files']:row(base/r['path'],r)
 return d
def main():
 own=indexed(C,PIN);need(len(own['files'])==29,'29 final source/evidence members')
 inputs=data(C/'input-freeze.json');need(len(inputs['files'])==190,'190 original input references')
 for r in inputs['files']:row(r['path'],r)
 indexed(D,'ad0d651fdb8653a8a708514131bad52cf8cc05b657c6cefd92604aca3c3f7a23')
 indexed(S,'d6f72a454fd7c8def6042827eb3a139312bb89a996db1d32e224d24e2467bb58')
 indexed(H,'534f2d86cb10776600089143609dc96c63c2e0a02bd8a6e3376f3ef9111429a5')
 lineage=data(C/'lineage.json')
 for n in ['originalSourceIndex','originalSourcePeerIndex','rootFailure','requiredCorrection']:row(lineage[n]['path'],lineage[n])
 for d in lineage['failureReview'].values():row(d['path'],d)
 need(data(lineage['failureReview']['result']['path'])['finding']=='COST-CONTROL-PARENT-DIRECTORY-M1'and row(lineage['requiredCorrection']['path'])['sha256']=='a0060ad6927ad1b934bab9c47b70cb877d6f2e03641829f520271a7460349b00','Actual prior failure and exact required correction contract')
 derivation=data(C/'source-derivations.json');need(len(derivation['files'])==2 and sum(len(r['edits'])for r in derivation['files'])==10,'Two afterimages/ten exact edits')
 patch=''
 for r in derivation['files']:
  row(r['origin']['path'],r['origin']);before=Path(r['origin']['path']).read_text();after=(C/r['afterimage']).read_text();current=before
  need(hashlib.sha256(after.encode()).hexdigest()==r['afterSha256'],'actual afterimage digest')
  for e in r['edits']:
   need(current.count(e['old'])==e['count']==1,'one exact edit occurrence');current=current.replace(e['old'],e['new']);need(current.index(e['new'])==e['afterOffsetAtEdit'],'exact after offset at edit')
  need(current==after,'whole forward afterimage')
  for e in reversed(r['edits']):
   at=e['afterOffsetAtEdit'];need(current[at:at+len(e['new'])]==e['new'],'exact reverse offset slice');current=current[:at]+e['old']+current[at+len(e['new']):]
  need(current==before,'whole reverse to immutable v1 source')
  patch+=''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+Path(r['origin']['path']).name,tofile='b/'+r['afterimage']))
 need(patch.encode()==(C/'control-v2.UNAPPLIED.patch').read_bytes(),'exact unapplied patch matches all ten edits')
 parent=(C/'run.mjs').read_text();admit=(C/'admission.mjs').read_text();oldworker=(D/'worker.mjs').read_text()
 need("await mkdir(join(output.root,'jobs'),{mode:0o700});await mkdir(join(output.root,'processes'),{mode:0o700});"in parent and parent.index("mkdir(join(output.root,'processes')")<parent.index('await runOwnedCommand('),'M1 actual caller prepares ordinaryprocesses0700 before unchanged lifecycle')
 need("args:[join(HERE,'../cost-jco-control-correctness-candidate-v1/worker.mjs')"in parent and not(C/'worker.mjs').exists(),'Direct immutable old worker reused as source, not old pass/output')
 need("ROOT_REVIEWED_ZLIB_COST_JCO_CONTROL_CORRECTNESS_V2"in admit and "INDEPENDENT_ZLIB_COST_JCO_CONTROL_SOURCE_REVIEW_PASSED_V2"in admit and '/zlib-cost-jco-control-correctness-v2' in admit,'Distinct V2 source/Root/peer/output identities')
 need(admit.index('const original=await sourceIndex(')<admit.index('const peer=await indexed(authority.sourceIndependentReview')<admit.index("await import('../cost-jco-correctness-candidate-v3/admission.mjs')"),'Own/original/failure/peer proof required before genuine prior guard import')
 need("await original.recheck();await failure.recheck();await regular(lineage.rootFailure);await regular(lineage.requiredCorrection)"in admit and '[...own.rows,...original.rows,...frame.criticalSourceFiles,rootRow]'in admit,'Donor/failure/own rechecks and worker critical tuple preserved')
 need("rootAction:completed.oldAuthority"in admit and 'priorControlOperations:0'in parent and "UNTIMED_ZLIB_JCO_CONTROLS_COMPLETE_PENDING_INDEPENDENT_REVIEW_V2"in parent,'Old genuine235d guard carrier not changed; new parent completion labels only')
 need("CONTROL_ARM_COMPLETE_EXTERNAL_OWNED_ZERO_REQUIRED_V1"in parent and "controlSourceIndexSha256:v.controlSourceIndexSha256"in oldworker and "sourceIndexSha256:v.controlSourceIndexSha256"in oldworker,'Unchanged per-armV1 wire schema carries actual new source digest dynamically')
 need("v.outputRoot===v.parentOutputRoot+'/jobs/'+v.arm"in oldworker and "for(let index=0;index<30;index++)"in oldworker and "for(const base of[30,60,90])for(let repeat=0;repeat<2;repeat++)"in oldworker,'Actual old worker accepts new parent-owned root and exact unchanged schedule')
 need((C/'scope.json').read_bytes()==(D/'scope.json').read_bytes()and(C/'prerequisites.json').read_bytes()==(D/'prerequisites.json').read_bytes(),'Exact old scope/prerequisite bytes unchanged')
 need('records.length===242' in oldworker and 'counts.codecCalls===0' in oldworker and 'counts.controlOperations===180' in oldworker and 2+30*(1+3*2+1)==242,'242/180 perarm726/540 total arithmetic unchanged')
 need(parent.index('for(const path of registered)')<parent.index('checkOwned(status)') and 'await admitted.recheck();await output.recheck()'in parent,'Original raw terminal/pipes-before-check and post-proof/output audits retained')
 template=data(C/'root-authority.template.json');need(template['state']=='ROOT_REVIEWED_ZLIB_COST_JCO_CONTROL_CORRECTNESS_V2'and template['actionAllowed']is False and template['controlSourceIndexSha256']is None and template['sourceIndependentReview']is None and template['ordinaryGuestControlCallsAllowed']is False,'Fresh Root/peer action fields unissued, V1 authority not accepted')
 need(all(template[n]is False for n in ['codecCallsAllowed','nodeCodecCallsAllowed','observeStageValidateAllowed','wasmtimeAllowed','pilotOrTimingAllowed','operationalAdmission','runtimeAcceptanceClaim','metadataProjection']),'No codec/WT/pilot/timing/admission expansion')
 # Decode authenticated actually executed BENIGN evidence; never rerun test.
 E=C/'evidence/benign-actual';reg=data(E/'results.json');missing=data(E/'missing-observed.json');helper=data(E/'prepared-helper-return.json');capture=data(E/'prepared-raw-capture.json');terminal=data(E/'prepared/processes/benign.terminal.json');launch=data(E/'prepared/processes/benign.launch.json')
 need(reg['state']=='BENIGN_GENUINE_LIFECYCLE_DIRECTORY_REGRESSION_PASSED'and reg['checks']==8 and reg['benignHostChildrenStarted']==1,'Stored8 actual benign lifecycle checks/one child, not controls')
 need(all(reg[n]is False for n in ['oldControlActionInvoked','newControlActionInvoked','preflightInvoked','guestInvoked','providerOrCodecInvoked']),'Regression explicitly excludes real control/preflight/guest/codec')
 need(missing==reg['records'][0]and missing['thrown']is True and missing['code']=='ENOENT'and missing['path']==reg['root']+'/missing/processes'and missing['registeredFiles']==missing['collectedFiles']==[]and missing['directoryEntries']==['jobs'],'Full missingdir failure data before expected-failure checks')
 need(missing['noChildClaimBasis']=='source ordering: ordinary() precedes launch record and spawn; no runtime spawn instrumentation','No-child claim explicitly source-order based')
 need(terminal['status']==0 and terminal['signal']is None and terminal['spawnError']is None and terminal['closed']is True and terminal['ownedGroupGone']is True and terminal['terminalExitZeroObserved']is True and terminal['timedOut']is False and terminal['errors']==[],'Actual benign terminal raw0/clean group, no fabricated pass')
 expected_stdout=b'BENIGN_CONTROL_DIRECTORY_STDOUT\n';expected_stderr=b'BENIGN_CONTROL_DIRECTORY_STDERR\n'
 for name,expected in [('stdout',expected_stdout),('stderr',expected_stderr)]:
  leaf=E/'prepared/processes'/('benign.'+name+'.txt');need(leaf.read_bytes()==expected and len(expected)==32,'Whole benign32-byte '+name);need(row(leaf)['sha256']==terminal[name]['sha256']==capture[name+'Sha256']and terminal[name]['bytes']==32,'Actual raw benign stream hashes '+name);row(terminal[name]['path'],terminal[name]);need(Path(terminal[name]['path']).read_bytes()==expected,'Original scratch benign bytes '+name)
 need(row(E/'prepared/processes/benign.terminal.json')['sha256']==capture['terminalSha256']==reg['records'][1]['terminal']['sha256'],'Actual terminal copy/control hash')
 row(reg['records'][1]['terminal']['path'],reg['records'][1]['terminal'])
 need(launch['executable']==terminal['executable']==helper['executable']and launch['args']==terminal['args']==helper['args']and terminal['args'][0]=='-e'and 'BENIGN_CONTROL_DIRECTORY_STDOUT'in terminal['args'][1]and 'BENIGN_CONTROL_DIRECTORY_STDERR'in terminal['args'][1],'Actual benign argv has no worker, guest, codec or preflight')
 need(terminal['pid']==helper['pid']==94171 and helper['stdout']==expected_stdout.decode()and helper['stderr']==expected_stderr.decode()and helper['ownedGroupGone']is True,'Whole actual helper return matches terminal/raw bytes')
 prepared_files={r['path']:r for r in reg['records'][1]['files']};need(set(prepared_files)=={'processes/benign.launch.json','processes/benign.terminal.json','processes/benign.stdout.txt','processes/benign.stderr.txt'},'Exact4 launch/pipes/terminal membership')
 for name,r in prepared_files.items():row(E/'prepared'/name,r);row(Path(reg['root'])/'prepared'/name,r)
 test=(C/'test-directory-prerequisite.mjs').read_text();need("import {DurableOutput} from '../cost-jco-correctness-candidate-v2/durable.mjs'"in test and "import {runOwnedCommand} from '../cost-jco-correctness-candidate-v2/durable-host.mjs'"in test and "await mkdtemp("in test and "for(const prepared of [false,true])"in test,'Regression uses genuine unchanged writer/helper and fresh scratch for both conditions')
 need(test.index("writeFile(join(root,'prepared-helper-return.json')")<test.index('checkOwnedTerminal(result)')and test.index("writeFile(join(root,'missing-observed.json')")<test.index("ck(error?.code==='ENOENT'"),'Actual raw/helper and missing-error records stored before assertions')
 evidence=data(C/'results.json');syntax=data(C/'evidence/syntax.json');need(evidence['sourceDataChecks']==79 and evidence['parseChecks']==5 and evidence['actualBenignDirectoryChecks']==8 and syntax['noMainsInvokedBySyntax']is True and len(syntax['records'])==5,'Stored79data/5parse/8benign evidence scopes')
 need(all(r.get('exitCode',0)==0 for r in syntax['records']),'Stored parse0 statuses')
 need(not Path(template['outputRoot']).exists(),'Fresh v2 actual control output absent at source inspection')
 oldpartial=Path('/private/tmp/starling-node-compat/zlib-cost-jco-control-correctness-v1');need({str(q.relative_to(oldpartial))for q in oldpartial.rglob('*')if q.is_file()}=={'failure.json','descriptors/native-on.json'},'Failed v1 partial membership remains unchanged')
 outcome=dict(schemaVersion=1,state='INDEPENDENT_ZLIB_COST_JCO_CONTROL_SOURCE_REVIEW_PASSED_V2',controlSourceIndexSha256=PIN,sourceOnly=True,sourceReviewPassed=True,ownerActionsInvoked=False,
  indexedSourceFilesRehashed=29,originalInputRowsRehashed=190,uniqueInputsRehashed=len(seen),exactAfterimages=2,exactReversibleEdits=10,resolvedFinding='COST-CONTROL-PARENT-DIRECTORY-M1',
  originalSourceIndexSha256=lineage['originalSourceIndex']['sha256'],originalSourcePeerIndexSha256=lineage['originalSourcePeerIndex']['sha256'],actualFailureReviewIndexSha256=lineage['failureReview']['index']['sha256'],requiredCorrectionSha256=lineage['requiredCorrection']['sha256'],
  originalWorkerLoaderCollectorAndGuestPayloadsUnchanged=True,original228ScheduleAndCompletedControlZeroProofsUnchanged=True,processesOrdinary0700CreatedBeforeGenuineLifecycle=True,
  freshOutputRoot=template['outputRoot'],rootAuthorityState=template['state'],futureSourcePeerAuthority=None,futureRootActionAuthority=None,
  unchangedSchedule=dict(arms=3,primarySetupsPerArm=30,controlRangeBases=[30,60,90],operationsPerCall=1,adjacentRepetitions=2,rawReturnsPerArm=242,controlOperationsPerArm=180,totalRawReturns=726,totalControlOperations=540,distinctArmControlCases=270,expectedCodecCalls=0),
  storedActualBenignRegression=dict(checks=8,benignChildrenStarted=1,pid=94171,preparedRawStatus=0,ownedGroupGone=True,stdoutBytes=32,stderrBytes=32,missingDirError='ENOENT before launch/spawn by authenticated source ordering',rawHelperAndErrorCapturedBeforeAssertions=True,originalScratchAndCopiedTextEvidenceRehashed=True,reviewerReran=False,notGuestOrControlEvidence=True),
  ownerEvidence=dict(dataChecks=79,parseChecks=5,sourceAndBenignChecksNotRerunByReviewer=True),
  actualNewControlWorkersOrGuestControlsExecuted=False,reviewerTestsHelpersGuardsPreflightNodeWorkersControlsCodecsGuestNativeOrHostActionsInvoked=False,
  operationalAdmission=False,runtimeAcceptanceClaim=False,pilotTimingAllowed=False,
  limitations=['SOURCE correction plus retained tiny benign lifecycle data only; actual three component sessions/726 controls remain unexecuted.','Per-armV1 markers describe the unchanged worker schema; actual new source SHA/root/outputs remain dynamic and V2 parent states distinct.','Prior228 correctness/control0 and failed v1 partial data are not new control passes.','600s/16MiB/disk bounds are operational, not completion/space/performance guarantees.','Reported guest FNV/sentinels/copy counters do not provide private heap/internal-copy/GC/reset/reuse proof.'])
 write('rehashed-inputs.json',[seen[k]for k in sorted(seen)]);write('static-and-benign-data-checks.json',dict(passed=True,checks=len(checks),details=checks,reviewerExecutedOwnerCode=False));write('results.json',outcome)
 print(json.dumps(dict(state=outcome['state'],inputs=len(seen),checks=len(checks),benignChecks=8)))
if __name__=='__main__':main()
