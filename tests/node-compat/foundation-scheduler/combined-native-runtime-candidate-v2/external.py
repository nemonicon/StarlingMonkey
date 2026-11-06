"""Dormant owned full80 runtime controller; no action on import."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/combined-native-runtime-candidate-v2'
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


def child_environment(original,tmp,package):
 forbidden=['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK','NODE_COMPAT_LEGACY_COMPONENTIZER','NODE_COMPAT_COMPONENTIZE_MODULE']
 env={k:v for k,v in original.items()if k not in forbidden};env.update(TMPDIR=str(tmp),NODE_COMPAT_TOOLCHAIN=package,PYTHONDONTWRITEBYTECODE='1',RAYON_NUM_THREADS='1',PREVIEW2_SHIM_DEBUG='0')
 for k in ['HOME','home','CODEX_HOME']:assert env.get(k)==original.get(k)
 return env

def parent(config_row):
 assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and Path(__file__).resolve().parent==OWN
 captured={};identities={};families=[];package=None
 def keep(d):
  p=checked(d);s=p.lstat();identity=(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  if d['path']in captured:assert captured[d['path']]==d and identities[d['path']]==identity
  captured[d['path']]=d;identities[d['path']]=identity
 def indexed(d):
  rows=family(d)
  for r in rows:keep(r)
  families.append(d);return rows
 def proof(pair):
  rows=indexed(pair['index']);assert rows.count(pair['result'])==1;return read(pair['result'])
 def roles(value):
  if type(value)is dict:
   if set(value)=={'path','sha256','bytes'}:keep(value)
   elif set(value)=={'index','result'}:proof(value)
   else:
    for x in value.values():roles(x)
  elif type(value)is list:
   for x in value:roles(x)
 def contract(pair,descriptor,state):
  rows=indexed(pair['index']);assert rows.count(pair['result'])==rows.count(descriptor)==1
  p=read(pair['result']);k=read(descriptor);assert p['schemaVersion']==1 and p['state']==state and p['verifiedPassed']is True and k['requiredReviewState']==state
  for group in ['requiredFixedValues','requiredExactDescriptors']:
   for name,value in k.get(group,{}).items():assert p[name]==value
  if 'requiredCoverage'in k:assert p['coverage']==k['requiredCoverage']
  roles(k.get('requiredExactDescriptors',{}));return p,k
 def recheck():
  for r in list(captured.values()):keep(r)
  for r in families:family(r)
 try:
  keep(config_row);cfg=read(config_row);assert cfg['schemaVersion']==1 and cfg['state']=='COMBINED355_RUNTIME_CONFIG_V2';own=cfg['sourceIndex'];assert own['path']==str(OWN/'index.json');rows=indexed(own)
  refs=read(next(r for r in rows if r['path']==str(OWN/'references.json')));inputs=read(next(r for r in rows if r['path']==str(OWN/'source-inputs.json')));assert refs['originalRoot']==str(OWN)
  for r in inputs['files']:keep(r)
  for r in inputs['families']:indexed(r)
  for bound in inputs['boundaries']:
   keep(bound['manifest']);b=read(bound['manifest']);assert len(b[bound['field']])==bound['expectedRows']
   for r in b[bound['field']]:keep(r)
   for r in b.get(bound['familyField'],[]):indexed(r)
  keep(refs['packageInventory']);package=read(refs['packageInventory'])['package'];package_tree(package,refs['loaderPackageRoot'],keep)
  root_row=cfg['rootAuthority'];keep(root_row);root=read(root_row);phase=cfg['phase'];assert phase in ['map','run','fatal']and root['phase']==phase and root['state']=='ROOT_REVIEWED_COMBINED355_NATIVE_RUNTIME_PHASE_V2'and root['sourceIndex']==own and 'config'not in root
  assert root['entry']==next(r for r in rows if r['path']==str(OWN/'entry.mjs'))and root['externalController']==next(r for r in rows if r['path']==str(OWN/'external.py'))
  fixture=next(x for x in read(refs['fixtureCatalogue'])['fixtures']if x['id']==cfg['fixtureId']);assert fixture['id']!='init-fatal'and root['fixtureId']==fixture['id']and root['fixtureSource']==fixture['source']and root['fixtureWit']==fixture['wit']and root['selectedInterfaces']==fixture['selectedInterfaces']
  assert root['nativeSourceFiles']==355 and root['externalEmbeddingSources']==3 and root['fullMetadataFields']==80 and root['selectedWholeManifests']==11 and root['nativeEngine']==refs['nativeEngine']and root['nativeMetadata']==refs['nativeMetadata']
  assert root['expectedFatalCallbackAcceptanceAllowed']is root['current355NativeCallbackDiagnosticAvailable']is False
  assert root['nativeReadOnlyApiAllowed']is True and root['nativeReadOnlyConfig']==refs['readOnlyConfig']and root['actualBootstrapReview']==refs['actualBootstrapReview']and root['actualReadOnlyReview']==refs['actualReadOnlyReview']
  assert root['mappingOnlyAllowed']is(phase=='map')and root['jcoCompilerHelpersAllowed']is(phase=='map')and root['generatedApplicationImportAllowed']is(phase!='map')and root['ordinaryGuestExportsAllowed']is(phase!='map')and root['stockWasmtimeAllowed']is(phase!='map')
  assert root['requiredExternalParentDeadlineSeconds']==1200 and root['childDeadlineMs']==180000 and root['maxOutputBytes']==16777216 and root['wallClockCoarseAllowanceMs']==1 and root['clockAdjustmentPolicy']=='inconclusive-if-host-wall-clock-decreases'and root['performanceTimeOriginEpochAssumed']is False
  for name in ['componentConstructionAllowed','nativeBuildAllowed','nativeFreezeAllowed','keyOrCryptoAllowed','gcOrFaultActionsAllowed','debugOrUnsafeResetAllowed','customHostServicesAllowed','adapterPromotionAllowed','metadataProjectionAllowed','nativeDiagnosticVariantAllowed','fullClockProfileAcceptance','runtimeAcceptanceClaim','operationalAdmission','timingAllowed']:assert root[name]is False
  p=proof(root['sourceIndependentReview']);assert p['state']=='INDEPENDENT_COMBINED355_NATIVE_RUNTIME_SOURCE_REVIEW_PASSED_V2'and p['sourceIndexSha256']==own['sha256']and p['sourceOnly']is p['sourceReviewPassed']is True and p['ownerActionsInvoked']is False
  fp=proof(refs['fixtureSourcePeer']);assert fp['state']==refs['fixtureReviewRequiredState']and fp['fixtureSourceIndexSha256']==refs['fixtureSourceIndex']['sha256']
  contract(refs['actualBootstrapReview'],refs['actualBootstrapContract'],'INDEPENDENT_COMBINED355_NORMAL_OFF_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1');contract(refs['actualReadOnlyReview'],refs['actualReadOnlyContract'],refs['actualReadOnlyRequiredState'])
  slot=refs['artifactSlots'][fixture['id']]
  if slot['actualReview']is not None:assert root['actualArtifactReview']==slot['actualReview']and root['actualArtifactContract']==slot['contract']
  p,k=contract(root['actualArtifactReview'],root['actualArtifactContract'],'INDEPENDENT_COMBINED355_'+fixture['id'].replace('-','_').upper()+'_COMPONENT_ARTIFACT_REVIEW_PASSED_V1')
  assert p['fixtureId']==fixture['id']and p['componentSourceIndexSha256']==refs['callerSourceIndex']['sha256']and p['artifacts']==k['artifacts']and p['artifacts']['fixtureSource']==fixture['source']and p['artifacts']['fixtureWit']==fixture['wit'];roles(k['artifacts']);roles(p['generatedFiles'])
  if phase!='map':
   p,k=contract(root['actualMappedReview'],root['actualMappedContract'],'INDEPENDENT_COMBINED355_MAPPED_OUTPUT_REVIEW_PASSED_V2');assert p['sourceIndexSha256']==own['sha256']and p['fixtureId']==fixture['id']and k['mappedFiles']==p['mappedFiles'];roles(p['mappedFiles'])
  assert refs['monitorEntry']in indexed(refs['monitorIndex']);assert checked(refs['python'])==Path(sys.executable).resolve();keep(refs['node']);recheck()
  output=Path(refs['outputBase']+'-'+fixture['id']+'-'+phase);external=Path(str(output)+'-external-root');tmp=Path(str(output)+'-tmp');assert root['outputRoot']==str(output)and root['externalOutputRoot']==str(external)
  for p in [output,external,tmp]:
   assert not p.exists()
   for q in(p,*p.parents):assert not q.is_symlink()
  env=child_environment(dict(os.environ),tmp,refs['loaderPackageRoot']);spec=importlib.util.spec_from_file_location('genuine0af_combined355_runtime_monitor',checked(refs['monitorEntry']));monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor);recheck();tmp.mkdir(mode=0o700);external.mkdir(mode=0o700)
  argv=[refs['node']['path'],str(OWN/'entry.mjs'),'parent',json.dumps(config_row,separators=(',',':'))];terminal=monitor.monitor(argv,str(REPO),env,external,1200,root_row);recheck()
  print(json.dumps(dict(schemaVersion=1,state='COMBINED355_RUNTIME_RAW_TERMINAL_UNREVIEWED_V2',phase=phase,fixtureId=fixture['id'],terminal=row(external/'terminal.json'),rawExitCode=terminal['rawExitCode'],requiresIndependentActualReview=True,operationalAdmission=False)),flush=True)
  assert terminal['rawExitCode']==0 and terminal['timeout']is terminal['forcedCleanup']is False and terminal['parentOwnedGroupGone']is terminal['allObservedOwnedGroupsGone']is True
  for key in ['errors','signals','interruptedSignals','remainingObservedPids']:assert terminal[key]==[]
 finally:
  recheck()
  if package is not None:package_tree(package,refs['loaderPackageRoot'],checked)
if __name__=='__main__':
 assert len(sys.argv)==2
 parent(json.loads(sys.argv[1]))
