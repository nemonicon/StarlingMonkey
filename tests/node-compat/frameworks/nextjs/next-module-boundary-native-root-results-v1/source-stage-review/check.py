"""Verify retained Source-stage DATA; optional --current checks selected text originals.

No producer import, subprocess, network, payload-tree scan or build invocation.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import stat
import tarfile

HERE = Path(__file__).resolve().parent


def need(value, label):
    if not value:
        raise ValueError(label)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main(current=False):
    index = json.loads((HERE / 'payload-index.json').read_bytes())
    rows = index['files']
    need(len(rows) == index['memberCount'] == 172, 'Exact finite denominator')
    expected = {r['path']: r for r in rows}
    need(len(expected) == len(rows), 'Unique retained paths')
    raw = (HERE / 'data.tar.gz').read_bytes()
    need(len(raw) == index['archive']['bytes'] <= 8 * 1024**2 and
         sha(raw) == index['archive']['sha256'], 'Archive descriptor')
    retained = {}
    total = 0
    with tarfile.open(HERE / 'data.tar.gz', 'r:gz') as archive:
        for member in archive:
            name = member.name
            rel = PurePosixPath(name)
            need(member.isfile() and not rel.is_absolute() and
                 '..' not in rel.parts and rel.as_posix() == name and
                 name not in retained and name in expected, 'Safe exact regular member')
            need(0 <= member.size <= 4 * 1024**2, 'Per-member bound')
            total += member.size
            need(total <= 16 * 1024**2, 'Uncompressed bound')
            stream = archive.extractfile(member)
            data = stream.read(member.size + 1)
            row = expected[name]
            need(len(data) == member.size == row['bytes'] and
                 sha(data) == row['sha256'] and member.mode == row['physicalAtCapture']['mode'],
                 'Retained original bytes/mode')
            data.decode('utf-8')
            retained[name] = data
    need(set(retained) == set(expected) and total == index['totalUncompressedBytes'],
         'Complete retained membership')
    by_original = {r['originalPath']: r for r in rows}
    need(len(by_original) == len(rows), 'Unique original roles')

    def document(name):
        return json.loads(retained[name])

    def ref(value):
        need(set(value) == {'path', 'sha256', 'bytes'}, 'Plain original descriptor')
        row = by_original[value['path']]
        need(all(row[k] == value[k] for k in ['sha256', 'bytes']), 'Original ref joins capture')
        return retained[row['path']]

    def original(value):
        return json.loads(ref(value))

    # These are complete new Source families only; no recursive ancestry replay.
    families = ['next-native-portable-source-v2', 'next-native-portable-build-preparation-v4',
                'next-native-portable-generator-check-v2', 'next-module-fileurl-boundary-candidate-v1']
    for family in families:
        prefix = 'source/' + family + '/'
        source_index = document(prefix + 'index.json')
        need({n[len(prefix):] for n in retained if n.startswith(prefix)} ==
             {'index.json', *[r['path'] for r in source_index['files']]}, 'Closed selected Source family')
        for row in source_index['files']:
            data = retained[prefix + row['path']]
            need(sha(data) == row['sha256'] and len(data) == row['bytes'], 'Indexed Source member')
    builder = document('source/next-native-portable-build-preparation-v4/plan.json')
    summary = document('materialization/source-materialization.json')
    composition = original(summary['composition'])
    selected = document('root/portable-selection.json')
    need(selected['sourceOnly'] is True and selected['engineBuilt'] is selected['guestExecuted'] is False,
         'Source-only selection')
    need(summary['files'] == len(summary['filesCopied']) == len(selected['files']) ==
         len(selected['physicalRecords']) == 825 and len(selected['directoryRecords']) == 171,
         'Source counts')
    need(summary['bytes'] == 7532227 and summary['roleCounts'] == selected['roleCounts'] ==
         {'native-policy-source': 435, 'build-support': 387, 'componentize-embedding': 3}, 'Role boundary')
    need(summary['roleContentSha256'] == selected['roleContentSha256'] ==
         builder['portableSourcePolicy']['roleContentSha256'] ==
         'cfbd75be70aeaa36006009fa6580b8f0f4bb789852e8d8201eefefd09d0a1550', 'New fingerprint')
    need(original(selected['sourceMaterialization']) == summary and
         original(selected['composition']) == composition and composition['nativeSourceFiles'] == 435,
         'Actual materialization/composition refs')
    observation = document('root/source-stage-tool-observation.json')
    need(type(observation['materializerToolExitCode']) is int and observation['materializerToolExitCode'] == 0
         and type(observation['selectionToolExitCode']) is int and observation['selectionToolExitCode'] == 0,
         'Preserved Root tool observations')

    generated = document('generator/result.json')
    generator_plan = original(generated['plan'])
    grant = original(generated['rootAuthority'])
    source_index = original(generated['sourceIndex'])
    need(any(r['path'] == 'plan.json' and all(r[k] == generated['plan'][k]
         for k in ['sha256', 'bytes']) for r in source_index['files']), 'Indexed producer plan')
    need(grant['sourceIndex'] == generated['sourceIndex'] and grant['plan'] == generated['plan'] and
         original(grant['portableSelection']) == selected and grant['generatorChecksAllowed'] is
         grant['nodeHostSourceOnly'] is True and grant['unissued'] is False, 'Generator-only Root roles')
    need(all(grant[k] is False for k in ['nativeBuildAllowed', 'compilerAllowed', 'cmakeAllowed',
         'cargoAllowed', 'engineAllowed', 'guestAllowed', 'networkAllowed', 'copySourceAllowed']),
         'Generator authority scope')
    need(generated['sourceRoot'] == generator_plan['sourceRoot'] == selected['sourceRoot'] and
         generated['composition'] == generator_plan['composition'] == selected['composition'] and
         generated['materializationSummary'] == generator_plan['materializationSummary'] == selected['sourceMaterialization'] and
         generated['roleContentSha256'] == generator_plan['roleContentSha256'] == selected['roleContentSha256'] and
         generator_plan['perCommandSeconds'] == 30 and generator_plan['outerSeconds'] == 900,
         'Producer plan/final/selection source roles and caps')
    original(generator_plan['materializerIndex'])
    original(generator_plan['portableAdmission']['sourceIndex'])
    need(original(generator_plan['portableAdmission']['plan']) == builder,
         'Genuine carrier policy plan')
    need(generated['passed'] is generated['portableInputsPreserved'] is True and
         generated['wholePortableBefore'] == generated['wholePortableAfter'] == selected['physicalRecords'] and
         generated['portableDirectoriesBefore'] == generated['portableDirectoriesAfter'] == selected['directoryRecords'],
         'Recorded full portable bookends')
    need(generated['sourceBefore'] == generated['sourceAfter'] and len(generated['sourceBefore']) == 435 and
         generated['node'] == generator_plan['node'], 'Native and Node roles')
    need(all(generated[k] is None for k in ['primaryError', 'finalProtectionError', 'toolProtectionError',
         'outerOwnerError']), 'Preserved generator errors')
    need(generated['toolInputsBefore'] == generated['toolInputsAfter'] ==
         generated['outerToolInputsBefore'] == generated['outerToolInputsAfter'] and
         len(generated['toolInputsBefore']) == 6, 'Recorded tool bookends')
    expected_argv = [[generated['node']['path'], str(Path(generated['sourceRoot']) / args[0]),
                      *[generated['sourceRoot'] if x == '$SOURCE' else x for x in args[1:]]]
                     for args in builder['portableSourcePolicy']['generatorCommands']]
    need([c['argv'] for c in generated['commands']] == expected_argv and len(expected_argv) == 10,
         'Ten original commands')

    def clean(value):
        need(type(value['rawExitCode']) is int and value['rawExitCode'] == 0 and
             value['parentOwnedGroupGone'] is value['allObservedOwnedGroupsGone'] is True and
             value['timeout'] is value['forcedCleanup'] is False and
             all(value[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']) and
             all(g['alive'] is False for g in value['finalGroups']), 'Original clean raw0 terminal')

    for command in generated['commands']:
        start, terminal = original(command['started']), original(command['terminal'])
        clean(terminal)
        need(start['argv'] == command['argv'] and start['timeoutSeconds'] == 30 and
             start['pid'] == terminal['pid'] and start['authority'] == terminal['authority'] == generated['rootAuthority'],
             'Original command start/cap/authority')
        need(command['cwd'] == generated['sourceRoot'] and command['rawExitCode'] == 0 and
             command['monitorError'] is None and command['ownedGroupsClean'] is True and
             terminal['stdout'] == command['stdout'] and terminal['stderr'] == command['stderr'], 'Command raw joins')
        ref(command['stdout'])
        need(ref(command['stderr']) == b'', 'Original empty command stderr')
    outer_start, outer = original(generated['outerStarted']), original(generated['outerTerminal'])
    clean(outer)
    need(outer_start['timeoutSeconds'] == 900 and outer_start['pid'] == outer['pid'] and
         outer_start['authority'] == outer['authority'] == generated['rootAuthority'] and
         outer_start['argv'] == [generator_plan['python']['path'], '-I', '-B',
         str(Path(generated['sourceIndex']['path']).parent / 'run.py'), '--worker-authority',
         generated['rootAuthority']['path']], 'Original outer worker/cap/authority')
    need(outer['stdout'] == generated['outerStdout'] and outer['stderr'] == generated['outerStderr'] and
         ref(generated['outerStderr']) == b'', 'Original outer streams')
    ref(generated['outerStdout'])
    body = original(generated['bodyResult'])
    need(all(generated[k] == v for k, v in body.items()), 'Whole body/final result joins')
    need(generated['outputCapSatisfied'] is True and generated['continuousFreeFloorClaimed'] is False and
         generated['minimumFreeBytes'] == 67108864 and generated['freeBytesAtAdmission'] >= 67108864,
         'Recorded bounded Source-only capacity scope')
    need(sum(r['bytes'] for r in rows if r['path'].startswith(('generator/', 'generator-outer/'))) == 1984333,
         'Complete finite generator text')

    preparation = document('preparation/preparation.json')
    prepared = original(preparation['unissuedAuthority'])
    cargo = original(preparation['portableCargoSelection'])
    assembled = document('root/authority.unissued.json')
    need(retained['root/preparation.stdout.log'] == retained['preparation/preparation.json'] and
         retained['root/preparation.stderr.log'] == b'' and preparation['originalInputsPreserved'] is True,
         'Whole actual preparation stdout/receipt')
    need(len([n for n in retained if n.startswith('preparation/')]) == 5 and
         preparation['portableSelection'] == grant['portableSelection'] and
         cargo['composition'] == selected['composition'] and cargo['sourceMaterialization'] == selected['sourceMaterialization'] and
         cargo['nativeSourceRoot'] == selected['sourceRoot'] and len(cargo['base21']) == 21,
         'Five new preparation roles and base21')
    need(cargo['audit']['packageCount'] == 84 and cargo['audit']['rootDependencies'] ==
         ['rust-encoding', 'rust-hooks', 'rust-url', 'multipart', 'icu_capi', 'unicode-bidi-ffi'] and
         cargo['audit']['oneAggregateStaticlib'] is True and cargo['oldMetadataDescriptorsRetargeted'] is False,
         'Original84 graph audit retained')
    config = original(preparation['preparationConfig'])
    need(cargo['metadataResult'] == config['cargoMetadataResult'] and
         cargo['actualMetadata']['sha256'] == '65544c7b180112e645902ff961db1198ea6d8699a78462cd6e935933ab3de08d' and
         cargo['intlLockfile']['sha256'] == 'dc098f33febee6952974705077140ff543ca37eb1cedad2e0b07496646c3bd61',
         'Unretargeted original graph/lock metadata witnesses')
    need(set(prepared['reusedTrees']) == {'intl-firefox', 'intl-vendor'} and len(assembled['reusedTrees']) == 10,
         'Fresh two Intl / eight reused tree roles')
    for role in prepared['reusedTrees']:
        need(prepared['reusedTrees'][role] == cargo['reusedTrees'][role] == assembled['reusedTrees'][role],
             'Fresh Intl inventory roles')
        original(cargo['reusedTrees'][role]['inventory'])
    for value in [prepared, assembled]:
        need(value['configureAllowed'] is value['buildAllowed'] is None and all(value[k] is False for k in
             ['engineOrGuestExecutionAllowed', 'freezeAllowed', 'networkAllowed', 'rustupAllowed']), 'Retained unissued authority')
    review = document('root/actual-preparation-review.json')
    need(review['verifiedPassed'] is True and review['reviewerIntakeCorrection']['firstRawExitCode'] == 1 and
         review['reviewerIntakeCorrection']['correctedRootDependencies'] == cargo['audit']['rootDependencies'],
         'Reviewer-only failed assertion preserved')
    original(review['complementaryIndependentRootPreparationAndLauncherReview'])
    need(builder['disk'] == {'startBytes': 3221225472, 'stopBytes': 1073741824} and
         builder['timeouts']['build'] == 7200, 'Unchanged full-build guard')
    if current:
        for row in rows:
            path = Path(row['originalPath'])
            need(path.resolve() == path, 'Current alias refused')
            value = path.lstat()
            physical = dict(dev=value.st_dev, ino=value.st_ino, nlink=value.st_nlink,
                            mode=stat.S_IMODE(value.st_mode), bytes=value.st_size,
                            mtimeNs=value.st_mtime_ns, ctimeNs=value.st_ctime_ns)
            need(stat.S_ISREG(value.st_mode) and value.st_nlink == 1 and
                 physical == row['physicalAtCapture'] and sha(path.read_bytes()) == row['sha256'],
                 'Selected current original differs')
    print(json.dumps(dict(retainedDataVerified=True, members=len(rows), textBytes=total,
                         generatorCommands=10, generatorOuter=1, preparationJsonFiles=5,
                         currentSelectedTextOriginalsVerified=current,
                         sourceOrToolPayloadTreesReplayed=False, nativeBuildReviewed=False,
                         engineOrGuestOrImportSafetyOrAdoptionClaimed=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current', action='store_true')
    main(parser.parse_args().current)
