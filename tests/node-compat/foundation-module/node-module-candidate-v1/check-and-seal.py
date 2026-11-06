"""Own Source/DATA/host-only checks. Never invokes native compiler/provider."""
from pathlib import Path
import ast,hashlib,json,subprocess,time
OWN=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_bytes())
def d(p):
 p=Path(p);b=p.read_bytes();return dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))
def save(n,v):(OWN/n).write_text(json.dumps(v,indent=2)+'\n')
assert not(OWN/'index.json').exists()
refs=read(OWN/'references.json');inputs=read(OWN/'input-hashes.json')['files']
for r in inputs:assert d(r['path'])==r
for key in ['parentFrozenReviewIndex','parentFrozenReviewResult','parentFrozenReceipt','parentFrozenEngine','parentFrozenMetadata']:assert d(refs[key]['path'])==refs[key]
parent=read(refs['parentFrozenReviewResult']['path']);assert parent['verifiedPassed']is True and parent['nativeSourceFiles']==357 and parent['rawMetadataFields']==83
assert parent['frozenEngine']==refs['parentFrozenEngine']and parent['frozenMetadata']==refs['parentFrozenMetadata']
assert parent['originalRecipeExitCode']==0 and parent['originalParentExitCodes']==[1,1]and parent['originalBuildPreservationPassed']is False and parent['originalBuildAccepted']is False
deriv=read(OWN/'derivations.json');assert len(deriv['files'])==6 and len(deriv['newSourcePaths'])==6
for r in deriv['files']:
 assert d(r['before']['path'])==r['before']and d(r['after']['path'])==r['after']
 original=Path(r['before']['path']).read_text();text=original
 for e in r['edits']:assert text.count(e['before'])==e['count'];text=text.replace(e['before'],e['after'])
 assert text==Path(r['after']['path']).read_text()
 for e in reversed(r['edits']):assert text.count(e['after'])==e['count'];text=text.replace(e['after'],e['before'])
 assert text==original
for r in deriv['newSourcePaths']:assert d(r['origin']['path'])==r['origin']
manifest=read(OWN/'prospective-source-manifest.json');assert(manifest['nativeSourceFiles'],manifest['retainedNativeFiles'],manifest['changedNativeFiles'],manifest['newNativeFiles'])==(363,351,6,6)
assert manifest['files']==sorted(manifest['files'],key=lambda r:r['path'])and len({r['path']for r in manifest['files']})==363
cpp=(OWN/'module-kernel.cpp').read_text();checks=[]
condition='engine&&engine->state()==api::EngineState::Initialized&&entropy::deployed_execution_started()'
assert condition in cpp and 'entropy::status()'not in cpp;checks.append('actual guard requires EngineInitialized and real deployed entry, independent of entropy availability')
for name,label in [('kind','module.stat'),('read_text','module.readText'),('real_path','module.realpath'),('cwd','module.cwd')]:
 start=cpp.index('static bool '+name+'(');end=cpp.index('\n}',start);body=cpp[start:end]
 assert body.index('if(!require_io(cx,"'+label+'"))return false;')<min(body.find('path_arg(')if'path_arg('in body else len(body),body.find('getcwd(')if'getcwd('in body else len(body));checks.append(name+' guards before path encoding/libc')
for name in ['builtin','compile']:
 start=cpp.index('static bool '+name+'(');end=cpp.index('\n}',start);assert 'require_io('not in cpp[start:end];checks.append(name+' pure native operation does not initialize filesystem')
for present in [False,True]:
 for state in ['Uninitialized','EngineInitializing','ScriptPreInitializing','Initialized','Aborted']:
  for deployed in [False,True]:
   expression=condition.replace('engine->state()','state').replace('api::EngineState::Initialized',repr('Initialized')).replace('entropy::deployed_execution_started()','deployed').replace('engine','present').replace('&&',' and ')
   accepted=bool(eval(expression,{'__builtins__':{}},dict(present=present,state=state,deployed=deployed)))
   assert accepted==((present,state,deployed)in {(True,'Initialized',True)});checks.append(dict(enginePresent=present,state=state,deployed=deployed,ioAllowed=accepted,scope='Actual extracted Source Boolean condition against sole permitted lifecycle tuple; no C++ execution'))
assert 'std::unique_ptr<FILE,CloseFile>'in cpp and 'file.release()'in cpp and 'JS::RootedFunction fn' in cpp and 'JS::EnvironmentChain chain' in cpp
assert 'JS::SourceOwnership::Borrowed'in cpp and 'source.ptr.get()'in cpp;checks.append('native-owned buffers and rooted compiler function Source inspected')
for p in OWN.glob('*.py'):ast.parse(p.read_bytes())
node=Path('/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node');node_row=d(node);assert node_row['sha256']=='e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
source_names=['module-core.mjs','test-provider.mjs','test-host.mjs','test-factory.mjs','generate-module-factory.mjs','node-inventory.json','module-factory.generated.h','export-manifest.module.node-v22.14.0.json']
before=[d(OWN/n)for n in source_names]
commands=[]
def command(args,stem):
 argv=[str(node),*args];started=time.monotonic();p=subprocess.run(argv,capture_output=True,timeout=90)
 (OWN/(stem+'.stdout.log')).write_bytes(p.stdout);(OWN/(stem+'.stderr.log')).write_bytes(p.stderr)
 r=dict(argv=argv,rawExitCode=p.returncode,elapsedOperationalSeconds=time.monotonic()-started,stdout=d(OWN/(stem+'.stdout.log')),stderr=d(OWN/(stem+'.stderr.log')),hostOnly=True,nativeProviderOrCompilerOrGuestExecuted=False)
 commands.append(r);assert p.returncode==0 and p.stderr==b'',p.stderr.decode(errors='replace');return p.stdout
