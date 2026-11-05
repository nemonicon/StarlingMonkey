"""Independent completed normal342 build DATA review. No owner import/tool action."""
from pathlib import Path
import ast,hashlib,json,os,re,shlex,stat,struct,tarfile
import review_io as I
HERE=Path(__file__).resolve().parent;S=HERE.parent;P=S/'resource-integration-candidate-v1';C=S/'resource-build-controller-candidate-v1'
SOURCE=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-source');WORK=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-build');BUILDOUT=Path('/private/tmp/starling-node-compat/scheduler-resource-v1-normal-off-build-root')
SOURCE_SHA='20e6bab4c34da81c6657341f4ae917e78614e9503d689d4b046fb14b980fc414';CONTROLLER_SHA='f75104547d0c39fd815101906a9f5f8065b5f486e522fd9fab2370cf01c72bd8'
def row(p):return I.descriptor(str(p))
def load(p):return I.read(row(p))
def verify_sha(p,sha):d=row(p);I.need(d['sha256']==sha,'actual fixed digest '+str(p));I.verify(d);return d
def eq(a,b,label):I.need(json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True),label)
def write(name,v):
    with(HERE/name).open('xb')as f:f.write((json.dumps(v,indent=2)+'\n').encode());f.flush();os.fsync(f.fileno())
def stream_member(tar,member):
    h=hashlib.sha256();f=tar.extractfile(member);n=0
    for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b);n+=len(b)
    I.need(n==member.size,'whole archive member bytes');return h.hexdigest(),n
root_row=dict(path=str(S/'resource-normal-off-build-v1-root-results.json'),sha256='a629c7239c3c17e9503f13e1e0d9aa9e1a5757714308a99cd7256a333eb48a87',bytes=3843)
r=I.read(root_row);I.verify_descriptors(r,'whole actual completed build Root observation');I.need(r['state']=='ROOT_OBSERVED_SCHEDULER_RESOURCE342_NORMAL_OFF_NATIVE_BUILD_PASSED_V1'and r['rootToolSession']==12069 and r['rootObservedToolRawExitCode']==0,'actual Root completed build tuple')
a=I.read(r['rootAuthority']);cfg=I.read(r['rootConfig']);built=I.read(r['actualBuildResult']);outer=I.read(r['externalParentTerminal']);m=I.read(r['metadata']);source_index=row(P/'index.json');controller_index=row(C/'index.json');I.need(source_index['sha256']==SOURCE_SHA==r['resourceSourceIndexSha256']and controller_index['sha256']==CONTROLLER_SHA==r['controllerSourceIndexSha256'],'exact actual342 source and new controller identities')
for d in [source_index,controller_index,a['sourceIndependentReview']['index'],a['controllerIndependentReview']['index'],a['independentStageReview']['index']]:I.indexed(d,'complete actual source/controller/source-peer/stage-proof family')
I.verify_descriptors(a,'whole actual build-only Root authority');eq(cfg,dict(schemaVersion=1,sourceIndex=source_index,controllerIndex=controller_index,rootAuthority=r['rootAuthority']),'whole actual build config')
I.need(a['state']=='ROOT_REVIEWED_SCHEDULER_RESOURCE342_NORMAL_OFF_BUILD_V1'and a['phase']=='build'and a['variant']=='normal-off'and a['buildAllowed']is True and a['nativeSourceFiles']==342 and a['externalEmbeddingSources']==3 and a['webTimersEnabled']is True and a['gcStress']is False,'actual normal-off342 build-only authority')
for k in ['stageAllowed','gcReconfigureAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','componentAllowed','guestAllowed','engineExecutionAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed']:I.need(a[k]is False,'non-build action remains closed '+k)
for k in ['actualBuildResult','engine','metadata','actualNormalFreeze','independentNormalFreezeReview','runtimeAction']:I.need(a[k]is None,'Root pre-action outcomes not projected '+k)
for pair,state,field,sha in [(a['sourceIndependentReview'],'INDEPENDENT_SCHEDULER_RESOURCE_INTEGRATION_SOURCE_REVIEW_PASSED_V1','sourceIndexSha256',SOURCE_SHA),(a['controllerIndependentReview'],'INDEPENDENT_SCHEDULER_RESOURCE342_BUILD_CONTROLLER_SOURCE_REVIEW_PASSED_V1','controllerSourceIndexSha256',CONTROLLER_SHA)]:
    v=I.read(pair['result']);I.need(v['state']==state and v[field]==sha and v['sourceOnly']is True and v['sourceReviewPassed']is True and v['ownerActionsInvoked']is False,'actual distinct source peer state/identity')
