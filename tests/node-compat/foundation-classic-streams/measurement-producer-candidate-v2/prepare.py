"""Source derivation only. No build, configuration, freezer or engine action."""
from pathlib import Path
import difflib
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
OLD = HERE.parent / 'measurement-producer-candidate-v1'
PARENT = HERE.parent / 'trace-integration-candidate-v1'
EXTENSION = HERE.parent / 'measurement-extension-candidate-v1'
PARENT_RECIPE = '3694c88b7d000f27e11ffcac835fe0b205b2075f5b1d8d29c61f5b0038ba1cf3'

def sha(data): return hashlib.sha256(data).hexdigest()
def put(name, data):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream: stream.write(data)
def document(name, value): put(name, (json.dumps(value, indent=2)+'\n').encode())

def main():
    assert sha((OLD/'index.json').read_bytes()) == '35ed348529d3b8c1bfa5d57343b784b3c0b5ee442603e570d72a696e45134ebc'
    for row in json.loads((OLD/'index.json').read_bytes())['files']:
        assert sha((OLD/row['path']).read_bytes()) == row['sha256']
    for name in ['artifact_common.py', 'build-one.py', 'tool-pins.json']:
        put('ancestry/'+name, (PARENT/'artifact-tools'/name).read_bytes())
    for name in ['admission-pins.json', 'policy.json']:
        put(name, (PARENT/name).read_bytes())
    policy = json.loads((PARENT/'policy.json').read_bytes())
    parent_contract = json.loads((PARENT/'contract.json').read_bytes())
    original = (PARENT/'source/tests/node-compat/build-engine.sh').read_text()
    assert sha(original.encode()) == PARENT_RECIPE
    put('before/build-engine.sh', original.encode())
    source, edits = original, []
    def replace(old, new, count=1):
        nonlocal source
        assert source.count(old) == count, (old, source.count(old))
        source = source.replace(old, new)
        edits.append({'old': old, 'new': new, 'count': count})
    # Reapply the already reviewed diagnostic-only mechanics to the actual new
    # production recipe. Changed parent fragments are selected explicitly.
    old_proof = json.loads((OLD/'producer-transformations.json').read_bytes())
    for edit in old_proof['edits']:
        old, new = edit['old'], edit['new']
        old = old.replace('foundation-classic-streams/integration-candidate-v1', 'foundation-classic-streams/trace-integration-candidate-v1')
        new = new.replace('foundation-classic-streams/integration-candidate-v1', 'foundation-classic-streams/trace-integration-candidate-v1')
        if old.startswith('policy_suffix='):
            old = 'policy_suffix="trace-v1.$entropy_mode.p$path_enabled.e$events_enabled.d$string_decoder_enabled.a$assert_enabled.q$querystring_enabled.u$util_enabled.w$stream_web_enabled.t$ticks_enabled.c$classic_enabled"'
            new = old[:-1]+'.classic-bench-trace-v2"'
        if old.startswith('artifact_name='):
            old = 'artifact_name="$artifact_name.trace-v1.$entropy_mode.p$path_enabled.e$events_enabled.d$string_decoder_enabled.a$assert_enabled.q$querystring_enabled.u$util_enabled.w$stream_web_enabled.t$ticks_enabled.c$classic_enabled"'
            new = 'artifact_name="sm-classic-bench-trace-v2.c$classic_enabled"'
        if 'Need exact reviewed source packet index SHA' in new:
            new = new.replace('[[ $# == 1 ]]', '[[ $# == 2 ]]').replace('Need exact reviewed source packet index SHA', 'Need exact packet index SHA and explicit containing corrected SOURCE_ROOT')
            new = new.replace('python3 "$packet_root/verify-packet.py" "$1"', '[[ "$(cd "$2" && pwd -P)" == "$repo_root" ]] || { echo "SOURCE_ROOT must be this containing corrected checkout" >&2; exit 1; }\npython3 "$packet_root/verify-packet.py" "$1" "$repo_root"')
        if 'verify-packet.py' in new and old.startswith('  2>&1'):
            new = new.replace('"$1"', '"$1" "$repo_root"')
        replace(old, new, edit['count'])
    replace('work_root="${NODE_COMPAT_BUILD_ROOT:-/tmp/starling-node-compat/classic-trace-v1-build}"', 'work_root="${NODE_COMPAT_BUILD_ROOT:-/tmp/starling-node-compat/classic-benchmark-trace-v2-build}"')
    reverse = source
    for edit in reversed(edits):
        assert reverse.count(edit['new']) == edit['count']
        reverse = reverse.replace(edit['new'], edit['old'])
    assert reverse == original
    put('build-classic-benchmark-engine.sh', source.encode())
    put('producer.UNAPPLIED.patch', ''.join(difflib.unified_diff(original.splitlines(True), source.splitlines(True), fromfile='a/tests/node-compat/build-engine.sh', tofile='b/measurement-producer-candidate-v2/build-classic-benchmark-engine.sh')).encode())
    document('producer-transformations.json', {'schemaVersion': 1, 'parentRecipeSha256': PARENT_RECIPE, 'afterRecipeSha256': sha(source.encode()), 'edits': edits, 'exactReverseProof': True, 'producerInvoked': False})
    # Expected policy DATA, not a projected engine receipt. Unchanged strict and
    # protected ancestry is preserved; new tick/classic static values are read
    # from the corrected source policy. Actual metadata is freshly decorated
    # by the new production layer during a future real build.
    static = json.loads((OLD/'parent-policy-values.json').read_bytes())
    for field, version in [('internalTickPolicy', policy['version']), ('classicStreamsPolicy', policy['classicPolicyVersion'])]:
        static[field]['version'] = version
        static[field]['policyFileSha256'] = parent_contract['sourcePolicySha256']
        static[field]['helperSha256'] = parent_contract['sourceHelperSha256']
    static['internalTickPolicy']['sourceLayer'] = policy['sourceLayer']
    document('parent-policy-values.json', static)
    contract = json.loads((OLD/'contract.json').read_bytes())
    contract.update({'state': 'CORRECTED_CLASSIC_BENCHMARK_DIAGNOSTIC_SOURCE_NO_REVIEWED_ARTIFACTS', 'recipeSha256': sha(source.encode()), 'parentRecipeSha256': PARENT_RECIPE,
        'sourcePolicySha256': parent_contract['sourcePolicySha256'], 'sourceHelperSha256': parent_contract['sourceHelperSha256'],
        'sourceContractVersion': parent_contract['sourceContractVersion'], 'classicTraceSourcePolicy': policy['classicTraceSourcePolicy'],
        'parentPolicyValuesSha256': sha((HERE/'parent-policy-values.json').read_bytes()),
        'diagnosticVersion': 'sm-classic-benchmark-trace-diagnostic-v2', 'freezeRoot': '/tmp/starling-node-compat/classic-benchmark-trace-v2-artifacts/native-freeze',
        'sourceRootContract': 'Explicit SOURCE_ROOT must equal the containing reviewed corrected checkout; original old342 is refused.',
        'previousProducerIndexSha256': '35ed348529d3b8c1bfa5d57343b784b3c0b5ee442603e570d72a696e45134ebc',
        'productionTraceSourceIndexSha256': sha((PARENT/'index.json').read_bytes())})
    document('contract.json', contract)
    for name in ['benchmark_common.py', 'benchmark-policy.py', 'build-one.py', 'freeze-engine.py', 'verify-frozen.py', 'verify-packet.py', 'export-pin-candidate.py', 'runtime-preflight.mjs', 'metadata-admission.mjs', 'reviewed-pins.json', 'test-source.py', 'test-host.mjs']:
        data = (OLD/name).read_text()
        data = data.replace('classic-benchmark-artifacts-v1', 'classic-benchmark-trace-v2-artifacts').replace('classic-benchmark-diagnostic-v1', 'classic-benchmark-trace-diagnostic-v2')
        data = data.replace('ROOT_REVIEWED_CLASSIC_BENCHMARK_DIAGNOSTIC_FREEZES_V1', 'ROOT_REVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V2')
        data = data.replace('UNREVIEWED_CLASSIC_BENCHMARK_DIAGNOSTIC_PIN_CANDIDATES_V1', 'UNREVIEWED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_PIN_CANDIDATES_V2')
        data = data.replace('UNCONFIGURED_CLASSIC_BENCHMARK_DIAGNOSTIC_FREEZES', 'UNCONFIGURED_CLASSIC_TRACE_BENCHMARK_DIAGNOSTIC_FREEZES_V2')
        data = data.replace('immutable-classic-benchmark-diagnostic-engine-frozen', 'immutable-classic-trace-benchmark-diagnostic-engine-frozen')
        data = data.replace('reviewed-classic-benchmark-diagnostic-freeze', 'reviewed-classic-trace-benchmark-diagnostic-freeze')
        data = data.replace('foundation-classic-streams/integration-candidate-v1', 'foundation-classic-streams/trace-integration-candidate-v1')
        put(name, data.encode())
    print(json.dumps({'recipeSha256': contract['recipeSha256'], 'edits': len(edits), 'actionsInvoked': False}))

if __name__ == '__main__': main()
