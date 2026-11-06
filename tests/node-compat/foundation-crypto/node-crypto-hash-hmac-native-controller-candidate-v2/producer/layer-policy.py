"""New357 source/compile producer; historical source is ancestry DATA."""
import copy
import hashlib
import importlib.util
import json
import pathlib
from pathlib import Path
import shlex
import sys
sys.dont_write_bytecode=True
if not __debug__:raise RuntimeError('Source policy checks require assertions')
HERE=Path(__file__).resolve().parent
REPO=Path('/private/tmp/starling-node-compat/node-crypto-hash-hmac-v1-source')
assert HERE==Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-crypto/node-crypto-hash-hmac-native-controller-candidate-v2/producer'), 'Exact active source helper context required'
# Own literal configured-native context; never mutate an imported donor namespace.
DONOR_INPUTS=HERE/'donor-inputs.json'
POLICY_SHA256='b2421527506774820551e448b8536e43e0a4e402cc6788dc62409c161debdf91'
AUTH_SHA256='c4189e1a5b15c5a847ee2c571868e0bd653d58d0ed3031501aace8d286a1279b'
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert digest(HERE/'policy.json')==POLICY_SHA256
POLICY=json.loads((HERE/'policy.json').read_bytes())

def authenticate_inputs():
    assert digest(DONOR_INPUTS)==AUTH_SHA256
    rows=json.loads(DONOR_INPUTS.read_bytes())['files']
    assert len(rows)==len({r['path']for r in rows})
    for r in rows:
        path=REPO
        for part in r['path'].split('/'):
            assert part and part not in('.','..');path/=part;assert not path.is_symlink(),path
        assert path.is_file()and path.stat().st_size==r['bytes']and digest(path)==r['sha256'],path
    return True
authenticate_inputs()
BASE_ROOT=REPO/'tests/node-compat/foundation-crypto/ownership-secret-integration-candidate-v1'
BASE=json.loads((BASE_ROOT/'policy.json').read_bytes())
ANCESTOR_ROOT=REPO/'tests/node-compat/foundation-scheduler/integration-candidate-v1'
ANCESTOR=json.loads((ANCESTOR_ROOT/'policy.json').read_bytes())
PARENT_ROOT=REPO/'tests/node-compat/foundation-scheduler/combined-native-build-controller-candidate-v2'
PARENT=json.loads((PARENT_ROOT/'policy.json').read_bytes())
assert PARENT['expectedNativeSourceManifest']==POLICY['combinedSourcePolicy']['parentExpectedNativeSourceManifest']
assert PARENT['combinedSourcePolicy']==POLICY['parentCombinedSourcePolicy']
assert BASE['expectedNativeSourceManifest']==PARENT['combinedSourcePolicy']['parentExpectedNativeSourceManifest']
before={r['path']:r['sha256']for r in PARENT['expectedNativeSourceManifest']}
after={r['path']:r['sha256']for r in POLICY['expectedNativeSourceManifest']}
assert len(before)==355 and len(after)==357 and before.keys() <= after.keys()
changes=POLICY['combinedSourcePolicy']['changes']
assert len(changes)==4 and sum(before[p]==after[p]for p in before)==353
assert sum(r['beforeSha256']is None for r in changes)==2
for r in changes:assert before.get(r['path'])==r['beforeSha256']and after[r['path']]==r['afterSha256']
for key in ('cryptoKeyOwnershipSourcePolicy','cryptoSecretFailureSourcePolicy','streamConsumersSourcePolicy','zlibSourcePolicy'):
    assert POLICY[key]==PARENT[key]==BASE[key], 'Historical ancestry preserved; current source checked separately'
for key in ('resourceOwnershipSourcePolicy','taskSelectionSourcePolicy','zlibErrorSemanticsSourcePolicy'):
    assert POLICY[key]==PARENT[key]
assert POLICY['parentExpectedNativeSourceManifest']==ANCESTOR['expectedNativeSourceManifest']
model_path=HERE/'hash-hmac-model.py'
assert digest(model_path)==POLICY['hashHmacModelSha256']
model_spec=importlib.util.spec_from_file_location('new357_hash_hmac_source_primitives',model_path)
HASH_MODEL=importlib.util.module_from_spec(model_spec);model_spec.loader.exec_module(HASH_MODEL)

