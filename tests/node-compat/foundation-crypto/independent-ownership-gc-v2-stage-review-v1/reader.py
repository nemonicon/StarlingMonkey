"""UNSEALED future actual-stage reader. Do not run until Root supplies terminal.
Only read/hash/JSON/physical metadata; no owner imports, Git or phase commands.
Writes audit DATA only, never a final peer PASS. Actual result is reviewed/sealed later.
"""
from pathlib import Path
import hashlib,json,os,stat,sys
REPO=Path('/Users/dan/dev/StarlingMonkey');K=REPO/'tests/node-compat/foundation-crypto'
SOURCE=Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-source')
NATIVE=K/'ownership-gc-native-candidate-v2'
NATIVE_SHA='ed0665046ec293b846069df0c050a388b1d717abbf4a0e56c64d8bd17d9a6d05'
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'
checks=0;seen={};cache={}
def need(ok,msg):
 global checks
 if not ok:raise AssertionError(msg)
 checks+=1
def identity(s):return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode,s.st_nlink)
def row(p):
 p=Path(p);h=hashlib.sha256();size=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b);size+=len(b)
 return dict(path=str(p),sha256=h.hexdigest(),bytes=size)
def verify(r,role):
 p=Path(r['path']);need(p.is_absolute()and p.is_file()and not p.is_symlink(),'ordinary absolute input')
 real=str(p.resolve());a=p.stat()
 if real not in cache:
  v=row(p);b=p.stat();need(identity(a)==identity(b),'stable streamed bytes');cache[real]=dict(sha256=v['sha256'],bytes=v['bytes'],identity=identity(b))
 else:need(identity(a)==cache[real]['identity'],'stable repeated input')
 need(cache[real]['sha256']==r['sha256']and cache[real]['bytes']==r['bytes'],'exact data '+str(p))
 if str(p)not in seen:seen[str(p)]={k:r[k]for k in ['path','sha256','bytes']};seen[str(p)]['roles']=set()
 seen[str(p)]['roles'].add(role);return r
def data(r,role):verify(r,role);return json.loads(Path(r['path']).read_bytes())
def family(r):
 ix=data(r,'source-index');names=set();rows=[]
 for e in ix['files']:
  n=e['path'];need(n and not n.startswith('/')and all(t not in ('','.','..')for t in n.split('/'))and n not in names,'safe unique member');names.add(n)
  a=dict(path=str(Path(r['path']).parent/n),sha256=e['sha256'],bytes=e['bytes']);verify(a,'indexed-source-member');rows.append(a)
 need({str(p.relative_to(Path(r['path']).parent))for p in Path(r['path']).parent.rglob('*')if p.is_file()}==names|{'index.json'},'exact source family membership')
 return rows

