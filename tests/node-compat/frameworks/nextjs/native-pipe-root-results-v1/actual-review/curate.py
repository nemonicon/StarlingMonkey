"""One-shot actual DATA retention; no process or guest/tool invocation."""
from pathlib import Path
import gzip,hashlib,io,json,tarfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
TEMP=Path('/private/tmp/starling-node-compat')
RUNTIME=TEMP/'native-pipe-wasmtime-probe-engine462-pipe-v1'
CONSTRUCTOR=TEMP/'native-pipe-regression-component-v1-pipe-regression-engine462-pipe-v1'

def row(path,data=None):
 path=Path(path);data=path.read_bytes() if data is None else data
 return dict(path=str(path),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
def checked(ref):
 path=Path(ref['path']);assert path.is_absolute() and path.is_file() and not path.is_symlink()
 data=path.read_bytes();assert row(path,data)=={k:ref[k] for k in ('path','sha256','bytes')};return data
def main():
 assert not(HERE/'data.tar.gz').exists()
 blobs={};files=[];captures={};outside={};families=[]
 def add(name,path,ref=None):
  assert name not in blobs;data=checked(ref or row(path));ref=row(path,data)
  blobs[name]=data;files.append(dict(path=name,original=ref));captures[ref['path']]=ref;return ref
 def evidence(ref):
  checked(ref)
  if ref['path'] in captures:return
  suffix=Path(ref['path']).suffix
  if suffix in ('.wasm','.a','.obj','.gz','.tar','.zip','.zst') or not suffix:
   outside[ref['path']]=ref;return
  add('evidence/'+str(len(files)).zfill(3)+'-'+Path(ref['path']).name,ref['path'],ref)
 def family(ref,retain=True):
  index=json.loads(checked(ref));base=Path(ref['path']).parent
  names=[item['path'] for item in index['files']];assert len(names)==len(set(names))
  assert not any(path.is_symlink() for path in base.rglob('*'))
  assert set(names)|{'index.json'}=={path.relative_to(base).as_posix() for path in base.rglob('*') if path.is_file()}
  if retain:add('sources/'+base.name+'/index.json',ref['path'],ref)
  else:evidence(ref)
  members=[]
  for item in index['files']:
   path=base/item['path'];assert not Path(item['path']).is_absolute() and '..' not in Path(item['path']).parts
   actual={**item,'path':str(path)};checked(actual);members.append(actual)
   if retain:add('sources/'+base.name+'/'+item['path'],path,actual)
   else:outside[actual['path']]=actual
  families.append(dict(index=ref,memberDescriptors=members,retainedMembers=retain))
 runtime=json.loads((RUNTIME/'result.json').read_bytes());construction=json.loads(checked(runtime['constructionResult']))
 authority=json.loads(checked(runtime['rootAuthority']));ca=json.loads(checked(construction['rootAuthority']))
 plan=json.loads(Path(runtime['sourceIndex']['path']).with_name('plan.json').read_bytes())
 for label,path in [('runtime',RUNTIME),('constructor',CONSTRUCTOR),('runtime-monitor',Path(str(RUNTIME)+'-external-root')),('constructor-monitor',Path(str(CONSTRUCTOR)+'-external-root')),('node-oracle',Path(runtime['nodeOracleStdout']['path']).parent)]:
  for item in sorted(path.rglob('*')):
   if item.is_file() and item.suffix not in ('.wasm','.a','.obj') and item.relative_to(path).as_posix()!='api-return/native-metadata-input.json':
    add(label+'/'+item.relative_to(path).as_posix(),item)
 refs=[runtime['sourceIndex'],runtime['constructionCallerIndex'],runtime['probeSourceIndex'],ca['worldSourceIndex']]
 for ref in refs:family(ref)
 for ref in authority['nativeSourceFamilies']:family(ref,False)
 for ref in [json.loads(checked(runtime['nodeOracleTerminal']))['authority'],runtime['rootAuthority'],construction['rootAuthority'],runtime['nativeMetadata'],*runtime['engineBuildEvidence'],*authority['nativeProtectedInputs'],*ca['newSourceEvidence']]:evidence(ref)
 for ref in [runtime['engine'],runtime['component'],plan['node'],plan['wasmtime'],plan['adapter'],plan['monitor']]:evidence(ref)
 for name in ['launch-pipe-v1-construction.py','launch-oracle.executed-v1.py','check-node-oracle.py']:
  if str(ROOT/name) not in captures:add('root-source/'+name,ROOT/name)
 # Rehash every retained/current selected row after collection. No SDK recursion.
 for ref in [*captures.values(),*outside.values()]:checked(ref)
 with(HERE/'data.tar.gz').open('xb')as output:
  with gzip.GzipFile(fileobj=output,mode='wb',filename='',mtime=0)as compressed:
   with tarfile.open(fileobj=compressed,mode='w')as archive:
    for name,data in sorted(blobs.items()):
     info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o600;info.mtime=0;archive.addfile(info,io.BytesIO(data))
 capsule=dict(schemaVersion=1,archive=row(HERE/'data.tar.gz'),files=sorted(files,key=lambda r:r['path']),families=families,
  externalDescriptors=list(outside.values()),runtimeResult=row(RUNTIME/'result.json'),constructionResult=runtime['constructionResult'],
  component=runtime['component'],engine=runtime['engine'],nativeMetadata=runtime['nativeMetadata'],
  selectedRowsRehashedBeforeFinal=len(set(captures)|set(outside)),nativeArchiveSdkAppOrComponentCopied=False,
  independentReviewScope='Current selected descriptors and exact declared family membership, not recursive SDK/native-source protection or all-time attestation',
  reviewerAuthoredPipeFacade=True,targetRerun=False)
 (HERE/'capsule.json').write_text(json.dumps(capsule,indent=2)+'\n')
 print(json.dumps(dict(files=len(files),textBytes=sum(r['original']['bytes'] for r in files),archive=capsule['archive'],selectedCurrentRows=capsule['selectedRowsRehashedBeforeFinal'])))
if __name__=='__main__':main()
