"""Finite diagnostic data/command/freeze checks. Import launches nothing."""
import sys
sys.dont_write_bytecode=True
import hashlib,importlib.util,json,os,re,shlex
from pathlib import Path
from ancestry.artifact_common import (checked,capture_regular,digest,sha,manifest,compile_command,
    embedding_command,checked_below,validate_plan,execute_plan,tool_dependencies)
if not __debug__:raise RuntimeError('Assertions required')
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
CONTRACT=json.loads((HERE/'contract.json').read_bytes())
RECIPE=CONTRACT['recipeSha256']
LABELS=tuple(CONTRACT['labels'])
OUTPUT=Path(CONTRACT['freezeRoot'])
EXTENSION=REPO/'tests/node-compat/foundation-classic-streams/measurement-extension-candidate-v1'
ADAPTER='988224282d03fe0bd3c25b62344aef265b1a8e1f5804bdbc34d6442507fabcc0'
ADAPTER_RELATIVE='host-apis/wasi-0.2.0/preview1-adapter-release/wasi_snapshot_preview1.wasm'
def adapter():
    path=checked_below(REPO,ADAPTER_RELATIVE,ADAPTER);assert path.stat().st_size==53512;return path

def require_source_root(value):
    root=Path(value).absolute()
    assert not root.is_symlink() and root.resolve(strict=True)==REPO,'Explicit SOURCE_ROOT must be the containing corrected checkout'
    layer().validate_sources(root)
    capture_addons();tool_dependencies(root);adapter()
    return root

def validate_external_sources(rows,root=None):
    manifest(rows,3)
    assert sorted(rows,key=lambda row:row['path'])==sorted(CONTRACT['externalSources'],key=lambda row:row['path'])
    if root is not None:
        for row in rows:checked_below(Path(root),row['path'],row['sha256'])
    return rows

def exact_release_command(command):
    words=shlex.split(command)
    assert words.count('-c')==1 and '-fsyntax-only'not in words
    assert '-D'not in words and '-U'not in words
    assert [word for word in words if re.fullmatch('-O(?:[0-9szg]|fast)?',word)]==['-O3']
    assert [word for word in words if word=='-DNDEBUG'or word.startswith('-DNDEBUG=')]==['-DNDEBUG']
    for name in ('DEBUG','NDEBUG','NODE_COMPAT_OOM_TESTING'):
        assert not any(word=='-U'+name or word.startswith('-U'+name+'=')for word in words)
        if name!='NDEBUG':assert not any(word=='-D'+name or word.startswith('-D'+name+'=')for word in words)
    for name in ('NODE_COMPAT_INTERNAL_TICKS','NODE_COMPAT_STRICT_INITIALIZATION','NODE_COMPAT_EVENTS_ADD_ABORT_LISTENER','NODE_COMPAT_ENTROPY_POLICY'):
        assert [word for word in words if word=='-D'+name or word.startswith('-D'+name+'=')]==['-D'+name+'=1']
        assert not any(word=='-U'+name or word.startswith('-U'+name+'=')for word in words)
    return words

