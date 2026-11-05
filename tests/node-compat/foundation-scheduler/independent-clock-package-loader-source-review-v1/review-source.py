"""Independent read/hash/static Source review only. No custom imports."""
from pathlib import Path
import hashlib,json,os,stat
HERE=Path(__file__).resolve().parent;SOURCE=HERE.parent/'clock-package-loader-candidate-v1'
checks=0;seen={};identities={}
def check(v):
 global checks
 assert v;checks+=1
def read(p):return json.loads(Path(p).read_bytes())
def physical(p):return Path('/private'+p)if p.startswith('/tmp/')else Path(p)
def identity(p):
 s=p.lstat();check(stat.S_ISREG(s.st_mode));return(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode,s.st_nlink)
def row(p):
 p=physical(str(p));check(p.is_absolute()and '..'not in p.parts)
 for q in(p,*p.parents):check(not q.is_symlink())
 a=identity(p);h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 check(a==identity(p));r=dict(path=str(p),sha256=h.hexdigest(),bytes=a[2]);seen[str(p)]=r;identities[str(p)]=a;return r
def verify(r):check(row(r['path'])==dict(r,path=str(physical(r['path']))))
def family(ix):
 verify(ix);base=physical(ix['path']).parent;wanted={'index.json'}
 for m in read(ix['path'])['files']:
  n=m['path'];check(n not in wanted and n and not n.startswith('/')and '\\'not in n and all(x not in('','.','..')for x in n.split('/')));wanted.add(n);verify(dict(m,path=str(base/n)))
 actual=set()
 for p in base.rglob('*'):
  check(not p.is_symlink()and(p.is_dir()or p.is_file()))
  if p.is_file():actual.add(p.relative_to(base).as_posix())
 check(actual==wanted)
ix=row(SOURCE/'index.json');check(ix['sha256']=='21b9f3063de6995b555400b2afd6deb3fdf0a6191fb1a540a6673ddb59dc060c');family(ix)
refs=read(SOURCE/'references.json');inputs=read(SOURCE/'source-inputs.json')
check(len(inputs['files'])==5028 and len(inputs['families'])==6)
for r in inputs['files']:verify(r)
for f in inputs['families']:family(f)
for key in ['toolsBuildReview','failedAdapterPhaseReview','metadataReview']:
 pair=refs[key];check(pair['result']in[dict(m,path=str(Path(pair['index']['path']).parent/m['path']))for m in read(pair['index']['path'])['files']])
build=read(refs['toolsBuildReview']['result']['path']);failed=read(refs['failedAdapterPhaseReview']['result']['path']);metadata=read(refs['metadataReview']['result']['path'])
check(build['verifiedPassed']is failed['verifiedPassed']is metadata['verifiedPassed']is True)
check(build['actualPrivatePackageInventory']==refs['packageInventory']and build['artifacts']==refs['actualArtifacts']and len(build['artifacts'])==25)
check(failed['phasePassed']is False and failed['adapterAccepted']is False and failed['metadataDecoded']is False and failed['coreDataAuditPassed']is True)
check(metadata['metadataContinuationPassed']is True and metadata['previousPhaseRemainsFailed']is True and metadata['adapterPromoted']is False)
for k in ['normalizedAdapter','prunedAdapter','metadataPayload']:check(failed[k]==metadata[k]==refs[k])
inventory=read(refs['packageInventory']['path'])['package'];root=Path(inventory['root']);wanted=set();ids=set()
check(str(root)==refs['packageRoot']and len(inventory['files'])==4889 and len(inventory['links'])==21 and stat.S_IMODE(root.stat().st_mode)==0o700)
for r in inventory['files']:
 p=physical(r['path']);s=p.stat();check(str(p)==str(root/r['relativePath'])and seen[str(p)]['sha256']==r['sha256']and seen[str(p)]['bytes']==r['bytes']);check(s.st_nlink==1 and stat.S_IMODE(s.st_mode)==r['mode']);wanted.add(r['relativePath']);ids.add((s.st_dev,s.st_ino))
check(len(ids)==4889)
for r in inventory['links']:
 p=root/r['path'];check(p.is_symlink()and os.readlink(p)==r['target']and str(p.resolve())==r['resolvedPath']and str(p.resolve()).startswith(str(root)+'/'));wanted.add(r['path'])
check({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()or p.is_symlink()}==wanted)
check(not(root/'splicer-build.json').exists())
source=(SOURCE/'loader.mjs').read_text();loadstart=source.index('export async function loadExperimentalClockPackage');load=source[loadstart:source.index('\n\nasync function fingerprint',loadstart)]
check(load.index("assert(!handleIssued")<load.index('const c=new Capture()')<load.index('try{'))
check('handleIssued=true;'in load and 'finally{await c.recheck();}'in load)
check("root.nativeMetadata.path===root.nativeEngine.path+'.build.json'"in source and 'releaseMetadataModel(nativeMetadata,root.nativeEngine.sha256)'in source)
check('context.selectedInterfacePolicy(context.nativeMetadata' in source and 'context.auditSelectedInterfaces(context.toolchain,result.component,policy)'in source)
check('context.packageComponentize(call.source,call.publicOptions)'in source and 'finally{await context.recheck();}'in source)
entry=Path(refs['packageEntry']['path']).read_text();check('export async function componentize('in entry and 'export const { version } = JSON.parse('in entry)
check("opts = _deprecatedWitWorldOrOpts;"in entry and 'wasi_snapshot_preview1: await readFile(preview2Adapter)'in entry)
check('splicer-build.json'not in source and 'loadComponentizer('not in source and 'process.env.TMPDIR='not in source.replace('===','EQ'))
tests=(SOURCE/'test-pure.mjs').read_text();check('selected.componentize(source,options())'in tests and 'await loadExperimentalClockPackage('not in tests)
for path,a in identities.items():check(identity(Path(path))==a)
for f in [ix,*inputs['families']]:family(f)
out=dict(schemaVersion=1,sourceIndex=ix,sourceMembers=43,declaredInputs=5028,completeFamilies=6,logicalInputBytes=sum(r['bytes']for r in inputs['files']),checks=checks,packageRegularFiles=4889,packageAliases=21,actualArtifacts=25,allHashesIdentityModesLinksAndBookendsPassed=True,actualThreeProofCompositionVerifiedAsData=True,oldFailedPhasePreserved=True,onlyKnownBlocker='SECOND_LOAD_REJECTS_BEFORE_RETAINED_PROTECTION_RECHECK',authorStoredPureCasesAuthenticatedNotRerun=59,ownerApiOrPackageOrComponentizeInvoked=False,grammarCheckerInvokedByReviewer=False)
(HERE/'checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
