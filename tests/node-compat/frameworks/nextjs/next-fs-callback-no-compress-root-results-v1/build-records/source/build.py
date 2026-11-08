"""Plan by default; explicit fresh --output builds only the pinned Next app.

No server, browser, historical corpus, native engine or guest execution.
--plan --output PATH prints a concrete plan without creating PATH.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import stat

HERE = Path(__file__).absolute().parent
REPO = HERE.parents[4]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def real(path, exists=True):
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts, 'Canonical absolute path required')
    require(not any(x.is_symlink() for x in (path, *path.parents)), 'Symlink path refused')
    require(path.resolve(strict=exists) == path, 'Path alias refused')
    return path


def row(path):
    path = real(path)
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, 'Unique regular file required')
    data = path.read_bytes()
    after = path.lstat()
    require(all(getattr(before, k) == getattr(after, k) for k in
                ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns', 'st_mode', 'st_nlink')), 'File changed during read')
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def same(ref):
    require(row(ref['path']) == ref, 'Input changed: ' + ref['path'])


def load(path):
    ref = row(path)
    data = Path(path).read_bytes()
    require(hashlib.sha256(data).hexdigest() == ref['sha256'], 'JSON changed while reading')
    return json.loads(data), ref


def relative(name):
    require(type(name) is str and name and '\\' not in name and '\0' not in name,
            'Invalid relative path')
    require(not any(x in ('', '.', '..') for x in name.split('/')), 'Unsafe relative path')
    return Path(*name.split('/'))


def inventory(root, internal_links=False):
    """Dynamic physical file inventory; no previous build's identities reused."""
    root = real(root)
    require(root.is_dir(), 'Inventory root missing')
    files, dirs, links = [], [], []
    for p in sorted(root.rglob('*')):
        s = p.lstat()
        name = p.relative_to(root).as_posix()
        if p.is_symlink():
            target = os.readlink(p)
            resolved = p.resolve(strict=True)
            require(internal_links and not Path(target).is_absolute() and root in resolved.parents,
                    'Tree symlink refused: ' + str(p))
            links.append(dict(path=name, target=target, dev=s.st_dev, ino=s.st_ino))
            continue
        if p.is_dir():
            dirs.append(dict(path=name, mode=stat.S_IMODE(s.st_mode), dev=s.st_dev, ino=s.st_ino))
        else:
            r = row(p)
            files.append(dict(r, path=name, mode=stat.S_IMODE(s.st_mode), dev=s.st_dev,
                              ino=s.st_ino, nlink=s.st_nlink))
    return dict(schemaVersion=1, root=str(root), files=files, directories=dirs,
                regularFiles=len(files), bytes=sum(x['bytes'] for x in files), symlinks=links)


def source(repo=REPO):
    repo = real(repo)
    spec, specrow = load(repo / 'tests/node-compat/frameworks/nextjs/next-fs-callback-no-compress-app-build-v1/fixture-inputs.json')
    fixture = repo / relative(spec['repositoryFixture'])
    actual = inventory(fixture)
    expected = spec['files']
    require([{k: r[k] for k in ('path', 'sha256', 'bytes')} for r in actual['files']] == expected,
            'Fixture whole file membership/hash differs')
    require([r['path'] for r in actual['directories']] == spec['directories'], 'Fixture directory membership differs')
    package, _ = load(fixture / 'package.json')
    lock, _ = load(fixture / 'package-lock.json')
    require(package['dependencies'] == spec['exactVersions'] == lock['packages']['']['dependencies'], 'Exact fixture dependencies differ')
    require(all(lock['packages']['node_modules/' + k]['version'] == v for k, v in spec['exactVersions'].items()), 'Locked package versions differ')
    contract = row(repo / relative(spec['contractRepositoryPath']))
    require(contract['sha256'] == spec['contractSha256'], 'Contract changed')
    monitor = row(repo / relative(spec['monitorRepositoryPath']))
    require(monitor['sha256'] == spec['monitorSha256'], 'Original ownership monitor changed')
    return spec, fixture, actual, [specrow, contract, monitor, row(Path(__file__).absolute())]