def classify(metadata,label):
    assert label in LABELS
    assert type(metadata)is dict
    assert metadata.get('diagnosticOnly')is True,'Must be the distinct benchmark diagnostic receipt'
    assert metadata.get('syntheticMetadataOnly',False)is False,'Synthetic metadata never authorizes artifacts'
    assert metadata.get('buildRecipeSha256')==RECIPE,'Exact new diagnostic recipe required'
    assert metadata.get('classicTraceSourcePolicy')==CONTRACT['classicTraceSourcePolicy'],'Corrected trace-source policy required; old342 cannot be relabelled'
    for field in ('profileEnabled','pathEnabled','eventsEnabled','stringDecoderEnabled','assertEnabled','querystringEnabled','utilEnabled','streamWebEnabled','internalTicksEnabled','strictInitialization','abiFixEnabled','bigIntFixEnabled'):
        assert metadata.get(field)is True,field
    for field in ('gcStress','oomTesting','debuggerEnabled','wptSupportEnabled'):
        assert metadata.get(field)is False,field
    assert metadata.get('entropyPolicy')=='off'
    assert metadata.get('classicStreamsEnabled')is(label=='benchmark-classic-on')
    assert 'internalTickDiagnosticPolicy'not in metadata,'Do not mix scheduler diagnostic namespaces'
    policy=metadata['classicBenchmarkDiagnosticPolicy']
    assert policy['version']==CONTRACT['diagnosticVersion']
    assert policy['moduleId']==CONTRACT['moduleId'] and policy['exports']==CONTRACT['exports']
    assert policy['addonSources']==CONTRACT['addonSources']
    assert policy['nativeInputs']==342 and policy['addonInputs']==2 and policy['totalDeclaredNativeAndBuildInputs']==344
    assert policy['externalEmbeddingInputs']==3 and policy['noPublicProcess']is True
    assert policy['namespace']==CONTRACT['namespace']
    assert policy['linkerFlags']=='' and policy['noGuestExecutionByProducer']is True
    return metadata['classicStreamsEnabled']

def layer():
    root=REPO/'tests/node-compat/foundation-classic-streams/trace-integration-candidate-v1'
    checked(root/'policy.json',CONTRACT['sourcePolicySha256'])
    helper=checked(root/'layer-policy.py',CONTRACT['sourceHelperSha256'])
    spec=importlib.util.spec_from_file_location('benchmark_actual342_source_layer',helper)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def capture_addons():
    rows=manifest(CONTRACT['addonSources'],2)
    for row in rows:checked_below(REPO,row['path'],row['sha256'])
    return rows

def cache_values(data):
    values={}
    for line in data.decode().splitlines():
        key,colon,rest=line.partition(':')
        if colon and '='in rest:values[key]=rest.partition('=')[2]
    return values

def required_cache(classic):
    return {'CMAKE_BUILD_TYPE':'Release','WEVAL':'OFF','USE_WASM_OPT':'ON','CMAKE_EXE_LINKER_FLAGS':'',
      'CMAKE_PROJECT_ComponentizeJS_INCLUDE':str(EXTENSION/'benchmark.cmake'),'ENABLE_BUILTIN_DIAGNOSTICS_CLASSIC_BENCHMARK':'ON',
      'ENABLE_BUILTIN_NODE_COMPAT':'ON','NODE_COMPAT_LOCKED_RUST':'ON','NODE_COMPAT_ENTROPY_MODE':'OFF',
      'NODE_COMPAT_INTERNAL_TICKS':'ON','NODE_COMPAT_CLASSIC_STREAMS':'ON'if classic else'OFF',
      'NODE_COMPAT_GC_STRESS':'OFF','NODE_COMPAT_OOM_TESTING':'OFF','ENABLE_JS_DEBUGGER':'OFF','ENABLE_BUILTIN_WPT_SUPPORT':'OFF',
      **{'NODE_COMPAT_'+key:'ON'for key in ('PATH','EVENTS','STRING_DECODER','ASSERT','QUERYSTRING','UTIL','STREAM_WEB')}}