def expected(relative,base_expected):
    prior=ANCESTOR['sourceLayer'].get(relative)
    parent=base_expected
    if prior is not None:
        assert prior['beforeSha256']==base_expected
        parent=prior['afterSha256']
    entry=POLICY['sourceLayer'].get(relative)
    if entry is None:return parent
    assert entry['beforeSha256']==parent,'Actual306 source ancestry mismatch: '+relative
    return entry['afterSha256']
def resolved(mapping):return{path:expected(path,value)for path,value in mapping.items()}
def source_manifest(repo):
    authenticate_inputs();repo=Path(repo)
    assert repo.resolve()==Path(POLICY['contexts']['configuredSourceRoot'])
    rows=POLICY['expectedNativeSourceManifest']
    assert len(rows)==len({r['path']for r in rows})==357
    for r in rows:
        path=repo
        for part in r['path'].split('/'):
            assert part and part not in('.','..');path/=part;assert not path.is_symlink(),path
        assert path.is_file()and digest(path)==r['sha256'],'Unreviewed combined355 source: '+r['path']
    return copy.deepcopy(rows)
def validate_sources(repo,manifest=None):
    actual=source_manifest(repo)
    if manifest is not None:assert sorted(manifest,key=lambda r:r['path'])==actual and all(set(r)=={'path','sha256'}for r in manifest)
    return True
def load_codec():
    authenticate_inputs()
    path=REPO/'tests/node-compat/foundation-zlib/native-integration-candidate-v4/codec-evidence.py'
    assert digest(path)==POLICY['selectedCodecCompileContract']['codecEvidenceSha256']
    spec=importlib.util.spec_from_file_location('genuine_selected_codec_primitives',path)
    codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
    return codec

def _macro(words,name,enabled):
    assert '-D'not in words and '-U'not in words,'Need joined captured macro arguments'
    values=[word for word in words if word=='-D'+name or word.startswith('-D'+name+'=')]
    assert values==(['-D'+name+'=1']if enabled else[]),'Conflicting/missing '+name
    assert '-U'+name not in words


def _release(words):
    assert [word for word in words if word.startswith('-O')]==['-O3'],'Exactly one Release optimization flag required'
    assert [word for word in words if word=='-DNDEBUG'or word.startswith('-DNDEBUG=')]==['-DNDEBUG'],'Exact NDEBUG definition required'
    assert '-UNDEBUG'not in words and '-UDEBUG'not in words and not any(word.startswith('-DDEBUG')for word in words)
    assert not any(word=='-DNODE_COMPAT_OOM_TESTING'or word.startswith('-DNODE_COMPAT_OOM_TESTING=')for word in words)
    assert '-UNODE_COMPAT_OOM_TESTING'not in words


def validate_layout_compilation(entries,embedding_commands,enabled,repo):
    assert type(enabled) is bool
    repo=pathlib.Path(repo)
    native=[i['command'] for i in entries if i['file'].endswith('.cpp') and
            any(pathlib.Path(i['file']).as_posix().startswith(str(repo/d)+'/') for d in ['builtins','runtime'])]
    assert native and embedding_commands,'Need actual native AND external embedding compiler observations'
    flag='-DNODE_COMPAT_INTERNAL_TICKS=1'
    for command in native+embedding_commands:
        words=shlex.split(command)
        assert '-c' in words and '-fsyntax-only' not in words,'Need actual engine compile, not syntax proof'
        assert (flag in words)==enabled,'Inconsistent scheduler layout macro'
        assert '-DNODE_COMPAT_STRICT_INITIALIZATION=1' in words
    queue=[i['command'] for i in entries if i['file'].endswith('/runtime/node_tick_queue.cpp')]
    assert len(queue)==int(enabled),'Queue TU must compile exactly once only when selected'
    for suffix in ['/runtime/engine.cpp','/runtime/event_loop.cpp','/builtins/node-compat/register.cpp']:
        assert sum(i['file'].endswith(suffix) for i in entries)==1,'Missing/duplicate layout TU: '+suffix
    return native,queue


