"""Independent read/hash/AST plus inert stdlib-module context inspection only."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,re,stat
OWN=Path(__file__).resolve().parent
SOURCE=OWN.parent/'ownership-secret-runtime-candidate-v3'
EXPECTED='1f357d3a2513fc8a823db4c770963bb5638783f61918ce6f68fa3c3d940ff24c'
rows={};checks=0

def need(value,message):
 global checks
 assert value,message;checks+=1

def read(path):return json.loads(Path(path).read_bytes())

def checked(row):
 p=Path(row['path']);need(set(row)=={'path','sha256','bytes'} and p.is_absolute() and str(p)==row['path'] and '..' not in p.parts and '\\' not in str(p) and '\0' not in str(p),'canonical descriptor')
 q=Path('/private'+str(p)) if str(p).startswith('/tmp/') else p
 for ancestor in (q,*q.parents):need(not ancestor.is_symlink(),'no undeclared symlink: '+str(ancestor))
 a=q.stat();need(stat.S_ISREG(a.st_mode) and a.st_size==row['bytes'],'regular exact size')
 h=hashlib.sha256()
 with q.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 z=q.stat();need((a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)==(z.st_dev,z.st_ino,z.st_size,z.st_mtime_ns,z.st_ctime_ns) and h.hexdigest()==row['sha256'],'unchanged exact bytes')
 if str(p) in rows:need(rows[str(p)]==row,'one exact descriptor')
 rows[str(p)]=row;return q

def desc(path):
 p=Path(path);return dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)

def family(row):
 checked(row);value=read(row['path']);root=Path(row['path']).parent;names=set()
 need(value['schemaVersion']==1,'family schema')
 for f in value['files']:
  name=f['path'];need(name and not name.startswith('/') and '\\' not in name and all(p not in ('','.','..') for p in name.split('/')) and name not in names,'finite unique family member');names.add(name)
  checked(dict(path=str(root/name),sha256=f['sha256'],bytes=f['bytes']))
 need(not any(p.is_symlink() for p in root.rglob('*')),'no family symlinks')
 need({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}==names|{'index.json'},'exact family membership')

index=desc(SOURCE/'index.json');need(index['sha256']==EXPECTED,'actual assigned source pin');family(index)
inputs=read(SOURCE/'source-inputs.json');refs=read(SOURCE/'references.json')
need(len(inputs['files'])==len({r['path'] for r in inputs['files']})==34167 and len(inputs['modeRows'])==34167 and len(inputs['families'])==35,'full actual intake')
for r in inputs['files']:checked(r)
for item in inputs['modeRows']:need(stat.S_IMODE(checked(item['file']).stat().st_mode)==item['mode'],'exact input mode')
for ix in inputs['families']:family(ix)
for t in inputs['historicalDonorTrees']:
 root=Path(t['root']);need(not any(p.is_symlink() for p in root.rglob('*')),'historical no symlinks');need({p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}==set(t['names']),'historical exact named context')
# Every derivation independently forwards and reverses; do not execute author sealer.
derivation=read(SOURCE/'derivations.json');edits=0
for f in derivation['files']:
 before=checked(f['donor']).read_text();after=checked(f['after']).read_text();work=before
 for e in f['edits']:
  need(work.count(e['before'])==e['occurrences'],'forward occurrence');work=work.replace(e['before'],e['after']);edits+=1
 need(work==after,'forward exact bytes: '+f['output'])
 for e in reversed(f['edits']):
  need(work.count(e['after'])==e['occurrences'],'reverse occurrence');work=work.replace(e['after'],e['before'])
 need(work==before,'reverse exact bytes: '+f['output'])
# Literal source graph, physically resolved from every actual file. Known dynamic
# own relative imports are separately enumerated below; no module execution.
source_files=[SOURCE/n for n in ('entry.mjs','runtime-body.mjs','loading.mjs','oracle.mjs','checks.mjs','parser-tuple.mjs')]
edges=[]
for path in source_files:
 text=path.read_text()
 for match in re.finditer(r"(?:from\s*|import\s*)['\"]([^'\"]+)['\"]",text):
  name=match.group(1)
  if name.startswith('.'):
   target=Path(os.path.abspath(path.parent/name));need(str(target) in rows,'physical literal dependency captured: '+str(target));edges.append(dict(importer=str(path),specifier=name,target=str(target)))
for name in ('entry.mjs','runtime-body.mjs'):
 need(str(SOURCE/name) in [str(SOURCE/f['path']) for f in read(SOURCE/'index.json')['files']],'own dynamic CLI/module in own family')
for key in ('retainedApi','packagingHelper','monitorEntry','node','pythonExecutable'):need(refs[key]['path'] in rows,'actual action dependency authenticated: '+key)
proof=read(refs['actualArtifactReview']['result']['path']);contract=read(refs['actualArtifactContract']['path'])
need(proof['verifiedPassed'] is True and proof['state']=='INDEPENDENT_CRYPTO_OWNER355_SECRET_COMPONENT_V2_ARTIFACT_REVIEW_PASSED_V1' and proof['artifacts']==contract['artifacts']==refs['artifacts'],'whole genuine artifact tuple')
need(proof['nativeSourceFiles']==355 and proof['fullMetadataFields']==75 and proof['selectedManifestCount']==11 and proof['componentSha256']==refs['artifacts']['component']['sha256'],'actual crypto native identity, not combined80')
# The external module has only inert stdlib imports/definitions and literal constants.
source=(SOURCE/'external.py').read_text();tree=ast.parse(source,filename=str(SOURCE/'external.py'))
allowed={'Import','ImportFrom','Assign','FunctionDef','Expr','If'}
for node in tree.body:
 need(type(node).__name__ in allowed,'finite external module initialization')
 if isinstance(node,ast.Import):need(all(n.name in ('hashlib','importlib.util','json','os','stat','sys') for n in node.names),'stdlib imports only')
 if isinstance(node,ast.ImportFrom):need(node.module=='pathlib','stdlib pathlib only')
 if isinstance(node,ast.Expr):need(isinstance(node.value,ast.Constant) and isinstance(node.value.value,str),'docstring only')
 if isinstance(node,ast.If):need(ast.unparse(node.test)=="__name__ == '__main__'",'only dormant CLI branch')
spec=importlib.util.spec_from_file_location('independent_actual_secret_runtime_v3_external',SOURCE/'external.py');external=importlib.util.module_from_spec(spec);spec.loader.exec_module(external)
need(external.OWN==SOURCE==Path(external.__file__).resolve().parent,'real OWN literal and __file__')
need(external.OUTPUT==Path(refs['outputRoot']) and external.OUT==Path(refs['externalOutputRoot']),'genuine output constants')
need(not external.OUTPUT.exists() and not external.OUT.exists(),'no actual V3 runtime output yet')
# No assigned values, namespace injection, replacement globals, authorize/run/monitor calls.
context=dict(actualModule=desc(SOURCE/'external.py'),moduleFile=external.__file__,actualOwn=str(external.OWN),output=str(external.OUTPUT),externalOutput=str(external.OUT),stdlibDefinitionsImported=True,runOrAuthorizeOrMonitorCalled=False,moduleGlobalsInjectedOrRebound=False)
for r in rows.values():checked(r)
(OWN/'input-hashes.json').write_text(json.dumps(dict(schemaVersion=1,files=sorted(rows.values(),key=lambda r:r['path'])),indent=2)+'\n')
report=dict(schemaVersion=1,passed=True,checks=checks,sourceIndex=index,actualInputRows=34167,sourceFamilies=35,derivedFiles=len(derivation['files']),exactReversibleEdits=edits,literalModuleEdges=edges,actualExternalContext=context,wholeArtifactMap=refs['artifacts'],noOwnerActionInvoked=True,generatedModuleImported=False,cryptoOrKeyOperationsInvoked=False)
(OWN/'read-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('literalModuleEdges','wholeArtifactMap')},indent=2))
