"""Dormant own357 native build/freeze controller. Stdlib before authentication."""
from pathlib import Path
import hashlib,importlib.util,json,os,shutil,stat,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-controller-candidate-v1'
SOURCE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
WORK=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-build')
FREEZE=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-freeze')
SOURCE_SHA='7c5a8468639f8bfab3b06f8a75e8cb74373747562b9826450397f90db2dc2429'
ENV_POLICY=dict(schemaVersion=1,mandatoryBeforeParentAndBashSpawn=True,stdlibLauncherOnlyBeforeCleanExec=True,removePrefixes=['BASH_FUNC_'],removeExactNames=['BASH_ENV','ENV','SHELLOPTS','BASHOPTS','CDPATH','GLOBIGNORE'],preserveExactNames=['HOME','home','CODEX_HOME'],rootAuthorityMustBindPolicy=True,actualParentAndWorkerMustContainNoRemovedEntries=True,recordRemovedVariableNamesOnly=True,recordEnvironmentValues=False,scope='Known Bash function/startup controls; isolated Python stdlib authentication is permitted before clean exec; not an OS sandbox')

def clean_environment(original):
 removed=sorted(k for k in original if k.startswith(tuple(ENV_POLICY['removePrefixes']))or k in ENV_POLICY['removeExactNames']);child={k:v for k,v in original.items()if k not in removed}
 for key in ENV_POLICY['preserveExactNames']:assert child.get(key)==original.get(key)and(key in child)==(key in original)
 return child,removed

def checked(r):
 assert type(r)is dict and set(r)=={'path','sha256','bytes'}and type(r['bytes'])is int and r['bytes']>=0
 assert type(r['path'])is str and Path(r['path']).is_absolute()and not r['path'].startswith('//')and str(Path(r['path']))==r['path']and '..'not in Path(r['path']).parts and '\\'not in r['path']and '\0'not in r['path']
 assert type(r['sha256'])is str and len(r['sha256'])==64 and all(c in'0123456789abcdef'for c in r['sha256'])
 p=Path(r['path'])
 if str(p).startswith('/tmp/'):assert Path('/tmp').resolve()==Path('/private/tmp');p=Path('/private'+str(p))
 for q in(p,*p.parents):assert not q.is_symlink()
 before=p.stat();assert stat.S_ISREG(before.st_mode)and before.st_size==r['bytes'];h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=p.stat();assert(before.st_dev,before.st_ino,before.st_mode,before.st_nlink,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_mode,z.st_nlink,z.st_size,z.st_mtime_ns,z.st_ctime_ns)
 assert h.hexdigest()==r['sha256'];return p

def unique(pairs):
 result={}
 for k,v in pairs:assert k not in result;result[k]=v
 return result