def task_selection_commands(entries,repo,metadata):
    repo=Path(repo);paths=['host-apis/wasi-0.2.0/host_api.cpp','runtime/event_loop.cpp'];found={}
    for name in paths:
        rows=[row for row in entries if row['file']==str(repo/name)]
        assert len(rows)==1,'Exactly one actual selector implementation/caller command required: '+name
        words=shlex.split(rows[0]['command']);assert words.count('-c')==1 and words[words.index('-c')+1]==str(repo/name)and '-fsyntax-only'not in words
        _release(words);_macro(words,'NODE_COMPAT_ENTROPY_POLICY',True)
        _macro(words,'NODE_COMPAT_ENTROPY_RUNTIME_ONLY',metadata['entropyPolicy']=='runtime-only')
        if name.startswith('host-apis/'):
            for macro in('NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_CLASSIC_STREAMS','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_GC_STRESS'):_macro(words,macro,False)
        found[name]=rows[0]['command']
    return found



def validate_classic_compilation(entries,embedding,repo,metadata):
    ticks=metadata['internalTicksEnabled'];classic=metadata['classicStreamsEnabled'];web=metadata['streamWebEnabled']
    assert all(type(value)is bool for value in[ticks,classic,web,metadata['eventsEnabled'],metadata['stringDecoderEnabled']])
    assert not(metadata['gcStress'] and metadata['entropyPolicy']=='runtime-only'),'RuntimeOnly+GC is outside this finite producer'
    if classic:assert ticks and metadata['eventsEnabled'] and metadata['stringDecoderEnabled']
    validate_sources(repo)
    codec=load_codec()
    selected=metadata['zlibSelectedCodecInput'];codec.selection_contract(selected)
    native,queue=validate_layout_compilation([row for row in entries if row['file']!=str(Path(repo)/'builtins/node-compat/zlib/kernel.cpp')],embedding,ticks,repo)
    cpp=[row['path']for row in POLICY['expectedNativeSourceManifest']if row['path'].endswith('.cpp')and row['path'].startswith(('builtins/','runtime/'))]
    active=[name for name in cpp if(ticks or name!='runtime/node_tick_queue.cpp')and(web or name!='builtins/node-compat/stream-web-kernel.cpp')and(metadata['zlibEnabled']or name!='builtins/node-compat/zlib/kernel.cpp')]
    assert len(cpp)==63
    rows=[row for row in entries if row['file'].endswith('.cpp')and any(Path(row['file']).as_posix().startswith(str(Path(repo)/base)+'/')for base in['builtins','runtime'])]
    mapped={}
    private=[]
    for row in rows:
        names=[name for name in cpp if row['file']==str(Path(repo)/name)]
        assert len(names)==1 and names[0]not in mapped,'Unknown/duplicate native TU'
        name=names[0];mapped[name]=row['command'];words=shlex.split(row['command'])
        assert words.count('-c')==1 and '-fsyntax-only'not in words
        _release(words)
        _macro(words,'NODE_COMPAT_STRICT_INITIALIZATION',True)
        _macro(words,'NODE_COMPAT_INTERNAL_TICKS',ticks)
        _macro(words,'NODE_COMPAT_CLASSIC_STREAMS',classic and name in POLICY['privateTargetCpp'])
        _macro(words,'NODE_COMPAT_ZLIB',metadata['zlibEnabled']and name.startswith('builtins/node-compat/'))
        _macro(words,'NODE_COMPAT_STREAM_CONSUMERS',metadata['streamConsumersEnabled']and name in POLICY['privateTargetCpp'])
        codec.no_second_codec(words,selected)
        _macro(words,'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER',metadata['eventsEnabled'])
        _macro(words,'NODE_COMPAT_STREAM_WEB',web and name.startswith('builtins/node-compat/'))
        _macro(words,'NODE_COMPAT_ENTROPY_RUNTIME_ONLY',metadata['entropyPolicy']=='runtime-only')
        _macro(words,'NODE_COMPAT_ENTROPY_POLICY',True)
        _macro(words,'NODE_COMPAT_GC_STRESS',metadata['gcStress'] and name in POLICY['privateTargetCpp'])
        if name in POLICY['privateTargetCpp']:private.append(row['command'])
    assert sorted(mapped)==sorted(active)
    for command in embedding:
        words=shlex.split(command);assert words.count('-c')==1 and '-fsyntax-only'not in words
        _release(words)
        _macro(words,'NODE_COMPAT_STRICT_INITIALIZATION',True)
        _macro(words,'NODE_COMPAT_INTERNAL_TICKS',ticks)
        _macro(words,'NODE_COMPAT_CLASSIC_STREAMS',False)
        _macro(words,'NODE_COMPAT_ZLIB',False)
        _macro(words,'NODE_COMPAT_STREAM_CONSUMERS',False)
        codec.no_second_codec(words,selected)
        _macro(words,'NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER',metadata['eventsEnabled'])
        _macro(words,'NODE_COMPAT_ENTROPY_RUNTIME_ONLY',metadata['entropyPolicy']=='runtime-only')
        _macro(words,'NODE_COMPAT_ENTROPY_POLICY',True)
        _macro(words,'NODE_COMPAT_GC_STRESS',False)
    assert len(embedding)==1 and len(private)==(5 if web else 4)+int(metadata['zlibEnabled'])+int(metadata['nodeCryptoHashHmacEnabled'])
    return [row['command']for row in rows],queue,private



