"""Bind the actual validated lifecycle component to the stock cloud collector."""
import hashlib
import json
import os
from pathlib import Path
import socket
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
SOURCE = BASE / 'lifecycle-wasmcloud-collector-v2'
OUTPUT = Path('/private/tmp/starling-node-compat/next-lifecycle-wasmcloud-v2-clone-cancel-first')
WASH = Path('/private/tmp/starling-node-compat/wasmcloud/bin/wash-2.11.0-aarch64-apple-darwin')


def row(path):
    assert path.is_absolute() and path.resolve(strict=True) == path and path.is_file()
    before = path.stat()
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024**2), b''):
            h.update(block)
    after = path.stat()
    assert all(getattr(before, k) == getattr(after, k) for k in
               ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'))
    return dict(path=str(path), sha256=h.hexdigest(), bytes=after.st_size)


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B without optimization')
    assert len(sys.argv) == 1 and not os.path.lexists(OUTPUT)
    assert not os.path.lexists(HERE / 'runtime-request.json')
    base_path = BASE / 'next-clone-cancel-component-root-results-v1/runtime-request.json'
    base_ref = row(base_path)
    assert base_ref['sha256'] == '3092c29eab862afbc1cb681065f8c0514e5bdc3729a6d407d20f869ce14a0871'
    original = json.loads(base_path.read_bytes())
    assert original['state'] == 'ROOT_LIFECYCLE_COMPONENT_RUNTIME_REQUEST_V3'
    assert original['component']['sha256'] == '7c22799781975b7e9c09d9df294fb1c5e3f243bb1c596d733425f98cf805f779'
    index_ref = row(SOURCE / 'index.json')
    assert index_ref['sha256'] == 'd67bc92a34f8167c8e26d5840ad6f58eeb1a9e59c1e6f28eb433698d345640bd'
    index = json.loads((SOURCE / 'index.json').read_bytes())
    assert len(index['files']) == 5
    source_refs = [index_ref]
    names = set()
    for item in index['files']:
        member = Path(item['path'])
        assert '..' not in member.parts and member.as_posix() == item['path']
        member = member if member.is_absolute() else SOURCE / member
        relative = member.relative_to(SOURCE).as_posix()
        assert relative not in names
        names.add(relative)
        ref = row(member)
        assert (ref['sha256'], ref['bytes']) == (item['sha256'], item['bytes'])
        source_refs.append(ref)
    assert {p.relative_to(SOURCE).as_posix() for p in SOURCE.rglob('*') if p.is_file()} == names | {'index.json'}
    assert not any(p.is_symlink() for p in SOURCE.rglob('*'))
    collector = row(SOURCE / 'run-wasmcloud.py')
    assert collector['sha256'] == '229903cbb09f8299341f9588ec4044154627c3dd238619b7fb1bc02aa1ef041a'
    wash = row(WASH)
    assert wash['sha256'] == '365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954' and wash['bytes'] == 101947952
    protected = [base_ref, row(Path(__file__).resolve()), *source_refs, *original['protectedInputs']]
    direct = [original[k] for k in ('component', 'wasmTools', 'validationStarted', 'validationTerminal', 'witStarted', 'witTerminal')]
    for ref in [*protected, *direct, wash]:
        assert row(Path(ref['path'])) == ref
    # The collector reacquires this exact port and holds it through config-show.
    # A race at that later bind fails; it must not silently select another port.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as lease:
        lease.bind(('127.0.0.1', 0))
        origin = 'http://127.0.0.1:' + str(lease.getsockname()[1])
    request = {k: original[k] for k in ('component', 'wasmTools', 'validationStarted', 'validationTerminal', 'witStarted', 'witTerminal')}
    request.update(schemaVersion=1, state='ROOT_LIFECYCLE_WASMCLOUD_RUNTIME_REQUEST_V2',
        wash=wash, runtimeSource=collector, outputRoot=str(OUTPUT), selfOrigin=origin,
        protectedInputs=protected, derivedFromValidatedWasmtimeRequest=base_ref,
        guestEnvironmentConfigured=False, applicationMounted=False, outgoingHostsAllowed=False,
        extraHttpRequests=0, semanticComparisonPerformed=False, fullNextAccepted=False)
    with (HERE / 'runtime-request.json').open('x') as f:
        json.dump(request, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(request=row(HERE / 'runtime-request.json'), origin=origin, protectedInputs=len(protected))))


if __name__ == '__main__':
    main()
