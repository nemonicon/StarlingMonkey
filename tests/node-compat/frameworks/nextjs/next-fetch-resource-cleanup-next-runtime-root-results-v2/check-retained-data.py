"""Check the retained failed sample offline; never run JavaScript or a component."""
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
ROOT = HERE / 'retained-raw-data-v1'
MANIFEST_SHA256 = '0e0a8e28f047064971a914d2e3201d0a868a5ca544ec6ec6e5b02a0818f9dbd8'


def main():
    assert __debug__
    data = (ROOT / 'manifest.json').read_bytes()
    assert hashlib.sha256(data).hexdigest() == MANIFEST_SHA256
    manifest = json.loads(data)
    names, originals, payload = set(), {}, 0
    for item in manifest['files']:
        ref = item['copied']
        rel = Path(ref['relativePath'])
        assert not rel.is_absolute() and '..' not in rel.parts
        assert rel.as_posix() == ref['relativePath'] and rel.as_posix() not in names
        names.add(rel.as_posix())
        path = ROOT / rel
        assert not any(p.is_symlink() for p in [path, *path.parents])
        before = path.stat()
        assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1
        assert before.st_size == ref['bytes'] and before.st_size <= 32 * 1024**2
        body = path.read_bytes()
        assert len(body) == ref['bytes'] and hashlib.sha256(body).hexdigest() == ref['sha256']
        after = path.stat()
        assert all(getattr(before, k) == getattr(after, k) for k in
                   ['st_dev', 'st_ino', 'st_size', 'st_mode', 'st_nlink', 'st_mtime_ns', 'st_ctime_ns'])
        assert item['original']['path'] not in originals
        originals[item['original']['path']] = body
        payload += len(body)
    assert len(names) == 69 and payload == 1555648
    assert {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()} == names | {'manifest.json'}

    def record(suffix):
        matches = [body for name, body in originals.items() if name.endswith(suffix)]
        assert len(matches) == 1
        return json.loads(matches[0])

    base = '/next-wasmtime-deployment-cleanup-476b-next-corrected'
    result = record(base + '/result.json')
    client = record(base + '/client/result.json')
    outer = record(base + '-external-root/observation.json')
    assert result['passed'] is False and result['originalInputsPreserved'] is result['readonlyAppPreserved'] is True
    assert result['component']['sha256'] == 'd990ecc139a2466ce70fe7f6eabdc1fa4b0f85c7535834545f75b3099471407f'
    assert outer['rawExitCode'] == 1 and outer['ownedGroupsClean'] is outer['protectedInputsPreserved'] is True
    assert client['portableCacheValidation']['passed'] is True and client['portableCacheValidation']['checks'] == 52
    assert client['supplementalValidation']['passed'] is True and client['supplementalValidation']['checks'] == 80
    assert len(client['http']) == 24 and all(r['passed'] is True for r in client['http'])
    assert all(r['failures'] == [] for r in client['http'][:23])
    assert client['http'][23]['id'] == 'server-action-submit'
    assert client['cacheInvalidation'] == dict(before=dict(marker='NEXT_CACHE_VALUE', generation=1),
        after=dict(marker='NEXT_CACHE_VALUE', generation=1), passed=False)
    assert client['streaming']['chunks'] == 5 and client['streaming']['complete'] is True
    browser = client['browser']
    assert len(browser['tests']) == 2 and all(t['passed'] is True for t in browser['tests'])
    assert browser['passed'] is False and browser['pageerrors'] == browser['consoleerrors'] == []
    assert [e['stage'] for e in browser['errors']] == ['server-action-response-body',
        'server-action-response-finished', 'server-action-request-sizes']
    assert len(browser['failedrequests']) == 1
    assert browser['failedrequests'][0]['failure']['errorText'] == 'net::ERR_ABORTED'
    assert client['passed'] is client['originalContractPassed'] is False
    assert client['errors'] == client['transportErrors'] == []
    print(json.dumps(dict(state='RETAINED_FAILED_FULL_NEXT_BASELINE_CHECKED_V1',
        files=69, bytes=payload, expectedFailures=['legacy-cache-generation', 'strict-server-action-capture'],
        actualOverallPassed=False, newExecution=False, omittedPayloadsReproduced=False)))


if __name__ == '__main__':
    main()
