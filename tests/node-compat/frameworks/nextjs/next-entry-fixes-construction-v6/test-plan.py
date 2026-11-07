"""Inert plan/metadata DATA checks; never imports a constructor or invokes tools."""
from pathlib import Path
import argparse
import ast
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'next-entry-fixes-construction-v5'
FULL = 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1'
INCREMENTAL = 'EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1'
EXPECTED_DELTAS = {
    'inputDelta', 'metadata', 'nativeMetadataKindRequiredInRootFixedValues',
    'nodeWorkingDirectory', 'outputPrefix', 'priorCallerSourceIndex', 'state',
}


def descriptor(path):
    data = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def full_shape(value):
    """Prospective Root DATA rule, not a new constructor admission API."""
    return (value.get('metadataKind') == FULL
            and all(type(value.get(k)) is int and value[k] == n for k, n in [
                ('schemaVersion', 1), ('nativePolicyInputCount', 435),
                ('buildSupportInputCount', 387), ('embeddingInputCount', 3)])
            and type(value.get('actualCompileRows')) is list
            and len(value['actualCompileRows']) == 80
            and type(value.get('actualSeparateEmbeddingCompileRows')) is list
            and len(value['actualSeparateEmbeddingCompileRows']) == 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata', help='Optional genuine metadata JSON, read as DATA only')
    args = parser.parse_args()
    count = 0

    def check(value, label):
        nonlocal count
        assert value is True, label
        count += 1

    plan = json.loads((HERE / 'plan.json').read_bytes())
    prior = json.loads((PARENT / 'plan.json').read_bytes())
    check(set(plan) == set(prior), 'No plan fields added or removed')
    check({k for k in plan if plan[k] != prior[k]} == EXPECTED_DELTAS, 'Seven exact plan changes')
    for name in ['entry.mjs', 'capture.mjs', 'run.py']:
        check((HERE / name).read_bytes() == (PARENT / name).read_bytes(), name + ' exact copy')
    check(plan['priorCallerSourceIndex'] == descriptor(PARENT / 'index.json'), 'Preserved V5 index')
    check(plan['state'] == 'NEXT_ENTRY_FIXES_CONSTRUCTION_SOURCE_ONLY_V6', 'V6 Source state')
    check(plan['nodeWorkingDirectory'] == str(HERE), 'Held caller cwd')
    check(plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-entry-fixes-component-v6', 'Fresh prefix')
    check(plan['nativeMetadataKindRequiredInRootFixedValues'] == FULL, 'Full kind required in Root fixed values')
    for key in ['engine', 'nativeMetadata', 'actualRootAuthority', 'actualComponent',
                'actualRuntime', 'expectedEngineForRootAuthority',
                'expectedNativeMetadataForRootAuthority',
                'expectedNativeMetadataFixedValuesForRootAuthority']:
        check(plan[key] is None, key + ' remains NULL')
    for key in ['pins', 'packageRoot', 'packageInventory', 'inputSourceIndex', 'entries',
                'witDirectory', 'worldSourceIndex', 'worldName', 'selectedInterfaces',
                'toolParserPreopens', 'api', 'componentizeNodeCapSeconds', 'dataToolCapSeconds']:
        check(plan[key] == prior[key], key + ' unchanged')
    check(len(plan['selectedInterfaces']) == 13, 'Thirteen selected interfaces')
    check(len(set(plan['selectedInterfaces'])) == 13, 'No duplicate interface')
    check(all(x.endswith('@0.2.10') for x in plan['selectedInterfaces']), 'Exact standard version')
    check(plan['toolParserPreopens'] == {plan['witDirectory']: plan['witDirectory']}, 'Single official parser preopen')

    # Compile only the copied producer's existing pure fixed-field predicate.
    # No module import, main(), monitor, componentizer or native engine is run.
    tree = ast.parse((HERE / 'run.py').read_text())
    matches = [x.test for x in ast.walk(tree) if isinstance(x, ast.Assert)
               and ast.unparse(x.test) == 'all((metadata[k] == v for k, v in a[\'metadataExpectedFixedValues\'].items()))']
    check(len(matches) == 1, 'Actual producer fixed-field predicate found once')
    expression = compile(ast.Expression(matches[0]), str(HERE / 'run.py'), 'eval')

    def fixed_accepts(metadata, expected):
        scope = {'__builtins__': {}, 'all': all, 'metadata': metadata,
                 'a': {'metadataExpectedFixedValues': expected}}
        return eval(expression, scope)

    fixed = dict(schemaVersion=1, metadataKind=FULL, nativePolicyInputCount=435,
                 buildSupportInputCount=387, embeddingInputCount=3)
    model = dict(fixed, actualCompileRows=[{} for _ in range(80)],
                 actualSeparateEmbeddingCompileRows=[{}])
    check(fixed_accepts(model, fixed), 'Full-kind fixed-field model accepted')
    check(full_shape(model), 'Full 80+1 arrays accepted')
    for key, bad in [('metadataKind', INCREMENTAL), ('schemaVersion', True),
                     ('nativePolicyInputCount', 434), ('buildSupportInputCount', 386),
                     ('embeddingInputCount', 2), ('actualCompileRows', 80),
                     ('actualCompileRows', [{} for _ in range(79)]),
                     ('actualSeparateEmbeddingCompileRows', 1),
                     ('actualSeparateEmbeddingCompileRows', []),
                     ('actualSeparateEmbeddingCompileRows', [{}, {}])]:
        changed = copy.deepcopy(model)
        changed[key] = bad
        check(not full_shape(changed), 'Refuse invalid full metadata shape: ' + key)
    old = copy.deepcopy(model)
    old['metadataKind'] = INCREMENTAL
    check(not fixed_accepts(old, fixed), 'Existing fixed predicate refuses incremental kind against full selection')
    check(not fixed_accepts(model, dict(fixed, actualCompileRows=80)), 'Array is not cast to scalar count')

    actual = None
    if args.metadata:
        path = Path(args.metadata)
        check(path.is_absolute() and path.resolve() == path, 'Canonical DATA metadata path')
        before = descriptor(path)
        value = json.loads(path.read_bytes())
        check(full_shape(value), 'Genuine full metadata has 80+1 actual arrays')
        check(fixed_accepts(value, fixed), 'Genuine full metadata matches selected actual fixed fields')
        check(not fixed_accepts(value, dict(fixed, metadataKind=INCREMENTAL)), 'Genuine full metadata refuses old incremental selection')
        check(descriptor(path) == before, 'Genuine full metadata bytes unchanged')
        actual = dict(descriptor=before, actualCompileRows=len(value['actualCompileRows']),
                      actualSeparateEmbeddingCompileRows=len(value['actualSeparateEmbeddingCompileRows']),
                      dataOnly=True, actualBuildAcceptedForConstruction=False)
    print(json.dumps(dict(schemaVersion=1, passed=True, checks=count,
                          genuineMetadataDataCheck=actual,
                          constructorOrApiOrMonitorInvoked=False,
                          rootAuthorityIssued=False, actualComponent=None,
                          actualRuntime=None)))


if __name__ == '__main__':
    main()
