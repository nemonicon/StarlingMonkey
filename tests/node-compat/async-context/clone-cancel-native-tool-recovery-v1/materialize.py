#!/usr/bin/env python3
"""Root-run, six pinned archives only; no tool command is executed."""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tarfile
import unicodedata

if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
    raise RuntimeError('run with Python -I -B, without optimization')

ROOT = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first')
PLAN = {'path': '/Users/dan/dev/StarlingMonkey/tests/node-compat/async-context/clone-cancel-native-build-plan-v1/recovery-plan.json', 'sha256': 'ed6f6a4ad53b4d1243cde1aa915f870d93371106fe102c3669ab1b7bd4552815', 'bytes': 15046}
DOWNLOADS = {'path': str(ROOT / 'archive-downloads.json'), 'sha256': '603a129b6292df6a262eb84741d44ebff43de5992fcabe347743bdbe78e500f8', 'bytes': 2743}
TOPS = {'wasi-sdk': 'wasi-sdk-30.0-arm64-macos', 'binaryen': 'binaryen-version_123', 'wasm-tools': 'wasm-tools-1.235.0-aarch64-macos', 'wasmtime': 'wasmtime-v42.0.1-aarch64-macos', 'weval': 'weval-v0.5.1-aarch64-macos', 'openssl': 'openssl-3.0.17'}
OUT = ROOT / 'tools'
RESULT = ROOT / 'tool-recovery-result.json'
LIMIT_MEMBERS = 20000
LIMIT_FILE = 512 * 1024 * 1024
LIMIT_TOTAL = 2 * 1024 * 1024 * 1024
INPUTS = {}


