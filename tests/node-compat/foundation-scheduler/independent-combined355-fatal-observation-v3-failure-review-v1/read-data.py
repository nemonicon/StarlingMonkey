"""Independent bounded SOURCE/DATA intake, no operational imports or calls."""
from pathlib import Path
import ast,hashlib,json,os,re,stat,subprocess,time
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'combined-native-runtime-candidate-v3'
EXPECTED='54a70237f27aa9f0d1c0d6d0f7766f1575734031c806478017f304d9a73cd424'
rows={};identities={};families={};checks=0
def need(v,m):
 global checks
 if not v:raise AssertionError(m)
 checks+=1
def digest(path):
 h=hashlib.sha256()
 with path.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def descriptor(path):return dict(path=str(path),sha256=digest(path),bytes=path.stat().st_size)
def key(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mode,s.st_nlink,s.st_mtime_ns,s.st_ctime_ns)
def checked(r):
 need(type(r)is dict and type(r['path'])is str and Path(r['path']).is_absolute(),'absolute descriptor')
 p=Path(r['path']);s=p.lstat();need(stat.S_ISREG(s.st_mode)and s.st_size==r['bytes'],'regular exact file')
 if str(p)in rows:
  need(rows[str(p)]==r and identities[str(p)]==key(s),'same descriptor/identity');return p
 need(digest(p)==r['sha256']and key(s)==key(p.lstat()),'full stable SHA '+str(p))
 rows[str(p)]=r;identities[str(p)]=key(s);return p