def read(r):assert r['bytes']<=32*1024*1024;return json.loads(checked(r).read_bytes(),object_pairs_hook=unique,parse_constant=lambda x:(_ for _ in()).throw(ValueError('Nonfinite JSON')))
def row(p):
 p=Path(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 d=dict(path=str(p),sha256=h.hexdigest(),bytes=p.stat().st_size);checked(d);return d

def family(index):
 v=read(index);base=Path(index['path']).parent;names={'index.json'};rows=[index]
 assert v['schemaVersion']==1 and 0<len(v['files'])<=2048
 for r in v['files']:
  n=r['path'];assert n and not n.startswith('/')and '\\'not in n and all(x not in('','.','..')for x in n.split('/'))and n not in names;names.add(n)
  value=dict(r,path=str(base/n));checked(value);rows.append(value)
 assert not any(p.is_symlink()for p in base.rglob('*'))and{str(p.relative_to(base))for p in base.rglob('*')if p.is_file()}==names
 return rows

def load(frame,name):
 r=next(r for r in frame['ownRows']if r['path']==str(OWN/name));checked(r)
 spec=importlib.util.spec_from_file_location('genuine_own357_'+name.replace('.','_'),r['path']);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def absent(p):
 for q in(p,*p.parents):assert not q.is_symlink()
 assert not p.exists()

def bootstrap(config_row):
 assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated==1 and Path(__file__).resolve().parent==OWN
 cfg=read(config_row);assert cfg['schemaVersion']==1 and cfg['state']=='NODE_CRYPTO_HASH_HMAC357_NATIVE_CONFIG_V1'
 root=read(cfg['rootAuthority']);own=cfg['controllerIndex'];assert own==root['controllerIndex']and own['path']==str(OWN/'index.json')
 own_rows=family(own);entry=next(r for r in own_rows if r['path']==str(OWN/'controller.py'));assert root['controllerEntry']==entry
 refs=read(next(r for r in own_rows if r['path']==str(OWN/'references.json')));assert refs['controllerEntryPath']==str(OWN/'controller.py')and cfg['integrationSourceIndex']==refs['integrationSourceIndex']
 assert root['state']=='ROOT_REVIEWED_NODE_CRYPTO_HASH_HMAC357_NATIVE_PHASE_V1'and root['phase']in['build','freeze']and root['rootEnvironmentPolicy']==ENV_POLICY
 captured={r['path']:r for r in [config_row,cfg['rootAuthority'],*own_rows]};indices={own['path']:own}
 def add(r):checked(r);assert r['path']not in captured or captured[r['path']]==r;captured[r['path']]=r
 def indexed(ix):
  rows=family(ix)
  for r in rows:add(r)
  indices[ix['path']]=ix;return rows
 inputs=read(next(r for r in own_rows if r['path']==str(OWN/'source-inputs.json')))
 for r in inputs['files']:add(r)
 for ix in inputs['families']:indexed(ix)
 # Contracts are authenticated as retained DATA. Never expand their historical
 # user-Git inventories or before/after original-identity maps as live paths.
 for pair,contract in [(refs['actualStageReview'],refs['actualStageContract']),(root['controllerSourceReview'],None)]:
  members=indexed(pair['index']);assert members.count(pair['result'])==1
  if contract:assert members.count(contract)==1
  value=read(pair['result'])
  if contract:
   k=read(contract);assert value['state']==k['requiredReviewState']and value['verifiedPassed']is True
   for group in ['requiredFixedValues','requiredExactDescriptors','requiredVerifiedProperties']:
    for key,wanted in k.get(group,{}).items():assert value[key]==wanted
   assert value['coverage']==k['requiredCoverage']
   for r in k['requiredExactDescriptors'].values():
    if type(r)is dict and set(r)=={'path','sha256','bytes'}:add(r)
  else:assert value['state']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_NATIVE_CONTROLLER_SOURCE_REVIEW_PASSED_V1'and value['controllerSourceIndexSha256']==own['sha256']and value['sourceReviewPassed']is value['sourceOnly']is True and value['ownerActionsInvoked']is False
 stage=read(refs['stageJournal']);assert stage['state']=='NODE_CRYPTO_HASH_HMAC357_SOURCE_STAGED_NOT_BUILT_V2'and stage['sourceIndexSha256']==SOURCE_SHA
 assert stage['configuredSourceRoot']==str(SOURCE)and len(stage['copies'])==1642 and len(stage['embeddingDataCompleted'])==3
 for r in stage['copies']:
  assert not r['path'].startswith('/')and all(x not in('','.','..')for x in r['path'].split('/'));add(dict(path=str(SOURCE/r['path']),sha256=r['sha256'],bytes=r['bytes']))
 for r in stage['embeddingDataCompleted']:add(r['target'])
 add(row(SOURCE/'.git/HEAD'));assert(SOURCE/'.git/HEAD').read_text()=='54b3329b3ce818fd1f244e871e9c259b63667cda\n'
 assert str(refs['configuredSourceRoot'])==str(SOURCE)and refs['workRoot']==str(WORK)and refs['freezeRoot']==str(FREEZE)
 if root['phase']=='freeze':
  # Full future BUILD proof and regular-input closure is read with stdlib gates
  # BEFORE the first custom own module import. Historical nested Git/preinstall
  # observations are not silently treated as live originals.
  pair=root['actualBuildReview'];members=indexed(pair['index']);assert members.count(pair['result'])==members.count(root['actualBuildContract'])==1
  proof=read(pair['result']);contract=read(root['actualBuildContract']);assert proof['schemaVersion']==1 and proof['state']==contract['requiredReviewState']=='INDEPENDENT_NODE_CRYPTO_HASH_HMAC357_NATIVE_BUILD_RESULTS_REVIEW_PASSED_V1'and proof['verifiedPassed']is True
  for group in ['requiredFixedValues','requiredExactDescriptors','requiredVerifiedProperties']:
   for k,v in contract.get(group,{}).items():assert proof[k]==v
  if 'requiredCoverage'in contract:assert proof['coverage']==contract['requiredCoverage']
  for r in contract.get('requiredExactDescriptors',{}).values():
   if type(r)is dict and set(r)=={'path','sha256','bytes'}:add(r)
   elif type(r)is dict and set(r)=={'index','result'}:assert indexed(r['index']).count(r['result'])==1
  for k in ['actualBuildResult','engine','metadata','inputHashes','referenceAliases']:add(proof[k])
  ledger=read(proof['inputHashes']);assert ledger['schemaVersion']==1 and type(ledger['files'])is list and 0<len(ledger['files'])<=65536 and len(ledger['files'])==len({r['path']for r in ledger['files']})
  for r in ledger['files']:add(r)
  aliases=read(proof['referenceAliases']);assert aliases['schemaVersion']==1 and type(aliases['symlinks'])is list and type(aliases['archiveHardlinks'])is list
 for r in captured.values():checked(r)
 frame=dict(config=cfg,configRow=config_row,root=root,ownIndex=own,ownRows=own_rows,refs=refs,stage=stage,captured=captured,familyIndices=indices)
 # Actual own modules are first imported only after complete physical intake.
 io=load(frame,'io_guard.py');cap=io.Capture()
 for r in captured.values():cap.add(r)
 for ix in indices.values():cap.family(ix)
 frame['io']=io;frame['capture']=cap;models=load(frame,'models.py');frame['models']=models
 frame['loadOwn']=lambda name:load(frame,name)
 models.cache_plan(read(refs['cachePlan']),refs)
 models.stage(read(refs['actualStageReview']['result']),refs);models.root(root,own,refs,ENV_POLICY);models.peer(read(root['controllerSourceReview']['result']),own,refs,ENV_POLICY)
 for pair in [refs['integrationSourceReview']]:
  members=cap.family(pair['index']);assert members.count(pair['result'])==1;p=io.read(pair['result']);assert p['sourceIndexSha256']==SOURCE_SHA and p['sourceReviewPassed']is True and p['sourceOnly']is True and p['ownerActionsInvoked']is False
 if root['phase']=='freeze':
  proof,k=cap.proof(root['actualBuildReview'],root['actualBuildContract'],models.BUILD_STATE);models.build_proof(proof,k,own,refs);frame['buildProof']=proof
  cap.add(proof['inputHashes']);cap.add(proof['referenceAliases'])
  ledger=io.read(proof['inputHashes']);assert ledger['schemaVersion']==1 and isinstance(ledger['files'],list)and 0<len(ledger['files'])<=65536 and len(ledger['files'])==len({r['path']for r in ledger['files']})
  for r in ledger['files']:cap.add(r)
  aliases=io.read(proof['referenceAliases']);frame['buildLedger']=ledger;frame['buildAliases']=aliases
 frame['configuredTree']=read(next(r for r in own_rows if r['path']==str(OWN/'configured-tree.json')))
 frame['originalModes']={r['path']:stat.S_IMODE(checked(r).stat().st_mode)for r in captured.values()}
 recheck(frame);return frame

def recheck(frame):
 frame['capture'].recheck()
 for r in frame['stage']['copies']:
  p=checked(dict(path=str(SOURCE/r['path']),sha256=r['sha256'],bytes=r['bytes']));s=p.stat();assert stat.S_IMODE(s.st_mode)==0o600 and s.st_nlink==1
 for r in frame['stage']['embeddingDataCompleted']:
  p=checked(r['target']);assert stat.S_IMODE(p.stat().st_mode)==0o600 and p.stat().st_nlink==1
 assert(SOURCE/'.git/HEAD').read_text()=='54b3329b3ce818fd1f244e871e9c259b63667cda\n'
 for path,mode in frame['originalModes'].items():assert stat.S_IMODE(checked(frame['capture'].files[path]).stat().st_mode)==mode
 for r in frame['refs']['hostTools']:
  selected=shutil.which(r['name'],path=frame['refs']['hostPath']);assert selected and str(Path(selected).resolve())==r['executable']['path'];checked(r['executable'])
 for r in frame.get('buildAliases',{}).get('symlinks',[]):
  p=Path(r['path']);assert p.is_symlink()and os.readlink(p)==r['linkText']and str(p.resolve())==r['resolved']
 for r in frame.get('buildAliases',{}).get('archiveHardlinks',[]):
  a=Path(r['path']).stat();b=Path(r['target']).stat();assert(a.st_dev,a.st_ino)==(b.st_dev,b.st_ino)
 tree=frame['configuredTree'];assert tree['root']==str(SOURCE)
 regular={r['file']['path']for r in tree['files']};links={r['path']:r['linkText']for r in tree['documentationLinks']};actual=set();actual_links={}
 for p in SOURCE.rglob('*'):
  if p.is_symlink():actual_links[p.relative_to(SOURCE).as_posix()]=os.readlink(p)
  elif p.is_file():actual.add(str(p))
 assert actual==regular and actual_links==links
 for r in tree['files']:assert stat.S_IMODE(checked(r['file']).stat().st_mode)==r['mode']
 # Source stage's historical original user .git equality is retained DATA only.
 # No current original repository Git inventory is consulted here.


def launcher(frame):
 io=frame['io'];phase=frame['root']['phase'];observer=Path(frame['root']['rootObserverOutputRoot'])
 for p in([WORK,FREEZE,Path(frame['refs']['buildOutputRoot']),Path(frame['root']['externalOutputRoot']),observer]if phase=='build'else[FREEZE,Path(frame['root']['externalOutputRoot']),observer]):absent(p)
 os.umask(0o077);observer.mkdir(mode=0o700)
 child,removed=clean_environment(dict(os.environ));argv=[frame['refs']['python']['path'],'-B','-I',str(OWN/'controller.py'),'parent',json.dumps(frame['configRow'],separators=(',',':'))]
 io.write(observer/'preentry-environment.json',dict(schemaVersion=1,rootAuthority=frame['config']['rootAuthority'],policy=ENV_POLICY,removedVariableNames=removed,environmentValuesRecorded=False,requiredEntriesAbsent=True,userHomeVariablesPreserved=True,argv=argv,phase=phase))
 recheck(frame);os.execve(argv[0],argv,child)


def parent(frame):
 assert clean_environment(dict(os.environ))[1]==[]
 io=frame['io'];root=frame['root'];refs=frame['refs'];out=Path(root['externalOutputRoot']);absent(out)
 pre=io.read(io.row(Path(root['rootObserverOutputRoot'])/'preentry-environment.json'));assert pre['rootAuthority']==frame['config']['rootAuthority']and pre['policy']==ENV_POLICY and pre['requiredEntriesAbsent']is True
 monitor_row=refs['monitorEntry'];assert monitor_row in io.family(refs['monitorIndex']);io.checked(monitor_row)
 spec=importlib.util.spec_from_file_location('genuine0af_hash_hmac_native_owned_monitor',monitor_row['path']);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);recheck(frame)
 out.mkdir(mode=0o700);argv=[refs['python']['path'],'-B','-I',str(OWN/'controller.py'),'worker',json.dumps(frame['configRow'],separators=(',',':'))]
 try:t=m.monitor(argv,str(REPO),{**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},out,root['externalParentDeadlineSeconds'],frame['config']['rootAuthority'])
 finally:recheck(frame)
 assert t['rawExitCode']==0 and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True and t['forcedCleanup']is t['timeout']is False
 for key in ['signals','errors','interruptedSignals','remainingObservedPids']:assert t[key]==[]
 assert t['stderr']['bytes']==0
 if root['phase']=='build':
  result=io.read(io.row(Path(refs['buildOutputRoot'])/'result.json'));assert result['rootAuthority']==frame['config']['rootAuthority']and result['sourceIndexSha256']==SOURCE_SHA and result['controllerIndex']==frame['ownIndex']
  assert result['state']=='native-build-completed-runtime-pending'and result['rawChildExitCode']==result['launcherExitCode']==0 and result['evidenceComplete']is result['lifecycleComplete']is True
  assert result['ownedGroupCleanup']['complete']is True and result['ownedGroupCleanup']['events']==result['ownedGroupCleanup']['errors']==[]
  assert result['allSourceStageOriginalAndCacheInputsPreserved']is True and len(result['cacheCopiesCompleted'])==4
  for k in ['engine','metadata','buildLog']:io.checked(result[k])
 else:
  result=io.read(io.row(FREEZE/'normal-off-freeze-receipt.json'));assert result['controllerSourceIndexSha256']==frame['ownIndex']['sha256']and result['state']=='NODE_CRYPTO_HASH_HMAC357_NORMAL_OFF_FREEZE_COMPLETE_UNREVIEWED_V1'
 recheck(frame)
 print(json.dumps(dict(schemaVersion=1,state='NODE_CRYPTO_HASH_HMAC357_NATIVE_PHASE_RAW_ZERO_UNREVIEWED_V1',phase=root['phase'],sourceIndexSha256=SOURCE_SHA,result=io.row(Path(refs['buildOutputRoot'])/'result.json')if root['phase']=='build'else io.row(FREEZE/'normal-off-freeze-receipt.json'),externalParentTerminal=io.row(out/'terminal.json'),requiresIndependentActualReview=True,engineExecuted=False,cryptoOperationsInvoked=False,operationalAdmission=False)),flush=True)


def main():
 assert len(sys.argv)==3 and sys.argv[1]in['launcher','parent','worker','admit'];frame=bootstrap(json.loads(sys.argv[2]));operation=sys.argv[1]
 try:
  if operation=='launcher':return launcher(frame)
  if operation=='parent':return parent(frame)
  assert clean_environment(dict(os.environ))[1]==[]
  if operation=='admit':
   assert frame['root']['phase']=='freeze';value=load(frame,'admission.py').admit(frame,recheck);print(json.dumps(value),flush=True);return value
  module=load(frame,'build_body.py'if frame['root']['phase']=='build'else'freeze_body.py');return module.run(frame,recheck)
 finally:recheck(frame)
if __name__=='__main__':main()