def validate_link(raw):
    selected=[]
    for line in raw.decode().splitlines():
        words=shlex.split(line)
        if '-o'not in words or 'starling-raw.wasm/starling-raw.wasm'not in words:continue
        assert not any(token in words for token in ('|',';','||')) and '`'not in line and '$('not in line
        segments=[[]]
        for word in words:
            if word=='&&':segments.append([])
            else:segments[-1].append(word)
        assert len(segments)==4 and segments[0]==[':']
        command=segments[1]
        assert Path(command[0]).is_absolute()
        assert command.count('-o')==1 and command[command.index('-o')+1]=='starling-raw.wasm/starling-raw.wasm'
        assert all(flag in command for flag in ('-O3','-DNDEBUG','-flto=thin'))
        assert [flag for flag in command if re.fullmatch('-O[0-9sz]',flag)]==['-O3']
        assert [flag for flag in command if flag.startswith('-flto')]==['-flto=thin']
        assert '-UNDEBUG'not in command and not any(flag.startswith('-DDEBUG')for flag in command)
        assert not any('--threads'in flag or '--thinlto-jobs'in flag for flag in command),'Empty selected EXE flags; no hidden link1 override'
        assert sum(word.endswith('libbuiltin_diagnostics_classic_benchmark.a')for word in command)==1
        assert segments[2][0]=='cd' and len(segments[2])==2
        assert segments[3][1:]==['--strip-debug','-O3','-o','starling-raw.wasm','starling-raw.wasm']
        selected.append({'linkCommand':command,'postLinkWasmOptCommand':segments[3]})
    assert len(selected)==1,'Need exactly one actual final linker/post-opt witness'
    return selected[0]

def validate_observations(metadata,label,cache,db,parent_raw,install,final_raw):
    classic=classify(metadata,label)
    for key,value in required_cache(classic).items():assert cache.get(key)==value,key
    assert cache.get('ENABLE_BUILTIN_DIAGNOSTICS_INTERNAL_TICKS','OFF')=='OFF'
    assert metadata['requestedCMakeOptions']==metadata['observedCMakeOptions']
    for key,value in metadata['observedCMakeOptions'].items():assert cache.get(key)==value,key
    source_layer=layer()
    source_layer.validate_sources(REPO,manifest(metadata['sourceManifest'],342))
    external=validate_external_sources(metadata['componentizeSourceManifest'])
    home=Path(cache['CMAKE_HOME_DIRECTORY'])
    embedding=embedding_command(parent_raw,str(home/'embedding/embedding.cpp'))
    diagnostic=embedding_command(parent_raw,str(EXTENSION/'benchmark-extension.cpp'))
    assert embedding==metadata['actualEmbeddingCompileCommands']
    native,queue,private=source_layer.validate_classic_compilation(db,embedding,REPO,metadata)
    assert len(native)==61 and len(queue)==1 and len(private)==5
    for command in native+embedding+diagnostic:exact_release_command(command)
    assert not any(row['file'].endswith('/embedding/embedding.cpp')or row['file']==str(EXTENSION/'benchmark-extension.cpp')for row in db),'Parent targets are separate Ninja evidence, not native JSON'
    compile_command(diagnostic[0],False,str((EXTENSION/'benchmark-extension.cpp').relative_to(REPO)),classic,False)
    assert private==metadata['classicStreamsPolicy']['actualPrivateTargetCompileCommands']
    assert native==metadata['internalTickPolicy']['actualLayoutCompileCommands']
    assert queue==metadata['internalTickPolicy']['actualQueueCompileCommands']
    strict=[row['command']for row in db if row['file'].endswith(('/runtime/engine.cpp','/runtime/event_loop.cpp','/runtime/node_tick_queue.cpp','/builtins/web/event/event-target.cpp'))]
    assert len(strict)==4 and sorted(strict)==sorted(metadata['strictEventExceptionPolicy']['actualNativeCompileCommands'])
    static=json.loads(checked(HERE/'parent-policy-values.json',CONTRACT['parentPolicyValuesSha256']).read_bytes())
    for field,values in static.items():
        for key,value in values.items():assert metadata[field][key]==value,(field,key)
    for field,enabled in [('internalTickPolicy',True),('classicStreamsPolicy',classic)]:
        assert metadata[field]['enabled']is enabled
        for name in ('requestedCMake','observedCMake'):assert metadata[field][name]==('ON'if enabled else'OFF')
    assert metadata['protectedAbortListenerPolicy']['enabled']is True and metadata['protectedAbortListenerEnabled']is True
    text=install.decode();line='NS_DEF(diagnostics::classic_benchmark)'
    assert text.count(line)==1 and text.count('NS_DEF(builtins::node_compat)')==1
    assert text.index(line)>text.index('NS_DEF(builtins::node_compat)')
    validate_link(final_raw)
    return {'native':native,'queue':queue,'private':private,'strict':strict,'embedding':embedding,'diagnostic':diagnostic}

