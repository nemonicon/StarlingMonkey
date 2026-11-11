"""Materialize the exact 271-file clock-I/O compiler Source; never build or invoke it."""
from pathlib import Path
import hashlib
import json
import os
import re
import stat
import sys
import tarfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ROOT = Path('/private/tmp/starling-node-compat/next-lifecycle-compiler-recovery-v1-first')
SOURCE = ROOT / 'source'
ARCHIVE = dict(path='/private/tmp/starling-node-compat/componentize-source-origin-v1-y69vgxkz/componentize-source.tar.gz', sha256='8178fb678ec1b8a33bbf3fa8db066bffe4dbf6a92c235150f56622b44ea27e10', bytes=162093)
CUT = dict(path=str(REPO / 'tests/node-compat/foundation-scheduler/clock-io-pruning-candidate-v1/source-cut.json'), sha256='356b802f11ee7730b23b8e43ef6cec62d6a962d1eb7e0921ab5b094e29b6ad3b', bytes=259329)
PATCH = dict(path=str(REPO / 'tests/node-compat/abi-fix/componentize-import-i32-v1.patch'), sha256='d300e345cb56a5bb1560f1f993c2cc763bca273e6bcf51e38aadc8e27d84782c', bytes=0)
AFTER_ROOT = REPO / 'tests/node-compat/foundation-scheduler/clock-io-pruning-candidate-v1/after'


def require(value, message):
    if not value:
        raise ValueError(message)


def stamp(s):
    return s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns


def checked(ref, finite=16 * 1024**2):
    p = Path(ref['path'])
    require(p.is_absolute() and p.resolve() == p and not any(q.is_symlink() for q in (p, *p.parents)), 'canonical input')
    before = p.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= finite, 'finite regular nlink1 input')
    raw = p.read_bytes()
    require((len(raw), hashlib.sha256(raw).hexdigest()) == (ref['bytes'], ref['sha256']), 'exact input ' + str(p))
    require(stamp(before) == stamp(p.lstat()), 'read bookend changed')
    return raw


def local(name):
    require(type(name) is str and name and not name.startswith('/') and '\\' not in name and '\0' not in name, 'relative member')
    require(all(x not in ('', '.', '..') for x in name.split('/')), 'safe relative components')
    return name


