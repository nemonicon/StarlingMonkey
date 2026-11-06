"""Read retained HTTP-bridge data only; never import or invoke the application."""
import base64
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'http-bridge-candidate-v1'

def descriptor(path):
    data = path.read_bytes()
    return {'path': str(path), 'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}

def read(path):
    return json.loads(path.read_text())

def main():
    expected = {
        'results': [('next-http-bridge-v1', 1, 22, 0, 0),
                    ('next-http-bridge-v2', 0, 24, 24, 0),
                    ('next-http-bridge-v3-browser', 0, 24, 24, 2)],
        'module-results': [('next-http-bridge-module-v1', 0, 24, 24, 2)],
    }
    source_files = [p for p in SOURCE.rglob('*') if p.is_file()
                    and 'results' not in p.relative_to(SOURCE).parts
                    and 'module-results' not in p.relative_to(SOURCE).parts]
    sources_by_hash = {}
    for path in source_files:
        sources_by_hash.setdefault(descriptor(path)['sha256'], []).append(str(path))
    contract_path = HERE.parent / 'fixture-contract.json'
    ids = [row['id'] for row in read(contract_path)['requests']] + ['server-action-submit']
    assert len(ids) == len(set(ids)) == 24
    summaries, runs, copy_count, copy_bytes = [], [], 0, 0
    for capsule, expected_runs in expected.items():
        root = SOURCE / capsule
        summary = read(root / 'summary.json')
        assert summary['nativeGuestExecuted'] is False and summary['componentExecuted'] is False
        assert [row['name'] for row in summary['runs']] == [row[0] for row in expected_runs]
        names = set()
        for row in summary['copies']:
            path = root / row['file']
            assert not path.is_symlink() and path.resolve().is_relative_to(root.resolve())
            assert row['file'] not in names
            names.add(row['file'])
            actual = descriptor(path)
            assert (actual['sha256'], actual['bytes']) == (row['sha256'], row['bytes'])
            copy_count += 1
            copy_bytes += actual['bytes']
        actual_files = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
        assert actual_files == names | {'summary.json'}
        summaries.append(descriptor(root / 'summary.json'))
        for name, raw_exit, observed, passed, browser_count in expected_runs:
            directory = root / name
            result = read(directory / 'result.json')
            terminal = read(directory / 'monitor/terminal.json')
            started = read(directory / 'monitor/started.json')
            assert terminal['rawExitCode'] == raw_exit
            for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']:
                assert terminal[key] == []
            assert terminal['parentOwnedGroupGone'] and terminal['allObservedOwnedGroupsGone']
            assert terminal['timeout'] is False and terminal['forcedCleanup'] is False
            assert started['argv'][0] == '/private/tmp/starling-node-compat/node-v22.14.0-darwin-arm64/bin/node'
            assert started['timeoutSeconds'] == 300
            assert result['node'] == 'v22.14.0' and result['guestExecuted'] is False
            assert result['applicationModified'] is False
            assert result['installed'] == {'next': '16.4.5', 'react': '19.3.1', 'react-dom': '19.3.1'}
            assert len(result['http']) == observed
            assert sum(row['passed'] is True for row in result['http']) == passed
            assert len({row['id'] for row in result['http']}) == observed
            if passed:
                assert set(row['id'] for row in result['http']) == set(ids)
                assert result['passed'] and result['errors'] == [] and result['transportErrors'] == []
                assert (directory / 'monitor/stderr.log').read_bytes() == b''
                assert result['cacheInvalidation']['before']['generation'] == 1
                assert result['cacheInvalidation']['after']['generation'] == 2
                chunks = read(directory / 'stream-chunks.json')
                assert len(chunks) == 5
                strings = []
                for chunk in chunks:
                    data = base64.b64decode(chunk['base64'], validate=True)
                    assert len(data) == chunk['bytes']
                    strings.append(data.decode('utf-8'))
                assert next(i for i, s in enumerate(strings) if 'NEXT_STREAM_SHELL' in s) == 0
                assert next(i for i, s in enumerate(strings) if 'NEXT_STREAM_READY' in s) == 2
            else:
                assert result['passed'] is False and result['errors'] and result['transportErrors']
            if browser_count:
                browser = read(directory / 'browser/result.json')
                assert browser == result['browser']
                assert browser['passed'] and len(browser['tests']) == browser_count
                assert all(row['passed'] and not row['timedOut'] for row in browser['tests'])
                assert result['browserExit'] == {'code': 0, 'signal': None}
                for key in ['errors', 'pageerrors', 'consoleerrors', 'failedrequests']:
                    assert browser[key] == []
            elif 'browser' in result:
                raise AssertionError('unexpected browser result')
            raw_json = [json.loads(line) for line in (directory / 'monitor/stdout.log').read_text().splitlines()
                        if line.startswith('{')]
            assert raw_json[-1]['http'] == observed and raw_json[-1]['passedHttp'] == passed
            assert raw_json[-1]['guestExecuted'] is False
            executed = {}
            for key in ['bridge', 'harness', 'moduleSource', 'hostModuleProvider']:
                if key in result:
                    row = result[key]
                    assert row['sha256'] in sources_by_hash or descriptor(Path(row['path'])) == row
                    matches = sources_by_hash.get(row['sha256'], [row['path']])
                    assert all(Path(p).stat().st_size == row['bytes'] for p in matches)
                    executed[key] = {'recorded': row, 'retainedSourceMatches': matches}
            module = None
            if 'moduleSnapshot' in result:
                snapshot = result['moduleSnapshot']
                assert len(snapshot['compiled']) == 406 and len(set(snapshot['compiled'])) == 406
                assert snapshot['cachedModules'] == 412 and snapshot['candidateModuleIdentity'] is True
                assert result['moduleObservations'] == {'hostGlobalsAndNodeBuiltins': True,
                    'nativeProviderExecuted': False, 'sourceOnlyCandidate': True}
                module = {'compiledFiles': 406, 'cachedModules': 412, 'candidateModuleIdentity': True,
                          'hostProvidersOnly': True}
            runs.append({'name': name, 'rawExitCode': raw_exit, 'httpObserved': observed,
                         'httpPassed': passed, 'browserPassed': browser_count,
                         'cleanOwnedGroups': True, 'startedArgv': started['argv'],
                         'result': descriptor(directory / 'result.json'),
                         'terminal': descriptor(directory / 'monitor/terminal.json'),
                         'streaming': result.get('streaming'), 'executedSource': executed,
                         'module': module})
    return {'schemaVersion': 1, 'state': 'INDEPENDENT_NEXT_HTTP_BRIDGE_HOST_DATA_REVIEW_PASSED_V1',
            'scope': 'Four retained Node-host attempts and current bounded bridge source; no guest acceptance',
            'retainedCopiesVerified': copy_count, 'retainedCopyBytes': copy_bytes,
            'closedCapsuleMembershipVerified': True, 'summaries': summaries, 'contract': descriptor(contract_path),
            'sourceFiles': [descriptor(p) for p in sorted(source_files)], 'runs': runs,
            'reviewerRelationship': 'Reviewer authored the proposed native ALS fresh-request seam, not this HTTP bridge',
            'guestExecutedByReviewer': False, 'applicationExecutedByReviewer': False,
            'compilerInvokedByReviewer': False, 'nativeAlsFreshRequestWired': False,
            'wasiResourcesValidatedInGuest': False, 'tlsSocketsImplemented': False,
            'guestRuntimeAccepted': False, 'limitationsDocument': 'README.md'}

if __name__ == '__main__':
    print(json.dumps(main(), indent=2, sort_keys=True))
