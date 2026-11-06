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
root=read(review_inputs['actualRootResult']);direct_roles(root);need(root['toolObservation']==dict(sessionId=review_inputs['originalRootToolSession'],rawExitCode=0)and root['sourceIndex']==ix,'actual originalRoot rawzero/currentSource')
rp=review_inputs['actualRootResult'];need(rp['sha256']==review_inputs['expectedRootResultSha256'],'actual finalRoot report pin')
auth=read(root['rootAuthority']);cfg=read(root['config']);inv=read(root['invocation']);direct_roles(inv)
need(auth['state']=='ROOT_REVIEWED_COMBINED355_NATIVE_RUNTIME_PHASE_V3'and auth['phase']==cfg['phase']=='run'and auth['fixtureId']==cfg['fixtureId']=='clock-snapshot'and auth['sourceIndex']==cfg['sourceIndex']==ix and cfg['rootAuthority']==root['rootAuthority'],'genuine separate ordinary run permission/context')
need(auth['mappingOnlyAllowed']is auth['jcoCompilerHelpersAllowed']is auth['nodePureOracleAllowed']is False and auth['generatedApplicationImportAllowed']is auth['ordinaryGuestExportsAllowed']is auth['stockWasmtimeAllowed']is True,'only original ordinary resourcework, no compiler/oracle')
for name in ['keyOrCryptoAllowed','nativeBuildAllowed','nativeFreezeAllowed','gcOrFaultActionsAllowed','debugOrUnsafeResetAllowed','timingAllowed','fullClockProfileAcceptance','operationalAdmission','runtimeAcceptanceClaim']:need(auth[name]is False,'no extra action '+name)
family(auth['sourceIndependentReview']['index']);sp=read(auth['sourceIndependentReview']['result']);need(auth['sourceIndependentReview']['index']['sha256']=='ecd595bc5dc3ad7e0d9130cb7b4b8d3caa45a6cbcb73c0f91f3b3856aaea419b'and sp['state']=='INDEPENDENT_COMBINED355_NATIVE_RUNTIME_SOURCE_REVIEW_PASSED_V3'and sp['sourceIndexSha256']==ix['sha256']and sp['sourceReviewPassed']is True,'genuine Sourceecd')
need(auth['nativeEngine']==refs['nativeEngine']and auth['nativeMetadata']==refs['nativeMetadata']and auth['nativeReadOnlyConfig']==refs['readOnlyConfig']and auth['actualBootstrapReview']==refs['actualBootstrapReview']and auth['actualReadOnlyReview']==refs['actualReadOnlyReview'],'real full80 native/API parents')
metadata=read(refs['nativeMetadata']);olddata=read(refs['actualReadOnlyData']);need(len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==11 and olddata['bootstrap']['metadata']==metadata,'whole raw80/355+3/11 unchanged')
map_pair=auth['actualMappedReview'];family(map_pair['index']);m=read(map_pair['result']);mc=read(auth['actualMappedContract']);need(map_pair==root['actualMappedReview']and map_pair['index']['sha256']=='07c61d255774188658870a2795e7a5fb3170d394c0dc670a86650733a69ac8a1'and m['state']==mc['requiredReviewState']=='INDEPENDENT_COMBINED355_MAPPED_OUTPUT_REVIEW_PASSED_V3'and m['sourceIndexSha256']==ix['sha256']and m['fixtureId']=='clock-snapshot','actual clockmapped07c6 gate')
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for name,v in mc[group].items():need(m[name]==v,'whole mapped contract '+name)
need(m['mappedFiles']==mc['mappedFiles']and m['coverage']==mc['requiredCoverage'],'complete actual mappedfiles/coverage');direct_roles(m['mappedFiles']);need(root['component']==m['component'],'same5e020b component')
# Prior failure remains originalDATA, not relabeled as new success.
family(refs['actualMappingFailureReview']['index']);family(refs['mappingFailureOriginalReviewIndex']);fp=read(refs['actualMappingFailureReview']['result']);need(fp['acceptedMappedOutput']is fp['actualPostCallOptionsObserved']is False and fp['sourceIndexSha256']==refs['publicationParentSourceIndex']['sha256'],'immutable failed V2lineage')
result=read(root['runtimeResult']);need(result['state']=='COMBINED355_RUNTIME_COMPLETE_UNREVIEWED_V3'and result['sourceIndex']==ix and result['rootAuthority']==root['rootAuthority']and result['config']==root['config']and result['component']==root['component']and result['fixtureId']=='clock-snapshot','whole actualordinary resultcontext')
coverage=dict(jcoRetainedStrings=3,jcoFreshStrings=1,freshWasmtimeStrings=3);need(result['coverage']==root['coverage']==coverage,'complete expected3retained/1freshJco/3freshWT coverage record')
need(result['callbackCause']=='not-exercised'and result['observationPublicationOnly']is False and result['genuineNativeCallbackDiagnostic']is None,'positive clock case cannotprovefatalcause')
for name in ['expectedCallbackFailureProved','fatalCallbackGateSatisfied','nativeOffsetInterestDropOrTeardownProved','fullSixFixturesAccepted','all17GatesSatisfied','fullProfileAcceptance','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']:need(result[name]is False,'actualruntime limitation '+name)
base=Path(auth['outputRoot']);need(str(base)==review_inputs['expectedOutputRoot'],'actual exact freshoutputroot');index=read(root['actualIndex']);completion=read(root['completion']);names={'index.json','completion.json'}
for row in index['files']:
 name=row['path'];need(name not in names and name and not name.startswith('/')and all(p not in('','.','..')for p in name.split('/')),'unique confined producer member');names.add(name);checked(dict(row,path=str(base/name)))