def apply_exact_patch(data, text):
    lines = text.splitlines(keepends=True)
    require(lines[0].startswith('--- a/') and lines[1].startswith('+++ b/'), 'one exact unified patch')
    name = local(lines[0][6:].rstrip('\n'))
    require(lines[1][6:].rstrip('\n') == name, 'same patch target')
    original = data[name].decode('utf-8').splitlines(keepends=True)
    output, cursor, i = [], 0, 2
    while i < len(lines):
        match = re.fullmatch(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@\n', lines[i])
        require(match is not None, 'exact hunk header')
        start = int(match[1]) - 1
        require(start >= cursor, 'ordered exact hunks')
        output.extend(original[cursor:start]); cursor = start
        old_count = new_count = 0
        i += 1
        while i < len(lines) and not lines[i].startswith('@@ '):
            item = lines[i]
            require(item[:1] in (' ', '+', '-'), 'ordinary hunk line')
            if item[:1] in (' ', '-'):
                require(cursor < len(original) and original[cursor] == item[1:], 'exact patch context, no fuzz')
                cursor += 1; old_count += 1
            if item[:1] in (' ', '+'):
                output.append(item[1:]); new_count += 1
            i += 1
        require(old_count == int(match[2] or 1) and new_count == int(match[4] or 1), 'hunk counts')
    output.extend(original[cursor:])
    data[name] = ''.join(output).encode()


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Requires nonoptimized isolated Python with bytecode disabled')
    require(sys.argv == [str(Path(__file__))], 'fixed no-argument materializer')
    manifest_path = HERE / 'source-manifest.json'
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)
    require(manifest['archive'] == ARCHIVE and manifest['sourceCut'] == CUT, 'declared original inputs')
    require(manifest['sourceRoot'] == str(SOURCE) and manifest['files'] == 271, 'exact fresh Source target')
    archive = checked(ARCHIVE)
    cut = json.loads(checked(CUT))
    patch_ref = manifest['importI32Patch']
    require(patch_ref['path'] == PATCH['path'] and patch_ref['sha256'] == PATCH['sha256'], 'original import-I32 correction')
    patch_text = checked(patch_ref).decode('utf-8')
    data = {}
    # tarfile reads authenticated compressed bytes only; no extract/extractall API.
    import io
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as bundle:
        members = bundle.getmembers()
        require(len(members) <= 1024, 'bounded archive entries')
        for member in members:
            require(member.isdir() or member.isfile(), 'no archive links/devices')
            if member.isdir():
                continue
            prefix, name = member.name.split('/', 1)
            require(prefix == 'ComponentizeJS-4d812f5a7b524cea5bcfd565cac55f3fab876a57', 'pinned archive root')
            name = local(name)
            require(name not in data and 0 <= member.size <= 4 * 1024**2, 'bounded unique file')
            data[name] = bundle.extractfile(member).read()
    require(len(data) == 270 and sum(map(len, data.values())) <= 4 * 1024**2, 'exact upstream regular set')
    apply_exact_patch(data, patch_text)
    data['.source-archive-sha256'] = (ARCHIVE['sha256'] + '\n').encode()
    expected = {row['path']: row for row in cut['files']}
    modes = {row['relativePath']: row['mode'] for row in cut['baseline']['files']}
    afterimages = []
    for member in cut['files']:
        if member['origin'] == 'CORRECTED_AFTERIMAGE':
            name = local(member['path'])
            ref = dict(path=str(AFTER_ROOT / name), sha256=member['sha256'], bytes=member['bytes'])
            data[name] = checked(ref); afterimages.append(ref)
        else:
            require(member['origin'] == 'UNCHANGED_BASELINE', 'known Source origin')
    require(len(afterimages) == 4 and len(data) == len(expected) == len(modes) == 271, 'complete Source and four afterimages')
    for name, raw in data.items():
        require(name in expected and (hashlib.sha256(raw).hexdigest(), len(raw)) == (expected[name]['sha256'], expected[name]['bytes']), 'full Source byte proof ' + name)
        require(modes[name] in (0o644, 0o755), 'captured Source mode')
    require(manifest['members'] == [dict(path=name, sha256=expected[name]['sha256'], bytes=expected[name]['bytes'], mode=modes[name]) for name in sorted(expected)], 'whole Source manifest equality')
    # No output until all upstream bytes, correction, afterimages and 271 expectations passed.
    require(ROOT.is_dir() and ROOT.resolve() == ROOT and not any(q.is_symlink() for q in (ROOT, *ROOT.parents)), 'existing independent owned recovery root')
    require(not SOURCE.exists() and not SOURCE.is_symlink(), 'fresh Source namespace')
    receipt_path = ROOT / 'source-materialization.json'
    require(not receipt_path.exists() and not receipt_path.is_symlink(), 'exclusive receipt')
    SOURCE.mkdir(mode=0o700)
    for name in sorted(data):
        target = SOURCE / name
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with target.open('xb') as out:
            out.write(data[name]); out.flush(); os.fsync(out.fileno())
        target.chmod(modes[name])
    for name, raw in data.items():
        require((SOURCE / name).read_bytes() == raw, 'full final Source bytes')
    require(sorted(q.relative_to(SOURCE).as_posix() for q in SOURCE.rglob('*') if q.is_file()) == sorted(data), 'exact final file membership')
    for ref in [ARCHIVE, CUT, patch_ref, *afterimages]:
        checked(ref)
    require(manifest_path.read_bytes() == manifest_raw, 'manifest bookend')
    receipt = dict(schemaVersion=1, state='EXACT_CLOCK_IO_COMPILER_SOURCE_MATERIALIZED_NOT_BUILT_V1', sourceRoot=str(SOURCE), sourceFiles=271,
        sourceBytes=sum(map(len, data.values())), sourceCut=CUT, archive=ARCHIVE, importI32Patch=patch_ref, afterimages=afterimages,
        manifest=dict(path=str(manifest_path), sha256=hashlib.sha256(manifest_raw).hexdigest(), bytes=len(manifest_raw)),
        sourceMembers=manifest['members'], exactAll271HashesVerified=True, originalSourceOrEvidenceModified=False,
        packageBuilt=False, nativeEngineBuilt=False, componentConstructed=False, guestExecuted=False)
    with receipt_path.open('x') as out:
        json.dump(receipt, out, indent=2); out.write('\n'); out.flush(); os.fsync(out.fileno())
    print(json.dumps(dict(receipt=str(receipt_path), sourceRoot=str(SOURCE), files=271, bytes=receipt['sourceBytes'])))


if __name__ == '__main__':
    main()
