"""Read only literal .a operands of the exact five admitted final Clang stages."""
from pathlib import Path
import hashlib
import json
import shlex
import stat
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PARENT = REPO / 'tests/node-compat/storage-candidate-audit-public-native-inputs-v1/results.json'
PARENT_SHA = 'a722f083adcca272a04a4c27718e2151a66117ad24baba1ff3421074cce4867d'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(data)
    return h.hexdigest()


def metadata(path):
    s = path.lstat()
    assert stat.S_ISREG(s.st_mode) and not path.is_symlink()
    return dict(device=s.st_dev, inode=s.st_ino, nlink=s.st_nlink,
                logicalBytes=s.st_size, allocatedBytes=s.st_blocks * 512,
                mode=stat.S_IMODE(s.st_mode), uid=s.st_uid, gid=s.st_gid,
                mtimeNs=s.st_mtime_ns, flags=s.st_flags)


assert digest(PARENT) == PARENT_SHA
parent = json.loads(PARENT.read_bytes())
previous = {str(Path(row['path']).resolve()): row for row in parent['rows']}
assert len(previous) == 472 and len(parent['configurations']) == 5
witnesses = HERE / 'ninja-metadata'
witnesses.mkdir()
configurations, archives, outside = [], {}, []
for config in parent['configurations']:
    label = config['label']
    sidecar = Path(config['sidecar'])
    assert digest(sidecar) == config['sidecarSha256']
    receipt = json.loads(sidecar.read_bytes())
    db, cache = Path(config['compileDatabase']), Path(config['cache'])
    assert digest(db) == config['compileDatabaseSha256'] == receipt['compileCommandsSha256']
    assert digest(cache) == config['cacheSha256'] == receipt['cmakeCacheSha256']
    build = db.parent
    argv = ['ninja', '-C', str(build), '-t', 'commands', 'starling-raw.wasm/starling-raw.wasm']
    raw = subprocess.run(argv, check=True, capture_output=True).stdout
    witness = witnesses / (label + '.final-target.commands.txt')
    with witness.open('xb') as stream:
        stream.write(raw)
    matches = []
    for line in raw.decode().splitlines():
        if 'starling-raw.wasm/starling-raw.wasm' not in line:
            continue
        lexer = shlex.shlex(line, posix=True, punctuation_chars=';&|()')
        lexer.whitespace_split, lexer.commenters = True, ''
        stages = [[]]
        for token in lexer:
            if token == '&&':
                stages.append([])
            else:
                assert token not in (';', '&', '|', '||', '(', ')')
                stages[-1].append(token)
        for stage in stages:
            if stage and stage[0] == str(build / 'cxx-wrapper') and stage.count('-o') == 1:
                if stage[stage.index('-o') + 1] == 'starling-raw.wasm/starling-raw.wasm':
                    matches.append((line, stages, stage))
    assert len(matches) == 1
    line, stages, clang = matches[0]
    assert len(stages) == 4 and stages[0] == [':'] and stages[1] == clang
    assert stages[2] == ['cd', str(build / 'starling-raw.wasm')]
    assert Path(stages[3][0]).name == 'wasm-opt' and stages[3][1:] == ['--strip-debug', '-O3', '-o', 'starling-raw.wasm', 'starling-raw.wasm']
    assert all(flag in clang for flag in ['-O3', '-DNDEBUG', '-flto=thin'])
    assert all(flag not in clang for flag in ['-c', '-###', '-fsyntax-only', '-DDEBUG'])
    operands = [arg for arg in clang[1:] if not arg.startswith('-') and arg.endswith('.a')]
    selected = []
    for operand in operands:
        path = (build / operand).resolve()
        if not path.is_relative_to(build.resolve()):
            assert path.name == 'libspidermonkey.a', 'Unexpected outside-root archive operand'
            outside.append(dict(label=label, operand=operand, path=str(path),
                                reason='SDK library outside the public build root; no content/metadata inspection'))
            continue
        assert not any(word in str(path.relative_to(build.resolve())).lower() for word in ('debug', 'oom', 'probe', 'candidate'))
        selected.append(str(path))
        archives.setdefault(str(path), dict(path=str(path), operands=[]))['operands'].append(dict(label=label, operand=operand))
    configurations.append(dict(label=label, sidecar=str(sidecar), sidecarSha256=digest(sidecar),
                               cacheSha256=digest(cache), compileDatabaseSha256=digest(db),
                               witnessPath=str(witness), witnessSha256=digest(witness), witnessBytes=len(raw),
                               collectionCommand=argv, selectedLine=line, selectedClangArguments=clang,
                               explicitArchiveOperands=len(operands), insideOperandOccurrences=len(selected),
                               uniqueInsideArchives=len(set(selected)), commandTextExecuted=False))
    assert digest(db) == config['compileDatabaseSha256'] and digest(cache) == config['cacheSha256']

for name, row in archives.items():
    path = Path(name)
    before = metadata(path)
    row.update(before, sha256=digest(path), compressed=bool(before['flags'] & stat.UF_COMPRESSED))
    row['alreadyIn472'] = name in previous
    if name in previous:
        old = previous[name]
        assert row['sha256'] == old['sha256']
        assert all(before[key] == old[key] for key in before)
    names = subprocess.run(['/usr/bin/xattr', name], check=True, capture_output=True, text=True).stdout.splitlines()
    row['xattrs'] = {}
    for attr in names:
        value = subprocess.run(['/usr/bin/xattr', '-px', attr, name], check=True, capture_output=True, text=True).stdout
        row['xattrs'][attr] = hashlib.sha256(bytes.fromhex(value)).hexdigest()
    row['aclLines'] = subprocess.run(['/bin/ls', '-lde', name], check=True, capture_output=True, text=True).stdout.splitlines()[1:]
    assert metadata(path) == before
    if name in previous:
        assert row['xattrs'] == old['xattrs'] and row['aclLines'] == old['aclLines']
new = [row for row in archives.values() if not row['alreadyIn472']]
result = dict(schemaVersion=1, state='READ_ONLY_FINAL_CLANG_ARCHIVE_OPERANDS_CLOSED',
              parentInventory=dict(path=str(PARENT), sha256=PARENT_SHA), configurations=configurations,
              archives=list(archives.values()), outsideRootExcludedOperands=outside,
              uniqueInsideArchives=len(archives), newPathsNotInPrevious472=len(new),
              additionalLogicalBytes=sum(row['logicalBytes'] for row in new),
              additionalSummedAllocatedBytes=sum(row['allocatedBytes'] for row in new),
              combinedEngineAndNativeInputAllocationCeilingBytes=parent['combinedSummedAllocationCeilingBytes'] + sum(row['allocatedBytes'] for row in new),
              scopeExpansion=False, compilerLinkBuildOrGuestExecuted=False, compressionAttempted=False,
              sdkContentsInspected=False, sharedExtentsMeasured=False, recoveryPromised=False,
              conclusion='All public build-root literal .a link inputs are already counted. No new capacity candidate and no broader crawl.')
with (HERE / 'results.json').open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps({key:result[key] for key in ['uniqueInsideArchives','newPathsNotInPrevious472','additionalSummedAllocatedBytes','combinedEngineAndNativeInputAllocationCeilingBytes']}))
