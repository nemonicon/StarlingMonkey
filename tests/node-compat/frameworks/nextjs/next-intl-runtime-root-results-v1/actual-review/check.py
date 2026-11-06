"""Portable DATA regression review. Exit0 means baseline verified, not Next passed."""
from pathlib import Path
import hashlib, json, tarfile

HERE = Path(__file__).resolve().parent

def main():
    index = json.loads((HERE/'index.json').read_text())
    assert {x['path'] for x in index['files']} == {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file() and p != HERE/'index.json'}
    assert not any(p.is_symlink() for p in HERE.rglob('*'))
    for row in index['files']:
        data = (HERE/row['path']).read_bytes()
        assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
    ledger = json.loads((HERE/'ledger.json').read_text())
    with tarfile.open(HERE/'data.tar.gz','r:gz') as archive:
        members = archive.getmembers()
        assert all(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in members)
        assert len(members) == len({m.name for m in members}) == len(ledger['files'])
        data = {m.name: archive.extractfile(m).read() for m in members}
    assert set(data) == {r['retained'] for r in ledger['files']}
    for r in ledger['files']:
        value = data[r['retained']]; value.decode('utf-8')
        assert len(value) == r['original']['bytes'] and hashlib.sha256(value).hexdigest() == r['original']['sha256']
    load = lambda name: json.loads(data[name])
    for key, run in ledger['runs'].items():
        terminal = load(run['terminal'])
        assert terminal['rawExitCode'] == run['rawExitCode']
        assert terminal['allObservedOwnedGroupsGone'] and terminal['parentOwnedGroupGone']
        assert not terminal['timeout'] and not terminal['forcedCleanup']
        assert all(terminal[k] == [] for k in ('errors','signals','interruptedSignals','remainingObservedPids'))
        result = load(run['result'])
        server = result['server']
        assert server['shutdownRequested'] and server['sigintSent'] and not server['forcedCleanup']
        assert server['exit'] == dict(code=0, signal=None, error=None)
        assert result['adoption'] is False
    unicode = load(ledger['runs']['unicode']['result'])
    assert unicode['nodeSelectedParity'] and unicode['observationsValid'] and unicode['inputsPreserved']
    assert len(unicode['comparisons']) == 36 and unicode['selectedDifferences'] == []
    assert [r['call'] for r in unicode['responses']] == [1,2,3]
    for comparison in unicode['comparisons']:
        actual = json.loads(json.dumps(comparison['actual']))
        expected = json.loads(json.dumps(comparison['node']))
        # Node and SpiderMonkey have different SyntaxError prose; all selected
        # compilation, class, code, match, index, source and flag fields agree.
        for value in (actual,expected):
            if not value['compiled']:
                value['error'].pop('message',None)
        assert actual == expected
    stack = load(ledger['runs']['stack']['result'])
    assert stack['observationsValid'] and stack['inputsPreserved'] and not stack['nodeSelectedParity']
    assert len(stack['selectedDifferences']) == 3
    for comparison in stack['comparisons']:
        assert comparison['differences'] == ['exact-depd-getStack-and-location']
        left, right = comparison['actualSelected'], comparison['nodeSelected']
        assert len(left['records']) == len(right['records']) == 4
        assert left['records'][:3] == right['records'][:3]
        a, b = left['records'][-1]['selected'], right['records'][-1]['selected']
        assert a['depdLocationSucceeded'] and b['depdLocationSucceeded']
        assert a['stack']['firstFrame']['getFunctionName']['returnType']['valueType'] == 'string'
        assert b['stack']['firstFrame']['getFunctionName']['returnType']['isNull'] is True
    deps = load(ledger['runs']['dependencies']['result'])
    assert deps['passed'] and deps['semanticChecksPassed'] and deps['originalInputsPreserved'] and deps['readonlyCopyPreserved']
    assert [q['method'] for q in deps['requests']] == ['GET','GET','POST']
    assert all(q['status'] == 200 and len(q['body']['records']) == 16 and all(r['passed'] for r in q['body']['records']) for q in deps['requests'])
    for key in ('next','diagnostic'):
        result = load(ledger['runs'][key]['result'])
        client = load(key+'/runtime/client/result.json')
        assert result['passed'] is False and result['originalInputsPreserved'] and result['readonlyAppPreserved']
        assert len(client['http']) == 24 and sum(x['passed'] for x in client['http']) == 11
        assert client['passed'] is False and client['errors'] and 'browser' not in client
    diagnostic = data['diagnostic/runtime/wasmtime.stderr.log'].decode()
    assert 'signal must be either undefined or an AbortSignal' in diagnostic
    assert 'NEXT_BUFFER_INPUT_DIAGNOSTIC' in diagnostic and '"isView":true' in diagnostic
    print(json.dumps(dict(baselineVerified=True, unicodeRecordsPassed=36, dependencyRecordsPassed=48, stackRecordsPassed=9, stackRecordsDifferent=3, nextHttpPassed=11, nextHttpTotal=24, nextPassed=False, guestExecutedByReader=False)))

if __name__ == '__main__':
    main()
