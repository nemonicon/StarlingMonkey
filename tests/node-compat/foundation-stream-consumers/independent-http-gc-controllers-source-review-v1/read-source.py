"""Independent read/hash and extracted-pure-model review; never imports a controller."""
import ast
import hashlib
import json
from pathlib import Path

REPO = Path('/Users/dan/dev/StarlingMonkey')
HERE = Path(__file__).resolve().parent
HTTP = REPO / 'tests/node-compat/foundation-stream-consumers/http-host-controller-candidate-v1'
GC = REPO / 'tests/node-compat/foundation-crypto/ownership-gc-stage-controller-candidate-v1'
PINS = {
    HTTP: '5ccf3aa6b9443ff2aecad8f02f22a69934adc73a5125e148c2a67cb24b171217',
    GC: '8ff1af8767dc131d29ab0c8b20d271b3bd025c91382dd79c98c0591210502cee',
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def checked(path, expected=None):
    path = Path(path)
    assert path.is_absolute() and '..' not in path.parts
    physical = Path('/private' + str(path)) if str(path).startswith('/tmp/') else path
    assert not any(p.is_symlink() for p in (physical, *physical.parents))
    before = path.stat()
    assert path.is_file()
    raw = path.read_bytes()
    after = path.stat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    row = dict(path=str(path), sha256=digest(raw), bytes=len(raw))
    if expected:
        assert row == {k: expected[k] for k in row}
    return raw, row


def review():
    inputs, families = [], []
    for root, pin in PINS.items():
        raw, index_row = checked(root / 'index.json')
        assert index_row['sha256'] == pin
        inputs.append(index_row)
        index = json.loads(raw)
        names = [r['path'] for r in index['files']]
        assert len(names) == len(set(names))
        actual = sorted(str(p.relative_to(root)) for p in root.rglob('*') if p.is_file())
        assert actual == sorted(names + ['index.json'])
        for row in index['files']:
            assert not Path(row['path']).is_absolute() and '..' not in Path(row['path']).parts
            _, observed = checked(root / row['path'], dict(row, path=str(root / row['path'])))
            inputs.append(observed)
        families.append(dict(index=index_row, members=len(names), exactMembership=True))

    source = (HTTP / 'controller.py').read_text()
    tree = ast.parse(source)
    names = {'identity', 'discover', 'group_model'}
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in functions} == names
    # These three actual function bodies contain no I/O or imports. No controller module executes.
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom, ast.AsyncFunctionDef)) for f in functions for n in ast.walk(f))
    pure = {}
    exec(compile(ast.Module(body=functions, type_ignores=[]), '<actual-controller-three-pure-models>', 'exec'), pure)
    def row(pid, ppid, pgid, birth='held-birth', command='benign-model'):
        return dict(pid=pid, ppid=ppid, pgid=pgid, birth=birth, command=command)
    root = row(100, 1, 100)
    cases = []
    for name, old, current in [
        ('known-nonleader-in-unobserved-leader-group', row(102, 100, 101), row(102, 1, 101)),
        ('known-pid-current-pgid-changed', row(102, 100, 100), row(102, 1, 102)),
    ]:
        known = {100: root, 102: old}
        rows = {102: current}
        before = json.dumps(known, sort_keys=True)
        added = pure['discover'](rows, known, 100)
        groups = pure['group_model'](rows, known, 100)
        assert before == json.dumps(known, sort_keys=True) and added == []
        complete = bool(groups) and not any(g['alive'] for g in groups)
        assert complete and 102 in rows and 102 in known
        assert not any(g['pgid'] == current['pgid'] for g in groups)
        cases.append(dict(name=name, knownProcesses=list(known.values()), currentProcesses=list(rows.values()), actualGroupModel=groups, controllerCompletionPredicateWithObservedParentRawZero=complete, knownPidStillPresent=True, pureSourceCounterexample=True, observedRuntimeLeak=False))
    # Existing identity refusal is retained, not broadened into signal permission.
    for name, replacement in [('pid-reused-birth', row(100, 1, 100, birth='replacement')), ('command-changed', row(100, 1, 100, command='replacement'))]:
        groups = pure['group_model']({100: replacement}, {100: root}, 100)
        assert groups[0]['alive'] is True and groups[0]['signalAllowed'] is False
        cases.append(dict(name=name, actualGroupModel=groups, completionRefused=True))
    assert 'complete = child is not None and bool(final_groups) and not any(g[\'alive\'] for g in final_groups)' in source

    benign = json.loads((HTTP / 'benign-inputs.json').read_bytes())
    for row in benign['files']:
        _, observed = checked(row['path'], row)
        inputs.append(observed)
    stdout = (HTTP / 'evidence/stdout.log').read_text().splitlines()
    summary = json.loads(stdout[-1])
    assert summary['checks'] == 25
    terminal = json.loads((HTTP / 'evidence/terminal.json').read_bytes())
    assert terminal['rawExitCode'] == 0
    sessions = []
    for name in ('normal', 'bounded-timeout', 'parent-exit-owned-descendant'):
        candidates = [r for r in benign['files'] if r['path'].endswith('/' + name + '/terminal.json')]
        assert len(candidates) == 1
        value = json.loads(Path(candidates[0]['path']).read_bytes())
        assert value['allObservedOwnedGroupsGone'] is True and value['errors'] == []
        if name == 'normal':
            assert value['rawExitCode'] == 0 and value['forcedCleanup'] is False and value['timeout'] is False
        else:
            assert value['forcedCleanup'] is True
        sessions.append(dict(name=name, terminal=candidates[0], rawExitCode=value['rawExitCode'], forcedCleanup=value['forcedCleanup'], timeout=value['timeout'], recordedGroupsGone=value['allObservedOwnedGroupsGone']))
    evidence = Path('/private/tmp/starling-node-compat/independent-gc-stage-caller-source-audit-v1.json')
    _, corroboration = checked(evidence, dict(path=str(evidence), sha256='0a2370f07b47af8354233998e51c5776e36ed69c39b8fabcb3c5d3776a6e10b0', bytes=5134))
    inputs.append(corroboration)
    gc_source = (GC / 'controller.py').read_text()
    ast.parse(gc_source)
    assert "module.monitor(argv,str(REPO),environment,OUT,600,config['rootAuthority'])" in gc_source.replace(' ', '')
    # Every initially consumed byte is checked again after the pure/data review.
    for observed in inputs:
        checked(observed['path'], observed)
    return dict(schemaVersion=1, sourceCheckpoint='d54d9d4b565cdd00f84cf751ac60fe5ec553f5c5', families=families, inputs=inputs, pureCases=cases, retainedAuthorBenignEvidence=dict(checks=25, sessions=sessions, authorBenignHostInfrastructureInvoked=True, reviewerReranBenignSessions=False), sourceAndDataOnly=True, controllerImported=False, monitorOrSnapshotInvoked=False, processesOrSignalsInvoked=False, sourceRecheckPassed=True)


if __name__ == '__main__':
    value = review()
    with (HERE / 'observations.json').open('x') as out:
        json.dump(value, out, indent=2)
        out.write('\n')
    print(json.dumps(dict(state='INDEPENDENT_CONTROLLER_SOURCE_MODEL_HOLD_CONFIRMED', families=len(value['families']), inputs=len(value['inputs']), pureCases=len(value['pureCases']), actionsInvoked=False)))
