"""Read-only exact outputs of five completed accepted public Release projects."""
from pathlib import Path
import datetime
import hashlib
import json
import shlex
import stat
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE = Path('/tmp/starling-node-compat')
CONFIGS = [
    ('v11-gc', 'foundations-v11/native-freeze/gc-foundations'),
    ('v11-runtime', 'foundations-v11/native-freeze/runtime-foundations'),
    ('v5-off', 'foundations-v5/native-freeze/off-path-events'),
    ('v5-runtime', 'foundations-v5/native-freeze/runtime-path-events'),
    ('v3-off', 'foundations-v3/native-freeze/off-path'),
]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def capture(path):
    s = path.lstat()
    assert stat.S_ISREG(s.st_mode) and not path.is_symlink()
    return dict(device=s.st_dev, inode=s.st_ino, nlink=s.st_nlink,
                logicalBytes=s.st_size, allocatedBytes=s.st_blocks * 512,
                mode=stat.S_IMODE(s.st_mode), uid=s.st_uid, gid=s.st_gid,
                mtimeNs=s.st_mtime_ns, flags=s.st_flags)


witnesses = HERE / 'ninja-metadata'
witnesses.mkdir()
rows = {}
configurations = []
for label, prefix in CONFIGS:
    sidecar = Path(str(BASE / prefix) + '.engine.wasm.build.json')
    data = json.loads(sidecar.read_bytes())
    options = data['observedCMakeOptions']
    assert options['CMAKE_BUILD_TYPE'] == 'Release' and data['oomTesting'] is False
    assert data['gcStress'] is (label == 'v11-gc')
    db, cache = Path(data['compileCommandsPath']), Path(data['cmakeCachePath'])
    assert digest(db) == data['compileCommandsSha256']
    assert digest(cache) == data['cmakeCacheSha256']
    build = db.parent.resolve()
    assert str(build).startswith(str(BASE.resolve()) + '/improved-build/engine-')
    assert not any(word in build.name.lower() for word in ('debug', 'oom', 'diagnostic', 'private', 'probe', 'candidate'))
    engine = Path(str(BASE / prefix) + '.engine.wasm')
    assert digest(engine) == data['engineSha256']
    frozen_db = Path(str(BASE / prefix) + '-compile_commands.json')
    frozen_cache = Path(str(BASE / prefix) + '-CMakeCache.txt')
    if frozen_db.exists() or frozen_cache.exists():
        assert frozen_db.is_file() and frozen_cache.is_file()
        assert digest(frozen_db) == digest(db) and digest(frozen_cache) == digest(cache)
    # Older accepted freezes retain the sidecar's digests without separate copies.
    for source, name in [(db, 'compile_commands.json'), (cache, 'CMakeCache.txt')]:
        with (witnesses / (label + '.' + name)).open('xb') as stream:
            stream.write(source.read_bytes())
    terminal = datetime.datetime.fromisoformat(data['builtAtUtc']).timestamp()
    candidates = {}

    def add(path, derivation):
        resolved = path.resolve()
        if not resolved.is_relative_to(build) or not resolved.exists():
            return
        assert resolved.suffix in ('.obj', '.a') and resolved.is_file() and not path.is_symlink()
        candidates.setdefault(str(resolved), []).append(derivation)

    for index, command in enumerate(json.loads(db.read_bytes())):
        args = shlex.split(command['command'])
        assert args.count('-o') == 1 and '-c' in args
        add(Path(command['directory']) / args[args.index('-o') + 1],
            dict(kind='exact compile-database -o operand', databaseRow=index))
    for command in data.get('actualEmbeddingCompileCommands', []):
        args = shlex.split(command)
        assert args.count('-o') == 1
        add(build / args[args.index('-o') + 1], dict(kind='recorded actual embedding compile -o operand'))

    commands = {}
    for name, suffix in [('commands', ['-t', 'commands', 'starlingmonkey_embedding']),
                         ('targets', ['-t', 'targets', 'all'])]:
        argv = ['ninja', '-C', str(db.parent), *suffix]
        output = subprocess.run(argv, check=True, capture_output=True)
        path = witnesses / (label + '.' + name + '.txt')
        with path.open('xb') as stream:
            stream.write(output.stdout)
        commands[name] = dict(argv=argv, path=str(path), sha256=digest(path), bytes=path.stat().st_size,
                              nativeCommandsExecuted=False)
    for line in Path(commands['targets']['path']).read_text().splitlines():
        target, sep, rule = line.rpartition(': ')
        if sep and target.endswith('.a') and rule != 'phony':
            add(build / target, dict(kind='exact Ninja-declared archive target', target=target, rule=rule))

    for name, derivations in candidates.items():
        path = Path(name)
        before = capture(path)
        assert before['mtimeNs'] <= int((terminal + 2) * 1e9), 'Output newer than terminal receipt: ' + name
        sha = digest(path)
        names = subprocess.run(['/usr/bin/xattr', name], check=True, capture_output=True, text=True).stdout.splitlines()
        xattrs = {}
        for attr in names:
            raw = subprocess.run(['/usr/bin/xattr', '-px', attr, name], check=True, capture_output=True, text=True).stdout
            xattrs[attr] = hashlib.sha256(bytes.fromhex(raw)).hexdigest()
        acl = subprocess.run(['/bin/ls', '-lde', name], check=True, capture_output=True, text=True).stdout.splitlines()[1:]
        assert capture(path) == before, 'Output changed while reading: ' + name
        row = rows.setdefault(name, dict(path=name, **before, sha256=sha,
                                         compressed=bool(before['flags'] & stat.UF_COMPRESSED),
                                         xattrs=xattrs, aclLines=acl, configurations=[]))
        row['configurations'].append(dict(label=label, derivations=derivations))
    assert digest(db) == data['compileCommandsSha256'] and digest(cache) == data['cmakeCacheSha256']
    configurations.append(dict(label=label, sidecar=str(sidecar), sidecarSha256=digest(sidecar),
                               engineSha256=data['engineSha256'], buildDirectory=str(build),
                               compileDatabase=str(db), compileDatabaseSha256=digest(db),
                               cache=str(cache), cacheSha256=digest(cache),
                               earlierFrozenConfigurationCopiesAvailable=frozen_db.exists(),
                               builtAtUtc=data['builtAtUtc'], eligibleOutputs=len(candidates), ninjaMetadata=commands))

