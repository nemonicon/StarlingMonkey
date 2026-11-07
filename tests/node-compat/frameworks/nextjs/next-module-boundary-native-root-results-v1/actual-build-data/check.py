"""Replay retained guarded-build text DATA, without invoking build or guest tools."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shlex
import stat
import tarfile

HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current', action='store_true', help='Also read only the selected original text files.')
    args = parser.parse_args()
    index = json.loads((HERE / 'payload-index.json').read_text())
    archive = (HERE / 'data.tar.gz').read_bytes()
    need(index['archive'] == dict(path='data.tar.gz', sha256=hashlib.sha256(archive).hexdigest(), bytes=len(archive)), 'archive descriptor')
    rows = index['members']
    need(index['memberCount'] == len(rows) <= 4000, 'finite member count')
    need(index['expandedBytes'] == sum(r['original']['bytes'] for r in rows) <= 64 * 1024**2, 'finite byte count')
    expected = {r['member']: r for r in rows}
    by_original = {r['original']['path']: r for r in rows}
    need(len(expected) == len(by_original) == len(rows), 'unique members/original paths')
    payload = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as tf:
        for item in tf:
            p = PurePosixPath(item.name)
            need(item.isfile() and not p.is_absolute() and '..' not in p.parts, 'ordinary confined member')
            need(item.name in expected and item.name not in payload, 'member set')
            record = expected[item.name]
            need(item.size == record['original']['bytes'] and item.mode == record['mode'], 'size/mode')
            data = tf.extractfile(item).read()
            need(hashlib.sha256(data).hexdigest() == record['original']['sha256'], 'member digest')
            data.decode('utf-8')
            need(b'\0' not in data, 'text payload')
            payload[item.name] = data
    need(set(payload) == set(expected), 'complete member set')
    current_rows = []
    if args.current:
        for record in rows:
            p = Path(record['original']['path'])
            need(p.is_absolute() and p.resolve() == p and all(not x.is_symlink() for x in (p, *p.parents)), 'current canonical path')
            before = p.stat()
            need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and stat.S_IMODE(before.st_mode) == record['mode'], 'current file/mode')
            need(p.read_bytes() == payload[record['member']], 'current selected original bytes')
            need(p.stat() == before, 'current immediate read bookend')
            current_rows.append((p, before))

    def obj_role(role):
        return json.loads(payload[index['roles'][role]])

    def ref(value):
        need(value['path'] in by_original, 'unretained text descriptor: ' + value['path'])
        record = by_original[value['path']]
        need(record['original'] == value, 'descriptor equality')
        return payload[record['member']]

    def clean(terminal):
        need(type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0, 'raw zero')
        need(terminal['timeout'] is terminal['forcedCleanup'] is False, 'no timeout/forced cleanup')
        need(terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True, 'owned groups gone')
        need(all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']), 'clean owner arrays')
        for key in ['authority', 'stdout', 'stderr']:
            ref(terminal[key])

    def owner(terminal_ref, cap):
        terminal = json.loads(ref(terminal_ref))
        clean(terminal)
        root = Path(terminal_ref['path']).parent
        start = json.loads(ref(by_original[str(root / 'started.json')]['original']))
        need(start['pid'] == terminal['pid'] and start['authority'] == terminal['authority'], 'started/terminal owner identity')
        need(start['timeoutSeconds'] == cap, 'unchanged owner cap')
        snapshots = sorted((r for path, r in by_original.items() if Path(path).parent == root and re.fullmatch(r'owned-\d+\.json', Path(path).name)), key=lambda r: r['original']['path'])
        observations = [json.loads(payload[r['member']]) for r in snapshots]
        need([v['sequence'] for v in observations] == list(range(len(observations))), 'complete owner record sequences')
        need([v['process'] for v in observations] == terminal['observedProcesses'], 'complete original process records')
        return terminal

    result = obj_role('result')
    native = obj_role('metadata')
    authority = obj_role('root-authority')
    review = obj_role('actual-build-review')
    observation = obj_role('outer-observation')
    need(result['passed'] is True and result['primaryError'] is None and result['postCollectionErrors'] == [], 'build success DATA')
    need(ref(result['metadata']) == payload[index['roles']['metadata']], 'full metadata bytes')
    need(review['verifiedPassed'] is True and review['state'] == 'INDEPENDENT_PORTABLE_NEXT_INTL_NATIVE_BUILD_DATA_REVIEW_PASSED_V1', 'actual DATA review')
    need(ref(review['actualResult']) == payload[index['roles']['result']], 'review/result join')
    need(ref(review['actualRootObservation']) == payload[index['roles']['outer-observation']], 'review/observation join')
    outer = owner(observation['terminal'], 7200)
    need(ref(outer['authority']) == payload[index['roles']['root-authority']], 'genuine issued authority')
    need(observation['ownedCleanRawZero'] is observation['workerReportedPassed'] is True and observation['errors'] == [], 'Root observation')
    need(authority['configureAllowed'] is authority['buildAllowed'] is True, 'build scope')
    need(all(authority[k] is False for k in ['engineOrGuestExecutionAllowed', 'freezeAllowed', 'networkAllowed', 'rustupAllowed']), 'forbidden scopes')
    labels = ['rust-version', 'cargo-version', 'rust-sysroot', 'configure', 'build', 'ninja-commands']
    need([p['label'] for p in result['phases']] == labels and native['phases'] == result['phases'], 'six genuine phases')
    for phase in result['phases']:
        terminal = owner(phase['outerTerminal'], {'configure': 2400, 'build': 7200}.get(phase['label'], 120))
        need(terminal['authority'] == native['rootAuthority'], 'phase authority')
        need(type(phase['rawExitCode']) is type(phase['outerRawExitCode']) is int and phase['rawExitCode'] == phase['outerRawExitCode'] == 0, 'phase raw codes')
        need(phase['ownedGone'] is phase['innerOwnedClean'] is True, 'phase owned cleanup')
        worker = json.loads(ref(phase['workerResult']))
        need(worker['rawChildExitCode'] == 0 and worker['lifecycleComplete'] is True and worker['launcherErrors'] == [], 'worker lifecycle')
        need(worker['stoppedForDiskSpace'] is False and worker['ownedGroupCleanup']['complete'] is True, 'worker completion')
        need(worker['ownedGroupCleanup']['events'] == worker['ownedGroupCleanup']['errors'] == [], 'worker cleanup arrays')
        ref(worker['rawCombinedLog'])
    need(native['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1' and type(native['portableBuildAdmissionVersion']) is int and native['portableBuildAdmissionVersion'] == 3, 'genuine metadata kind')
    need([native[k] for k in ['nativePolicyInputCount', 'buildSupportInputCount', 'embeddingInputCount']] == [435, 387, 3], '825 input roles')
    need(len(result['sourceCopies']) == 825, '825 copy records')
    for copy in result['sourceCopies']:
        need(copy['singleLink'] is copy['distinctInode'] is True, 'copy identity records')
        need((copy['source']['sha256'], copy['source']['bytes']) == (copy['target']['sha256'], copy['target']['bytes']), 'copy byte records')
    loader = [c for c in result['sourceCopies'] if c['target']['path'].endswith('/native-source/runtime/script_loader.cpp')]
    need(len(loader) == 1 and loader[0]['target']['sha256'] == 'fbc1d13eebc66d20b01b1828008f3918609752e060320dbd16837722d4216ab8', 'compiled guarded loader copy')
    need(len(native['actualCompileRows']) == 80 and len(native['actualSeparateEmbeddingCompileRows']) == 1, '80 native/one embedding')
    generated = Path(native['compiledSourceRoot']).parent / 'build/starling-raw.wasm/null.cpp'
    outsiders = [Path(r['file']) for r in native['actualCompileRows'] if Path(native['compiledSourceRoot']) not in Path(r['file']).parents]
    need(outsiders == [generated] and ref(by_original[str(generated)]['original']) == b'', 'generated empty null.cpp exception')
    for compile_row in native['actualCompileRows']:
        argv = shlex.split(compile_row['command'])
        need(all(flag in argv for flag in ['--target=wasm32-wasi', '-m32', '-O3', '-DNDEBUG', '-flto=thin']), 'actual compile flags')
    need(result['inputProtection']['files'] == review['protectedFileDescriptorsChecked'] == 1841, 'protected descriptor count')
    need(result['inputProtection']['wholeTrees'] == len(authority['reusedTrees']) == 10, 'ten protected trees')
    need(result['inputProtection']['unchanged'] is True and result['inputProtection']['errors'] == [], 'protected input result')
    need(native['engine'] == review['engine'] == result['engineCandidate'], 'actual engine descriptors')
    need(native['engine']['sha256'] == 'ca84baa11cf88bd6c6aa96b2806df05baef11f9ba89edb5f6dc5c66e0d035eb7', 'actual engine generation')
    need(all(native[k] is False for k in ['engineExecuted', 'guestExecuted', 'adoption', 'old83MetadataProjected']), 'execution scope')
    for p, before in current_rows:
        need(p.stat() == before, 'whole selected-current read bookend')
    print(json.dumps(dict(state='GUARDED_FULL_NATIVE_BUILD_TEXT_DATA_REPLAY_PASSED_V1', members=len(rows),
        expandedBytes=index['expandedBytes'], nativeBuildDataPassed=True, currentOriginalTextRehashed=args.current,
        engineOrGuestExecuted=False, binariesOr825PayloadsRehashed=False, importOrRuntimeAccepted=False, adoption=False)))


if __name__ == '__main__':
    main()