refs=load(C/'references.json')
for f in refs['families']:I.indexed(f['index'],'original monitor donor/reference SOURCE only family')
I.verify_descriptors(refs,'complete original source/stage/proof reference descriptors')
for root in [P,C]:
    for d in load(root/'input-freeze.json')['files']:I.verify(d,'complete finite source/controller preparation references')
stage_pair=a['independentStageReview'];stage_result=I.read(stage_pair['result']);stage=I.read(a['actualStageResult']);I.need(stage_result['state']=='INDEPENDENT_SCHEDULER_RESOURCE342_SOURCE_STAGE_REVIEW_PASSED_V1'and stage_result['verifiedPassed']is True and stage_result['actualStageResult']==a['actualStageResult']and stage_result['rootObservation']==a['actualStageRootObservation'],'genuine exact completed501-stage proof, no old receipt projection')
for d in load(Path(stage_pair['index']['path']).parent/'rehashed-inputs.json')['files']:I.verify(d,'all stage/source/original/proof protection rows unchanged')
for pair in [a['sourceIndependentReview'],a['controllerIndependentReview']]:
    for d in load(Path(pair['index']['path']).parent/'rehashed-inputs.json')['files']:I.verify(d,'all independent source-review original inputs unchanged')
I.need(len(stage['copies'])==501 and stage['nativeFiles']==342 and stage['destination']==str(SOURCE),'actual staged source context')
for d in stage['copies']:
    source=I.verify(d['original'],'actual original staged provenance');p=I.verify(dict(d['original'],path=d['path']),'all501 actual staged copies');s=p.stat();o=source.stat();I.need((s.st_dev,s.st_ino)!=(o.st_dev,o.st_ino)and stat.S_IMODE(s.st_mode)==stat.S_IMODE(o.st_mode),'staged copy remains distinct/mode preserved')
# Both durable ownership layers, complete raw streams, all714 process observations.
I.need(built['state']=='native-build-completed-runtime-pending'and built['rawChildExitCode']==built['status']==built['launcherExitCode']==0 and built['evidenceComplete']is True and built['lifecycleComplete']is True,'actual inner native build lifecycle completed raw0')
for key,value in dict(pid=96368,rawExitCode=0,timeout=False,forcedCleanup=False,parentOwnedGroupGone=True,allObservedOwnedGroupsGone=True).items():eq(outer[key],value,'actual outer clean '+key)
for key in ['interruptedSignals','remainingObservedPids','signals','errors']:eq(outer[key],[],'actual outer no error/residual '+key)
eq(outer['authority'],r['rootAuthority'],'actual outer Root authority');I.verify_descriptors(outer,'actual outer raw stdout/stderr')
ex=Path(r['externalParentTerminal']['path']).parent;events=[]
for p in sorted(ex.iterdir()):
    I.verify(row(p),'whole retained external ownership/process evidence')
    if p.name.startswith('owned-'):e=load(p);I.need(e['sequence']==len(events),'ordered actual714 identities');events.append(e['process'])
