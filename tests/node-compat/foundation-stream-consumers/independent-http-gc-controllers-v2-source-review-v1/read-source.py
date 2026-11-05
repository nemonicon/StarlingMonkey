"""Read/hash, exact derivations and extracted pure models; no controller import/action."""
import ast
import hashlib
import json
from pathlib import Path

REPO = Path('/Users/dan/dev/StarlingMonkey')
HERE = Path(__file__).resolve().parent
S = REPO / 'tests/node-compat/foundation-stream-consumers'
K = REPO / 'tests/node-compat/foundation-crypto'
HTTP = S / 'http-host-controller-candidate-v2'
GC = K / 'ownership-gc-stage-controller-candidate-v2'
PINS = {
    HTTP: '71b7f8e54ae2e21d6673d054a20efa7b1e00409d22d8af7c5b064ad9a6380ddf',
    GC: '29d59208114b7cb0aed21be2fe09bd35a1efc9de841d49157e3e83378790700d',
    S / 'http-host-controller-candidate-v1': '5ccf3aa6b9443ff2aecad8f02f22a69934adc73a5125e148c2a67cb24b171217',
    K / 'ownership-gc-stage-controller-candidate-v1': '8ff1af8767dc131d29ab0c8b20d271b3bd025c91382dd79c98c0591210502cee',
    S / 'independent-http-gc-controllers-source-review-v1': '23738f9606e41b4e986576a4512a252206f9d684cc054104ea4586ee5052185c',
}


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
    row = dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))
    if expected:
        assert row == {k: expected[k] for k in row}
    return raw, row


