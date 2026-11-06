"""Unexecuted Source-only dormant combined355 owned caller. Stdlib only before authentication."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/combined-native-pure-runtime-control-candidate-v1'
def row(path):
 p=Path(path);a=p.stat();assert stat.S_ISREG(p.lstat().st_mode);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=p.stat();assert(a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns);return dict(path=str(p),sha256=h.hexdigest(),bytes=a.st_size)
def checked(d):
 assert type(d)is dict and set(d)=={'path','sha256','bytes'}and type(d['bytes'])is int and d['bytes']>=0
 assert type(d['path'])is str and Path(d['path']).is_absolute()and str(Path(d['path']))==d['path']and '..'not in Path(d['path']).parts and '\\'not in d['path']and '\0'not in d['path'];assert row(d['path'])==d;return Path(d['path'])
def read(d):
 p=checked(d);assert d['bytes']<=32*1024*1024;return json.loads(p.read_bytes())
def family(d):
 value=read(d);root=Path(d['path']).parent;names={'index.json'};rows=[d]
 for r in value['files']:
  n=r['path'];assert n not in names and n and not n.startswith('/')and '\\'not in n and all(p not in('','.','..')for p in n.split('/'));names.add(n);x=dict(r,path=str(root/n));checked(x);rows.append(x)
 assert not any(p.is_symlink()for p in root.rglob('*'))and{p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}==names;return rows

def child_environment(original):
 forbidden=['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK','NODE_COMPAT_LEGACY_COMPONENTIZER','NODE_COMPAT_COMPONENTIZE_MODULE']
 env={k:v for k,v in original.items()if k not in forbidden};env.update(PYTHONDONTWRITEBYTECODE='1')
 for k in ['HOME','home','CODEX_HOME']:assert env.get(k)==original.get(k)
 return env

def clean_terminal(t):
 assert type(t['rawExitCode'])is int and t['rawExitCode']==0 and t['timeout']is t['forcedCleanup']is False and t['parentOwnedGroupGone']is t['allObservedOwnedGroupsGone']is True
 for k in ['errors','signals','interruptedSignals','remainingObservedPids']:assert t[k]==[]

def package_tree(value,root,keep):
 assert value['root']==root and len(value['files'])==4889 and len(value['links'])==21
 base=Path(root);s=base.lstat();assert stat.S_ISDIR(s.st_mode)and stat.S_IMODE(s.st_mode)==0o700
 files=set();links={}
 for r in value['files']:
  n=r['relativePath'];assert n and not n.startswith('/')and '\\'not in n and all(x not in('','.','..')for x in n.split('/'))and n not in files and r['path']==str(base/n);files.add(n);keep({k:r[k]for k in ['path','sha256','bytes']});s=(base/n).lstat();assert stat.S_IMODE(s.st_mode)==r['mode']and s.st_nlink==1
 for r in value['links']:assert r['path']not in files and r['path']not in links;links[r['path']]=r
 actual=set()
 for p in base.rglob('*'):
  n=p.relative_to(base).as_posix()
  if p.is_symlink():
   r=links[n];assert os.readlink(p)==r['target']and str(p.resolve(strict=True))==r['resolvedPath']and p.resolve(strict=True).is_relative_to(base)and p.resolve(strict=True).relative_to(base).as_posix()in files;actual.add(n)
  elif p.is_file():assert n in files;actual.add(n)
 assert actual==files|set(links)

def parent(config_row):
 if not __debug__ or not sys.dont_write_bytecode or not sys.flags.isolated:raise RuntimeError('Require unoptimized isolated bytecode-off Python')
 assert Path(__file__).resolve().parent==OWN
 captured={};identities={};families=[]
 def keep(d):
  p=checked(d);s=p.lstat();identity=(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  if d['path']in captured:assert captured[d['path']]==d and identities[d['path']]==identity
  captured[d['path']]=d;identities[d['path']]=identity
 def indexed(d):
  rs=family(d)
  for r in rs:keep(r)
  families.append(d);return rs
 def proof(pair):
  rs=indexed(pair['index']);assert pair['result']in rs;return read(pair['result'])
 def recheck():
  for r in list(captured.values()):keep(r)
  for ix in families:family(ix)
 try:
  keep(config_row);cfg=read(config_row);assert cfg['schemaVersion']==1 and cfg['state']=='COMBINED355_PURE_CONTROL_CONFIG_V1'
  own=cfg['sourceIndex'];assert own['path']==str(OWN/'index.json');rs=indexed(own)
  refs=read(next(r for r in rs if r['path']==str(OWN/'references.json')));inputs=read(next(r for r in rs if r['path']==str(OWN/'source-inputs.json')))
  for r in inputs['files']:keep(r)
  for ix in inputs['families']:indexed(ix)
  v=read(inputs['parentOnlyBoundary']);keep(inputs['parentOnlyBoundary'])
  for r in v['files']:keep(r)
  for ix in v['families']:indexed(ix)
  for bound in v['boundaries']:
   b=read(bound['manifest']);keep(bound['manifest']);assert len(b[bound['field']])==bound['expectedRows']
   for r in b[bound['field']]:keep(r)
   for ix in b.get(bound['familyField'],[]):indexed(ix)
  package=read(refs['packageInventory']);keep(refs['packageInventory']);package_tree(package['package'],refs['loaderPackageRoot'],keep)
  pure=proof(refs['actualPureReview']);contract=read(refs['actualPureContract']);keep(refs['actualPureContract'])
  assert pure['state']=='INDEPENDENT_COMBINED355_PURE_COMPONENT_ARTIFACT_REVIEW_PASSED_V1'and pure['verifiedPassed']is True and pure['componentSourceIndexSha256']==refs['callerSourceIndex']['sha256']
  assert pure['nativeSourceFiles']==355 and pure['externalEmbeddingSources']==3 and pure['fullMetadataFields']==80 and pure['selectedWholeManifests']==11 and pure['emittedImports']==[]and pure['publicAbiFunctions']==['run']
  assert contract['artifacts']==pure['artifacts']and contract['generatedFiles']==pure['generatedFiles']==refs['generated']and pure['componentSha256']==refs['component']['sha256']
  assert contract['schemaVersion']==1 and contract['requiredReviewState']==pure['state']
  for k,v in contract['requiredFixedValues'].items():assert pure[k]==v and type(pure[k])is type(v)
  assert pure['publicAbiSignatures']==[{'name':'run','params':[],'result':'string'}]
  root_row=cfg['rootAuthority'];root=read(root_row);keep(root_row)
  assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_COMBINED355_PRELIMINARY_PURE_CONTROL_V1'and root['sourceIndex']==own
  assert root['nativeSourceFiles']==355 and root['externalEmbeddingSources']==3 and root['fullMetadataFields']==80 and root['selectedWholeManifests']==11
  assert root['entry']==next(r for r in rs if r['path']==str(OWN/'entry.mjs'))and root['externalController']==next(r for r in rs if r['path']==str(OWN/'external.py'))
  for k in ['actualPureReview','actualPureContract','component','fixtureSource','readOnlyConfig']:assert root[k]==refs[k]
  for k in ['parentNativeReadOnlyApiAllowed','nodeFixtureOracleAllowed','pureGeneratedImportAllowed','pureRunAllowed','stockWasmtimeAllowed']:assert root[k]is True
  for k in ['resourceRuntimeAllowed','otherGuestAllowed','componentConstructionAllowed','transpileOrMappingAllowed','nativeBuildAllowed','nativeFreezeAllowed','keyOrCryptoAllowed','gcOrOomOrFaultAllowed','unsafeResetOrReuseAllowed','allSixFixtureGateComplete','fullSeventeenGateComplete','fullNextCompatibility','deploymentAccepted','adoptionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:assert root[k]is False
  assert root['parentDeadlineSeconds']==1200 and root['childDeadlineMs']==60000 and root['parentNativeApiCalls']==1 and root['childNativeApiCalls']==0
  assert[root[k]for k in ['nodeOracleCalls','retainedJcoCalls','freshJcoCalls','freshWasmtimeCalls','componentValues','totalValues']]==[3,3,1,3,7,10]
  peer=proof(root['sourceIndependentReview']);assert peer['state']=='INDEPENDENT_COMBINED355_PURE_RUNTIME_CONTROL_SOURCE_REVIEW_PASSED_V1'and peer['sourceIndexSha256']==own['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True
  for k in ['ownerActionsInvoked','hostActionsInvoked','runtimeActionsInvoked']:assert peer[k]is False
  assert root['outputRoot']==refs['outputRoot']and root['externalRoot']==refs['outputRoot']+'-external-root'
  for p in [Path(root['outputRoot']),Path(root['externalRoot'])]:
   assert not p.exists()
   for q in[p,*p.parents]:assert not q.is_symlink()
  assert checked(refs['python'])==Path(sys.executable).resolve();assert refs['monitorEntry']in indexed(refs['monitorIndex']);recheck()
  # Original six-argument API, original physical module context; no globals reset.
  spec=importlib.util.spec_from_file_location('genuine0af_pure_control_monitor',checked(refs['monitorEntry']));monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor)
  recheck();output=Path(root['externalRoot']);output.mkdir(mode=0o700)
  env=child_environment(dict(os.environ))
  argv=[refs['node']['path'],str(OWN/'entry.mjs'),'parent',json.dumps(config_row,separators=(',',':'))]
  terminal=monitor.monitor(argv,str(REPO),env,output,1200,root_row)
  print(json.dumps({'schemaVersion':1,'state':'COMBINED355_PURE_CONTROL_EXTERNAL_RAW_TERMINAL_UNREVIEWED_V1','terminal':row(output/'terminal.json'),'rawExitCode':terminal['rawExitCode'],'requiresIndependentActualReview':True,'runtimeAcceptanceClaim':False}),flush=True)
  clean_terminal(terminal)
 finally:
  # Attempt package and complete file/family audits independently on failures.
  errors=[]
  try:recheck()
  except BaseException as error:errors.append(error)
  if 'package'in locals():
   try:package_tree(package['package'],refs['loaderPackageRoot'],checked)
   except BaseException as error:errors.append(error)
  if errors:raise RuntimeError('Final complete source/package audit failed',errors)
if __name__=='__main__':
 assert len(sys.argv)==2
 parent(json.loads(sys.argv[1]))

