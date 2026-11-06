"""Read-only verification of actual seven-frontend SDK evidence. No compiler call."""
from pathlib import Path
import hashlib
import json
import os
import stat

BASE = Path('/Users/dan/dev/StarlingMonkey/tests/node-compat/foundation-scheduler')
FAMILY = BASE / 'combined-clock-diagnostics-sdk-syntax-v2'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4194304), b''):
            h.update(block)
    return h.hexdigest()


def checked(row):
    path = Path(row['path'])
    assert path.is_file() and path.stat().st_size == row['bytes']
    assert digest(path) == row['sha256'], str(path)
    return path


index = json.loads((FAMILY / 'index.json').read_text())
assert digest(FAMILY / 'index.json') == 'c669522fa5b0ed01dee8d7fbf58484c45f0414ebb89aa46fb0ff72b8e07cbba8'
names = {'index.json'}
for row in index['files']:
    assert row['path'] not in names
    names.add(row['path'])
    checked(dict(row, path=str(FAMILY / row['path'])))
assert names == {p.relative_to(FAMILY).as_posix() for p in FAMILY.rglob('*') if p.is_file()}
result = json.loads((FAMILY / 'results.json').read_text())
plan = json.loads(checked(result['actualPlan']).read_text())
before = json.loads(checked(result['originalProtectionBefore']).read_text())
final = json.loads(checked(result['originalProtectionFinal']).read_text())
for path, expected in before['files'].items():
    p = Path(path)
    s = p.stat()
    assert (stat.S_IMODE(s.st_mode), s.st_dev, s.st_ino, s.st_nlink, s.st_size) == (
        expected['mode'], expected['device'], expected['inode'], expected['nlink'], expected['bytes']), path
    assert digest(p) == expected['sha256'], path
assert final['allHashesModesInodesLinksUnchanged'] is True
assert final['sdkAliasesUnchanged'] == len(plan['sdkAliases']) == 31
for alias in plan['sdkAliases']:
    p = Path(alias['path'])
    assert p.is_symlink() and os.readlink(p) == alias['linkText']
    assert str(p.resolve(strict=True)) == alias['resolved']
assert len(result['units']) == len(plan['commands']) == 7
observations = []
for unit, command in zip(result['units'], plan['commands']):
    assert unit['id'] == command['id']
    terminal = json.loads(checked(unit['terminal']).read_text())
    started = json.loads((Path(unit['terminal']['path']).parent / 'started.json').read_text())
    assert started['argv'] == command['argv'] and terminal['pid'] == unit['pid']
    args = command['argv']
    assert '-fsyntax-only' in args and '-c' not in args and '-o' not in args
    assert '--target=wasm32-wasi' in args and '-DNODE_COMPAT_LIFECYCLE_DIAGNOSTICS=1' in args
    assert terminal['rawExitCode'] == 0
    assert terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
    assert terminal['timeout'] is terminal['forcedCleanup'] is False
    assert all(terminal[key] == [] for key in ('signals', 'errors', 'interruptedSignals', 'remainingObservedPids'))
    for key in ('stdout', 'stderr'):
        assert checked(terminal[key]).read_bytes() == b''
    observations.append(dict(id=unit['id'], partition=unit['partition'], pid=terminal['pid'], rawExitCode=0))
assert sum(row['partition'] == 'native' for row in observations) == 6
value = dict(schemaVersion=1, state='ROOT_READ_ONLY_DIAGNOSTIC_V2_SEVEN_SDK_FRONTENDS_CONFIRMED',
             sourceIndex=result['sourceIndex'], sourcePeerIndex=result['sourcePeerIndex'],
             sdkFamilyIndex=dict(path=str(FAMILY / 'index.json'), sha256=digest(FAMILY / 'index.json'),
                                 bytes=(FAMILY / 'index.json').stat().st_size),
             indexedPayloads=len(index['files']), currentOriginalsRehashed=len(before['files']),
             sdkAliasesRechecked=len(plan['sdkAliases']), actualObservedCommands=observations,
             sourceAndInputProtectionPassed=True, syntaxOnly=True, linkOrODRProved=False,
             engineExecuted=False, guestExecuted=False, runtimeAcceptanceClaim=False,
             readerPreparation='Initial inline reader treated sdkAliasesUnchanged as a boolean; '
                               'the real producer records a count. Corrected to exact31 before report publication; '
                               'no compiler or native operation was rerun.')
out = BASE / 'combined-clock-diagnostics-sdk-syntax-v2-root-observation.json'
with out.open('x') as stream:
    json.dump(value, stream, indent=2)
    stream.write('\n')
print(json.dumps(value), flush=True)