def verify_frozen(label,root=OUTPUT):
    assert label in LABELS and root==OUTPUT
    receipt_path=root/(label+'-freeze-receipt.json')
    raw,receipt_sha=capture_regular(receipt_path);receipt=json.loads(raw)
    assert receipt['schemaVersion']==1 and receipt['state']=='immutable-classic-trace-benchmark-diagnostic-engine-frozen'
    assert receipt['label']==label and receipt['recipeSha256']==RECIPE
    assert receipt['nativeInputsVerified']==342 and receipt['addonInputsVerified']==2 and receipt['totalDeclaredNativeAndBuildInputs']==344
    assert receipt['externalEmbeddingInputsVerified']==3
    for key,value in {'actualNativeCommands':61,'actualStrictCommands':4,'actualPrivateCommands':5,'actualEmbeddingCommands':1,'actualDiagnosticCommands':1}.items():assert receipt[key]==value
    assert receipt['diagnosticOnly']is True and receipt['productionSelectorRefused']is True
    assert receipt['sourceContractVersion']==CONTRACT['sourceContractVersion']
    assert receipt['classicTraceSourcePolicy']==CONTRACT['classicTraceSourcePolicy']
    metadata=json.loads(checked(root/(label+'.engine.wasm.build.json'),receipt['metadataSha256']).read_bytes())
    classify(metadata,label)
    rows=receipt['copies'];assert len(rows)==len({row['path']for row in rows})
    for row in rows:
        path=Path(row['path']);assert path.is_relative_to(root)
        current=path
        while current!=root:assert not current.is_symlink();current=current.parent
        assert checked(path,row['sha256']).stat().st_size==row['bytes']
    inventory={row['path']:row for row in rows}
    def own(name,expected=None):
        row=inventory[str(root/name)]
        if expected is not None:assert row['sha256']==expected
        return checked(root/name,row['sha256']).read_bytes()
    own(label+'.engine.wasm',metadata['engineSha256']);assert metadata['engineBytes']==receipt['engineBytes']
    for source in manifest(metadata['sourceManifest'],342):own('source/'+source['path'],source['sha256'])
    for source in capture_addons():own('addon/'+source['path'],source['sha256'])
    for source in manifest(metadata['componentizeSourceManifest'],3):own('componentize-source/'+source['path'],source['sha256'])
    own('producer/build-classic-benchmark-engine.sh',RECIPE)
    own('producer/contract.json',sha(HERE/'contract.json'))
    own('producer/index.json',receipt['sourceIndexSha256'])
    assert len(own('tooling/wasi_snapshot_preview1.wasm',ADAPTER))==53512
    assert receipt['toolingAdapter']=={'path':str(root/'tooling/wasi_snapshot_preview1.wasm'),'sha256':ADAPTER,'bytes':53512,'nativeInputCountUnchanged':True}
    adapter()
    expected_tools=tool_dependencies(REPO)
    assert len(receipt['toolDependencyClosure'])==len(expected_tools)
    for row in expected_tools:
        own('tooling/repository/'+row['path'],row['sha256'])
        assert {'path':str(root/'tooling/repository'/row['path']),'sourcePath':row['path'],'sha256':row['sha256'],'bytes':row['bytes']}in receipt['toolDependencyClosure']
    semantic=receipt['semanticSourceProvenance']
    base=root/'tooling/repository/tests/node-compat/foundation-classic-streams/trace-semantics-candidate-v1'
    assert semantic['fixSourceIndexSha256']==CONTRACT['classicTraceSourcePolicy']['fixSourceIndexSha256']
    assert semantic['correctedReceiptAnnotationBase']==str(base)
    assert semantic['primaryPinsPath']==str(base/'primary-source-pins.json') and semantic['nodeMitNoticePath']==str(base/'LICENSE.node')
    assert own(str((base/'primary-source-pins.json').relative_to(root)),semantic['primaryPinsSha256'])
    own(str((base/'LICENSE.node').relative_to(root)),semantic['nodeMitNoticeSha256'])
    primary=json.loads(own(str((base/'primary-source-pins.json').relative_to(root))))
    for row in primary['sources']:
        assert len(own(str((base/row['path']).relative_to(root)),row['sha256']))==row['bytes']
    policy=metadata['classicBenchmarkDiagnosticPolicy'];ev=policy['evidence']
    assert ev['version']=='benchmark-before-after-command-config-v1'and ev['exactBytesUnchanged']is True
    pre=json.loads(own(label+'-witness/before-capture.json',ev['beforeCaptureSha256']))
    assert pre['files']==ev['before']and pre['collectionCommands']==ev['collectionCommands']
    assert len(ev['before'])==len(ev['after'])==8
    names=set()
    for before,after in zip(ev['before'],ev['after']):
        name=before['name'];assert name==after['name']and name not in names;names.add(name)
        assert before['sha256']==after['sha256']and before['bytes']==after['bytes']
        assert own(label+'-witness/before/'+name,before['sha256'])==own(label+'-witness/after/'+name,after['sha256'])
    assert names=={'CMakeCache.txt','compile_commands.json','builtins.incl','parent-targets.commands.txt','parent-targets.commands.txt.stderr','final-link.commands.txt','final-link.commands.txt.stderr','tool-witnesses.json'}
    for name in ('CMakeCache.txt','compile_commands.json','builtins.incl','parent-targets.commands.txt','final-link.commands.txt'):
        assert own(label+'-'+name)==own(label+'-witness/after/'+name)
    assert json.loads(own(label+'-witness/after/tool-witnesses.json'))==receipt['toolWitnesses']
    for index,row in enumerate(receipt['toolWitnesses']):
        if row['frozenCopyRequired']:own(label+'-tools/'+str(index)+'-'+Path(row['resolvedPath']).name,row['sha256'])
    observations=validate_observations(metadata,label,cache_values(own(label+'-CMakeCache.txt',metadata['cmakeCacheSha256'])),
      json.loads(own(label+'-compile_commands.json',metadata['compileCommandsSha256'])),own(label+'-parent-targets.commands.txt'),own(label+'-builtins.incl'),own(label+'-final-link.commands.txt'))
    assert {key:len(observations[key])for key in ('native','strict','embedding','diagnostic')}=={'native':61,'strict':4,'embedding':1,'diagnostic':1}
    assert policy['actualDiagnosticCompileCommands']==observations['diagnostic']and policy['actualEmbeddingCompileCommands']==observations['embedding']
    dependency_hashes={row['sha256']for row in rows}
    rust=metadata['generatedRustProject'];openssl=metadata['openssl']
    for value in (rust['manifestSha256'],rust['lockSha256'],openssl['receiptSha256'],openssl['configureRecipe']['sha256'],openssl['configdata']['sha256'],openssl['completeSourceAudit']['beforeReportSha256'],openssl['library']['sha256']):assert value in dependency_hashes
    assert openssl['completeSourceAudit']['sourceFilesVerified']==4650 and openssl['completeSourceAudit']['beforeAndAfterBuild']is True
    assert rust['cargoBuildLocked']is True and rust['manifestAndLockCheckedBeforeAndAfterBuild']is True
    for row in receipt['licenses']:
        assert row['path']in inventory and inventory[row['path']]['sha256']==row['sha256']
    assert any(row['path'].endswith('/licenses/openssl-LICENSE.txt')for row in receipt['licenses'])
    assert receipt['allInputsValidatedBeforeCopies']is True and receipt['allCopiesAndOriginalsRehashed']is True
    checked(receipt_path,receipt_sha)
    return receipt,metadata,receipt_sha
