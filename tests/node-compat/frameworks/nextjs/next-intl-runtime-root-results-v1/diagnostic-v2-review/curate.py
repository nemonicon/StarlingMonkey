"""One-time diagnostic DATA curation; no component/runtime/code invocation."""
from pathlib import Path
import gzip,hashlib,importlib.util,io,json,tarfile
HERE=Path(__file__).resolve().parent
NEXT=HERE.parents[1]
AUTH=NEXT/'intl-component-root-results-v1'
RUNTIME=Path('/private/tmp/starling-node-compat/next-wasmtime-deployment-enginee7baa5a9-source-view-v2')
def row(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def save(p,v):
 with p.open('x')as f:json.dump(v,f,indent=2);f.write('\n')
def main():
 data={};origins={};before={};external=[]
 def add(n,p):
  assert n not in data;r=row(p);b=Path(p).read_bytes();b.decode();assert hashlib.sha256(b).hexdigest()==r['sha256'];data[n]=b;origins[n]=r;before[r['path']]=r
 def shared(r):
  assert row(r['path'])==r
  if r['path']not in before:add('shared/'+hashlib.sha256(r['path'].encode()).hexdigest()[:12]+'-'+Path(r['path']).name,r['path'])
 def family(r):
  shared(r);parent=Path(r['path']).parent
  for item in json.loads(Path(r['path']).read_text())['files']:
   shared(dict(path=str(parent/item['path']),bytes=item['bytes'],sha256=item['sha256']))
 add('authority/construction.json',AUTH/'diagnostic-v2-construction-authority.json');add('authority/runtime.json',AUTH/'diagnostic-v2-runtime-authority.json')
 ca=json.loads(data['authority/construction.json']);ra=json.loads(data['authority/runtime.json']);constructor=Path(ca['outputRoot']);cr=json.loads((constructor/'result.json').read_text());rr=json.loads((RUNTIME/'result.json').read_text())
 assert cr['passed']is True and rr['passed']is False
 for kind,root in [('constructor',constructor),('runtime',RUNTIME)]:
  for p in sorted(root.rglob('*')):
   if not p.is_file():continue
   relative=p.relative_to(root)
   if kind=='runtime'and relative.parts[0]in ['app','cache','xdg']:continue
   if p.suffix=='.wasm':
    r=row(p);external.append(r);before[r['path']]=r;continue
   add(kind+'/'+relative.as_posix(),p)
  outer=Path(str(root)+'-external-root')
  for p in sorted(outer.rglob('*')):
   if p.is_file():add(kind+'-outer/'+p.relative_to(outer).as_posix(),p)
 family(ca['callerIndex']);family(ra['sourceIndex']);family(ra['inputSourceIndex']);shared(cr['plan']);shared(ra['plan']);shared(ra['inputEntry'])
 for r in [ca['engine'],cr['artifacts']['adapter']]:assert row(r['path'])==r;before[r['path']]=r;external.append(r)
 assert all(row(p)==r for p,r in before.items())
 bundle=HERE/'data.tar.gz'
 with bundle.open('xb')as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0)as gz,tarfile.open(fileobj=gz,mode='w|',format=tarfile.USTAR_FORMAT)as tar:
  for n,b in sorted(data.items()):m=tarfile.TarInfo(n);m.size=len(b);m.mode=0o600;m.mtime=0;tar.addfile(m,io.BytesIO(b))
 entries=[dict(path=n,originalPath=origins[n]['path'],bytes=len(b),sha256=hashlib.sha256(b).hexdigest())for n,b in sorted(data.items())]
 save(HERE/'payload-index.json',dict(schemaVersion=1,entries=entries,bundle=dict(path=bundle.name,**{k:row(bundle)[k]for k in ['bytes','sha256']}),externalBinaryReferences=external,allSelectedReferencesRehashedBeforeFinal=len(before),originalInputsUnchangedDuringCuration=True,applicationOrCacheBodiesCopied=False))
 spec=importlib.util.spec_from_file_location('diagnostic_v2_data_checker',HERE/'check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);review=m.verify(HERE);save(HERE/'review.json',review)
 print(json.dumps(dict(review=row(HERE/'review.json'),bundle=row(bundle),textPayloads=len(data),rawTextBytes=sum(map(len,data.values())),referenceBookends=len(before),underlyingRuntimePassed=False)),flush=True)
if __name__=='__main__':main()
