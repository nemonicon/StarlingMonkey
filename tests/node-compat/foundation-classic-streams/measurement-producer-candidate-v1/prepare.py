"""Derive source files only. No configure, compiler, launcher or guest."""
from pathlib import Path
import hashlib,json,difflib
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
PARENT=HERE.parent/'integration-candidate-v1'
EXTENSION=HERE.parent/'measurement-extension-candidate-v1'
PARENT_RECIPE='71b48d2e70c5e003fcbcce7620366744c089dd55036036e52926224dfa2614f7'
EXTENSION_INDEX='69d61ebd61a93d5c34f56b4c4d2fd5d0988b07495ce5636df102a543a036d0aa'
def sha(data):return hashlib.sha256(data).hexdigest()
def put(name,data):
    path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb')as stream:stream.write(data)
def main():
    assert sha((EXTENSION/'index.json').read_bytes())==EXTENSION_INDEX
    for row in json.loads((EXTENSION/'index.json').read_bytes())['files']:
        assert sha((EXTENSION/row['path']).read_bytes())==row['sha256']
    for name in ('artifact_common.py','build-one.py','tool-pins.json'):
        put('ancestry/'+name,(PARENT/'artifact-tools'/name).read_bytes())
    put('admission-pins.json',(PARENT/'admission-pins.json').read_bytes())
    original=(REPO/'tests/node-compat/build-engine.sh').read_text();assert sha(original.encode())==PARENT_RECIPE
    put('before/build-engine.sh',original.encode())
    source=original;edits=[]
    def replace(old,new,count=1):
        nonlocal source
        assert source.count(old)==count,(old,source.count(old))
        source=source.replace(old,new);edits.append({'old':old,'new':new,'count':count})
    replace('repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"',
        'packet_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"\nrepo_root="$(cd "$packet_root/../../../.." && pwd -P)"\n'+
        '[[ $# == 1 ]] || { echo "Need exact reviewed source packet index SHA" >&2; exit 1; }\n'+
        'python3 "$packet_root/verify-packet.py" "$1"\n'+
        'benchmark_root="$repo_root/tests/node-compat/foundation-classic-streams/measurement-extension-candidate-v1"')
    replace('layer_root="$repo_root/tests/node-compat/foundation-classic-streams/integration-candidate-v1"',
        '[[ "$build_type" == Release && "$stress" == 0 && "$oom" == 0 && "$entropy_mode" == OFF && "$build_jobs" == 1 && -z "$artifact_tag" ]] || { echo "Benchmark requires Release/OFF/no stress/one job/empty tag" >&2; exit 1; }\n'+
        'for value in "$ticks_enabled" "$path_enabled" "$events_enabled" "$string_decoder_enabled" "$assert_enabled" "$querystring_enabled" "$util_enabled" "$stream_web_enabled"; do\n'+
        '  [[ "$value" == 1 ]] || { echo "Benchmark requires every shared prerequisite" >&2; exit 1; }\ndone\n'+
        'layer_root="$repo_root/tests/node-compat/foundation-classic-streams/integration-candidate-v1"')
    replace('policy_suffix="$policy_suffix.private-ticks-v1-$ticks_enabled.classic-v1-$classic_enabled"',
        'policy_suffix="$policy_suffix.private-ticks-v1-$ticks_enabled.classic-v1-$classic_enabled.classic-bench-v1"')
    boundary='[[ "$(sha256_file "$source_dir/embedding/embedding.cpp")" == 9dcb63beaf55ff6af9ca4d2019316d4a167657c02ed76a1bf246012da0bcd205 ]] || { echo \'Private tick boundary source mismatch\' >&2; exit 1; }'
    replace(boundary,boundary+'\npython3 "$packet_root/benchmark-policy.py" external "$source_dir"')
    replace('artifact_name="$artifact_name.classic-v1.$entropy_mode.p$path_enabled.e$events_enabled.d$string_decoder_enabled.a$assert_enabled.q$querystring_enabled.u$util_enabled.w$stream_web_enabled.t$ticks_enabled.c$classic_enabled"',
        'artifact_name="sm-classic-bench-v1.c$classic_enabled"')
    replace('sha256_file "$repo_root/tests/node-compat/build-engine.sh" > "$recipe_before"',
        'sha256_file "$packet_root/build-classic-benchmark-engine.sh" > "$recipe_before"\n'+
        'addon_manifest="$work_root/benchmark-inputs-$artifact_name.json"\n'+
        'python3 "$packet_root/benchmark-policy.py" capture "$addon_manifest"')
    replace('  -DCMAKE_BUILD_TYPE="$build_type" -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DWEVAL=OFF -DUSE_WASM_OPT=ON \\',
        '  -DCMAKE_BUILD_TYPE="$build_type" -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DWEVAL=OFF -DUSE_WASM_OPT=ON \\\n'+
        '  -DCMAKE_EXE_LINKER_FLAGS="" -DCMAKE_PROJECT_ComponentizeJS_INCLUDE="$benchmark_root/benchmark.cmake" -DENABLE_BUILTIN_DIAGNOSTICS_CLASSIC_BENCHMARK=ON \\')
    replace('# Ninja does not provide Make\'s jobserver to the OpenSSL external project.',
        'python3 "$packet_root/benchmark-policy.py" before "$build_dir" "$artifact" "$addon_manifest"\n'+
        '# Ninja does not provide Make\'s jobserver to the OpenSSL external project.')
    replace('  2>&1 | tee "$work_root/build-$artifact_name.log"',
        '  2>&1 | tee "$work_root/build-$artifact_name.log"\npython3 "$packet_root/verify-packet.py" "$1"')
    replace('"$classic_enabled" <<\'PY\'', '"$classic_enabled" "$packet_root" <<\'PY\'')
    replace('stream_web_enabled, ticks_enabled, classic_enabled = sys.argv[1:]', 'stream_web_enabled, ticks_enabled, classic_enabled, packet_root = sys.argv[1:]')
    replace("assert digest(pathlib.Path(repo)/'tests/node-compat/build-engine.sh') == pathlib.Path(recipe_before).read_text().strip()", "assert digest(pathlib.Path(packet_root)/'build-classic-benchmark-engine.sh') == pathlib.Path(recipe_before).read_text().strip()")
    replace("    if line.startswith('CMAKE_PROJECT_ComponentizeJS_INCLUDE:'): assert line.partition('=')[2] == '', 'No diagnostic CMake extension'", "    if line.startswith('CMAKE_PROJECT_ComponentizeJS_INCLUDE:'): assert line.partition('=')[2] == str(pathlib.Path(repo)/'tests/node-compat/foundation-classic-streams/measurement-extension-candidate-v1/benchmark.cmake'), 'Exact benchmark include only'")
    replace("    'buildRecipeSha256': digest(pathlib.Path(repo) / 'tests/node-compat/build-engine.sh'),", "    'buildRecipeSha256': digest(pathlib.Path(packet_root) / 'build-classic-benchmark-engine.sh'),")
    replace("with open(artifact + '.build.json', 'w') as output:",
        "benchmark_spec = importlib.util.spec_from_file_location('classic_benchmark_build_policy',pathlib.Path(packet_root)/'benchmark-policy.py')\n"+
        "benchmark = importlib.util.module_from_spec(benchmark_spec);benchmark_spec.loader.exec_module(benchmark)\n"+
        "metadata = benchmark.decorate(metadata, pathlib.Path(artifact))\n\n"+
        "with open(artifact + '.build.json', 'x') as output:")
    restored=source
    for edit in reversed(edits):
        assert restored.count(edit['new'])==edit['count'];restored=restored.replace(edit['new'],edit['old'])
    assert restored==original
    put('build-classic-benchmark-engine.sh',source.encode())
    put('producer.UNAPPLIED.patch',''.join(difflib.unified_diff(original.splitlines(True),source.splitlines(True),fromfile='a/tests/node-compat/build-engine.sh',tofile='b/measurement-producer-candidate-v1/build-classic-benchmark-engine.sh')).encode())
    put('producer-transformations.json',(json.dumps({'schemaVersion':1,'parentRecipeSha256':PARENT_RECIPE,'afterRecipeSha256':sha(source.encode()),'edits':edits,'exactReverseProof':True,'producerInvoked':False},indent=2)+'\n').encode())
    metadata=json.loads(Path('/tmp/starling-node-compat/production-classic-artifacts-v1/native-freeze/normal-off.engine.wasm.build.json').read_bytes())
    static={}
    for field in ('strictEventExceptionPolicy','protectedAbortListenerPolicy','internalTickPolicy','classicStreamsPolicy'):
        static[field]={key:value for key,value in metadata[field].items() if not key.startswith('actual') and key not in ('enabled','requestedCMake','observedCMake')}
    put('parent-policy-values.json',(json.dumps(static,indent=2)+'\n').encode())
    contract={'schemaVersion':1,'state':'CLASSIC_BENCHMARK_DIAGNOSTIC_SOURCE_CONTRACT_NO_REVIEWED_ARTIFACTS',
      'recipeSha256':sha(source.encode()),'parentRecipeSha256':PARENT_RECIPE,'sourcePolicySha256':'137a35959131d5cb5125bb5fc97324dfa4ba2ce18441818dd95cf83d19c88d6f',
      'sourceHelperSha256':'f4a303250ac979206f0c2b358f4dd16d2a5e3a3e3007200901dedba8576b9a1e','extensionIndexSha256':EXTENSION_INDEX,
      'nativeSources':342,'addonSources':[{'path':str((EXTENSION/name).relative_to(REPO)),'sha256':sha((EXTENSION/name).read_bytes())} for name in ('benchmark-extension.cpp','benchmark.cmake')],
      'declaredNativeAndBuildInputs':344,'externalEmbeddingInputs':3,'moduleId':'starling:test-classic-benchmark','exports':['default','nextTick'],
      'externalSources':metadata['componentizeSourceManifest'],
      'target':'builtin_diagnostics_classic_benchmark','namespace':'diagnostics::classic_benchmark','diagnosticVersion':'sm-classic-benchmark-diagnostic-v1',
      'linkerFlags':'','parentPolicyValuesSha256':sha((json.dumps(static,indent=2)+'\n').encode()),'reviewedEnginePins':None,
      'freezeRoot':'/tmp/starling-node-compat/classic-benchmark-artifacts-v1/native-freeze','labels':['benchmark-classic-on','benchmark-classic-off']}
    put('contract.json',(json.dumps(contract,indent=2)+'\n').encode())
    print(json.dumps({'recipeSha256':contract['recipeSha256'],'edits':len(edits)}))
if __name__=='__main__':main()
