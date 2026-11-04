"""Read only accepted public Release embedding engines; never execute binaries."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shlex
import stat
import subprocess

REPO = Path(__file__).resolve().parents[3]
BASE = Path('/tmp/starling-node-compat')
HERE = Path(__file__).resolve().parent


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def snapshot(path):
    s = path.lstat()
    assert stat.S_ISREG(s.st_mode) and not path.is_symlink()
    return dict(device=s.st_dev, inode=s.st_ino, nlink=s.st_nlink,
                logicalBytes=s.st_size, allocatedBytes=s.st_blocks * 512,
                flags=s.st_flags, mode=stat.S_IMODE(s.st_mode), uid=s.st_uid,
                gid=s.st_gid, mtimeNs=s.st_mtime_ns)


accepted = {}
milestone_witnesses = []
for path in sorted((REPO / 'tests/node-compat/milestones').glob('*/results.json')):
    value = json.loads(path.read_bytes())
    milestone_witnesses.append(dict(path=str(path), sha256=digest(path)))

    def descend(item, key):
        if isinstance(item, str) and re.fullmatch('[0-9a-f]{64}', item):
            accepted.setdefault(item, []).append(dict(path=str(path), key=key))
        elif isinstance(item, dict):
            if isinstance(item.get('sha256'), str):
                descend(item['sha256'], key + '.sha256')
            else:
                for name, child in item.items():
                    descend(child, key + '.' + name)

    for key, item in value.items():
        if 'engine' in key.lower():
            descend(item, key)

roots = [BASE / f'foundations-v{i}/native-freeze' for i in range(1, 12)]
roots.append(BASE / 'allocation-r2-native-freeze')
metadata = []
candidates = {}
excluded_metadata = []


def add(path, kind, meta, expected):
    if not str(path).startswith(str(BASE) + '/') or not path.exists():
        return
    if path.is_symlink() or not path.is_file():
        return
    key = str(path.resolve())
    row = candidates.setdefault(key, dict(path=str(path), derivations=[]))
    row['derivations'].append(dict(kind=kind, sidecar=str(meta), expectedSha256=expected))


for root in roots:
    for path in sorted(root.glob('*.wasm.build.json')):
        if re.search('(gc|debug|oom)', path.name, re.I):
            continue
        item = json.loads(path.read_bytes())
        sha = item.get('engineSha256')
        if sha not in accepted:
            excluded_metadata.append(dict(path=str(path), reason='not a selected top-level accepted milestone engine'))
            continue
        options = item.get('observedCMakeOptions', item.get('requestedCMakeOptions', {}))
        if item.get('gcStress') is not False or item.get('oomTesting') is not False or options.get('CMAKE_BUILD_TYPE') != 'Release':
            excluded_metadata.append(dict(path=str(path), reason='not explicit ordinary Release with GC/OOM off'))
            continue
        metadata.append(dict(path=str(path), sha256=digest(path), engineSha256=sha,
                             builtAtUtc=item.get('builtAtUtc'), milestoneReferences=accepted[sha]))
        add(Path(str(path)[:-len('.build.json')]), 'frozen accepted engine', path, sha)
        add(Path(item['enginePath']), 'artifact path in terminal frozen sidecar', path, sha)
        if item.get('compileCommandsPath'):
            add(Path(item['compileCommandsPath']).parent / 'starling-raw.wasm/starling-raw.wasm',
                'final target in recorded build directory', path, sha)
        for command in item.get('actualEmbeddingCompileCommands', []):
            argv = shlex.split(command)
            if '-c' in argv:
                source = Path(argv[argv.index('-c') + 1]).parent.parent
                add(source / 'lib/starlingmonkey_embedding.wasm', 'project output derived from actual embedding compilation', path, sha)
        if root.name == 'allocation-r2-native-freeze':
            # The archived recipe fixes componentize-abi-fixed + -bigint-v1.
            add(BASE / 'improved-build/componentize-abi-fixed-bigint-v1/lib/starlingmonkey_embedding.wasm',
                'allocation-r2 archived recipe source_dir and copy source', path, sha)

allowed = {row['engineSha256'] for row in metadata}
rows, rejected = [], []
for row in candidates.values():
    path = Path(row['path'])
    before = snapshot(path)
    sha = digest(path)
    assert snapshot(path) == before, 'File changed during read: ' + str(path)
    row.update(before, sha256=sha, compressed=bool(before['flags'] & stat.UF_COMPRESSED))
    if sha not in allowed:
        row['reason'] = 'mutable project output no longer matches an accepted ordinary Release hash; excluded'
        rejected.append(row)
        continue
    row['matchingAcceptedMilestones'] = accepted[sha]
    names = subprocess.run(['/usr/bin/xattr', str(path)], check=True, capture_output=True, text=True).stdout.splitlines()
    row['xattrs'] = {}
    for name in names:
        raw = subprocess.run(['/usr/bin/xattr', '-px', name, str(path)], check=True, capture_output=True, text=True).stdout
        row['xattrs'][name] = hashlib.sha256(bytes.fromhex(raw)).hexdigest()
    acl = subprocess.run(['/bin/ls', '-lde', str(path)], check=True, capture_output=True, text=True)
    row['aclLines'] = acl.stdout.splitlines()[1:]
    row['requiredMetadataExcludes'] = ['read-atime', 'ctime', 'birthtime']
    assert snapshot(path) == before, 'File changed during metadata reading: ' + str(path)
    rows.append(row)

unique = {(row['device'], row['inode']): row for row in rows}
uncompressed = [row for row in unique.values() if not row['compressed']]
result = dict(schemaVersion=1, state='READ_ONLY_ACCEPTED_PUBLIC_ORDINARY_RELEASE_ENGINE_INVENTORY',
              capturedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              acceptedMilestoneWitnesses=milestone_witnesses, terminalSidecars=metadata,
              initialCandidatePaths=len(candidates), eligiblePaths=len(rows), uniqueInodes=len(unique),
              uncompressedUniqueInodes=len(uncompressed),
              logicalBytes=sum(row['logicalBytes'] for row in unique.values()),
              summedAllocatedBytes=sum(row['allocatedBytes'] for row in unique.values()),
              uncompressedSummedAllocatedBytes=sum(row['allocatedBytes'] for row in uncompressed),
              rows=rows, excludedMutableOutputs=rejected, excludedPublicMetadata=excluded_metadata,
              knownCowProvenance='v11 duplicate raw engine restoration used cp -c against frozen engines; exact shared extents are unmeasured. Other APFS sharing is unknown.',
              summedAllocationIsUniqueExtentOrRecoveryEstimate=False,
              compressionAttempted=False, binariesExecuted=False, nativeBuildOrGuestExecuted=False,
              sdkDebugOomPrivateFaultOrProbeContentsInspected=False,
              conclusion='No recovery guarantee. Even eliminating every eligible reported block gives only an allocation ceiling; compression needs nonzero output and can interact with shared extents.')
output = HERE / 'results.json'
with output.open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps({key: result[key] for key in ['initialCandidatePaths', 'eligiblePaths', 'uniqueInodes', 'uncompressedUniqueInodes', 'logicalBytes', 'summedAllocatedBytes']}))