need(len(index['files'])==42 and len(names)==44 and {p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names,'whole42payload/44actual incl nestedchildindices')
pipe_names={f'processes/{name}.{stream}.txt'for name in ['retained','fresh','wasmtime-0','wasmtime-1','wasmtime-2']for stream in ['stdout','stderr']}
for p in [base,*base.rglob('*')]:
 st=p.lstat();need(not p.is_symlink(),'no runtimeoutputalias')
 if p.is_dir():need(stat.S_IMODE(st.st_mode)==0o700,'private actual directory')
 else:need(stat.S_ISREG(st.st_mode)and st.st_nlink==1 and stat.S_IMODE(st.st_mode)==(0o644 if p.relative_to(base).as_posix()in pipe_names else 0o600),'actualpipe644/other600/singlelink')
need(completion['externalRawZeroAndSeparateReviewRequired']is True and completion['index']==dict(root['actualIndex'],path='index.json')and completion['result']==dict(root['runtimeResult'],path='result.json'),'original relative whole publication roles')
for role in ['externalParentTerminal','outerTerminal']:
 t=read(root[role]);need(t['rawExitCode']==0 and t['authority']==root['rootAuthority']and t['timeout']is t['forcedCleanup']is False and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True,'both rawzero clean monitors')
 for field in ['errors','signals','interruptedSignals','remainingObservedPids']:need(t[field]==[],'no monitorcleanup '+field)
 need(all(not g['alive']for g in t['finalGroups']),'all observed groups gone');checked(t['stdout']);checked(t['stderr']);need(t['stderr']['bytes']==0,'empty original parentstderr')
inner=read(root['externalParentTerminal']);outer=read(root['outerTerminal']);pythonlines=[json.loads(x)for x in Path(outer['stdout']['path']).read_text().splitlines()];need(len(pythonlines)==2 and pythonlines[0]==dict(pid=inner['pid'],timeoutSeconds=1200)and pythonlines[1]['terminal']==root['externalParentTerminal']and pythonlines[1]['rawExitCode']==0,'separate actual outerPython JSONL frame')
node=json.loads(Path(inner['stdout']['path']).read_text());need(node==dict(root=str(base),index=dict(root['actualIndex'],path='index.json'),completion=dict(root['completion'],path='completion.json'),completeUnreviewed=True),'separate original innerNode relativepublication frame')
need(any(p['pid']==inner['pid']for p in outer['observedProcesses']),'actual outerobservedNode pid')
need(len(result['sessions'])==5 and root['sessions']==result['sessions'],'complete actual5session result maps')
child_pids=[]
for session in result['sessions']:
 term=read(session['terminal']);need(term['status']==0 and term['signal']is term['spawnError']is term['externalSignal']is None and term['timedOut']is term['outputLimitExceeded']is False and term['closed']is term['ownedGroupGone']is term['terminalExitZeroObserved']is True and term['errors']==term['signals']==[]and term['signalCount']==0,'all5 durable childterminals rawzero/no kill')
 child_pids.append(term['pid']);checked(term['stdout']);checked(term['stderr']);need(term['stderr']['bytes']==0 and term['timeoutMs']==180000 and term['maxOutputBytes']==16777216,'childfullpipes/bounds')
 launch=read(descriptor(base/'processes'/f"{term['name']}.launch.json"));need(launch['executable']==term['executable']and launch['args']==term['args']and launch['timeoutMs']==term['timeoutMs']and launch['detachedOwnedSession']is True,'real launch/terminal join')
 need(any(p['pid']==term['pid']for p in inner['observedProcesses']),'monitor observed each actual ownedchild')
need(len(set(child_pids))==5 and len({*child_pids,inner['pid'],outer['pid']})==7,'five distinctfreshcommands+two original parents')
for scenario in ['retained','fresh']:
 cb=base/scenario;ci=read(descriptor(cb/'index.json'));cc=read(descriptor(cb/'completion.json'));cn={'index.json','completion.json'}
 for row in ci['files']:
  need(row['path']not in cn,'unique nestedchildmember');cn.add(row['path']);checked(dict(row,path=str(cb/row['path'])))
 need({p.relative_to(cb).as_posix()for p in cb.rglob('*')if p.is_file()}==cn,'full nested publication membership')
 need(cc['index']==dict(descriptor(cb/'index.json'),path='index.json')and cc['result']==dict(descriptor(cb/'result.json'),path='result.json')and cc['externalRawZeroAndSeparateReviewRequired']is True,'nestedchild relativeindex/completion roles')
# Observer correction is prior read-only preparation history; its OLD source
# descriptor is not a current file to reopen or silently normalize/rewrite.
correction=OWN.parent/'combined-native-runtime-v3-root-observe-preparation-correction-v1.json';cor=read(descriptor(correction));need(cor['targetOperationRerun']is False and cor['targetToolSession']==30639 and cor['rootResultWrittenBeforeCorrection']is False,'prior clockobserverpreparation correction, not clock runtime targetrerun')
need(root['observer']['sha256']=='888fb6c6fe77e81759b5141f9f2ea236fee1772fae2f344e8e096c245c497f9b','current corrected actual clockobserver')
copies=[];chosen=[base/r['path']for r in index['files']]+[base/'index.json',base/'completion.json',Path(rp['path']),correction,*[Path(root[k]['path'])for k in ['rootAuthority','config','invocation','externalParentTerminal','outerTerminal']],*[Path(t[k]['path'])for t in [inner,outer]for k in ['stdout','stderr']]]
for p in dict.fromkeys(chosen):
 label='actual/'+p.relative_to(base).as_posix()if p.is_relative_to(base)else'external/'+p.parent.name+'/'+p.name;dest=OWN/'raw'/label;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes());need(descriptor(dest)['sha256']==descriptor(p)['sha256'],'all compact exact actualraw text');copies.append(dict(original=descriptor(p),copy=descriptor(dest)))
