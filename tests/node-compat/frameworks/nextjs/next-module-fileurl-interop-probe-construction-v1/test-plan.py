"""Finite Source/selector DATA only; no producer, tool or build import."""
from pathlib import Path
import ast
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'next-module-fileurl-probe-construction-v1'
V6 = HERE.parent / 'next-entry-fixes-construction-v6'
PROBE = HERE.parent / 'next-module-fileurl-probe-candidate-v1'
DELTA = {'state', 'entries', 'outputPrefix', 'metadata', 'application',
         'priorCallerSourceIndex', 'nodeWorkingDirectory', 'inputDelta',
         'expectedEngineForRootAuthority', 'expectedNativeMetadataForRootAuthority'}


def row(path):
    raw = path.read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def interop_only(plan):
    return (plan['inputSourceIndex'] == row(PROBE / 'index.json') and
            plan['entries'] == {'interop': row(PROBE / 'guest-interop.mjs')})


def main():
    checks = 0

    def need(value, label):
        nonlocal checks
        assert value is True, label
        checks += 1

    plan = json.loads((HERE / 'plan.json').read_bytes())
    before = json.loads((PARENT / 'plan.json').read_bytes())
    need(set(plan) == set(before), 'No new execution API field')
    need({k for k in plan if plan[k] != before[k]} == DELTA, 'Exactly ten existing plan deltas')
    need(plan['priorCallerSourceIndex'] == row(PARENT / 'index.json'), 'Guard constructor is ancestry')
    need(plan['nodeWorkingDirectory'] == str(HERE), 'Own held Source cwd')
    need(plan['outputPrefix'] == '/private/tmp/starling-node-compat/next-module-fileurl-interop-probe-component-v1',
         'Distinct fixed output prefix')
    for name in ['run.py', 'entry.mjs', 'capture.mjs']:
        need((HERE / name).read_bytes() == (PARENT / name).read_bytes() == (V6 / name).read_bytes(),
             name + ' exact three-way V6 bytes')
    need(interop_only(plan), 'Only sealed interop literal entry selectable')
    wrong = copy.deepcopy(plan)
    wrong['entries']['guard'] = row(PROBE / 'guest-guard.mjs')
    need(not interop_only(wrong), 'Adding guard mode is outside this selector')
    wrong = copy.deepcopy(plan)
    wrong['entries']['interop'] = row(PROBE / 'guest-guard.mjs')
    need(not interop_only(wrong), 'Guard entry cannot replace interop')
    need(plan['entries']['interop']['sha256'] == 'a53ed6f28ecc5104668e31afd9bb6fab5acb1eda4a99853446b7cecb0e8be372',
         'Exact reviewed interop entry')
    for name in ['engine', 'nativeMetadata', 'actualRootAuthority', 'actualComponent', 'actualRuntime',
                 'expectedEngineForRootAuthority', 'expectedNativeMetadataForRootAuthority',
                 'expectedNativeMetadataFixedValuesForRootAuthority']:
        need(plan[name] is None, name + ' remains null; no future artifact invented')
    for name in ['pins', 'packageRoot', 'packageInventory', 'inputSourceIndex', 'witDirectory',
                 'worldSourceIndex', 'worldName', 'selectedInterfaces', 'toolParserPreopens',
                 'api', 'featuresRetained', 'componentizeNodeCapSeconds', 'dataToolCapSeconds',
                 'nativeMetadataKindRequiredInRootFixedValues', 'noOrdinaryGuestExecution',
                 'noProductionProfilePromotion']:
        need(plan[name] == before[name], name + ' unchanged')
    need(plan['toolParserPreopens'] == {plan['witDirectory']: plan['witDirectory']},
         'Only construction-parser world preopen')
    need(len(set(plan['selectedInterfaces'])) == 13 and all(x.endswith('@0.2.10') for x in plan['selectedInterfaces']),
         'Same standard13 exact interface set')
    need(plan['componentizeNodeCapSeconds'] == 1800 and plan['dataToolCapSeconds'] == 120,
         'Original inner caps')
    need(plan['noOrdinaryGuestExecution'] is plan['noProductionProfilePromotion'] is True,
         'No ordinary probe permission')
    source = json.loads((PROBE / 'plan.json').read_bytes())
    need(source['modes']['interop']['entryFile'] == 'guest-interop.mjs' and
         source['modes']['interop']['expectedCases'] == len(source['modes']['interop']['caseIds']) == 16,
         'Complete sealed16-case contract')
    need(source['modes']['interop']['nativeLoaderSource']['sha256'] ==
         '25c19d29caf370104f40036df8d20633fdb64396c30f5993a5fe52315e619b28',
         'Future interop loader role differs from guard fbc1')
    need(source['initialization']['ordinaryFsEntropyTimersHandlesOrContextCaptureAtInit'] is False,
         'No new INIT side effects')
    need(source['request']['method'] == 'GET' and source['request']['path'] == '/probe' and
         source['request']['requestsPerComponent'] == 1, 'Future single deployed request only')
    for path in HERE.glob('*.py'):
        ast.parse(path.read_bytes())
    print(json.dumps(dict(sourceOnly=True, passed=True, checks=checks,
                         exactV6ExecutableCopies=3, interopCases=16, engineAndMetadataProspective=True,
                         originalMetadataOrArtifactRetargeted=False,
                         constructorToolFixtureImportOrBuildInvoked=False,
                         actualConstructor=None, actualComponent=None, actualProbe=None)))


if __name__ == '__main__':
    main()
