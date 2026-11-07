"""One-shot retained paired actual CDP-positive DATA collection. No imports of executable project code."""
from pathlib import Path
import gzip, hashlib, io, json, stat, tarfile
HERE=Path(__file__).resolve().parent
NEXT=HERE.parents[1]
TEMP=Path('/private/tmp/starling-node-compat')
RUNTIME=TEMP/'next-wasmtime-deployment-engine462-full-next-cdp-v6-first'
STOCK=TEMP/'next-browser-hydration-stock-v2'
CONSTRUCTOR=TEMP/'next-entry-fixes-component-v5-real-next-engine462-io-abort-v5'
AUTHORITIES=NEXT/'next-entry-fixes-root-results-v5'
def digest(b):return dict(sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def descriptor(p,b=None):
 p=Path(p);return dict(path=str(p),**digest(p.read_bytes() if b is None else b))
def checked(r):
 p=Path(r['path']);assert p.is_absolute() and p.is_file() and not p.is_symlink()
 b=p.read_bytes();assert descriptor(p,b)=={k:r[k] for k in ['path','sha256','bytes']};return b
def main():
 assert not (HERE/'data.tar.gz').exists()
 data={};entries=[];originals={};external={};families={}
 def add(name,p,row=None):
  p=Path(p);r=row or descriptor(p);b=checked(r)
  if str(p) in originals:
   old=originals[str(p)];assert old['original']==r and data[old['path']]==b;return old['path']
  assert name not in data and not name.startswith('/') and '..' not in Path(name).parts
  item=dict(path=name,original=r,kind='png' if p.suffix=='.png' else 'utf8')
  if item['kind']=='utf8':b.decode('utf8')
  data[name]=b;entries.append(item);originals[str(p)]=item;return name
 def family(r):
  if r['path'] in families:assert families[r['path']]==r;return
  index=json.loads(checked(r));base=Path(r['path']).parent
  names=[x['path'] for x in index['files']];assert len(names)==len(set(names))
  assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}==set(names)|{'index.json'}
  add('sources/'+base.name+'/index.json',r['path'],r)
  for x in index['files']:add('sources/'+base.name+'/'+x['path'],base/x['path'],{**x,'path':str(base/x['path'])})
  families[r['path']]=r
 for kind,root in [('constructor',CONSTRUCTOR),('runtime',RUNTIME)]:
  for p in sorted(root.rglob('*')):
   assert not p.is_symlink()
   if not p.is_file():continue
   relative=p.relative_to(root)
   if relative.parts[0] in ['app','cache'] or p.suffix in ['.wasm','.a','.o'] or relative.as_posix()=='api-return/native-metadata-input.json':continue
   add(kind+'/'+relative.as_posix(),p)
  monitor=Path(str(root)+'-external-root')
  for p in sorted(monitor.rglob('*')):
   assert not p.is_symlink()
   if p.is_file():add(kind+'-outer/'+p.relative_to(monitor).as_posix(),p)
  t=json.loads((monitor/'terminal.json').read_text())
  add('authority/'+kind+'.json',t['authority']['path'],t['authority'])
  started=json.loads((monitor/'started.json').read_text())
  for arg in started['argv']:
   p=Path(arg)
   if p.is_absolute() and p.is_file() and p.suffix in ['.py','.mjs']:add('root-callers/'+p.parent.name+'/'+p.name,p)
 runtime=json.loads((RUNTIME/'result.json').read_text());construction=json.loads(checked(runtime['constructionResult']))
 for r in [runtime['inputSourceIndex'],runtime['sourceIndex'],construction['callerIndex']]:family(r)
 ca=json.loads(checked(construction['rootAuthority']));ra=json.loads(checked(runtime['rootAuthority']))
 for n,r in enumerate(ca['newSourceEvidence']):add('inputs/source-evidence/'+str(n)+'-'+Path(r['path']).name,r['path'],r)
 sourceplan=json.loads((Path(runtime['inputSourceIndex']['path']).parent/'plan.json').read_text())
 family(ca['worldSourceIndex'])
 for n,facade in enumerate(sourceplan['facadeReferences']):
  add('inputs/facades/'+str(n)+'-'+Path(facade['path']).name,facade['path'],facade)
 for r in ra['nativeProtectedInputs']:add('inputs/native-protection/'+str(len(entries))+'-'+Path(r['path']).name,r['path'],r)
 add('inputs/native-metadata.json',construction['artifacts']['nativeMetadata']['path'],construction['artifacts']['nativeMetadata'])
 add('inputs/full-world-guard.json',AUTHORITIES/'engine462-full-next-cdp-v6-first-full-world-guard.json')
 for k in ['component','engine','nativeMetadata','adapter']:
  r=construction['artifacts'][k];checked(r);external[r['path']]=r
 for r in construction['artifacts']['engineBuildEvidence']:checked(r);external[r['path']]=r
 plan=json.loads(checked(dict(path=str(NEXT/'wasmtime-deployment-candidate-v6/plan.json'),**digest((NEXT/'wasmtime-deployment-candidate-v6/plan.json').read_bytes()))))
 for name in ['wasmtime','node']:
  r=plan[name];checked(r);external[r['path']]=r
 application=json.loads(checked(plan['applicationInputs']));add('inputs/application-inputs.json',plan['applicationInputs']['path'],plan['applicationInputs'])
 add('inputs/fixture-contract.json',NEXT/'fixture-contract.json')
 add('inputs/browser-check.mjs',NEXT/'browser-hydration-candidate-v2/browser-check.mjs')
 stockresult=json.loads((STOCK/'result.json').read_text())
 for q in sorted(STOCK.rglob('*')):
  if not q.is_file():continue
  rel=q.relative_to(STOCK)
  if rel.parts[0]in ['application','app','cache']:continue
  add('stock/'+rel.as_posix(),q)
 for q in sorted(Path(str(STOCK)+'-monitor').rglob('*')):
  if q.is_file():add('stock-outer/'+q.relative_to(Path(str(STOCK)+'-monitor')).as_posix(),q)
 st=json.loads(Path(str(STOCK)+'-monitor/terminal.json').read_text());add('authority/stock.json',st['authority']['path'],st['authority'])
 sa=json.loads(checked(st['authority']));family(sa['sourceIndex']);add('inputs/stock-plans.json',sa['plans']['path'],sa['plans'])
 observer=next(x for x in plan['sourceFamilies']if Path(x['path']).parent.name=='browser-hydration-candidate-v2');family(observer)
 for k in ['bridge','harness','moduleSource','hostModuleProvider']:add('inputs/stock-'+k+'.mjs',stockresult[k]['path'],stockresult[k])
 external[stockresult['sourceServer']['path']]=stockresult['sourceServer'];checked(stockresult['sourceServer'])
 stockimmutable=0
 for item in application['files']:
  if item['path'].startswith('.next/cache/'):continue
  original=Path(application['root'])/item['path'];copy=STOCK/'application'/item['path'];checked(dict(item,path=str(copy)));a,b=original.stat(),copy.stat()
  assert b.st_nlink==1 and b.st_mode&0o777==item['mode']and(a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino);stockimmutable+=1
 for directory in application['directories']:
  if directory['path']=='.next/cache'or directory['path'].startswith('.next/cache/'):continue
  assert((STOCK/'application'/directory['path']).stat().st_mode&0o777)==directory['mode']
 expected={r['path']:r for r in application['files']};app=RUNTIME/'app'
 assert {p.relative_to(app).as_posix() for p in app.rglob('*') if p.is_file()}==set(expected)
 for relative,r in expected.items():
  source=Path(application['root'])/relative;copy=app/relative
  checked({**r,'path':str(source)});checked({**r,'path':str(copy)})
  a,b=source.stat(),copy.stat();assert b.st_nlink==1 and stat.S_IMODE(b.st_mode)==0o444 and (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)
 assert all(stat.S_IMODE(p.stat().st_mode)==0o555 for p in app.rglob('*') if p.is_dir()) and stat.S_IMODE(app.stat().st_mode)==0o555
 for relative,r in expected.items():
  checked({**r,'path':str(Path(application['root'])/relative)});checked({**r,'path':str(app/relative)})
 for item in originals.values():checked(item['original'])
 for r in external.values():checked(r)
 with (HERE/'data.tar.gz').open('xb') as file:
  with gzip.GzipFile(fileobj=file,mode='wb',filename='',mtime=0) as compressed:
   with tarfile.open(fileobj=compressed,mode='w') as archive:
    for name,b in sorted(data.items()):
     info=tarfile.TarInfo(name);info.size=len(b);info.mode=0o600;info.mtime=0;archive.addfile(info,io.BytesIO(b))
 capsule=dict(schemaVersion=1,bundle=descriptor(HERE/'data.tar.gz'),entries=sorted(entries,key=lambda r:r['path']),externalReferences=list(external.values()),sourceFamilies=list(families.values()),currentOriginalsRehashedBeforeFinal=len(originals),
  currentAppReadback=dict(files=len(expected),bytes=sum(r['bytes'] for r in expected.values()),originalAndCopyHashMatch=True,currentBeforeAndFinalAppHashesMatch=True,copyFilesMode='0444',copyDirectoriesMode='0555',distinctInodesAndSingleLinks=True,preopenReadOnlyRightsProved=False),
  originalRuntimePassed=runtime['passed'],stockRuntimePassed=stockresult['passed'],stockCurrentImmutableCopyFiles=stockimmutable,stockOwnedCacheExcludedFromImmutableCopyClaim=True,bigBinaryOrApplicationPayloadsCopied=False,actualBrowserPngIncluded=True,newTargetAction=False)
 (HERE/'capsule.json').write_text(json.dumps(capsule,indent=2)+'\n')
 print(json.dumps(dict(retainedFiles=len(data),retainedBytes=sum(len(b) for b in data.values()),currentAppFiles=len(expected),bundle=capsule['bundle'])))
if __name__=='__main__':main()
