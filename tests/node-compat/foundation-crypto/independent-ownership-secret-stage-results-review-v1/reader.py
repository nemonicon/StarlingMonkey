"""Actual source-stage read/hash/data audit only. No Git/owner/helper/process invocation."""
from pathlib import Path
from collections import Counter
import hashlib,json,os,stat

HERE=Path(__file__).resolve().parent;K=HERE.parent;REPO=K.parents[2]
SOURCE=K/'ownership-secret-integration-candidate-v1'
DEST=Path('/private/tmp/starling-node-compat/crypto-owner355-secret-v1-source')
BASE='54b3329b3ce818fd1f244e871e9c259b63667cda'
ROOT_SHA='417fbe749e08f2dbd41d4a27e8ce1149e5e2721d5e3441872439896595aee67a'
rows={};checks=0
def need(v,m):
 global checks
 checks+=1
 if not v:raise AssertionError(m)
def physical(p):
 p=Path(p);return Path('/private'+str(p))if str(p).startswith('/tmp/')else p
def row(path):
 p=physical(path)
 for q in(p,*p.parents):need(not q.is_symlink(),'no symlink source/data ancestor')
 a=p.stat();need(stat.S_ISREG(a.st_mode),'regular file');h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=p.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable read')
 return dict(path=str(path),sha256=h.hexdigest(),bytes=z.st_size)
def verify(d,base=None):
 p=Path(d['path'])
 if not p.is_absolute():need(base is not None and '..'not in p.parts,'explicit relative context');p=base/p
 need(p.is_absolute(),'absolute data path');key=str(physical(p));a=rows.get(key)
 if a is None:a=row(p);rows[key]=a
 need((a['sha256'],a['bytes'])==(d['sha256'],d['bytes']),'exact hash/bytes '+str(p));return physical(p)
def load(p):
 p=Path(p);d=row(p);rows[str(physical(p))]=d;return json.loads(physical(p).read_text())
def described(d):return load(verify(d))
def family(d):
 p=verify(d);ix=load(p);names=[r['path']for r in ix['files']];need(len(names)==len(set(names)),'unique family rows')
 for r in ix['files']:verify(r,p.parent)
 need({q.relative_to(p.parent).as_posix()for q in p.parent.rglob('*')if q.is_file()}==set(names)|{'index.json'},'exact source family membership')
 return [d]+[dict(r,path=str(p.parent/r['path']))for r in ix['files']]
rootpath=K/'ownership-secret-stage-v1-root-results.json';need(row(rootpath)['sha256']==ROOT_SHA,'completed Root report SHA');root=load(rootpath)
authority=described(root['rootAuthority']);config=described(root['config'])
need(config['rootAuthority']==root['rootAuthority']and config['sourceIndex']['sha256']==authority['sourceIndexSha256'],'actual authority/config/source')
source_rows=family(config['sourceIndex']);controller_rows=family(root['controllerSourceIndex']);family(root['controllerSourceReview']['index']);described(root['controllerSourceReview']['result'])
need(config['sourceIndex']['sha256']=='7eb863b94b3f65b8f19480d8e8a5f3a1dac62c65d5be241097c6a0f382d74108','integration exact7eb')
need(root['controllerSourceIndex']['sha256']=='7758e1a722043a3ecc0ba6d3e95eb3a6f53ddf1dcfaa684460c801cf10e60a12','actual controller7758')
family(authority['independentSourceReview']['index']);integration_peer=described(authority['independentSourceReview']['result'])
need(integration_peer['sourceReviewPassed']is True and integration_peer['sourceIndexSha256']==config['sourceIndex']['sha256'],'actual integration source peer')
family(authority['payloadSourceReview']['index']);described(authority['payloadSourceReview']['result']);described(authority['payloadSourceReview']['contract'])
family(authority['genericMonitorIndex']);verify(authority['genericMonitorEntry']);verify(authority['rootCaller']);verify(root['reportReader'])
for key in ['nativeBuildAllowed','freezeAllowed','engineExecutionAllowed','keyOperationsAllowed','guestAllowed','gcAllowed','operationalAdmission','runtimeAcceptanceClaim','pinsAdopted','normalMutationAllowed','metadataProjectionAllowed','timingAllowed']:need(authority[key]is False,'closed nonstage scope '+key)
need(authority['sourceStageAllowed']is True and authority['expectedStageCopies']==1424,'actual stage-only authorization')
outer=described(root['outerTerminal']);inner=described(root['innerTerminal']);journal=described(root['actualJournal'])
for label,t,expected_pid in [('controller',outer,42623),('stage',inner,42671)]:
 need(t['pid']==expected_pid and t['rawExitCode']==0,'actual saved '+label+' terminal0')
 need(t['timeout']is False and t['forcedCleanup']is False and t['allObservedOwnedGroupsGone']is True and t['parentOwnedGroupGone']is True,'clean '+label+' lifetime')
 need(t['interruptedSignals']==t['remainingObservedPids']==t['signals']==t['errors']==[],'no signals/errors '+label)
 need(all(g['alive']is False for g in t['finalGroups']),'final observed groups gone '+label)
 for k in ['stdout','stderr','authority']:verify(t[k])
 need(t['authority']==root['rootAuthority']and verify(t['stderr']).read_bytes()==b'','actual Root and empty '+label+' stderr')