def audit(spec):
 need(spec['actualStageOutcomeSuppliedByRoot']is True and spec['rootObservedRawExitCode']==0 and type(spec['rootToolSession'])is int,'Root must supply actual terminal outcome first')
 need(spec['sourceIndex']['sha256']==NATIVE_SHA and spec['sourceIndex']['path']==str(NATIVE/'index.json'),'exact reviewed source family')
 family(spec['sourceIndex']);family(spec['sourceReview']['index']);peer=data(spec['sourceReview']['result'],'independent-source-peer')
 need(peer['state']=='INDEPENDENT_CRYPTO_OWNER355_GC_NATIVE_SOURCE_REVIEW_PASSED_V2'and peer['sourceIndexSha256']==NATIVE_SHA and peer['sourceReviewPassed']and peer['sourceOnly']and peer['ownerActionsInvoked']is False,'separate source-only peer')
 for k in ['stageControllerSourceIndex','genericMonitorSourceIndex']:
  family(spec[k])
 family(spec['controllerReview']['index']);controllerpeer=data(spec['controllerReview']['result'],'controller-source-review')
 need(controllerpeer['sourceOnly']and controllerpeer['sourceReviewPassed']and controllerpeer['hostActionsInvoked']is False,'actual source controller review')
 need(controllerpeer['gcStageControllerSourceIndexSha256']==spec['stageControllerSourceIndex']['sha256']and controllerpeer['httpControllerSourceIndexSha256']==spec['genericMonitorSourceIndex']['sha256'],'exact controller/generic monitor source identities')
 authority=data(spec['rootAuthority'],'actual-stage-only-Root-authority');config=data(spec['config'],'actual-stage-config')
 need(config['sourceIndex']==spec['sourceIndex']and config['rootAuthority']==spec['rootAuthority'],'whole config/source/Root binding')
 need(authority['phase']=='stage'and authority['stageAllowed']is True and authority['state']=='ROOT_REVIEWED_CRYPTO_OWNER355_ISOLATED_GC_NATIVE_PHASE_V1'and authority['sourceIndexSha256']==NATIVE_SHA,'only exact actual stage Root phase')
 need(authority['configuredSourceRoot']==str(SOURCE)and authority['externalParentDeadlineSeconds']==600,'actual v2 configured context and finite600s controller')
 for k in ['buildAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','guestAllowed','keyOperationsAllowed','prototypeWorkloadsAllowed','componentAllowed','nativeSourceChangesAllowed','normalMutationAllowed','metadataProjectionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:need(authority[k]is False,'scope remains closed '+k)
 need(authority['inheritedStageInputsDestination']=='/private/tmp/starling-node-compat/crypto-owner355-gc-v1-source'and authority['actualConfiguredSourceRoot']==str(SOURCE),'explicit historical destination DATA qualification')
 terminal=data(spec['externalTerminal'],'actual-owned-controller-terminal');started=data(spec['started'],'actual-owned-started')
 for k,v in dict(rawExitCode=0,timeout=False,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True,forcedCleanup=False).items():need(terminal[k]==v,'actual outer terminal '+k)
 need(terminal['errors']==terminal['signals']==terminal['interruptedSignals']==terminal['remainingObservedPids']==[]and terminal['authority']==spec['rootAuthority'],'no cleanup/signal/error adoption')
 need(terminal['finalGroups']and all(g['alive']is False for g in terminal['finalGroups']),'all actual observed final groups gone')
 need(started['pid']==terminal['pid']and started['timeoutSeconds']==600 and started['authority']==spec['rootAuthority'],'same actual owned session/deadline')
 need(started['argv'][1]==str(NATIVE/'stage.py')and json.loads(started['argv'][2])==spec['config'],'actual stage-only entry/config argv')
 for k in ['stdout','stderr']:verify(terminal[k],'complete-controller-stream')
 need(terminal['stderr']['bytes']==0,'complete empty actual stderr')
 journal=data(spec['journal'],'actual-stage-journal')
 need(journal['state']=='CRYPTO_OWNER355_GC_SOURCE_STAGE_COMPLETE_UNREVIEWED_V1'and journal['sourceIndexSha256']==NATIVE_SHA and journal['destination']==str(SOURCE),'whole actual v2 stage identity, not historical plan destination')
 need(journal['copiedPaths']==1311 and journal['nativeSourceFiles']==355 and journal['toolRows']==922 and journal['metadataProjected']is False and journal['nativeBuildOrRuntimeInvoked']is False,'actual counts and phase scope')
 need(json.loads(Path(terminal['stdout']['path']).read_bytes())==journal,'whole raw stage stdout equals journal')
 commands=journal['commands'];need(len(commands)==2 and all(c['rawExitCode']==0 for c in commands),'actual clone+checkout commands raw0')
 need(commands[0]['argv']==['git','clone','--no-local','--no-checkout','/private/tmp/starling-node-compat/crypto-owner-source-v2',str(SOURCE)]and commands[1]['argv']==['git','-C',str(SOURCE),'checkout','--detach',BASE],'exact fresh local clone/checkout arguments')
 need((SOURCE/'.git/HEAD').read_text()==BASE+'\n'and not(SOURCE/'.git/objects/info/alternates').exists(),'actual detached base/no alternates')
 for p in (SOURCE/'.git').rglob('*'):
  need(not p.is_symlink(),'ordinary isolated Git files')
  if p.is_file():need(p.stat().st_nlink==1,'no Git object hardlinks')
 plan=data(row(NATIVE/'stage-inputs.json'),'authentic-row-plan');need(plan['destination']=='/private/tmp/starling-node-compat/crypto-owner355-gc-v1-source','copied plan destination remains historical DATA')
 need(len(plan['files'])==1311 and len({r['path']for r in plan['files']})==1311,'all exact1311 declared rows')
 filemap={r['path']:r for r in plan['files']}
 copies=[]
 for r in plan['files']:
  n=r['path'];need(n and not n.startswith('/')and all(t not in ('','.','..')for t in n.split('/')),'safe copy path');original=r['original'];verify(original,'unchanged-original-native-source-or-tool')
  target=SOURCE/n
  for p in [target,*target.parents]:need(not p.is_symlink(),'no stage/source alias')
  verify(dict(path=str(target),sha256=original['sha256'],bytes=original['bytes']),'actual-staged-copy')
  a,b=Path(original['path']).stat(),target.stat();need(a.st_dev!=b.st_dev or a.st_ino!=b.st_ino,'independent original/target inode');need(b.st_nlink==1 and stat.S_IMODE(a.st_mode)==stat.S_IMODE(b.st_mode)==r['mode'],'actual copy mode/no hardlinks')
  copies.append(dict(path=n,sha256=original['sha256'],bytes=original['bytes'],mode=r['mode'],distinctInode=True))
 layer='tests/node-compat/foundation-crypto/native-integration-candidate-v2/'
 policy=json.loads((SOURCE/layer/'policy.json').read_bytes());tools=json.loads((SOURCE/layer/'artifact-tools/tool-pins.json').read_bytes())
 need(len(policy['expectedNativeSourceManifest'])==355 and len(tools['toolDependencies'])==922,'full actual native355/tool922 sets')
 for label,rs in [('native355',policy['expectedNativeSourceManifest']),('tools922',tools['toolDependencies'])]:
  for r in rs:need(r['path']in filemap and filemap[r['path']]['original']['sha256']==r['sha256'],'actual named source/tool membership '+label)
 protection=data(row(NATIVE/'normal-protection.json'),'unchanged-normal-protection');need(len(protection['originals'])==1387 and protection['distinctOriginalPaths']==1378 and len(protection['frozenCopyEntries'])==1390,'all normal reference/copy counts')
 for r in protection['originals']:verify(r['original'],'protected-normal-original');verify(r['frozen'],'protected-normal-frozen')
 for r in protection['frozenCopyEntries']:verify({k:r[k]for k in ['path','sha256','bytes']},'all-normal-frozen-copy')
 verify(protection['freezeReceipt'],'original-normal-freeze-receipt')
 normal=Path('/private/tmp/starling-node-compat/production-crypto-owner-v2/native-freeze');need({str(p.relative_to(normal))for p in normal.rglob('*')if p.is_file()}==set(protection['requiredNormalFreezeMembership']),'strict unchanged1391 normal freeze membership')
 need(len(protection['vulnerableProjectOriginals'])==2,'normal cache+DB protected with no drift allowance')
 for real,r in cache.items():need(identity(Path(real).stat())==r['identity'],'all source/input evidence stable at final read')
 return dict(schemaVersion=1,state='UNSEALED_ACTUAL_GC_SOURCE_STAGE_AUDIT_DATA_ONLY',actualStageResult=spec['journal'],sourceIndexSha256=NATIVE_SHA,configuredSourceRoot=str(SOURCE),rootToolStatusReportedOnly=spec['rootObservedRawExitCode'],externalParentExitCode=0,ownedGroupGone=True,copyRows=1311,nativeFiles=355,toolRows=922,normalOriginalEntries=1387,normalFrozenMembers=1391,allDeclaredCopiesOriginalsModesAndInodesVerified=True,actualDetachedBase=BASE,gitAlternatesAbsent=True,sourceOnly=True,nativeOrGuestOrPhaseActionsInvokedByReader=False,finalPeerPassIssued=False,checks=checks,copies=copies,inputRows=[dict(r,roles=sorted(r['roles']))for r in seen.values()])

if __name__=='__main__':
 need(len(sys.argv)==3,'Actual evidence spec and owned audit output path required; no default run')
 spec=json.loads(Path(sys.argv[1]).read_bytes());value=audit(spec)
 target=Path(sys.argv[2]);need(not target.exists(),'exclusive new audit DATA output');target.write_text(json.dumps(value,indent=2)+'\n')
 print(json.dumps(dict(auditDataComplete=True,finalPeerPassIssued=False,checks=checks)))
