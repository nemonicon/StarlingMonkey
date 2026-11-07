"""One-shot finite DATA retention. No process, oracle, tool or guest invocation."""
from pathlib import Path
import gzip,hashlib,io,json,tarfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
TEMP=Path('/private/tmp/starling-node-compat')
RUNTIME=TEMP/'peer-disconnect-wasmtime-probe-v1-engine462-peer-v1'
CONSTRUCTOR=TEMP/'peer-disconnect-component-v1-peer-disconnect-engine462-peer-v1'
def row(path,data=None):
 path=Path(path);data=path.read_bytes()if data is None else data
 return dict(path=str(path),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
def checked(ref):
 p=Path(ref['path']);assert p.is_absolute()and p.is_file()and not p.is_symlink()
 b=p.read_bytes();assert row(p,b)=={k:ref[k]for k in ('path','sha256','bytes')};return b
def main():
 assert not(HERE/'data.tar.gz').exists()
 blobs={};files=[];captured={};external={};families=[]
 def add(name,path,ref=None):
  assert name not in blobs
  b=checked(ref or row(path));r=row(path,b);blobs[name]=b
  files.append(dict(path=name,original=r));captured[r['path']]=r;return r
 def evidence(ref,retain=True):
  checked(ref)
  if ref['path']in captured:return
  if not retain or Path(ref['path']).suffix in ('.wasm','.a','.obj','.zip','.zst')or not Path(ref['path']).suffix:
   external[ref['path']]=ref;return
  add('evidence/'+str(len(files)).zfill(3)+'-'+Path(ref['path']).name,ref['path'],ref)
 def family(ref,retain=True):
  index=json.loads(checked(ref));base=Path(ref['path']).parent
  names=[x['path']for x in index['files']];assert len(names)==len(set(names))
  assert not any(p.is_symlink()for p in base.rglob('*'))
  assert set(names)|{'index.json'}=={p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()}
  add('sources/'+base.name+'/index.json',ref['path'],ref)
  members=[]
  for item in index['files']:
   rel=Path(item['path']);assert not rel.is_absolute()and'..'not in rel.parts
   r={**item,'path':str(base/rel)};checked(r);members.append(r)
   if retain:add('sources/'+base.name+'/'+item['path'],r['path'],r)
   else:external[r['path']]=r
  families.append(dict(index=ref,memberDescriptors=members,retainedMembers=retain))
 r=json.loads((RUNTIME/'result.json').read_bytes());c=json.loads(checked(r['constructionResult']))
 a=json.loads(checked(r['rootAuthority']));ca=json.loads(checked(c['rootAuthority']))
 plan=json.loads(Path(r['sourceIndex']['path']).with_name('plan.json').read_bytes())
 host=json.loads(checked(plan['referenceHostChecks']));node=next(x for x in host['phases']if x['name']=='node-localhost-reference')
 assert row(RUNTIME/'result.json')['sha256']=='e5e10dac6bb752ecf78f90345478ed229a7a4f5fad586feeefde41f4fd80870a'
 for label,path in [('runtime',RUNTIME),('constructor',CONSTRUCTOR),('runtime-monitor',Path(str(RUNTIME)+'-external-root')),('constructor-monitor',Path(str(CONSTRUCTOR)+'-external-root')),('node-reference',Path(node['stdout']['path']).parent)]:
  for item in sorted(path.rglob('*')):
   if item.is_file()and item.suffix not in ('.wasm','.a','.obj')and item.relative_to(path).as_posix()!='api-return/native-metadata-input.json':
    add(label+'/'+item.relative_to(path).as_posix(),item)
 for ref in [r['sourceIndex'],r['constructionCallerIndex'],r['probeSourceIndex'],ca['worldSourceIndex']]:family(ref)
 for ref in a['nativeSourceFamilies']:family(ref,False)
 for ref in [r['rootAuthority'],c['rootAuthority'],r['nativeMetadata'],json.loads(checked(node['terminal']))['authority'],*a['nativeProtectedInputs'],*ca['newSourceEvidence']]:evidence(ref)
 # Direct native ancestry descriptors are rehashed, not recursively recopied.
 for ref in r['engineBuildEvidence']:evidence(ref,False)
 for ref in [r['engine'],r['component'],plan['node'],plan['wasmtime'],plan['adapter'],plan['monitor']]:evidence(ref,False)
 for ref in [*captured.values(),*external.values()]:checked(ref)
 with(HERE/'data.tar.gz').open('xb')as output:
  with gzip.GzipFile(fileobj=output,mode='wb',filename='',mtime=0)as zipped:
   with tarfile.open(fileobj=zipped,mode='w')as archive:
    for name,b in sorted(blobs.items()):
     info=tarfile.TarInfo(name);info.size=len(b);info.mode=0o600;info.mtime=0;archive.addfile(info,io.BytesIO(b))
 capsule=dict(schemaVersion=1,archive=row(HERE/'data.tar.gz'),files=sorted(files,key=lambda r:r['path']),families=families,
  externalDescriptors=list(external.values()),runtimeResult=row(RUNTIME/'result.json'),constructionResult=r['constructionResult'],
  component=r['component'],engine=r['engine'],nativeMetadata=r['nativeMetadata'],
  selectedRowsRehashedBeforeFinal=len(set(captured)|set(external)),nativeArchiveSdkAppOrComponentCopied=False,
  independentReviewScope='Finite current descriptor before/final hashes and declared Source-family membership; not recursive SDK/build ancestry, filesystem identity or all-time protection',
  reviewerAuthoredOriginalAlsAndConstructorTooling=True,targetRerun=False)
 (HERE/'capsule.json').write_text(json.dumps(capsule,indent=2)+'\n')
 print(json.dumps(dict(files=len(files),expandedBytes=sum(x['original']['bytes']for x in files),archive=capsule['archive'],selectedCurrentRows=capsule['selectedRowsRehashedBeforeFinal'])))
if __name__=='__main__':main()
