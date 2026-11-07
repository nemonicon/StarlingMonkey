"""Read/AST/data checks only; never import or invoke constructor executables."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'next-entry-fixes-construction-v6'
ENTRY = HERE.parent / 'next-cache-affinity-diagnostic-entry-v1'


def row(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', action='store_true')
    args = parser.parse_args()
    actual = json.loads((HERE / 'plan.json').read_bytes())
    before = json.loads((BASE / 'plan.json').read_bytes())
    expected = {'state', 'inputSourceIndex', 'entries', 'outputPrefix', 'nodeWorkingDirectory', 'priorCallerSourceIndex', 'inputDelta'}
    assert {k for k in set(actual) | set(before) if actual.get(k) != before.get(k)} == expected
    for name in ['entry.mjs', 'capture.mjs', 'run.py']:
        assert (HERE / name).read_bytes() == (BASE / name).read_bytes()
    ast.parse((HERE / 'run.py').read_text())
    assert actual['entries'] == {'real-next': row(ENTRY / 'guest-entry.mjs')}
    assert actual['priorCallerSourceIndex'] == row(BASE / 'index.json')
    assert actual['nodeWorkingDirectory'] == str(HERE)
    assert actual['outputPrefix'] == '/private/tmp/starling-node-compat/next-cache-affinity-diagnostic-component-v1'
    if args.draft:
        assert actual['inputSourceIndex'] is None
    else:
        assert actual['inputSourceIndex'] == row(ENTRY / 'index.json')
        value = json.loads((ENTRY / 'index.json').read_bytes())
        assert {r['path'] for r in value['files']} | {'index.json'} == {str(p.relative_to(ENTRY)) for p in ENTRY.rglob('*') if p.is_file()}
        for ref in value['files']:
            assert row(ENTRY / ref['path']) == dict(ref, path=str(ENTRY / ref['path']))
    plan = json.loads((ENTRY / 'plan.json').read_bytes())
    assert actual['worldSourceIndex'] == before['worldSourceIndex'] == plan['worldSourceIndex']
    assert actual['witDirectory'] == before['witDirectory'] == plan['witDirectory']
    assert actual['selectedInterfaces'] == before['selectedInterfaces'] == plan['selectedInterfaces']
    assert len(actual['selectedInterfaces']) == 13 and all(x.endswith('@0.2.10') for x in actual['selectedInterfaces'])
    assert actual['nativeMetadataKindRequiredInRootFixedValues'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1'
    for key in ['engine', 'nativeMetadata', 'actualRootAuthority', 'actualComponent', 'actualRuntime', 'expectedEngineForRootAuthority', 'expectedNativeMetadataForRootAuthority', 'expectedNativeMetadataFixedValuesForRootAuthority']:
        assert actual[key] is None
    print(json.dumps(dict(sourceOnly=True, constructorExecutablesByteIdentical=3, exactPlanDeltaFields=7,
        unchangedSelectedInterfaces=13, fullBuildMetadataPolicyUnchanged=True, pendingEntryIndex=args.draft,
        actualSlotsNull=True, constructorOrApiOrActorInvoked=False)))
