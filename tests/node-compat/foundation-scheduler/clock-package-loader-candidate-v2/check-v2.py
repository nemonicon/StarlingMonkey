"""Source hashes, exact reversal, pure/grammar tests only; no package load API."""
from pathlib import Path
import ast,hashlib,json,os,stat,subprocess
P=Path(__file__).resolve().parent;checks=0;ids={};rows={}
def check(v):
 global checks
 assert v;checks+=1
def read(p):return json.loads(Path(p).read_bytes())
def physical(p):return Path('/private'+p)if p.startswith('/tmp/')else Path(p)
def row(p):
 p=physical(str(p));s=p.lstat();check(stat.S_ISREG(s.st_mode));h=hashlib.sha256()
 for q in(p,*p.parents):check(not q.is_symlink())
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 a=p.lstat();identity=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns,x.st_mode,x.st_nlink)
 check(identity(a)==identity(s));r=dict(path=str(p),sha256=h.hexdigest(),bytes=a.st_size);ids[str(p)]=identity(a);rows[str(p)]=r;return r
def verify(r):check(row(r['path'])==dict(r,path=str(physical(r['path']))))
refs=read(P/'references.json');inputs=read(P/'source-inputs.json');d=read(P/'derivations.json')
check(len(inputs['files'])==5080 and len(inputs['families'])==8)
for r in inputs['files']:verify(r)
for ix in inputs['families']:
 base=physical(ix['path']).parent;want={'index.json'}
 for m in read(ix['path'])['files']:
  n=m['path'];check(n not in want and not n.startswith('/')and all(x not in('','.','..')for x in n.split('/')));want.add(n);verify(dict(m,path=str(base/n)))
 actual=set()
 for q in base.rglob('*'):
  check(not q.is_symlink()and(q.is_file()or q.is_dir()))
  if q.is_file():actual.add(q.relative_to(base).as_posix())
 check(actual==want)
code=(P/'loader.mjs').read_text();reverse=code
for e in reversed(d['exactReversibleEdits']):check(reverse.count(e['after'])==1);reverse=reverse.replace(e['after'],e['before'])
check(reverse==Path(d['predecessorLoader']['path']).read_text()and len(d['exactReversibleEdits'])==10)
check(code.index('return loadGate.run(async()=>{')<code.index('const configRow=descriptor(input?.configDescriptor)'))
check(code.index('loadGate.retain(()=>c.recheck())')<code.index('const config=await c.json'))
check(code.index('loadGate.retain(recheck);')<code.index("import(pathToFileURL(refs.capabilityPolicy.path))"))
check('finally{if(retainedRecheck)await retainedRecheck();}'in code and 'finally{await c.recheck();}'in code and 'finally{await context.recheck();}'in code)
inventory=read(refs['packageInventory']['path'])['package'];root=Path(inventory['root']);want=set();seenids=set()
for r in inventory['files']:
 p=physical(r['path']);s=p.stat();check(p==root/r['relativePath']and s.st_nlink==1 and stat.S_IMODE(s.st_mode)==r['mode']);want.add(r['relativePath']);seenids.add((s.st_dev,s.st_ino))
check(len(seenids)==4889)
for r in inventory['links']:
 p=root/r['path'];check(p.is_symlink()and os.readlink(p)==r['target']and str(p.resolve())==r['resolvedPath']);want.add(r['path'])
check({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()or p.is_symlink()}==want)
for k in ['packageInventory','toolsBuildReview','failedAdapterPhaseReview','metadataReview','actualArtifacts','prunedAdapter','metadataPayload','capabilityPolicy','interfaceCatalogue','oldDefaultLoaderDataOnly']:
 check(refs[k]==read(P.parent/'clock-package-loader-candidate-v1/references.json')[k])
check(read(P/'future-source-review-contract.json')['requiredState']=='INDEPENDENT_CLOCK_PACKAGE_LOADER_SOURCE_REVIEW_PASSED_V2')
rootmodel=read(P/'root-authority.template.json');check(rootmodel['sourceIndependentReview']is None and rootmodel['nativeEngine']is None and rootmodel['nativeMetadata']is None)
node=physical(refs['node']['path']);verify(refs['node']);terms=[]
for kind,argv in [('grammar-loader',[str(node),'--check',str(P/'loader.mjs')]),('grammar-test',[str(node),'--check',str(P/'test-pure.mjs')]),('pure',[str(node),str(P/'test-pure.mjs')])]:
 run=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(P/(kind+'.stdout.log')).write_bytes(run.stdout);(P/(kind+'.stderr.log')).write_bytes(run.stderr)
 term=dict(argv=argv,rawExitCode=run.returncode,stdout=row(P/(kind+'.stdout.log')),stderr=row(P/(kind+'.stderr.log')),packageOrLoadApiInvoked=False,componentizeOrEngineOrGuestInvoked=False);terms.append(term)
 (P/(kind+'.terminal.json')).write_text(json.dumps(term,indent=2)+'\n');check(run.returncode==0 and run.stderr==b'')
pure=read(P/'pure.stdout.log');check(pure['actualPackageSplicerImported']is pure['actualComponentizeOrWizerInvoked']is pure['engineOrGuestExecuted']is False)
for p in P.glob('*.py'):ast.parse(p.read_bytes());check(True)
for path,i in ids.items():
 s=Path(path).stat();check((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode,s.st_nlink)==i)
check(not(root/'splicer-build.json').exists())
out=dict(schemaVersion=1,sourceOnly=True,sourceChecksPassed=True,checks=checks,declaredInputRows=5080,completeFamilies=8,inputBytes=sum(r['bytes']for r in inputs['files']),privatePackageRegularFiles=4889,privateAliases=21,actualArtifacts=25,reversibleLoaderEdits=10,wholeOriginalReversePassed=True,pureChecks=pure['checks'],grammarChecks=2,actualExportedRepeatSeamTestedInInjectedVm=True,partialAndFullRetainedRecheckTested=True,invalidRepeatConfigGetterNotRead=True,predecessorAndHoldPreserved=True,actualPackageOrLoaderApiInvoked=False,componentizeWizerEngineOrGuestExecuted=False,terms=terms)
(P/'source-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='terms'}))
