#!/usr/bin/env python3
"""Read retained DATA only. Never invokes the native builder or a Wasm engine."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile

HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise AssertionError(message)


def digest(data, row):
    require(len(data) == row['bytes'], 'byte length: ' + row['path'])
    require(hashlib.sha256(data).hexdigest() == row['sha256'], 'SHA256: ' + row['path'])


def clean_terminal(record):
    require(type(record['rawExitCode']) is int and record['rawExitCode'] == 0, 'raw exit')
    for key in ('timeout', 'forcedCleanup'):
        require(record[key] is False, key)
    for key in ('parentOwnedGroupGone', 'allObservedOwnedGroupsGone'):
        require(record[key] is True, key)
    for key in ('errors', 'signals', 'interruptedSignals', 'remainingObservedPids'):
        require(record[key] == [], key)
    require(all(group['alive'] is False for group in record['finalGroups']), 'final groups')


def main():
    capsule = json.loads((HERE / 'capsule.json').read_bytes())
    review = json.loads((HERE / 'review.json').read_bytes())
    digest((HERE / 'data.tar.gz').read_bytes(), capsule['archive'])
    rows = capsule['files']
    require(len(rows) == 322, 'finite capsule membership')
    names = [row['path'] for row in rows]
    require(len(set(names)) == len(names), 'duplicate capsule member')
    blobs = {}
    with tarfile.open(HERE / 'data.tar.gz', 'r:gz') as archive:
        members = archive.getmembers()
        require(sorted(member.name for member in members) == sorted(names), 'whole tar membership')
        for member in members:
            path = PurePosixPath(member.name)
            require(member.isfile() and not path.is_absolute() and '..' not in path.parts, 'unsafe tar member')
            blobs[member.name] = archive.extractfile(member).read()
    originals = {}
    for row in rows:
        data = blobs[row['path']]
        digest(data, row['original'])
        originals.setdefault(row['original']['path'], []).append(data)

    def load(name):
        return json.loads(blobs[name])

    def retained(row):
        require(row['path'] in originals, 'missing retained descriptor: ' + row['path'])
        for data in originals[row['path']]:
            digest(data, row)

    result, metadata, plan = load('actual/result.json'), load('actual/metadata.json'), load('source/plan')
    require(result['passed'] is True and result['primaryError'] is None and result['collectorErrors'] == [], 'result acceptance')
    require(result['state'] == 'EXPERIMENTAL_MODULE_UTF16_NATIVE_DELTA_COMPLETED_RUNTIME_PENDING_V1', 'result state')
    require(metadata['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_INCREMENTAL_NATIVE_BUILD_ACTUAL_V1', 'new metadata kind')
    require(metadata['engine'] == capsule['engine'] == review['engine'], 'engine descriptor')
    retained(capsule['metadata'])
    retained(capsule['actualResult'])
    require(metadata['freshFrontendCompileRows'] == 1 and metadata['baselineCompileDatabaseRows'] == 80, 'compile provenance')
    require(metadata['unchangedBaselineCompileDatabaseRows'] == 79 and metadata['baselineSeparateEmbeddingRows'] == 1, 'retained compile provenance')
    for key in ('all80FreshCompilationClaimed', 'fullBuildOrConfigureOrCargoExecuted', 'oldMetadataProjected', 'engineOrGuestExecuted', 'runtimeAcceptance'):
        require(metadata[key] is False, key)
    require(result['inputProtection'] == {'rows':1949, 'trees':13, 'unchanged':True, 'errors':[], 'currentBeforePhaseFinalOnly':True}, 'operation-time protection')
    dependencies = result['compileDependencies']
    require(len(dependencies['files']) == 1046, 'dependency count')
    require(dependencies == metadata['compileDependencies'], 'metadata dependencies')
    require(len({row['path'] for row in dependencies['files']}) == 1046, 'unique dependencies')
    require([row['role'] for row in dependencies['files']].count('exact-vfs-afterimage') == 1, 'single VFS source')
    require(all(row['role'] in ('exact-vfs-afterimage', 'authenticated-before-compile') for row in dependencies['files']), 'dependency authentication roles')
    retained(dependencies['depfile'])
    retained(metadata['actualAfterimage'])
    require(blobs['actual/module-kernel.cpp'] == blobs['inputs/afterimage'], 'private source bytes')
    overlay = load('actual/overlay.json')
    require(overlay == {'version':0, 'case-sensitive':True, 'use-external-names':False, 'roots':[{'type':'file', 'name':metadata['virtualOriginalSource']['path'], 'external-contents':str(Path(capsule['engine']['path']).parent / 'module-kernel.cpp')}]}, 'exact one-file VFS overlay')
    old, new = metadata['archiveAudit']['old'], metadata['archiveAudit']['new']
    require(len(old) == len(new) == 15 and metadata['archiveAudit']['onlySelectedCodeMemberReplaced'] is True, 'archive inventory')
    require([row['name'] for row in old] == [row['name'] for row in new], 'archive member names')
    require([a['name'] for a,b in zip(old,new) if a != b] == ['module-kernel.cpp.obj'], 'only module member changed')
    require(result['archiveAudit'] == metadata['archiveAudit'], 'archive result join')
    require(metadata['coreImportsExportsAndFunctionTypesMatchBaseline'] is True and result['coreSurfaceMatchesBaseline'] is True, 'typed core comparison')
    require(metadata['coreSurface'] == result['coreSurface'], 'whole core surface retained')
    labels = ['compile', 'archive', 'ranlib', 'link', 'optimize']
    require([phase['label'] for phase in result['phases']] == labels, 'five phase order')
    require(result['phases'] == metadata['phases'], 'metadata phase join')
    for label in labels:
        phase = load('phases/' + label + '/phase.json')
        worker = load('phases/' + label + '/worker-result.json')
        require(phase == result['phases'][labels.index(label)], 'whole phase join')
        clean_terminal(load('phases/' + label + '/owned-monitor/terminal.json'))
        for key in ('outerTerminal', 'workerResult'):
            retained(phase[key])
        require(worker['argv'] == phase['argv'], 'actual argv join')
        require(worker['rawChildExitCode'] == 0 and worker['status'] == 0 and worker['childStarted'] is True and worker['lifecycleComplete'] is True, 'actual child completion')
        require(worker['stoppedForDiskSpace'] is False and worker['stopReason'] is None and worker['sigtermReceived'] == 0 and worker['launcherErrors'] == [], 'child failure fields')
        require(worker['ownedGroupCleanup']['complete'] is True and worker['ownedGroupCleanup']['errors'] == [] and worker['ownedGroupCleanup']['events'] == [], 'child group cleanup')
        retained(worker['log'])
        require(worker['log']['bytes'] == 0, 'empty actual tool log')
        for point in ('preBudget', 'postBudget'):
            require(phase[point]['freeBytes'] >= 800*1024*1024 and phase[point]['privateBytes'] <= 100*1024*1024, 'phase disk budget')
    clean_terminal(load('root-monitor/terminal.json'))
    for terminal_name in ['root-monitor/terminal.json'] + ['phases/' + label + '/owned-monitor/terminal.json' for label in labels]:
        terminal = load(terminal_name)
        for key in ('stdout', 'stderr', 'authority'):
            retained(terminal[key])
    require(load('phases/ranlib/phase.json')['argv'][1] == 's', 'regular llvm-ar dispatch')
    require(metadata['additionalLinkFlags'] == ['-Wl,--strip-debug'] == plan['additionalLinkFlags'], 'declared link flag delta')
    require(result['initialFreeBytes'] >= 1024**3, 'limited start guard')
    require(review['currentOriginalInputRows'] == 1949 and review['currentWholeTrees'] == 13 and review['currentRegularFileReads'] == 16692, 'independent current readback record')
    require(review['sourceAuthorRelationshipDisclosed'] is True and review['actualTargetCommandsRerun'] is False and capsule['binaryPayloadsCopied'] is False, 'review scope')
    print(json.dumps({'passed':True, 'retainedTextFiles':len(rows), 'freshFrontendRows':1, 'baselineRows':80, 'compileDependencies':1046, 'unchangedArchiveMembers':14, 'cleanPhases':5, 'engine':capsule['engine'], 'guestOrCompilerInvokedByChecker':False}, sort_keys=True))


if __name__ == '__main__':
    main()