eq(events,outer['observedProcesses'],'all actual process identity objects retained');I.need(len(events)==714 and events[0]['pid']==96368 and any(z['pid']==96374 and z['ppid']==96368 for z in events),'actual Python parent and Bash build owner tree')
I.need(all(z['alive']is False and z['signalAllowed']is False for z in outer['finalGroups'])and {96368,96374}<={z['pgid']for z in outer['finalGroups']},'all recorded owned groups gone without signaling')
I.exact_tree(ex,['started.json','terminal.json','stdout.log','stderr.log',*[f'owned-{n:04d}.json'for n in range(714)]]);I.exact_tree(BUILDOUT,['launch.json','build.log','result.json'])
started=load(ex/'started.json');I.need(started['pid']==96368 and started['timeoutSeconds']==7200 and started['argv'][1:4]==['-B','-I',str(C/'build.py')],'actual bounded isolated parent argv');eq(I.decode(started['argv'][4].encode()),r['rootConfig'],'actual config command argument');eq(started['authority'],r['rootAuthority'],'actual launch Root descriptor')
eq(I.read(outer['stdout']),dict(output=str(BUILDOUT),result=built),'whole actual stdout envelope .result equals disk result');I.need(outer['stderr']['bytes']==0,'actual empty external stderr')
cleanup=built['ownedGroupCleanup'];I.need(cleanup['pgid']==96374 and cleanup['complete']is True and cleanup['rawChildExitCode']==0 and cleanup['events']==cleanup['errors']==built['launcherErrors']==[]and built['sigtermReceived']==0 and built['temporarySigtermHandlerRestored']is True and built['stopReason']is None and built['stoppedForDiskSpace']is False,'real inner owner cleanup no forced kill/signal')
I.need(built['allSourceStageAndProofBytesPreserved']is True and built['parallelBuilds']==1 and built['requiredStartFreeBytes']==2147483648 and built['stopBelowFreeBytes']==838860800 and built['freeBytesBefore']>=2147483648 and built['freeBytesAfter']>=838860800,'actual disk/source/serial operational record')
env={**load(P/'build-plan.json')['explicitEnvironment'],**refs['normalEnvironmentExtra']};eq(built['explicitEnvironment'],env,'whole explicit profile environment');I.need(env['NODE_COMPAT_GC_STRESS']=='0'and env['NODE_COMPAT_ENTROPY_MODE']=='OFF'and env['NODE_COMPAT_BUILD_ROOT']==str(WORK)and env['NODE_COMPAT_OOM_TESTING']=='0'and all(env[x]=='1'for x in ['NODE_COMPAT_JOBS','BINARYEN_CORES','RAYON_NUM_THREADS','CARGO_BUILD_JOBS']),'no GC/OOM, actual single-job Release environment')
launch=load(BUILDOUT/'launch.json');I.need(launch['state']=='RESOURCE342_NORMAL_OFF_NATIVE_BUILD_STARTED'and launch['rawChildExitCode']is None,'historical launch not relabelled');eq(launch['explicitEnvironment'],env,'actual launch exact environment');eq(built['command'],['bash',str(SOURCE/'tests/node-compat/build-engine.sh')],'real staged build recipe')
eq(built['rootAuthority'],r['rootAuthority'],'actual inner Root binding');I.need(built['resourceSourceIndexSha256']==SOURCE_SHA and built['configuredSourceRoot']==str(SOURCE)and built['workRoot']==str(WORK),'actual inner source/work context')
log=I.verify(r['buildLog']).read_text();I.need(r['buildLog']['sha256']==built['logSha256']and '[107/107]'in log and '[106/107] Linking CXX executable starling-raw.wasm/starling-raw.wasm'in log,'full retained107-step successful Ninja build log')
steps=[int(n)for n in re.findall(r'^\[(\d+)/107\]',log,re.M)];I.need(steps==[*range(1,32),31,*range(33,108)]and 'Finished `release` profile'in log,'exact actual107 progress lines: Cargo console command starts at currentfinished31;32 is not separately rendered')
# Complete actual source342 and external embedding3, current cache/DB, generated timer path.
policy=load(P/'policy.json');pins=load(P/'baseline-pins.json');eq(m['sourceManifest'],policy['expectedNativeSourceManifest'],'whole actual342 native manifest equals reviewed sourcepolicy')
I.need(len(m['sourceManifest'])==342 and m['auditedBaseRevision']==m['starlingMonkeyRevision']==stage['baseline']and m['enginePath']==r['engine']['path']and m['engineSha256']==r['engine']['sha256']and m['engineBytes']==r['engine']['bytes'],'actual source baseline/native engine identity')
for d in m['sourceManifest']:verify_sha(SOURCE/d['path'],d['sha256'])
I.need(m['gcStress']is False and m['oomTesting']is False and m['entropyPolicy']=='off'and m['strictInitialization']is True and m['hostApi']=='wasi-0.2.10','actual normal-off noGC/noOOM/entropyoff profile')
cache=I.verify(verify_sha(m['cmakeCachePath'],m['cmakeCacheSha256'])).read_text();values={k.split(':',1)[0]:v for line in cache.splitlines()if line and not line.startswith(('#','//'))and '='in line for k,v in [line.split('=',1)]}
for k,v in m['observedCMakeOptions'].items():I.need(values[k]==v,'whole actual CMake option '+k)
eq(m['requestedCMakeOptions'],m['observedCMakeOptions'],'all requested/observed exact option values');I.need(values['CMAKE_BUILD_TYPE']=='Release'and values['ENABLE_BUILTIN_WEB_TIMERS']=='ON'and values['NODE_COMPAT_GC_STRESS']==values['NODE_COMPAT_OOM_TESTING']=='OFF'and values['NODE_COMPAT_ENTROPY_MODE']=='OFF'and values['WASI_SDK_VERSION']=='30','actual release timer-enabled cache')
build=Path(m['cmakeCachePath']).parent;ext=Path(values['CMAKE_HOME_DIRECTORY']);eq(m['componentizeSourceManifest'],pins['externalEmbeddingSources'],'actual external3 accepted ancestry unchanged, now actual build source')
for d in m['componentizeSourceManifest']:verify_sha(ext/d['path'],d['sha256'])
install=verify_sha(r['actualTimerInstallationPath'],r['actualTimerInstallationSha256']);incl=I.verify(install).read_text();I.need(incl.count('NS_DEF(builtins::web::timers)')==1 and incl.count('NS_DEF(builtins::node_compat)')==1 and incl.count('NS_DEF(componentize::embedding)')==1,'actual generated timer/node/embedding namespace installation once')
rp=m['resourceOwnershipPolicy'];eq(rp['sourcePolicy'],policy['resourceOwnershipSourcePolicy'],'actual resource source ownership policy');I.need(rp['nativeRuntimeValidation']is None and rp['fullResetOrReuse']is False and rp['timerInstallation']['sha256']==install['sha256']and rp['timerInstallation']['webTimersEnabled']=='ON','timer source installation, no runtime/reset acceptance')
verify_sha(SOURCE/'tests/node-compat/build-engine.sh',m['buildRecipeSha256']);I.need(m['buildRecipeSha256']=='be43e88a99fc2ce0ac8f546404b90813856df1964befcbad4977630ce01a6527','genuine reviewed recipe afterimage')
stem=Path(r['engine']['path']).stem
for prefix,digest,value in [('source-inputs-',m['sourceInputManifestSha256'],m['sourceManifest']),('componentize-native-inputs-',m['componentizeInputManifestSha256'],m['componentizeSourceManifest'])]:eq(I.read(verify_sha(WORK/(prefix+stem+'.json'),digest)),value,'actual prebuild native/external source snapshot')
I.need(I.verify(row(WORK/('recipe-'+stem+'.sha256'))).read_text().strip()==m['buildRecipeSha256'],'actual recipe pre/post seal')
db=I.read(verify_sha(m['compileCommandsPath'],m['compileCommandsSha256']));I.need(len(db)==67,'actual67 compiler DB rows');native={Path(d['file']).relative_to(SOURCE).as_posix():d for d in db if d['file'].startswith(str(SOURCE)+'/')};I.need(len(native)==66,'actual66 configured-source commands:61policy plus5host/binding/wrapper files');generated=[d for d in db if not d['file'].startswith(str(SOURCE)+'/')];I.need(len(generated)==1 and generated[0]['file']==str(build/'starling-raw.wasm/null.cpp'),'one generated null.cpp, zero embedding rows in actual DB');I.verify(row(generated[0]['file']),'actual generated empty Rust aggregation CPP')
commands=[]
for d in db:
    w=shlex.split(d['command']);I.need(w.count('-c')==w.count('-o')==1 and w[w.index('-c')+1]==d['file']and '-fsyntax-only'not in w and '--target=wasm32-wasi'in w and [x for x in w if x.startswith('-O')]==['-O3']and '-DNDEBUG'in w,'actual finite Release compile input/output')
    I.need(not any(x.startswith(('-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY','-DDEBUG','@'))for x in w),'no GC/OOM/runtime/debug/response injection in actual normal compile context')
    for i,x in enumerate(w):
        if x=='-include':I.need(w[i+1]==str(WORK/'spidermonkey-dist-release/include/js-confdefs.h'),'only selectedSM forced header')
    I.verify(row(Path(d['directory'])/d['output']),'actual corresponding native/embedding object bytes');commands.append(dict(file=d['file'],command=d['command'],output=str(Path(d['directory'])/d['output'])))
