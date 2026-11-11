"""Retain closed small records for the first new-engine Wasmtime regression."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
TMP = Path('/private/tmp/starling-node-compat')
COMMANDS = TMP / 'next-clone-cancel-native-recovery-v1-first/commands'
COMPONENT = TMP / 'next-clone-cancel-component-v1-first'
RUNTIME = TMP / 'next-lifecycle-runtime-v3-clone-cancel-first'


def main():
    if not __debug__ or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise RuntimeError('Use Python -I -B without optimization')
    assert len(sys.argv) == 1
    out = HERE / 'raw-records'
    assert not out.exists()
    selected = {}
    def add(name, path):
        assert name not in selected and path.resolve(strict=True) == path and path.is_file()
        selected[name] = path
    commands = ('admit-native-v2', 'prepare-clone-component', 'clone-comparator-syntax',
        'clone-componentize', 'clone-validate-component', 'clone-component-wit',
        'review-clone-component', 'clone-wasmtime-runtime', 'clone-compare-runtime')
    for name in commands:
        folder = COMMANDS / name
        terminal = json.loads((folder / 'terminal.json').read_bytes())
        assert terminal['rawExitCode'] == 0 and terminal['allObservedOwnedGroupsGone'] is True
        assert terminal['parentOwnedGroupGone'] is True and terminal['timeout'] is terminal['forcedCleanup'] is False
        assert all(terminal[k] == [] for k in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'))
        for p in sorted(folder.iterdir()):
            if p.is_file():
                add('commands/' + name + '/' + p.name, p)
    for name in ('construction-request.json', 'construction-review.json', 'runtime-request.json',
                 'differential-result.json', 'source-api-peer.json'):
        add('review/' + name, HERE / name)
    for name in ('result.json', 'options.json', 'final-preopens.json', 'returned-imports.json', 'returned-own-shape.json'):
        add('component/' + name, COMPONENT / name)
    for p in sorted(RUNTIME.iterdir()):
        assert p.is_file()
        add('runtime/' + p.name, p)
    for name, folder in (('context', 'web-stream-context-candidate-v2-node-first'),
                         ('clone', 'response-clone-cancel-candidate-v1-node-first'),
                         ('followups', 'response-clone-cancel-followup-candidate-v1-node-first')):
        add('node/' + name + '.json', TMP / folder / 'result.json')
    for name in ('compare-results.mjs', 'review-construction.py', 'retain.py'):
        add('source/' + name, HERE / name)
    for family, names in (
        ('web-stream-context-component-v1', ('compare.mjs',)),
        ('web-stream-context-component-v2', ('guest-entry.mjs', 'index.json')),
        ('lifecycle-wasmtime-collector-v3', ('run-wasmtime.py', 'index.json')),
        ('clone-cancel-component-construction-v1', ('prepare.py', 'componentize.mjs')),
        ('clone-cancel-native-build-v1', ('review-build.py', 'actual-engine-admission.json'))):
        for name in names:
            add('source/' + family + '/' + name, BASE / family / name)
    add('build/metadata.json', TMP / 'next-clone-cancel-native-build-v1-first/closed-collection-v2/metadata.json')
    add('build/collection-result.json', TMP / 'next-clone-cancel-native-build-v1-first/closed-collection-v2/result.json')
    runtime = json.loads((RUNTIME / 'result.json').read_bytes())
    differential = json.loads((HERE / 'differential-result.json').read_bytes())
    assert runtime['collectionClean'] is differential['passed'] is True
    out.mkdir(mode=0o700)
    rows = []
    for name, p in sorted(selected.items()):
        before = p.stat()
        raw = p.read_bytes()
        after = p.stat()
        assert all(getattr(before, k) == getattr(after, k) for k in
                   ('st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_size', 'st_mtime_ns', 'st_ctime_ns'))
        assert len(raw) == before.st_size and len(raw) <= 16 * 1024**2
        compressed = len(raw) > 100000
        stored = gzip.compress(raw, mtime=0) if compressed else raw
        relative = name + '.gz' if compressed else name
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as f:
            f.write(stored)
        rows.append(dict(path=relative, sha256=hashlib.sha256(stored).hexdigest(), bytes=len(stored),
            encoding='gzip' if compressed else 'identity', original=dict(path=str(p),
            sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw))))
    result = dict(schemaVersion=1, state='CLONE_CANCEL_WASMTIME_PASS_RECORDS_RETAINED_V1', files=rows,
        payloadFiles=len(rows), retainedBytes=sum(r['bytes'] for r in rows),
        originalBytes=sum(r['original']['bytes'] for r in rows),
        component=runtime['component'], originalRuntimeOwnerPid=76401, originalComparisonOwnerPid=76491,
        runtimeRawExitCode=0, comparisonRawExitCode=0, contextRuns=2, contextAssertionsPerRun=95,
        originalCloneMatchesNode=True, fourFollowupsMatchNode=True, originalOldEngineFailurePreserved=True,
        engineAndComponentBinariesRetained=False, wasmcloudExecuted=False, fullNextAccepted=False,
        sameStoreIdentityProved=False, nativeResourceRetirementProved=False, productionPromoted=False)
    with (out / 'index.json').open('x') as f:
        json.dump(result, f, indent=2); f.write('\n')
    data = (out / 'index.json').read_bytes()
    print(json.dumps(dict(index=dict(path=str(out / 'index.json'), sha256=hashlib.sha256(data).hexdigest(),
        bytes=len(data)), payloadFiles=len(rows), retainedBytes=result['retainedBytes'])))


if __name__ == '__main__':
    main()
