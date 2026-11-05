"""Independent Source/data boundary, package/context and oracle audit. No actions."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,re,stat
OWN=Path(__file__).resolve().parent;SOURCE=OWN.parent/'clock-v13-runtime-candidate-v1';EXPECTED='3107eee7440638cef9b54d9add797cc5ffda8c766f8fd060b550be7493d0f939'
checks=0;captured={}

def need(v,m):
 global checks
 assert v,m;checks+=1

def desc(path):
 p=Path(path);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)

def checked(row):
 p=Path(row['path']);need(set(row)=={'path','sha256','bytes'} and p.is_absolute() and str(p)==row['path'] and '..' not in p.parts,'actual canonical descriptor')
 q=Path('/private'+str(p)) if str(p).startswith('/tmp/') else p
 for a in (q,*q.parents):need(not a.is_symlink(),'ordinary path except system/tmp alias: '+str(a))
 a=q.stat();need(stat.S_ISREG(a.st_mode) and a.st_size==row['bytes'],'regular exact size');h=hashlib.sha256()
 with q.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=q.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns) and h.hexdigest()==row['sha256'],'stable whole SHA')
 if str(p) in captured:need(captured[str(p)]==row,'single descriptor identity')
 captured[str(p)]=row;return q

def read(row):return json.loads(checked(row).read_bytes())
def family(row):
 value=read(row);root=Path(row['path']).parent;names=set()
 for r in value['files']:
  n=r['path'];need(n and not n.startswith('/') and '\\' not in n and all(p not in ('','.','..') for p in n.split('/')) and n not in names,'unique confined family row');names.add(n);checked(dict(path=str(root/n),sha256=r['sha256'],bytes=r['bytes']))
 need(not any(p.is_symlink() for p in root.rglob('*')),'no family aliases')
 need({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}==names|{'index.json'},'whole family membership')
index=desc(SOURCE/'index.json');need(index['sha256']==EXPECTED,'assigned exact seal');family(index)
inputs=json.loads((SOURCE/'source-inputs.json').read_bytes());refs=json.loads((SOURCE/'references.json').read_bytes());need(len(inputs['files'])==len({r['path'] for r in inputs['files']})==11995 and len(inputs['families'])==16,'whole actual Source intake')
for r in inputs['files']:checked(r)
for ix in inputs['families']:family(ix)
package=read(refs['packageInventory'])['package'];root=Path(package['root']);need(str(root)==refs['loaderPackageRoot'] and not root.is_symlink() and stat.S_IMODE(root.stat().st_mode)==0o700,'actual private package root')
files={r['relativePath']:r for r in package['files']};links={r['path']:r for r in package['links']};need(len(files)==4889 and len(links)==21,'complete physical package')
actual=set()
for p in root.rglob('*'):
 n=p.relative_to(root).as_posix();s=p.lstat()
 if p.is_symlink():need(n in links and os.readlink(p)==links[n]['target'] and str(p.resolve())==links[n]['resolvedPath'] and p.resolve().is_relative_to(root),'exact package alias');actual.add(n)
 elif p.is_dir():need(stat.S_IMODE(s.st_mode)==0o700,'private package dirs')
 else:
  r=files[n];need(s.st_nlink==1 and stat.S_IMODE(s.st_mode)==r['mode'],'independent package mode/inode');checked({k:r[k] for k in ('path','sha256','bytes')});actual.add(n)
need(actual==set(files)|set(links),'exact complete package names')
proof=read(refs['actualArtifactReview']['result']);contract=read(refs['actualArtifactContract']);need(proof['artifacts']==contract['artifacts']==refs['artifacts'] and len(refs['artifacts'])==14,'whole actual artifact map')
for r in refs['artifacts'].values():checked(r)
for r in refs['generatedFiles'].values():checked(r)
need(len(refs['generatedFiles'])==7 and proof['componentSha256']==refs['component']['sha256'] and proof['engineSha256']==refs['nativeEngine']['sha256'],'unchanged component/native and generated tuple')
metadata=read(refs['nativeMetadata']);need(len(metadata)==64 and len(metadata['sourceManifest'])==342 and len(metadata['componentizeSourceManifest'])==3 and len(metadata['selectedModuleManifests'])==9,'full genuine342+3/64/9 frame DATA')
report=read(refs['oracleEvidence']['report']);command=refs['oracleEvidence']['command'];stdout=read(command['stdout']);checked(command['stderr'])
need(command['status']==0 and command['closed'] is True and command['ownedGroupGone'] is True and command['terminalExitZeroObserved'] is True and not command['timedOut'] and not command['outputLimitExceeded'] and command['errors']==command['signals']==[],'actual retained clean Node command')
need(stdout['status']=='passed' and stdout['value']==refs['oracleValue'],'derive whole oracle from raw retained stdout')
public=json.loads(stdout['value']);need(list(public)==['library','html','bytes'] and public['library']=='react-dom/server.edge' and public['html']=='<p id="wasm-ssr">Hello from real ReactDOM</p>' and public['bytes']==len(public['html'].encode())==45,'whole HTML/UTF8 bytes')
need(any(v==command for v in report.get('commands',[])) or str(command['pid']) in json.dumps(report),'command belongs actual report')
segments=json.loads((SOURCE/'derivations.json').read_bytes())['segments']
for segment in segments:
 donor=checked(segment['donor']).read_text();text=segment['text'];need(text in donor and hashlib.sha256(text.encode()).hexdigest()==segment['sha256'] and len(text.encode())==segment['bytes'],'exact donor segment')
 need(any(text in (SOURCE/f).read_text() for f in ('entry.mjs','wave.mjs','external.py')),'actual target segment retained')
# Actual inert stdlib controller initialization; no fabricated namespace/Frame.
path=SOURCE/'external.py';tree=ast.parse(path.read_text())
for node in tree.body:
 need(isinstance(node,(ast.Expr,ast.Import,ast.ImportFrom,ast.Assign,ast.FunctionDef,ast.If)),'inert top-level kinds')
 if isinstance(node,ast.Import):need(all(a.name in ['hashlib','importlib.util','json','os','stat','sys'] for a in node.names),'stdlib import only')
 if isinstance(node,ast.ImportFrom):need(node.module=='pathlib','stdlib pathlib only')
 if isinstance(node,ast.Expr):need(isinstance(node.value,ast.Constant) and isinstance(node.value.value,str),'docstring only')
 if isinstance(node,ast.If):need(ast.unparse(node.test)=="__name__ == '__main__'",'only dormant CLI')
spec=importlib.util.spec_from_file_location('actual_inert_clock_runtime_external',path);external=importlib.util.module_from_spec(spec);spec.loader.exec_module(external)
need(external.OWN==Path(external.__file__).resolve().parent==SOURCE,'actual external OWN follows genuine physical file')
need(refs['originalRoot']==str(SOURCE),'own reference original context')
for n in ('mappedOutputRoot','runtimeOutputRoot'):need(not Path(refs[n]).exists() and not Path(refs[n]+'-external-root').exists(),'no actual phase output yet')
edges=[]
for f in ('entry.mjs','body.mjs','models.mjs','wave.mjs'):
 p=SOURCE/f
 for m in re.finditer(r"(?:from\s*|import\s*)['\"]([^'\"]+)['\"]",p.read_text()):
  if m[1].startswith('.'):
   target=Path(os.path.abspath(p.parent/m[1]));need(str(target) in captured,'physical import closure');edges.append(dict(importer=str(p),specifier=m[1],target=str(target)))
for role in ('nativePreflight','jcoApi','shimClocks','shimIo','parser','node','wasmtime','monitorEntry'):need(refs[role]['path'] in captured,'actual later dynamic role captured: '+role)
for r in list(captured.values()):checked(r)
(OWN/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=sorted(captured.values(),key=lambda r:r['path'])),indent=2)+'\n')
result=dict(schemaVersion=1,sourceIntegrityPassed=True,checks=checks,sourceIndex=index,inputRows=11995,sourceFamilies=16,packageFiles=4889,packageAliases=21,wholeArtifactMap=refs['artifacts'],wholeGeneratedMap=refs['generatedFiles'],donorSegments=10,physicalModuleEdges=edges,actualExternalOwn=str(external.OWN),actualExternalFile=external.__file__,actualOracleValue=stdout['value'],nativeFields=64,nativeSources=342,externalSources=3,selectedManifests=9,actualModuleImportedOnlyAsInertStdlibDefinitions=True,ownerAPIsOrMonitorOrJcoOrShimOrGeneratedOrWasmtimeOrGuestInvoked=False)
(OWN/'data-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('wholeArtifactMap','wholeGeneratedMap','physicalModuleEdges')},indent=2))