I.need(len(m['internalTickPolicy']['actualLayoutCompileCommands'])==61 and len(m['strictEventExceptionPolicy']['actualNativeCompileCommands'])==4 and len(m['classicStreamsPolicy']['actualPrivateTargetCompileCommands'])==5,'actual61 layout/strict4/private5 command evidence')
for group in [m['internalTickPolicy']['actualLayoutCompileCommands'],m['strictEventExceptionPolicy']['actualNativeCompileCommands'],m['classicStreamsPolicy']['actualPrivateTargetCompileCommands']]:I.need(all(c in [d['command']for d in db]for c in group),'metadata policy command witnesses equal actual current compileDB')
I.need(len(m['actualEmbeddingCompileCommands'])==1 and m['actualEmbeddingCompileCommands']==m['internalTickPolicy']['actualEmbeddingCompileCommands']==m['protectedAbortListenerPolicy']['actualEmbeddingCompileCommands'],'actual separate embedding1 capture, not a compileDB row')
embedding_words=shlex.split(m['actualEmbeddingCompileCommands'][0]);I.need(embedding_words[0]==str(WORK/'cache/wasi-sdk/85e6/bin/clang++')and embedding_words.count('-c')==embedding_words.count('-o')==1 and embedding_words[embedding_words.index('-c')+1]==str(ext/'embedding/embedding.cpp')and '--target=wasm32-wasi'in embedding_words and '-O3'in embedding_words and '-DNDEBUG'in embedding_words and not any(x.startswith(('-flto','-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_OOM_TESTING','@'))for x in embedding_words),'actual separate Release noGC/noLTO embedding command context');I.verify(row(build/embedding_words[embedding_words.index('-o')+1]),'actual separate embedding object')
eq([native[n]['command']for n in ['builtins/web/timers.cpp','runtime/event_loop.cpp']], [next(d['command']for d in db if d['file']==str(SOURCE/n))for n in ['builtins/web/timers.cpp','runtime/event_loop.cpp']],'both reviewed afterimages actually included by DB')
# Actual retained Ninja rule/link inputs are source/control-flow evidence, not verbose raw argv.
ninja_row=row(build/'build.ninja');ninja=I.verify(ninja_row).read_text();rules_row=row(build/'CMakeFiles/rules.ninja');rules=I.verify(rules_row).read_text();block=ninja.split('build starling-raw.wasm/starling-raw.wasm: ',1)[1].split('\n\n',1)[0];fields={line.strip().split(' = ',1)[0]:line.strip().split(' = ',1)[1]for line in block.splitlines()[1:]if ' = 'in line};libs=shlex.split(fields['LINK_LIBRARIES']);I.need('starling-raw.wasm/libbuiltin_web_timers.a'in libs and 'libbuiltin_componentize_embedding.a'in libs,'actual timer/embedding static-library link graph')
embedding_out=embedding_words[embedding_words.index('-o')+1];embedding_block=ninja.split('build '+embedding_out+': ',1)[1].split('\n\n',1)[0];I.need(str(ext/'embedding/embedding.cpp')in embedding_block and 'CXX_COMPILER__builtin_componentize_embedding_unscanned_Release'in embedding_block,'separate actual embedding command matches parent Ninja source rule');embedding_fields={line.strip().split(' = ',1)[0]:line.strip().split(' = ',1)[1]for line in embedding_block.splitlines()[1:]if ' = 'in line}
for key in ['DEFINES','INCLUDES','FLAGS']:I.need(all(x in embedding_words for x in shlex.split(embedding_fields[key])),'separate embedding actual parent-rule '+key)
library_rows=[]
for name in sorted(set(libs)):
    I.need(name.endswith('.a'),'finite static link inputs');p=Path(name)if name.startswith('/')else build/name;d=row(p);I.verify(d,'all actual selected static libraries');library_rows.append(d)
