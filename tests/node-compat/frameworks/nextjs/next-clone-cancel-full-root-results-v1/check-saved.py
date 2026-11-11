"""Check the fixed saved three-arm sample using repository copies only.

Run Python -I -B check-saved.py, without -O. Root binds the three packet literals
after retention closes. Absolute source paths are dictionary keys, never I/O
targets. Exact approved reviewer Source supplies the unchanged semantic/owner/
capture validators; only raw-file and callback-namespace I/O are substituted.
No native binary, application tree, tool, host or target is executed or opened.
"""
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys

HERE = Path(__file__).resolve().parent
RAW_INDEX_SHA256 = 'bd5f325130a6515c3a899b2b19a6abe70993330f120e36cde339ab6bb7a5fd98'
EXPECTED_FILES = 350
EXPECTED_BYTES = 16214908
REVIEWER_SHA256 = '871d21ffd0a0edb8c8c7948a3c0e76592fcb0a54936d776cada095c550a65839'
REVIEWER_BYTES = 45078
REVIEW_SHA256 = '003ba83cfebef6f3beb2f204f7ebbfe47c8eda7ad3ee3baf14f9c5be2c37fb45'
REVIEW_BYTES = 84890
BINDING_SHA256 = '49f3b6c36ab2271f9685a74f6f6d116ed174f89ac62c01fa9a92a438f035ec4f'
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
    a = stamp(path)
    need(stat.S_ISREG(a[2]) and a[3] == 1 and 0 <= a[4] <= cap, 'Retained regular/link/size bound')
    with path.open('rb') as f:
        data = f.read(cap + 1)
    need(len(data) == a[4] and a == stamp(path), 'Retained read changed or overflowed')
    need(path not in STAMPS or STAMPS[path] == a, 'Retained input changed between reads')
    STAMPS[path] = a
    return data


