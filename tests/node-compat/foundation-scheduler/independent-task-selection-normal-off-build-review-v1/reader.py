"""Actual selector342 BUILD-only DATA review. No owner imports/tool execution."""
from pathlib import Path
import hashlib,json,os,re,shlex,stat,tarfile
import review_io as I

OWN=Path(__file__).resolve().parent;S=OWN.parent
P=S/'task-selection-integration-candidate-v1';C=S/'task-selection-build-controller-candidate-v1'
SOURCE=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-source')
WORK=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-build')
OUT=Path('/private/tmp/starling-node-compat/scheduler-resource-selection-v1-normal-off-build-root')
SOURCE_SHA='88af5db1cb6bc98960eaa12dac7df2d8595602c47806a25f9ebc7c6ed04474f1'
CONTROLLER_SHA='dd69c40580cfbb8671a4e3197e65a9e7f763c96f623ee95e6d3e14aa144c980f'
ALIASES=[];HARDLINKS=[]

def row(p):return I.descriptor(str(p))
def load(p):return I.read(row(p))
def eq(a,b,why):I.need(a==b,why)
def sha_file(p,sha):d=row(p);I.need(d['sha256']==sha,'actual fixed SHA '+str(p));I.verify(d);return d
def write(name,v):(OWN/name).write_text(json.dumps(v,indent=2)+'\n')
def member_hash(t,m):
    f=t.extractfile(m);h=hashlib.sha256();n=0
    for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b);n+=len(b)
    I.need(n==m.size,'whole archive member streamed');return h.hexdigest(),n
def copies(journal):
    for c in journal['copies']:
        I.verify(c['original'],'actual unchanged stage original')
        p=I.verify(dict(c['original'],path=c['path']),'actual unchanged stage copy')
        o=I.canonical(c['original']['path']);a,b=p.stat(),o.stat()
        I.need((a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino),'stage copy distinct inode')
def terminal(d,mode,root):
    t=I.read(d);I.verify_descriptors(t,'complete raw terminal+streams')
    I.need(t['rawExitCode']==0 and not t['timeout'] and not t['forcedCleanup'] and t['parentOwnedGroupGone'] and t['allObservedOwnedGroupsGone'],'actual owned raw0 without force/timeout')
    for k in ['interruptedSignals','remainingObservedPids','signals','errors']:eq(t[k],[],'empty actual terminal '+k)
    I.need(all(not g['alive'] and not g['signalAllowed']for g in t['finalGroups']),'all actual final groups absent')
    ex=Path(d['path']).parent;start=load(ex/'started.json')
    eq(start['authority'],root['rootAuthority'],'actual launch Root authority')
    eq(start['argv'][1:5],['-B','-I',str(C/'controller.py'),mode],'actual controller entry/mode, not old guard')
    eq(json.loads(start['argv'][5]),root['config'],'actual exact CLI config descriptor')
    I.need(start['pid']==t['pid'] and start['timeoutSeconds']==7200,'actual owned7200 deadline/PID')
    events=[]
    for p in sorted(ex.glob('owned-*.json')):
        e=load(p);I.need(e['sequence']==len(events),'ordered complete actual process records');events.append(e['process'])
    eq(events,t['observedProcesses'],'whole actual observed process identity list')
    I.exact_tree(ex,['started.json','terminal.json','stdout.log','stderr.log',*[f'owned-{n:04d}.json'for n in range(len(events))]])
    I.need(t['stderr']['bytes']==0,'actual empty raw external stderr')
    return t