unique = {(row['device'], row['inode']): row for row in rows.values()}
engine_inventory = REPO / 'tests/node-compat/storage-candidate-audit-public-engines-v1/results.json'
assert digest(engine_inventory) == '1dc393a9ba5658f37b69857b6d324251129e2e871f9172856e501c2578d76206'
engines = json.loads(engine_inventory.read_bytes())
result = dict(schemaVersion=1, state='READ_ONLY_EXACT_PUBLIC_RELEASE_OBJECT_ARCHIVE_OUTPUT_INVENTORY',
              configurations=configurations, rows=list(rows.values()), eligiblePaths=len(rows), uniqueInodes=len(unique),
              logicalBytes=sum(row['logicalBytes'] for row in unique.values()),
              summedAllocatedBytes=sum(row['allocatedBytes'] for row in unique.values()),
              compressedUniqueInodes=sum(row['compressed'] for row in unique.values()),
              relatedEngineInventory=dict(path=str(engine_inventory), sha256=digest(engine_inventory),
                                          summedAllocatedBytes=engines['summedAllocatedBytes']),
              combinedSummedAllocationCeilingBytes=engines['summedAllocatedBytes'] + sum(row['allocatedBytes'] for row in unique.values()),
              excludes=['SDK/tools', 'DEBUG/OOM/private/fault/probe/candidate trees', 'source/configuration files',
                        'undeclared Cargo/cache files', 'engines already counted separately'],
              historicalIndividualObjectDigestProof=False,
              provenanceLimit='Present hashes are not historical per-object hashes. Exact terminal sidecars, unchanged cache/database, declared outputs and pre-terminal mtimes constrain provenance; no source recompilation or object execution occurs.',
              sharedExtentsMeasured=False, recoveryPromised=False, compressionAttempted=False,
              nativeBuildLinkCompilerOrGuestExecuted=False,
              requiredMetadataExcludes=['read-atime', 'ctime', 'birthtime'])
with (HERE / 'results.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps({key: result[key] for key in ['eligiblePaths', 'uniqueInodes', 'logicalBytes', 'summedAllocatedBytes', 'combinedSummedAllocationCeilingBytes']}))
