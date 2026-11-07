"""Read-only Source identity/policy checks; no preparation or action entrypoint."""
from pathlib import Path
import ast
import hashlib
import json

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'next-native-portable-build-preparation-v7'
REPO = HERE.parents[4]


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def main():
    before, after = [json.loads((p / 'plan.json').read_bytes()) for p in (OLD, HERE)]
    assert {k for k in after if after[k] != before[k]} == {'portableSourcePolicy', 'portableCargoPolicy'}
    for name in ('run.py', 'prepare.py', 'cargo-selection.py', 'portable.py', 'root-authority.template.json'):
        assert (HERE / name).read_bytes() == (OLD / name).read_bytes()
    policy, previous = after['portableSourcePolicy'], before['portableSourcePolicy']
    assert {k for k in policy if policy[k] != previous[k]} == {'materializerIndex', 'materializerSelection', 'expectedBytes', 'roleContentSha256'}
    assert policy['expectedCounts'] == previous['expectedCounts'] == {'native-policy-source': 435, 'build-support': 387, 'componentize-embedding': 3}
    assert policy['expectedFiles'] == 825 and policy['expectedBytes'] == 7554700
    assert policy['roleContentSha256'] == 'c0d113eccc91c6646aadcf29ec3d9272e866a3e794eeb195c6f784472ecec799'
    for key, name in (('materializerIndex', 'index.json'), ('materializerSelection', 'selection.json')):
        path = HERE.parent / 'next-native-portable-source-v6' / name
        assert policy[key]['repositoryPath'] == path.relative_to(REPO).as_posix()
        assert all(row(path)[k] == policy[key][k] for k in ('sha256', 'bytes'))
    assert after['portableCargoPolicy'] == dict(before['portableCargoPolicy'], helper=row(HERE / 'cargo-selection.py'))
    assert after['portableAdmissionSourceIndex'] == before['portableAdmissionSourceIndex']
    assert after['portableAdmissionModule'] == before['portableAdmissionModule']
    for key in ('disk', 'timeouts', 'cmakeAdditions', 'wrapperPython', 'baseRunner', 'basePlan'):
        assert after[key] == before[key]
    assert after['actionsAllowed'] is False
    assert all(after[key] is None for key in ('rootAuthority', 'actualBuild', 'actualMetadata'))
    template = json.loads((HERE / 'root-authority.template.json').read_bytes())
    for key in ('workRoot', 'configureAllowed', 'buildAllowed', 'installedGeneratorResult', 'portableSelection', 'portableCargoSelection'):
        assert template[key] is None
    for path in HERE.glob('*.py'):
        ast.parse(path.read_text())
    print(json.dumps(dict(sourceOnly=True, operationalFilesByteIdentical=4,
        rootTemplateByteIdentical=True, onlyMaterializerPolicyAndOwnCargoHelperPathChanged=True,
        newMaterializerIndexBound=True, nativeCommandsOrPreparationInvoked=False,
        physicalSelectionOrGeneratorProofClaimed=False, cppCompiled=False)))


if __name__ == '__main__':
    main()
