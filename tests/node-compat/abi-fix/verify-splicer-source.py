#!/usr/bin/env python3
"""Verify every source file against the pinned archive and explicit edits."""
import datetime
import hashlib
import json
import pathlib
import sys
import tarfile

archive, source, profile, output = map(str, sys.argv[1:])
archive, source, output = pathlib.Path(archive), pathlib.Path(source), pathlib.Path(output)
assert profile in ['import-i32-v1', 'import-i32-clock-v2']
def sha(data): return hashlib.sha256(data).hexdigest()
archive_sha = '8178fb678ec1b8a33bbf3fa8db066bffe4dbf6a92c235150f56622b44ea27e10'
assert sha(archive.read_bytes()) == archive_sha, 'Archive mismatch'
edits = {
    'Cargo.lock': '6472e3cd45eeaacdd5f7133e8eaab8e4411ef77272812d97dd6ac729462f6ffd',
    'crates/spidermonkey-embedding-splicer/src/splice.rs': 'f54d9d7562c525131def2a89d512883118d3c7a6af29a1e1021dfec76c31a048',
}
if profile == 'import-i32-clock-v2':
    edits['crates/spidermonkey-embedding-splicer/src/stub_wasi.rs'] = 'a8bd26e5ab6edba7a83dcf8642e2c591c1465f92f0bf3f0c8eda15a99c3da2d8'
entries = []
with tarfile.open(archive, 'r:gz') as handle:
    for entry in handle.getmembers():
        assert not entry.issym() and not entry.islnk(), 'Unexpected source archive link'
        if not entry.isfile(): continue
        path = '/'.join(pathlib.PurePosixPath(entry.name).parts[1:])
        assert path and '..' not in pathlib.PurePosixPath(path).parts
        upstream = sha(handle.extractfile(entry).read())
        expected = edits.get(path, upstream)
        actual_path = source / path
        assert actual_path.is_file() and not actual_path.is_symlink(), path
        actual = sha(actual_path.read_bytes())
        assert actual == expected, f'Unreviewed source change: {path}: {actual} != {expected}'
        entries.append({'path': path, 'sha256': actual, 'upstreamSha256': upstream,
                        'explicitlyModified': path in edits})
entries.sort(key=lambda item: item['path'])
expected_paths = {entry['path'] for entry in entries}
actual_paths = {str(path.relative_to(source)) for path in source.rglob('*') if path.is_file() or path.is_symlink()}
assert actual_paths - {'.source-archive-sha256'} == expected_paths, 'Missing or extra source files'
marker = source / '.source-archive-sha256'
if marker.exists(): assert marker.read_text().strip() == archive_sha
proof = {'schemaVersion': 1, 'verifiedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'archivePath': str(archive), 'archiveSha256': archive_sha, 'sourceDirectory': str(source),
         'profile': profile, 'archiveMarkerPresent': marker.exists(), 'fileCount': len(entries), 'explicitlyModifiedPaths': sorted(edits),
         'treeSha256': sha(json.dumps(entries, sort_keys=True, separators=(',', ':')).encode()),
         'sourceManifest': entries,
         'scope': 'Complete regular-file source inventory compared with pristine pinned archive; only the named versioned Rust patch(es) and exact lock repair differ. No extra source files or source symlinks accepted.'}
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(proof, indent=2) + '\n')
print(json.dumps({'proofPath': str(output), 'files': len(entries), 'treeSha256': proof['treeSha256']}))
