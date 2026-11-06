"""Unexecuted Source-only dormant combined355 owned caller. Stdlib only before authentication."""
from pathlib import Path
import hashlib,importlib.util,json,os,stat,sys
REPO=Path('/Users/dan/dev/StarlingMonkey')
OWN=REPO/'tests/node-compat/foundation-scheduler/combined-native-component-caller-candidate-v1'
BASE='/private/tmp/starling-node-compat/combined-native-component-caller-v1'
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

def phase_paths(phase,fixture_id):
 assert phase in ['bundle','construct']and fixture_id in ['resource','pure','fatal','init-fatal','clock-snapshot','surviving-interest']
 output=Path(BASE+'-'+phase+'-'+fixture_id)
 return output,Path(str(output)+'-external-root'),Path(str(output)+'-tmp'),1200 if phase=='bundle'else 2400

def child_environment(original,tmp,package):
 forbidden=['NODE_OPTIONS','NODE_PATH','PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','LD_PRELOAD','LD_LIBRARY_PATH','DYLD_INSERT_LIBRARIES','DYLD_LIBRARY_PATH','NAPI_RS_NATIVE_LIBRARY_PATH','NAPI_RS_FORCE_WASI','NAPI_RS_WASI_FLAVOR','NAPI_RS_ENFORCE_VERSION_CHECK','NODE_COMPAT_LEGACY_COMPONENTIZER','NODE_COMPAT_COMPONENTIZE_MODULE']
 env={k:v for k,v in original.items()if k not in forbidden};env.update(TMPDIR=str(tmp),NODE_COMPAT_TOOLCHAIN=package,PYTHONDONTWRITEBYTECODE='1')
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

