"""Independent finite Source/hash audit; no owner operational function imports."""
from pathlib import Path
import json,hashlib,ast,stat
P=Path(__file__).resolve().parent
S=P.parent/'combined-native-pure-runtime-control-candidate-v1'
SOURCE=dict(path=str(S/'index.json'),sha256='8feef25e0b40980877ad3d7b335256d937ed7603bd2a7e65a159b06fa0e0f41f',bytes=11770)
checks=0;files={};families={}
def check(v,m):
 global checks
 assert v,m;checks+=1

def read(d):
 p=Path(d['path']);a=p.lstat();check(stat.S_ISREG(a.st_mode)and a.st_size==d['bytes'],'ordinary exact size '+str(p));h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 z=p.lstat();check((a.st_dev,a.st_ino,a.st_mode,a.st_nlink,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_mode,z.st_nlink,z.st_size,z.st_mtime_ns,z.st_ctime_ns)and h.hexdigest()==d['sha256'],'stable exact hash '+str(p));files[str(p)]=d
 return p

def json_at(d):return json.loads(read(d).read_bytes())
def family(d):
 v=json_at(d);base=Path(d['path']).parent;names={'index.json'};rows=[d]
 for x in v['files']:
  n=x['path'];check(n not in names and n and not n.startswith('/')and '\\'not in n and all(q not in('','.','..')for q in n.split('/')),'unique finite family member');names.add(n);r=dict(x,path=str(base/n));read(r);rows.append(r)
 check(not any(q.is_symlink()for q in base.rglob('*'))and{q.relative_to(base).as_posix()for q in base.rglob('*')if q.is_file()}==names,'exact family membership '+str(base));families[d['path']]=d;return rows

def descriptor(p):
 b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
rows=family(SOURCE);check(len(rows)==75,'74 indexed plus index');refs=json.loads((S/'references.json').read_text());inputs=json.loads((S/'source-inputs.json').read_text())
for r in inputs['files']:read(r)
for r in inputs['families']:family(r)
parent=json_at(inputs['parentOnlyBoundary'])
for r in parent['files']:read(r)
for r in parent['families']:
 if r['path']not in families:family(r)
for b in parent['boundaries']:
 m=json_at(b['manifest']);check(len(m[b['field']])==b['expectedRows'],'finite original boundary count')
 for r in m[b['field']]:
  if r['path']not in files:read(r)
 for r in m.get(b['familyField'],[]):
  if r['path']not in families:family(r)
inv=json_at(refs['packageInventory'])['package'];base=Path(refs['loaderPackageRoot']);check(inv['root']==str(base)and len(inv['files'])==4889 and len(inv['links'])==21,'whole private package4889+21');names=set();aliases=set()
for r in inv['files']:
 check(r['path']==str(base/r['relativePath'])and r['relativePath']not in names,'actual private package path');names.add(r['relativePath']);read({k:r[k]for k in ['path','sha256','bytes']});q=Path(r['path']).lstat();check(q.st_nlink==1 and stat.S_IMODE(q.st_mode)==r['mode'],'actual private mode/inode')
for r in inv['links']:
 p=base/r['path'];check(p.is_symlink()and p.readlink().as_posix()==r['target']and str(p.resolve())==r['resolvedPath']and p.resolve().is_relative_to(base),'exact confined alias');aliases.add(r['path'])
check({p.relative_to(base).as_posix()for p in base.rglob('*')if p.is_file()or p.is_symlink()}==names|aliases,'exact private package membership')
# Derivations are text assembly/extraction, never import old operational guards.
d=json.loads((S/'source-derivations.json').read_text());donor=read(d['stdlibCapturePrefixDonor']).read_text();prefix=donor.split(d['prefixEndsBefore'],1)[0];sub=d['ownOriginalPathSubstitution'];prefix=prefix.replace("const ORIGINAL='"+sub['from']+"';","const ORIGINAL='"+sub['to']+"';")
check((S/'entry.mjs').read_text()==prefix+(S/'entry-body.txt').read_text(),'exact actual prefix+own body assembly');check((S/'wave.mjs').read_bytes()==read(d['waveDonor']).read_bytes(),'byte-identical WAVE parser')
# Actual immutable proof/metadata/data, not model-only schema assertions.
p=json_at(refs['actualPureReview']['result']);k=json_at(refs['actualPureContract']);check(p['generatedFiles']==refs['generated']==k['generatedFiles']and p['artifacts']==k['artifacts'],'whole actual artifact maps')
for group in ['requiredFixedValues','requiredExactDescriptors']:
 for n,v in k[group].items():check(p[n]==v and type(p[n])is type(v),'actual contract '+n)
check(p['publicAbiSignatures']==[dict(name='run',params=[],result='string')]and p['emittedImports']==[],'actual original scalar/import graph')
metadata=json_at(refs['nativeMetadata']);record=json_at(refs['actualReadOnlyData']);check(len(metadata)==80 and len(metadata['sourceManifest'])==355 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==11,'actual complete80/355+3/11');check(record['bootstrap']['metadata']==metadata and record['bootstrap']['engine']==refs['nativeEngine'],'actual full original retained DATA')
ix=p['artifacts']['constructionIndex'];done=p['artifacts']['constructionCompletion'];read(ix);read(done);v=json.loads(Path(ix['path']).read_text());check(len(v['files'])==18,'actual construction publication required18 rows')
# Source dynamic APIs all execute only after byte authentication; compile AST only.
for f in S.glob('*.py'):ast.parse(f.read_text(),filename=str(f));checks+=1
root=json.loads((S/'future-root-authority.template.json').read_text());check(root['state'].startswith('UNISSUED')and all(root[n]is None for n in ['sourceIndex','sourceIndependentReview','entry','externalController','parentNativeReadOnlyApiAllowed','nodeFixtureOracleAllowed','pureGeneratedImportAllowed','pureRunAllowed','stockWasmtimeAllowed']),'unissued Root/action template')
source_contract=json.loads((S/'future-source-review-contract.json').read_text());check(source_contract['requiredState']=='INDEPENDENT_COMBINED355_PURE_RUNTIME_CONTROL_SOURCE_REVIEW_PASSED_V1'and source_contract['actualProof']is None and source_contract['grantsRuntimeAuthority']is False,'actual prospective peer contract')
summary=dict(schemaVersion=1,state='INDEPENDENT_FINITE_PURE_CONTROL_SOURCE_AUTHENTICATION_PASSED_V1',sourceIndex=SOURCE,checks=checks,currentUniqueInputFiles=len(files),logicalInputBytes=sum(x['bytes']for x in files.values()),sourceFamilies=len(families),ownerIndexedMembers=74,ownerActualFiles=75,privatePackageFiles=4889,privatePackageAliases=21,exactDerivations=2,pythonAstFiles=len(list(S.glob('*.py'))),ownerOperationalFunctionsImportedOrInvoked=False)
(P/'source-authentication.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
