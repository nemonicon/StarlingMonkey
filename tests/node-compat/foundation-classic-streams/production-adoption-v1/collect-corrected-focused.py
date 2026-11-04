"""Capture Root-observed terminal results; not an independent guest verifier."""
import argparse
import hashlib
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path('/tmp/starling-node-compat/production-classic-corrected-regression-v1')
LABELS = {
    'focused-off': ('normal-off', 'NEW_CLASSIC342_ORDINARY_NATIVE_ADD_ABORT_LISTENER_PASSED'),
    'focused-runtime': ('normal-runtime', 'NEW_CLASSIC342_ORDINARY_NATIVE_ADD_ABORT_LISTENER_PASSED'),
    'focused-gc': ('gc-off', 'NEW_CLASSIC342_RELEASE_MOVING_GC_COMBINED_OWNER_GATE_PASSED'),
    'getter': ('normal-off', 'CONFIRMED_FRESH_CALLBACK_RETURN_THEN_GETTER_COUNTEREXAMPLE'),
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def row(path):
    assert path.is_file() and not path.is_symlink(), path
    data = path.read_bytes()
    return {'path': str(path), 'sha256': sha(data), 'bytes': len(data)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('label', choices=LABELS)
    parser.add_argument('--raw-exit-code', required=True, type=int)
    parser.add_argument('--tool-session', required=True, type=int)
    args = parser.parse_args()
    assert args.raw_exit_code == 0, 'A nonzero or unobserved exit cannot publish a completion capture'
    variant, state = LABELS[args.label]
    root = BASE / args.label
    assert root.is_dir() and not root.is_symlink()
    pins_raw = (HERE / 'reviewed-trace-runtime-pins-v1.json').read_bytes()
    assert sha(pins_raw) == '182e8b724d94ebf73450c0ffcea81fb19b902028e2839bd2a9d1452ab7fab5eb'
    pin = json.loads(pins_raw)['variants'][variant]
    assert pin['sourceContractVersion'] == 'sm-classic-trace-source-v1'
    report = json.loads((root / 'results.json').read_bytes())
    completion = json.loads((root / 'production-admission-complete.json').read_bytes())
    assert report['state'] == state
    assert report['engineSha256'] == completion['engineSha256'] == pin['engineSha256']
    assert completion['variant'] == variant and completion['consumedInputsRecheckedAfterRun'] is True
    assert report['preflight']['sourceFilesVerified'] == completion['sourceFilesVerified'] == 342
    # sourceFiles is the fixture-file list, not the native source count.
    assert isinstance(report['sourceFiles'], list)
    for source in report['sourceFiles']:
        assert row(Path(source['path']))['sha256'] == source['sha256']
    if args.label in ('focused-off', 'focused-runtime'):
        assert report['publicNodeGroups']['total'] == 29
        assert len(report['initializers']) == 8 and len(report['fatal']) == 5
    if args.label == 'getter':
        assert report['observationCompleted'] is True and report['nodeCompatibilityPassed'] is False
    artifacts, links = [], []
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            links.append({'path': str(path), 'target': os.readlink(path)})
        elif path.is_file():
            artifacts.append(row(path))
    for suffix in ('stdout', 'stderr'):
        artifacts.append(row(Path('/tmp/starling-node-compat') / f'classic-corrected-{args.label}-v1.{suffix}.log'))
    result = {
        'schemaVersion': 1, 'state': 'ROOT_CORRECTED_FOCUSED_TERMINAL_ZERO_AND_OUTPUTS_CAPTURED',
        'label': args.label, 'variant': variant, 'resultState': state,
        'rawTerminalExitCodeObservedByRoot': args.raw_exit_code, 'toolSession': args.tool_session,
        'engineSha256': pin['engineSha256'], 'nativeSourceFiles': 342,
        'fixtureSourceFiles': len(report['sourceFiles']), 'consumedInputsRecheckedAfterRun': True,
        'artifacts': artifacts, 'links': links, 'collector': row(Path(__file__)),
        'nodeGetterParityClaim': False, 'isolatedGCRootClaim': False,
        'independentReviewPending': True, 'compatibilityAccepted': False,
        'collectorHistory': 'First unsaved Root attempt expected sourceFiles to be an integer; it is a fixture list. Assertion stopped before output. Native count is the actual preflight.sourceFilesVerified.',
    }
    output = HERE / f'corrected-{args.label}-root-results.json'
    with output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'output': str(output), 'sha256': sha(output.read_bytes()), 'artifacts': len(artifacts), 'links': len(links)}))

if __name__ == '__main__':
    main()
