"""Read/hash source and write this proposal's receipt only; run no code/tools."""
from pathlib import Path
import hashlib
import json
import re
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
def sha(data):return hashlib.sha256(data).hexdigest()
def put(name,value):
    with (HERE/name).open('x') as stream:json.dump(value,stream,indent=2);stream.write('\n')
def main():
    assert not (HERE/'index.json').exists()
    design=HERE.parent/'measurement-design-v2'
    assert sha((design/'index.json').read_bytes())=='23d0c5514534727fc692427018c2928680bd8478d4e34c714fa0ebc303ce2043'
    inputs={}
    def add(path,role,expected=None):
        path=path.absolute();assert path.is_file() and not path.is_symlink(),path
        data=path.read_bytes();digest=sha(data)
        if expected is not None:assert digest==expected,path
        row={'path':str(path),'sha256':digest,'bytes':len(data),'role':role}
        if str(path) not in inputs:inputs[str(path)]=row
        else:assert inputs[str(path)]['sha256']==digest
        return data
    add(design/'index.json','parent-design-index')
    for row in json.loads((design/'index.json').read_bytes())['files']:add(design/row['path'],'parent-design',row['sha256'])
    policy_path=HERE.parent/'integration-candidate-v1/policy.json'
    policy=json.loads(add(policy_path,'actual342-source-policy','137a35959131d5cb5125bb5fc97324dfa4ba2ce18441818dd95cf83d19c88d6f'))
    assert len(policy['expectedNativeSourceManifest'])==342
    for row in policy['expectedNativeSourceManifest']:add(REPO/row['path'],'current-production-native342',row['sha256'])
    for name in ('cmake/add_builtin.cmake','cmake/add_as_subproject.cmake','include/extension-api.h','runtime/event_loop.cpp','runtime/event_loop.h','runtime/node_tick_queue.cpp','runtime/node_tick_queue.h',
                 'builtins/node-compat/register.cpp','tests/node-compat/classic-streams-admission.mjs'):
        add(REPO/name,'actual-api-or-build-source')
    add(REPO/'tests/node-compat/build-engine.sh','parent-production-recipe','71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7')
    add(Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze/componentize-source/CMakeLists.txt'),'actual-frozen-parent-project-hook')
    add(Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze/normal-off-CMakeCache.txt'),'actual-production-config-reference-only')
    for name in ('diagnostic.cmake','test-extension.cpp'):add(REPO/'tests/node-compat/foundation-scheduler/diagnostic-candidate-v1'/name,'existing-diagnostic-extension-mechanism')
    for name in ('source/tests/node-compat/build-diagnostic-engine.sh','pins.json','link-policy.py','policy.json'):
        add(REPO/'tests/node-compat/foundation-scheduler/diagnostic-producer-v3-link1'/name,'existing-diagnostic-producer-or-link-mechanism')
    root=Path('/tmp/starling-node-compat/native-toolchain-lock/node_modules')
    for relative in ('@bytecodealliance/jco/dist/node-builtins/index.js','@bytecodealliance/jco/dist/node-builtins/stream.js','@bytecodealliance/jco/dist/node-builtins/shared.js',
                     '@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/scheduler.js','@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/core.js',
                     '@bytecodealliance/jco-std/dist/wasi/0.2.x/node/24.x.x/stream/index.js'):
        add(root/relative,'actual-stock-provider-source')
    for row in json.loads((design/'source-review.json').read_bytes())['sourceFiles']:
        add(Path(row['path']),'parent-pinned-provider-source-or-license',row['sha256'])
    for name in ('README.md','producer-plan.md','measurement-protocol.json','benchmark-extension.cpp','benchmark.cmake','native-entry.mjs','reference-entry.mjs','benchmark.wit','future-pins.json','seal-source.py'):
        add(HERE/name,'proposal-source')
    cpp=(HERE/'benchmark-extension.cpp').read_text()
    assert cpp.index('if (!record) return false;')<cpp.index('create_internal_next_tick')
    assert cpp.index('if (!next_tick) return false;')<cpp.index('JS_DefineProperty')
    assert cpp.count('define_builtin_module(')==1
    code=re.sub(r'//[^\n]*','',cpp)
    assert not any(token in code for token in ('PersistentRooted','AsyncTask','JS_GC','reset(', 'chrono'))
    assert 'JSPROP_ENUMERATE' in cpp and 'starling:test-classic-benchmark' in cpp
    for name in ('native-entry.mjs','reference-entry.mjs'):
        source=(HERE/name).read_text();assert 'process.' not in source and 'queueMicrotask' not in source
        assert "from 'starling:test-classic-benchmark'" in source
    pins=json.loads((HERE/'future-pins.json').read_bytes());assert all(value is None for value in pins['variants'].values())
    assert pins['diagnosticRecipeSha256'] is None and pins['componentArtifacts'] is None
    add_on=[{'path':str((HERE/name).relative_to(REPO)),'sha256':sha((HERE/name).read_bytes())} for name in ('benchmark-extension.cpp','benchmark.cmake')]
    put('input-freeze.json',{'schemaVersion':1,'state':'SOURCE_ONLY_CLASSIC_BENCHMARK_PROPOSAL_INPUTS','inputs':sorted(inputs.values(),key=lambda row:row['path'])})
    put('source-review.json',{'schemaVersion':1,'state':'UNAPPLIED_UNCOMPILED_BOUNDED_CLASSIC_BENCHMARK_EXTENSION_PROPOSAL',
        'parentMeasurementDesignIndexSha256':'23d0c5514534727fc692427018c2928680bd8478d4e34c714fa0ebc303ce2043',
        'currentNativeInputsVerified':342,'proposedAdditionalSourceInputs':add_on,'proposedDeclaredNativeAndBuildInputs':344,'externalEmbeddingInputsRemainSeparate':3,
        'parentProductionRecipeSha256':'71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7',
        'proposedModuleId':'starling:test-classic-benchmark','proposedEnumerableExports':['default','nextTick'],
        'sourceOnlyChecks':['source342 actual hashes','parent design index/rows','rooted sequential allocations','one finite module definition','no separate queue/task/root/clock/reset','reference/native private binding import','null future pins'],
        'inputFreezeSha256':sha((HERE/'input-freeze.json').read_bytes()),'inputFiles':len(inputs),
        'producerImplemented':False,'freezerImplemented':False,'workloadsImplemented':False,'nodeOracleExecuted':False,'compilerExecuted':False,'guestOrTargetHostExecuted':False,'benchmarkExecuted':False,
        'productionPinsModified':False,'productionSelectorsModified':False,'measuredAdvantage':None,'runtimeAcceptanceClaim':False})
    files=[{'path':str(path.relative_to(HERE)),'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size} for path in sorted(HERE.iterdir()) if path.is_file()]
    put('index.json',{'schemaVersion':1,'state':'SOURCE_ONLY_CLASSIC_BENCHMARK_EXTENSION_PROPOSAL_SEALED','files':files,'runtimeAcceptanceClaim':False})
    print(json.dumps({'indexSha256':sha((HERE/'index.json').read_bytes()),'files':len(files),'inputs':len(inputs)}))
if __name__=='__main__':main()
