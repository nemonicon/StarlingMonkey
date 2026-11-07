"""Read retained text DATA only; never import or execute the app/build sources."""
from pathlib import Path
import copy
import datetime
import gzip
import hashlib
import json

HERE = Path(__file__).absolute().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2) + '\n').encode()


def validate(data, rows, review):
    def raw(name):
        return data[name].encode('utf8')

    def read(name):
        return json.loads(data[name])

    def pinned(name, ref):
        b = raw(name)
        assert rows[name]['origin'] == ref['path']
        assert digest(b) == ref['sha256'] and len(b) == ref['bytes']

    def by_ref(ref):
        names = [n for n, row in rows.items() if row['origin'] == ref['path']]
        assert len(names) == 1
        pinned(names[0], ref)
        return names[0]

    result = read('raw/result.json')
    pinned('raw/result.json', review['actualResult'])
    assert result['state'] == 'NEXT_APP_BUILD_PASSED_UNREVIEWED_V1'
    assert result['passed'] is True and result['errors'] == []
    assert result['originalInputsPreserved'] is True
    assert result['runtimeOrNativeEngineExecuted'] is False
    assert result['sourceOnlyPreparation'] is False
    plan = read('raw/plan.json')
    plan_ref = dict(path=rows['raw/plan.json']['origin'],
                    sha256=digest(raw('raw/plan.json')), bytes=len(raw('raw/plan.json')))
    source_index = read('source/cli/index.json')
    pinned('source/cli/index.json', review['cliSourceIndex'])
    assert review['cliSourceIndex']['sha256'] == '0e19088378de7e0afab9686935bbb2ab7ded00ed7161f4a2c63c8362b84627ec'
    assert {n.removeprefix('source/cli/') for n in data if n.startswith('source/cli/')} == {'index.json'} | {r['path'] for r in source_index['files']}
    for row in source_index['files']:
        b = raw('source/cli/' + row['path'])
        assert digest(b) == row['sha256'] and len(b) == row['bytes']
    spec = read('source/cli/fixture-inputs.json')
    assert len(spec['files']) == 29 and sum(r['bytes'] for r in spec['files']) == 41174
    assert {n.removeprefix('source/fixture/') for n in data if n.startswith('source/fixture/')} == {r['path'] for r in spec['files']}
    for row in spec['files']:
        b = raw('source/fixture/' + row['path'])
        assert digest(b) == row['sha256'] and len(b) == row['bytes']
    fixture = read('raw/fixture-before.json')
    assert [{k: r[k] for k in ('path', 'sha256', 'bytes')} for r in fixture['files']] == spec['files']
    assert [r['path'] for r in fixture['directories']] == spec['directories']
    assert fixture['symlinks'] == []
    assert digest(raw('source/monitor.py')) == spec['monitorSha256']
    assert digest(raw('source/fixture-contract.json')) == spec['contractSha256']

    assert plan['node']['sha256'] == 'e2d4915d03eda6a2f00a09920e7eeb7a04ad123f9aaad61b1481179fe1bf50e0'
    assert plan['node']['bytes'] == 108619024
    pinned('tools/npm-cli.js', plan['npmCli'])
    pinned('tools/npm-package.json', plan['npmPackage'])
    npm_package = read('tools/npm-package.json')
    assert npm_package['name'] == 'npm' and npm_package['version'] == '10.9.2'
    npm = read('raw/npm-before.json')
    assert npm['regularFiles'] == len(npm['files']) == 2379
    assert npm['bytes'] == sum(r['bytes'] for r in npm['files']) == 11690702
    assert len(npm['directories']) == 561 and npm['symlinks'] == []
    for relative_name, role in [('bin/npm-cli.js', 'npmCli'), ('package.json', 'npmPackage')]:
        row = next(r for r in npm['files'] if r['path'] == relative_name)
        assert {k: row[k] for k in ('sha256', 'bytes')} == {k: plan[role][k] for k in ('sha256', 'bytes')}
    output = result['outputRoot']
    environment = plan['environment']
    assert environment['HOME'] == '/Users/dan'
    assert environment['PATH'] == str(Path(plan['node']['path']).parent) + ':/usr/bin:/bin'
    for key, suffix in [('NPM_CONFIG_CACHE', 'npm-cache'), ('TMPDIR', 'tmp'),
                        ('NPM_CONFIG_USERCONFIG', 'empty-user.npmrc'),
                        ('NPM_CONFIG_GLOBALCONFIG', 'empty-global.npmrc')]:
        assert environment[key] == output + '/' + suffix
    assert raw('raw/empty-user.npmrc') == raw('raw/empty-global.npmrc') == b''
    assert set(environment) == {'HOME', 'USER', 'LOGNAME', 'PATH', 'LANG', 'LC_ALL',
                                'NEXT_TELEMETRY_DISABLED', 'CI', 'NODE_ENV', 'NPM_CONFIG_CACHE',
                                'TMPDIR', 'NPM_CONFIG_USERCONFIG', 'NPM_CONFIG_GLOBALCONFIG'}
    assert environment['NODE_ENV'] == 'production'
    assert environment['CI'] == environment['NEXT_TELEMETRY_DISABLED'] == '1'
    ids = ['node-version', 'npm-version', 'npm-ci', 'next-build']
    caps = [120, 120, 600, 900]
    node, npm_cli = plan['node']['path'], plan['npmCli']['path']
    argv = [[node, '--version'], [node, npm_cli, '--version'],
            [node, npm_cli, 'ci', '--ignore-scripts', '--no-audit', '--no-fund'],
            [node, output + '/application/node_modules/next/dist/bin/next', 'build', '--webpack']]
    assert [p['command'] for p in result['phases']] == plan['commands']
    dates = []
    for i, phase in enumerate(result['phases']):
        command = phase['command']
        assert command == dict(id=ids[i], argv=argv[i],
                               cwd=output if i < 2 else output + '/application', seconds=caps[i])
        prefix = 'raw/commands/' + ids[i] + '/'
        terminal_name = by_ref(phase['terminal'])
        terminal = read(terminal_name)
        started = read(prefix + 'started.json')
        assert started['argv'] == argv[i] and started['timeoutSeconds'] == caps[i]
        assert started['authority'] == terminal['authority'] == plan_ref
        assert started['pid'] == terminal['pid']
        dates.append(datetime.datetime.fromisoformat(started['startedAtUtc']))
        assert type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0
        assert terminal['timeout'] is False and terminal['forcedCleanup'] is False
        assert terminal['parentOwnedGroupGone'] is True and terminal['allObservedOwnedGroupsGone'] is True
        assert all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
        assert type(terminal['finalGroups']) is list and all(g['alive'] is False for g in terminal['finalGroups'])
        assert terminal['operationalElapsedSeconds'] <= caps[i]
        for key in ('stdout', 'stderr'):
            assert terminal[key] == phase[key]
            assert by_ref(phase[key]) == prefix + key + '.log'
        assert raw(prefix + 'stderr.log') == b''
        events = [n for n in data if n.startswith(prefix + 'owned-')]
        assert events
        for name in events:
            event = read(name)
            assert type(event['sequence']) is int and event['sequence'] >= 0
            assert event['process']['pgid'] in {g['pgid'] for g in terminal['finalGroups']}
    assert len(dates) == 4 and dates == sorted(dates)
    assert raw('raw/commands/node-version/stdout.log') == b'v22.14.0\n'
    assert raw('raw/commands/npm-version/stdout.log') == b'10.9.2\n'
    assert 'Compiled successfully' in data['raw/commands/next-build/stdout.log']
    assert 'Next.js 16.4.5 (webpack)' in data['raw/commands/next-build/stdout.log']
    for name in ('package.json', 'package-lock.json'):
        assert raw('installed/' + name) == raw('source/fixture/' + name)
    wanted = {'next': '16.4.5', 'react': '19.3.1', 'react-dom': '19.3.1'}
    installed = {name: read('installed/' + name + '/package.json')['version'] for name in wanted}
    assert installed == result['installedVersionsBeforeNextBuild'] == result['installedVersions'] == wanted
    inventory = read('raw/application-inputs.json')
    pinned('raw/application-inputs.json', result['applicationInventoryDescriptor'])
    assert result['applicationInventory'] == inventory
    assert inventory['regularFiles'] == len(inventory['files']) == 2181
    assert inventory['bytes'] == sum(r['bytes'] for r in inventory['files']) == 48714867
    assert len(inventory['directories']) == 425 and inventory['symlinks'] == []
    assert len({r['path'] for r in inventory['files']}) == 2181
    assert all(r['nlink'] == 1 and not r['path'].startswith('/') and '..' not in Path(r['path']).parts for r in inventory['files'])
    assert inventory['root'] == output + '/application/.next/standalone'
    pinned('generated/BUILD_ID', result['buildIdFile'])
    assert data['generated/BUILD_ID'].strip() == result['actualBuildId'] == 'c2R8ovhEoFinJh6IvlO5M'
    actions = read('projections/server-reference.json')
    assert actions['originalDescriptor'] == result['serverReferenceManifest']
    installed_by_name = {r['path']: r for r in inventory['files']}
    for name, ref in [('.next/BUILD_ID', result['buildIdFile']),
                      ('.next/server/server-reference-manifest.json', result['serverReferenceManifest'])]:
        assert {k: installed_by_name[name][k] for k in ('sha256', 'bytes')} == {k: ref[k] for k in ('sha256', 'bytes')}
    traced = next(r for r in spec['files'] if r['path'] == 'fixtures/message.txt')
    assert {k: installed_by_name['fixtures/message.txt'][k] for k in ('sha256', 'bytes')} == {k: traced[k] for k in ('sha256', 'bytes')}
    assert actions['rawEncryptionKeyContentsRetained'] is False
    assert {k: sorted(actions[k]) for k in ('node', 'edge')} == result['actualActionIds']
    assert result['actualActionIds'] == {'node': ['40ca0bda6c41d5a4ff46cda3035ad9babb89d96900'], 'edge': []}
    previous = read('projections/old-new-identifiers.json')
    assert previous['oldBuildId'] != previous['newBuildId'] == result['actualBuildId']
    assert previous['oldActionIds'] != previous['newActionIds'] == result['actualActionIds']
    assert previous['oldPhysicalInventoryReused'] is False
    assert review['newAppServed'] is review['componentized'] is review['runtimeAccepted'] is False
    assert review['cleanMachineNativeBuildProved'] is review['adoption'] is False
    assert review['curatorExecutedNodeNpmNextOrActor'] is False
    return dict(phases=4, allRaw0Clean=True, fixtureFiles=29, npmToolFiles=2379,
                standaloneFiles=2181, standaloneBytes=48714867, standaloneDirectoriesExcludingRoot=425,
                appServedOrGuestOrNativeBuildClaimed=False)


