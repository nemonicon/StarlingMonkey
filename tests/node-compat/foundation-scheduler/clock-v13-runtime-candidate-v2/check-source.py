"""Full read/hash, actual module context and reversible Source checks. No phases."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,stat
OWN=Path(__file__).resolve().parent;checks=0;seen={}

def need(v,m):
 global checks
 assert v,m;checks+=1

def data(path):return json.loads(Path(path).read_bytes())
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def desc(path):return dict(path=str(path),sha256=sha(path),bytes=path.stat().st_size)
def checked(row):
 p=Path(row['path']);need(set(row)=={'path','sha256','bytes'} and p.is_absolute() and str(p)==row['path'] and '..' not in p.parts,'canonical original descriptor')
 q=Path('/private'+str(p)) if str(p).startswith('/tmp/') else p
 for parent in (q,*q.parents):need(not parent.is_symlink(),'no undeclared alias')
 a=q.stat();need(stat.S_ISREG(a.st_mode) and a.st_size==row['bytes'],'regular exact size');need(sha(q)==row['sha256'],'whole SHA');z=q.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns),'stable identity')
 if row['path'] in seen:need(seen[row['path']]==row,'one descriptor per original path')
 seen[row['path']]=row;return q

def family(row):
 checked(row);value=data(row['path']);root=Path(row['path']).parent;names=set()
 for r in value['files']:
  n=r['path'];need(n and not n.startswith('/') and '\\' not in n and all(p not in ('','.','..') for p in n.split('/')) and n not in names,'confined family member');names.add(n);checked(dict(path=str(root/n),sha256=r['sha256'],bytes=r['bytes']))
 need(not any(p.is_symlink() for p in root.rglob('*')) and {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}==names|{'index.json'},'complete unchanged family')
refs=data(OWN/'references.json');inputs=data(OWN/'source-inputs.json');before=[desc(OWN/n) for n in ('entry.mjs','body.mjs','models.mjs','wave.mjs','external.py','test-pure.mjs','test-presence.mjs','references.json','source-inputs.json')]
need(len(inputs['files'])==len({r['path'] for r in inputs['files']})==12079 and len(inputs['families'])==18,'full inherited genuine intake plus priorSource/HOLD')
for row in inputs['files']:checked(row)
for ix in inputs['families']:family(ix)
held=data(refs['previousSourceHold']['result']['path']);correction=data(refs['requiredCorrectionContract']['path']);need(held['state']=='INDEPENDENT_CLOCK_V13_REACTDOM_RUNTIME_SOURCE_REVIEW_HELD_V1' and held['sourceReviewPassed'] is False and held['sourceIndex']==correction['heldSourceIndex']==refs['previousSourceIndex'],'actual null-presence HOLD lineage')
deriv=data(OWN/'derivations.json');edits=0
for item in deriv['files']:
 text=checked(item['donor']).read_text();before_text=text
 for e in item['edits']:need(text.count(e['before'])==e['occurrences'],'exact forward occurrence');text=text.replace(e['before'],e['after']);edits+=1
 need(text==(OWN/item['output']).read_text() and desc(OWN/item['output'])==item['after'],'exact forward bytes')
 for e in reversed(item['edits']):need(text.count(e['after'])==e['occurrences'],'exact inverse occurrence');text=text.replace(e['after'],e['before'])
 need(text==before_text,'exact inverse bytes')
source=(OWN/'entry.mjs').read_text();body=(OWN/'body.mjs').read_text()
need('clock-v13-runtime-candidate-v2' in source and 'primary!==null' not in source+body,'real ownSource and null sentinel removed')
need(body.count('primaryPresent,primary:observed(primary)')==3 and body.count('catch(error){primaryPresent=true;primary=error;}')==3,'all three phase failure records/catches')
need(source.count('primaryPresent=true;primary=error;throw error;')==2 and source.count('if(primaryPresent)throw new AggregateError')==2,'all two entry combined failures')
# Inert import of actual stdlib-only external module; no fake globals or run call.
path=OWN/'external.py';tree=ast.parse(path.read_text())
for n in tree.body:
 need(isinstance(n,(ast.Expr,ast.Import,ast.ImportFrom,ast.Assign,ast.FunctionDef,ast.If)),'finite inert external definitions')
 if isinstance(n,ast.Import):need(all(a.name in ['hashlib','importlib.util','json','os','stat','sys'] for a in n.names),'stdlib only')
 if isinstance(n,ast.ImportFrom):need(n.module=='pathlib','stdlib pathlib')
 if isinstance(n,ast.Expr):need(isinstance(n.value,ast.Constant) and isinstance(n.value.value,str),'docstring only')
 if isinstance(n,ast.If):need(ast.unparse(n.test)=="__name__ == '__main__'",'dormant CLI only')
spec=importlib.util.spec_from_file_location('genuine_inert_clock_runtime_v2_external',path);external=importlib.util.module_from_spec(spec);spec.loader.exec_module(external)
need(external.OWN==Path(external.__file__).resolve().parent==OWN and refs['originalRoot']==str(OWN),'actual physical OWN and Source reference')
for k in ('mappedOutputRoot','runtimeOutputRoot'):need(str(refs[k]).endswith('-v2') and not Path(refs[k]).exists() and not Path(refs[k]+'-external-root').exists(),'fresh inactive v2 namespaces')
# Full actual package, including declared aliases only, without importing it.
pkg=data(refs['packageInventory']['path'])['package'];root=Path(pkg['root']);need(str(root)==refs['loaderPackageRoot'] and stat.S_IMODE(root.stat().st_mode)==0o700 and not root.is_symlink(),'actual private package')
files={r['relativePath']:r for r in pkg['files']};links={r['path']:r for r in pkg['links']};need(len(files)==4889 and len(links)==21,'whole package counts');actual=set()
for p in root.rglob('*'):
 name=p.relative_to(root).as_posix();s=p.lstat()
 if p.is_symlink():need(name in links and os.readlink(p)==links[name]['target'] and str(p.resolve())==links[name]['resolvedPath'] and p.resolve().is_relative_to(root),'exact alias');actual.add(name)
 elif p.is_dir():need(stat.S_IMODE(s.st_mode)==0o700,'private dirs')
 else:r=files[name];need(s.st_nlink==1 and stat.S_IMODE(s.st_mode)==r['mode'],'independent regular package');checked({k:r[k] for k in ('path','sha256','bytes')});actual.add(name)
need(actual==set(files)|set(links),'whole package physical membership')
proof=data(refs['actualArtifactReview']['result']['path']);contract=data(refs['actualArtifactContract']['path']);need(proof['artifacts']==contract['artifacts']==refs['artifacts'] and len(refs['artifacts'])==14 and len(refs['generatedFiles'])==7,'same whole original artifact maps')
parent=data(Path(refs['previousSourceIndex']['path']).parent/'references.json')
for key in ('artifacts','generatedFiles','component','nativeEngine','nativeMetadata','guest','bundle','oracleValue','oracleEvidence','mappingOptions','inlineCoreModules'):need(refs[key]==parent[key],'unchanged actual role: '+key)
# Exact whole Node oracle is DATA, never rerun.
command=refs['oracleEvidence']['command'];stdout=json.loads(checked(command['stdout']).read_bytes());need(stdout['status']=='passed' and stdout['value']==refs['oracleValue'] and command in data(refs['oracleEvidence']['report']['path'])['commands'],'whole retained raw/report Node oracle')
for p in OWN.glob('*.py'):ast.parse(p.read_text(),filename=str(p));checks+=1
for row in before:need(desc(Path(row['path']))==row,'own runtime Source unchanged across reader')
(OWN/'source-check-results.json').write_text(json.dumps(dict(schemaVersion=1,passed=True,checks=checks,inputRows=12079,completeFamilies=18,packageFiles=4889,packageAliases=21,derivedFiles=6,reversibleEdits=edits,realExternalOwn=str(external.OWN),externalModuleDefinitionsImported=True,moduleGlobalsInjectedOrRebound=False,actualArtifactMapsUnchanged=True,actualNodeOracleRerun=False,jcoOrShimOrNativePreflightOrGeneratedModuleOrMonitorOrWasmtimeOrGuestInvoked=False),indent=2)+'\n');print(json.dumps(dict(checks=checks,files=12079,families=18,passed=True,actions=False)))
