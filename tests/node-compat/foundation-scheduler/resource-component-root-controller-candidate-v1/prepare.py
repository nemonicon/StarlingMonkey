"""Source and pure-model preparation only. Never imports the action controller."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def row(path):
    data = Path(path).read_bytes()
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def write(name, value):
    with (HERE / name).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    assert __debug__
    text = (HERE / 'controller.py').read_text()
    tree = ast.parse(text)
    functions = {v.name: v for v in tree.body if isinstance(v, ast.FunctionDef)}
    assert set(functions) == {'row', 'checked', 'load', 'family', 'write', 'action_model', 'owned_clean', 'inventory', 'main'}
    # Extract only two IO-free definitions into a fresh explicit namespace.
    environment = dict(Path=Path, OUTPUT_BASE=Path('/private/tmp/starling-node-compat/scheduler-resource-component-v1'), FIXTURES=('resource', 'pure', 'fatal', 'init-fatal'))
    module = ast.Module(body=[functions['action_model'], functions['owned_clean']], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), '<isolated pure controller models>', 'exec'), environment)
    checks = 0
    for fixture in environment['FIXTURES']:
        model = environment['action_model'](fixture)
        assert model == dict(fixture=fixture, outputRoot=str(environment['OUTPUT_BASE']) + '-' + fixture, externalRoot=str(environment['OUTPUT_BASE']) + '-' + fixture + '-external-root', timeoutSeconds=2400)
        checks += 1
    for fixture in ['', 'then', 'unknown', None, 0, '../resource', 'resource/old']:
        try:
            environment['action_model'](fixture)
        except AssertionError:
            checks += 1
        else:
            raise AssertionError('invalid fixture accepted')
    terminal = dict(allObservedOwnedGroupsGone=True, timeout=False, forcedCleanup=False, remainingObservedPids=[], errors=[], signals=[], interruptedSignals=[])
    assert environment['owned_clean'](terminal)
    checks += 1
    for key in terminal:
        bad = dict(terminal)
        bad[key] = [1] if isinstance(terminal[key], list) else not terminal[key]
        assert not environment['owned_clean'](bad)
        checks += 1
    assert text.index('monitor_index = family(MONITOR') < text.index('spec.loader.exec_module(monitor)') < text.index('terminal = monitor.monitor(')
    assert text.index('peer = dict(index=family(PEER') < text.index('terminal = monitor.monitor(')
    assert text.index('review_value = load(') < text.index('root_row = write(') < text.index('terminal = monitor.monitor(')
    assert "model['timeoutSeconds']" in text and "'construct'" in text
    assert "if __name__ == '__main__':" in text
    assert 'process.env.HOME' not in text and "environment['HOME']" not in text and 'module.HERE' not in text and 'module.SOURCE' not in text
    families = []
    for path, expected in [
        (HERE.parent / 'resource-component-candidate-v1', '74413aa9d1520139dc2ac4d8e43f0d99bab06477b8d8eb6e9d2db6bb58580055'),
        (HERE.parent / 'independent-resource-component-source-review-v1', 'dc452069b619be3a50dbf3bf71ba9487fe39194637da1dcb60806516a21fe02c'),
        (HERE.parents[1] / 'foundation-crypto/ownership-gc-build-controller-candidate-v1', '0afae87d0a1d7d32b272005cf6b252f9a318ed1799ff4c4605686c507d947f1b'),
    ]:
        descriptor = row(path / 'index.json')
        assert descriptor['sha256'] == expected
        index = json.loads((path / 'index.json').read_bytes())
        for member in index['files']:
            assert row(path / member['path']) == dict(member, path=str(path / member['path']))
        assert {p.relative_to(path).as_posix() for p in path.rglob('*') if p.is_file()} == {'index.json'} | {v['path'] for v in index['files']}
        families.append(descriptor)
    write('references.json', dict(schemaVersion=1, families=families, existingMonitorApi='monitor(argv,cwd,environment,output,timeout_seconds,authority)', outerTimeoutSeconds=2400, workerTimeoutSeconds=600, nativeOrGuestActionsInvoked=False))
    write('pure-source-results.json', dict(schemaVersion=1, state='RESOURCE_COMPONENT_ROOT_CONTROLLER_SOURCE_AND_PURE_CHECKS_PASSED_V1', pureCases=checks, parsedPython=['controller.py', 'prepare.py'], originalMonitorContextPreserved=True, actionControllerImported=False, sourceOnly=True, ownerActionsInvoked=False, actualRootAuthority=None, actualConstruction=None))
    write('future-source-peer-contract.json', dict(schemaVersion=1, state='INDEPENDENT_RESOURCE342_COMPONENT_ROOT_CONTROLLER_SOURCE_REVIEW_PASSED_V1', controllerSourceIndexSha256=None, sourceOnly=True, sourceReviewPassed=True, ownerActionsInvoked=False, grantsAnyActionAuthority=False))
    members = [dict(row(path), path=path.name) for path in sorted(HERE.iterdir()) if path.is_file()]
    write('index.json', dict(schemaVersion=1, state='SOURCE_ONLY_RESOURCE_COMPONENT_ROOT_CONTROLLER_CANDIDATE_V1', files=members))
    print(json.dumps(dict(index=row(HERE / 'index.json'), members=len(members), pureCases=checks, ownerActionsInvoked=False)))


if __name__ == '__main__':
    main()
