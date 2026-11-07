"""Read-only Source/actual JSON binding checks; no producer or tool import."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'next-native-portable-generator-check-v5'


def read_ref(ref):
    data = Path(ref['path']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == ref['sha256'] and len(data) == ref['bytes']
    return data


def main():
    before, after = [json.loads((p / 'plan.json').read_bytes()) for p in (OLD, HERE)]
    assert (HERE / 'run.py').read_bytes() == (OLD / 'run.py').read_bytes()
    assert {k for k in after if after[k] != before[k]} == {'materializerIndex', 'materializationRoot',
        'sourceRoot', 'composition', 'materializationSummary', 'roleContentSha256', 'portableAdmission'}
    assert after['materializationRoot'] == '/private/tmp/starling-node-compat/next-native-portable-source-v6-materialization-v1'
    assert after['sourceRoot'] == after['materializationRoot'] + '/source'
    read_ref(after['materializerIndex'])
    admission = after['portableAdmission']
    read_ref(admission['sourceIndex'])
    assert Path(admission['module']['path']).read_bytes() == (HERE.parent / 'next-native-portable-build-preparation-v7/portable.py').read_bytes()
    read_ref(admission['module'])
    builder = json.loads(read_ref(admission['plan']))
    policy = builder['portableSourcePolicy']
    assert after['roleContentSha256'] == policy['roleContentSha256'] == 'c0d113eccc91c6646aadcf29ec3d9272e866a3e794eeb195c6f784472ecec799'
    assert after['composition']['path'] == after['materializationRoot'] + '/composition.json'
    assert after['materializationSummary']['path'] == after['materializationRoot'] + '/source-materialization.json'
    summary = json.loads(read_ref(after['materializationSummary']))
    composition = json.loads(read_ref(after['composition']))
    assert summary['state'] == 'NEXT_PORTABLE_SOURCE_MATERIALIZED_V1'
    assert summary['composition'] == after['composition'] and summary['outputRoot'] == after['materializationRoot']
    assert summary['files'] == 825 and summary['bytes'] == 7554700 and summary['roleCounts'] == after['expectedRoleCounts']
    assert summary['roleContentSha256'] == after['roleContentSha256']
    assert composition['sourceRoot'] == after['sourceRoot'] and composition['nativeSourceFiles'] == len(composition['files']) == 435
    assert summary['compilerOrGuestExecuted'] is composition['engineBuilt'] is composition['guestExecuted'] is False
    for key in ('node', 'monitor', 'python', 'commandDonor', 'outputPrefix', 'perCommandSeconds',
                'outerSeconds', 'minimumFreeBytes', 'maxAcceptedRawStreamBytes', 'maxAcceptedOutputBytes',
                'byteCapsArePostCaptureAdmissionNotContinuousLimits', 'expectedRoleCounts'):
        assert after[key] == before[key]
    assert after['perCommandSeconds'] == 30 and after['outerSeconds'] == 900
    assert all(after[k] is None for k in ('actualRootAuthority', 'actualRuntime', 'actualGeneratorProof'))
    assert 'portableSelection' not in after
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text())
    print(json.dumps(dict(sourceOnly=True, controllerByteIdentical=True, realMat6JsonBindings=True,
        readOnlyJsonAndSourceChecks=True, rootSelectionRemainsLateAuthorityField=True,
        originalCommandAndCapacityPolicyUnchanged=True, producerOrToolInvoked=False)))


if __name__ == '__main__':
    main()
