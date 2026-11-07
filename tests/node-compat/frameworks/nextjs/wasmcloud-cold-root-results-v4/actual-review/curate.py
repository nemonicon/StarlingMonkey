"""One-shot finite DATA retention. No process, oracle, tool or guest invocation."""
from pathlib import Path
import gzip,hashlib,io,json,tarfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
TEMP=Path('/private/tmp/starling-node-compat')
RUNTIME=TEMP/'next-wasmcloud-cold-v4-engine462-fresh-app-cold-v4-first'
def row(path,data=None):
 path=Path(path);data=path.read_bytes()if data is None else data
 return dict(path=str(path),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
def checked(ref):
 p=Path(ref['path']);assert p.is_absolute()and p.is_file()and not p.is_symlink()
 b=p.read_bytes();assert row(p,b)=={k:ref[k]for k in ('path','sha256','bytes')};return b
def app_guard(inventory,copy_root,root_identity):
 identities=[]
 for kind,root in [('source',Path(inventory['root'])),('copy',copy_root)]:
  assert root.resolve()==root and root.is_dir() and not root.is_symlink()
  st=root.stat();actual=dict(dev=st.st_dev,ino=st.st_ino,nlink=st.st_nlink,mode=st.st_mode&0o777)
  if kind=='source':assert actual==root_identity
  else:assert actual['mode']==0o555 and (st.st_dev,st.st_ino)!=(root_identity['dev'],root_identity['ino'])
  identities.append([kind,'.',st.st_dev,st.st_ino,st.st_nlink,st.st_mode&0o777])
  nodes=list(root.rglob('*'));assert not any(p.is_symlink()for p in nodes)
  assert all(p.is_file()or p.is_dir()for p in nodes)
  assert{p.relative_to(root).as_posix()for p in nodes if p.is_file()}=={r['path']for r in inventory['files']}
  assert{p.relative_to(root).as_posix()for p in nodes if p.is_dir()}=={r['path']for r in inventory['directories']}
  assert not(root/'.next/cache').exists()
  for r in inventory['files']:
   p=root/r['path'];checked(dict(path=str(p),sha256=r['sha256'],bytes=r['bytes']));st=p.stat()
   if kind=='source':assert(st.st_dev,st.st_ino,st.st_nlink,st.st_mode&0o777)==(r['dev'],r['ino'],r['nlink'],r['mode'])
   else:assert st.st_nlink==1 and st.st_mode&0o777==0o444 and(st.st_dev,st.st_ino)!=(r['dev'],r['ino'])
   identities.append([kind,r['path'],st.st_dev,st.st_ino,st.st_nlink,st.st_mode&0o777])
  for r in inventory['directories']:
   p=root/r['path'];st=p.stat()
   if kind=='source':assert(st.st_dev,st.st_ino,st.st_mode&0o777)==(r['dev'],r['ino'],r['mode'])
   else:assert st.st_mode&0o777==0o555
   identities.append([kind,r['path'],st.st_dev,st.st_ino,st.st_nlink,st.st_mode&0o777])
 cache=copy_root.parent/'cache';st=cache.lstat();assert cache.is_dir() and not cache.is_symlink() and cache.resolve()==cache and st.st_mode&0o777==0o700
 assert list(cache.iterdir())==[]
 identities.append(['separate-cache','.',st.st_dev,st.st_ino,st.st_nlink,st.st_mode&0o777])
 return dict(filesPerTree=len(inventory['files']),directoriesExcludingRoot=len(inventory['directories']),directoriesPerTree=1+len(inventory['directories']),bytesPerTree=inventory['bytes'],
  sourceRootIdentity=root_identity,sourceMatchesPublishedIdentity=True,copyByteIdenticalDistinctInodesAndReadOnlyModes=True,
  sourceAndCopyHaveNoCacheMountpoint=True,separateHostCacheReal0700AndEmpty=True,
  combinedIdentitySha256=hashlib.sha256(json.dumps(identities,separators=(',',':')).encode()).hexdigest())
def main():
 assert not(HERE/'data.tar.gz').exists()
 blobs={};files=[];captured={};external={};families=[]
 def add(name,path,ref=None):
  assert name not in blobs;b=checked(ref or row(path));r=row(path,b);blobs[name]=b;files.append(dict(path=name,original=r));captured[r['path']]=r;return r
 def evidence(ref,retain=True):
  checked(ref)
  if ref['path']in captured:return
  if not retain or Path(ref['path']).suffix in ('.wasm','.a','.zip','.zst')or not Path(ref['path']).suffix:external[ref['path']]=ref;return
  add('evidence/'+str(len(files)).zfill(3)+'-'+Path(ref['path']).name,ref['path'],ref)
 def family(ref,retain=True):
  idx=json.loads(checked(ref));root=Path(ref['path']).parent;names=[r['path']for r in idx['files']]
  assert len(names)==len(set(names))and not any(p.is_symlink()for p in root.rglob('*'))
  assert set(names)|{'index.json'}=={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}
  add('sources/'+root.name+'/index.json',ref['path'],ref);members=[]
  for r in idx['files']:
   rel=Path(r['path']);assert not rel.is_absolute()and'..'not in rel.parts
   q={**r,'path':str(root/rel)};checked(q);members.append(q)
   if retain:add('sources/'+root.name+'/'+r['path'],q['path'],q)
   else:external[q['path']]=q
  families.append(dict(index=ref,memberDescriptors=members,retainedMembers=retain))
 r=json.loads((RUNTIME/'result.json').read_bytes());assert row(RUNTIME/'result.json')['sha256']=='6d959823d9f9b54782ecfb0f093c84ee593557cad40851315fc9cef1995271cb'
 a=json.loads(checked(r['rootAuthority']));p=json.loads(Path(r['sourceIndex']['path']).with_name('plan.json').read_bytes());c=json.loads(checked(r['constructionResult']))
 for q in sorted(RUNTIME.iterdir()):
  if q.is_file():add('runtime/'+q.name,q)
 for q in sorted((RUNTIME/'responses').iterdir()):add('runtime/responses/'+q.name,q)
 for q in sorted(Path(str(RUNTIME)+'-external-root').iterdir()):
  if q.is_file():add('runtime-monitor/'+q.name,q)
 add('runtime/project/.wash/config.json',RUNTIME/'project/.wash/config.json')
 for ref in [r['sourceIndex'],a['constructionCallerIndex'],a['inputSourceIndex'],r['worldFamily']]:family(ref)
 for ref in a['nativeSourceFamilies']:family(ref,False)
 family(row(ROOT.parent/'next-app-build-v1/index.json'))
 for ref in [r['applicationBuildResult'],r['rootAuthority'],r['constructionResult'],r['componentAudit'],r['nativeMetadata'],r['applicationInputs'],c['rootAuthority'],c['plan'],*a['nativeProtectedInputs'],*p['protectedSourceReferences']]:evidence(ref)
 for command in c['commands']:
  for key in ['terminal','stdout','stderr']:evidence(command[key])
 for ref in [*r['engineBuildEvidence'],r['engine'],r['component'],r['wash'],p['node'],p['monitor']]:evidence(ref,False)
 def world_guard():
  base=Path(r['worldFamily']['path']).parent;actual=[]
  for item in r['worldBefore']:
   q=base/item['relativePath'];assert not q.is_symlink();st=q.stat();assert(st.st_dev,st.st_ino,st.st_nlink,st.st_mode&0o777)==(item['dev'],item['ino'],item['nlink'],item['mode'])
   assert q.is_file()if item['kind']=='file'else q.is_dir();actual.append(item)
  nodes=list(base.rglob('*'));assert{'.'}|{q.relative_to(base).as_posix()for q in nodes}=={x['relativePath']for x in r['worldBefore']}
  return hashlib.sha256(json.dumps(actual,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 for name in ['launch-admission.json','first-cli.stdout.log','first-cli.stderr.log']:add('root/'+name,ROOT/name)
 pair=ROOT.parent/'next-app-runtime-root-results-v1'
 for role,path in [('stock',TEMP/'next-browser-hydration-stock-v3'),('native',TEMP/'next-wasmtime-deployment-engine462-fresh-app-v7-first')]:
  add('first-pair/'+role+'/result.json',path/'result.json')
  outer=Path(str(path)+('-monitor'if role=='stock'else'-external-root'))
  for name in ['terminal.json','started.json','observation.json']:add('first-pair/'+role+'/'+name,outer/name)
  obs=json.loads((outer/'observation.json').read_bytes());assert obs.get('hostExperimentPassed',obs.get('passed'))is True
  term=json.loads((outer/'terminal.json').read_bytes());evidence(term['authority'])
  if role=='native':
   rr=json.loads((path/'result.json').read_bytes());add('first-pair/native/client-result.json',rr['client']['result']['path'],rr['client']['result'])
 add('first-pair/native/world-guard.json',pair/'engine462-fresh-app-v7-first-full-world-guard.json')
 worldbefore=world_guard()
 app=json.loads(checked(r['applicationInputs']));before=app_guard(app,RUNTIME/'app',p['applicationRootIdentity'])
 for ref in [*captured.values(),*external.values()]:checked(ref)
 after=app_guard(app,RUNTIME/'app',p['applicationRootIdentity']);assert before==after;assert worldbefore==world_guard()
 with(HERE/'data.tar.gz').open('xb')as output:
  with gzip.GzipFile(fileobj=output,mode='wb',filename='',mtime=0)as zipped:
   with tarfile.open(fileobj=zipped,mode='w')as archive:
    for name,b in sorted(blobs.items()):
     info=tarfile.TarInfo(name);info.size=len(b);info.mode=0o600;info.mtime=0;archive.addfile(info,io.BytesIO(b))
 cap=dict(schemaVersion=1,archive=row(HERE/'data.tar.gz'),files=sorted(files,key=lambda r:r['path']),families=families,
  externalDescriptors=list(external.values()),runtimeResult=row(RUNTIME/'result.json'),applicationCurrentBeforeFinal=before,
  selectedRowsRehashedBeforeFinal=len(set(captured)|set(external)),retainedFiles=len(files),worldCurrentBeforeFinalIdentitySha256=worldbefore,component=r['component'],engine=r['engine'],nativeMetadata=r['nativeMetadata'],
  protectionScope='Finite original descriptor hashes and declared Source-family membership plus current original/copied app hashes/modes/identity bookends; no all-time or recursive SDK ancestry attestation',
  reviewerAuthoredEarlierAlsConstructorToolingAndAppCli=True,reviewerPreviousColdSourcePassMissedRegistrationGate=True,targetRerun=False,
  noBinarySdkAppOrRecursiveBuildAncestryCopied=True)
 (HERE/'capsule.json').write_text(json.dumps(cap,indent=2)+'\n')
 print(json.dumps(dict(files=len(files),expandedBytes=sum(x['original']['bytes']for x in files),archive=cap['archive'],selectedRows=cap['selectedRowsRehashedBeforeFinal'],app=before)))
if __name__=='__main__':main()
