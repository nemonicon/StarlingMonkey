"""Retain closed recovery evidence, without tool binaries or native artifacts."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
RECOVERY = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-recovery-v1-first')
BUILD = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first')
RUST = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-rust-recovery-v1-first')
OUT = HERE / 'recovery-records'


def descriptor(path, raw):
    return dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))


def read(path):
    s = path.lstat()
    assert path.resolve() == path and stat.S_ISREG(s.st_mode) and s.st_nlink == 1
    assert s.st_size <= 16 * 1024**2
    raw = path.read_bytes()
    after = path.stat()
    assert (s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns) == (after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
    return raw


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode
    assert not OUT.exists() and not OUT.is_symlink()
    selections = []
    for path in sorted(RECOVERY.iterdir()):
        if path.is_file() and path.suffix in ('.json', '.py'):
            selections.append((path, Path('recovery') / path.name))
    for name in ['commands', 'header-acquisition-first']:
        for path in sorted((RECOVERY / name).rglob('*')):
            assert not path.is_symlink()
            if path.is_file():
                assert path.suffix in ('.json', '.log', '.body')
                selections.append((path, Path('recovery') / path.relative_to(RECOVERY)))
    # Every selected command has closed before retention; failed raw exits are retained.
    for command in (RECOVERY / 'commands').iterdir():
        assert command.is_dir() and (command / 'terminal.json').is_file() and (command / 'collection.json').is_file()
        terminal = json.loads(read(command / 'terminal.json'))
        assert terminal['allObservedOwnedGroupsGone'] and not terminal['timeout'] and not terminal['forcedCleanup']
        assert not terminal['errors'] and not terminal['signals'] and not terminal['interruptedSignals']
    for name in ['source-materialization.json']:
        selections.append((BUILD / name, Path('build-preparation') / name))
    for name in ['generator-checks', 'cargo-project']:
        for path in sorted((BUILD / name).rglob('*')):
            assert not path.is_symlink()
            if path.is_file():
                selections.append((path, Path('build-preparation') / path.relative_to(BUILD)))
    selections.append((BUILD / 'cargo-home/config.toml', Path('build-preparation/cargo-home/config.toml')))
    for name in ['rust-result.json', 'corrosion-result.json']:
        selections.append((RUST / name, Path('rust-recovery') / name))
    header = RECOVERY / 'headers-exact/include/mozilla/intl/unicode_bidi_ffi_generated.h'
    selections.append((header, Path('generated/unicode_bidi_ffi_generated.h')))
    selections.append((Path('/private/tmp/starling-node-compat/response-clone-cancel-followup-candidate-v1-node-first/result.json'), Path('references/node-followups.json')))
    assert len({str(p) for p, _ in selections}) == len(selections)
    assert len({str(p) for _, p in selections}) == len(selections)
    assert len(selections) < 2000
    # Pre-read the bounded evidence, then use exclusive output publication.
    prepared = [(source, rel, read(source)) for source, rel in selections]
    assert sum(len(raw) for _, _, raw in prepared) < 64 * 1024**2
    OUT.mkdir(mode=0o700)
    rows = []
    for source, rel, raw in prepared:
        compressed = len(raw) > 65536
        payload = gzip.compress(raw, mtime=0) if compressed else raw
        rel = Path(str(rel) + '.gz') if compressed else rel
        target = OUT / rel; target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as f:
            f.write(payload); f.flush(); os.fsync(f.fileno())
        assert read(target) == payload and read(source) == raw
        rows.append(dict(path=rel.as_posix(), sha256=hashlib.sha256(payload).hexdigest(), bytes=len(payload),
                         encoding='gzip' if compressed else 'identity', original=descriptor(source, raw)))
    index = dict(schemaVersion=1, state='CLONE_CANCEL_RECOVERY_CLOSED_RECORDS_V1', files=rows,
                 payloadFiles=len(rows), retainedBytes=sum(r['bytes'] for r in rows),
                 originalBytes=sum(r['original']['bytes'] for r in rows),
                 binaryToolPayloadsRetained=False, nativeEngineBuildIncluded=False,
                 fixedGuestRunIncluded=False, originalFailurePreserved=True)
    with (OUT / 'index.json').open('x') as f:
        json.dump(index, f, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps({k: v for k, v in index.items() if k != 'files'}))


if __name__ == '__main__':
    main()
