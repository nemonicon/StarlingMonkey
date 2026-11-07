"""Read-only DATA regression; --actual-regression explicitly reads existing stage."""
import argparse
import ast
import copy
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('corrected_cargo_admission_v2', HERE / 'admit.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def function(source, name):
    return next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--actual-regression', action='store_true')
    args = parser.parse_args()
    p, c, plan, protected = a.context()
    recorded = dict(dev=17, ino=23, mode=0o700, nlink=6)
    current = dict(recorded, nlink=7, bytes=224, mtimeNs=1, ctimeNs=2)
    observation = a.stable_root_identity(current, recorded)
    assert observation['recordedPrePublicationNlink'] == 6 and observation['currentNlink'] == 7
    assert observation['crossPublicationNlinkCompared'] is False
    assert a.stable_root_identity(dict(current, nlink=6), recorded)
    refusals = []
    for key, value in [('dev', 18), ('ino', 24), ('mode', 0o755), ('nlink', 0), ('nlink', True)]:
        try:
            a.stable_root_identity({**current, key: value}, recorded)
        except ValueError:
            refusals.append('current-' + key + '-' + str(value))
        else:
            raise AssertionError('accepted unstable root: ' + key)
    for changed in ({**recorded, 'nlink': False}, {**recorded, 'extra': 1},
                    {k: v for k, v in recorded.items() if k != 'nlink'}):
        try:
            a.stable_root_identity(current, changed)
        except ValueError:
            refusals.append('historical-root-shape-' + str(len(refusals)))
        else:
            raise AssertionError('accepted malformed historical observation')
    old = function(Path(p.__file__).read_text(), 'admit_restore')
    new = function((HERE / 'admit.py').read_text(), 'admit_restore')
    critical = {'read_file', 'payload_layout', 'tree', 'recorded_bookends', 'guard_sources'}
    def calls(node):
        found = []
        for call in ast.walk(node):
            if isinstance(call, ast.Call):
                name = call.func.id if isinstance(call.func, ast.Name) else call.func.attr if isinstance(call.func, ast.Attribute) else None
                if name in critical:
                    found.append((call.lineno, name))
        return [name for _, name in sorted(found)]
    assert calls(old) == calls(new) == ['read_file', 'payload_layout', 'tree', 'recorded_bookends', 'guard_sources']
    guard_line = next(n.lineno for n in ast.walk(new) if isinstance(n, ast.Call) and
                      isinstance(n.func, ast.Attribute) and n.func.attr == 'guard_sources')
    assert not any(n.lineno > guard_line and isinstance(n.func, ast.Attribute) and
                   n.func.attr in ('read_file', 'tree', 'recorded_bookends')
                   for n in ast.walk(new) if isinstance(n, ast.Call))
    result = dict(rootIdentityRefusals=refusals, refusalCount=len(refusals),
                  historicalNlinkChangeAccepted=True, criticalProducerCallOrderPreserved=True,
                  noPostBookendFileReads=True, actualRegressionExecuted=False,
                  newSourceStageOrCargoOrCompilerOrNetworkOrGuestExecuted=False)
    if args.actual_regression:
        ref = plan['regression']['receipt']
        raw, before = p.read_file(ref['path'], ref)
        original = json.loads(raw)
        stage_ref = plan['regression']['rootStageProcess']
        stage_raw, stage_row = a.checked(a.REPO / stage_ref['path'], stage_ref)
        stage = json.loads(stage_raw)
        assert stage['rawExitCode'] == 0 and stage['sourceOnly'] is True
        assert stage['cargoOrCompilerOrNetworkOrGuestInvoked'] is False
        try:
            p.admit_restore(ref)
        except ValueError as error:
            assert str(error) == 'owned root identity'
            original_failure = dict(type=type(error).__name__, message=str(error))
        else:
            raise AssertionError('expected retained V1 publication-nlink refusal')
        admitted = a.admit_restore(ref)
        assert admitted['dataConsistent'] is True and admitted['state'] == 'RESTORED_CARGO_SOURCE_DATA_CONSISTENT_V2'
        assert admitted['sourceIndex']['sha256'] == plan['producerSourceIndex']['sha256']
        assert admitted['admissionSourceIndex']['sha256'] == protected[0]['sha256']
        assert admitted['actualCargoMetadata'] is None and admitted['sourceProcessExecutionAttested'] is False
        assert len([r for r in admitted['physicalRecords'] if r.get('kind') == 'file']) == 3507
        assert len([r for r in admitted['physicalRecords'] if r.get('kind') == 'directory']) == 464
        p.guard_sources([before, stage_row] + protected)
        result['actualRegressionExecuted'] = True
        result['originalSourceStageRawExitCode'] = stage['rawExitCode']
        result['originalV1ReaderFailure'] = original_failure
        result['unchangedOriginalReceipt'] = p.plain_descriptor(before)
        result['correctedCurrentPayloadFilesIncludingReceipt'] = 3507
        result['correctedCurrentDirectoriesIncludingRoot'] = 464
        result['producerSourceIndex'] = admitted['sourceIndex']
        result['admissionSourceIndex'] = admitted['admissionSourceIndex']
        result['rootLinkCountObservation'] = admitted['rootLinkCountObservation']
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
