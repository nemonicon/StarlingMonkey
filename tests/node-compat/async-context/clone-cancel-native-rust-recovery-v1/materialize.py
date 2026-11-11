#!/usr/bin/env python3
"""Root-only offline copies; never invokes Rust, rustup, CMake or another tool."""
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import sys
import tarfile

if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
    raise RuntimeError('use Python -I -B without optimization')

HERE = Path(__file__).resolve().parent
ROOT = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-rust-recovery-v1-first')
GLOBAL_RUST = Path('/Users/dan/.rustup/toolchains/1.88.0-aarch64-apple-darwin')
RUST_INVENTORY = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-build-v4-root-results/rust-inventory.json', 'sha256': '8612936caa7e277bb9497bce9044058062d2239e6b6193667ebb33f86d9afd58', 'bytes': 55499}
CORROSION_INVENTORY = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/frameworks/nextjs/next-native-build-v4-root-results/corrosion-inventory.json', 'sha256': '9a2ccd2c888f527759492a0f22858872985fa6abf2998614f66f98b111f962ad', 'bytes': 91493}
RUST_AUDIT = {'path': str(HERE / 'rust-donor-audit.json'), 'sha256': 'a821e3b1b6891137aa30740d101502f8d654de15d5846c1b80cf9826d69e7ad8', 'bytes': 174561}
CORROSION_ARCHIVE = {'path': '/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first/archives/corrosion-v0.5.1.tar.gz', 'sha256': '843334a9f0f5efbc225dccfa88031fe0f2ec6fd787ca1e7d55ed27b2c25d9c97', 'bytes': 91574}  # Root downloaded; R independently compared all 193 source payloads.
CORROSION_URL = 'https://github.com/corrosion-rs/corrosion/archive/refs/tags/v0.5.1.tar.gz'
INPUTS = {}
DIRECTORIES = {}
CAP = 512 * 1024 * 1024


