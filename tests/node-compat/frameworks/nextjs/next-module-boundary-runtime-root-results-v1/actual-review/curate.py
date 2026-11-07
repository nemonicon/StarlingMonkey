"""Retain only named completed DATA/Source/images; no tools, engines or actors."""
from pathlib import Path
import gzip, hashlib, io, json, os, stat, tarfile
HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
KIND = 'runtime'
CTOR_ROOT = BASE/'next-module-boundary-construction-root-results-v1'
RUNTIME_ROOT = BASE/'next-module-boundary-runtime-root-results-v1'
CTOR = Path('/private/tmp/starling-node-compat/next-module-boundary-component-v1-real-next-guard-ca84-first')
RUNTIME = Path('/private/tmp/starling-node-compat/next-wasmtime-deployment-guard-ca84-next-requests-first')

def physical(p):
 s=p.stat();return [s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def main():
 records=[]; payload={}; originals={}; roles={}
 def add(name,path,role=None):
  path=Path(path);assert path.is_absolute() and path.resolve()==path
  assert all(not q.is_symlink() for q in (path,*path.parents))
  before=physical(path);assert stat.S_ISREG(before[2]) and before[3]==1
  data=path.read_bytes();assert physical(path)==before
  kind='observed-fixture-screenshot' if path.suffix=='.png' else 'retained-text'
  if kind=='observed-fixture-screenshot':assert data.startswith(b'\x89PNG\r\n\x1a\n')
  else:data.decode('utf-8');assert b'\0' not in data
  ref=dict(path=str(path),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
  if str(path) in originals:
   prior=originals[str(path)];assert prior['original']==ref and prior['physicalBefore']==before
   if role:roles[role]=prior['member']
   return prior['member']
  assert name not in payload
  entry=dict(member=name,original=ref,mode=stat.S_IMODE(before[2]),physicalBefore=before,role=kind)
  records.append(entry);originals[str(path)]=entry;payload[name]=data
  if role:roles[role]=name
  return name
 def tree(prefix,path,exclude=()):
  for q in sorted(Path(path).rglob('*')):
   rel=q.relative_to(path);assert not q.is_symlink() and (q.is_dir() or q.is_file())
   if q.is_file() and not any(x in exclude for x in rel.parts):add(prefix+'/'+rel.as_posix(),q)
 def family(name):
  path=BASE/name;index=json.loads((path/'index.json').read_bytes())
  add('source/'+name+'/index.json',path/'index.json')
  for r in index['files']:
   rel=Path(r['path']);assert not rel.is_absolute() and '..' not in rel.parts
   add('source/'+name+'/'+r['path'],path/rel)
   assert originals[str(path/rel)]['original']==dict(r,path=str(path/rel))
 for name in ['next-module-boundary-construction-v1','next-component-entry-fixes-v5','regexp-unicode-probe-candidate-v1','next-module-fileurl-boundary-candidate-v1','next-native-portable-build-preparation-v4']:
  family(name)
 if KIND=='runtime':
  family('wasmtime-deployment-guard-candidate-v1');family('browser-hydration-candidate-v3')
 work=CTOR if KIND=='construction' else RUNTIME
 tree('work',work,('app','cache','tmp','returned-component.wasm'))
 tree('outer',Path(str(work)+'-external-root'))
 parent=CTOR_ROOT if KIND=='construction' else RUNTIME_ROOT
 for q in sorted(parent.iterdir()):
  if q.is_file() and q.name not in ['README.md','index.json']:
   add('root/'+q.name,q)
 ctor_result=json.loads((CTOR/'result.json').read_bytes())
 ctor_auth=json.loads(Path(ctor_result['rootAuthority']['path']).read_bytes())
 if KIND=='runtime':
  for q in sorted(CTOR_ROOT.iterdir()):
   if q.is_file() and q.name not in ['README.md','index.json']:add('ctor-root/'+q.name,q)
  for name in ['result.json','component-audit.json']:
   add('constructor/'+name,CTOR/name)
  tree('constructor-outer',Path(str(CTOR)+'-external-root'))
  for command in ctor_result['commands']:
   tree('constructor/'+command['label'],CTOR/command['label'])
  runtime_result=json.loads((RUNTIME/'result.json').read_bytes())
  for key in ['applicationInputs','applicationBuildResult']:
   add('inputs/'+key+'.json',Path(runtime_result[key]['path']))
  for entry in runtime_result['cacheInventory']:
   add('observed-cache/'+entry['relativePath'],entry['path'])
  policy=json.loads((BASE/'next-request-regression-check-v3/policy.json').read_bytes())
  add('inputs/fixture-contract.json',policy['roles']['fixtureContract']['path'])
  add('inputs/asset-pins.json',policy['roles']['assetPins']['path'],'assetPins')
  add('inputs/shared-supplemental.mjs',BASE/'wasmtime-deployment-candidate-v8/supplemental.mjs')
  add('inputs/full-native-metadata.json',ctor_auth['nativeMetadata']['path'])
  add('inputs/actual-native-build-review.json',BASE/'next-module-boundary-native-root-results-v1/actual-build-review.json')
 # Genuine finite build receipts, never tool/library/engine/825-tree payloads.
 for n,r in enumerate(ctor_auth['engineBuildEvidence']):add('native-evidence/'+str(n).zfill(2)+'-'+Path(r['path']).name,r['path'])
 assert len(records)<2000 and sum(len(v) for v in payload.values())<64*1024**2
 output=io.BytesIO()
 with gzip.GzipFile(fileobj=output,mode='wb',mtime=0) as gz:
  with tarfile.open(fileobj=gz,mode='w') as tf:
   for r in records:
    b=payload[r['member']];i=tarfile.TarInfo(r['member']);i.size=len(b);i.mode=r['mode'];i.mtime=0;tf.addfile(i,io.BytesIO(b))
 for r in records:
  path=Path(r['original']['path']);assert physical(path)==r['physicalBefore'] and path.read_bytes()==payload[r['member']]
 data=output.getvalue();index=dict(schemaVersion=1,capsuleKind=KIND,archive=dict(path='data.tar.gz',sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)),memberCount=len(records),expandedBytes=sum(len(v) for v in payload.values()),roles=roles,members=records,allSelectedOriginalPhysicalAndContentBookendsUnchanged=True,actorOrToolInvoked=False,componentEngineLibraryPackageAppOr825TreesIncluded=False,scope='Finite completed DATA/explicit small Source families and observed PNGs only; logical binary/tree descriptors retained without their payloads. No recursive DATA archives.')
 for name,b in [('data.tar.gz',data),('payload-index.json',(json.dumps(index,indent=2)+'\n').encode())]:
  fd=os.open(HERE/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
  with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 print(json.dumps(dict(capsuleKind=KIND,memberCount=len(records),expandedBytes=index['expandedBytes'],archive=index['archive'],sourceAndDataOnly=True,actorInvoked=False)))
if __name__=='__main__':main()
