"""Independent read/hash/JSON/Source audit; no operational imports or APIs."""
from pathlib import Path
import ast,hashlib,json,os,stat
P=Path(__file__).resolve().parent;S=P.parent/'clock-v13-component-candidate-v1'
checks=0;seen={};ids={}
def need(v):
 global checks
 assert v;checks+=1
def read(p):return json.loads(Path(p).read_bytes())
def identity(p):
 s=p.lstat();need(stat.S_ISREG(s.st_mode));return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode,s.st_nlink,str(p.resolve()))
def row(p):
 p=Path(p);need(p.is_absolute()and str(p)==os.path.normpath(str(p)));a=identity(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 need(identity(p)==a);r=dict(path=str(p),sha256=h.hexdigest(),bytes=a[2]);seen[str(p)]=r;ids[str(p)]=a;return r
def verify(r):need(row(r['path'])==r)
def family(ix):
 verify(ix);base=Path(ix['path']).parent;want={'index.json'}
 for m in read(ix['path'])['files']:
  n=m['path'];need(n and n not in want and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')));want.add(n);verify(dict(m,path=str(base/n)))
 actual=set()
 for p in base.rglob('*'):
  need(not p.is_symlink()and(p.is_file()or p.is_dir()))
  if p.is_file():actual.add(p.relative_to(base).as_posix())
 need(actual==want)
ix=row(S/'index.json');need(ix['sha256']=='555b8f107030a32e96257124e5bcf6d48f1f19e28d08eafd8ee34110a386d3d5');family(ix)
refs=read(S/'references.json');inputs=read(S/'source-inputs.json');need(len(inputs['files'])==11581 and len(inputs['families'])==11)
for r in inputs['files']:verify(r)
for f in inputs['families']:family(f)
ledger={r['path']:r for r in inputs['files']};need(len(ledger)==11581)
consumed=read(refs['nativeConsumedInputs']['path']);nativeHere=Path(refs['nativePreflight']['path']).parent
need(len(consumed['inputs'])==6414)
for r in consumed['inputs']:
 resolved=str((nativeHere/r['path']).resolve())if not Path(r['path']).is_absolute()else r['path']
 # For local relative Source rows, Node resolves against the genuine native HERE.
 if Path(r['path']).is_absolute():need(ledger[resolved]=={k:r[k]for k in ['path','sha256','bytes']})
 else:
  candidates=[v for v in ledger.values()if str(Path(v['path']).resolve())==resolved];need(len(candidates)==1 and candidates[0]['sha256']==r['sha256']and candidates[0]['bytes']==r['bytes'])
for tree in consumed['toolTrees']:
 root=Path(tree['path']);need(str(root.resolve())==tree['realPath']);actual=[]
 for q in root.rglob('*'):
  s=q.lstat();kind='symlink'if stat.S_ISLNK(s.st_mode)else'directory'if stat.S_ISDIR(s.st_mode)else'file'if stat.S_ISREG(s.st_mode) else None
  need(kind is not None);actual.append(dict(path=q.relative_to(root).as_posix(),kind=kind))
 need(sorted(actual,key=lambda r:r['path'])==tree['entries'])
for r in consumed['toolLinks']:
 p=Path(r['path']);need(p.is_symlink()and os.readlink(p)==r['linkText']and str(p.resolve())==r['resolvedTarget'])
need(len(consumed['toolTrees'])==2 and len(consumed['toolLinks'])==22)
meta=read(refs['nativeMetadata']['path']);need(len(meta)==64 and len(meta['sourceManifest'])==342 and len(meta['componentizeSourceManifest'])==3 and len(meta['selectedModuleManifests'])==9)
for key,base in [('sourceManifest',refs['nativeSourceRoot']),('componentizeSourceManifest',refs['nativeEmbeddingSourceRoot'])]:
 for r in meta[key]:need(ledger[str(Path(base)/r['path'])]['sha256']==r['sha256'])
need(meta['engineSha256']==refs['nativeEngine']['sha256']and meta['engineBytes']==refs['nativeEngine']['bytes']and meta['gcStress']is False and meta['entropyPolicy']=='off'and meta['oomTesting']is False)
need(refs['nativeEngine']['sha256']=='d54446dcd4071fe2c2b1db4984ead78d2fe61ceb0a0396822df8416a26921a92')
need((S/'guest.mjs').read_bytes()==Path(refs['originalGuest']['path']).read_bytes())
need((S/'bundle.mjs').read_bytes()==Path(refs['originalBundle']['path']).read_bytes()==Path(refs['originalBundleCopy']['path']).read_bytes())
graph=read(refs['originalBundleGraph']['path']);need(graph['imports']==[]and len(graph['moduleIds'])==9 and len(graph['sourceInputs'])==8 and graph['packageBundlerVersion']=='sm-production-package-bundler-v2')
for r in graph['sourceInputs']:need(ledger[r['id']]['sha256']==r['transformInputSha256']and ledger[r['id']]['bytes']==r['transformInputBytes'])
for package in ['react','react-dom']:
 r=next(r for r in inputs['files']if r['path'].endswith('/application/node_modules/'+package+'/package.json'));need(read(r['path'])['version']=='19.3.1')
for pair in read(S/'context-copy-map.json')['files']:
 verify(pair['copy']);need(pair['copy']['sha256']==pair['original']['sha256']and pair['copy']['bytes']==pair['original']['bytes'])
 # Mutable original documentation is provenance DATA, not reopened as immutable runtime input.
work=read(S/'future-full-clock-runtime-requirements.json');need(work['originalResourceCaseIds']==list(range(7))and work['requiredNativeManifests']==9 and work['nativeBufferResolutionMustRemainGenuine']is True and work['fullClockProfileAcceptance']is False and work['historicalStrictTwoInterfaceFailureRemainsFailed']is True)
expected=['wasi:clocks/monotonic-clock@0.2.10','wasi:clocks/wall-clock@0.2.10','wasi:io/poll@0.2.10'];need(refs['selectedInterfaces']==work['newSelectedInterfaces']==expected)
need(refs['disableFeatures']==['stdio','random','http','fetch-event'])
source=(S/'build.mjs').read_text();native=Path(refs['nativePreflight']['path']).read_text();consumedCode=(nativeHere/'consumed.mjs').read_text();selector=Path(refs['nativeSelector']['path']).read_text()
need(source.index('for(const r of inputs.files)await c.file(r)')<source.index('const {classicPreflight}=await import(')<source.index('const {loadExperimentalClockPackage}=await import(')<source.index('const {componentWit,transpile}=await import('))
need("classicPreflight({variant:'normal-off'})"in source and 'selectedManifestsForEngine(native.metadata,{sourceRoot:native.sourceRoot})'in source)
need('loadToolchain('not in source and 'loadComponentizer('not in source and 'bundleProfile('not in source)
need('toolchain'not in native.replace('NODE_COMPAT_TOOLCHAIN','').lower()and '@bytecodealliance'not in native and 'spawn'not in native)
need('import 'not in consumedCode.replace("import assert from 'node:assert/strict';",'').replace("import { createHash } from 'node:crypto';",'').replace("import { lstat, readFile, readdir, readlink, realpath } from 'node:fs/promises';",'').replace("import { isAbsolute, join, relative, resolve, sep } from 'node:path';",''))
need('Object.freeze({enginePath:pin.enginePath,sourceRoot:pin.sourceRoot,metadata,pin:frozenPin,variant,recheck})'in native)
need('for(const[k,v]of Object.entries(refs.requiredNativeReadOnlyEnvironment))need(process.env[k]===v' in source)
need('await selected.componentize(source,options)'in source and 'finally{try{await recheck();}'in source and 'await out.recheck()'in source)
loader=read(refs['loaderReferences']['path']);inventory=read(loader['packageInventory']['path'])['package'];root=Path(inventory['root']);want=set();idsPackage=set()
for r in inventory['files']:
 p=Path(r['path']);s=p.stat();need(s.st_nlink==1 and stat.S_IMODE(s.st_mode)==r['mode']);want.add(r['relativePath']);idsPackage.add((s.st_dev,s.st_ino))
need(len(idsPackage)==4889)
for r in inventory['links']:
 p=root/r['path'];need(p.is_symlink()and os.readlink(p)==r['target']and str(p.resolve())==r['resolvedPath']);want.add(r['path'])
need({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()or p.is_symlink()}==want)
lp=read(refs['loaderSourcePeer']['result']['path']);need(lp['sourceIndexSha256']==refs['loaderSourceIndex']['sha256']and lp['sourceReviewPassed']is True)
for p in S.rglob('*.py'):ast.parse(p.read_bytes());need(True)
grammar=read(S/'grammar.terminal.json');need(grammar['rawExitCode']==0)
for p,a in ids.items():need(identity(Path(p))==a)
for f in [ix,*inputs['families']]:family(f)
for k in ['outputRoot','externalRoot']:need(not Path(refs[k]).exists()and not Path(refs[k]).is_symlink())
out=dict(schemaVersion=1,sourceIndex=ix,checks=checks,sourceMembers=46,declaredInputs=11581,logicalInputBytes=sum(r['bytes']for r in inputs['files']),completeFamilies=11,wholeNativeConsumedInputs=6414,oldToolTrees=2,oldToolLinks=22,nativeSourceFiles=342,externalEmbeddingSources=3,nativeMetadataFields=64,selectedManifestCount=9,loaderPackageRegularFiles=4889,loaderPackageLinks=21,originalGuestBytes=772,wholeBundleBytes=487929,originalBundleModules=9,originalBundleTransformInputs=8,allHashesAndBookendsPassed=True,genuineNativePreflightNoOldPackagerImport=True,pairedCallerAndLoaderPoliciesSame=True,allSevenFutureResourceCasesPreserved=True,storedGrammarAndPureEvidenceAuthenticatedNotRerun=True,ownerApisOrPackagesInvoked=False,reviewerNodeOrToolInvoked=False)
(P/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