def distribution(archive,destination,marker_names=()):
    """Archive member bytes and explicit links; no extraction or executable call."""
    expected=set();regular=0;links=0;hardlinks=0
    with tarfile.open(archive)as t:
        for m in t.getmembers():
            top,sep,name=m.name.partition('/')
            if not sep or not name:continue
            if m.isdir():
                I.member(name.rstrip('/'));continue
            I.member(name)
            I.need(name not in expected,'unique selected distribution member');expected.add(name)
            p=destination/name
            if m.issym():
                I.need(p.is_symlink()and os.readlink(p)==m.linkname,'actual declared archive symlink')
                target=p.resolve(strict=True);I.need(target.is_relative_to(destination),'selected distribution link stays inside root')
                ALIASES.append(dict(path=str(p),linkText=m.linkname,resolvedPath=str(target),archive=str(archive),archiveMember=m.name))
                if target.is_file():I.verify(row(target),'actual alias target bytes')
                links+=1
            elif m.islnk():
                target_top,sep,target_name=m.linkname.partition('/');I.need(sep and target_top==top,'declared archive hardlink same root')
                I.member(target_name);target=destination/target_name
                target_member=t.getmember(m.linkname);I.need(target_member.isfile(),'declared archive hardlink target regular')
                sha,n=member_hash(t,target_member);I.verify(dict(path=str(p),sha256=sha,bytes=n),'actual declared hardlink member bytes');I.verify(dict(path=str(target),sha256=sha,bytes=n),'actual declared hardlink target bytes')
                HARDLINKS.append(dict(path=str(p),target=str(target),archiveMember=m.name,archiveTarget=m.linkname,actualSameInode=(p.stat().st_dev,p.stat().st_ino)==(target.stat().st_dev,target.stat().st_ino)))
                hardlinks+=1
            else:
                I.need(m.isfile(),'finite regular/symlink distribution entries')
                sha,n=member_hash(t,m);I.verify(dict(path=str(p),sha256=sha,bytes=n),'whole actual distribution archive/member match');regular+=1
    actual=set()
    for base,dirs,files in os.walk(destination,followlinks=False):
        for name in [*dirs,*files]:
            p=Path(base)/name
            if p.is_file()or p.is_symlink():actual.add(p.relative_to(destination).as_posix())
    eq(actual,expected|set(marker_names),'exact selected distribution physical membership')
    return dict(archive=row(archive),root=str(destination),regularFiles=regular,links=links,declaredHardlinks=hardlinks)

