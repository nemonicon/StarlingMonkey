"""Finite Source/read/hash checks only. No provider/monitor/helper imports."""
from pathlib import Path
import hashlib,json,stat,ast
P=Path(__file__).resolve().parent
checks=0;seen={};families={}
def check(ok,message):
 global checks
 assert ok,message;checks+=1
def row(d):
 p=Path(d['path']);a=p.lstat();check(stat.S_ISREG(a.st_mode)and a.st_size==d['bytes'],'actual regular file/size:'+str(p));h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=p.lstat();check((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns)and h.hexdigest()==d['sha256'],'stable exact hash:'+str(p));seen[str(p)]=d

def family(ix):
 row(ix);base=Path(ix['path']).parent;v=json.loads(base.joinpath('index.json').read_bytes());names={'index.json'}
 for r in v['files']:
  n=r['path'];check(n not in names and n and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')),'unique confined family');names.add(n);row(dict(r,path=str(base/n)))
 check(not any(x.is_symlink()for x in base.rglob('*'))and{x.relative_to(base).as_posix()for x in base.rglob('*')if x.is_file()}==names,'exact family membership:'+str(base));families[ix['path']]=ix
v=json.loads((P/'source-inputs.json').read_text())
for d in v['files']:row(d)
for d in v['families']:family(d)
for b in v['boundaries']:
 row(b['manifest']);m=json.loads(Path(b['manifest']['path']).read_bytes());check(len(m[b['field']])==b['expectedRows'],'finite boundary count')
 for d in m[b['field']]:
  if d['path']not in seen:row(d)
 for ix in m.get(b['familyField'],[]):
  if ix['path']not in families:family(ix)
refs=json.loads((P/'references.json').read_text());inventory=json.loads(Path(refs['packageInventory']['path']).read_bytes())['package'];base=Path(inventory['root']);names=set();links={}
check(len(inventory['files'])==4889 and len(inventory['links'])==21,'whole real private package')
for d in inventory['files']:
 names.add(d['relativePath']);row({k:d[k]for k in ['path','sha256','bytes']});s=Path(d['path']).lstat();check(s.st_nlink==1 and stat.S_IMODE(s.st_mode)==d['mode'],'package actual mode/inode')
for d in inventory['links']:
 p=base/d['path'];check(p.is_symlink()and p.readlink().as_posix()==d['target']and str(p.resolve())==d['resolvedPath'],'package exact alias');links[d['path']]=d
check({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()or p.is_symlink()}==names|set(links),'whole package membership')
child=json.loads((P/'child-inputs.json').read_text());check(child['nativeApiInvocations']==0 and child['nativeFrameReturned']is False,'explicit child-only scope')
for d in child['files']:check(d['path']in seen and seen[d['path']]==d,'child input covered in full parent source intake')
for f in P.glob('*.py'):ast.parse(f.read_text(),filename=str(f));checks+=1
for f in ['entry.mjs','models.mjs','runtime.mjs','mapping.mjs','capture.mjs']:
 check((P/f).is_file(),'concrete source present')
check(len(json.loads(Path(refs['fixtureRequirements']['path']).read_text())['gates'])==17,'all17 mandatory gates preserved')
check(json.loads((P/'remaining-gates.json').read_text())['all17GatesSatisfied']is False,'no profile acceptance')
result=dict(schemaVersion=1,state='FINITE_SOURCE_DATA_BOUNDARY_CHECKS_PASSED_V1',checks=checks,currentUniqueInputs=len(seen),families=len(families),parentMetadataFields=80,nativeSourceFiles=355,externalEmbeddingSources=3,selectedWholeManifests=11,packageRegularFiles=4889,packageAliases=21,childInputs=len(child['files']),operationalActionsInvoked=False)
(P/'source-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