def snapshot(p):
    s = p.lstat()
    return tuple(getattr(s, k) for k in ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'))


def digest(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        while b := f.read(1024 * 1024):
            h.update(b)
    return h.hexdigest()


def checked(ref, mode=None):
    assert set(ref) == {'path', 'sha256', 'bytes'}
    assert type(ref['bytes']) is int and 0 <= ref['bytes'] <= CAP
    p = Path(ref['path']); before = snapshot(p)
    assert p.is_absolute() and p.resolve() == p and stat.S_ISREG(before[2]) and before[3] == 1
    assert before[4] == ref['bytes'] and digest(p) == ref['sha256'] and snapshot(p) == before
    if mode is not None:
        assert stat.S_IMODE(before[2]) == mode
    INPUTS[str(p)] = (ref, before)
    return p


def document(ref):
    assert ref['bytes'] <= 1024 * 1024
    p = checked(ref); b = p.read_bytes()
    assert snapshot(p) == INPUTS[str(p)][1] and len(b) == ref['bytes'] and hashlib.sha256(b).hexdigest() == ref['sha256']
    return json.loads(b)


def relative(text):
    p = Path(text)
    assert isinstance(text, str) and text and not p.is_absolute() and len(p.parts) <= 32
    assert p.as_posix() == text and all(x not in ('', '.', '..') for x in p.parts) and '\\' not in text and '\x00' not in text
    return p


def historical(ref, omit_git=False):
    old = document(ref); rows = {}
    for r in old['entries']:
        rel = relative(r['path'])
        if omit_git and rel.parts[0] == '.git':
            continue
        assert r['path'] not in rows and r['kind'] in ('file', 'directory')
        assert r['mode'] in (0o600, 0o700)
        rows[r['path']] = r
    assert len(rows) <= 1000
    for name in rows:
        for parent in relative(name).parents:
            if parent != Path('.'):
                assert parent.as_posix() in rows and rows[parent.as_posix()]['kind'] == 'directory'
    return old, rows


def remember_directory(p, mode):
    before = snapshot(p)
    assert p.resolve() == p and stat.S_ISDIR(before[2]) and stat.S_IMODE(before[2]) == mode
    DIRECTORIES[str(p)] = before


def rust_selection():
    old, rows = historical(RUST_INVENTORY)
    audit = document(RUST_AUDIT)
    assert audit['historicalInventory'] == RUST_INVENTORY and audit['globalRoot'] == str(GLOBAL_RUST)
    records = {r['relativePath']: r for r in audit['records']}
    assert set(records) == set(rows) and len(rows) == 178
    remember_directory(GLOBAL_RUST, 0o755)
    sources = {}; rewritten = {}
    for name, row in rows.items():
        donor = records[name]['global']; p = GLOBAL_RUST / relative(name)
        assert donor['path'] == str(p) and donor['status'] == 'present' and donor['kind'] == row['kind']
        if row['kind'] == 'directory':
            remember_directory(p, donor['mode']); continue
        ref = {k: donor[k] for k in ('path', 'sha256', 'bytes')}
        sources[name] = checked(ref, donor['mode'])
        if name == 'lib/rustlib/components':
            raw = p.read_bytes(); lines = raw.splitlines(keepends=True)
            assert lines == [b'rust-std-aarch64-apple-darwin\n', b'cargo-aarch64-apple-darwin\n', b'rustc-aarch64-apple-darwin\n']
            rewritten[name] = lines[1] + lines[0] + lines[2] + b'rust-std-wasm32-wasip1\n'
        elif name == 'lib/rustlib/multirust-config.toml':
            parts = p.read_bytes().split(b'[[components]]\n')
            assert len(parts) == 5
            rewritten[name] = parts[0] + b''.join(b'[[components]]\n' + parts[i + 1] for i in (2, 0, 1, 3))
        else:
            assert donor['sha256'] == row['sha256'] and donor['bytes'] == row['bytes']
        if name in rewritten:
            b = rewritten[name]
            assert len(b) == row['bytes'] and hashlib.sha256(b).hexdigest() == row['sha256']
    assert len(rewritten) == 2 and sum(r['kind'] == 'file' for r in rows.values()) == 155
    return old, rows, sources, rewritten, None


def corrosion_selection():
    assert CORROSION_ARCHIVE is not None, 'unbound Corrosion archive: no writes'
    old, rows = historical(CORROSION_INVENTORY, omit_git=True)
    assert len(rows) == 306 and sum(r['kind'] == 'file' for r in rows.values()) == 193
    archive = checked(CORROSION_ARCHIVE); members = {}; top = 'corrosion-0.5.1'
    with tarfile.open(archive, 'r:gz') as t:
        for m in t:
            assert len(members) < 1000 and not m.issparse() and m.mode & ~0o777 == 0
            name = m.name.rstrip('/'); rel = relative(name)
            assert rel.parts[0] == top
            if len(rel.parts) == 1:
                assert m.isdir(); continue
            name = Path(*rel.parts[1:]).as_posix()
            assert name not in members and name in rows, 'unexpected/duplicate archive source entry'
            row = rows[name]
            assert (m.isfile() and row['kind'] == 'file') or (m.isdir() and row['kind'] == 'directory')
            if m.isfile():
                assert m.size == row['bytes'] and 0 <= m.size <= 1024 * 1024
                h = hashlib.sha256(); count = 0
                with t.extractfile(m) as f:
                    while b := f.read(65536):
                        count += len(b); assert count <= row['bytes']; h.update(b)
                assert count == row['bytes'] and h.hexdigest() == row['sha256'], 'archive source payload differs'
            members[name] = m
    assert set(members) == set(rows), 'archive lacks historical non-Git source membership'
    return old, rows, {}, {}, members


def fsync_dir(p):
    fd = os.open(p, os.O_RDONLY); primary = None
    try:
        os.fsync(fd)
    except BaseException as e:
        primary = e
    try:
        os.close(fd)
    except BaseException:
        if primary is not None: raise primary
        raise
    if primary is not None: raise primary


def copy_file(dest, source, row):
    fd = None; primary = None
    try:
        fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        h = hashlib.sha256(); count = 0
        while b := source.read(1024 * 1024):
            count += len(b); assert count <= row['bytes']; h.update(b); view = memoryview(b)
            while view:
                n = os.write(fd, view); assert n > 0; view = view[n:]
        assert count == row['bytes'] and h.hexdigest() == row['sha256']
        os.fchmod(fd, row['mode']); os.fsync(fd)
    except BaseException as e:
        primary = e
    for close in (source.close, (lambda: os.close(fd)) if fd is not None else None):
        if close is not None:
            try: close()
            except BaseException as e:
                if primary is None: primary = e
    if primary is not None: raise primary


def output_inventory(out, rows):
    observed = set(); pending = [out]; result = []; inodes = set()
    while pending:
        for p in pending.pop().iterdir():
            name = p.relative_to(out).as_posix(); assert name in rows and name not in observed; observed.add(name)
            if stat.S_ISDIR(p.lstat().st_mode): pending.append(p)
    assert observed == set(rows)
    for name, row in sorted(rows.items()):
        p = out / name; before = snapshot(p)
        assert p.resolve() == p and stat.S_IMODE(before[2]) == row['mode']
        r = {'path': name, 'kind': row['kind'], 'mode': row['mode'], 'dev': before[0], 'ino': before[1], 'nlink': before[3]}
        if row['kind'] == 'file':
            assert stat.S_ISREG(before[2]) and before[3] == 1 and before[:2] not in inodes; inodes.add(before[:2])
            assert before[4] == row['bytes'] and digest(p) == row['sha256']
            r.update(bytes=before[4], sha256=row['sha256'])
        else:
            assert stat.S_ISDIR(before[2])
        assert snapshot(p) == before; result.append(r)
    return result


def main():
    assert len(sys.argv) == 2 and sys.argv[1] in ('--rust', '--corrosion')
    role = sys.argv[1][2:]
    if role == 'corrosion': assert CORROSION_ARCHIVE is not None, 'unbound archive before reads/writes'
    out = ROOT / role; result_path = ROOT / (role + '-result.json')
    assert ROOT.resolve() == ROOT and not os.path.lexists(out) and not os.path.lexists(result_path)
    old, rows, sources, rewritten, members = rust_selection() if role == 'rust' else corrosion_selection()
    checked({'path': str(Path(__file__).resolve()), 'sha256': digest(Path(__file__).resolve()), 'bytes': Path(__file__).stat().st_size})
    if not ROOT.exists(): ROOT.mkdir(mode=0o700)
    assert ROOT.is_dir() and ROOT.resolve() == ROOT
    result = {'schemaVersion': 1, 'state': 'PRIVATE_TOOL_SOURCE_RECOVERY_FAILED_V1', 'role': role, 'root': str(out), 'historicalInventory': RUST_INVENTORY if role == 'rust' else CORROSION_INVENTORY, 'inputs': [r for r, _ in INPUTS.values()], 'reconstructedReceiptPaths': sorted(rewritten), 'gitMetadataMaterialized': False, 'toolCommandsExecuted': False, 'oldInodeOrMtimeClaimed': False, 'errors': [], 'secondaryErrors': []}
    primary = None
    try:
        out.mkdir(mode=old['rootIdentity']['mode'])
        for name, row in sorted(rows.items(), key=lambda x: (len(Path(x[0]).parts), x[0])):
            if row['kind'] == 'directory': (out / name).mkdir(mode=row['mode'])
        archive = tarfile.open(CORROSION_ARCHIVE['path'], 'r:gz') if role == 'corrosion' else None
        copy_error = None
        try:
            for name, row in rows.items():
                if row['kind'] != 'file': continue
                assert (out / name).parent.resolve() == (out / name).parent
                source = io.BytesIO(rewritten[name]) if name in rewritten else archive.extractfile(members[name]) if archive is not None else sources[name].open('rb')
                assert source is not None; copy_file(out / name, source, row)
        except BaseException as e:
            copy_error = e
        if archive is not None:
            try: archive.close()
            except BaseException:
                if copy_error is not None: raise copy_error
                raise
        if copy_error is not None: raise copy_error
        for name, row in sorted(rows.items(), key=lambda x: -len(Path(x[0]).parts)):
            if row['kind'] == 'directory': fsync_dir(out / name)
        fsync_dir(out); result['entries'] = output_inventory(out, rows)
        s = out.stat(); assert stat.S_IMODE(s.st_mode) == old['rootIdentity']['mode']; result['rootIdentity'] = {'path': str(out), 'dev': s.st_dev, 'ino': s.st_ino, 'mode': stat.S_IMODE(s.st_mode), 'nlink': s.st_nlink}
    except BaseException as e:
        primary = e; result['errors'].append({'type': type(e).__name__, 'message': str(e)})
    try:
        for path, (ref, before) in INPUTS.items():
            assert snapshot(Path(path)) == before and digest(Path(path)) == ref['sha256'] and snapshot(Path(path)) == before
        for path, before in DIRECTORIES.items(): assert snapshot(Path(path)) == before
        result['inputsPreserved'] = True
    except BaseException as e:
        result['inputsPreserved'] = False
        if primary is None: primary = e; result['errors'].append({'type': type(e).__name__, 'message': str(e)})
        else: result['secondaryErrors'].append({'type': type(e).__name__, 'message': str(e)})
    if primary is None: result['state'] = 'PRIVATE_TOOL_SOURCE_RECOVERY_VERIFIED_V1'
    raw = (json.dumps(result, indent=2) + '\n').encode()
    try:
        copy_file(result_path, io.BytesIO(raw), {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'mode': 0o600}); fsync_dir(ROOT)
        assert result_path.stat().st_size == len(raw) and digest(result_path) == hashlib.sha256(raw).hexdigest()
    except BaseException:
        if primary is not None: raise primary
        raise
    print(json.dumps({'state': result['state'], 'result': {'path': str(result_path), 'sha256': digest(result_path), 'bytes': result_path.stat().st_size}, 'role': role}), flush=True)
    if primary is not None: raise primary


if __name__ == '__main__':
    main()