I.need(fields['POST_BUILD']==f'cd {build}/starling-raw.wasm && {WORK}/cache/binaryen/1b13/bin/wasm-opt --strip-debug -O3 -o starling-raw.wasm starling-raw.wasm','actual in-place optimizer rule on linker output')
I.need(str(build/'cxx-wrapper')+' --target=wasm32-wasi $FLAGS $LINK_FLAGS $in -o $TARGET_FILE $LINK_PATH $LINK_LIBRARIES && $POST_BUILD'in rules,'actual selected compiler/link/postoptimizer rule')
wrapper=I.verify(row(build/'cxx-wrapper')).read_text();I.need(str(WORK/'cache/wasi-sdk/85e6/bin/clang++')in wrapper and str(SOURCE/'scripts')in wrapper,'actual compiler wrapper selects own SDK/source scripts')
for p in [build/'starling-raw.wasm/starling-raw.wasm',ext/'lib/starlingmonkey_embedding.wasm']:verify_sha(p,r['engine']['sha256'])
I.need(I.verify(r['engine']).read_bytes()[:8]==b'\0asm\1\0\0\0','actual built engine core-Wasm header; no execution')
# Archive/tool/library bytes authenticated as DATA, never invoked.
for d in m['downloadedArchives']:verify_sha(d['path'],d['sha256'])
for p,sha in [(WORK/'componentize-source.tar.gz',m['archivePins']['componentizeJsSha256']),(WORK/'spidermonkey-release.tar.gz',m['archivePins']['spiderMonkeySha256'])]:verify_sha(p,sha)
sdk=WORK/'cache/wasi-sdk/85e6';sdk_archive=next(d for d in m['downloadedArchives']if Path(d['path']).name=='wasi-sdk-30.0-arm64-macos.tar.gz');tool_aliases=[]
with tarfile.open(sdk_archive['path'])as tar:
    for name in ['VERSION','bin/clang++','bin/clang','bin/clang-21','bin/llvm-ar','bin/llvm-ranlib']:
        member=tar.getmember('wasi-sdk-30.0-arm64-macos/'+name);p=sdk/name
        if member.issym():I.need(p.is_symlink()and os.readlink(p)==member.linkname,'actual SDK declared alias');tool_aliases.append(dict(path=str(p),link=member.linkname,resolvedTarget=str(p.resolve(strict=True))))
        else:sha,n=stream_member(tar,member);I.verify(dict(path=str(p.resolve(strict=True)),sha256=sha,bytes=n),'actual SDK tar leaf bytes')
