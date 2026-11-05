"""Exact355 secret-failure source/compile layer; old owner355 is ancestry DATA."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import sys
sys.dont_write_bytecode=True
if not __debug__:raise RuntimeError('Source policy checks require assertions')
HERE=Path(__file__).resolve().parent
POLICY_SHA256='cb35fec0a5628110a046cef0a51ffed058ffd31b2a732d94711fabda08b4a612'
PARENT_POLICY_SHA256='98e80d36b8eb9b7ac99de54832288bd8eec148fa1b9fe0b27b3bada4d12b2cd0'
PARENT_HELPER_SHA256='78521feeefe299360228e5db76bfde0b11e6eeee93bd2374cd39b2fe695b610c'
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert digest(HERE/'policy.json')==POLICY_SHA256
POLICY=json.loads((HERE/'policy.json').read_bytes())

# Exact previous342 source ancestry is data, never an engine metadata adapter.
def verify_consumers_ancestry():
    root=HERE.parents[1]/'foundation-zlib/native-integration-candidate-v4'
    authority=POLICY['streamConsumersSourcePolicy']
    for name,key in [('index.json','parentIndexSha256'),('policy.json','parentPolicySha256'),('layer-policy.py','parentHelperSha256')]:assert digest(root/name)==authority[key]
    for row in json.loads((root/'index.json').read_bytes())['files']:
        path=root/row['path'];assert path.is_file()and not path.is_symlink()and path.stat().st_size==row['bytes']and digest(path)==row['sha256']
    before={row['path']:row['sha256']for row in json.loads((root/'policy.json').read_bytes())['expectedNativeSourceManifest']}
    after={row['path']:row['sha256']for row in json.loads((HERE.parents[1]/'foundation-stream-consumers/native-integration-candidate-v2/policy.json').read_bytes())['expectedNativeSourceManifest']}
    assert len(before)==350 and len(after)==355 and set(after)-set(before)==set(authority['addedSources'])
    assert sum(after[path]==before[path]for path in before)==348
    for row in authority['changes']:assert before[row['path']]==row['beforeSha256']and after[row['path']]==row['afterSha256']
    assert POLICY['zlibSourcePolicy']==json.loads((root/'policy.json').read_bytes())['zlibSourcePolicy']
    return True
def verify_crypto_ancestry():
    parent=HERE.parents[1]/'foundation-stream-consumers/native-integration-candidate-v2'
    crypto=POLICY['cryptoKeyOwnershipSourcePolicy']
    for name,key in [('index.json','parent355ProducerIndexSha256'),('policy.json','parent355PolicySha256'),('layer-policy.py','parent355HelperSha256')]:assert digest(parent/name)==crypto[key]
    before={row['path']:row['sha256']for row in json.loads((parent/'policy.json').read_bytes())['expectedNativeSourceManifest']}
    owner_parent=json.loads((HERE.parent/'native-integration-candidate-v2/policy.json').read_bytes())
    after={row['path']:row['sha256']for row in owner_parent['expectedNativeSourceManifest']}
    assert len(before)==len(after)==355 and set(before)==set(after)
    assert len(crypto['changes'])==5 and sum(before[name]==after[name]for name in before)==350
    for row in crypto['changes']:assert before[row['path']]==row['beforeSha256']and after[row['path']]==row['afterSha256']
    for name,key in [('key-owner-candidate-v1','ownerSourceIndexSha256'),('prototype-key-guard-candidate-v1','prototypeGuardSourceIndexSha256')]:assert digest(HERE.parent/name/'index.json')==crypto[key]
    assert digest(HERE.parent/'prototype-key-guard-candidate-v1/composition.json')==crypto['compositionSha256']
    return True
def verify_secret_failure_ancestry():
    contract=POLICY['cryptoSecretFailureSourcePolicy']
    for role in ['parent355Index','parent355Policy','parent355Helper','parent355Recipe','payloadSourceIndex','payloadSourceContract']:
        row=contract[role]
        relative=Path(row['path']).relative_to(Path('/Users/dan/dev/StarlingMonkey'))
        path=HERE.parents[3]/relative
        assert path.is_file() and not path.is_symlink() and path.stat().st_size==row['bytes'] and digest(path)==row['sha256']
    base=json.loads((HERE.parent/'native-integration-candidate-v2/policy.json').read_bytes())
    payload=json.loads((HERE.parent/'ownership-secret-failure-candidate-v2/source-contract.json').read_bytes())
    before={r['path']:r['sha256']for r in base['expectedNativeSourceManifest']}
    after={r['path']:r['sha256']for r in POLICY['expectedNativeSourceManifest']}
    assert len(before)==len(after)==355 and before.keys()==after.keys()
    assert payload['expectedNativeSourceManifest']==POLICY['expectedNativeSourceManifest']
    assert sum(before[k]==after[k]for k in before)==352 and len(contract['changes'])==3
    assert sorted(k for k in before if before[k]!=after[k])==sorted(r['path']for r in contract['changes'])
    for row in contract['changes']:assert before[row['path']]==row['beforeSha256'] and after[row['path']]==row['afterSha256']
    return True
verify_secret_failure_ancestry()
verify_crypto_ancestry()
verify_consumers_ancestry()
PARENT_ROOT=HERE.parents[1]/'foundation-scheduler/integration-candidate-v1'
assert digest(PARENT_ROOT/'policy.json')==PARENT_POLICY_SHA256
assert digest(PARENT_ROOT/'layer-policy.py')==PARENT_HELPER_SHA256
_spec=importlib.util.spec_from_file_location('classic_source_parent306',PARENT_ROOT/'layer-policy.py')
PARENT=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(PARENT)
assert POLICY['parentExpectedNativeSourceManifest']==PARENT.POLICY['expectedNativeSourceManifest']
def expected(relative,base_expected):
    parent=PARENT.expected(relative,base_expected)
    entry=POLICY['sourceLayer'].get(relative)
    if entry is None:return parent
    assert entry['beforeSha256']==parent,'Immediate306 ancestry mismatch: '+relative
    return entry['afterSha256']
def resolved(mapping):return{path:expected(path,value)for path,value in mapping.items()}
def source_manifest(repo):
    repo=Path(repo);rows=POLICY['expectedNativeSourceManifest']
    assert len(rows)==len({row['path']for row in rows})==355
    for row in rows:
        path=repo
        for part in row['path'].split('/'):
            assert part and part not in('.','..');path/=part;assert not path.is_symlink(),path
        assert path.is_file() and digest(path)==row['sha256'],'Unreviewed355 source: '+row['path']
    return copy.deepcopy(rows)
def validate_sources(repo,manifest=None):
    actual=source_manifest(repo)
    if manifest is not None:
        assert all(set(row)=={'path','sha256'}for row in manifest)
        assert sorted(manifest,key=lambda row:row['path'])==actual
    return True
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
def validate_classic_compilation(entries,embedding,repo,metadata):
    ticks=metadata['internalTicksEnabled'];classic=metadata['classicStreamsEnabled'];web=metadata['streamWebEnabled']
    assert all(type(value)is bool for value in[ticks,classic,web,metadata['eventsEnabled'],metadata['stringDecoderEnabled']])
    assert not(metadata['gcStress'] and metadata['entropyPolicy']=='runtime-only'),'RuntimeOnly+GC is outside this finite producer'
    if classic:assert ticks and metadata['eventsEnabled'] and metadata['stringDecoderEnabled']
    codec_file=HERE.parents[1]/'foundation-zlib/native-integration-candidate-v4/codec-evidence.py';assert digest(codec_file)==POLICY['selectedCodecCompileContract']['codecEvidenceSha256']
    spec=importlib.util.spec_from_file_location('selected_zlib_compile_input',codec_file)
    codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
    selected=metadata['zlibSelectedCodecInput'];codec.selection_contract(selected)
    native,queue=PARENT.validate_compilation([row for row in entries if row['file']!=str(Path(repo)/'builtins/node-compat/zlib/kernel.cpp')],embedding,ticks,repo)
    cpp=[row['path']for row in POLICY['expectedNativeSourceManifest']if row['path'].endswith('.cpp')and row['path'].startswith(('builtins/','runtime/'))]
    active=[name for name in cpp if(ticks or name!='runtime/node_tick_queue.cpp')and(web or name!='builtins/node-compat/stream-web-kernel.cpp')and(metadata['zlibEnabled']or name!='builtins/node-compat/zlib/kernel.cpp')]
    assert len(cpp)==62
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
    assert len(embedding)==1 and len(private)==(5 if web else 4)+int(metadata['zlibEnabled'])
    return [row['command']for row in rows],queue,private
def decorate(metadata,repo,source_dir,entries,embedding_commands,enabled):
    assert metadata['gcStress']is False and metadata['entropyPolicy']=='off','Only initial normal-OFF secret source producer is implemented'
    validate_sources(repo,metadata['sourceManifest'])
    assert type(enabled)is bool and metadata['internalTicksEnabled']is enabled
    choice='ON'if metadata['classicStreamsEnabled']else'OFF'
    for field in['requestedCMakeOptions','observedCMakeOptions']:
        assert metadata[field]['NODE_COMPAT_CLASSIC_STREAMS']==choice
    assert metadata['oomTesting']is False and metadata['observedCMakeOptions']['CMAKE_BUILD_TYPE']=='Release'
    assert digest(Path(source_dir)/'embedding/embedding.cpp')==POLICY['embedding']['afterSha256']
    native,queue,private=validate_classic_compilation(entries,embedding_commands,repo,metadata)
    strict=metadata['strictEventExceptionPolicy'];protected=metadata['protectedAbortListenerPolicy']
    assert strict['version']==PARENT.POLICY['parentStrictPolicyVersion']
    assert protected['version']==PARENT.POLICY['parentProtectedPolicyVersion']
    strict['parentSourcePolicy']={key:copy.deepcopy(strict[key])for key in['version','patchSha256','basePolicy','embeddingBoundaryPatchSha256','nativeSourceSha256']}
    protected['parentSourcePolicy']={key:copy.deepcopy(protected[key])for key in['version','patchSha256','sourceSha256','strictPolicyVersion']}
    strict['version']=POLICY['strictPolicyVersion'];strict['nativeSourceSha256']=resolved(strict['nativeSourceSha256'])
    for name in['runtime/node_tick_queue.cpp','runtime/node_tick_queue.h']:strict['nativeSourceSha256'][name]=PARENT.POLICY['sourceLayer'][name]['afterSha256']
    strict['actualNativeCompileCommands']+=queue
    protected['version']=POLICY['protectedPolicyVersion'];protected['strictPolicyVersion']=strict['version'];protected['sourceSha256']=resolved(protected['sourceSha256'])
    metadata['internalTickPolicy']={
      'version':POLICY['version'],'enabled':enabled,'sourcePolicyInstalled':True,
      'parentRecipeSha256':POLICY['parentRecipeSha256'],'parentNativeManifestCanonicalSha256':POLICY['parentNativeManifestCanonicalSha256'],
      'parentPrivateTickPolicyFileSha256':PARENT_POLICY_SHA256,'parentPrivateTickHelperSha256':PARENT_HELPER_SHA256,
      'sourceLayer':POLICY['sourceLayer'],'nativePatchSha256':POLICY['nativePatchSha256'],
      'embeddingPatchSha256':POLICY['embedding']['patchSha256'],'embeddingBeforeSha256':POLICY['embedding']['beforeSha256'],'embeddingAfterSha256':POLICY['embedding']['afterSha256'],
      'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),
      'actualLayoutCompileCommands':native,'actualQueueCompileCommands':queue,'actualEmbeddingCompileCommands':embedding_commands,
      'requestedCMake':metadata['requestedCMakeOptions']['NODE_COMPAT_INTERNAL_TICKS'],'observedCMake':metadata['observedCMakeOptions']['NODE_COMPAT_INTERNAL_TICKS'],
      'limits':PARENT.POLICY['limits'],'addsExternalCapabilities':False,'publicProcessModule':False,
      'resetSafeReuse':'OPEN; cancellation and teardown not established',
      'scope':'Actual355 source/command observations; parent342/306 are immutable ancestry, never projected metadata.'}
    metadata['classicTraceSourcePolicy']=copy.deepcopy(POLICY['classicTraceSourcePolicy'])
    metadata['classicStreamsPolicy']={
      'version':POLICY['classicPolicyVersion'],'enabled':metadata['classicStreamsEnabled'],'policyFileSha256':POLICY_SHA256,'helperSha256':digest(__file__),
      'parentRecipeSha256':POLICY['parentRecipeSha256'],'parentSourceManifestCanonicalSha256':POLICY['parentNativeManifestCanonicalSha256'],
      'nativePatchSha256':POLICY['nativePatchSha256'],'addedSourcePaths':POLICY['classicAddedSourcePaths'],
      'actualPrivateTargetCompileCommands':private,'actualRegistrationCompileCommands':metadata['actualRegistrationCompileCommands'],
      'requestedCMake':choice,'observedCMake':choice,'addsExternalCapabilities':False,'publicProcessModule':False,
      'moduleManifest':POLICY['classicManifest'],'apiScope':'Large captured guest JS state machines over existing native byte primitives; partial Node22 contract; no performance claim.'}
    metadata['componentizeJsPatches'].append({'name':PARENT.POLICY['version']+'-boundary','baseRevision':metadata['componentizeJsRevision'],
       'path':str(PARENT_ROOT.parent/'taskqueue-owner-v2/componentize-taskqueue-ticks.UNAPPLIED.patch'),
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
    return metadata
if __name__=='__main__':
    assert len(sys.argv)==2;validate_sources(sys.argv[1]);print('Exact355 secret-failure source policy verified; no compiler or guest ran')
