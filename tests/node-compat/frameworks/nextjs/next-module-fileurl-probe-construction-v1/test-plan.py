"""Inert constructor plan/retained metadata DATA only; never imports a producer or tool."""
from pathlib import Path
import ast
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'next-module-boundary-construction-v1'
PROBE = HERE.parent / 'next-module-fileurl-probe-candidate-v1'
DELTA = {'state', 'inputSourceIndex', 'entries', 'outputPrefix', 'metadata', 'application',
         'priorCallerSourceIndex', 'nodeWorkingDirectory', 'inputDelta'}


def row(path):
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def guard_entries(plan):
    return (plan['inputSourceIndex'] == row(PROBE / 'index.json') and
            plan['entries'] == {'guard': row(PROBE / 'guest-guard.mjs')})


def main():
    checks = 0

    def need(value, reason):
        nonlocal checks
        assert value is True, reason
        checks += 1

    p = json.loads((HERE / 'plan.json').read_bytes())
    old = json.loads((PARENT / 'plan.json').read_bytes())
    need(set(p) == set(old), 'No new executable API fields')
    need({k for k in p if p[k] != old[k]} == DELTA, 'Only nine existing plan fields')
    need(p['priorCallerSourceIndex'] == row(PARENT / 'index.json'), 'Genuine held guard constructor ancestry')
    need(p['nodeWorkingDirectory'] == str(HERE), 'Own held Source cwd')
    need(p['outputPrefix'] == '/private/tmp/starling-node-compat/next-module-fileurl-probe-component-v1',
         'Distinct fixed private namespace')
    for name in ['run.py', 'entry.mjs', 'capture.mjs']:
        need((HERE / name).read_bytes() == (PARENT / name).read_bytes(), 'Exact donor executable: ' + name)
    need(guard_entries(p), 'Only sealed literal guard entry selectable')
    wrong = copy.deepcopy(p)
    wrong['entries']['interop'] = row(PROBE / 'guest-interop.mjs')
    need(not guard_entries(wrong), 'Future interop cannot be added to this declared selector')
    wrong = copy.deepcopy(p)
    wrong['entries']['guard'] = row(PROBE / 'guest-interop.mjs')
    need(not guard_entries(wrong), 'Future interop cannot replace guard entry')
    for name in ['engine', 'nativeMetadata', 'actualRootAuthority', 'actualComponent', 'actualRuntime',
                 'expectedNativeMetadataFixedValuesForRootAuthority']:
        need(p[name] is None, 'Operational role stays NULL: ' + name)
    for name in ['pins', 'packageRoot', 'packageInventory', 'witDirectory', 'worldSourceIndex', 'worldName',
                 'selectedInterfaces', 'toolParserPreopens', 'api', 'featuresRetained',
                 'componentizeNodeCapSeconds', 'dataToolCapSeconds',
                 'expectedEngineForRootAuthority', 'expectedNativeMetadataForRootAuthority',
                 'nativeMetadataKindRequiredInRootFixedValues', 'noOrdinaryGuestExecution',
                 'noProductionProfilePromotion']:
        need(p[name] == old[name], 'Existing selected policy unchanged: ' + name)
    need(p['toolParserPreopens'] == {p['witDirectory']: p['witDirectory']},
         'Only construction-tool WIT parser preopen, never fixture/app root')
    need(len(set(p['selectedInterfaces'])) == 13 and all(x.endswith('@0.2.10') for x in p['selectedInterfaces']),
         'Same exact13 standard interface contract')
    need(p['componentizeNodeCapSeconds'] == 1800 and p['dataToolCapSeconds'] == 120,
         'Existing inner caps unchanged')
    need(p['noOrdinaryGuestExecution'] is p['noProductionProfilePromotion'] is True,
         'Constructor has no ordinary probe permission')
    source = json.loads((PROBE / 'plan.json').read_bytes())
    need(source['modes']['guard']['caseIds'] == ['cjs-dynamic-builtin', 'guard-natural-fileurl-refusal'],
         'Actual bound two-case contract')
    need(source['request']['method'] == 'GET' and source['request']['path'] == '/probe' and
         source['request']['requestsPerComponent'] == 1, 'Future single ordinary request')
    metadata_ref = p['expectedNativeMetadataForRootAuthority']
    path = Path(metadata_ref['path'])
    need(row(path) == metadata_ref, 'Actual full metadata selected, read as DATA')
    m = json.loads(path.read_bytes())
    need(m['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1' and
         type(m['actualCompileRows']) is list and len(m['actualCompileRows']) == 80 and
         type(m['actualSeparateEmbeddingCompileRows']) is list and len(m['actualSeparateEmbeddingCompileRows']) == 1,
         'Actual full arrays are retained')
    need(m['engine'] == p['expectedEngineForRootAuthority'], 'Selected metadata actual engine')
    loader = [q for q in m['nativePolicyInputManifest'] if q['path'] == 'runtime/script_loader.cpp']
    need(len(loader) == 1 and loader[0]['sha256'] == 'fbc1d13eebc66d20b01b1828008f3918609752e060320dbd16837722d4216ab8',
         'Guard fbc1 selected, future native25c excluded')
    need(row(path) == metadata_ref, 'Genuine metadata unchanged during read')
    for path in HERE.glob('*.py'):
        ast.parse(path.read_bytes())
    print(json.dumps(dict(sourceOnly=True, passed=True, checks=checks,
                         originalMetadataDataRead=metadata_ref,
                         constructorOrEngineOrFixtureStageOrImportInvoked=False,
                         actualConstructor=None, actualComponent=None, actualProbe=None)))


if __name__ == '__main__':
    main()