def review():
    inputs, families, reversals = [], [], []
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
    for root, expected_edits in [(HTTP, 7), (GC, 3)]:
        derivation = json.loads((root / 'derivations.json').read_bytes())
        before, observed = checked(derivation['source']['path'], derivation['source'])
        inputs.append(observed)
        edits = derivation['edits']
        assert len(edits) == expected_edits
        text = before.decode()
        for edit in edits:
            assert text.count(edit['before']) == edit['count'] == 1
            text = text.replace(edit['before'], edit['after'])
        after = (root / 'controller.py').read_bytes()
        assert text.encode() == after
        for edit in reversed(edits):
            assert text.count(edit['after']) == 1
            text = text.replace(edit['after'], edit['before'])
        assert text.encode() == before
        reversals.append(dict(afterimage=str(root / 'controller.py'), edits=len(edits), forwardExact=True, reverseExact=True))

    source = (HTTP / 'controller.py').read_text()
    tree = ast.parse(source)
    names = {'identity', 'discover', 'group_model'}
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in functions} == names
    assert not any(isinstance(n, (ast.Import, ast.ImportFrom)) for f in functions for n in ast.walk(f))
    pure = {}
    exec(compile(ast.Module(body=functions, type_ignores=[]), '<actual-v2-three-pure-models>', 'exec'), pure)
    monitor = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'monitor')
    completion = [n for n in monitor.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in {'remaining_observed_pids', 'complete'} for t in n.targets)]
    assert len(completion) == 2
    predicate = compile(ast.Module(body=completion, type_ignores=[]), '<actual-v2-two-pure-completion-statements>', 'exec')
    def row(pid, ppid, pgid, birth='held-birth', command='benign-model'):
        return dict(pid=pid, ppid=ppid, pgid=pgid, birth=birth, command=command)
    root = row(100, 1, 100)
    cases = []
    test_cases = [
        ('leaderless-unobserved-session', {100: root, 102: row(102, 100, 101)}, {102: row(102, 1, 101)}, 101, False, False),
        ('known-current-pgid-migration', {100: root, 102: row(102, 100, 100)}, {102: row(102, 1, 102)}, 102, False, False),
        ('reused-pid-new-birth-and-group', {100: root, 102: row(102, 100, 100)}, {102: row(102, 1, 777, birth='replacement')}, 777, False, False),
        ('known-root-birth-changed', {100: root}, {100: row(100, 1, 100, birth='replacement')}, 100, False, False),
        ('known-root-command-changed', {100: root}, {100: row(100, 1, 100, command='replacement')}, 100, False, False),
        ('captured-session-leader-gone-member-remains', {100: root, 101: row(101, 100, 101), 102: row(102, 101, 101)}, {102: row(102, 1, 101)}, 101, True, False),
        ('actual-parent-current-identity', {100: root}, {100: root}, 100, True, False),
        ('all-known-gone', {100: root, 101: row(101, 100, 101)}, {}, 100, False, True),
    ]
    for name, known, rows, target_group, signal_allowed, complete in test_cases:
        before = json.dumps(known, sort_keys=True)
        pure['discover'](rows, known, 100)
        assert json.dumps(known, sort_keys=True) == before
        groups = pure['group_model'](rows, known, 100)
        group = next(g for g in groups if g['pgid'] == target_group)
        assert group['signalAllowed'] is signal_allowed
        frame = dict(child=object(), final_groups=groups, known=known, final_rows=rows)
        exec(predicate, frame)
        assert frame['complete'] is complete
        assert frame['remaining_observed_pids'] == sorted(set(known) & set(rows))
        cases.append(dict(name=name, known=list(known.values()), current=list(rows.values()), groups=groups, remainingObservedPids=frame['remaining_observed_pids'], completion=frame['complete'], targetGroupSignalAllowed=group['signalAllowed']))
    # Every signal path consults the same group model and rejects unsigned ownership.
    assert "if not group['signalAllowed']:" in source and "errors.append(dict(stage='unknown-current-group-identity', group=group))" in source
    assert source.count('final_rows = observe()') == 2
    assert "forcedCleanup=forced_cleanup, remainingObservedPids=remaining_observed_pids" in source

    benign = json.loads((HTTP / 'benign-inputs.json').read_bytes())
    assert len(benign['files']) == 18
    for row in benign['files']:
        _, observed = checked(row['path'], row)
        inputs.append(observed)
    summary = json.loads((HTTP / 'evidence/stdout.log').read_text().splitlines()[-1])
    author_terminal = json.loads((HTTP / 'evidence/terminal.json').read_bytes())
    assert summary['checks'] == 35 and author_terminal['rawExitCode'] == 0
    assert author_terminal['argv'][1] == str(HTTP / 'test-controller.py')
    sessions = []
    for entry in summary['benignOwnedSessions']:
        expected = entry['terminal']
        assert expected in benign['files']
        value = json.loads(Path(expected['path']).read_bytes())
        assert value['allObservedOwnedGroupsGone'] is True and value['remainingObservedPids'] == [] and value['errors'] == []
        for field in ('stdout', 'stderr'):
            assert value[field] in benign['files']
            checked(value[field]['path'], value[field])
        owned = [json.loads(Path(r['path']).read_bytes()) for r in benign['files'] if Path(r['path']).parent == Path(expected['path']).parent and Path(r['path']).name.startswith('owned-')]
        assert [r['sequence'] for r in sorted(owned, key=lambda r:r['sequence'])] == list(range(len(owned)))
        assert [r['process'] for r in sorted(owned, key=lambda r:r['sequence'])] == value['observedProcesses']
        assert all(not g['alive'] for g in value['finalGroups'])
        if entry['name'] == 'normal':
            assert value['rawExitCode'] == 0 and not value['forcedCleanup'] and not value['timeout'] and not value['signals']
        elif entry['name'] == 'bounded-timeout':
            assert value['rawExitCode'] < 0 and value['forcedCleanup'] and value['timeout'] and value['signals']
        else:
            assert entry['name'] == 'parent-exit-owned-descendant'
            descendant_pid = int(Path(value['stdout']['path']).read_text())
            assert value['rawExitCode'] == 0 and value['forcedCleanup'] and not value['timeout']
            assert descendant_pid in {r['pid'] for r in value['observedProcesses']}
            assert any(r['pgid'] == descendant_pid for r in value['signals'])
        sessions.append(dict(name=entry['name'], terminal=expected, rawExitCode=value['rawExitCode'], forcedCleanup=value['forcedCleanup'], timeout=value['timeout'], remainingObservedPids=value['remainingObservedPids']))
    gc_source = (GC / 'controller.py').read_text()
    ast.parse(gc_source)
    assert "module.monitor(argv,str(REPO),environment,OUT,600,config['rootAuthority'])" in gc_source.replace(' ', '')
    # Supplemental independent caller delta audit is data; it does not approve the monitor.
    supplemental = dict(path='/private/tmp/starling-node-compat/independent-gc-stage-caller-v2-delta-audit.json', sha256='af2a5c1a781aab47b0abcc0bb92dee16257bc479944a5117715b1224eb618436', bytes=2362)
    _, observed = checked(supplemental['path'], supplemental)
    inputs.append(observed)
    unique = {r['path']:r for r in inputs}
    for r in unique.values():
        checked(r['path'], r)
    return dict(schemaVersion=1, families=families, inputs=list(unique.values()), derivations=reversals, pureModels=cases, authorBenignEvidence=dict(checks=35, sessions=sessions, actualAuthorBenignInfrastructureInvoked=True, reviewerReranBenignSessions=False), sourceRecheckPassed=True, controllerImported=False, monitorOrSnapshotInvoked=False, processesOrSignalsInvoked=False)


if __name__ == '__main__':
    value = review()
    with (HERE / 'observations.json').open('x') as out:
        json.dump(value, out, indent=2)
        out.write('\n')
    print(json.dumps(dict(state='INDEPENDENT_V2_CONTROLLER_SOURCE_CORRECTION_CHECKS_PASSED', families=len(value['families']), uniqueInputs=len(value['inputs']), pureModels=len(value['pureModels']), sourceEdits=sum(r['edits'] for r in value['derivations']), operationalActionsInvoked=False)))
