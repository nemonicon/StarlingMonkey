"""Inert Source/argv/copy/packaging tests. Never call run(), npm or Next."""
from pathlib import Path
import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = Path(__file__).absolute().parent
ms = importlib.util.spec_from_file_location('app_builder_source_under_test', HERE / 'build.py')
m = importlib.util.module_from_spec(ms)
ms.loader.exec_module(m)


def main():
    cases = []

    def check(ok, name):
        if not ok:
            raise AssertionError(name)
        cases.append(name)

    def refuse(fn, name):
        try:
            fn()
        except (ValueError, FileExistsError, FileNotFoundError):
            cases.append(name)
            return
        raise AssertionError('Accepted: ' + name)

    spec, fixture, before, _ = m.source()
    check(before['regularFiles'] == 29 and before['bytes'] == 41174, 'exact genuine fixture29files41174B')
    check(spec['expectedNodeVersion'] == 'v22.14.0', 'Node22.14 mandatory')
    caps = spec['capsSeconds']
    commands = m.command_plan('/tools/node', '/tools/npm/bin/npm-cli.js', '/owned', caps)
    check(commands[2] == dict(id='npm-ci', argv=['/tools/node', '/tools/npm/bin/npm-cli.js', 'ci', '--ignore-scripts', '--no-audit', '--no-fund'], cwd='/owned/application', seconds=600), 'actual historical locked npm argv/cap')
    check(commands[3] == dict(id='next-build', argv=['/tools/node', '/owned/application/node_modules/next/dist/bin/next', 'build', '--webpack'], cwd='/owned/application', seconds=900), 'actual webpack argv/cap')
    check([x['id'] for x in commands] == ['node-version', 'npm-version', 'npm-ci', 'next-build'], 'no corpus/server/browser/guest phases')
    env = m.environment('/tools/node', '/owned', {'HOME': '/real-home', 'USER': 'real-user', 'NODE_OPTIONS': '--unsafe', 'NODE_COMPILE_CACHE': '/old', 'NPM_CONFIG_CACHE': '/old'})
    check(env['HOME'] == '/real-home' and env['USER'] == 'real-user', 'HOME/USER preserved')
    check(env['NPM_CONFIG_CACHE'] == '/owned/npm-cache' and env['TMPDIR'] == '/owned/tmp', 'private owned cache/temp')
    check('NODE_OPTIONS' not in env and 'NODE_COMPILE_CACHE' not in env, 'no ambient Node options/cache')
    check(env['NEXT_TELEMETRY_DISABLED'] == env['CI'] == '1' and env['NODE_ENV'] == 'production', 'real build environment')
    good = dict(rawExitCode=0, timeout=False, forcedCleanup=False, parentOwnedGroupGone=True,
                allObservedOwnedGroupsGone=True, errors=[], signals=[], interruptedSignals=[],
                remainingObservedPids=[], finalGroups=[dict(alive=False)])
    check(m.clean(good), 'clean raw0 predicate')
    for key, value in [('rawExitCode', 1), ('rawExitCode', False), ('timeout', True), ('forcedCleanup', True),
                       ('parentOwnedGroupGone', False), ('allObservedOwnedGroupsGone', False),
                       ('errors', ['error']), ('signals', [15]), ('interruptedSignals', [2]),
                       ('remainingObservedPids', [123]), ('finalGroups', [dict(alive=True)])]:
        bad = copy.deepcopy(good)
        bad[key] = value
        check(not m.clean(bad), 'terminal refusal ' + key + repr(value))
    for key in good:
        bad = copy.deepcopy(good)
        del bad[key]
        check(not m.clean(bad), 'missing terminal field ' + key)
    m.validate_version(b'v22.14.0\n', b'', 'v22.14.0')
    cases.append('version parser exact Node')
    refuse(lambda: m.validate_version(b'v24.0.0\n', b'', 'v22.14.0'), 'wrong actual Node refuses')
    refuse(lambda: m.validate_version(b'v22.14.0\n', b'warning', 'v22.14.0'), 'version stderr refuses')
    refuse(lambda: m.tools(None, None), 'missing explicit tools refuses')
    for value in ('../x', '/absolute', 'a//b', 'a\\b', ''):
        refuse(lambda: m.relative(value), 'relative path refuses ' + repr(value))

    with tempfile.TemporaryDirectory(prefix='next-app-source-test-', dir='/private/tmp') as t:
        root = Path(t)
        dst = root / 'fixture-copy'
        copied = m.copy_tree(fixture, dst)
        check(copied['regularFiles'] == 29, 'real fixture copied without executing it')
        refuse(lambda: m.copy_tree(fixture, dst), 'copy overwrite refuses')
        alias = root / 'alias'
        alias.symlink_to(dst, target_is_directory=True)
        refuse(lambda: m.real(alias), 'output alias refuses')
        refuse(lambda: m.real(alias / 'child', exists=False), 'output ancestor alias refuses')
        link = dst / 'unlisted-link'
        link.symlink_to(fixture / 'package.json')
        refuse(lambda: m.inventory(dst), 'fixture or output symlink refuses')
        link.unlink()

        # Synthetic packaging DATA, deliberately not a framework build result.
        app = root / 'synthetic-packaging-data'
        standalone = app / '.next/standalone'
        standalone.mkdir(parents=True)
        (standalone / 'server.js').write_text('// synthetic nonexecuted packaging data\n')
        for name, data in [('.next/static/chunk.js', b'not executed'), ('public/fixture.txt', b'asset'),
                           ('.next/standalone/fixtures/message.txt', (fixture / 'fixtures/message.txt').read_bytes()),
                           ('.next/BUILD_ID', b'dynamic-test-id\n')]:
            p = app / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        for name, version in spec['exactVersions'].items():
            p = app / 'node_modules' / name / 'package.json'
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(dict(version=version)))
        action = app / '.next/server/server-reference-manifest.json'
        action.parent.mkdir(parents=True)
        action.write_text(json.dumps(dict(node={'fresh-action-A': {}}, edge={})))
        value = m.package(app, fixture)
        check(value['actualBuildId'] == 'dynamic-test-id' and value['actualActionIds']['node'] == ['fresh-action-A'], 'dynamic identifiers read from DATA not hardcoded baseline')
        check({r['path'] for r in value['applicationInventory']['files']} == {'server.js', 'fixtures/message.txt', '.next/static/chunk.js', 'public/fixture.txt'}, 'finite static/public/traced fixture packaging')
        refuse(lambda: m.package(app, fixture), 'packaging collision refuses')
        # A missing traced file is refused, never fabricated. Remove only the
        # owned prior copied static/public nodes so this tests the tracing gate.
        import shutil
        shutil.rmtree(standalone / '.next/static')
        shutil.rmtree(standalone / 'public')
        (standalone / 'fixtures/message.txt').unlink()
        refuse(lambda: m.package(app, fixture), 'missing trace refuses without fallback')
        check(not (standalone / 'fixtures/message.txt').exists(), 'missing fixture not silently installed')
        cli = subprocess.run([sys.executable, '-I', '-B', str(HERE / 'build.py'), '--plan', '--output', str(root / 'never-created')], capture_output=True, timeout=30)
        check(cli.returncode == 0 and cli.stderr == b'', 'real read-only plan CLI')
        plan = json.loads(cli.stdout)
        check(plan['state'] == 'NEXT_APP_BUILD_PLAN_ONLY_V1' and not plan['buildExecuted'] and not plan['buildPathActuallyTested'] and plan['toolInputs'] is None, 'plan incomplete tools explicit/no execution claim')
        check(not (root / 'never-created').exists(), 'plan creates no output/cache')
    check(m.inventory(fixture) == before, 'original fixture untouched')
    return dict(schemaVersion=1, sourceChecksPassed=True, checks=len(cases), cases=cases,
                actualNodeNpmNextOrNetworkExecuted=False, actualAppBuildExecuted=False,
                buildPathActuallyTested=False, syntheticPackagingDataOnly=True,
                freshStandaloneRuntimeAccepted=False, compilerOrGuestExecuted=False)


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