for d in m['wasiSdkVersionFiles']:I.need(I.verify(row(d['path'])).read_text()==d['contents']and 'llvm-version: 21.1.4'in d['contents'],'actual SDK30 LLVM21 version data')
with tarfile.open(WORK/'spidermonkey-release.tar.gz')as tar:
    for name in ['libspidermonkey.a','include/js-confdefs.h','include/js/RootingAPI.h','include/js/TypeDecls.h','include/js/MemoryFunctions.h']:
        member=tar.getmember('spidermonkey-dist-release/'+name);sha,n=stream_member(tar,member);I.verify(dict(path=str(WORK/'spidermonkey-dist-release'/name),sha256=sha,bytes=n),'actual selected SM archive/header bytes equal source archive')
I.need(I.verify(row(WORK/'spidermonkey-dist-release/.source-archive-sha256')).read_text().strip()==m['archivePins']['spiderMonkeySha256'],'actual SpiderMonkey source archive pin marker')
binaryen=next(d for d in m['downloadedArchives']if Path(d['path']).name=='binaryen-version_123-arm64-macos.tar.gz')
with tarfile.open(binaryen['path'])as tar:
    member=next(z for z in tar.getmembers()if z.isfile()and z.name.endswith('/bin/wasm-opt'));sha,n=stream_member(tar,member);I.verify(dict(path=str(WORK/'cache/binaryen/1b13/bin/wasm-opt'),sha256=sha,bytes=n),'actual postoptimizer tar bytes')
