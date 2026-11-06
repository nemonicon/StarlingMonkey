"""Retain completed native hydration V5 DATA; no subprocess or executable import."""
from pathlib import Path
import gzip, hashlib, io, json, stat, tarfile
HERE=Path(__file__).resolve().parent
NEXT=HERE.parents[1]
TEMP=Path('/private/tmp/starling-node-compat')
RUNS=[('first',TEMP/'next-wasmtime-deployment-engine462-hydration-v5-first'),('repeat',TEMP/'next-wasmtime-deployment-engine462-hydration-v5-repeat')]
def digest(b):return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def desc(p,b=None):
 p=Path(p);return dict(path=str(p),**digest(p.read_bytes() if b is None else b))
def checked(r):
 p=Path(r['path']);assert p.is_file() and p.is_absolute() and not p.is_symlink();b=p.read_bytes()
 assert desc(p,b)=={k:r[k] for k in ['path','bytes','sha256']};return b
def main():
 assert not (HERE/'data.tar.gz').exists()
 data={};origins={};entries=[];external={};families={}
 def add(name,p,r=None):
  p=Path(p);r=r or desc(p);b=checked(r)
  if str(p) in origins:
   prior=origins[str(p)];assert prior['original']==r and data[prior['path']]==b;return prior['path']
  assert name not in data and not name.startswith('/') and '..' not in Path(name).parts
  kind='png' if p.suffix=='.png' else 'utf8'
  if kind=='utf8':b.decode('utf8')
  row=dict(path=name,kind=kind,original=r);data[name]=b;entries.append(row);origins[str(p)]=row;return name
 def family(r):
  if r['path'] in families:assert families[r['path']]==r;return
  index=json.loads(checked(r));base=Path(r['path']).parent;names=[x['path'] for x in index['files']]
  assert len(names)==len(set(names)) and {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}==set(names)|{'index.json'}
  add('sources/'+base.name+'/index.json',r['path'],r)
  for x in index['files']:add('sources/'+base.name+'/'+x['path'],base/x['path'],{**x,'path':str(base/x['path'])})
  families[r['path']]=r
 def ext(r):checked(r);external[r['path']]=r
 records=[]
 for label,runtime in RUNS:
  for p in sorted(runtime.rglob('*')):
   assert not p.is_symlink()
   if not p.is_file():continue
   relative=p.relative_to(runtime)
   if relative.parts[0] in ['app','cache']:continue
   assert p.suffix not in ['.wasm','.a','.o']
   add(label+'/runtime/'+relative.as_posix(),p)
  monitor=Path(str(runtime)+'-external-root')
  for p in sorted(monitor.rglob('*')):
   assert not p.is_symlink()
   if p.is_file():add(label+'/runtime-outer/'+p.relative_to(monitor).as_posix(),p)
  result=json.loads((runtime/'result.json').read_text());authority=json.loads(checked(result['rootAuthority']))
  add(label+'/authority/runtime.json',result['rootAuthority']['path'],result['rootAuthority'])
  records.append(dict(label=label,runtimeRoot=str(runtime),runtimeResult=desc(runtime/'result.json'),rootAuthority=result['rootAuthority']))
 rr=json.loads((RUNS[0][1]/'result.json').read_text());ra=json.loads(checked(rr['rootAuthority']))
 for label,runtime in RUNS[1:]:
  other=json.loads((runtime/'result.json').read_text())
  for k in ['component','componentAudit','constructionResult','inputEntry','inputSourceIndex','sourceIndex']:assert other[k]==rr[k]
 cr=json.loads(checked(rr['constructionResult']));constructor=Path(rr['constructionResult']['path']).parent
 for name in ['result.json','component-audit.json','api-return/node-result.json','api-return/returned-imports.json','api-return/returned-own-shape.json','api-return/requested-options.json','component-wit/stdout.log']:
  add('constructor/'+name,constructor/name)
 # The constructor's complete raw streams/parents are already closed in V4.
 prior=NEXT/'next-intl-runtime-root-results-v1/body-context-v4-review'
 pi=desc(prior/'index.json');pr=desc(prior/'review.json')
 assert pi['sha256']=='03a56dd3139b84e1490033e5ca8282af67f4acd7da3125d45e2c799b9762d289'
 assert pr['sha256']=='07e47d0f709d928cc70017e6bbb52c48d3acad26b91f82497b6f41acf7682c05'
 add('prior-constructor-review/index.json',pi['path'],pi);add('prior-constructor-review/review.json',pr['path'],pr)
 parentRows=[]
 for x in json.loads(checked(pi))['files']:
  r={**x,'path':str(prior/x['path'])};checked(r);parentRows.append(r)
 add('authority/constructor.json',cr['rootAuthority']['path'],cr['rootAuthority'])
 add('inputs/regression-wrapper.py',NEXT/'run-native-next-regression.py')
 for r in [rr['sourceIndex'],rr['inputSourceIndex'],cr['callerIndex']]:family(r)
 plan=json.loads(checked(ra['plan']));browserRow=next(r for r in plan['sourceFamilies'] if '/browser-hydration-candidate-v1/' in r['path']);family(browserRow)
 for key in ['component','engine','nativeMetadata','adapter']:ext(cr['artifacts'][key])
 for r in cr['artifacts']['engineBuildEvidence']:ext(r)
 for r in plan['protectedInputs']:ext(r)
 for key in ['wasmtime','node','monitor']:ext(plan[key])
 appManifest=json.loads(checked(plan['applicationInputs']));add('inputs/application-inputs.json',plan['applicationInputs']['path'],plan['applicationInputs'])
 add('inputs/fixture-contract.json',NEXT/'fixture-contract.json')
 expected={r['path']:r for r in appManifest['files']};appReadbacks=[]
 pins=json.loads((Path(browserRow['path']).parent/'asset-pins.json').read_text())['assets']
 for label,runtime in RUNS:
  app=runtime/'app';assert {p.relative_to(app).as_posix() for p in app.rglob('*') if p.is_file()}==set(expected)
  for relative,r in expected.items():
   source=Path(appManifest['root'])/relative;copy=app/relative;checked({**r,'path':str(source)});checked({**r,'path':str(copy)})
   a,b=source.stat(),copy.stat();assert b.st_nlink==1 and stat.S_IMODE(b.st_mode)==0o444 and (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino)
  assert stat.S_IMODE(app.stat().st_mode)==0o555 and all(stat.S_IMODE(p.stat().st_mode)==0o555 for p in app.rglob('*') if p.is_dir())
  appReadbacks.append(dict(run=label,files=len(expected),bytes=sum(x['bytes'] for x in expected.values()),originalAndCopyHashMatch=True,copyFilesMode='0444',copyDirectoriesMode='0555',distinctInodesAndSingleLinks=True,preopenReadOnlyRightsProved=False))
  for pin in pins:
   ext(pin['source']);r={k:pin[k] for k in ['sha256','bytes']};r['path']=str(app/('.next/'+pin['path'].removeprefix('/_next/')));ext(r)
  # Selected identities only, not a full macOS dylib closure.
  browser=json.loads((runtime/'client/browser/result.json').read_text())
  for key in ['executable','playwrightPackage','playwrightEntry']:ext(browser[key])
 for row in origins.values():checked(row['original'])
 for r in list(external.values())+parentRows:checked(r)
 with (HERE/'data.tar.gz').open('xb') as file:
  with gzip.GzipFile(fileobj=file,mode='wb',filename='',mtime=0) as compressed:
   with tarfile.open(fileobj=compressed,mode='w') as archive:
    for name,b in sorted(data.items()):
     info=tarfile.TarInfo(name);info.size=len(b);info.mode=0o600;info.mtime=0;archive.addfile(info,io.BytesIO(b))
 capsule=dict(schemaVersion=1,bundle=desc(HERE/'data.tar.gz'),entries=sorted(entries,key=lambda r:r['path']),externalReferences=list(external.values()),sourceFamilies=list(families.values()),priorConstructorReviewIndex=pi,priorConstructorReview=pr,priorConstructorPayloadsRehashed=len(parentRows),selectedOriginalsRehashedBeforeFinal=len(origins),runs=records,currentAppReadbacks=appReadbacks,
  bigBinaryOrApplicationTreeCopied=False,actualNetworkBodiesAndBrowserPngsIncluded=True,newTargetAction=False)
 (HERE/'capsule.json').write_text(json.dumps(capsule,indent=2)+'\n')
 print(json.dumps(dict(retainedRecords=len(entries),retainedBytes=sum(len(b) for b in data.values()),bundle=capsule['bundle'],externalRefs=len(external))))
if __name__=='__main__':main()
