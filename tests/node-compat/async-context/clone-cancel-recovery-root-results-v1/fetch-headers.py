"""Acquire candidate headers; publish only bytes matching the selected SDK pins."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
MANIFEST = HERE.parent / 'clone-cancel-native-sdk-recovery-v1/remote-header-candidates.json'
MANIFEST_SHA = '562902469ec7fb8980a00658b8096388fd53a7762f45abc5ed97ed987c0c3aac'
WORK = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first')
OUTPUT = WORK / 'headers-exact'
LOGS = WORK / 'header-acquisition-first'
PREFIX = 'https://raw.githubusercontent.com/bytecodealliance/firefox/9dab3d6f643e926a340c391ea30968e940390dec/'


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as handle:
        handle.write(data); handle.flush(); os.fsync(handle.fileno())


def acquire(index, header):
    result = dict(sdkPath=header['sdkPath'], expectedSha256=header['sha256'], expectedBytes=header['bytes'],
                  attempts=[], matched=False, generated=header['generatedHeaderMayNeedExactReproduction'])
    for ordinal, url in enumerate(header['candidateUrls']):
        attempt = dict(url=url, responseStatus=None, error=None)
        limit = min(header['bytes'] + 1, 1024**2)
        raw = b''
        try:
            try:
                response = urllib.request.urlopen(url, timeout=20)
            except urllib.error.HTTPError as error:
                response = error
            with response:
                attempt['responseStatus'] = response.status
                attempt['finalUrl'] = response.url
                raw = response.read(limit)
            attempt['bodyAtReadLimit'] = len(raw) == limit
        except Exception as error:
            attempt['error'] = dict(type=type(error).__name__, message=str(error)[:1024])
        attempt.update(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        stem = f'{index:03d}-{ordinal}'
        write(LOGS / (stem + '.body'), raw)
        attempt['bodyFile'] = str(LOGS / (stem + '.body'))
        result['attempts'].append(attempt)
        if attempt['responseStatus'] == 200 and attempt['error'] is None and \
                len(raw) == header['bytes'] and attempt['sha256'] == header['sha256']:
            write(Path(header['freshTarget']), raw)
            result.update(matched=True, publishedPath=header['freshTarget'])
            break
    write(LOGS / f'{index:03d}.json', (json.dumps(result, indent=2) + '\n').encode())
    return result


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B, without -O')
    original = MANIFEST.read_bytes()
    if hashlib.sha256(original).hexdigest() != MANIFEST_SHA:
        raise RuntimeError('Frozen candidate map changed')
    manifest = json.loads(original)
    headers = manifest['headers']
    if len(headers) != 243 or len({row['sdkPath'] for row in headers}) != 243:
        raise RuntimeError('Exact header inventory required')
    for header in headers:
        path = Path(header['sdkPath'])
        if path.is_absolute() or '..' in path.parts or str(OUTPUT / path) != header['freshTarget']:
            raise RuntimeError('Invalid publication path')
        if not 0 < header['bytes'] < 1024**2 or not 1 <= len(header['candidateUrls']) <= 3:
            raise RuntimeError('Finite header/attempt bound required')
        if not all(url.startswith(PREFIX) for url in header['candidateUrls']):
            raise RuntimeError('Only the pinned Firefox source commit is selected')
    if WORK.resolve() != WORK or not WORK.is_dir():
        raise RuntimeError('Owned canonical recovery root required')
    OUTPUT.mkdir(mode=0o700); LOGS.mkdir(mode=0o700)
    results = []
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(acquire, index, header) for index, header in enumerate(headers)]
        for future in as_completed(futures):
            results.append(future.result())
            if len(results) % 25 == 0:
                print(json.dumps(dict(completed=len(results), matched=sum(row['matched'] for row in results))), flush=True)
    if MANIFEST.read_bytes() != original:
        raise RuntimeError('Candidate map changed during acquisition')
    results.sort(key=lambda row: row['sdkPath'])
    result = dict(schemaVersion=1, state='PINNED_SDK_HEADER_ACQUISITION_COMPLETED_V1',
                  manifest=dict(path=str(MANIFEST), sha256=MANIFEST_SHA, bytes=len(original)),
                  headers=results, matched=sum(row['matched'] for row in results),
                  unresolved=[row['sdkPath'] for row in results if not row['matched']],
                  onlyHashMatchingFilesPublished=True, nativeBuildExecuted=False)
    write(WORK / 'header-acquisition.json', (json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps(dict(matched=result['matched'], unresolved=result['unresolved'])), flush=True)
    return 0 if not result['unresolved'] else 2


if __name__ == '__main__':
    sys.exit(main())
