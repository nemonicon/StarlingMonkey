"""Retain only the terminal interop INIT/runtime raw records and selected witnesses."""
from pathlib import Path
import gzip,hashlib,io,json,os,stat,tarfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
BASE=ROOT.parent
CTOR=Path('/private/tmp/starling-node-compat/next-module-fileurl-interop-probe-component-v2-interop-interop-2251-first')
RUN=Path('/private/tmp/starling-node-compat/next-module-fileurl-interop-probe-v1-interop-2251-probe-first')
ROOT_NAMES=['actual-construction-review.json','actual-owner-world-review.json','actual-package-review.json',
 'actual-runtime-outcome-review.json','actual-runtime-review.json','interop-probe-v2-construction-authority.json',
 'interop-2251-first-runtime-authority.json','interop-2251-probe-first-full-native-world-guard.json',
 'launch-construction.py','prepare-construction.py','prepare-runtime.py','run-probe.py',
 'construction-preparation.json','construction.stdout.log','construction.stderr.log','runtime-preparation.json',
 'runtime-source-admission-review.json','runtime.stdout.log','runtime.stderr.log']
WITNESSES=['next-module-fileurl-interop-probe-runtime-candidate-v1/index.json',
 'next-module-fileurl-interop-probe-runtime-candidate-v1/plan.json',
 'next-module-fileurl-interop-probe-runtime-candidate-v1/comparison.mjs',
 'next-module-fileurl-interop-probe-construction-v2/index.json','next-module-fileurl-interop-probe-construction-v2/plan.json',
 'next-module-fileurl-probe-candidate-v1/index.json','next-module-fileurl-probe-candidate-v1/plan.json',
 'next-module-fileurl-probe-candidate-v1/cases.mjs','regexp-unicode-probe-candidate-v1/index.json']
def physical(p):
 s=p.lstat();return[s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns]
def main():
 rows=[];data={};originals={};trees=[];roles={}
 def add(p,role):
  p=Path(p);assert p.resolve(strict=True)==p and not any(q.is_symlink()for q in [p,*p.parents]);before=physical(p)
  assert stat.S_ISREG(before[2])and before[3]==1;v=p.read_bytes();assert physical(p)==before;v.decode('utf-8');assert b'\0'not in v
  ref=dict(path=str(p),sha256=hashlib.sha256(v).hexdigest(),bytes=len(v))
  if str(p)in originals:assert originals[str(p)]['original']==ref;return ref
  name='data/'+str(len(rows)).zfill(5);record=dict(archivePath=name,original=ref,mode=stat.S_IMODE(before[2]),physicalBefore=before,role=role);rows.append(record);data[name]=v;originals[str(p)]=record;return ref
 def tree(root,role,exclude=None):
  files=[];dirs=[dict(path='.',physicalBefore=physical(root))]
  for p in sorted(root.rglob('*')):
   assert not p.is_symlink()and(p.is_file()or p.is_dir())
   rel=p.relative_to(root).as_posix()
   if p.is_dir():dirs.append(dict(path=rel,physicalBefore=physical(p)))
   elif exclude is not None and rel==exclude:continue
   else:files.append(rel);add(p,role)
  trees.append(dict(root=str(root),files=files,directories=dirs,exactOmittedFile=exclude))
 tree(CTOR,'complete-init-text-originals','api-return/returned-component.wasm')
 tree(Path(str(CTOR)+'-external-root'),'complete-init-root-owned-originals')
 tree(RUN,'complete-runtime-originals')
 tree(Path(str(RUN)+'-external-root'),'complete-runtime-root-owned-originals')
 for name in ROOT_NAMES:roles[name]=add(ROOT/name,'closed-root-review-authority-or-source')
 for name in WITNESSES:roles[name]=add(BASE/name,'finite-source-id-and-contract-witness')
 buf=io.BytesIO()
 with gzip.GzipFile(fileobj=buf,mode='wb',compresslevel=6,mtime=0)as zipped:
  with tarfile.open(fileobj=zipped,mode='w',format=tarfile.USTAR_FORMAT)as archive:
   for record in rows:
    v=data[record['archivePath']];m=tarfile.TarInfo(record['archivePath']);m.size=len(v);m.mode=record['mode'];m.mtime=0;archive.addfile(m,io.BytesIO(v))
 for record in rows:
  p=Path(record['original']['path']);assert physical(p)==record['physicalBefore']and p.read_bytes()==data[record['archivePath']]
 for tree in trees:
  for q in tree['directories']:assert physical(Path(tree['root'])/q['path'])==q['physicalBefore']
 v=buf.getvalue();index=dict(schemaVersion=1,state='UNSEALED_INTEROP_INIT_AND_RUNTIME_FINITE_RAW_DATA_V1',bundle=dict(path='data.tar.gz',sha256=hashlib.sha256(v).hexdigest(),bytes=len(v)),files=rows,memberCount=len(rows),logicalBytes=sum(len(v)for v in data.values()),trees=trees,roles=roles,constructorRoot=str(CTOR),runtimeRoot=str(RUN),rootRecords=str(ROOT),selectedOriginalsBeforeFinalHashAndPhysicalBookendsUnchanged=True,sourceWitnessesAreNotRecursiveSourceClosure=True,binaryOrPackageSdkNativeTreePayloadIncluded=False,fullBuildOrSourceTreeRescanned=False,actorOrNetworkInvoked=False)
 for name,v in [('data.tar.gz',v),('payload-index.json',(json.dumps(index,indent=2)+'\n').encode())]:
  fd=os.open(HERE/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
  with os.fdopen(fd,'wb')as f:f.write(v);f.flush();os.fsync(f.fileno())
 print(json.dumps(dict(members=len(rows),logicalBytes=index['logicalBytes'],archive=index['bundle'],actorInvoked=False)))
if __name__=='__main__':main()