for path,ident in identities.items():need(key(Path(path).lstat())==ident,'final fullSource/native/package/actual identitybookend')
for path in families:
 b=Path(path).parent;need({p.relative_to(b).as_posix()for p in b.rglob('*')if p.is_file()}=={'index.json',*[r['path']for r in json.loads(Path(path).read_bytes())['files']]},'final whole currentfamily membership')
need({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}==names,'final exact runtimepublication')
summary=dict(schemaVersion=1,state='INDEPENDENT_CLOCK_SNAPSHOT_RUNTIME_V3_ACTUAL_READ_ONLY_INTAKE_PASSED',originalRootTerminalSupplied=True,checks=checks,currentFullHashFiles=len(rows),currentLogicalBytes=sum(r['bytes']for r in rows.values()),currentFamilies=len(families),sourceIndex=ix,sourcePeer=auth['sourceIndependentReview'],rootResult=rp,runtimeRootAuthority=root['rootAuthority'],runtimeConfig=root['config'],invocation=root['invocation'],actualOutputRoot=str(base),actualIndex=root['actualIndex'],result=root['runtimeResult'],completion=root['completion'],externalParentTerminal=root['externalParentTerminal'],outerTerminal=root['outerTerminal'],innerNodePid=inner['pid'],outerParentPid=outer['pid'],childPids=child_pids,component=root['component'],mappedReview=map_pair,mappedContract=auth['actualMappedContract'],nativeEngine=refs['nativeEngine'],nativeMetadata=refs['nativeMetadata'],freezeReceipt=refs['freezeReceipt'],actualFiles=[dict(r,path=str(base/r['path']))for r in index['files']]+[root['actualIndex'],root['completion']],coverage=coverage,observerPreparationCorrection=descriptor(correction),currentObserver=root['observer'],actualTimeProtectionQualification='Source-coupled original success/final API checks and childfinalProtectionErrors[]/both monitorraw0 plus current independent whole file/hash/mode/membership audits; no actual-time per-readtrace or newly captured nativeframe',targetOrApiHelperRecheckWorkerGuestReruns=False)
(OWN/'intake-summary.json').write_text(json.dumps(summary,indent=2)+'\n');(OWN/'raw-copy-ledger.json').write_text(json.dumps(dict(schemaVersion=1,files=copies),indent=2)+'\n');print(json.dumps({k:summary[k]for k in ['state','checks','currentFullHashFiles','currentLogicalBytes','currentFamilies','innerNodePid','outerParentPid','childPids']}))