def parent(config_row,phase):
 assert __debug__ and sys.dont_write_bytecode and sys.flags.isolated and Path(__file__).resolve().parent==OWN
 assert phase in ['bundle','construct'];captured={};identities={};families=[]
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
  for x in list(captured.values()):keep(x)
  for x in families:family(x)
 try:
  keep(config_row)
  cfg=read(config_row);assert cfg['schemaVersion']==1 and cfg['state']=='COMBINED355_COMPONENT_CALLER_CONFIG_V1'and cfg['phase']==phase;own=cfg['sourceIndex'];assert own['path']==str(OWN/'index.json');rs=indexed(own);refs=read(next(x for x in rs if x['path']==str(OWN/'references.json')));inputs=read(next(x for x in rs if x['path']==str(OWN/'source-inputs.json')))
  for x in inputs['files']:keep(x)
  for x in inputs['families']:indexed(x)
  for bound in inputs['boundaries']:
   b=read(bound['manifest']);keep(bound['manifest']);assert len(b[bound['field']])==bound['expectedRows']
   for x in b[bound['field']]:keep(x)
   for ix in b.get(bound['familyField'],[]):indexed(ix)
  package=read(refs['packageInventory']);keep(refs['packageInventory']);package_tree(package['package'],refs['loaderPackageRoot'],keep)
  assert all(refs[k]is not None for k in ['fixtureSourcePeer','readOnlyConfig','actualReadOnlyReview','actualReadOnlyContract','actualReadOnlyData','actualReadOnlyRequiredState','actualBootstrapReview','actualBootstrapContract']), 'Actual prerequisite pending; Source draft has no action authority'
  catalogue=read(refs['fixtureCatalogue']);fixture=next(x for x in catalogue['fixtures']if x['id']==cfg['fixtureId']);keep(fixture['source']);keep(fixture['wit']);root_row=cfg['rootAuthority'];root=read(root_row);keep(root_row)
  assert root['schemaVersion']==1 and root['state']=='ROOT_REVIEWED_COMBINED355_COMPONENT_CALLER_V1'and root['phase']==phase and root['sourceIndex']==own and root['entry']==next(r for r in rs if r['path']==str(OWN/'entry.mjs'))and root['externalController']==next(r for r in rs if r['path']==str(OWN/'external.py'))
  assert root['fixtureId']==fixture['id']and root['fixtureSource']==fixture['source']and root['fixtureWit']==fixture['wit']and root['worldName']==fixture['worldName']
  assert root['nativeSourceFiles']==355 and root['externalEmbeddingSources']==3 and root['fullMetadataFields']==80 and root['selectedWholeManifests']==11 and root['nativeEngine']==refs['nativeEngine']and root['nativeMetadata']==refs['nativeMetadata']
  assert root['bundlePreparationAllowed']is(phase=='bundle')and root['componentConstructionAllowed']is(phase=='construct')and root['engineInitializationAllowed']is(phase=='construct')and root['nativeReadOnlyApiAllowed']is True
  for k in ['ordinaryGuestExportsAllowed','generatedModuleImportAllowed','keyOrCryptoAllowed','hostServersAllowed','adapterPromotionAllowed','defaultPackagerReplacementAllowed','nativeBuildAllowed','nativeFreezeAllowed','gcReconfigureAllowed','unsafeResetAllowed','metadataProjectionAllowed','sourcePromotionAllowed','operationalAdmission','runtimeAcceptanceClaim','timingAllowed']:assert root[k]is False
  assert root['actualComponentReview']is root['actualRuntimeAuthority']is None
  assert root['readOnlyConfig']==refs['readOnlyConfig']and root['actualBootstrapReview']==refs['actualBootstrapReview']and root['actualReadOnlyReview']==refs['actualReadOnlyReview']
  assert root['selectedInterfaces']==fixture['selectedInterfaces']and root['disableFeatures']==fixture['disableFeatures'];assert fixture['id']!='pure'or root['selectedInterfaces']==[]
  output,external,tmp,deadline=phase_paths(phase,fixture['id'])
  assert root['outputRoot']==str(output)and root['externalRoot']==str(external)and root['privateTemporaryRoot']==str(tmp)and root['ownedNodeDeadlineSeconds']==deadline
  peer=proof(root['sourceIndependentReview']);assert peer['state']=='INDEPENDENT_COMBINED355_COMPONENT_CALLER_SOURCE_REVIEW_PASSED_V1'and peer['componentSourceIndexSha256']==own['sha256']and peer['sourceOnly']is peer['sourceReviewPassed']is True and peer['ownerActionsInvoked']is False
  proof(refs['nativeApiSourcePeer']);proof(refs['loaderSourcePeer']);fp=proof(refs['fixtureSourcePeer']);assert fp['state']==refs['fixtureReviewRequiredState']and fp[refs['fixtureReviewSourceField']]==refs['fixtureSourceIndex']['sha256']
  for pair,key,expected in [(refs['actualBootstrapReview'],'actualBootstrapContract','INDEPENDENT_COMBINED355_NORMAL_OFF_BOOTSTRAP_RESULTS_REVIEW_PASSED_V1'),(refs['actualReadOnlyReview'],'actualReadOnlyContract',refs['actualReadOnlyRequiredState'])]:
   p=proof(pair);contract=read(refs[key]);keep(refs[key]);assert p['schemaVersion']==1 and p['state']==expected and p['verifiedPassed']is True and contract['requiredReviewState']==expected
   for group in ['requiredFixedValues','requiredExactDescriptors']:
    for k,v in contract.get(group,{}).items():assert p[k]==v
   if 'requiredCoverage'in contract:assert p['coverage']==contract['requiredCoverage']
   def exact_roles(v):
    if type(v)is dict:
     if set(v)=={'path','sha256','bytes'}:keep(v)
     elif set(v)=={'index','result'}:proof(v)
     else:
      for x in v.values():exact_roles(x)
    elif type(v)is list:
     for x in v:exact_roles(x)
   exact_roles(contract.get('requiredExactDescriptors',{}))
  monitor_ix=refs['monitorIndex'];assert refs['monitorEntry']in indexed(monitor_ix);assert checked(refs['python'])==Path(sys.executable).resolve();keep(refs['node']);recheck()
  for p in [output,external,tmp]:
   assert not p.exists()
   for q in(p,*p.parents):assert not q.is_symlink()
  # Explicit selected child dictionary; preserve homes and avoid global mutation.
  env=child_environment(dict(os.environ),tmp,refs['loaderPackageRoot'])
  spec=importlib.util.spec_from_file_location('genuine0af_combined355_component_monitor',checked(refs['monitorEntry']));monitor=importlib.util.module_from_spec(spec);spec.loader.exec_module(monitor);recheck();tmp.mkdir(mode=0o700);external.mkdir(mode=0o700)
  argv=[refs['node']['path'],str(OWN/'entry.mjs'),phase,json.dumps(config_row,separators=(',',':'))];terminal=monitor.monitor(argv,str(REPO),env,external,deadline,root_row);recheck()
  # Durable monitor files exist before any success/refusal interpretation.
  print(json.dumps(dict(schemaVersion=1,state='COMBINED355_CALLER_RAW_TERMINAL_UNREVIEWED_V1',phase=phase,fixtureId=fixture['id'],terminal=row(external/'terminal.json'),rawExitCode=terminal['rawExitCode'],requiresIndependentActualReview=True,operationalAdmission=False)),flush=True)
  clean_terminal(terminal)
 finally:recheck();package_tree(package['package'],refs['loaderPackageRoot'],checked)if'package'in locals()else None
if __name__=='__main__':
 assert len(sys.argv)==3
 parent(json.loads(sys.argv[2]),sys.argv[1])
