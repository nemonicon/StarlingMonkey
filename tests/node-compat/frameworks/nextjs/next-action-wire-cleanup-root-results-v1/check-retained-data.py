"""Offline Python DATA validation of the retained non-browser transport pair."""
import hashlib
import importlib.util
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent
RAW = HERE / 'retained-raw-data-v1'
MANIFEST_SHA = '9f5c3b56104dfcd7b9758a3fa778efc78f675d740411db583bdf5f79e9820b34'


def main():
    assert __debug__
    path = RAW / 'manifest.json'
    assert path.stat().st_size == 38655
    manifest_bytes = path.read_bytes()
    assert hashlib.sha256(manifest_bytes).hexdigest() == MANIFEST_SHA
    manifest = json.loads(manifest_bytes)
    names, total = set(), 0
    for item in manifest['files']:
        ref = item['copied']
        rel = Path(ref['relativePath'])
        assert not rel.is_absolute() and '..' not in rel.parts and rel.as_posix() == ref['relativePath']
        assert ref['relativePath'] not in names
        names.add(ref['relativePath'])
        path = RAW / rel
        assert not any(p.is_symlink() for p in [path, *path.parents])
        before = path.stat()
        assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1
        assert before.st_size == ref['bytes'] and before.st_size <= 2 * 1024**2
        data = path.read_bytes()
        assert len(data) == ref['bytes'] and hashlib.sha256(data).hexdigest() == ref['sha256']
        after = path.stat()
        assert all(getattr(before, k) == getattr(after, k) for k in
                   ['st_dev', 'st_ino', 'st_size', 'st_mode', 'st_nlink', 'st_mtime_ns', 'st_ctime_ns'])
        total += len(data)
    assert len(names) == 33 and total == 671933
    assert {p.relative_to(RAW).as_posix() for p in RAW.rglob('*') if p.is_file()} == names | {'manifest.json'}
    verifier = HERE.parent / 'next-response-gzip-composition-probe-candidate-v1/verify-data.py'
    assert hashlib.sha256(verifier.read_bytes()).hexdigest() == '6e1a79abc3b688741fb8af8099f6f1cd0b49be6a3dcf18275db6b9e407716075'
    spec = importlib.util.spec_from_file_location('held_transport_data_parser', verifier)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    outputs = []
    for arm in ['native', 'stock']:
        root = RAW / 'files' / arm / 'transport'
        result = json.loads((root / 'result.json').read_bytes())
        encoded, headers = module.http((root / 'raw-socket-prefix.bin').read_bytes())
        assert encoded == (root / 'node-http-encoded-prefix.bin').read_bytes()
        decoded = (root / 'decoded-flight.body').read_bytes()
        observed = module.gzip_member(encoded, decoded)
        assert len(decoded) == 2963 and headers['content-type'].split(';')[0] == 'text/x-component'
        assert result['passed'] is True and result['errors'] == []
        assert result['fullNextAcceptance'] is result['browserInvoked'] is result['reactFlightParsed'] is False
        assert result['sourceBodySha256'] == 'cc609fbe813753e8cc29ec04c0e6bb243c7c656c22338943553d83221ef71f99'
        assert result['capture']['httpMessageEndObserved'] is result['capture']['responseComplete'] is True
        assert result['capture']['peerSocketEndObserved'] is False
        assert observed['crc32'] == result['validation']['crc32']
        assert observed['isize'] == result['validation']['isize']
        outputs.append(dict(arm=arm, encodedBytes=len(encoded), decodedBytes=len(decoded), crc32=observed['crc32']))
    print(json.dumps(dict(state='RETAINED_CURRENT_ACTION_TRANSPORT_DATA_CHECKED_V1',
        files=33, bytes=total, arms=outputs, newNodeGuestOrNetworkExecution=False,
        httpMessageEofVerified=True, peerSocketEofClaimed=False,
        reactFlightParsed=False, fullNextAccepted=False, causeProved=False)))


if __name__ == '__main__':
    main()