def main():
    rootrow=dict(path=str(S/'task-selection-normal-off-build-v1-root-results.json'),sha256='2cc53b1177caebd620bd60a4a0b66f03710ff8e60a77e09e21c68f2aa40e3ef4',bytes=4951)
    root=I.read(rootrow);I.verify_descriptors(root,'whole actual completed Root observation')
    a=I.read(root['rootAuthority']);cfg=I.read(root['config']);built=I.read(root['actualBuildResult'])
    obs=root['actualMetadataObservation'];m=I.read(obs['metadata']);I.verify_descriptors(a,'actual build-only Root sources')
    I.need(a['phase']=='build'and a['variant']=='normal-off'and a['buildAllowed']and a['sourceIndexSha256']==SOURCE_SHA and a['configuredSourceRoot']==str(SOURCE)and a['workRoot']==str(WORK),'actual genuine new task-selector source/work/build phase')
    for k in ['stageAllowed','gcReconfigureAllowed','freezeAllowed','exportAllowed','bootstrapAllowed','componentAllowed','guestAllowed','engineExecutionAllowed','runtimeAcceptanceClaim','operationalAdmission','sourcePromotionAllowed','metadataProjectionAllowed','timingAllowed']:I.need(a[k]is False,'nonbuild gate closed '+k)
    for k in ['actualBuildResult','engine','metadata','actualNormalFreeze','independentNormalFreezeReview','runtimeAction']:I.need(a[k]is None,'pre-action Root slots preservedNULL '+k)
    eq(cfg,dict(schemaVersion=1,sourceIndex=root['taskSelectionSourceIndex'],controllerIndex=root['controllerSourceIndex'],rootAuthority=root['rootAuthority']),'full actual config')
    I.need(root['controllerSourceIndex']['sha256']==CONTROLLER_SHA and root['taskSelectionSourceIndex']['sha256']==SOURCE_SHA,'exact own source and controller roles')
    refs=load(C/'references.json');policy=load(P/'policy.json');pins=load(P/'baseline-pins.json')
    for f in refs['families']:I.indexed(f['index'],'finite original source/ancestor/stage/monitor/lifecycle family')
    for d in [root['controllerSourceIndex'],root['controllerSourceReview']['index']]:I.indexed(d,'actual controller/source-peer')
    I.verify_descriptors(refs,'actual declared source/stage/control descriptors')
    for f in [P/'input-freeze.json',C/'input-hashes.json',Path(refs['actualStageInputLedger']['path'])]:
        for d in load(f)['files']:I.verify(d,'complete finite original preparation/stage ledger')
    stage=I.read(refs['actualJournal']);I.need(len(stage['copies'])==566 and stage['destination']==str(SOURCE)and stage['nativeFiles']==342,'actual unchanged566-source stage');copies(stage)
    oldstage=I.read(refs['resourceStage']);I.need(len(oldstage['copies'])==501,'old501 staged protection');copies(oldstage)
    oldfreeze=I.read(refs['resourceFreezeReceipt']);I.need(len(oldfreeze['copies'])==666,'protected old666 frozen copies')
    for c in oldfreeze['copies']:
        I.verify(c,'old resource frozen bytes protected')
        if c['original']is not None:I.verify(c['original'],'old resource original protected including cache/DB')
    I.need(sum(c['original']is not None for c in oldfreeze['copies'])==663,'old663 original entries')
    oldroot=Path(refs['resourceFreezeReceipt']['path']).parent
    I.exact_tree(oldroot,[Path(c['path']).relative_to(oldroot).as_posix()for c in oldfreeze['copies']]+['normal-off-freeze-receipt.json'])
    outer=terminal(root['outerTerminal'],'parent',root);inner=terminal(root['innerTerminal'],'worker',root)
    outerstdout=[json.loads(x)for x in I.verify(outer['stdout']).read_text().splitlines()]
    I.need(len(outerstdout)==2 and outerstdout[0]==dict(pid=inner['pid'],timeoutSeconds=7200),'whole actual outer launch record')
    I.need(all(inner[k]==v for k,v in outerstdout[1].items()),'whole raw outer terminal frame equals disk inner terminal')
    eq(I.read(inner['stdout']),dict(output=str(OUT),result=built),'whole raw inner .result equals actual disk result')
    I.exact_tree(OUT,['launch.json','build.log','result.json'])
    I.need(built['state']=='native-build-completed-runtime-pending'and built['status']==built['rawChildExitCode']==built['launcherExitCode']==0 and built['lifecycleComplete']and built['evidenceComplete'],'actual completed native lifecycle')
    cleanup=built['ownedGroupCleanup'];I.need(cleanup['complete']and cleanup['rawChildExitCode']==0 and cleanup['events']==cleanup['errors']==built['launcherErrors']==[]and built['sigtermReceived']==0 and built['temporarySigtermHandlerRestored']and built['stopReason']is None and built['stoppedForDiskSpace']is False,'native Bash group clean/no signals/disk stop')
    eq(built['actualMetadataObservation'],obs,'Root observation equals raw result actual metadata view')
    eq(built['rootAuthority'],root['rootAuthority'],'actual native Root binding')
    I.need(built['configuredSourceRoot']==str(SOURCE)and built['workRoot']==str(WORK)and built['taskSelectionSourceIndexSha256']==SOURCE_SHA and built['parallelBuilds']==1,'actual source/work/single-job frame')
    I.need(built['requiredStartFreeBytes']==2147483648 and built['stopBelowFreeBytes']==838860800 and built['freeBytesBefore']>=2147483648 and built['freeBytesAfter']>=838860800,'actual disk lifecycle bounds')
    plan=load(P/'build-plan.json');env={**plan['explicitEnvironment'],**refs['normalEnvironmentExtra']};eq(built['explicitEnvironment'],env,'whole actual explicit environment')
    I.need(all(env[k]=='1'for k in ['NODE_COMPAT_JOBS','BINARYEN_CORES','RAYON_NUM_THREADS','CARGO_BUILD_JOBS'])and env['NODE_COMPAT_ENTROPY_MODE']=='OFF'and env['NODE_COMPAT_GC_STRESS']==env['NODE_COMPAT_OOM_TESTING']=='0'and env['NODE_COMPAT_ARTIFACT_TAG']=='selectionv1','actual finite jobs1/normalOFF/tag')
    eq(built['command'],['bash',str(SOURCE/'tests/node-compat/build-engine.sh')],'actual staged recipe argv')
    log=I.verify(root['buildLog']).read_text();eq(root['buildLog'],built['buildLog'],'full raw build log descriptor')
    steps=[int(x)for x in re.findall(r'^\[(\d+)/107\]',log,re.M)]
    I.need(steps[-1]==107 and max(steps)==107 and '[107/107]'in log and 'Finished `release` profile'in log,'actual final107-step build/Cargo completion')
    eq(m['sourceManifest'],policy['expectedNativeSourceManifest'],'actual new342 source manifest matches reviewed selector policy')
    I.need(len(m['sourceManifest'])==342 and m['auditedBaseRevision']==m['starlingMonkeyRevision']==stage['baseline'],'actual342 baseline')
    parent=load(Path(pins['parentPolicy']['path']))
    old={d['path']:d['sha256']for d in parent['expectedNativeSourceManifest']}
    changed=[d['path']for d in m['sourceManifest']if d['sha256']!=old[d['path']]]
    eq(set(changed),{'include/extension-api.h','host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp'},'actual339 unchanged+3 ABI/source corrections')
    for d in m['sourceManifest']:sha_file(SOURCE/d['path'],d['sha256'])
    eq(m['taskSelectionPolicy']['sourcePolicy'],policy['taskSelectionSourcePolicy'],'new actual source-derived taskSelectionPolicy')
    I.need(m['taskSelectionPolicy']['allNativeDependentsRequireRebuild']and m['taskSelectionPolicy']['nativeAllInvalidRuntimeValidation']is None and m['taskSelectionPolicy']['fullResetOrReuse']is False,'ABI rebuild source contract, no runtime/reset claim')
    I.need(m['gcStress']is False and m['oomTesting']is False and m['entropyPolicy']=='off'and m['strictInitialization'],'actual normalOFF/noGC/OOM')
    eq(m['enginePath'],obs['engine']['path'],'raw metadata original new engine path')
    I.need(m['engineSha256']==obs['engine']['sha256']=='f6a775f019ca48bb6b9a46a88364aa51a2691101a9e79325848afb5504c3034f'and m['engineBytes']==9976922,'actual new engine identity, not fec7')
    I.need(obs['metadata']['sha256']=='8219b7aaea6f5a311ccd9e2d038edcd213663078f9ff18917c155dfeb51dde4f','untouched raw new sidecar')
    cache=I.verify(sha_file(m['cmakeCachePath'],m['cmakeCacheSha256'])).read_text();values={k.split(':',1)[0]:v for line in cache.splitlines()if line and not line.startswith(('#','//'))and '='in line for k,v in[line.split('=',1)]}
    for k,v in m['observedCMakeOptions'].items():eq(values[k],v,'actual CMake option '+k)
    eq(m['requestedCMakeOptions'],m['observedCMakeOptions'],'all requested/observed CMake options')
    I.need(values['CMAKE_BUILD_TYPE']=='Release'and values['ENABLE_BUILTIN_WEB_TIMERS']=='ON'and values['NODE_COMPAT_GC_STRESS']==values['NODE_COMPAT_OOM_TESTING']=='OFF'and values['WASI_SDK_VERSION']=='30','actual Release/timers/SDK30')
    build=Path(m['cmakeCachePath']).parent;external=Path(values['CMAKE_HOME_DIRECTORY'])
    eq(m['componentizeSourceManifest'],pins['externalEmbeddingSources'],'genuine external3 unchanged source ancestry')
    for d in m['componentizeSourceManifest']:sha_file(external/d['path'],d['sha256'])
    sha_file(SOURCE/'tests/node-compat/build-engine.sh',m['buildRecipeSha256']);I.need(m['buildRecipeSha256']=='e62b6b8e6bec5f28b6d87c5e47a27ae377a4496d37e3227760c88a548eb2b691','actual new recipe')
    stem=Path(obs['engine']['path']).stem
    for prefix,sha,value in [('source-inputs-',m['sourceInputManifestSha256'],m['sourceManifest']),('componentize-native-inputs-',m['componentizeInputManifestSha256'],m['componentizeSourceManifest'])]:eq(I.read(sha_file(WORK/(prefix+stem+'.json'),sha)),value,'actual prebuild source capture')
    I.need(I.verify(row(WORK/('recipe-'+stem+'.sha256'))).read_text().strip()==m['buildRecipeSha256'],'actual recipe pre/post capture')
    db=I.read(sha_file(m['compileCommandsPath'],m['compileCommandsSha256']));I.need(len(db)==67,'actual67 compile database')
    layout={str(SOURCE/d['path'])for d in m['sourceManifest']if d['path'].endswith('.cpp')and d['path'].startswith(('runtime/','builtins/'))}
    native=[d for d in db if d['file']in layout];other=[d for d in db if d['file']not in layout]
    I.need(len(native)==61 and len([d for d in other if d['file'].startswith(str(SOURCE)+'/')])==5 and len([d for d in other if d['file']==str(build/'starling-raw.wasm/null.cpp')])==1,'actual61+5+1 classification')
    objects=[]
    for d in db:
        w=shlex.split(d['command']);I.need(w.count('-c')==w.count('-o')==1 and w[w.index('-c')+1]==d['file']and '--target=wasm32-wasi'in w and [x for x in w if x.startswith('-O')]==['-O3']and '-DNDEBUG'in w,'actual compile input/output Release flags')
        I.need(not any(x.startswith(('-DNODE_COMPAT_GC_STRESS','-DNODE_COMPAT_OOM_TESTING','-DNODE_COMPAT_ENTROPY_RUNTIME_ONLY','-DDEBUG','@'))for x in w)and '-fsyntax-only'not in w,'no GC/OOM/runtime/debug/response injection')
        if d['file']==str(build/'starling-raw.wasm/null.cpp'):
            I.need(w.count('-include')==0,'generated null aggregation source has no selected SM forced include')
            I.verify(row(d['file']),'actual generated null aggregation source')
        else:I.need(w.count('-include')==1 and w[w.index('-include')+1]==str(WORK/'spidermonkey-dist-release/include/js-confdefs.h'),'singleton exact selected SM forced header on configured sources')
        objects.append(row(Path(d['directory'])/d['output']));I.verify(objects[-1],'all actual corresponding67 object bytes')
    for group,count in [(m['internalTickPolicy']['actualLayoutCompileCommands'],61),(m['strictEventExceptionPolicy']['actualNativeCompileCommands'],4),(m['classicStreamsPolicy']['actualPrivateTargetCompileCommands'],5)]:I.need(len(group)==count and all(c in[d['command']for d in db]for c in group),'actual full61/4/5 command arrays')
    private={str(SOURCE/name)for name in policy['privateTargetCpp']}
    I.need(len(private)==5,'five declared private targets')
    for d in native:
        words=shlex.split(d['command'])
        for macro in ['NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER','NODE_COMPAT_ENTROPY_POLICY']:I.need('-D'+macro+'=1'in words,'public native boundary macro '+macro)
        I.need(('-DNODE_COMPAT_CLASSIC_STREAMS=1'in words)==(d['file']in private),'actual exact private classic macro scope')
    for key,path in [('actualHostApiCompileCommands','host-apis/wasi-0.2.0/host_api.cpp'),('actualEventLoopCompileCommands','runtime/event_loop.cpp')]:eq(m['taskSelectionPolicy'][key],[next(d['command']for d in db if d['file']==str(SOURCE/path))],'actual new selector ABI dependent compiled '+path)
    embed=m['actualEmbeddingCompileCommands'];eq(embed,m['internalTickPolicy']['actualEmbeddingCompileCommands'],'actual separate embedding command')
    I.need(len(embed)==1,'embedding separate1');ew=shlex.split(embed[0]);I.need(ew.count('-c')==ew.count('-o')==1 and ew[ew.index('-c')+1]==str(external/'embedding/embedding.cpp')and '-O3'in ew and '-DNDEBUG'in ew and not any(x.startswith('-flto')for x in ew),'actual Release separate NoLTO embedding')
    I.need(ew.count('-include')==1 and ew[ew.index('-include')+1]==str(WORK/'spidermonkey-dist-release/include/js-confdefs.h')and '-DNODE_COMPAT_CLASSIC_STREAMS=1'not in ew,'embedding exact forced header/no private classic macro')
    objects.append(row(build/ew[ew.index('-o')+1]));I.verify(objects[-1],'actual separate embedding object')
    ninja=I.verify(row(build/'build.ninja')).read_text();rules=I.verify(row(build/'CMakeFiles/rules.ninja')).read_text()
    block=ninja.split('build starling-raw.wasm/starling-raw.wasm: ',1)[1].split('\n\n',1)[0]
    fields={x.strip().split(' = ',1)[0]:x.strip().split(' = ',1)[1]for x in block.splitlines()[1:]if ' = 'in x};libs=shlex.split(fields['LINK_LIBRARIES'])
    I.need('starling-raw.wasm/libbuiltin_web_timers.a'in libs and 'libbuiltin_componentize_embedding.a'in libs,'actual timer/embedding link graph')
    library_rows=[]
    for name in sorted(set(libs)):
        I.need(name.endswith('.a'),'finite actual static link inputs');p=Path(name)if name.startswith('/')else build/name;d=row(p);I.verify(d,'all actual selected linked libraries');library_rows.append(d)
    I.need(fields['POST_BUILD']==f'cd {build}/starling-raw.wasm && {WORK}/cache/binaryen/1b13/bin/wasm-opt --strip-debug -O3 -o starling-raw.wasm starling-raw.wasm','actual compiler/optimizer in-place link graph')
    I.need(str(build/'cxx-wrapper')+' --target=wasm32-wasi $FLAGS $LINK_FLAGS $in -o $TARGET_FILE $LINK_PATH $LINK_LIBRARIES && $POST_BUILD'in rules,'actual compiler linker rule')
    eblock=ninja.split('build '+ew[ew.index('-o')+1]+': ',1)[1].split('\n\n',1)[0];I.need(str(external/'embedding/embedding.cpp')in eblock,'actual parent embedding source rule')
    for line in eblock.splitlines()[1:]:
        if ' = 'in line:
            k,v=line.strip().split(' = ',1)
            if k in ['DEFINES','INCLUDES','FLAGS']:I.need(all(x in ew for x in shlex.split(v)),'actual embedding Ninja flags '+k)
    for p in [build/'starling-raw.wasm/starling-raw.wasm',external/'lib/starlingmonkey_embedding.wasm']:sha_file(p,obs['engine']['sha256'])
    I.need(I.verify(obs['engine']).read_bytes()[:8]==b'\0asm\1\0\0\0','actual core Wasm magic, not execution')
    incl=sha_file(m['resourceOwnershipPolicy']['timerInstallation']['path'],m['resourceOwnershipPolicy']['timerInstallation']['sha256']);install=I.verify(incl).read_text()
    I.need(install.count('NS_DEF(builtins::web::timers)')==1 and install.count('NS_DEF(builtins::node_compat)')==1 and install.count('NS_DEF(componentize::embedding)')==1,'actual generated timer/node/embedding registration')
    for d in m['downloadedArchives']:sha_file(d['path'],d['sha256'])
    for p,sha in [(WORK/'componentize-source.tar.gz',m['archivePins']['componentizeJsSha256']),(WORK/'spidermonkey-release.tar.gz',m['archivePins']['spiderMonkeySha256'])]:sha_file(p,sha)
    sdk_archive=next(d['path']for d in m['downloadedArchives']if Path(d['path']).name=='wasi-sdk-30.0-arm64-macos.tar.gz')
    distributions=[distribution(sdk_archive,WORK/'cache/wasi-sdk/85e6'),distribution(WORK/'spidermonkey-release.tar.gz',WORK/'spidermonkey-dist-release',['.source-archive-sha256'])]
    I.need(I.verify(row(WORK/'spidermonkey-dist-release/.source-archive-sha256')).read_text().strip()==m['archivePins']['spiderMonkeySha256'],'actual selected SM cache archive marker')
    binaryen=next(d['path']for d in m['downloadedArchives']if Path(d['path']).name=='binaryen-version_123-arm64-macos.tar.gz');distributions.append(distribution(binaryen,WORK/'cache/binaryen/1b13'))
    for d in m['wasiSdkVersionFiles']:I.need(I.verify(row(d['path'])).read_text()==d['contents']and'llvm-version: 21.1.4'in d['contents'],'actual SDK30/LLVM21 version data')
    rust=m['generatedRustProject'];I.need(rust['cargoBuildLocked']and rust['manifestAndLockCheckedBeforeAndAfterBuild']and rust['lockSha256']==rust['versionedLockSha256'],'actual locked Rust')
    for p,h in [('manifestPath','manifestSha256'),('lockPath','lockSha256'),('versionedLockPath','versionedLockSha256')]:sha_file(rust[p],rust[h])
    I.need(all('--locked'in shlex.split(c)and'--release'in shlex.split(c)and c in log for c in rust['actualCargoBuildCommands']),'whole actual locked/release Cargo command retained')
    ssl=m['openssl'];audit=ssl['completeSourceAudit'];before=I.read(sha_file(audit['beforeReportPath'],audit['beforeReportSha256']))
    I.need(ssl['version']=='3.0.17'and ssl['entropy']=='OFF'and ssl['randSeed']=='none'and audit['sourceFilesVerified']==4650 and audit['unexpectedFiles']==audit['missingFiles']==[]and all(audit[k]==v for k,v in before.items()),'actual OpenSSL4650 before/after record')
    sha_file(audit['archivePath'],audit['archiveSha256']);expected_ssl={}
    with tarfile.open(audit['archivePath'])as t:
        for z in t.getmembers():
            if not z.isfile():I.need(z.isdir(),'ordinary OpenSSL archive');continue
            top,sep,name=z.name.partition('/');I.need(top=='openssl-3.0.17'and sep and name not in expected_ssl,'finite unique OpenSSL source path');expected_ssl[name]=audit['patchedSources'].get(name)or member_hash(t,z)[0]
    actual_ssl={}
    for p in Path(ssl['sourceDir']).rglob('*'):
        I.need(not p.is_symlink(),'ordinary actual OpenSSL source')
        if p.is_file():d=row(p);I.verify(d,'all actual4650 OpenSSL source bytes');actual_ssl[p.relative_to(ssl['sourceDir']).as_posix()]=d['sha256']
    eq(actual_ssl,expected_ssl,'all4650 OpenSSL sources equal archive plus two declared patches')
    canon=[dict(path=k,sha256=v)for k,v in sorted(actual_ssl.items())];I.need(hashlib.sha256(json.dumps(canon,separators=(',',':')).encode()).hexdigest()==audit['sourceManifestSha256'],'full OpenSSL canonical manifest')
    for d in [ssl['configureRecipe'],ssl['configdata'],ssl['library']]:sha_file(d['path'],d['sha256'])
    I.need(I.verify(row(ssl['configureRecipe']['path'])).read_text()==ssl['configureRecipe']['contents']and'--with-rand-seed=none'in ssl['configureRecipe']['contents'],'actual entropy-none OpenSSL configure record')
    I.need(any(d['path']==ssl['library']['path']and d['sha256']==ssl['library']['sha256']for d in library_rows),'actual selected linked libcrypto')
    sha_file(ssl['receiptPath'],ssl['receiptSha256'])
    # Host tools are provenance data, including exact declared leaf aliases.
    tool_refs=[]
    for name in ['CMAKE_COMMAND','CMAKE_MAKE_PROGRAM','CBINDGEN_EXECUTABLE']:
        p=Path(values[name]);target=p.resolve(strict=True);tool_refs.append(dict(role=name,declaredPath=str(p),resolved=row(target),linkText=os.readlink(p)if p.is_symlink()else None));I.verify(tool_refs[-1]['resolved'],'actual selected host tool')
    for command in rust['actualCargoBuildCommands']:
        for word in shlex.split(command):
            if word.startswith('CARGO_BUILD_RUSTC='):
                p=Path(word.split('=',1)[1]);I.verify(row(p),'actual Rust compiler tool')
            elif word.startswith('/')and word.endswith('/cargo'):I.verify(row(word),'actual Cargo tool')
    I.final_rehash()
    # Explicit aliases are rechecked, not copied or normalized to different roles.
    for d in ALIASES:I.need(os.readlink(d['path'])==d['linkText']and str(Path(d['path']).resolve())==d['resolvedPath'],'all final declared SDK aliases unchanged')
    write('build-data.json',dict(schemaVersion=1,metadata=m,actualBuildResult=built,actualSourceManifest=m['sourceManifest'],actualExternalManifest=m['componentizeSourceManifest'],nativeCompileCommands=db,separateEmbeddingCommands=embed,actualNinjaLinkBlock=block,linkedLibraries=library_rows,actualObjects=objects,distributions=distributions,referenceAliases=ALIASES,declaredArchiveHardlinks=HARDLINKS,hostToolReferences=tool_refs,rawNinjaProgressCounters=steps,opensslCanonicalManifest=canon,engineExecuted=False))
    write('input-hashes.json',dict(schemaVersion=1,files=list(I.ROWS.values()),aliasesDeclaredSeparately=True,allFinalInputHashesStable=True,reviewerOwnerActionsInvoked=False))
    write('data-results.json',dict(schemaVersion=1,state='ACTUAL_TASK_SELECTION342_NORMAL_OFF_BUILD_DATA_AUDIT_PASSED_V1',verifiedPassed=True,rootObservation=rootrow,sourceIndex=root['taskSelectionSourceIndex'],controllerSourceIndex=root['controllerSourceIndex'],actualBuildResult=root['actualBuildResult'],externalParentTerminal=root['outerTerminal'],ownedWorkerTerminal=root['innerTerminal'],rootAuthority=root['rootAuthority'],rootConfig=root['config'],engine=obs['engine'],metadata=obs['metadata'],buildLog=root['buildLog'],nativeSourceFiles=342,unchangedParentFiles=339,changedFiles=changed,externalEmbeddingSources=3,selectedManifestCount=9,compileDatabaseRows=67,policyNativeCppCommands=61,otherConfiguredCommands=5,generatedNullCommands=1,strictCommands=4,privateCommands=5,separateEmbeddingCommands=1,actualObjectFiles=len(objects),linkedStaticLibraries=len(library_rows),orderedStaticLibraryArguments=len(libs),distributions=distributions,sdkAliases=len(ALIASES),opensslSourceFiles=4650,sourceStageCopies=566,oldResourceStageCopies=501,oldResourceFrozenCopies=666,oldResourceOriginalEntries=663,outerObservedProcesses=len(outer['observedProcesses']),innerObservedProcesses=len(inner['observedProcesses']),actualBuildOutputFiles=3,lastNinjaStep=107,rawOuterExitCode=0,rawInnerExitCode=0,rawBashExitCode=0,allObservedOwnedGroupsGone=True,forcedCleanup=False,engineExecuted=False,freezeInvoked=False,guestExecuted=False,operationalAdmission=False,runtimeAcceptanceClaim=False,actualFreeze=None,physicalInputFiles=len(I.ROWS),checks=I.CHECKS,reviewerOwnerActionsInvoked=False))
    print(json.dumps(dict(checks=I.CHECKS,physicalInputs=len(I.ROWS),lastNinjaStep=107,engine=obs['engine'],metadata=obs['metadata'],distributions=distributions)))

if __name__=='__main__':main()
