"""Compact Source/host check; no native compiler/provider or guest execution."""
from pathlib import Path
import ast,hashlib,json,subprocess,time
OWN=Path(__file__).resolve().parent;OUT=OWN/'native/builtins/node-compat'
def d(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def read(p):return json.loads(Path(p).read_bytes())
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists()
inputs=read(OWN/'inputs.json');rows=inputs['productionFiles']+inputs['apiHeaders']+[inputs['nodeSource']]
for r in rows:assert d(r['path'])==r
deriv=read(OWN/'derivations.json')
for r in deriv['files']:
 assert d(r['before']['path'])==r['before']and d(r['after']['path'])==r['after'];original=Path(r['before']['path']).read_text();s=original
 for e in r['edits']:assert s.count(e['before'])==1;s=s.replace(e['before'],e['after'])
 assert s==Path(r['after']['path']).read_text()
 for e in reversed(r['edits']):assert s.count(e['after'])==1;s=s.replace(e['after'],e['before'])
 assert s==original
before=read(deriv['manifestBefore']['path']);after=read(deriv['manifestAfter']['path'])
assert before['modules']['node:child_process']==after['modules']['node:child_process']
assert before['modules']['node:buffer']['exports']==after['modules']['node:buffer']['exports']
assert 'concat'in before['modules']['node:buffer']['unsupportedStatic']and'concat'not in after['modules']['node:buffer']['unsupportedStatic']
cpp=(OUT/'buffer.cpp').read_text();start=cpp.index('static bool concat_bytes(');end=cpp.index('\nJSObject *create_kernel',start);kernel=cpp[start:end]
assert 'JS::RootedObjectVector sources(cx)'in kernel and 'JS::RootedObject output' in kernel
assert kernel.index('if(!sources.append(view))')<kernel.index('JS_NewUint8Array')<kernel.index('JS::AutoCheckCannotGC')<kernel.index('std::memcpy')
assert kernel.count('JS_GetArrayBufferViewBuffer')==2
borrow=kernel[kernel.index('JS::AutoCheckCannotGC'):];assert 'JS_GetElement'not in borrow and 'JS_New'not in borrow and 'stress_gc('not in kernel
assert 'std::min(bytes,length-position)'in borrow and 'if(length)std::memset'in borrow and 'if(take)'in borrow
node=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node');node_row=d(node);assert node_row['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
commands=[]
def run(args,stem):
 argv=[str(node),*args];start=time.monotonic();p=subprocess.run(argv,capture_output=True,timeout=90)
 (OWN/(stem+'.stdout.log')).write_bytes(p.stdout);(OWN/(stem+'.stderr.log')).write_bytes(p.stderr)
 commands.append(dict(argv=argv,rawExitCode=p.returncode,stdout=d(OWN/(stem+'.stdout.log')),stderr=d(OWN/(stem+'.stderr.log')),elapsedOperationalSeconds=time.monotonic()-start,hostSourceOnly=True,nativeKernelOrGuestExecuted=False))
 assert p.returncode==0 and p.stderr==b'',p.stderr.decode(errors='replace');return p.stdout
source_before=[d(p)for p in sorted(OUT.glob('*'))if p.is_file()]+[d(OWN/'test-host.mjs')]
for p in [OUT/'buffer-facade.mjs',OUT/'generate-factories.mjs',OWN/'test-host.mjs']:assert run(['--check',str(p)],'grammar-'+p.name)==b''
run([str(OUT/'generate-factories.mjs'),'--core-only','--check'],'generator-check')
host=json.loads(run([str(OWN/'test-host.mjs')],'final-host-tests'));assert host['checks']==50 and host['nativeKernelExecuted']is host['nativeCppCompiled']is host['guestExecuted']is False
assert source_before==[d(p)for p in sorted(OUT.glob('*'))if p.is_file()]+[d(OWN/'test-host.mjs')]
for r in rows:assert d(r['path'])==r
assert d(node)==node_row
for p in OWN.glob('*.py'):ast.parse(p.read_bytes())
save('checks.json',dict(schemaVersion=1,commands=commands,hostChecks=50,nodeDifferentialCases=sum('node'in r for r in host['cases']),profileCases=sum('node'not in r for r in host['cases']),actualSourceBefore=source_before,actualSourceAfter=[d(p)for p in sorted(OUT.glob('*'))if p.is_file()]+[d(OWN/'test-host.mjs')],nativeSourceOrderRootingAndBorrowChecksPassed=True,nativeFrontendOrCppExecuted=False))
save('results.json',dict(schemaVersion=1,state='BUFFER_CONCAT_SOURCE_READY_FOR_INDEPENDENT_REVIEW_V1',sourceOnly=True,sourceChecksPassed=True,hostDifferentialChecksPassed=True,hostChecks=50,nodeDifferentialCases=sum('node'in r for r in host['cases']),existingNativeFilesChanged=5,newNativeSourcePaths=0,publicExportNamesChanged=False,newCMakeFlag=None,newHostImportsDeclared=False,profileManifest='sm-node-22.14.0-m0.18',outputLimitBytes=16777216,visibleInputLimitBytes=16777216,chunkCountLimit=65536,propertySlotPreserved=True,nativeMemcpyKernelSource=True,nativeRootingAndFixedBackingSourceChecksPassed=True,allOtherBufferAndChildProcessScopesPreserved=True,sourcePeer=None,rootAuthority=None,actualNativeBuild=None,actualGuest=None,productionSourceEdited=False,nativeCompilerInvoked=False,nativeKernelExecuted=False,guestExecuted=False,operationalAdmission=False))
save('source-receipt.json',dict(schemaVersion=1,result=d(OWN/'results.json'),checks=d(OWN/'checks.json'),derivations=d(OWN/'derivations.json'),generatedHeader=d(OUT/'factories.generated.h'),generatedHeaderBefore=next(r for r in inputs['productionFiles']if r['path'].endswith('/factories.generated.h')),generatedHeaderGenuine=True,allFutureAuthoritiesNull=True,nativeOrGuestActionsInvoked=False))
files=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():files.append(dict(d(p),path=p.relative_to(OWN).as_posix()))
save('index.json',dict(schemaVersion=1,state='SEALED_UNCOMPILED_BUFFER_CONCAT_SOURCE_V1',files=files))
for n in ['index.json','results.json','source-receipt.json']:print(json.dumps(d(OWN/n)))
