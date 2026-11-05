"""Root-owned construction observer. Uses the unchanged original 0af monitor."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
import time

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'ownership-secret-component-candidate-v2'
MONITOR = HERE / 'ownership-gc-build-controller-candidate-v1/monitor.py'
MONITOR_SHA = '86913867251bc889701859ca6a361ccf9c17288a6a3bfc7a5c8d8e5bbe5c4cbe'


def row(path):
    p = Path(path)
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return dict(path=str(p), sha256=h.hexdigest(), bytes=p.stat().st_size)


def read(path):
    return json.loads(Path(path).read_bytes())


def clean_environment(environment, required, tempdir):
    result = dict(environment)
    removed = []
    exact = {'NODE_OPTIONS', 'NODE_PATH', 'PYTHONPATH', 'PYTHONHOME', 'PYTHONOPTIMIZE',
             'LD_PRELOAD', 'LD_LIBRARY_PATH', 'BASH_ENV', 'ENV', 'SHELLOPTS', 'BASHOPTS', 'CDPATH', 'GLOBIGNORE'}
    for key in list(result):
        if key in exact or key.startswith(('NODE_COMPAT_', 'NAPI_RS_', 'DYLD_', 'BASH_FUNC_')):
            del result[key]
            removed.append(key)
    result.update(required)
    result['TMPDIR'] = str(tempdir)
    assert all(result.get(k) == environment.get(k) for k in ['HOME', 'home', 'CODEX_HOME'])
    return result, sorted(removed)


def terminal_success(terminal):
    return (isinstance(terminal, dict) and terminal.get('schemaVersion') == 1
            and terminal.get('rawExitCode') == 0
            and terminal.get('allObservedOwnedGroupsGone') is True
            and terminal.get('parentOwnedGroupGone') is True
            and terminal.get('timeout') is False and terminal.get('forcedCleanup') is False
            and terminal.get('remainingObservedPids') == []
            and terminal.get('interruptedSignals') == [] and terminal.get('signals') == []
            and terminal.get('errors') == [])


def main():
    assert len(sys.argv) == 2, 'One config descriptor JSON'
    begin = time.monotonic()
    config_descriptor = json.loads(sys.argv[1])
    assert row(config_descriptor['path']) == config_descriptor
    config = read(config_descriptor['path'])
    ix = config['sourceIndex']
    assert ix['path'] == str(SOURCE / 'index.json') and row(ix['path']) == ix
    refs = read(SOURCE / 'references.json')
    ledger = read(SOURCE / 'source-inputs.json')
    protected = {r['path']: r for r in ledger['files']}
    families = list(ledger['families']) + [ix]
    assert row(config['rootAuthority']['path']) == config['rootAuthority']
    authority = read(config['rootAuthority']['path'])
    families.append(authority['sourceIndependentReview']['index'])
    protected[config_descriptor['path']] = config_descriptor
    protected[config['rootAuthority']['path']] = config['rootAuthority']
    for family in families:
        assert row(family['path']) == family
        protected[family['path']] = family
        for member in read(family['path'])['files']:
            r = dict(member, path=str(Path(family['path']).parent / member['path']))
            if r['path'] in protected:
                assert protected[r['path']] == r
            protected[r['path']] = r
    protected[str(MONITOR)] = dict(path=str(MONITOR), sha256=MONITOR_SHA, bytes=15094)
    launcher = row(__file__)
    assert authority['rootLauncher'] == launcher
    protected[launcher['path']] = launcher

    def recheck():
        for r in protected.values():
            assert row(r['path']) == r, r['path']
        for family in families:
            base = Path(family['path']).parent
            expected = {'index.json'} | {r['path'] for r in read(family['path'])['files']}
            actual = set()
            for p in base.rglob('*'):
                assert not p.is_symlink(), str(p)
                if p.is_file():
                    actual.add(p.relative_to(base).as_posix())
            assert actual == expected, str(base)

    recheck()
    required = refs['requiredPackagingEnvironment']
    assert authority['requiredPackagingEnvironment'] == required
    assert authority['componentInitializationAllowed'] is True
    for key in ['ordinaryGuestExportsAllowed', 'keyOrCryptoOperationsAllowed', 'generatedModuleImportAllowed', 'operationalAdmission']:
        assert authority[key] is False
    external = Path(refs['externalRoot'])
    observer = external.with_name(external.name + '-observer')
    assert not external.exists() and not observer.exists() and not Path(refs['outputRoot']).exists()
    external.mkdir(mode=0o700)
    observer.mkdir(mode=0o700)
    tempdir = observer / 'tmp'
    tempdir.mkdir(mode=0o700)
    node_output = external / 'node'
    node_output.mkdir(mode=0o700)
    environment, removed = clean_environment(os.environ, required, tempdir)
    env_observation = dict(schemaVersion=1, selectedEnvironment=required, removedVariableNames=removed,
                           homeValuesPreserved=True, wholeEnvironmentRetained=False, tempdir=str(tempdir))
    (observer / 'environment-policy.json').write_text(json.dumps(env_observation, indent=2) + '\n')
    spec = importlib.util.spec_from_file_location('original_0af_crypto_monitor', MONITOR)
    monitor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(monitor)
    argv = [refs['node']['path'], str(SOURCE / 'build.mjs'), json.dumps(config_descriptor, separators=(',', ':'))]
    terminal = None
    failure = None
    protection_error = None
    envelope = None
    try:
        terminal = monitor.monitor(argv, str(HERE.parents[2]), environment, str(node_output), 1800, authority)
        stdout = (node_output / 'stdout.log').read_text()
        lines = stdout.splitlines()
        if lines:
            try:
                envelope = json.loads(lines[-1])
            except json.JSONDecodeError:
                pass
    except BaseException as error:
        failure = dict(type=type(error).__name__, message=str(error))
    finally:
        try:
            recheck()
        except BaseException as error:
            protection_error = dict(type=type(error).__name__, message=str(error))
    elapsed = time.monotonic() - begin
    clean = terminal_success(terminal)
    passed = bool(clean and failure is None and protection_error is None and elapsed <= 2400 and envelope and envelope.get('completeUnreviewed') is True)
    observation = dict(schemaVersion=1, state='ROOT_OBSERVED_SECRET355_COMPONENT_CONSTRUCTION_ZERO_UNREVIEWED_V2' if passed else 'ROOT_OBSERVED_SECRET355_COMPONENT_CONSTRUCTION_FAILED_V2',
                       sourceIndex=ix, rootAuthority=config['rootAuthority'], config=config_descriptor, launcher=launcher,
                       actualArgv=argv, environmentPolicy=row(observer / 'environment-policy.json'),
                       terminal=row(node_output / 'terminal.json') if (node_output / 'terminal.json').exists() else None,
                       stdout=row(node_output / 'stdout.log') if (node_output / 'stdout.log').exists() else None,
                       stderr=row(node_output / 'stderr.log') if (node_output / 'stderr.log').exists() else None,
                       returnedEnvelope=envelope, error=failure, rootInputProtectionError=protection_error,
                       protectedFiles=len(protected), operationalWallSeconds=elapsed, nodeDeadlineSeconds=1800,
                       observedWholePhaseBudgetSeconds=2400, operationalPhaseBudgetSatisfied=elapsed <= 2400,
                       componentInitializationAllowed=True, ordinaryGuestExportsInvoked=False, keyOperationsInvoked=False,
                       generatedModuleImported=False, operationalAdmission=False, runtimeAcceptanceClaim=False,
                       requiresIndependentActualReview=True)
    data = json.dumps(observation, indent=2) + '\n'
    (observer / 'root-observation.json').write_text(data)
    (HERE / 'ownership-secret-component-v2-root-results.json').write_text(data)
    print(json.dumps(observation))
    return 0 if passed else 1


if __name__ == '__main__':
    sys.exit(main())