def decorate(metadata,repo,source_dir,entries,embedding_commands,enabled,ninja_capture,ninja_text):
    assert metadata['gcStress']is False and metadata['entropyPolicy']=='off','Only initial normal-OFF Hash/Hmac357 producer is implemented'
    validate_sources(repo,metadata['sourceManifest'])
    assert type(enabled)is bool and metadata['internalTicksEnabled']is enabled
    choice='ON'if metadata['classicStreamsEnabled']else'OFF'
    for field in['requestedCMakeOptions','observedCMakeOptions']:
        assert metadata[field]['NODE_COMPAT_CLASSIC_STREAMS']==choice
    assert metadata['oomTesting']is False and metadata['observedCMakeOptions']['CMAKE_BUILD_TYPE']=='Release'
    assert digest(Path(source_dir)/'embedding/embedding.cpp')==POLICY['embedding']['afterSha256']
    native,queue,private=validate_classic_compilation(entries,embedding_commands,repo,metadata)
    strict=metadata['strictEventExceptionPolicy'];protected=metadata['protectedAbortListenerPolicy']
    assert strict['version']==ANCESTOR['parentStrictPolicyVersion']
    assert protected['version']==ANCESTOR['parentProtectedPolicyVersion']
    strict['parentSourcePolicy']={key:copy.deepcopy(strict[key])for key in['version','patchSha256','basePolicy','embeddingBoundaryPatchSha256','nativeSourceSha256']}
    protected['parentSourcePolicy']={key:copy.deepcopy(protected[key])for key in['version','patchSha256','sourceSha256','strictPolicyVersion']}
    strict['version']=POLICY['strictPolicyVersion'];strict['nativeSourceSha256']=resolved(strict['nativeSourceSha256'])
    for name in['runtime/node_tick_queue.cpp','runtime/node_tick_queue.h']:strict['nativeSourceSha256'][name]=ANCESTOR['sourceLayer'][name]['afterSha256']
    strict['actualNativeCompileCommands']+=queue
    protected['version']=POLICY['protectedPolicyVersion'];protected['strictPolicyVersion']=strict['version'];protected['sourceSha256']=resolved(protected['sourceSha256'])
    metadata['internalTickPolicy']={
      'version':POLICY['version'],'enabled':enabled,'sourcePolicyInstalled':True,
      'parentRecipeSha256':POLICY['parentRecipeSha256'],'parentNativeManifestCanonicalSha256':POLICY['parentNativeManifestCanonicalSha256'],
      'parentPrivateTickPolicyFileSha256':POLICY['parentPolicySha256'],'parentPrivateTickHelperSha256':POLICY['parentHelperSha256'],
      'sourceLayer':POLICY['sourceLayer'],'nativePatchSha256':POLICY['nativePatchSha256'],
      'embeddingPatchSha256':POLICY['embedding']['patchSha256'],'embeddingBeforeSha256':POLICY['embedding']['beforeSha256'],'embeddingAfterSha256':POLICY['embedding']['afterSha256'],
      'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),
      'actualLayoutCompileCommands':native,'actualQueueCompileCommands':queue,'actualEmbeddingCompileCommands':embedding_commands,
      'requestedCMake':metadata['requestedCMakeOptions']['NODE_COMPAT_INTERNAL_TICKS'],'observedCMake':metadata['observedCMakeOptions']['NODE_COMPAT_INTERNAL_TICKS'],
      'limits':ANCESTOR['limits'],'addsExternalCapabilities':False,'publicProcessModule':False,
      'resetSafeReuse':'OPEN; cancellation and teardown not established',
      'scope':'Actual new357 source/command observations; parent355/342/306 are immutable ancestry, never projected metadata.'}
    metadata['classicTraceSourcePolicy']=copy.deepcopy(POLICY['classicTraceSourcePolicy'])
    metadata['classicStreamsPolicy']={
      'version':POLICY['classicPolicyVersion'],'enabled':metadata['classicStreamsEnabled'],'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),
      'parentRecipeSha256':POLICY['parentRecipeSha256'],'parentSourceManifestCanonicalSha256':POLICY['parentNativeManifestCanonicalSha256'],
      'nativePatchSha256':POLICY['nativePatchSha256'],'addedSourcePaths':POLICY['classicAddedSourcePaths'],
      'actualPrivateTargetCompileCommands':private,'actualRegistrationCompileCommands':metadata['actualRegistrationCompileCommands'],
      'requestedCMake':choice,'observedCMake':choice,'addsExternalCapabilities':False,'publicProcessModule':False,
      'moduleManifest':POLICY['classicManifest'],'apiScope':'Large captured guest JS state machines over existing native byte primitives; partial Node22 contract; no performance claim.'}
    metadata['componentizeJsPatches'].append({'name':ANCESTOR['version']+'-boundary','baseRevision':metadata['componentizeJsRevision'],
       'path':str(ANCESTOR_ROOT.parent/'taskqueue-owner-v2/componentize-taskqueue-ticks.UNAPPLIED.patch'),
       'sha256':POLICY['embedding']['patchSha256'],'applied':True,'files':['embedding/embedding.cpp']})
    zlib=metadata['zlibEnabled'];assert type(zlib)is bool
    for field in ['requestedCMakeOptions','observedCMakeOptions']:assert metadata[field]['NODE_COMPAT_ZLIB']==('ON'if zlib else'OFF')
    metadata['zlibSourcePolicy']=copy.deepcopy(POLICY['zlibSourcePolicy'])
    metadata['zlibPolicy']={'version':'sm-bounded-zlib-install-v1','enabled':zlib,'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),
      'moduleManifest':POLICY['zlibManifest'],'moduleManifestSha256':POLICY['zlibManifestSha256'],'requiredHostInterfaces':[],
      'actualKernelCompileCommands':[row['command']for row in entries if row['file']==str(Path(repo)/'builtins/node-compat/zlib/kernel.cpp')],
      'runtimeBackendProof':{'verified':False,'version':None,'vernum':None}}
    consumers=metadata['streamConsumersEnabled'];assert type(consumers)is bool
    for field in ['requestedCMakeOptions','observedCMakeOptions']:
        assert metadata[field]['NODE_COMPAT_STREAM_CONSUMERS']==('ON'if consumers else'OFF')
        assert metadata[field]['ENABLE_BUILTIN_WEB_TEXT_CODEC']=='ON'
    cache=Path(metadata['cmakeCachePath']);values={line.split(':',1)[0]:line.split('=',1)[1]for line in cache.read_text().splitlines()if ':'in line and '='in line}
    install=Path(values['INSTALL_BUILTINS']);install_text=install.read_text()
    decoder_ns='NS_DEF(builtins::web::text_codec)';node_ns='NS_DEF(builtins::node_compat)'
    assert values['ENABLE_BUILTIN_WEB_TEXT_CODEC']=='ON'and install_text.count(decoder_ns)==install_text.count(node_ns)==1
    assert install_text.index(decoder_ns)<install_text.index(node_ns),'Actual builtin installation must precede consumer dependency capture'
    metadata['streamConsumersSourcePolicy']=copy.deepcopy(POLICY['streamConsumersSourcePolicy'])
    metadata['streamConsumersPolicy']={'version':'sm-stream-consumers-text-json-install-v1','enabled':consumers,'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),'moduleManifest':POLICY['streamConsumersSourcePolicy']['moduleManifest'],'moduleManifestSha256':POLICY['streamConsumersSourcePolicy']['moduleManifestSha256'],'requiredHostInterfaces':[],'nativeTextDecoderSource':POLICY['streamConsumersSourcePolicy']['nativeTextDecoderSource'],'prerequisiteCMakeOptions':{'ENABLE_BUILTIN_WEB_TEXT_CODEC':'ON'},'actualPrivateTargetCompileCommands':private,'actualRegistrationCompileCommands':metadata['actualRegistrationCompileCommands'],'installationOrder':{'path':str(install),'sha256':digest(install),'decoderNamespace':decoder_ns,'nodeNamespace':node_ns,'decoderBeforeNode':True},'aliasRegistrationTransactional':False,'startupFailurePolicy':'Abort initialization and discard incomplete instance; no reset/reuse rollback claim.'}
    assert values['ENABLE_BUILTIN_WEB_CRYPTO']=='ON', 'Actual existing WebCrypto builtin required'
    crypto_namespace='NS_DEF(builtins::web::crypto)'
    assert install_text.count(crypto_namespace)==1, 'Actual generated crypto installation required'
    crypto_changed=[row['command']for row in entries if row['file']in[str(Path(repo)/item['path'])for item in POLICY['cryptoKeyOwnershipSourcePolicy']['changes']if item['path'].endswith('.cpp')]]
    assert len(crypto_changed)==3
    metadata['cryptoKeyOwnershipBuildEvidence']={'cryptoBuiltinEnabled':True,'cachePath':str(cache),'cacheSha256':digest(cache),'installationSource':{'path':str(install),'sha256':digest(install),'namespace':crypto_namespace,'count':1},'changedNativeCompileCommands':crypto_changed}
    metadata['cryptoKeyOwnershipPolicy']=copy.deepcopy(POLICY['cryptoKeyOwnershipSourcePolicy'])
    metadata['cryptoSecretFailureSourcePolicy']=copy.deepcopy(POLICY['cryptoSecretFailureSourcePolicy'])
    secret_cpp=[str(Path(repo)/r['path'])for r in POLICY['cryptoSecretFailureSourcePolicy']['changes']if r['path'].endswith('.cpp')]
    secret_commands=[r['command']for r in entries if r['file']in secret_cpp]
    assert len(secret_commands)==2
    metadata['cryptoSecretFailureBuildEvidence']={'version':'sm-webcrypto-secret-failure-build-evidence-v1','cryptoBuiltinEnabled':True,'changedNativeCompileCommands':secret_commands,'currentSourceManifestValidated':True,'faultInjectionObserved':False,'runtimeValidation':None}
    assert Path(repo).resolve()==Path(POLICY['contexts']['configuredSourceRoot'])
    database=list(entries)
    assert len(database)==len({r['file']for r in database})==69
    source_prefix=str(Path(repo))+'/'
    generated=[r['command']for r in database if r['file']==str(cache.parent/'starling-raw.wasm/null.cpp')]
    other=[r['command']for r in database if r['file'].startswith(source_prefix)and not r['file'].startswith((source_prefix+'builtins/',source_prefix+'runtime/'))]
    assert len(native)==63 and len(other)==5 and len(generated)==1 and len(private)==7
    assert values['ENABLE_BUILTIN_WEB_TIMERS']=='ON'
    assert install_text.count('NS_DEF(builtins::web::timers)')==1
    commands={r['file']:r['command']for r in database}
    assert str(Path(repo)/'host-apis/wasi-0.2.0/host_api.cpp')in commands
    selection_commands=task_selection_commands(database,repo,metadata)
    metadata['resourceOwnershipPolicy']={'sourcePolicy':copy.deepcopy(POLICY['resourceOwnershipSourcePolicy']),'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),'timerInstallation':{'path':str(install),'sha256':digest(install),'webTimersEnabled':'ON'},'nativeRuntimeValidation':None,'fullResetOrReuse':False}
    metadata['taskSelectionPolicy']={'sourcePolicy':copy.deepcopy(POLICY['taskSelectionSourcePolicy']),'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),'actualHostApiCompileCommands':[selection_commands['host-apis/wasi-0.2.0/host_api.cpp']],'actualEventLoopCompileCommands':[selection_commands['runtime/event_loop.cpp']],'allNativeDependentsRequireRebuild':True,'nativeAllInvalidRuntimeValidation':None,'fullResetOrReuse':False}
    metadata['zlibErrorSemanticsPolicy']={'sourcePolicy':copy.deepcopy(POLICY['zlibErrorSemanticsSourcePolicy']),'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),'remainingRecordedDifferences':15,'remainingDeviationsApproved':False,'runtimeValidation':None}
    manifest_values=[json.loads((Path(repo)/r['path']).read_bytes())for r in metadata['selectedModuleManifests']]
    assert metadata['selectedModuleManifests']==POLICY['selectedModuleManifests']and manifest_values==POLICY['selectedManifestValues']
    artifact_name=Path(metadata['enginePath']).name.removesuffix('.wasm')
    fresh_path=Path(POLICY['contexts']['workRoot'])/('fresh-abi-'+artifact_name+'.json')
    fresh=json.loads(fresh_path.read_bytes())
    assert fresh['state']=='ACTUAL_FRESH_HASH_HMAC357_ABI_PRECONFIGURE_PATH_OBSERVATION_V1'
    assert fresh['configuredSourceRoot']==str(Path(repo))and fresh['workRoot']==POLICY['contexts']['workRoot']
    assert fresh['sourceDirExisted']is fresh['buildDirExisted']is fresh['artifactExisted']is False
    assert fresh['sourceDir']==str(Path(source_dir))and fresh['buildDir']==str(cache.parent)and fresh['artifact']==metadata['enginePath']
    for key in('CMAKE_C_COMPILER_LAUNCHER','CMAKE_CXX_COMPILER_LAUNCHER'):assert values[key]==''
    for command in metadata['generatedRustProject']['actualCargoBuildCommands']:
        words=shlex.split(command);assert words.count('--target-dir')==1
        assert Path(words[words.index('--target-dir')+1]).resolve()==(cache.parent/'cargo/build').resolve()
        assert '--locked'in words
    assert fresh['compilerLauncherReuseAllowed']is False and fresh['rustIncrementalReuseAllowed']is False
    metadata['combinedNativeSourcePolicy']={'sourcePolicy':copy.deepcopy(POLICY['combinedSourcePolicy']),'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),'configuredSourceRoot':str(Path(repo)),'workRoot':POLICY['contexts']['workRoot'],'externalConfiguredSourceRoot':str(Path(source_dir)),'selectedManifests':manifest_values,'sourceManifestCheckedBeforeAndAfterBuild':metadata['sourceInputsCapturedBeforeBuild']and metadata['buildRecipeCheckedBeforeAndAfterBuild'],'actualCompileDatabaseRows':69,'actualPolicyCppCompileCommands':native,'actualOtherConfiguredCompileCommands':other,'actualGeneratedNullCompileCommands':generated,'actualSeparateEmbeddingCompileCommands':embedding_commands,'freshAbiEvidence':fresh,'freshAbiEvidenceFile':{'path':str(fresh_path),'sha256':digest(fresh_path)},'privateBackendEvidenceHookEnabled':False,'runtimeValidation':None,'operationalAdmission':False}
    metadata['nodeCryptoHashHmacPolicy']=HASH_MODEL.observe_hash_hmac(
        metadata,POLICY,repo,entries,embedding_commands,install_text,
        dict(path=str(install),sha256=digest(install),bytes=install.stat().st_size),
        manifest_values,ninja_capture,ninja_text)
    authenticate_inputs()
    assert digest(model_path)==POLICY['hashHmacModelSha256']
    return metadata



if __name__=='__main__':
    assert len(sys.argv)==2
    validate_sources(sys.argv[1])
    print('Exact new357 Hash/Hmac initial normal-OFF source policy verified; no compiler or guest ran')
