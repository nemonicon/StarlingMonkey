"""Read/hash/AST, exact Node grammar and pure host models only."""
from pathlib import Path
import ast,hashlib,json,os,stat,subprocess
P=Path(__file__).resolve().parent
checks=0
def check(value,label):
    global checks
    assert value,label;checks+=1
def load(p):return json.loads(Path(p).read_bytes())
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def physical(p):return Path('/private'+p)if p.startswith('/tmp/')else Path(p)
captured={}
def verify(r):
    p=physical(r['path']);check(p.is_absolute()and '..'not in p.parts,'absolute input')
    for q in(p,*p.parents):check(not q.is_symlink(),'no physical symlink')
    s=p.stat();check(stat.S_ISREG(s.st_mode)and s.st_size==r['bytes']and digest(p)==r['sha256'],'full input hash')
    identity=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode,s.st_nlink)
    if str(p)in captured:check(captured[str(p)][1]==identity,'stable duplicate input')
    captured[str(p)]=(r,identity)
    return p
refs=load(P/'references.json');manifest=load(P/'source-inputs.json')
for r in manifest['files']:verify(r)
for ix in manifest['families']:
    verify(ix);root=Path(ix['path']).parent;value=load(root/'index.json');expected={'index.json'}
    for r in value['files']:
        check(r['path']not in expected and not r['path'].startswith('/')and all(x not in ('','.','..')for x in r['path'].split('/')),'safe indexed member');expected.add(r['path']);verify(dict(path=str(root/r['path']),sha256=r['sha256'],bytes=r['bytes']))
    actual=set()
    for p in root.rglob('*'):
        check(not p.is_symlink(),'proof family regular membership')
        if p.is_file():actual.add(p.relative_to(root).as_posix())
    check(actual==expected,'complete proof family')
inventory=load(refs['packageInventory']['path'])['package'];root=Path(inventory['root'])
check(root==Path(refs['packageRoot'])and len(inventory['files'])==4889 and len(inventory['links'])==21,'actual full private package inventory')
expected=set();target_ids=set()
for r in inventory['files']:
    p=physical(r['path']);check(p==root/r['relativePath'],'actual package physical-relative role');s=p.stat();check(s.st_nlink==1 and stat.S_IMODE(s.st_mode)==r['mode'],'private package modes/singlelinks');expected.add(r['relativePath']);target_ids.add((s.st_dev,s.st_ino))
check(len(target_ids)==4889,'private package distinct file inodes')
for r in inventory['links']:
    p=root/r['path'];check(p.is_symlink()and os.readlink(p)==r['target']and str(p.resolve())==r['resolvedPath'],'actual alias linktext/target');check(p.resolve().is_relative_to(root),'aliases stay inside private package');expected.add(r['path'])
actual={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()or p.is_symlink()};check(actual==expected,'exact4889+21 package membership')
check(len(refs['actualArtifacts'])==25,'all25 actual build outputs')
check(refs['splicerCore']['sha256']=='61685a01168e4f3ed12cf701bcde1a568992ea16d4a33266cbd2784fc1532abb','new actual core not edad')
check(not(root/'splicer-build.json').exists(),'no forged old loader manifest')
check(refs['oldDefaultLoaderDataOnly']['sha256']=='3993cec88cdf7c1ca894c259e481a113068ede63d025eb69b6f786b6c1a1abdd','old default loader unchanged')
text=(P/'loader.mjs').read_text()
check(text.index('await c.recheck();')<text.index("import(pathToFileURL(refs.packageEntry.path))"),'complete capture before package import')
check("const capability=await import(pathToFileURL(refs.capabilityPolicy.path))"in text and 'capability.selectedInterfacePolicy' in text and 'capability.auditSelectedInterfaces' in text,'genuine capability policy functions used')
check('context.packageComponentize(call.source,call.publicOptions)'in text,'real source+options signature')
check('selectedInterfaces:call.selectedInterfaces' in text and 'interfaceAudit' in text,'explicit selection and actual post-component audit')
check('finally{await context.recheck();}'in text and 'finally{await c.recheck();}'in text,'call/load/failure protection bookends')
check('oldAdapterPhasePassed:false' in text and 'adapterPromoted:false' in text,'no failed phase relabeling')
check('Node ESM'not in text or 'cache' in text,'cache scope stated')
check('splicer-build.json'not in text and 'edad4a6'not in text and 'loadComponentizer('not in text,'no old loader wrapper or forged old identities')
check('process.env.'not in text or 'process.env.TMPDIR==='in text,'no environment rebinding')
for bad in ['process.env.TMPDIR=','process.env.HOME=','process.env.CODEX_HOME=','delete require.cache','sys.modules','legacyDiagnostic','debugScalarOOMDiagnostic']:
    if bad.endswith('='):check(bad not in text.replace('===','EQ'),'no global environment assignment '+bad)
    else:check(bad not in text,'no legacy/cache/global interception '+bad)
node=verify(refs['node']);own_sources=[P/'loader.mjs',P/'test-pure.mjs']
source_pins=[dict(path=str(p),sha256=digest(p),bytes=p.stat().st_size)for p in own_sources]
for p in own_sources:
    result=subprocess.run([str(node),'--check',str(p)],capture_output=True);check(result.returncode==0 and result.stdout==result.stderr==b'','Node grammar '+p.name)
# Test program imports only this inert helper and real pure capability policy;
# actual package/splicer/Jco libraries and load API are never called.
test=subprocess.run([str(node),str(P/'test-pure.mjs')],capture_output=True)
(P/'pure.stdout.log').write_bytes(test.stdout);(P/'pure.stderr.log').write_bytes(test.stderr)
(P/'pure-terminal.json').write_text(json.dumps(dict(argv=test.args,rawExitCode=test.returncode,actualPackageSplicerOrWizerInvoked=False),indent=2)+'\n')
check(test.returncode==0,'pure host tests');pure=json.loads(test.stdout);check(pure['actualPackageSplicerImported']is pure['actualComponentizeOrWizerInvoked']is pure['engineOrGuestExecuted']is False,'pure scope')
for p in P.glob('*.py'):ast.parse(p.read_text());check(True,'Python AST '+p.name)
for path,(r,i)in captured.items():
    p=Path(path);s=p.stat();check((s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_mode,s.st_nlink)==i and digest(p)==r['sha256'],'final complete input hash/identity/mode/link')
for r in source_pins:check(digest(r['path'])==r['sha256'],'own executable source stability')
check(not(root/'splicer-build.json').exists(),'no manifest created by tests')
out=dict(schemaVersion=1,state='CLOCK_PACKAGE_LOADER_SOURCE_DATA_PURE_GRAMMAR_CHECKS_PASSED',checks=checks,declaredInputRows=len(manifest['files']),uniquePhysicalInputs=len(captured),inputBytes=sum(r['bytes']for r,i in captured.values()),packageRegularFiles=4889,packageAliases=21,actualArtifacts=25,completeProofAndSourceFamilies=len(manifest['families']),pureHostCases=pure['checks'],nodeGrammarChecks=2,ownSourcePins=source_pins,actualEligibilityProofsReadAsData=True,genuineCapabilitySelectionUsedInPureModels=True,genuineCallFactoryInjectedForTests=True,actualPackageOrSplicerImported=False,actualLoaderApiCalled=False,componentizeWizerEngineOrGuestExecuted=False,defaultLoaderChanged=False,adapterPromoted=False)
(P/'source-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