def tools(node, npm_cli):
    require(node is not None and npm_cli is not None, 'Explicit --node and --npm-cli required to build')
    node, npm_cli = real(node), real(npm_cli)
    require(node.name == 'node' and os.access(node, os.X_OK), 'Real executable Node path required')
    require(npm_cli.name == 'npm-cli.js' and npm_cli.parent.name == 'bin', 'Explicit npm bin/npm-cli.js required')
    package_root = npm_cli.parent.parent
    package, package_row = load(package_root / 'package.json')
    require(package['name'] == 'npm' and type(package['version']) is str and package['version'], 'Real npm package required')
    return dict(node=row(node), npmCli=row(npm_cli), npmPackage=package_row,
                npmVersion=package['version'], npmTree=inventory(package_root, internal_links=True))


def environment(node, output, inherited):
    env = {k: inherited[k] for k in ('HOME', 'USER', 'LOGNAME') if k in inherited}
    env.update(PATH=str(Path(node).parent) + ':/usr/bin:/bin', LANG='C', LC_ALL='C',
               NEXT_TELEMETRY_DISABLED='1', CI='1', NODE_ENV='production',
               NPM_CONFIG_CACHE=str(Path(output) / 'npm-cache'), TMPDIR=str(Path(output) / 'tmp'),
               NPM_CONFIG_USERCONFIG=str(Path(output) / 'empty-user.npmrc'),
               NPM_CONFIG_GLOBALCONFIG=str(Path(output) / 'empty-global.npmrc'))
    return env


def command_plan(node, npm_cli, output, caps):
    app = str(Path(output) / 'application')
    return [dict(id='node-version', argv=[str(node), '--version'], cwd=str(output), seconds=caps['node-version']),
            dict(id='npm-version', argv=[str(node), str(npm_cli), '--version'], cwd=str(output), seconds=caps['npm-version']),
            dict(id='npm-ci', argv=[str(node), str(npm_cli), 'ci', '--ignore-scripts', '--no-audit', '--no-fund'], cwd=app, seconds=caps['npm-ci']),
            dict(id='next-build', argv=[str(node), str(Path(app) / 'node_modules/next/dist/bin/next'), 'build', '--webpack'], cwd=app, seconds=caps['next-build'])]


