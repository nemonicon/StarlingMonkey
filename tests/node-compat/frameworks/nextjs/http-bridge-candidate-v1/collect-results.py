"""Retain the three actual host runs, excluding application/node_modules copies.

This copies evidence only. It never starts Next, a browser, compiler or guest.
Use a new output directory; the original run files remain unchanged.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = Path('/private/tmp/starling-node-compat')
RUNS = ('next-http-bridge-v1', 'next-http-bridge-v2', 'next-http-bridge-v3-browser')


def digest(path):
    data = path.read_bytes()
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def main():
    output = Path(sys.argv[1]).resolve()
    output.mkdir(parents=True, exist_ok=False)
    copies, runs = [], []
    names = tuple(sys.argv[2:]) or RUNS
    assert all(name in RUNS + ('next-http-bridge-module-v1',) for name in names)
    for name in names:
        run, monitor = BASE / name, BASE / (name + '-monitor')
        result = json.loads((run / 'result.json').read_text())
        terminal = json.loads((monitor / 'terminal.json').read_text())
        clean = (not terminal['timeout'] and not terminal['forcedCleanup']
                 and terminal['allObservedOwnedGroupsGone']
                 and terminal['parentOwnedGroupGone']
                 and all(terminal[key] == [] for key in
                         ('interruptedSignals', 'signals', 'errors', 'remainingObservedPids')))
        assert clean
        assert terminal['rawExitCode'] == (1 if name == 'next-http-bridge-v1' else 0)
        assert result['guestExecuted'] is False and result['applicationModified'] is False
        assert result['installed'] == {'next': '16.4.5', 'react': '19.3.1', 'react-dom': '19.3.1'}
        selected = [run / 'result.json']
        selected += sorted((run / 'responses').glob('*'))
        if (run / 'stream-chunks.json').exists():
            selected.append(run / 'stream-chunks.json')
        if (run / 'browser').is_dir():
            selected += sorted((run / 'browser').rglob('*'))
        selected += sorted(monitor.iterdir())
        for source in selected:
            if not source.is_file():
                continue
            assert not source.is_symlink()
            if source.is_relative_to(monitor):
                relative = Path(name) / 'monitor' / source.relative_to(monitor)
            else:
                relative = Path(name) / source.relative_to(run)
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            before = digest(source)
            shutil.copyfile(source, target)
            assert before == digest(source) == digest(target)
            copies.append({'original': str(source), 'file': str(relative), **before})
        http = result['http']
        runs.append({'name': name, 'rawExitCode': terminal['rawExitCode'], 'ownedGroupsClean': clean,
                     'httpObserved': len(http), 'httpPassed': sum(row['passed'] for row in http),
                     'browserPassed': sum(row['passed'] for row in result.get('browser', {}).get('tests', [])),
                     'streaming': result.get('streaming'), 'passed': result['passed']})
    # These two files must be the exact sources recorded by the final actual run.
    final = json.loads((BASE / names[-1] / 'result.json').read_text())
    harness = 'run-module-host.mjs' if names[-1] == 'next-http-bridge-module-v1' else 'run-host.mjs'
    for key, filename in (('bridge', 'bridge.mjs'), ('harness', harness)):
        source = HERE / filename
        assert digest(source) == {field: final[key][field] for field in ('sha256', 'bytes')}
    summary = {'schemaVersion': 1, 'suite': 'FULL_NEXT_HOST_HTTP_BRIDGE_RESULTS_V1',
               'scope': 'Node host bridge control; full Next Wasm gate remains open',
               'nativeGuestExecuted': False, 'componentExecuted': False,
               'runs': runs, 'copies': copies}
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({'copiedFiles': len(copies), 'copiedBytes': sum(row['bytes'] for row in copies),
                      'runs': runs, 'guestExecuted': False}))


if __name__ == '__main__':
    main()
