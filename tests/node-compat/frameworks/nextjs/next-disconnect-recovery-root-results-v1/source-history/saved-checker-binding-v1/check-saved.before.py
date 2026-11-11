"""Verify the fixed retained disconnect/recovery sample using copies only.

Root binds three literal pins after the packet, reviewer and review close.
Absolute original paths are lookup keys, never filesystem IO destinations.
The exact approved reviewer is loaded with inert main; only raw() is replaced.
No target, host, compiler, binary or project helper is executed or opened.
"""
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys

HERE = Path(__file__).resolve().parent
PACKET = None
REVIEWER = None
REVIEW = None
MAX_FILES, MAX_SOURCE = 4096, 32 * 1024**2
MAX_STORED, MAX_EXPANDED = 256 * 1024**2, 384 * 1024**2
STAMPS = {}


def need(value, message):
    if value is not True:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def stamp(path):
    s = path.lstat()
    return (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def local_bytes(path, cap):
    need(path.is_absolute() and path.resolve(strict=True) == path, 'Noncanonical retained path')
    before = stamp(path)
    need(stat.S_ISREG(before[2]) and before[3] == 1 and 0 <= before[4] <= cap, 'Retained type/link/size bound')
    with path.open('rb') as f:
        data = f.read(cap + 1)
    need(len(data) == before[4] and stamp(path) == before, 'Retained changed/overflow read')
    need(path not in STAMPS or STAMPS[path] == before, 'Retained changed between reads')
    STAMPS[path] = before
    return data


def descriptor(ref, relative=False):
    need(type(ref) is dict and set(ref) == {'path', 'sha256', 'bytes'}, 'Exact typed tuple')
    need(type(ref['path']) is str and type(ref['bytes']) is int and 0 <= ref['bytes'] <= MAX_SOURCE + 1024**2 and
         type(ref['sha256']) is str and re.fullmatch('[0-9a-f]{64}', ref['sha256']) is not None, 'Tuple field types/bounds')
    path = PurePosixPath(ref['path'])
    need(path.as_posix() == ref['path'] and '..' not in path.parts and path.is_absolute() is not relative, 'Tuple path form')
    if relative:
        need(len(path.parts) == 2 and path.parts[0] == 'files', 'Retained member namespace')
    return ref['path'], ref['sha256'], ref['bytes']


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B, without -O; refused before packet reads')
    need(len(sys.argv) == 1, 'No original path/command arguments')
    need(type(PACKET) is dict and set(PACKET) == {'sha256', 'payloadFiles', 'retainedBytes'}, 'Unbound packet pin; refused before packet reads')
    need(type(PACKET['sha256']) is str and re.fullmatch('[0-9a-f]{64}', PACKET['sha256']) is not None and
         type(PACKET['payloadFiles']) is int and 1 <= PACKET['payloadFiles'] <= MAX_FILES and
         type(PACKET['retainedBytes']) is int and 0 <= PACKET['retainedBytes'] <= MAX_STORED, 'Packet pin types/bounds')
    descriptor(REVIEWER); descriptor(REVIEW)
    root = HERE / 'raw-records'
    need(root.resolve(strict=True) == root and root.is_dir(), 'Canonical retained root')
    root_before = stamp(root)
    index_bytes = local_bytes(root / 'index.json', 4 * 1024**2)
    need(sha(index_bytes) == PACKET['sha256'], 'Fixed retained index SHA256')
    index = json.loads(index_bytes)
    need(index['schemaVersion'] == 1 and index['state'] == 'DISCONNECT_RECOVERY_CLOSED_RESULTS_RETAINED_DATA_V1', 'Retained schema')
    need(index['sourcePathsAreLookupKeysOnly'] is True and index['originalPathReadsAllowedBySavedChecker'] is False and index['allReviewedInputsRetained'] is True, 'Copy-only policy')
    entries = index['entries']
    need(type(entries) is list and len(entries) == index['payloadFiles'] == PACKET['payloadFiles'], 'Fixed payload count')
    stored = expanded = 0; paths = set(); originals = set()
    for item in entries:
        key = descriptor(item['source']); descriptor(item['retained'], True)
        need(key[2] <= MAX_SOURCE and item['retained']['path'] not in paths and key[0] not in originals, 'Duplicate/oversized tuple')
        need(item['encoding'] in ('identity', 'gzip') and type(item['reviewedInput']) is bool, 'Encoding/reviewer role')
        paths.add(item['retained']['path']); originals.add(key[0])
        stored += item['retained']['bytes']; expanded += key[2]
    need(stored == index['retainedBytes'] == PACKET['retainedBytes'] <= MAX_STORED and expanded == index['expandedBytes'] <= MAX_EXPANDED, 'Upfront aggregate bounds')
    need({p.name for p in root.iterdir()} == {'index.json', 'files'}, 'Closed retained root membership')
    files = root / 'files'; need(files.resolve(strict=True) == files and files.is_dir(), 'Canonical retained files')
    files_before = stamp(files)
    members = list(files.iterdir())
    need(len(members) == len(paths) and {p.relative_to(root).as_posix() for p in members} == paths, 'Closed payload membership')
    blobs, refs, copies, inodes = {}, {}, {}, set()
    for item in entries:
        ref, saved = item['source'], item['retained']; path = root / saved['path']
        encoded = local_bytes(path, MAX_SOURCE + 1024**2); physical = STAMPS[path]
        need((physical[0], physical[1]) not in inodes, 'Retained inode alias'); inodes.add((physical[0], physical[1]))
        need(len(encoded) == saved['bytes'] and sha(encoded) == saved['sha256'], 'Stored SHA/byte tuple')
        if item['encoding'] == 'gzip':
            with gzip.GzipFile(fileobj=io.BytesIO(encoded), mode='rb') as f:
                data = f.read(ref['bytes'] + 1)
                need(len(data) == ref['bytes'] and f.read(1) == b'', 'Bounded full gzip expansion')
        else:
            data = encoded
        need(len(data) == ref['bytes'] and sha(data) == ref['sha256'], 'Expanded original tuple')
        blobs[ref['path']], refs[ref['path']], copies[ref['path']] = data, ref, path
    seen = set()

    def saved_raw(path, cap=24 * 1024**2):
        key = str(path)  # No original resolve/stat/open.
        need(key in blobs and len(blobs[key]) <= cap, 'Missing/oversized retained reviewer input: ' + key)
        seen.add(key)
        return blobs[key]

    def take(ref):
        descriptor(ref)
        need(refs.get(ref['path']) == ref, 'No exact retained declared tuple')
        return saved_raw(ref['path'], MAX_SOURCE)

    need(index['actualReview'] == REVIEW, 'Fixed actual review tuple')
    review = json.loads(take(REVIEW))
    need(review['state'] == 'ROOT_DISCONNECT_RECOVERY_DATA_REVIEW_COMPLETED_V1' and review['verifiedDataReviewPassed'] is True and
         review['nativeLifecycleAccepted'] is review['fullOriginalContractExecuted'] is review['fullNextAccepted'] is False and
         review['guestAbortDiagnosticsPresent'] is True and type(review['allFunctionalRecoveryPassed']) is type(review['allClientObservationsPassed']) is bool, 'Original negative lifecycle scope')
    binding_ref = index['runtimeBindings']; need(review['runtimeBindings'] == binding_ref, 'Actual binding role')
    binding = json.loads(take(binding_ref))
    order = ['wasmtime', 'cloud', 'stock']
    need(binding['state'] == 'ROOT_DISCONNECT_RECOVERY_ACTUAL_BINDINGS_V1' and [t['arm'] for t in binding['arms']] == order and
         [t['outerSeconds'] for t in binding['arms']] == [600, 600, 300] and set(review['arms']) == set(order) and index['unattemptedArms'] == [], 'Complete original fixed sample')
    need(review['actualReviewer'] == REVIEWER, 'Exact approved reviewer tuple')
    source = take(REVIEWER)
    namespace = {'__name__': 'retained_disconnect_recovery_validators', '__file__': str(copies[REVIEWER['path']])}
    # Approved pinned Source has stdlib imports/constants/definitions only;
    # its main guard is inert. No project/candidate module is imported.
    exec(compile(source, str(copies[REVIEWER['path']]), 'exec'), namespace)
    namespace['raw'] = saved_raw
    arms = {}
    for trial in binding['arms']:
        arm = trial['arm']; actual = namespace['review_trial'](trial, binding)
        need(namespace['typed_equal'](actual, review['arms'][arm]), 'Exact reviewer replay differs: ' + arm)
        need(actual['verifiedDataReviewPassed'] is True and actual['probe']['collectionComplete'] is actual['probe']['cleanupComplete'] is True and
             actual['probe']['callCount'] == 114 and actual['probe']['unattemptedCalls'] == 0 and actual['nativeLifecycleAccepted'] is False, 'Complete probe collection; no lifecycle acceptance')
        arms[arm] = {key: actual[key] for key in ('owner', 'clientObservationsPassed', 'functionalRecoveryPassed', 'actorTransportErrorCount', 'guestAbortDiagnosticsPresent', 'diagnostics')}
    need(review['allClientObservationsPassed'] is all(a['clientObservationsPassed'] for a in arms.values()) and
         review['allFunctionalRecoveryPassed'] is all(a['functionalRecoveryPassed'] for a in arms.values()) and
         review['guestAbortDiagnosticsPresent'] is any(a['guestAbortDiagnosticsPresent'] for a in arms.values()), 'Original aggregate outcome flags')
    reviewed = {descriptor(ref) for ref in review['reviewedInputs']}
    marked = {descriptor(item['source']) for item in entries if item['reviewedInput']}
    need(reviewed == marked and len(reviewed) == index['reviewedInputTuples'] and all(key[0] in seen for key in reviewed), 'All reviewer inputs copied and replayed through saved seam')
    for key in ('verifiedDataReviewPassed', 'allFunctionalRecoveryPassed', 'guestAbortDiagnosticsPresent', 'nativeLifecycleAccepted', 'fullOriginalContractExecuted', 'fullNextAccepted'):
        need(index[key] is review[key], 'Retained outcome remains exact: ' + key)
    need(index['deepNativePayloadsRetained'] is False and index['originalFailuresPreserved'] is True, 'Preserved failures/omission scope')
    need(stamp(root) == root_before and stamp(files) == files_before and all(stamp(p) == before for p, before in STAMPS.items()), 'Final retained namespace/file bookends')
    print(json.dumps(dict(state='SAVED_DISCONNECT_RECOVERY_SAMPLE_DATA_VERIFIED_V1', passed=True, payloadFiles=len(entries),
        retainedBytes=stored, expandedBytes=expanded, reviewedInputTuples=len(reviewed), arms=arms,
        allClientObservationsPassed=review['allClientObservationsPassed'], allFunctionalRecoveryPassed=review['allFunctionalRecoveryPassed'],
        guestAbortDiagnosticsPresent=True, nativeLifecycleAccepted=False,
        originalPathReads=False, targetOrHostOrToolExecution=False, fullOriginalContractExecuted=False, fullNextAccepted=False)))


if __name__ == '__main__':
    main()
