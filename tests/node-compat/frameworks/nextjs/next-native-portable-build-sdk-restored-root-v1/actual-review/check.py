#!/usr/bin/env python3
"""Read retained text DATA only. Never invoke build, tools, engine or guest."""
import argparse
import collections
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import shlex
import tarfile

HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current', action='store_true', help='Also rehash only the 2502 original text records; no binary/tool/source-tree traversal.')
    args = parser.parse_args()
    index = json.loads((HERE / 'payload-index.json').read_bytes())
    archive = (HERE / index['archive']['path']).read_bytes()
    need(len(archive) == index['archive']['bytes'] and digest(archive) == index['archive']['sha256'], 'archive descriptor')
    rows = index['members']
    need(index['memberCount'] == len(rows) == 2502, 'finite member count')
    need(index['expandedBytes'] == sum(v['original']['bytes'] for v in rows) == 23567578, 'expanded bytes')
    expected = {v['member']: v for v in rows}
    need(len(expected) == len(rows), 'duplicate member')
    payload = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode='r:gz') as tf:
        for member in tf:
            path = PurePosixPath(member.name)
            need(member.isfile() and not path.is_absolute() and '..' not in path.parts, 'unsafe member')
            need(member.name in expected and member.name not in payload, 'unknown/duplicate member')
            row = expected[member.name]
            need(member.size == row['original']['bytes'] and member.mode == int(row['originalFilesystemMode'], 8), 'member size/mode')
            data = tf.extractfile(member).read()
            need(digest(data) == row['original']['sha256'], 'member digest')
            data.decode('utf-8')
            need(b'\0' not in data, 'binary payload')
            payload[member.name] = data
    need(set(payload) == set(expected), 'archive membership')
    by_original = collections.defaultdict(list)
    for row in rows:
        by_original[row['original']['path']].append(row)
        if args.current:
            current = Path(row['original']['path']).read_bytes()
            need(current == payload[row['member']], 'current original text changed')

    def raw(name):
        return payload[name]

    def obj(name):
        return json.loads(raw(name))

    def ref(value):
        matches = [row for row in by_original[value['path']] if row['original'] == value]
        need(bool(matches), 'unretained/mismatched text descriptor: ' + value['path'])
        return payload[matches[0]['member']]

    def clean(terminal, code=0, prefix=None):
        need(type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == code, 'raw outcome')
        need(terminal['timeout'] is False and terminal['forcedCleanup'] is False, 'timeout/forced cleanup')
        need(terminal['parentOwnedGroupGone'] is True and terminal['allObservedOwnedGroupsGone'] is True, 'owned groups')
        for key in ['interruptedSignals', 'remainingObservedPids', 'signals', 'errors']:
            need(terminal[key] == [], key)
        ref(terminal['authority'])
        ref(terminal['stdout'])
        ref(terminal['stderr'])
        if prefix is not None:
            names = sorted(name for name in payload if name.startswith(prefix + 'owned-') and name.endswith('.json'))
            snapshots = [obj(name) for name in names]
            need([v['sequence'] for v in snapshots] == list(range(len(snapshots))), 'all owned record sequences')
            need([v['process'] for v in snapshots] == terminal['observedProcesses'], 'all original owned process records')

    result = obj('success/work/result.json')
    metadata = obj('success/work/metadata.json')
    authority = obj('success/work/root-authority.json')
    observation = obj('success/outer/observation.json')
    review = obj('root/sdk-restored/actual-build-review.json')
    need(result['state'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_COMPLETED_RUNTIME_PENDING_V1' and result['passed'] is True, 'actual build result')
    need(result['primaryError'] is None and result['postCollectionErrors'] == [], 'build errors')
    need(result['engineOrGuestExecuted'] is False and result['adoption'] is False, 'execution/adoption scope')
    need(ref(result['metadata']) == raw('success/work/metadata.json'), 'metadata join')
    need(ref(review['actualResult']) == raw('success/work/result.json'), 'review result join')
    need(ref(review['actualRootObservation']) == raw('success/outer/observation.json'), 'review observation join')
    need(review['verifiedPassed'] is True and review['allSixPhaseAndOuterStartedTerminalAuthorityArgvRawStreamsAndOwnedRecordsVerified'] is True, 'independent DATA review')
    need(observation['rawExitCode'] == 0 and observation['ownedCleanRawZero'] is True and observation['workerReportedPassed'] is True and observation['errors'] == [], 'Root observation')
    need(ref(observation['workerResult']) == raw('success/work/result.json'), 'Root worker join')
    outer = obj('success/outer/terminal.json')
    clean(outer, prefix='success/outer/')
    need(ref(observation['terminal']) == raw('success/outer/terminal.json'), 'Root terminal join')
    started = obj('success/outer/started.json')
    need(started['pid'] == outer['pid'] and started['authority'] == outer['authority'] and started['timeoutSeconds'] == 7200, 'outer started join')
    need(started['argv'] == [authority['wrapperPython']['path'], '-B', '-I', authority['entry']['path'], '--authority', outer['authority']['path']], 'outer argv')
    need(ref(outer['authority']) == raw('success/work/root-authority.json'), 'issued authority equality')
    need(authority['configureAllowed'] is True and authority['buildAllowed'] is True, 'issued build scope')
    for key in ['engineOrGuestExecutionAllowed', 'freezeAllowed', 'networkAllowed', 'rustupAllowed']:
        need(authority[key] is False, 'forbidden scope: ' + key)

    labels = ['rust-version', 'cargo-version', 'rust-sysroot', 'configure', 'build', 'ninja-commands']
    need([p['label'] for p in result['phases']] == labels, 'six exact phases')
    for phase in result['phases']:
        prefix = 'success/phases/' + phase['label'] + '/'
        need(obj(prefix + 'phase.json') == phase, 'phase receipt')
        terminal = json.loads(ref(phase['outerTerminal']))
        need(ref(phase['outerTerminal']) == raw(prefix + 'owned-monitor/terminal.json'), 'phase terminal join')
        clean(terminal, prefix=prefix + 'owned-monitor/')
        start = obj(prefix + 'owned-monitor/started.json')
        packet = obj(prefix + 'packet.json')
        worker = json.loads(ref(phase['workerResult']))
        need(packet['authority'] == terminal['authority'] == start['authority'] and start['pid'] == terminal['pid'], 'phase authority/pid')
        need(start['timeoutSeconds'] == {'configure': 2400, 'build': 7200}.get(phase['label'], 120), 'exact phase cap')
        need(start['argv'] == [authority['wrapperPython']['path'], '-B', '-I', authority['entry']['path'], '--worker-packet', expected[prefix + 'packet.json']['original']['path']], 'worker argv')
        need(packet['argv'] == worker['argv'] == phase['argv'], 'actual command argv')
        need(packet['environment'] == obj('success/work/environment-policy.json')['environment'], 'phase environment')
        need(worker['rawChildExitCode'] == 0 and worker['lifecycleComplete'] is True and worker['launcherErrors'] == [], 'genuine child result')
        need(worker['stoppedForDiskSpace'] is False and type(worker['sigtermReceived']) is int and worker['sigtermReceived'] == 0 and worker['temporarySigtermHandlerRestored'] is True, 'worker lifecycle')
        need(worker['ownedGroupCleanup']['complete'] is True and worker['ownedGroupCleanup']['errors'] == [], 'inner owned cleanup')
        need(phase['innerOwnedClean'] is True and phase['ownedGone'] is True and phase['rawExitCode'] == phase['outerRawExitCode'] == 0, 'phase clean')
        need(ref(worker['rawCombinedLog']) == raw(prefix + 'command.combined.log'), 'combined raw log')

    need(metadata['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1' and metadata['portableBuildAdmissionVersion'] == 3, 'full metadata kind')
    need([metadata[k] for k in ['nativePolicyInputCount', 'buildSupportInputCount', 'embeddingInputCount']] == [435, 387, 3], 'input roles')
    copies = result['sourceCopies']
    need(len(copies) == 825 and len({v['target']['path'] for v in copies}) == 825, 'copy count')
    for copy in copies:
        need(copy['source']['sha256'] == copy['target']['sha256'] and copy['source']['bytes'] == copy['target']['bytes'], 'copied content records')
        need(copy['singleLink'] is True and copy['distinctInode'] is True and copy['mode'] in [0o600, 0o755], 'copy identity records')
    need(collections.Counter(v['mode'] for v in copies) == {0o600: 820, 0o755: 5}, 'copy modes')
    need(len(metadata['actualCompileRows']) == 80 and len(metadata['actualSeparateEmbeddingCompileRows']) == 1, '80+1 compile records')
    for row in metadata['actualCompileRows']:
        tokens = shlex.split(row['command'])
        need(all(flag in tokens for flag in ['--target=wasm32-wasi', '-m32', '-O3', '-DNDEBUG', '-flto=thin']), 'actual compile flags')
    need(ref(result['compileDatabase']) == raw('success/configured/build/compile_commands.json'), 'compile DB descriptor')
    need(ref(result['cmakeCache']) == raw('success/configured/build/CMakeCache.txt'), 'CMake cache descriptor')
    need(ref(result['wholeNinjaCommands']) == raw('success/phases/ninja-commands/command.combined.log'), 'full Ninja descriptor')
    need(ref(result['configuredRust']['manifest']) == raw('success/configured/build/starling-raw.wasm/Cargo.toml'), 'configured aggregate')
    need(ref(result['configuredRust']['lock']) == raw('success/configured/build/starling-raw.wasm/Cargo.lock'), 'configured lock')
    need(result['configuredRust']['lock']['sha256'] == 'dc098f33febee6952974705077140ff543ca37eb1cedad2e0b07496646c3bd61', 'exact 84-package lock')
    need(len(obj('success/work/protection-before.json')) == len(authority['reusedTrees']) == 10, 'ten tree snapshots')
    for role, tree in authority['reusedTrees'].items():
        need(ref(tree['inventory']) == raw('inputs/tree-inventories/' + role + '.json'), 'tree inventory join')
    need(result['inputProtection'] == {'files': 1825, 'wholeTrees': 10, 'unchanged': True, 'errors': [], 'currentBeforeFinalOnly': True}, 'protection result')
    for key in ['engineExecuted', 'guestExecuted', 'adoption', 'old83MetadataProjected', 'originalExtractionWholeTreeAttestationClaimed']:
        need(metadata[key] is False, 'metadata scope: ' + key)
    failure = obj('failure/sdk-admission/outer/observation.json')
    clean(obj('failure/sdk-admission/outer/terminal.json'), 1, prefix='failure/sdk-admission/outer/')
    need(failure['workerResult'] is None and failure['rawExitCode'] == 1, 'original pre-WORK failure preserved')
    need(b'WASI-SDK' in raw('failure/sdk-admission/outer/stderr.log') or b'wasi-sdk' in raw('failure/sdk-admission/outer/stderr.log'), 'original SDK failure raw')
    print(json.dumps({'state': 'FINITE_FULL_NATIVE_BUILD_DATA_CHECKED_V1', 'textRecords': len(rows), 'expandedBytes': index['expandedBytes'], 'sixPhaseRawCodes': [p['rawExitCode'] for p in result['phases']], 'outerRawCode': 0, 'earlierSdkFailureRawCode': 1, 'fullBuildDataVerified': True, 'engineOrGuestExecuted': False, 'importsOrRuntimeAccepted': False, 'adoption': False, 'currentOriginalTextRehashed': args.current}, sort_keys=True))


if __name__ == '__main__':
    main()
