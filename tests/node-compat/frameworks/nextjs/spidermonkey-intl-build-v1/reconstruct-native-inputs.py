"""Copy the exact current-C2 baseline inputs from a reviewed repository checkout.

No donor is imported or executed. This does not apply Intl/Error overlays,
fetch tools, configure, build, or make a metadata/runtime acceptance claim.
Run --check for a read-only donor check, or pass one fresh absolute output root.
The three retained afterimages must travel in the same committed checkout as
the map; repository commit authorization remains the caller's responsibility.
"""
from pathlib import Path, PurePosixPath
import collections
import hashlib
import json
import os
import stat
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
MAP = HERE / 'portable-native-inputs.json'


def relative(value):
    if not isinstance(value, str) or not value or '\\' in value or '\0' in value:
        raise ValueError('Expected a nonempty relative POSIX path')
    parts = value.split('/')
    if any(part in ('', '.', '..') for part in parts):
        raise ValueError('Absolute, empty, or traversal path component')
    path = PurePosixPath(value)
    if path.is_absolute() or str(path) != value:
        raise ValueError('Noncanonical relative path')
    return Path(*parts)


def no_links(path):
    for item in (path, *path.parents):
        if item.is_symlink():
            raise ValueError('Symlink refused: ' + str(item))


def file_bytes(path, row):
    no_links(path)
    before = path.stat()
    if not stat.S_ISREG(before.st_mode):
        raise ValueError('Regular donor required: ' + str(path))
    with path.open('rb') as stream:
        raw = stream.read(row['bytes'] + 1)
    after = path.stat()
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    if any(getattr(before, key) != getattr(after, key) for key in fields):
        raise ValueError('Donor changed during read: ' + str(path))
    if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
        raise ValueError('Donor bytes/hash differ: ' + str(path))
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    if blob != row['gitBlobSha1']:
        raise ValueError('Donor Git blob differs: ' + str(path))
    return raw


def validated():
    no_links(MAP)
    map_raw = MAP.read_bytes()
    mapping = json.loads(map_raw)
    if mapping['state'] != 'EXACT_CURRENT_C2_BASELINE_PORTABLE_SOURCE_MAP_NO_INTL_OR_ERROR_OVERLAY':
        raise ValueError('Unexpected baseline map')
    rows = mapping['files']
    if len(rows) != 824 or sum(row['bytes'] for row in rows) != 7507787:
        raise ValueError('Unexpected finite input boundary')
    counts = collections.Counter(row['role'] for row in rows)
    if counts != {'native-policy-source': 435, 'build-support': 386, 'componentize-embedding': 3}:
        raise ValueError('Unexpected role counts')
    seen = set()
    data = []
    for row in rows:
        destination = relative(row['destination'])
        expected_root = 'componentize-source' if row['role'] == 'componentize-embedding' else 'native-source'
        if destination.parts[0] != expected_root or len(destination.parts) < 2 or destination in seen:
            raise ValueError('Duplicate or out-of-scope destination')
        seen.add(destination)
        mode = int(row['copyMode'], 8)
        if mode not in (0o600, 0o644, 0o755):
            raise ValueError('Unexpected copy mode')
        donor = row['repositoryDonor']
        if donor['bytes'] != row['bytes'] or donor['sha256'] != row['sha256']:
            raise ValueError('Donor/destination descriptor mismatch')
        path = REPO / relative(donor['path'])
        data.append((row, destination, mode, file_bytes(path, donor)))
    return mapping, hashlib.sha256(map_raw).hexdigest(), data


def main(argument):
    mapping, map_sha, data = validated()
    summary = dict(schemaVersion=1, state='BASELINE_SOURCE_DONORS_VERIFIED_NO_BUILD',
                   mapSha256=map_sha, files=len(data), bytes=sum(len(item[3]) for item in data),
                   currentC2BaselineOnly=True, intlOrErrorOverlayApplied=False,
                   donorCodeOrBuildToolExecuted=False, buildOrGuestExecuted=False)
    if argument == '--check':
        print(json.dumps(summary, indent=2))
        return
    output = Path(argument)
    if not output.is_absolute() or str(output) != argument or '..' in output.parts:
        raise ValueError('Output must be a canonical absolute path')
    no_links(output)
    if output.exists() or not output.parent.is_dir():
        raise ValueError('Output must be fresh under an existing parent')
    for source in (REPO, Path(mapping['originalWorkRoot']), Path(mapping['originalCompositionRoot'])):
        if output == source or source in output.parents:
            raise ValueError('Output may not be inside repository or original inputs')
    os.umask(0o077)
    output.mkdir(mode=0o700)
    written = []
    try:
        for row, destination, mode, raw in data:
            path = output / destination
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            no_links(path)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(raw)
                stream.flush()
                os.fchmod(stream.fileno(), mode)
                os.fsync(stream.fileno())
            if path.read_bytes() != raw or stat.S_IMODE(path.stat().st_mode) != mode:
                raise ValueError('Output copy differs: ' + str(destination))
            written.append(row['destination'])
        actual = {str(path.relative_to(output)) for path in output.rglob('*') if path.is_file()}
        if actual != set(written):
            raise ValueError('Output membership differs')
        summary['state'] = 'BASELINE_SOURCE_RECONSTRUCTED_NO_BUILD'
        summary['outputRoot'] = str(output)
    except BaseException as error:
        summary.update(state='SOURCE_COPY_FAILED_PARTIAL_OUTPUT_PRESERVED', written=written,
                       error=dict(type=type(error).__name__, message=str(error)))
        raise
    finally:
        with (output / 'source-reconstruction.json').open('x') as stream:
            json.dump(summary, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: reconstruct-native-inputs.py --check | /fresh/absolute/output')
    main(sys.argv[1])
