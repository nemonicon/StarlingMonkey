"""Collect completed constructor DATA; executes no historical source or tools."""
from pathlib import Path
import gzip,hashlib,importlib.util,io,json,tarfile

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
KINDS=['regexp','stacktrace','dependencies','real-next']


def row(p):
 p=Path(p);assert not p.is_symlink()and p.is_file();h=hashlib.sha256();n=0
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024**2),b''):h.update(b);n+=len(b)
 return dict(path=str(p),bytes=n,sha256=h.hexdigest())
def save(p,x):
 with p.open('x')as f:json.dump(x,f,indent=2);f.write('\n')


def main():
 data={};origins={};before={};external=[]
 def add(n,p):
  assert n not in data;r=row(p);b=Path(p).read_bytes();b.decode();assert hashlib.sha256(b).hexdigest()==r['sha256'];data[n]=b;origins[n]=r;before[r['path']]=r
 def shared(r):
  assert row(r['path'])==r
  if r['path']in before:return
  p=Path(r['path']);assert p.suffix!='.wasm'
  add('shared/'+r['sha256'][:16]+'-'+p.name,p)
 add('source-data/launch-construction.py',PARENT/'launch-construction.py')
 for kind in KINDS:
  path=PARENT/(kind+'-construction-authority.json');add(kind+'/authority.json',path);a=json.loads(path.read_text());out=Path(a['outputRoot']);r=json.loads((out/'result.json').read_text())
  assert r['passed']is True and json.loads((Path(str(out)+'-external-root')/'terminal.json').read_text())['rawExitCode']==0
  component=r['artifacts']['component'];assert row(component['path'])==component
  with Path(component['path']).open('rb')as f:assert f.read(8)==b'\0asm\x0d\0\x01\0'
  before[component['path']]=component;external.append(component)
  for p in sorted(out.rglob('*')):
   if p.is_file()and p!=Path(component['path']):
    assert p.suffix!='.wasm',p;add(kind+'/output/'+str(p.relative_to(out)),p)
  outer=Path(str(out)+'-external-root')
  for p in sorted(outer.rglob('*')):
   if p.is_file():add(kind+'/outer/'+str(p.relative_to(outer)),p)
  for key in ['callerIndex','plan']:shared(r[key])
  caller=Path(r['callerIndex']['path']).parent;idx=json.loads(Path(r['callerIndex']['path']).read_text())
  for item in idx['files']:
   shared(dict(path=str(caller/item['path']),bytes=item['bytes'],sha256=item['sha256']))
  for key in ['inputEntry','inputSourceIndex','nativeMetadata']:shared(r['artifacts'][key])
  for ref in [a['engine'],r['artifacts']['adapter']]:
   assert row(ref['path'])==ref;before[ref['path']]=ref
   if ref not in external:external.append(ref)
  # The actual typed return remains entire, not a reconstructed approximation.
  assert row(r['artifacts']['returnedOwnShape']['path'])==r['artifacts']['returnedOwnShape']
 assert all(row(p)==r for p,r in before.items())
 bundle=HERE/'data.tar.gz'
 with bundle.open('xb')as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0)as gz,tarfile.open(fileobj=gz,mode='w|',format=tarfile.USTAR_FORMAT)as tar:
  for n,b in sorted(data.items()):
   m=tarfile.TarInfo(n);m.size=len(b);m.mode=0o600;m.mtime=0;tar.addfile(m,io.BytesIO(b))
 entries=[dict(path=n,originalPath=origins[n]['path'],bytes=len(b),sha256=hashlib.sha256(b).hexdigest())for n,b in sorted(data.items())]
 save(HERE/'payload-index.json',dict(schemaVersion=1,entries=entries,bundle=dict(path=bundle.name,**{k:row(bundle)[k]for k in ['bytes','sha256']}),externalBinaryReferences=external,
                                   sourceAndArtifactReferencesRehashedBeforeFinal=len(before),allSelectedReferencesUnchanged=True,largeBinaryPayloadsCopied=False))
 spec=importlib.util.spec_from_file_location('four_constructor_data_checker',HERE/'check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);review=m.verify(HERE)
 review.update(authorRelationship='Reviewer authored predecessor fixtures/callers and some artifact preparation; not operator of these four constructions.',
               allOriginalProducerInputsPreauthenticatedClaimed=False,scope='Actual INIT-only construction, validation and complete emitted-WIT/typed-return DATA; ordinary runtime remains separate.')
 save(HERE/'review.json',review)
 print(json.dumps(dict(review=row(HERE/'review.json'),bundle=row(bundle),payloads=len(data),rawTextBytes=sum(map(len,data.values())),externalBinaryReferences=len(external))),flush=True)


if __name__=='__main__':main()
