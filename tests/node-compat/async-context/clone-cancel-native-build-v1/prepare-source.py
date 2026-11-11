"""Materialize the actual 825-input recipe with exactly one C++ replacement.

This prepares fresh inputs only. It does not admit an engine or execute a build.
The full previous metadata is ancestry, never rewritten to describe this run.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tomllib

REPO = Path(__file__).resolve().parents[4]
WORK = Path('/private/tmp/starling-node-compat/next-clone-cancel-native-build-v1-first')
OLD = Path('/private/tmp/starling-node-compat/next-native-export-diagnostic-build-v1-first')
META = dict(path=str(OLD / 'metadata.json'), sha256='500e76acf6d76c1552ad3208a6b2498f3b1439bbb14a5ac043f8c35d0405a48e', bytes=4859956)
REL = 'builtins/web/fetch/request-response.cpp'
AFTER = dict(path=str(REPO / 'tests/node-compat/async-context/response-clone-cancel-native-candidate-v1/after' / REL), sha256='0431184d4562972c98538494caf46d2b11cdf0280f51d0e7143cd8534526442e', bytes=130742)
BEFORE_SHA = '1fe296b8472f14e50556910227b184552e0a0ac424f97a0f170c4b91cfd35fa6'
PROTECTED = {}


def snapshot(p):
    s = p.lstat()
    return tuple(getattr(s, k) for k in ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'))


def descriptor(p):
    p = Path(p)
    before = snapshot(p)
    assert p.is_absolute() and p.resolve(strict=True) == p and stat.S_ISREG(before[2])
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    assert snapshot(p) == before
    return dict(path=str(p), sha256=h.hexdigest(), bytes=before[4])


def checked(r):
    p = Path(r['path'])
    assert descriptor(p) == r, str(p)
    before = snapshot(p)
    assert before[3] == 1
    PROTECTED[str(p)] = (r, before)
    return p


def read(r):
    return json.loads(checked(r).read_bytes())


def safe(relative):
    p = Path(relative)
    assert not p.is_absolute() and '..' not in p.parts and p.parts and p.as_posix() == relative
    return p


def write(p, b, mode=0o600):
    p.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    assert p.parent.resolve() == p.parent
    with p.open('xb') as f:
        f.write(b); f.flush(); os.fchmod(f.fileno(), mode); os.fsync(f.fileno())
    return descriptor(p)


def save(p, value):
    return write(p, (json.dumps(value, indent=2) + '\n').encode())


def main():
    assert __debug__ and sys.flags.isolated and sys.dont_write_bytecode and len(sys.argv) == 1
    assert not os.path.lexists(WORK) and WORK.parent.resolve() == WORK.parent
    assert os.statvfs(WORK.parent).f_bavail * os.statvfs(WORK.parent).f_frsize >= 3 * 1024**3
    m = read(META)
    assert len(m) == 52 and m['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1'
    assert m['engine']['sha256'] == '237c4e5ace16d6ad20f00e2da08501e6948e29056a5d2aad2a25e55bc894453a'
    checked(m['engine'])
    previous = read(m['sourceComposition'])
    assert previous['files'] == m['nativePolicyInputManifest'] and previous['nativeSourceFiles'] == 435
    native = m['nativePolicyInputManifest']; support = m['buildSupportInputManifest']; embedding = m['embeddingInputManifest']
    assert (len(native), len(support), len(embedding)) == (435, 387, 3)
    assert (m['nativePolicyInputCount'], m['buildSupportInputCount'], m['embeddingInputCount']) == (435, 387, 3)
    assert len({r['path'] for r in native}) == 435 and len({r['relativePath'] for r in support}) == 387
    assert not {r['path'] for r in native} & {r['relativePath'] for r in support}
    assert {r['relativePath'] for r in embedding} == {'CMakeLists.txt', 'embedding/embedding.cpp', 'embedding/embedding.h'}
    after = checked(AFTER)
    rows = []
    for r in native:
        rel = safe(r['path'])
        old = dict(path=str(Path(m['sourceRoot']) / rel), sha256=r['sha256'], bytes=r['bytes'])
        compiled = dict(path=str(Path(m['compiledSourceRoot']) / rel), sha256=r['sha256'], bytes=r['bytes'])
        checked(old); checked(compiled)
        assert compiled in m['compiledAfterInputs']
        if r['path'] == REL:
            assert r['sha256'] == BEFORE_SHA and r['bytes'] == 126132
        rows.append(dict(role='native', relativePath=r['path'], source=AFTER if r['path'] == REL else old,
                         predecessor=old, destination=str(WORK / 'native-source' / rel), mode=0o600))
    assert sum(r['source'] != r['predecessor'] for r in rows) == 1
    for role, items, base in [('support', support, 'native-source'), ('embedding', embedding, 'componentize-source')]:
        for r in items:
            rel = safe(r['relativePath']); checked(r['source'])
            rows.append(dict(role=role, relativePath=r['relativePath'], source=r['source'],
                             destination=str(WORK / base / rel), mode=r['mode']))
    assert len(rows) == len({r['destination'] for r in rows}) == 825
    authority = read(m['rootAuthority'])
    generators = read(authority['installedGeneratorResult'])
    assert generators['passed'] and len(generators['commands']) == 10
    node = checked(authority['generatorNode'])
    commands = []
    for i, cmd in enumerate(generators['commands']):
        argv = cmd['argv']
        assert argv[0] == str(node) and argv[-1] == '--check' and cmd['cwd'] == m['sourceRoot']
        assert cmd['rawExitCode'] == 0 and cmd['stderr']['bytes'] == 0
        # Relocate only complete path arguments, never arbitrary source strings.
        updated = []
        for arg in argv:
            if arg == m['sourceRoot']:
                arg = str(WORK / 'native-source')
            elif arg.startswith(m['sourceRoot'] + '/'):
                arg = str(WORK / 'native-source' / safe(arg[len(m['sourceRoot']) + 1:]))
            updated.append(arg)
        assert any(r['destination'] == updated[1] for r in rows)
        commands.append(dict(label=f'generator-{i:02d}', argv=updated, cwd=str(WORK / 'native-source'), seconds=120))
    manifest_ref = m['actualRustConfiguration']['manifest']
    original_manifest = checked(manifest_ref).read_text()
    staticlib_refs = [r for r in m['linkAndRustInputs']
                      if r['path'] == str(Path(manifest_ref['path']).parent / 'rust-staticlib.rs')]
    assert len(staticlib_refs) == 1
    original_staticlib = checked(staticlib_refs[0]).read_bytes()
    lock = checked(m['actualAggregateLock']).read_bytes()
    config = checked(m['offlineCargoConfig']).read_bytes()
    manifest = original_manifest
    original = tomllib.loads(original_manifest)
    expected = tomllib.loads(original_manifest)
    for name, rel in {'rust-encoding': 'rust-encoding', 'rust-hooks': 'rust-hooks', 'rust-url': 'rust-url', 'multipart': 'rust-multipart'}.items():
        old_path = original['dependencies'][name]['path']
        new_path = str(WORK / 'native-source/crates' / rel)
        assert manifest.count('"' + old_path + '"') == 1
        manifest = manifest.replace('"' + old_path + '"', '"' + new_path + '"')
        expected['dependencies'][name]['path'] = new_path
    assert tomllib.loads(manifest) == expected
    # All input checks precede publication. No historical output is modified.
    WORK.mkdir(mode=0o700)
    for name in ['commands', 'componentize-source/lib', 'cargo-home', 'tmp', 'git-template', 'git-hooks']:
        (WORK / name).mkdir(parents=True, mode=0o700, exist_ok=True)
    copies = []
    for r in rows:
        src = checked(r['source']); dest = Path(r['destination'])
        target = write(dest, src.read_bytes(), r['mode'])
        assert target['sha256'] == r['source']['sha256'] and target['bytes'] == r['source']['bytes']
        assert snapshot(src)[:2] != snapshot(dest)[:2] and snapshot(dest)[3] == 1
        copies.append({**r, 'target': target})
    cargo = dict(manifest=write(WORK / 'cargo-project/Cargo.toml', manifest.encode()),
                 lock=write(WORK / 'cargo-project/Cargo.lock', lock),
                 staticlib=write(WORK / 'cargo-project/rust-staticlib.rs', original_staticlib),
                 config=write(WORK / 'cargo-home/config.toml', config),
                 predecessorActualManifest=manifest_ref, predecessorActualStaticlib=staticlib_refs[0],
                 onlyFourBasePathsRelocated=True, lockBytesUnchanged=True, metadataExecuted=False)
    for p, (r, before) in PROTECTED.items():
        assert snapshot(Path(p)) == before and descriptor(p) == r and snapshot(Path(p)) == before
    result = dict(schemaVersion=1, state='CLONE_CANCEL_825_INPUTS_MATERIALIZED_V1',
                  recipe=descriptor(__file__), predecessorWholeMetadata=META,
                  predecessorComposition=m['sourceComposition'], replacement=AFTER,
                  workRoot=str(WORK), copies=copies, nativeCount=435, supportCount=387,
                  embeddingCount=3, changedNativePaths=[REL], generatorCommands=commands,
                  generatorNode=authority['generatorNode'], cargo=cargo,
                  selectedModuleManifests=m['selectedModuleManifests'],
                  protectedInputs=[r for r, _ in PROTECTED.values()], inputsUnchanged=True,
                  previousMetadataProjected=False, nativeBuildExecuted=False, guestExecuted=False)
    result_row = save(WORK / 'source-materialization.json', result)
    print(json.dumps(dict(result=result_row, copied=len(copies), nativeBuildExecuted=False)), flush=True)


if __name__ == '__main__':
    main()