def snapshot(p):
    s = p.lstat()
    return tuple(getattr(s, k) for k in ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'))


def sha_file(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def checked(ref):
    assert set(ref) == {'path', 'sha256', 'bytes'}
    p = Path(ref['path'])
    before = snapshot(p)
    assert p.is_absolute() and p.resolve() == p and stat.S_ISREG(before[2]) and before[3] == 1
    assert before[4] == ref['bytes'] and sha_file(p) == ref['sha256']
    assert snapshot(p) == before
    INPUTS[str(p)] = (ref, before)
    return p


def document(ref):
    assert 0 < ref['bytes'] <= 1024 * 1024
    return json.loads(checked(ref).read_bytes())


def confined_parts(text, base=()):
    assert isinstance(text, str) and text and len(text.encode('utf-8')) <= 1024
    assert not text.startswith('/') and '\\' not in text and '\x00' not in text
    parts = list(base)
    for item in text.split('/'):
        if item in ('', '.'):
            continue
        if item == '..':
            assert parts, 'link escapes its selected tool root'
            parts.pop()
        else:
            parts.append(item)
    assert len(parts) <= 32
    return tuple(parts)


def archive_plan(row):
    """Validate the complete virtual namespace, including links, before writes."""
    role = row['role']
    p = checked(row['archive'])
    entries = {}
    folded = set()
    payload_bytes = 0
    with tarfile.open(p, 'r:*') as t:
        for m in t:
            assert len(entries) < LIMIT_MEMBERS
            name = m.name.rstrip('/')
            parts = confined_parts(name)
            assert parts and parts[0] == TOPS[role]
            assert '/'.join(parts) == name, 'noncanonical archive member'
            rel = parts[1:]
            assert rel not in entries, 'duplicate archive member'
            key = unicodedata.normalize('NFC', '/'.join(rel)).casefold()
            assert key not in folded, 'filesystem case/normalization collision'
            folded.add(key)
            kind = 'file' if m.isfile() else 'dir' if m.isdir() else 'symlink' if m.issym() else 'hardlink' if m.islnk() else None
            assert kind is not None, 'special/sparse archive entry refused'
            assert not m.issparse() and not (m.mode & ~0o777)
            assert 0 <= m.size <= LIMIT_FILE
            if kind == 'file':
                payload_bytes += m.size
                assert payload_bytes <= LIMIT_TOTAL
            if not rel:
                assert kind == 'dir'
            entries[rel] = {'member': m, 'kind': kind, 'mode': m.mode}
    # Infer only absent directories. A link or file may never be an ancestor.
    dirs = {()}
    for rel, e in entries.items():
        if e['kind'] == 'dir':
            dirs.add(rel)
        for i in range(len(rel)):
            parent = rel[:i]
            assert parent not in entries or entries[parent]['kind'] == 'dir'
            dirs.add(parent)
        if e['kind'] == 'symlink':
            e['target'] = confined_parts(e['member'].linkname, rel[:-1])
        elif e['kind'] == 'hardlink':
            target = confined_parts(e['member'].linkname)
            assert target and target[0] == TOPS[role]
            assert '/'.join(target) == e['member'].linkname
            e['target'] = target[1:]
    all_folded = [unicodedata.normalize('NFC', '/'.join(p)).casefold() for p in set(entries) | dirs]
    assert len(all_folded) == len(set(all_folded)), 'implicit directory alias'

    def resolve(parts, seen=()):
        assert len(seen) <= 128
        for i in range(1, len(parts) + 1):
            prefix = parts[:i]
            entry = entries.get(prefix)
            if entry and entry['kind'] in ('symlink', 'hardlink'):
                assert prefix not in seen, 'archive link cycle'
                return resolve(entry['target'] + parts[i:], seen + (prefix,))
            if i < len(parts):
                assert prefix in dirs, 'missing/non-directory link ancestor'
        return parts

    for rel, e in entries.items():
        if e['kind'] in ('symlink', 'hardlink'):
            target = resolve(e['target'], (rel,))
            assert target in dirs or target in entries, 'dangling archive link'
            if e['kind'] == 'hardlink':
                assert e['target'] == target and target in entries and entries[target]['kind'] == 'file'
                assert e['mode'] == entries[target]['mode'], 'hardlink modes disagree'
            e['resolved'] = target
    return {'role': role, 'archive': row['archive'], 'entries': entries, 'dirs': dirs, 'payloadBytes': payload_bytes}


def fsync_dir(p):
    fd = os.open(p, os.O_RDONLY)
    primary = None
    try:
        os.fsync(fd)
    except BaseException as error:
        primary = error
    try:
        os.close(fd)
    except BaseException:
        if primary is not None:
            raise primary
        raise
    if primary is not None:
        raise primary


def write_member(dest, source, member):
    fd = None
    primary = None
    try:
        fd = os.open(dest, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        count = 0
        while b := source.read(1024 * 1024):
            count += len(b)
            assert count <= member.size
            view = memoryview(b)
            while view:
                written = os.write(fd, view)
                assert written > 0
                view = view[written:]
        assert count == member.size
        os.fchmod(fd, member.mode)
        os.fsync(fd)
    except BaseException as error:
        primary = error
    for close in (source.close, (lambda: os.close(fd)) if fd is not None else None):
        if close is not None:
            try:
                close()
            except BaseException as error:
                if primary is None:
                    primary = error
    if primary is not None:
        raise primary


def materialize(selected):
    root = OUT / selected['role']
    root.mkdir(mode=0o700)
    for rel in sorted(selected['dirs'], key=lambda p: (len(p), p)):
        if rel:
            root.joinpath(*rel).mkdir(mode=0o700)
    # No tar extraction API or archive ownership/timestamps are applied.
    with tarfile.open(selected['archive']['path'], 'r:*') as t:
        for rel, e in selected['entries'].items():
            if e['kind'] != 'file':
                continue
            dest = root.joinpath(*rel)
            assert dest.parent.resolve() == dest.parent
            source = t.extractfile(e['member'])
            assert source is not None
            write_member(dest, source, e['member'])
    for rel, e in selected['entries'].items():
        dest = root.joinpath(*rel)
        if e['kind'] == 'hardlink':
            os.link(root.joinpath(*e['resolved']), dest, follow_symlinks=False)
        elif e['kind'] == 'symlink':
            os.symlink(e['member'].linkname, dest)
    for rel in sorted(selected['dirs'], key=lambda p: (-len(p), p)):
        directory = root.joinpath(*rel)
        os.chmod(directory, selected['entries'].get(rel, {'mode': 0o755})['mode'])
        fsync_dir(directory)


def inventory(selected):
    root = OUT / selected['role']
    rows = []
    links = {rel: 1 for rel, e in selected['entries'].items() if e['kind'] == 'file'}
    for e in selected['entries'].values():
        if e['kind'] == 'hardlink':
            links[e['resolved']] += 1
    expected = set(selected['entries']) | selected['dirs']
    observed = {()}
    pending = [root]
    while pending:
        parent = pending.pop()
        for child in sorted(parent.iterdir()):
            rel = child.relative_to(root).parts
            assert rel not in observed and rel in expected
            observed.add(rel)
            s = child.lstat()
            if stat.S_ISDIR(s.st_mode):
                pending.append(child)
    assert observed == expected
    for rel in sorted(expected):
        p = root.joinpath(*rel)
        before = snapshot(p)
        e = selected['entries'].get(rel, {'kind': 'dir', 'mode': 0o755})
        row = {'path': str(p), 'relativePath': '/'.join(rel), 'kind': e['kind'], 'mode': stat.S_IMODE(before[2]), 'dev': before[0], 'ino': before[1], 'nlink': before[3]}
        if e['kind'] in ('file', 'hardlink'):
            assert stat.S_ISREG(before[2]) and row['mode'] == e['mode']
            original = e['resolved'] if e['kind'] == 'hardlink' else rel
            assert before[3] == links[original]
            assert before[4] == (e['member'].size if e['kind'] == 'file' else selected['entries'][e['resolved']]['member'].size)
            row.update(bytes=before[4], sha256=sha_file(p))
            if e['kind'] == 'hardlink':
                target = root.joinpath(*e['resolved']).stat()
                assert (target.st_dev, target.st_ino) == before[:2]
                row['hardlinkTarget'] = str(root.joinpath(*e['resolved']))
        elif e['kind'] == 'dir':
            assert stat.S_ISDIR(before[2]) and row['mode'] == e['mode']
        else:
            assert stat.S_ISLNK(before[2]) and row['mode'] == e['mode']
            assert os.readlink(p) == e['member'].linkname
            assert p.resolve(strict=True) == root.joinpath(*e['resolved'])
            row.update(link=os.readlink(p), resolvedPath=str(root.joinpath(*e['resolved'])))
        assert snapshot(p) == before
        rows.append(row)
    return {'role': selected['role'], 'root': str(root), 'archive': selected['archive'], 'memberCount': len(selected['entries']), 'regularPayloadBytes': selected['payloadBytes'], 'rows': rows, 'files': sum(r['kind'] in ('file', 'hardlink') for r in rows), 'symlinks': sum(r['kind'] == 'symlink' for r in rows), 'hardlinks': sum(r['kind'] == 'hardlink' for r in rows), 'directoriesIncludingRoot': sum(r['kind'] == 'dir' for r in rows)}


def main():
    assert len(sys.argv) == 1 and ROOT.resolve() == ROOT and ROOT.is_dir()
    assert not os.path.lexists(OUT) and not os.path.lexists(RESULT)
    me = Path(__file__).resolve()
    checked({'path': str(me), 'sha256': sha_file(me), 'bytes': me.stat().st_size})
    plan = document(PLAN)
    downloads = document(DOWNLOADS)
    assert plan['state'] == 'CLONE_CANCEL_NATIVE_BUILD_RECOVERY_SOURCE_PLAN_V1'
    assert downloads['state'] == 'NATIVE_RECOVERY_ARCHIVE_HASHES_MATCH_V1'
    rows = downloads['archives']
    assert len(rows) == len(TOPS) and {r['role'] for r in rows} == set(TOPS)
    original = {r['role']: r for r in plan['archiveRecovery']}
    for r in rows:
        old = original[r['role']]
        assert {k: r['archive'][k] for k in ('sha256', 'bytes')} == {k: old['historicalPin'][k] for k in ('sha256', 'bytes')}
        assert r['url'] == old['sourceDerivedUrl']
        assert Path(r['archive']['path']) == ROOT / 'archives' / Path(old['historicalPin']['path']).name
    selected = [archive_plan(r) for r in rows]
    # Every archive's complete namespace has been checked before this first write.
    OUT.mkdir(mode=0o755)
    result = {'schemaVersion': 1, 'state': 'NATIVE_TOOL_RECOVERY_FAILED_V1', 'plan': PLAN, 'downloads': DOWNLOADS, 'outputRoot': str(OUT), 'tools': [], 'errors': [], 'secondaryErrors': [], 'toolCommandsExecuted': False, 'nativeBuildExecuted': False, 'oldRootOrInodeIdentityClaimed': False, 'RustOrCorrosionMaterialized': False}
    primary = None
    try:
        for item in selected:
            materialize(item)
            result['tools'].append(inventory(item))
        fsync_dir(OUT)
    except BaseException as error:
        primary = error
        result['errors'].append({'type': type(error).__name__, 'message': str(error)})
    try:
        for path, (ref, before) in INPUTS.items():
            assert snapshot(Path(path)) == before and sha_file(Path(path)) == ref['sha256'] and snapshot(Path(path)) == before
        result['inputsPreserved'] = True
    except BaseException as error:
        result['inputsPreserved'] = False
        if primary is None:
            primary = error
            result['errors'].append({'type': type(error).__name__, 'message': str(error)})
        else:
            result['secondaryErrors'].append({'type': type(error).__name__, 'message': str(error)})
    if primary is None:
        result['state'] = 'NATIVE_TOOL_RECOVERY_MATERIALIZED_AND_INVENTORIED_V1'
    try:
        f = RESULT.open('xb')
        publish_error = None
        try:
            f.write((json.dumps(result, indent=2) + '\n').encode())
            f.flush()
            os.fsync(f.fileno())
        except BaseException as error:
            publish_error = error
        try:
            f.close()
        except BaseException as error:
            if publish_error is None:
                publish_error = error
        if publish_error is not None:
            raise publish_error
        fsync_dir(ROOT)
        print(json.dumps({'state': result['state'], 'result': {'path': str(RESULT), 'sha256': sha_file(RESULT), 'bytes': RESULT.stat().st_size}, 'roles': len(result['tools']), 'inputsPreserved': result['inputsPreserved']}), flush=True)
    except BaseException:
        if primary is not None:
            raise primary
        raise
    if primary is not None:
        raise primary


if __name__ == '__main__':
    main()