def clean(t):
    return (type(t.get('rawExitCode')) is int and t['rawExitCode'] == 0 and
            t.get('timeout') is False and t.get('forcedCleanup') is False and
            t.get('parentOwnedGroupGone') is True and t.get('allObservedOwnedGroupsGone') is True and
            all(t.get(k) == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids')) and
            type(t.get('finalGroups')) is list and all(g.get('alive') is False for g in t['finalGroups']))


def validate_version(stdout, stderr, expected):
    require(stderr == b'' and stdout.decode('utf8').strip() == expected, 'Actual tool version differs')


def write_new(path, data, mode=0o600):
    real(path.parent)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fchmod(stream.fileno(), mode)
        os.fsync(stream.fileno())


def save(path, value):
    write_new(path, (json.dumps(value, indent=2) + '\n').encode())


def copy_tree(src, dst):
    before = inventory(src)
    require(not dst.exists() and not dst.is_symlink(), 'Copy destination already exists')
    real(dst.parent)
    dst.mkdir(mode=0o700)
    for d in before['directories']:
        (dst / relative(d['path'])).mkdir(mode=0o700)
    for r in before['files']:
        p = src / relative(r['path'])
        data = p.read_bytes()
        require(hashlib.sha256(data).hexdigest() == r['sha256'], 'Copy source changed')
        write_new(dst / relative(r['path']), data)
    after = inventory(src)
    require(after == before, 'Copy source changed during copy')
    copied = inventory(dst)
    require([{k: r[k] for k in ('path', 'sha256', 'bytes')} for r in copied['files']] ==
            [{k: r[k] for k in ('path', 'sha256', 'bytes')} for r in before['files']], 'Copy bytes differ')
    require(all((a['dev'], a['ino']) != (b['dev'], b['ino']) for a, b in zip(before['files'], copied['files'])), 'Copy aliases input')
    return copied


def package(app, fixture):
    standalone = app / '.next/standalone'
    require((standalone / 'server.js').is_file(), 'Real standalone server missing')
    copy_tree(app / '.next/static', standalone / '.next/static')
    copy_tree(app / 'public', standalone / 'public')
    # next.config.mjs explicitly traces this file. Missing tracing is a failure,
    # never repaired by silently fabricating an extra runtime file.
    require((standalone / 'fixtures/message.txt').read_bytes() == (fixture / 'fixtures/message.txt').read_bytes(), 'Traced runtime fixture missing/changed')
    installed = installed_versions(app)

    build_id = (app / '.next/BUILD_ID').read_text().strip()
    require(build_id and len(build_id) <= 256 and '\0' not in build_id, 'Actual build ID missing')
    actions, action_row = load(app / '.next/server/server-reference-manifest.json')
    require(type(actions.get('node')) is dict and type(actions.get('edge')) is dict, 'Actual action manifest shape')
    require(set(actions['node']) | set(actions['edge']), 'Fixture action IDs missing')
    return dict(applicationInventory=inventory(standalone), installedVersions=installed,
                actualBuildId=build_id, buildIdFile=row(app / '.next/BUILD_ID'),
                serverReferenceManifest=action_row,
                actualActionIds=dict(node=sorted(actions['node']), edge=sorted(actions['edge'])))


def installed_versions(app):
    installed = {}
    for name in ('next', 'react', 'react-dom'):
        installed[name] = load(app / 'node_modules' / name / 'package.json')[0]['version']
    require(installed == {'next': '16.4.5', 'react': '19.3.1', 'react-dom': '19.3.1'}, 'Installed versions differ')
    return installed


def run(output, node, npm_cli):
    output = real(output, exists=False)
    require(not output.exists() and output.parent.is_dir() and REPO not in output.parents,
            'Fresh output outside checkout required')
    spec, fixture, fixture_before, refs = source()
    tool = tools(node, npm_cli)
    env = environment(tool['node']['path'], output, os.environ)
    commands = command_plan(tool['node']['path'], tool['npmCli']['path'], output, spec['capsSeconds'])
    result = dict(schemaVersion=1, state='NEXT_APP_BUILD_FAILED_OR_PARTIAL_V1', passed=False,
                  sourceOnlyPreparation=False, outputRoot=str(output), phases=[], errors=[],
                  applicationInventory=None, runtimeOrNativeEngineExecuted=False)
    output.mkdir(mode=0o700)
    for name in ('npm-cache', 'tmp', 'commands'):
        (output / name).mkdir(mode=0o700)
    for name in ('empty-user.npmrc', 'empty-global.npmrc'):
        write_new(output / name, b'')
    plan_path = output / 'plan.json'
    save(plan_path, dict(schemaVersion=1, commands=commands, environment=env, node=tool['node'],
                         npmCli=tool['npmCli'], npmPackage=tool['npmPackage'], expectedNodeVersion=spec['expectedNodeVersion']))
    save(output / 'fixture-before.json', fixture_before)
    save(output / 'npm-before.json', tool['npmTree'])

    def protect():
        for r in refs + [tool['node'], tool['npmCli'], tool['npmPackage']]:
            same(r)
        require(inventory(fixture) == fixture_before, 'Original fixture changed')
        require(inventory(Path(tool['npmTree']['root']), internal_links=True) == tool['npmTree'], 'Original npm tools changed')

    try:
        copy_tree(fixture, output / 'application')
        monitor_path = REPO / spec['monitorRepositoryPath']
        modspec = importlib.util.spec_from_file_location('original_app_build_owned_monitor', monitor_path)
        monitor = importlib.util.module_from_spec(modspec)
        modspec.loader.exec_module(monitor)
        for command in commands:
            protect()
            logs = output / 'commands' / command['id']
            logs.mkdir(mode=0o700)
            terminal = monitor.monitor(command['argv'], command['cwd'], env, logs,
                                       command['seconds'], row(plan_path))
            result['phases'].append(dict(command=command, terminal=row(logs / 'terminal.json'),
                                         stdout=row(logs / 'stdout.log'), stderr=row(logs / 'stderr.log')))
            protect()
            require(clean(terminal), 'Command did not finish raw0/clean: ' + command['id'])
            if command['id'] in ('node-version', 'npm-version'):
                expected = spec['expectedNodeVersion'] if command['id'] == 'node-version' else tool['npmVersion']
                validate_version((logs / 'stdout.log').read_bytes(), (logs / 'stderr.log').read_bytes(), expected)
            if command['id'] == 'npm-ci':
                result['installedVersionsBeforeNextBuild'] = installed_versions(output / 'application')
                for name in ('package.json', 'package-lock.json'):
                    require((output / 'application' / name).read_bytes() == (fixture / name).read_bytes(), 'Owned package/lock changed before Next')
        for name in ('package.json', 'package-lock.json'):
            require((output / 'application' / name).read_bytes() == (fixture / name).read_bytes(), 'Owned package/lock changed')
        result.update(package(output / 'application', fixture))
        save(output / 'application-inputs.json', result['applicationInventory'])
        result['applicationInventoryDescriptor'] = row(output / 'application-inputs.json')
        result['state'] = 'NEXT_APP_BUILD_PASSED_UNREVIEWED_V1'
        result['passed'] = True
    except BaseException as error:
        result['errors'].append(dict(stage='build-or-package', type=type(error).__name__, message=str(error)))
    finally:
        try:
            protect()
            result['originalInputsPreserved'] = True
        except BaseException as error:
            result['originalInputsPreserved'] = False
            result['passed'] = False
            result['errors'].append(dict(stage='final-protection', type=type(error).__name__, message=str(error)))
        if not result['passed']:
            result['state'] = 'NEXT_APP_BUILD_FAILED_OR_PARTIAL_V1'
        save(output / 'result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--node', type=Path)
    parser.add_argument('--npm-cli', type=Path)
    args = parser.parse_args()
    if args.plan or args.output is None:
        spec, fixture, _, _ = source()
        tool = tools(args.node, args.npm_cli) if args.node or args.npm_cli else None
        root = str(real(args.output, exists=False)) if args.output else '{FRESH_OUTPUT}'
        if args.output:
            require(not args.output.exists() and REPO not in args.output.parents, 'Proposed output not fresh/outside checkout')
        node = tool['node']['path'] if tool else '{NODE_22_14_0}'
        npm = tool['npmCli']['path'] if tool else '{NPM_CLI_JS}'
        env = environment(node, root, os.environ)
        if not tool:
            env['PATH'] = '{NODE_DIRECTORY}:/usr/bin:/bin'
        print(json.dumps(dict(schemaVersion=1, state='NEXT_APP_BUILD_PLAN_ONLY_V1', buildExecuted=False,
                              buildPathActuallyTested=False, fixtureRoot=str(fixture), outputRoot=args.output and str(args.output),
                              expectedNodeVersion=spec['expectedNodeVersion'], actualVersionProbesRequired=True,
                              explicitToolsRequiredBeforeBuild=True, toolInputs=tool and {k: v for k, v in tool.items() if k != 'npmTree'},
                              commands=command_plan(node, npm, root, spec['capsSeconds']),
                              environment=env,
                              packaging=['real .next/standalone/server.js', 'copy .next/static', 'copy public', 'verify traced fixtures/message.txt', 'fresh dynamic inventory/BUILD_ID/action manifest']), indent=2))
        return 0
    result = run(args.output, args.node, args.npm_cli)
    print(json.dumps({k: result[k] for k in ('state', 'passed', 'outputRoot', 'errors')}, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