outer_records=[json.loads(line)for line in verify(outer['stdout']).read_text().splitlines()]
need(len(outer_records)==2 and set(outer_records[0])=={'pid','timeoutSeconds'},'complete two-record outer stdout')
need(outer_records[0]==dict(pid=42671,timeoutSeconds=600),'inner launch envelope')
published=outer_records[1]
need(published['state']=='SECRET_SOURCE_STAGE_RAW_ZERO_UNREVIEWED_V1'and published['copies']==1424 and published['actualJournal']==root['actualJournal']and published['externalTerminal']==root['innerTerminal'],'complete result envelope exact binding')
inner_records=[json.loads(line)for line in verify(inner['stdout']).read_text().splitlines()]
need(len(inner_records)==1 and json.dumps(inner_records[0],sort_keys=True)==json.dumps(journal,sort_keys=True),'whole typed inner stdout record equals complete journal')
try:json.loads(verify(outer['stdout']).read_text());extra_data=False
except json.JSONDecodeError as e:extra_data=(e.msg=='Extra data')
need(extra_data,'original one-document report reader would fail after successful action')
caller=verify(authority['rootCaller']).read_text();need("child_result=json.loads(Path(terminal['stdout']['path']).read_bytes())"in caller,'retained exact old reader boundary')
need(root['rootCallerExitCode']==1 and root['actualControllerExitCode']==root['actualStageExitCode']==0,'Root report keeps caller/actual stage distinction')
for t,base,deadline in [(outer,Path(authority['rootCallerOuterOutputRoot']),900),(inner,Path(authority['externalOutputRoot']),600)]:
 started=load(base/'started.json');need(started['pid']==t['pid']and started['timeoutSeconds']==deadline,'actual started/deadline')
 need(started['argv'][1:3]==['-B','-I'],'explicit plain isolated Python caller')
need(journal['state']=='SECRET_NATIVE355_SOURCE_STAGED_NOT_BUILT'and journal['sourceIndexSha256']==config['sourceIndex']['sha256'],'actual journal state')
need(journal['configuredSourceRoot']==str(DEST)and len(journal['copies'])==1424,'actual target/rows')
need(journal['commands'][0]['argv']==['git','clone','--no-local','--no-checkout',str(REPO),str(DEST)],'actual isolated clone argv')
need(journal['commands'][1]['argv']==['git','-C',str(DEST),'checkout','--detach',BASE]and len(journal['commands'])==2 and all(c['returncode']==0 for c in journal['commands']),'actual clone/checkout terminal0 data')
refs=load(SOURCE/'references.json')
for item in refs['families']:family(item['index'])
verify(refs['mandatoryHistoryErratum'])
native=load(SOURCE/'native-origins.json');tools=load(SOURCE/'tool-origins.json');plan=load(SOURCE/'stage-input-plan.json')
need(len(native['files'])==355 and len(tools['files'])==1051 and len(plan['files'])==1403,'finite355+1051tool/base1403 union')
expected={}
def add(relative,original,checksum,size,role):
 need(not relative.startswith('/')and all(x not in ('','.','..')for x in relative.split('/')),'finite staged relative path')
 original_path=verify(dict(path=original,sha256=checksum,bytes=size));mode=stat.S_IMODE(original_path.stat().st_mode)
 d=dict(path=relative,original=str(original_path),sha256=checksum,bytes=size,sourceMode=mode,roles=[role])
 if relative in expected:
  need(all(expected[relative][k]==d[k]for k in ['sha256','bytes','sourceMode']),'honest equal-byte role overlap');expected[relative]['roles'].append(role)
 else:expected[relative]=d