def main():
    index = json.loads((HERE / 'index.json').read_text())
    assert {r['path'] for r in index['files']} == {str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name != 'index.json'}
    for row in index['files']:
        b = (HERE / row['path']).read_bytes()
        assert digest(b) == row['sha256'] and len(b) == row['bytes']
    manifest = json.loads((HERE / 'evidence-index.json').read_text())
    bundle = (HERE / 'evidence.json.gz').read_bytes()
    assert digest(bundle) == manifest['bundle']['sha256'] and len(bundle) == manifest['bundle']['bytes']
    expanded = gzip.decompress(bundle)
    assert len(expanded) == manifest['expandedBundleBytes'] < 10 * 1024**2
    data = json.loads(expanded)['files']
    rows = {r['path']: r for r in manifest['files']}
    assert len(rows) == manifest['payloads'] == len(data) and set(data) == set(rows)
    for name, row in rows.items():
        assert not name.startswith('/') and '..' not in Path(name).parts
        b = data[name].encode('utf8')
        assert digest(b) == row['sha256'] and len(b) == row['bytes']
    assert sum(r['bytes'] for r in rows.values()) == manifest['bytes']
    review = json.loads((HERE / 'review.json').read_text())
    summary = validate(data, rows, review)
    # Actual validator DATA mutations, no actor/resource objects or tool calls.
    negatives = 0
    for name, mutate in [
        ('raw/commands/next-build/terminal.json', lambda j: j.update(rawExitCode=1)),
        ('raw/commands/npm-ci/started.json', lambda j: j.update(timeoutSeconds=601)),
        ('raw/application-inputs.json', lambda j: j.update(regularFiles=2218)),
        ('projections/server-reference.json', lambda j: j.update(node={'old-action-id': {}})),
    ]:
        changed = dict(data)
        value = json.loads(changed[name])
        mutate(value)
        changed[name] = encoded(value).decode()
        # Keep descriptor validation active too; no failed target is rewritten.
        try:
            validate(changed, rows, review)
        except (AssertionError, KeyError):
            negatives += 1
        else:
            raise AssertionError('Accepted DATA mutation: ' + name)
    assert negatives == 4
    print(json.dumps(dict(passed=True, retainedTextPayloads=len(data), dataOnlyNegatives=negatives,
                          originalFilesRequired=False, toolsOrAppExecuted=False, **summary)))


if __name__ == '__main__':
    main()