rust=m['generatedRustProject'];I.need(rust['cargoBuildLocked']is True and rust['manifestAndLockCheckedBeforeAndAfterBuild']is True and rust['lockSha256']==rust['versionedLockSha256'],'actual locked Rust policy')
for path,sha in [('manifestPath','manifestSha256'),('lockPath','lockSha256'),('versionedLockPath','versionedLockSha256')]:verify_sha(rust[path],rust[sha])
I.need(all('--locked'in shlex.split(c)and'--release'in shlex.split(c)and'--target=wasm32-wasip1'in shlex.split(c)for c in rust['actualCargoBuildCommands']),'actual captured locked/release Rust command rule')
I.need(all(c in log for c in rust['actualCargoBuildCommands']),'whole actual console-pool Cargo command retained in raw build log')
ssl=m['openssl'];audit=ssl['completeSourceAudit'];before=I.read(verify_sha(audit['beforeReportPath'],audit['beforeReportSha256']));I.need(ssl['version']=='3.0.17'and ssl['entropy']=='OFF'and ssl['randSeed']=='none'and audit['sourceFilesVerified']==4650 and audit['beforeAndAfterBuild']is True and audit['unexpectedFiles']==audit['missingFiles']==[]and all(audit[k]==v for k,v in before.items()),'actual OpenSSL before/after full source receipt')
verify_sha(audit['archivePath'],audit['archiveSha256']);expected_ssl={}
with tarfile.open(audit['archivePath'])as tar:
    for member in tar.getmembers():
        if not member.isfile():I.need(member.isdir(),'ordinary pristine OpenSSL archive');continue
        top,sep,name=member.name.partition('/');I.need(top=='openssl-3.0.17'and sep and name not in expected_ssl,'finite unique OpenSSL archive path');expected_ssl[name]=audit['patchedSources'].get(name)or stream_member(tar,member)[0]
actual_ssl={}
for p in Path(ssl['sourceDir']).rglob('*'):
    I.need(not p.is_symlink(),'ordinary actual OpenSSL source tree')
    if p.is_file():d=row(p);I.verify(d,'all actual4650 OpenSSL source bytes');actual_ssl[p.relative_to(ssl['sourceDir']).as_posix()]=d['sha256']