def read(r):return json.loads(checked(r).read_bytes())
def family(ix):
 if ix['path']in families:need(families[ix['path']]==ix,'same family');return
 v=read(ix);root=Path(ix['path']).parent;names={'index.json'}
 for r in v['files']:
  n=r['path'];need(n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')),'unique member')
  names.add(n);checked(dict(path=str(root/n),sha256=r['sha256'],bytes=r['bytes']))
 paths=list(root.rglob('*'));need(not any(p.is_symlink()for p in paths),'no family symlinks')
 need({p.relative_to(root).as_posix()for p in paths if p.is_file()}==names,'exact whole indexed family')
 families[ix['path']]=ix


if __name__!='__main__':raise SystemExit('Read-only reader is an explicit terminal-bound command')
review_inputs=json.loads((OWN/'review-inputs.json').read_bytes());need(review_inputs.get('actualReaderRunAllowed')is True and review_inputs.get('actualRootResult')is not None,'Original Root terminal/report required before target inspection')
ix=descriptor(SOURCE/'index.json');need(ix['sha256']==EXPECTED,'original caller source');family(ix)
source_inputs=json.loads((SOURCE/'source-inputs.json').read_bytes());refs=json.loads((SOURCE/'references.json').read_bytes())
for r in source_inputs['files']:checked(r)
for r in source_inputs['families']:family(r)
for boundary in source_inputs['boundaries']:
 b=read(boundary['manifest']);need(len(b[boundary['field']])==boundary['expectedRows'],'declared current rows')
 for r in b[boundary['field']]:checked(r)
 for r in b.get(boundary['familyField'],[]):family(r)
package=read(refs['packageInventory'])['package'];base=Path(package['root']);names=set();links={r['path']:r for r in package['links']}
need(len(package['files'])==4889 and len(links)==21 and stat.S_IMODE(base.lstat().st_mode)==0o700,'reviewed private package')
for r in package['files']:
 checked({k:r[k]for k in ['path','sha256','bytes']});p=Path(r['path']);need(p==base/r['relativePath']and stat.S_IMODE(p.lstat().st_mode)==r['mode']and p.lstat().st_nlink==1,'package mode/window');names.add(r['relativePath'])
found=set()
for p in base.rglob('*'):
 n=p.relative_to(base).as_posix()
 if p.is_symlink():
  r=links[n];need(os.readlink(p)==r['target']and str(p.resolve(strict=True))==r['resolvedPath']and p.resolve(strict=True).is_relative_to(base),'private alias');found.add(n)
 elif p.is_file():need(n in names,'package member');found.add(n)
need(found==names|set(links),'whole package member set')
def direct_roles(v):
 if type(v)is dict:
  if set(v)=={'path','sha256','bytes'}:checked(v)
  else:
   for x in v.values():direct_roles(x)
 elif type(v)is list:
  for x in v:direct_roles(x)
root=read(review_inputs['actualRootResult']);direct_roles(root);rp=review_inputs['actualRootResult']
need(rp['sha256']=='bb0d68c83b9ea2d2f0a0d28d5c11ebe8ce11cfcf3b06bce0e59fc57a8295522b'and root['toolObservation']==dict(sessionId=52435,rawExitCode=1),'original failed52435 raw1')
need(root['sourceIndex']==ix and root['state']=='ROOT_OBSERVED_COMBINED355_FATAL_OBSERVATION_UNACCEPTED_V3','unaccepted originalSource54a')
auth=read(root['rootAuthority']);cfg=read(root['config']);inv=read(root['invocation']);direct_roles(inv)
need(auth['state']=='ROOT_REVIEWED_COMBINED355_NATIVE_RUNTIME_PHASE_V3'and auth['phase']==cfg['phase']==auth['fixtureId']==cfg['fixtureId']=='fatal'and auth['sourceIndex']==cfg['sourceIndex']==ix and cfg['rootAuthority']==root['rootAuthority'],'genuine fatal phase/context')
family(auth['sourceIndependentReview']['index']);sp=read(auth['sourceIndependentReview']['result']);need(auth['sourceIndependentReview']['index']['sha256']=='ecd595bc5dc3ad7e0d9130cb7b4b8d3caa45a6cbcb73c0f91f3b3856aaea419b'and sp['state']=='INDEPENDENT_COMBINED355_NATIVE_RUNTIME_SOURCE_REVIEW_PASSED_V3','actual Sourcepeer')
for name in ['expectedFatalCallbackAcceptanceAllowed','current355NativeCallbackDiagnosticAvailable','componentConstructionAllowed','mappingOnlyAllowed','jcoCompilerHelpersAllowed','nodePureOracleAllowed','keyOrCryptoAllowed','nativeBuildAllowed','nativeFreezeAllowed','gcOrFaultActionsAllowed','debugOrUnsafeResetAllowed','timingAllowed','fullClockProfileAcceptance','operationalAdmission','runtimeAcceptanceClaim']:need(auth[name]is False,'no extra acceptance/action '+name)
need(auth['generatedApplicationImportAllowed']is auth['ordinaryGuestExportsAllowed']is auth['stockWasmtimeAllowed']is True,'original bounded disposable work grant')
need(auth['nativeEngine']==refs['nativeEngine']and auth['nativeMetadata']==refs['nativeMetadata']and auth['nativeReadOnlyConfig']==refs['readOnlyConfig']and auth['actualBootstrapReview']==refs['actualBootstrapReview']and auth['actualReadOnlyReview']==refs['actualReadOnlyReview'],'unchanged genuine native/APIroles')
metadata=read(refs['nativeMetadata']);olddata=read(refs['actualReadOnlyData']);need(len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==11 and olddata['bootstrap']['metadata']==metadata,'full raw80/355+3/11 genuine frame')
mp=auth['actualMappedReview'];family(mp['index']);m=read(mp['result']);mk=read(auth['actualMappedContract']);need(mp==root['actualMappedReview']and mp['index']['sha256']=='580e1f5902d1a8e0cc47840b49c8735db7b3d64a80966bd4fa53199814fe0bb5'and m['state']==mk['requiredReviewState']=='INDEPENDENT_COMBINED355_MAPPED_OUTPUT_REVIEW_PASSED_V3'and m['fixtureId']=='fatal'and m['sourceIndexSha256']==ix['sha256'],'actual mappedfatal lineage')
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for n,v in mk[group].items():need(m[n]==v,'whole mappedcontract '+n)
need(m['mappedFiles']==mk['mappedFiles']and m['coverage']==mk['requiredCoverage'],'whole mapped files/coverage');direct_roles(m['mappedFiles']);component=m['component'];need(component==refs['artifactSlots']['fatal']['knownComponent'],'actual9d289 component')
rpair=auth['actualResourceRuntimeReview'];family(rpair['index']);p=read(rpair['result']);k=read(auth['actualResourceRuntimeContract']);need(rpair==root['actualResourceRuntimeReview']and rpair['index']['sha256']=='d77c82e2abf8678b527910ae6be2f2df7250da7e72010e6cf5b90a8a35f90387'and p['state']==k['requiredReviewState']=='INDEPENDENT_COMBINED355_RESOURCE_RUNTIME_RESULTS_REVIEW_PASSED_V3'and p['verifiedPassed']is True and p['sourceIndexSha256']==ix['sha256']and p['nativeEngineSha256']==refs['nativeEngine']['sha256'],'real handled-error resource prerequisite')
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for n,v in k[group].items():need(p[n]==v,'whole resourcecontract '+n)
need(p['coverage']==k['requiredCoverage']and p['coverage']['runRecords']==49 and p['coverage']['callbackObservations']==98 and p['coverage']['newIds']==322,'whole actual resource prerequisite, no counts-only substitution')
base=Path(auth['outputRoot']);need(str(base)==review_inputs['expectedOutputRoot'],'fixed failed output context');partial=root['actualPartialFiles'];names=set(partial)
expected={'inputs.json','failure.json','fatal-jco/fatal-armed.json','fatal-jco/caught-failure.json','fatal-jco/raw/001.json',*[f'processes/{n}.{s}'for n in ['jco-fatal','wasmtime-fatal']for s in ['stdout.txt','stderr.txt','launch.json','terminal.json']],*[f'brackets/{n}.json'for n in ['jco-fatal','wasmtime-fatal']]}
need(names==expected and len(names)==15 and root['partialFileCount']==15 and {p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names,'complete exact15partialfiles')
for name,row in partial.items():need(Path(row['path'])==base/name,'confined original partial role');checked(row)
for pth in [base,*base.rglob('*')]:
 st=pth.lstat();need(not pth.is_symlink(),'no partialaliases')
 if pth.is_dir():need(stat.S_IMODE(st.st_mode)==0o700,'private failedoutputdirectory')
 else:need(stat.S_ISREG(st.st_mode)and st.st_nlink==1 and stat.S_IMODE(st.st_mode)==(0o644 if pth.name.endswith(('.stdout.txt','.stderr.txt'))else 0o600),'partialpipes644/others600')
for name in ['result.json','index.json','completion.json','fatal-classification.json','fatal-jco/unexpected-normal-return.json','fatal-jco/index.json','fatal-jco/completion.json']:need(not(base/name).exists(),'absent unproduced result/classification '+name)
for name in ['originalResultPublished','originalIndexPublished','originalCompletionPublished','originalFatalClassificationPublished','expectedCallbackFailureProved','fatalCallbackGateSatisfied','nativeCallbackReachedObserved','uniqueOriginalJsErrorIdentityProved','phaseSucceeded','runtimeAcceptanceClaim','operationalAdmission']:need(root[name]is False,'unaccepted failure limitation '+name)
need(root['callbackCause']=='inconclusive'and root['ownedProcessCleanupVerified']is True and root['sourceControlledFailureFinalErrors']==[],'inconclusive outcome, actual cleanup separatefrom rawzero')
inputs=read(partial['inputs.json']);need(inputs['sourceIndex']==ix and inputs['rootAuthority']==root['rootAuthority']and inputs['config']==root['config']and inputs['component']==component and inputs['nativeRecordData']==refs['actualReadOnlyData'],'original inputs real frame/root/component')
failure=read(partial['failure.json']);need(failure['primaryPresent']is True and failure['partialEvidenceOnly']is True and failure['finalErrors']==failure['sessions']==[],'actual parent failure final record')
for role in ['externalParentTerminal','outerTerminal']:
 t=read(root[role]);need(t['rawExitCode']==1 and t['authority']==root['rootAuthority']and t['timeout']is t['forcedCleanup']is False and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True,'both parentraw1 with clean owned groups')
 for f in ['errors','signals','interruptedSignals','remainingObservedPids']:need(t[f]==[],'clean fatalparent '+f)
 need(all(not g['alive']for g in t['finalGroups']),'all final observed groups gone');checked(t['stdout']);checked(t['stderr'])
inner=read(root['externalParentTerminal']);outer=read(root['outerTerminal']);need(inner['stdout']['bytes']==0,'no Node result publicationframe');lines=[json.loads(x)for x in Path(outer['stdout']['path']).read_text().splitlines()];need(len(lines)==2 and lines[0]==dict(pid=inner['pid'],timeoutSeconds=1200)and lines[1]['terminal']==root['externalParentTerminal']and lines[1]['rawExitCode']==1,'outerPython raw1 terminalframe separatefrom empty Node stdout')
need(any(o['pid']==inner['pid']for o in outer['observedProcesses']),'actual outer observed innerpid');need(inv['originalOuterDeadlineSeconds']==1800 and inv['originalInnerDeadlineSeconds']==1200,'original bounded monitor budgets')
terms={n:read(d)for n,d in root['childTerminals'].items()};need(set(terms)=={'jco-fatal','wasmtime-fatal'},'exact two disposable attempts');pids=[]
for n,t in terms.items():
 need(t['status']==(1 if n=='jco-fatal'else 134)and t['signal']is t['spawnError']is t['externalSignal']is None and t['timedOut']is t['outputLimitExceeded']is t['terminalExitZeroObserved']is False and t['closed']is t['ownedGroupGone']is True and t['signalCount']==0 and t['signals']==t['errors']==[],'actual expected nonzero terminal, not signal classification')
 need(t['timeoutMs']==180000 and t['maxOutputBytes']==16777216,'bounded children');checked(t['stdout']);checked(t['stderr']);need(t['stdout']['bytes']==0,'empty original childstdout');pids.append(t['pid'])
 launch=read(partial[f'processes/{n}.launch.json']);need(launch['executable']==t['executable']and launch['args']==t['args']and launch['timeoutMs']==t['timeoutMs']and launch['detachedOwnedSession']is True,'original launch join')
 need(any(o['pid']==t['pid']for o in inner['observedProcesses']),'monitor actual observed each child')
need(len({*pids,inner['pid'],outer['pid']})==4,'four distinct original ownedprocess roles')
j=terms['jco-fatal'];w=terms['wasmtime-fatal'];need(j['executable']==refs['node']['path']and j['args']==[str(SOURCE/'entry.mjs'),'fatal-worker',json.dumps(root['config'],separators=(',',':'))],'actual original Node fatalworker argv');need(w['executable']==refs['wasmtime']['path']and w['args']==['run','--invoke','run()',component['path']],'original literal freshWT invocation')
marker=read(partial['fatal-jco/fatal-armed.json']);typed=read(partial['fatal-jco/raw/001.json']);caught=read(partial['fatal-jco/caught-failure.json']);need(marker['sourceIndex']==ix and marker['component']==component and marker['actualMappedReview']==mp and marker['state']=='COMBINED355_FATAL_PUBLIC_CALL_ARMED_V3'and marker['moduleImportCompleted']is marker['publicExportAboutToBeInvoked']is True,'actual post-import before-call marker')
need(typed['kind']=='throw'and typed['observed']==dict(type='object',opaque=True,fullOpaqueValueClaim=False)and caught['original']==typed['observed']and caught['capture']==dict(attempted=1,written=1,captureFailures=[])and caught['expectedFatalClaim']is False,'one whole typed opaque thrown observation, not JS identity proof')
wtstderr=Path(w['stderr']['path']).read_text();need('unreachable'in wtstderr and 'RESOURCE_UNHANDLED_TIMER_CALLBACK'not in wtstderr,'generic WT trap with no Source-specific callback diagnostic')
message='WT fatal identity/reach evidence pending if diagnostic absent; nonzero alone never enough';need(message in Path(inner['stderr']['path']).read_text()and 'models.mjs:4'in Path(inner['stderr']['path']).read_text()and 'runtime.mjs:54'in Path(inner['stderr']['path']).read_text(),'actual Source predicate refusal stack')
need('AssertionError'in Path(outer['stderr']['path']).read_text()and "terminal['rawExitCode']==0"in Path(outer['stderr']['path']).read_text(),'outer rawzero acceptance conjunction failure, not cleanup failure')
copies=[];chosen=[Path(d['path'])for d in partial.values()]+[Path(rp['path']),*[Path(root[k]['path'])for k in ['rootAuthority','config','invocation','externalParentTerminal','outerTerminal']],*[Path(t[k]['path'])for t in [inner,outer]for k in ['stdout','stderr']]]
for pth in dict.fromkeys(chosen):
 label='actual/'+pth.relative_to(base).as_posix()if pth.is_relative_to(base)else'external/'+pth.parent.name+'/'+pth.name;dest=OWN/'raw'/label;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(pth.read_bytes());need(descriptor(dest)['sha256']==descriptor(pth)['sha256'],'exact compact actualraw copy');copies.append(dict(original=descriptor(pth),copy=descriptor(dest)))
for path,ident in identities.items():need(key(Path(path).lstat())==ident,'final current Source/native/package/actual identitybookend')
for path in families:
 b=Path(path).parent;need({p.relative_to(b).as_posix()for p in b.rglob('*')if p.is_file()}=={'index.json',*[r['path']for r in json.loads(Path(path).read_bytes())['files']]},'final exact family membership')
need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names,'final whole15partialpublication')
summary=dict(schemaVersion=1,state='INDEPENDENT_FATAL_V3_ACTUAL_FAILURE_READ_ONLY_INTAKE_PASSED',originalRootTerminalSupplied=True,checks=checks,currentFullHashFiles=len(rows),currentLogicalBytes=sum(r['bytes']for r in rows.values()),currentFamilies=len(families),sourceIndex=ix,sourcePeer=auth['sourceIndependentReview'],rootResult=rp,runtimeRootAuthority=root['rootAuthority'],runtimeConfig=root['config'],invocation=root['invocation'],actualOutputRoot=str(base),externalParentTerminal=root['externalParentTerminal'],outerTerminal=root['outerTerminal'],innerNodePid=inner['pid'],outerParentPid=outer['pid'],childPids=pids,component=component,mappedReview=mp,mappedContract=auth['actualMappedContract'],resourceRuntimeReview=rpair,resourceRuntimeContract=auth['actualResourceRuntimeContract'],nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],freezeReceipt=refs['freezeReceipt'],actualFiles=list(partial.values()),actualPartialFiles=partial,childTerminals=root['childTerminals'],currentObserver=root['observer'],coverage=dict(freshJcoAttempts=1,freshWasmtimeAttempts=1,typedJcoThrows=1,actualPartialFiles=15,originalResultPublications=0,originalFatalClassifications=0),actualTimeProtectionQualification='Original Source-coupled parent finally record finalErrors[] plus current fullhash/mode/membership/identity protections; original raw1 is predicate refusal, not successful result and not an actual-time per-read trace; workerFinallyExecutionProvedfalse',targetOrApiHelperRecheckWorkerGuestReruns=False)
(OWN/'intake-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(OWN/'raw-copy-ledger.json').write_text(json.dumps(dict(schemaVersion=1,files=copies),indent=2)+'\n');print(json.dumps({k:summary[k]for k in ['state','checks','currentFullHashFiles','currentLogicalBytes','currentFamilies','innerNodePid','outerParentPid','childPids']}))
