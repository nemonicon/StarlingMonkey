"""Restore the exact locked macOS LZMA payload skipped by npm's engine filter.

Only acquisition and byte verification occur here. Its newer declared Node
engine range remains a toolchain limitation; no compatibility is inferred.
"""
import base64
import hashlib
import io
import json
from pathlib import Path
import tarfile
import urllib.request

REPO = Path(__file__).resolve().parents[4]
WORK = Path('/private/tmp/starling-node-compat/next-lifecycle-compiler-recovery-v1-first')
REL = 'node_modules/@napi-rs/lzma-darwin-arm64'
TOOLS = WORK / 'toolchain'
LOCK = TOOLS / 'package-lock.json'
REFERENCES = REPO / 'tests/node-compat/foundation-scheduler/clock-io-pruning-candidate-v1/tool-cut-references.json'


def main():
    lock_bytes = LOCK.read_bytes()
    selected = json.loads(lock_bytes)['packages'][REL]
    with urllib.request.urlopen(selected['resolved'], timeout=60) as response:
        data = response.read(32 * 1024**2 + 1)
    if len(data) > 32 * 1024**2 or 'sha512-' + base64.b64encode(hashlib.sha512(data).digest()).decode() != selected['integrity']:
        raise RuntimeError('Archive failed original lock integrity')
    expected = {r['relativePath'][len(REL) + 1:]: r for r in json.loads(REFERENCES.read_bytes())['jsToolchain']['files']
                if r['relativePath'].startswith(REL + '/')}
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        members = archive.getmembers()
        if len(members) != 3 or {m.name for m in members} != {'package/' + name for name in expected}:
            raise RuntimeError('Unexpected archive membership')
        payloads = {}
        for member in members:
            if not member.isfile():
                raise RuntimeError('Only independent regular files are allowed')
            name = member.name.removeprefix('package/')
            payload = archive.extractfile(member).read()
            ref = expected[name]['descriptor']
            if len(payload) != ref['bytes'] or hashlib.sha256(payload).hexdigest() != ref['sha256']:
                raise RuntimeError('Original tool-cut payload mismatch: ' + name)
            payloads[name] = payload
    destination = TOOLS / REL
    destination.mkdir(mode=0o755)
    for name, payload in payloads.items():
        with (destination / name).open('xb') as handle:
            handle.write(payload)
        (destination / name).chmod(expected[name]['mode'])
    with (WORK / 'locked-lzma-darwin-arm64-1.5.1.tgz').open('xb') as handle:
        handle.write(data)
    if LOCK.read_bytes() != lock_bytes:
        raise RuntimeError('Lock changed')
    result = dict(schemaVersion=1, state='EXACT_SKIPPED_OPTIONAL_PAYLOAD_RESTORED_V1',
                  package=selected, files=sorted(payloads), originalToolCutBytesMatch=True,
                  archiveSha256=hashlib.sha256(data).hexdigest(), archiveBytes=len(data),
                  imported=False, declaredNodeEngineRangeNotWaived=True)
    with (Path(__file__).parent / 'optional-restoration.json').open('x') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