for d in native['files']:add(d['path'],d['original'],d['sha256'],d['bytes'],'EXACT_SECRET_NATIVE355')
for d in tools['files']:add(d['path'],d['original'],d['sha256'],d['bytes'],'AUTHENTICATED_TOOL_OR_ANCESTRY')
need(len(expected)==1403,'native/tool three overlaps')
for d in source_rows:add(str(Path(d['path']).relative_to(REPO)),d['path'],d['sha256'],d['bytes'],'OWN_SOURCE_SEAL')
need([expected[p]for p in sorted(expected)]==journal['copies'],'entire actual1424 row/role/original union reconstructed')
for d in journal['copies']:
 original=verify(dict(path=d['original'],sha256=d['sha256'],bytes=d['bytes']));target=verify(dict(path=str(DEST/d['path']),sha256=d['sha256'],bytes=d['bytes']))
 a=original.stat();b=target.stat();need(stat.S_IMODE(a.st_mode)==stat.S_IMODE(b.st_mode)==d['sourceMode'],'mode preserved')
 need((a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)and b.st_nlink==1,'independent target inode')
policy=load(SOURCE/'policy.json');manifest={d['path']:d['sha256']for d in policy['expectedNativeSourceManifest']}
need(len(manifest)==355 and {d['path']:d['sha256']for d in native['files']}==manifest,'actual whole355 source policy')
oldmeta=load(Path('/private/tmp/starling-node-compat/crypto-owner355-gc-v2-freeze/gc-off.engine.wasm.build.json'))
oldmanifest={d['path']:d['sha256']for d in oldmeta['sourceManifest']}
need(set(manifest)==set(oldmanifest)and sum(manifest[p]!=oldmanifest[p]for p in manifest)==3,'352 parent bytes unchanged/three payload afterimages')
changed=[p for p in manifest if manifest[p]!=oldmanifest[p]]
need(set(changed)=={'builtins/web/crypto/crypto-algorithm.cpp','builtins/web/crypto/crypto-key.cpp','builtins/web/crypto/crypto-raii.h'},'exact three reviewed changes')
need((DEST/'.git/HEAD').read_text().strip()==BASE,'actual detached baseline HEAD data')
need(not(DEST/'.git/objects/info/alternates').exists(),'no shared object alternates')
def object_set(base):
 files=[]
 for p in(base/'.git/objects').rglob('*'):
  need(not p.is_symlink(),'no Git object symlink')
  if p.is_file():files.append((p.stat().st_dev,p.stat().st_ino))
 return set(files)
source_objects=object_set(REPO);target_objects=object_set(DEST)
need(len(source_objects)==16 and len(target_objects)==3 and not source_objects&target_objects,'independent Git object inode sets')
normal=described(refs['normalProtection']);need(len(normal['originals'])==1387 and len(normal['requiredNormalFreezeMembership'])==1391,'normal protection counters')
for d in normal['frozenCopyEntries']:verify(d)
for d in normal['originals']:verify(d['original']);verify(d['frozen'])
verify(normal['freezeReceipt']);normal_root=Path(normal['freezeReceipt']['path']).parent
need({p.relative_to(normal_root).as_posix()for p in normal_root.rglob('*')if p.is_file()}==set(normal['requiredNormalFreezeMembership']),'strict normal1391 membership')
need(not Path(authority['workRoot']).exists()and not Path(authority['freezeRoot']).exists(),'no new build/freeze output')
for key in ['nativeBuildExecuted','engineExecuted','operationalAdmission','metadataProjected']:need(journal[key]is False,'journal closed '+key)
report=dict(schemaVersion=1,state='INDEPENDENT_SECRET_SOURCE_STAGE_DATA_AUDIT_PASSED_V1',checks=checks,distinctHashedFiles=len(rows),distinctHashedBytes=sum(d['bytes']for d in rows.values()),
 copiedRows=1424,nativeSourceFiles=355,unchangedParentNativeFiles=352,changedNativeFiles=changed,baseInputUnion=1403,toolRows=1051,
 outerStdoutRecords=2,innerStdoutRecords=1,wholeInnerStdoutEqualsJournal=True,callerSingleJsonReaderFailureReproducedAsData=True,
 observedControllerExitCode=0,observedStageExitCode=0,rootReportedCallerExitCode=1,controllerPid=42623,stagePid=42671,
 detachedBaseline=BASE,sourceGitObjectFiles=16,targetGitObjectFiles=3,gitObjectInodesDisjoint=True,
 normalFrozenMembers=1391,normalOriginalReferences=1387,workAndFreezeAbsent=True,reviewerGitHelpersStagesBuildNodeGuestOrProcessActionsInvoked=False)
with(HERE/'data-audit.json').open('x')as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(dict(audit=row(HERE/'data-audit.json'),checks=checks,files=len(rows),copies=1424,stageZero=True,reportReaderExit1Separate=True,actionsInvoked=False)))