def descriptor(ref, relative=False):
    need(type(ref) is dict and set(ref) == {'path', 'sha256', 'bytes'}, 'Exact typed descriptor')
    need(type(ref['path']) is str and type(ref['bytes']) is int and 0 <= ref['bytes'] <= MAX_SOURCE + 1024**2 and
         type(ref['sha256']) is str and re.fullmatch('[0-9a-f]{64}', ref['sha256']) is not None, 'Descriptor field types/bounds')
    path = PurePosixPath(ref['path'])
    need(path.as_posix() == ref['path'] and '..' not in path.parts and path.is_absolute() is not relative, 'Descriptor path form')
    if relative:
        need(path.parts[0] == 'files' and len(path.parts) == 2, 'Retained member namespace')
    return (ref['path'], ref['sha256'], ref['bytes'])


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B, without -O; refused before packet reads')
    need(len(sys.argv) == 1, 'No original path/command arguments accepted')
    need(type(RAW_INDEX_SHA256) is str and re.fullmatch('[0-9a-f]{64}', RAW_INDEX_SHA256) is not None and
         type(EXPECTED_FILES) is int and 1 <= EXPECTED_FILES <= MAX_FILES and
         type(EXPECTED_BYTES) is int and 0 <= EXPECTED_BYTES <= MAX_STORED,
         'Unbound saved-packet literals; refused before packet reads')
    root = HERE / 'raw-records'
    index_bytes = local_bytes(root / 'index.json', 4 * 1024**2)
    need(sha(index_bytes) == RAW_INDEX_SHA256, 'Fixed raw index SHA256')
    index = json.loads(index_bytes)
    need(index['schemaVersion'] == 1 and index['state'] == 'CLONE_CANCEL_NEXT_FULL_CLOSED_RESULTS_RETAINED_DATA_V1', 'Retained index schema')
    need(index['sourcePathsAreLookupKeysOnly'] is True and index['originalPathReadsAllowedBySavedChecker'] is False and index['allReviewedInputsRetained'] is True, 'Copy-only retention policy')
    entries = index['entries']
    need(type(entries) is list and len(entries) == index['payloadFiles'] == EXPECTED_FILES, 'Fixed payload count')
    stored = expanded = 0; paths = set(); source_keys = set()
    for item in entries:
        key = descriptor(item['source']); descriptor(item['retained'], relative=True)
        need(key[2] <= MAX_SOURCE and item['retained']['path'] not in paths and key[0] not in source_keys, 'Duplicate/oversized source or member')
        need(item['encoding'] in ('identity', 'gzip') and type(item['reviewedInput']) is bool, 'Explicit encoding/reviewed-input roles')
        paths.add(item['retained']['path']); source_keys.add(key[0]); stored += item['retained']['bytes']; expanded += key[2]
    need(stored == index['retainedBytes'] == EXPECTED_BYTES and stored <= MAX_STORED and expanded == index['expandedBytes'] <= MAX_EXPANDED, 'Pre-read aggregate bounds')
    nodes = list(root.rglob('*'))
    need(all(not p.is_symlink() for p in nodes), 'Retained packet symlink')
    need({p.relative_to(root).as_posix() for p in nodes if p.is_file()} == paths | {'index.json'}, 'Closed retained file membership')
    blobs, refs, copies, inodes = {}, {}, {}, set()
    for item in entries:
        ref, saved = item['source'], item['retained']; path = root / saved['path']
        encoded = local_bytes(path, MAX_SOURCE + 1024**2)
        physical = STAMPS[path]
        need((physical[0], physical[1]) not in inodes, 'Retained payload inode alias'); inodes.add((physical[0], physical[1]))
        need(len(encoded) == saved['bytes'] and sha(encoded) == saved['sha256'], 'Retained payload SHA/bytes')
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
        # Deliberately no resolve/stat/open on this original path.
        key = str(path)
        need(key in blobs, 'Original tuple has no retained copy: ' + key)
        data = blobs[key]
        need(len(data) <= cap, 'Original reviewer per-read bound')
        seen.add(key)
        return data

    def take(ref):
        descriptor(ref)
        need(refs.get(ref['path']) == ref, 'Declared original reference has no exact retained tuple')
        return saved_raw(ref['path'], MAX_SOURCE)

    review_ref = index['actualReview']; need(review_ref['sha256'] == REVIEW_SHA256 and review_ref['bytes'] == REVIEW_BYTES, 'Fixed original review')
    review = json.loads(take(review_ref))
    binding_ref = index['runtimeBindings']; need(binding_ref['sha256'] == BINDING_SHA256 and review['runtimeBindings'] == binding_ref, 'Fixed original binding')
    binding = json.loads(take(binding_ref))
    need(review['state'] == 'ROOT_CLONE_CANCEL_NEXT_FULL_DATA_REVIEW_COMPLETED_V1' and review['verifiedDataReviewPassed'] is True and review['allFullContractsPassed'] is True and review['fullNextAccepted'] is False, 'Original saved positive sample scope')
    need(binding['state'] == 'ROOT_CLONE_CANCEL_NEXT_FULL_ACTUAL_BINDINGS_V1' and [t['arm'] for t in binding['arms']] == ['wasmtime', 'cloud', 'stock'] and [t['outerSeconds'] for t in binding['arms']] == [600, 600, 300], 'Fixed original three slots')
    source_ref = review['actualReviewer']
    need(source_ref['sha256'] == REVIEWER_SHA256 and source_ref['bytes'] == REVIEWER_BYTES, 'Exact approved validator Source')
    source = take(source_ref)
    # The pinned Source has only stdlib imports/constants/definitions at top level;
    # its __main__ guard is inert. No project/candidate module is imported.
    namespace = {'__name__': 'retained_full_contract_validators', '__file__': str(copies[source_ref['path']])}
    exec(compile(source, str(copies[source_ref['path']]), 'exec'), namespace)

    def retained_callback_state(arm, work, expected):
        # Directory membership/absence is the original closed observation, not
        # a claim that this checkout contains or reopens that original directory.
        value = copy.deepcopy(review['arms'][arm]['callbackState'])
        parent = str(work) + ('/application/.next/cache' if arm == 'stock' else '/cache')
        root_name = parent + '/app-callback-generation-v1'
        need(value['namespace'] == root_name and value['members'] == ['generation.json'] and value['pendingAbsent'] is True, 'Retained original namespace observation')
        need(value['generation'] == expected and type(expected) is int and 1 <= expected <= 1000000, 'Retained canonical callback generation')
        ref = value['state']; need(ref['path'] == root_name + '/generation.json', 'Owned callback state role')
        data = take(ref)
        need(data == b'{"schemaVersion":1,"generation":' + str(expected).encode('ascii') + b'}\n', 'Actual retained state bytes')
        need(set(value['namespacePhysical']) == {'dev', 'ino', 'mode', 'nlink'} and all(type(v) is int for v in value['namespacePhysical'].values()), 'Retained physical observation types')
        return value

    namespace['raw'], namespace['callback_state'] = saved_raw, retained_callback_state
    arms = {}
    for trial, owner in zip(binding['arms'], (85601, 86646, 88034)):
        arm = trial['arm']; actual = namespace['review_arm'](trial, binding)
        need(namespace['typed_equal'](actual, review['arms'][arm]), 'Unchanged validator recomputation differs: ' + arm)
        need(actual['collectionVerified'] is True and actual['semanticPassed'] is True and actual['owner']['originalOwner'] == owner and actual['owner']['rawExitCode'] == 0, 'Golden full sample/original owner')
        need(actual['httpPassed'] == actual['httpTotal'] == 24 and actual['portable']['checks'] == 52 and actual['supplemental']['checks'] == 80, 'Golden complete contract counts')
        need(actual['generation']['before'] == 1 and actual['generation']['after'] == 2 and actual['browser']['strictPassed'] is True and actual['browser']['assetsPassed'] is True and actual['browser']['resource']['completeResourceBody'] is True, 'Golden application/browser/resource gates')
        arms[arm] = {key: actual[key] for key in ('httpPassed', 'portable', 'supplemental', 'generation', 'streaming')}
        arms[arm].update(originalOwner=owner, rawExitCode=0, strictPassed=True, resourceComplete=True)
    reviewed = {descriptor(ref) for ref in review['reviewedInputs']}
    marked = {descriptor(item['source']) for item in entries if item['reviewedInput']}
    need(len(reviewed) == index['reviewedInputTuples'] == 210 and reviewed == marked and all(key[0] in seen for key in reviewed), 'Every original reviewer input copied and used through the copy-only seam')
    need(index['verifiedDataReviewPassed'] is index['allFullContractsPassed'] is True and index['deepNativePayloadsRetained'] is index['fullNextAccepted'] is False, 'Retained review/omission scope')
    need(all(stamp(p) == before for p, before in STAMPS.items()), 'Final retained read bookends')
    print(json.dumps(dict(state='SAVED_CLONE_CANCEL_NEXT_FULL_THREE_ARM_SAMPLE_PASSED_V1', passed=True,
        payloadFiles=EXPECTED_FILES, retainedBytes=EXPECTED_BYTES, expandedBytes=expanded, reviewedInputTuples=210, arms=arms,
        originalPathReads=False, nativeOrToolExecution=False, freshHostExecution=False,
        callbackNamespaceAbsence='Original closed observation only; no fresh physical directory claim',
        omittedScope=index['omissions'], fullNextAccepted=False), ensure_ascii=False))


if __name__ == '__main__':
    main()