for name in sorted(p.name for p in OWN.glob('*.mjs')):assert command(['--check',str(OWN/name)],'grammar-'+name)==b''
assert command([str(OWN/'generate-module-factory.mjs'),'--check'],'generated-header-check')==b''
host=json.loads(command([str(OWN/'test-host.mjs')],'final-host-tests'));assert host['checks']==42 and host['nativeGuestProviderExecuted']is host['nextApplicationServerExecuted']is False
factory=json.loads(command([str(OWN/'test-factory.mjs')],'final-factory-tests'));assert factory['checks']==8 and factory['nativeProviderCalled']is False
assert before==[d(OWN/n)for n in source_names]
for r in inputs:assert d(r['path'])==r
assert d(node)==node_row
save('check-results.json',dict(schemaVersion=1,state='NODE_MODULE_SOURCE_AND_HOST_CHECKS_PASSED_V1',nativeSourceChecks=checks,hostChecks=host['checks'],generatedFactoryChecks=factory['checks'],commands=commands,hostSourceBefore=before,hostSourceAfter=[d(OWN/n)for n in source_names],actualNextHook=host['actualNextHook'],actualWebpackRuntime=host['actualWebpackRuntime'],nativeCppParsed=False,nativeProviderExecuted=False))
save('author-history.json',dict(schemaVersion=1,sourceOnly=True,retainedHostFailures=['authoring-attempt1','authoring-attempt2','authoring-attempt3','authoring-attempt4'],retainedPreparationFailure='preparation-failures',notes=['Node oracle showed BOM before shebang must remain SyntaxError; core corrected.','createRequire trailing-directory source bug corrected to logical noop.js parent.','Extensionless .cjs and invalid-argument-after-Next-hook expectations were test assumptions, not native failures.','Deployed-only IO guard added after libc preopen-cache risk was identified; shared accessor exact with FS lane.'],nativeOrGuestInvoked=False))
save('results.json',dict(schemaVersion=1,state='NODE_MODULE_COMMONJS_GUEST_SOURCE_READY_FOR_INDEPENDENT_REVIEW_V1',sourceOnly=True,sourceChecksPassed=True,hostDifferentialChecksPassed=True,hostChecks=42,generatedFactoryChecks=8,nativeSourceFiles=363,retainedNativeFiles=351,changedNativeFiles=6,newNativeFiles=6,externalEmbeddingSources=3,externalEmbeddingChanges=0,defaultEnabled=False,featureFlag='NODE_COMPAT_MODULE',profileManifest='sm-node-22.14.0-m0.17',parentFrozenReviewIndex=refs['parentFrozenReviewIndex'],parentFrozenReceipt=refs['parentFrozenReceipt'],parentEngine=refs['parentFrozenEngine'],parentMetadata=refs['parentFrozenMetadata'],parentOriginalBuildAccepted=False,privateNativeLookup='ScriptLoader::lookup_registered_builtin',nativeIOPhaseGuard='EngineInitialized AND actual entropy TU deployed-entry bit before path encoding/libc',sharedDeployedAccessor='entropy::deployed_execution_started',cacheStorage='Ordinary traced JS objects/closures; no native persistent JS pointers',hostAdapterPackaged=False,actualNextHookHostTestPassed=True,actualGeneratedWebpackHostTestPassed=True,ownerNativeActionsInvoked=False,compilerActionsInvoked=False,guestActionsInvoked=False,nextServerExecuted=False,sourcePeer=None,rootAuthority=None,actualNativeIntegration=None,actualNativeBuild=None,actualComponent=None,actualRuntime=None,actualMetadataSchema=None,operationalAdmission=False,fullNextAcceptance=False,qualifications=['Native C++ has not passed frontend/link/guest validation; host compiler adapter is test-only.','No live production/staged/frozen source was edited.','Initial native IO gate blocks Wizer/pre-deployment and aborted engines; re-snapshotting deployed instances is not admitted.','General FS native provider may replace private libc IO through its actual future reviewed API; no invented reader symbol is depended on here.','Complete npm/Node ESM, addon, callback loader APIs, filesystem error parity, AsyncLocalStorage/process and HTTP remain separate requirements.']))
save('source-receipt.json',dict(schemaVersion=1,state='NODE_MODULE_COMMONJS_SOURCE_SEALED_UNCOMPILED_V1',result=d(OWN/'results.json'),checks=d(OWN/'check-results.json'),derivations=d(OWN/'derivations.json'),sourceContract=d(OWN/'future-source-review-contract.json'),allFutureAuthoritiesUnissued=True,nativeActionsInvoked=False))
rows=[]
for p in sorted(OWN.rglob('*')):
 assert not p.is_symlink()
 if p.is_file():rows.append(dict(d(p),path=p.relative_to(OWN).as_posix()))
save('index.json',dict(schemaVersion=1,state='SEALED_UNCOMPILED_NODE_MODULE_COMMONJS_SOURCE_V1',files=rows))
for n in ['index.json','results.json','source-receipt.json','future-source-review-contract.json']:print(json.dumps(d(OWN/n)))