eq(actual_ssl,expected_ssl,'all4650 actual OpenSSL files equal archive plus exact two source patches');I.need(len(actual_ssl)==4650,'full actual OpenSSL count')
canonical=[dict(path=k,sha256=v)for k,v in sorted(actual_ssl.items())];I.need(hashlib.sha256(json.dumps(canonical,separators=(',',':')).encode()).hexdigest()==audit['sourceManifestSha256'],'actual lexical relative-path OpenSSL canonical manifest')
for d in [ssl['configureRecipe'],ssl['configdata'],ssl['library']]:verify_sha(d['path'],d['sha256'])
I.need(I.verify(row(ssl['configureRecipe']['path'])).read_text()==ssl['configureRecipe']['contents']and'--with-rand-seed=none'in ssl['configureRecipe']['contents']and'--release;-O3;'in ssl['configureRecipe']['contents'],'actual OpenSSL release/entropy-none configure data')
linked_crypto=[d for d in library_rows if d['path']==ssl['library']['path']];I.need(len(linked_crypto)==1 and linked_crypto[0]['sha256']==ssl['library']['sha256'],'actual libcrypto link input and metadata digest')
I.need(I.verify(row(ssl['receiptPath'])).read_bytes()and row(ssl['receiptPath'])['sha256']==ssl['receiptSha256'],'actual OpenSSL profile receipt bytes')
for p in C.glob('*.py'):ast.parse(I.verify(row(p)).read_text())
history=I.read(r['readerHistory']);I.need(history['correctedReaderPassed']is True and history['actualStdoutResultEqualsDiskResult']is True,'Root reader envelope mistake retained separately, no repeated build')
I.final_rehash()
write('build-data.json',dict(schemaVersion=1,metadata=m,actualBuildResult=built,actualSourceManifest=m['sourceManifest'],actualExternalManifest=m['componentizeSourceManifest'],compileCommands=commands,actualNinjaLinkBlock=block,actualNinjaLinkRule=rules.split('rule CXX_EXECUTABLE_LINKER__starling-raw.2ewasm_Release\n',1)[1].split('\n\n',1)[0],selectedStaticLibraries=library_rows,sdkAliases=tool_aliases,toolVersionsSourceCoupled=m['buildTools'],actualInstallSource=incl,opensslCanonicalManifest=canonical,rawNinjaSteps=steps,compileAndLinkTemplatesNotRawPerChildTerminals=True))
write('rehashed-inputs.json',dict(schemaVersion=1,files=list(I.ROWS.values()),allFinalInputHashesStable=True,reviewerOwnerActionsInvoked=False))
write('data-results.json',dict(schemaVersion=1,state='ACTUAL_RESOURCE342_NORMAL_OFF_BUILD_DATA_AUDIT_PASSED',rootObservation=root_row,resourceSourceIndex=source_index,controllerSourceIndex=controller_index,actualBuildResult=r['actualBuildResult'],rootAuthority=r['rootAuthority'],rootConfig=r['rootConfig'],externalParentTerminal=r['externalParentTerminal'],engine=r['engine'],metadata=r['metadata'],buildLog=r['buildLog'],independentStageReview=stage_pair,nativeSourceFiles=342,externalEmbeddingSources=3,stagedCopies=501,compileDbRows=67,configuredSourceCompileRows=66,layoutCompileRows=61,otherConfiguredCompileRows=5,generatedNullCompileRows=1,embeddingRowsInCompileDb=0,strictCompileRows=4,privateCompileRows=5,separateEmbeddingCompileRows=1,selectedManifestCount=9,ninjaSteps=107,rawProgressCounter31Repeated=True,rawProgressCounter32Rendered=False,timerNamespaceDefinitions=1,opensslSourceFiles=4650,selectedStaticLibraries=len(library_rows),observedProcesses=714,observedGroups=len(outer['finalGroups']),externalFiles=718,actualBuildOutputFiles=3,engineSha256=r['engine']['sha256'],metadataSha256=r['metadata']['sha256'],variant='normal-off',gcStress=False,entropyPolicy='off',oomTesting=False,cargoLocked=True,sdkVersion=30,llvmVersion='21.1.4',allSourceStageAndProofProtectionsPreserved=True,physicalInputs=len(I.ROWS),readHashChecks=I.CHECKS,rawOuterExitCode=0,rawInnerChildExitCode=0,allObservedOwnedGroupsGone=True,rawVerboseCompilerLinkArgvRetained=False,engineExecuted=False,componentOrGuestInvoked=False,reviewerOwnerActionsInvoked=False,operationalAdmission=False,runtimeAcceptanceClaim=False,actualNormalFreeze=None))
print(json.dumps(dict(state='ACTUAL_NORMAL_OFF_BUILD_DATA_PASSED',physicalInputs=len(I.ROWS),checks=I.CHECKS,nativeSources=342,externalSources=3,ninjaSteps=107,engineExecuted=False,reviewerOwnerActionsInvoked=False)))
