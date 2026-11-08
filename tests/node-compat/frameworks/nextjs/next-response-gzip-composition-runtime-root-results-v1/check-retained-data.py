"""Offline bytes/Python DATA decoding; no Node, component or HTTP invocation."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import stat
import tempfile

HERE = Path(__file__).resolve().parent
RAW = HERE / 'retained-raw-data-v1'
MANIFEST_SHA = '11d9a1b9aab5deb0d427cd109cafae36de8508ad053c42ed2d9a050129a21b02'
VERIFIER_SHA = '6e1a79abc3b688741fb8af8099f6f1cd0b49be6a3dcf18275db6b9e407716075'


def main():
    assert __debug__
    assert (RAW / 'manifest.json').stat().st_size == 19223
    data = (RAW / 'manifest.json').read_bytes()
    assert hashlib.sha256(data).hexdigest() == MANIFEST_SHA
    manifest = json.loads(data)
    names, total = set(), 0
    for item in manifest['files']:
        ref = item['retained']
        rel = Path(ref['path'])
        assert not rel.is_absolute() and '..' not in rel.parts and rel.as_posix() == ref['path']
        assert ref['path'] not in names
        names.add(ref['path'])
        path = RAW / rel
        assert not any(p.is_symlink() for p in [path, *path.parents])
        before = path.stat()
        assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1
        assert before.st_size == ref['bytes'] and before.st_size <= 8 * 1024**2
        body = path.read_bytes()
        assert len(body) == ref['bytes'] and hashlib.sha256(body).hexdigest() == ref['sha256']
        after = path.stat()
        assert all(getattr(before, k) == getattr(after, k) for k in
                   ['st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'])
        total += len(body)
    assert len(names) == 39 and total == 6350276
    assert {p.relative_to(RAW).as_posix() for p in RAW.rglob('*') if p.is_file()} == names | {'manifest.json'}
    verifier = HERE.parent / 'next-response-gzip-composition-probe-candidate-v1/verify-data.py'
    assert hashlib.sha256(verifier.read_bytes()).hexdigest() == VERIFIER_SHA
    spec = importlib.util.spec_from_file_location('held_gzip_data_verifier', verifier)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Original JSON stays byte-identical. Relocate only DATA file descriptors in
    # an explicitly derived temporary view, satisfying the held verifier's
    # canonical same-directory roles after a repository checkout moves.
    with tempfile.TemporaryDirectory(prefix='starling-gzip-offline-') as temporary:
        temp = Path(temporary).resolve()
        reference, wire = temp / 'node-reference', temp / 'wire'
        reference.mkdir(mode=0o700)
        wire.mkdir(mode=0o700)
        node = json.loads((RAW / 'files/node-reference/reference.json').read_bytes())
        capture = json.loads((RAW / 'files/wire/wire-capture.json').read_bytes())
        assert [r['caseId'] for r in node['cases']] == ['small', 'large']
        assert [r['caseId'] for r in capture['requests']] == ['small', 'large']
        for case, request in zip(node['cases'], capture['requests']):
            case_id = case['caseId']
            for key, suffix in [('plain', '.plain'), ('gzip', '.gzip')]:
                name = case_id + suffix
                shutil.copyfile(RAW / 'files/node-reference' / name, reference / name)
                case[key]['path'] = str(reference / name)
            name = case_id + '.http'
            shutil.copyfile(RAW / 'files/wire' / name, wire / name)
            request['wire']['path'] = str(wire / name)
        node_path, capture_path = reference / 'reference.json', wire / 'wire-capture.json'
        node_path.write_text(json.dumps(node) + '\n')
        capture_path.write_text(json.dumps(capture) + '\n')
        result = module.verify(capture_path, node_path, RAW / 'files/controller/wasmtime.stdout.log')
        assert result['compositionProfilePassed'] is result['publicResponseBackpressureObserved'] is True
    print(json.dumps(dict(state='RETAINED_GZIP_COMPOSITION_PUBLIC_DATA_CHECKED_V1',
        files=39, bytes=total, cases=2, publicBackpressureObserved=True,
        newExecution=False, originalRecordsModified=False,
        privateWasiFinishCountProved=False, fullNextAccepted=False)))


if __name__ == '__main__':
    main()
