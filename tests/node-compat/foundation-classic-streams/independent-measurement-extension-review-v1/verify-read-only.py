#!/usr/bin/env python3
"""Independent source/hash review. Does not import or execute reviewed code.

The separately captured compiler run is -fsyntax-only with dependency text only;
this reader does not rerun it and no native producer/configure/link is invoked.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shlex
import stat
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'measurement-extension-candidate-v1'
REPO=HERE.parents[3]
INDEX='69d61ebd61a93d5c34f56b4c4d2fd5d0988b07495ce5636df102a543a036d0aa'
PINS='c998dce40ff66a1764ad8c44f8a492b830d40bb6dce958aab711ecf3c5bcbf3e'
ROOT='1df0d5bcbb4792efa9fe7329b164aede3a2da7bc4dec6c90d011972cfb6d7f56'
RECIPE='71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'
checks={}
def digest(data):return hashlib.sha256(data).hexdigest()
def regular(path,expected=None,size=None):
    path=Path(os.path.abspath(path));before=path.lstat();assert stat.S_ISREG(before.st_mode),path
    h=hashlib.sha256()
    with path.open('rb')as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    after=path.lstat();assert(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),path
    row={'path':str(path),'sha256':h.hexdigest(),'bytes':before.st_size}
    assert expected is None or row['sha256']==expected,path
    assert size is None or row['bytes']==size,path
    if str(path)in checks:assert checks[str(path)]==row
    checks[str(path)]=row;return row
def document(path,expected=None):
    row=regular(path,expected);b=Path(path).read_bytes();assert digest(b)==row['sha256'];return json.loads(b)
def text(path):regular(path);return Path(path).read_text()
def main():
    index=document(BASE/'index.json',INDEX)
    assert index['state']=='SOURCE_ONLY_CLASSIC_BENCHMARK_EXTENSION_PROPOSAL_SEALED'and index['runtimeAcceptanceClaim']is False
    indexed={r['path']:r for r in index['files']};assert len(indexed)==len(index['files'])==13
    assert {p.name for p in BASE.iterdir()if p.is_file()}==set(indexed)|{'index.json'}
    assert not any(p.is_symlink()for p in BASE.rglob('*'))
    for name,row in indexed.items():
        assert not Path(name).is_absolute()and '..'not in Path(name).parts
        regular(BASE/name,row['sha256'],row['bytes'])
    receipt=document(BASE/'source-review.json',indexed['source-review.json']['sha256'])
    freeze=document(BASE/'input-freeze.json',receipt['inputFreezeSha256'])
    rows={}
    for row in freeze['inputs']:
        path=Path(row['path']);assert path.is_absolute()and path not in rows;rows[path]=row
        regular(path,row['sha256'],row['bytes'])
    assert len(rows)==receipt['inputFiles']==401
    native=[r for r in freeze['inputs']if r['role']=='current-production-native342'];assert len(native)==342
    policy=document(BASE.parent/'integration-candidate-v1/policy.json','137a35959131d5cb5125bb5fc97324dfa4ba2ce18441818dd95cf83d19c88d6f')
    assert {Path(r['path']):(r['sha256'],r['bytes'])for r in native}=={
        REPO/r['path']:(r['sha256'],(REPO/r['path']).stat().st_size)for r in policy['expectedNativeSourceManifest']}
    design=BASE.parent/'measurement-design-v2'
    design_index=document(design/'index.json','23d0c5514534727fc692427018c2928680bd8478d4e34c714fa0ebc303ce2043')
    for row in design_index['files']:regular(design/row['path'],row['sha256'],row['bytes'])
    assert receipt['currentNativeInputsVerified']==342 and receipt['proposedDeclaredNativeAndBuildInputs']==344
    assert receipt['externalEmbeddingInputsRemainSeparate']==3 and receipt['parentProductionRecipeSha256']==RECIPE
    for row in receipt['proposedAdditionalSourceInputs']:regular(REPO/row['path'],row['sha256'])
    for field in ['producerImplemented','freezerImplemented','workloadsImplemented','nodeOracleExecuted','compilerExecuted',
                  'guestOrTargetHostExecuted','benchmarkExecuted','productionPinsModified','productionSelectorsModified','runtimeAcceptanceClaim']:
        assert receipt[field]is False
    pins_path=BASE.parent/'production-adoption-v1/reviewed-runtime-pins-v1.json'
    pins=document(pins_path,PINS)
    authority=document(BASE.parent/'production-adoption-v1/root-pin-review-receipt.json',ROOT)
    production=[]
    for label,pin in pins['variants'].items():
        for field in ['engineSha256','engineBytes','receiptSha256','freezeReceiptSha256']:
            assert pin[field]==authority['variants'][label][field]
        production.append(regular(pin['enginePath'],pin['engineSha256'],pin['engineBytes']))
        regular(pin['enginePath']+'.build.json',pin['receiptSha256'])
    cpp=text(BASE/'benchmark-extension.cpp');code=re.sub(r'//[^\n]*','',cpp)
    assert code.count('define_builtin_module(')==1 and code.count('create_internal_next_tick(')==1
    assert '"starling:test-classic-benchmark"'in code
    assert code.index('JSAutoRealm realm(cx, engine->global());')<code.index('JS_NewPlainObject')
    assert code.index('JS::RootedObject record')<code.index('if (!record) return false;')<code.index('create_internal_next_tick')
    assert code.index('JS::RootedObject next_tick')<code.index('if (!next_tick) return false;')<code.index('JS_DefineProperty')
    assert code.count('JSPROP_ENUMERATE')==2 and 'JS::RootedValue module(cx, JS::ObjectValue(*record));'in code
    assert not any(x in code for x in ['PersistentRooted','AsyncTask','JS_GC','malloc(','new ','reset(','chrono','queueMicrotask','process'])
    event=text(REPO/'runtime/event_loop.cpp');queue=text(REPO/'runtime/node_tick_queue.cpp');queue_header=text(REPO/'runtime/node_tick_queue.h')
    assert 'static PersistentRooted<TaskQueue> queue;'in event and 'ticks.trace(trc);'in event
    assert 'return queue.get().ticks.enqueue(cx, JS::CallArgsFromVp(argc, vp));'in event
    assert 'JS::RootedFunction function(cx, JS_NewFunction(cx, enqueue_internal_tick, 1, 0, "nextTick"));'in event
    assert 'TraceEdge(trc, &callback,'in queue and 'TraceEdge(trc, &arguments,'in queue
    assert 'RootedObject callback(cx, tick.callback), arguments(cx, tick.arguments);'in queue
    assert queue.index('RootedObject callback(cx, tick.callback), arguments(cx, tick.arguments);')<queue.index('tick.callback = nullptr; tick.arguments = nullptr; tick.argc = 0;',queue.index('bool InternalTickQueue::drain_ticks'))
    assert all(value in queue_header for value in ['MaxPending = 4096','MaxArgumentsPerTick = 1024','MaxPendingArguments = 65536','MaxCallbacksPerCheckpoint = 65536'])
    loader=text(REPO/'runtime/script_loader.cpp');engine=text(REPO/'runtime/engine.cpp');api=text(REPO/'include/extension-api.h')
    assert 'JS::PersistentRootedObject builtinModules;'in loader and 'builtinModules.init(cx, JS::NewMapObject(cx));'in loader
    assert 'MapSet(cx, builtinModules, id_val, builtin)'in loader
    assert 'bool define_builtin_module(const char *id, HandleValue builtin);'in api
    assert engine.index('scriptLoader = new ScriptLoader')<engine.index('core::EventLoop::init(cx());')<engine.index('if (!install_builtins(this))')
    cmake=text(BASE/'benchmark.cmake');add=text(REPO/'cmake/add_builtin.cmake')
    assert 'option(ENABLE_BUILTIN_DIAGNOSTICS_CLASSIC_BENCHMARK 'in cmake and ' OFF)'in cmake
    assert 'if(NOT NODE_COMPAT_INTERNAL_TICKS)'in cmake
    assert 'NOT TARGET builtin_node_compat OR NOT NODE_COMPAT_EVENTS OR NOT NODE_COMPAT_STRING_DECODER'in cmake
    assert 'add_builtin(diagnostics::classic_benchmark DISABLED_BY_DEFAULT'in cmake
    assert 'DEPENDENCIES builtin_node_compat)'in cmake and 'NODE_COMPAT_CLASSIC_STREAMS'not in cmake
    assert 'file(APPEND $CACHE{INSTALL_BUILTINS} "NS_DEF(${NS})\\n")'in add
    external_cmake=text(Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze/componentize-source/CMakeLists.txt'))
    assert external_cmake.index('include("${STARLINGMONKEY_SRC}/cmake/add_as_subproject.cmake")')<external_cmake.index('add_builtin(componentize::embedding')<external_cmake.index('project(ComponentizeJS)')
    hook=document(HERE/'cmake-hook-help.json');assert hook['exitCode']==0
    help_text=text(HERE/'cmake-hook-help.stdout.txt');assert 'included as the last step'in help_text
    assert digest(help_text.encode())==hook['stdoutSha256']
    assert text(HERE/'cmake-hook-help.stderr.txt')==''
    production_recipe=text(REPO/'tests/node-compat/build-engine.sh');regular(REPO/'tests/node-compat/build-engine.sh',RECIPE)
    assert 'No diagnostic CMake extension'in production_recipe
    admission=text(REPO/'tests/node-compat/classic-streams-admission.mjs')
    assert "metadata.diagnosticOnly===undefined||metadata.diagnosticOnly===false"in admission
    assert "assert.equal(metadata.buildRecipeSha256,pins.productionRecipeSha256);"in admission
    selection=text(REPO/'tests/node-compat/module-selection.mjs');assert 'const classic = validateClassicSourceAdmission(metadata,'in selection
    future=document(BASE/'future-pins.json');assert len(future['variants'])==2 and all(x is None for x in future['variants'].values())
    for field in ['diagnosticRecipeSha256','nodeOracleSha256','componentArtifacts']:assert future[field]is None
    assert future['reviewRequiredBeforeBuild']is future['reviewRequiredBeforeExecution']is True
    protocol=document(BASE/'measurement-protocol.json')
    assert len(protocol['scenarios'])==7 and protocol['oracleAndCorrectness']['expectedChecksums']is protocol['oracleAndCorrectness']['expectedTraces']is None
    assert protocol['hostSampling']['expectedInterfaceImports']==protocol['hostSampling']['guestClockImports']==[]
    assert protocol['runBounds']['privateQueueCheckpointWorkLimit']==65536
    assert protocol['sameEnginePrimary']['callableIdentityMayDiffer']is True
    reference=text(BASE/'reference-entry.mjs');installed=text(BASE/'native-entry.mjs')
    for source in [reference,installed]:
        assert "from 'starling:test-classic-benchmark'"in source
        assert not any(token in source for token in ['process.','queueMicrotask','setTimeout'])
    assert "from '../../../../builtins/node-compat/classic-streams/classic-streams.mjs'"in reference
    assert 'createClassicStreams({Buffer,events,StringDecoder,nextTick,'in reference
    assert 'export default graph.root.default;'in reference
    assert "from 'node:stream'"in installed and "from 'node:stream/promises'"in installed
    # The captured compiler run only parsed the candidate with actual public
    # interface flags; the .d target label does not represent a produced object.
    syntax=document(HERE/'syntax-results.json');assert syntax['state']=='WASI_SDK_SYNTAX_ONLY_PASS'and syntax['exitCode']==0
    argv=syntax['argv'];assert '-fsyntax-only'in argv and '-c'not in argv and '-o'not in argv
    assert not any(a.startswith(('-DNODE_COMPAT_CLASSIC_STREAMS','-DNODE_COMPAT_GC_STRESS','-DDEBUG','-DNODE_COMPAT_OOM_TESTING'))for a in argv)
    assert '-DNODE_COMPAT_INTERNAL_TICKS=1'in argv and '-DNODE_COMPAT_STRICT_INITIALIZATION=1'in argv
    assert argv[-1]==str(BASE/'benchmark-extension.cpp')
    assert syntax['stdout']==syntax['stderr']==''and syntax['nativeObjectOrLinkProduced']is syntax['targetGuestExecuted']is False
    regular(syntax['sourceCompileCommandEvidence']['path'],syntax['sourceCompileCommandEvidence']['sha256'])
    compiler=Path(argv[0]);compiler_real=compiler.resolve(strict=True);compiler_row=regular(compiler_real)
    cmake_real=Path(hook['argv'][0]).resolve(strict=True);regular(cmake_real)
    depfile=HERE/'syntax-dependencies.d';raw=depfile.read_text();body=raw.replace('\\\n',' ').split(':',1)[1]
    deps=list(dict.fromkeys(shlex.split(body)));assert str(BASE/'benchmark-extension.cpp')in deps
    header_rows=[]
    for path in deps:
        p=Path(path).resolve(strict=True);header_rows.append(regular(p))
    # Recheck candidate/production boundaries after syntax and all source reads.
    for row in freeze['inputs']:regular(row['path'],row['sha256'],row['bytes'])
    regular(BASE/'index.json',INDEX);regular(pins_path,PINS)
    result={'schemaVersion':1,'state':'INDEPENDENT_MEASUREMENT_EXTENSION_SOURCE_REVIEW_PASSED_NOT_NATIVE_APPROVAL',
      'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'candidateIndex':regular(BASE/'index.json',INDEX),
      'indexedFilesRehashed':13,'consumedRowsRehashed':401,'actualNativeSourceRowsRehashed':342,
      'proposedAddonSourceBuildRows':2,'externalEmbeddingPartition':3,
      'syntaxOnly':{'receipt':regular(HERE/'syntax-results.json'),'compiler':compiler_row,'dependencyFilesRehashed':len(deps),'noObjectOrLink':True},
      'cmakeHookHelp':regular(HERE/'cmake-hook-help.json'),'actualProductionPins':regular(pins_path,PINS),'productionEnginesRehashed':production,
      'findings':[
        'Exact current APIs accept the rooted object/value calls. Record and nextTick allocations are checked sequentially in the content realm; the successful module Map retains the record/default self-edge/function graph.',
        'The function calls the existing traced TaskQueue-owned InternalTickQueue; no new static root, queue, AsyncTask, borrowed data, reset hook or host service is introduced. This is source ownership reasoning, not new GC execution evidence.',
        'Actual ComponentizeJS source declares Starling and the embedding before project(ComponentizeJS); installed CMake documents the hook as its last step. add_builtin derives builtin_diagnostics_classic_benchmark and appends its installer after existing prerequisite declarations.',
        'The disabled-by-default CMake option requires native Buffer/Events/StringDecoder/private ticks and permits CLASSIC OFF. The two added source/build inputs are separately declared rather than projected into the actual342 manifest.',
        'Future diagnostic recipe and both engine/component/oracle pins remain null; no producer, freezer, raw diagnostic admission or workload is implemented. Production source/pins never establish that this additional binding exists.',
        'Future artifacts require diagnosticOnly:true plus a new exact recipe and separate namespace/freezer/raw consumer; current production admission rejects diagnosticOnly and any new recipe. These negative tests remain a future producer gate.',
        'The same-engine bounded factory arm shares native dependencies and the existing queue but may use a distinct callable. Whole-profile ON/OFF and stock Jco/provider comparisons remain separate experiments; no timings or advantage are established.'
      ],
      'limitations':['The SDK syntax check parses only; no object, archive, link, CMake configure, installed include, final interface or runtime behavior is proven.',
        'No native producer, package, Node oracle/workload, guest or target host ran. The CMake command only queried installed variable help.',
        'Module install order is supported by current source append order; actual future generated builtins.incl and compile/link commands must be frozen and checked.',
        'The native root/GC/engine ownership argument does not establish isolated moving-GC behavior, safe instance reuse, full Node equivalence, performance or memory advantage.'],
      'nativeProducerApproved':False,'productionPinsReusableForDiagnostic':False,'productionSourceOrPinsChanged':False,
      'compilerSyntaxOnlyExecuted':True,'nativeObjectBuildOrGuestExecuted':False,'runtimeAcceptanceClaim':False,'performanceClaim':False}
    (HERE/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    (HERE/'verified-files.json').write_text(json.dumps({'schemaVersion':1,'files':sorted(checks.values(),key=lambda r:r['path'])},indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['state','indexedFilesRehashed','consumedRowsRehashed','actualNativeSourceRowsRehashed','nativeProducerApproved']}))
if __name__=='__main__':main()
