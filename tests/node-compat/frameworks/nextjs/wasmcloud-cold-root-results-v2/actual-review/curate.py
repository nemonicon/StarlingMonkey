"""One-shot finite DATA retention. No process, oracle, tool or guest invocation."""
from pathlib import Path
import gzip,hashlib,io,json,tarfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
TEMP=Path('/private/tmp/starling-node-compat')
RUNTIME=TEMP/'next-wasmcloud-cold-v2-engine462-cold-v2'
def row(path,data=None):
 path=Path(path);data=path.read_bytes()if data is None else data
 return dict(path=str(path),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
def checked(ref):
 p=Path(ref['path']);assert p.is_absolute()and p.is_file()and not p.is_symlink()
 b=p.read_bytes();assert row(p,b)=={k:ref[k]for k in ('path','sha256','bytes')};return b
def app_guard(inventory,copy_root):
 identities=[]
 for kind,root in [('source',Path(inventory['root'])),('copy',copy_root)]:
  nodes=list(root.rglob('*'));assert not any(p.is_symlink()for p in nodes)
  assert{p.relative_to(root).as_posix()for p in nodes if p.is_file()}=={r['path']for r in inventory['files']}
  assert{'.'}|{p.relative_to(root).as_posix()for p in nodes if p.is_dir()}=={r['path']for r in inventory['directories']}
  for r in inventory['files']:
   p=root/r['path'];checked(dict(path=str(p),sha256=r['sha256'],bytes=r['bytes']));s=p.stat()
   if kind=='source':assert(s.st_dev,s.st_ino,s.st_nlink,s.st_mode&0o777)==(r['dev'],r['ino'],r['nlink'],r['mode'])
   else:assert s.st_nlink==1 and s.st_mode&0o777==0o444 and(s.st_dev,s.st_ino)!=(r['dev'],r['ino'])
   identities.append([kind,r['path'],s.st_dev,s.st_ino,s.st_nlink,s.st_mode&0o777])
  for r in inventory['directories']:
   p=root/r['path'];s=p.stat()
   if kind=='source':assert(s.st_dev,s.st_ino,s.st_mode&0o777)==(r['dev'],r['ino'],r['mode'])
   else:assert s.st_mode&0o777==0o555
   identities.append([kind,r['path'],s.st_dev,s.st_ino,s.st_nlink,s.st_mode&0o777])
 return dict(filesPerTree=len(inventory['files']),directoriesPerTree=len(inventory['directories']),bytesPerTree=inventory['bytes'],
  sourceMatchesPublishedIdentity=True,copyByteIdenticalDistinctInodesAndReadOnlyModes=True,
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
 r=json.loads((RUNTIME/'result.json').read_bytes());assert row(RUNTIME/'result.json')['sha256']=='0d73be85f0d1efed109799a0d6e02070dd8f1b0d2f632a474069de30826a07e9'
 a=json.loads(checked(r['rootAuthority']));p=json.loads(Path(r['sourceIndex']['path']).with_name('plan.json').read_bytes());c=json.loads(checked(r['constructionResult']))
 for q in sorted(RUNTIME.iterdir()):
  if q.is_file():add('runtime/'+q.name,q)
 for q in sorted((RUNTIME/'responses').iterdir()):add('runtime/responses/'+q.name,q)
 for q in sorted(Path(str(RUNTIME)+'-external-root').iterdir()):
  if q.is_file():add('runtime-monitor/'+q.name,q)
 add('runtime/project/.wash/config.json',RUNTIME/'project/.wash/config.json')
 for ref in [r['sourceIndex'],a['constructionCallerIndex'],a['inputSourceIndex']]:family(ref)
 for ref in a['nativeSourceFamilies']:family(ref,False)
 for ref in [r['rootAuthority'],r['constructionResult'],r['componentAudit'],r['nativeMetadata'],r['applicationInputs'],c['rootAuthority'],c['plan'],*a['nativeProtectedInputs'],*p['protectedSourceReferences']]:evidence(ref)
 for command in c['commands']:
  for key in ['terminal','stdout','stderr']:evidence(command[key])
 for ref in [*r['engineBuildEvidence'],r['engine'],r['component'],r['wash'],p['node'],p['monitor']]:evidence(ref,False)
 app=json.loads(checked(r['applicationInputs']));before=app_guard(app,RUNTIME/'app')
 for ref in [*captured.values(),*external.values()]:checked(ref)
 after=app_guard(app,RUNTIME/'app');assert before==after
 with(HERE/'data.tar.gz').open('xb')as output:
  with gzip.GzipFile(fileobj=output,mode='wb',filename='',mtime=0)as zipped:
   with tarfile.open(fileobj=zipped,mode='w')as archive:
    for name,b in sorted(blobs.items()):
     info=tarfile.TarInfo(name);info.size=len(b);info.mode=0o600;info.mtime=0;archive.addfile(info,io.BytesIO(b))
 cap=dict(schemaVersion=1,archive=row(HERE/'data.tar.gz'),files=sorted(files,key=lambda r:r['path']),families=families,
  externalDescriptors=list(external.values()),runtimeResult=row(RUNTIME/'result.json'),applicationCurrentBeforeFinal=before,
  selectedRowsRehashedBeforeFinal=len(set(captured)|set(external)),component=r['component'],engine=r['engine'],nativeMetadata=r['nativeMetadata'],
  protectionScope='Finite original descriptor hashes and declared Source-family membership plus current original/copied app hashes/modes/identity bookends; no all-time or recursive SDK ancestry attestation',
  reviewerAuthoredEarlierAlsAndConstructorTooling=True,reviewerPreviousColdSourcePassMissedRegistrationGate=True,targetRerun=False,
  noBinarySdkAppOrRecursiveBuildAncestryCopied=True)
 (HERE/'capsule.json').write_text(json.dumps(cap,indent=2)+'\n')
 print(json.dumps(dict(files=len(files),expandedBytes=sum(x['original']['bytes']for x in files),archive=cap['archive'],selectedRows=cap['selectedRowsRehashedBeforeFinal'],app=before)))
if __name__=='__main__':main()
