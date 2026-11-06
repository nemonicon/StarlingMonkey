"""Root DATA observation after an already terminal component-caller phase.

This script cannot launch a process, engine, module or guest. It records actual
tool-session observations supplied by Root, verifies whole output publications
and original monitor terminals, and binds completed bundles for later separate
construction. An observation grants no ordinary runtime or adoption authority.
"""
from pathlib import Path
import hashlib
import json
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
SCHEDULER = REPO / 'tests/node-compat/foundation-scheduler'
CALLER = SCHEDULER / 'combined-native-component-caller-candidate-v1'
BASE = '/private/tmp/starling-node-compat/combined-native-component-caller-v1'
SOURCE_SHA = 'aec12b5c21995f1f080871be2d8fa77ee5aa20fe884e220dd94db7d6573993f1'
DATA_SHA = '9eaa5cd246fda65f8436554f9177baa0d82054bfeef3da0f8477edfac287f48e'


def descriptor(path):
    path = Path(path)
    a = path.lstat()
    assert path.is_file() and not path.is_symlink()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4194304), b''):
            digest.update(block)
    z = path.lstat()
    assert (a.st_dev, a.st_ino, a.st_size, a.st_mode, a.st_mtime_ns, a.st_ctime_ns) == (
        z.st_dev, z.st_ino, z.st_size, z.st_mode, z.st_mtime_ns, z.st_ctime_ns)
    return dict(path=str(path), sha256=digest.hexdigest(), bytes=z.st_size)


def read(path):
    return json.loads(Path(path).read_bytes())


def checked(row, base=None):
    path = Path(row['path'])
    if not path.is_absolute():
        assert base is not None and '..' not in path.parts
        path = base / path
    actual = descriptor(path)
    assert (actual['sha256'], actual['bytes']) == (row['sha256'], row['bytes'])
    return actual


def publication(base):
    index = read(base / 'index.json')
    names = {'index.json', 'completion.json'}
    assert index['schemaVersion'] == 1
    for row in index['files']:
        name = row['path']
        assert name not in names and not Path(name).is_absolute()
        assert '\\' not in name and all(p not in ('', '.', '..') for p in name.split('/'))
        names.add(name)
        checked(row, base)
    assert not any(p.is_symlink() for p in base.rglob('*'))
    assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()} == names
    completion = read(base / 'completion.json')
    checked(completion['index'], base)
    checked(completion['result'], base)
    assert completion['index']['path'] == 'index.json'
    assert completion['result']['path'] == 'result.json'
    return index, completion


def terminal(path, expected):
    value = read(path)
    assert type(value['rawExitCode']) is int and value['rawExitCode'] == expected
    assert value['parentOwnedGroupGone'] is value['allObservedOwnedGroupsGone'] is True
    assert value['timeout'] is value['forcedCleanup'] is False
    for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']:
        assert value[key] == []
    return value


def write_new(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    assert len(sys.argv) == 5
    phase, case, session_text, exit_text = sys.argv[1:]
    assert phase in ['bundle', 'construct']
    assert case in ['pure', 'resource', 'fatal', 'init-fatal', 'clock-snapshot', 'surviving-interest']
    session, tool_exit = int(session_text), int(exit_text)
    assert session > 0
    expected_failure = phase == 'construct' and case == 'init-fatal'
    assert tool_exit == (1 if expected_failure else 0)
    output = Path(BASE + '-' + phase + '-' + case)
    prefix = SCHEDULER / ('combined-native-component-v1-' + phase + '-' + case)
    result_path = Path(str(prefix) + '-root-results.json')
    assert not result_path.exists()
    assert descriptor(CALLER / 'index.json')['sha256'] == SOURCE_SHA
    index, completion = publication(output)
    result = read(output / 'result.json')
    inner_path = Path(str(output) + '-external-root') / 'terminal.json'
    outer_path = Path(str(output) + '-root-caller') / 'terminal.json'
    inner, outer = terminal(inner_path, tool_exit), terminal(outer_path, tool_exit)
    root_path = Path(str(prefix) + '-root-authority.json')
    config_path = Path(str(prefix) + '-root-config.json')
    root, config = read(root_path), read(config_path)
    assert result['rootAuthority'] == descriptor(root_path)
    assert result['config'] == descriptor(config_path)
    assert result['sourceIndex'] == descriptor(CALLER / 'index.json')
    assert result['fixtureId'] == root['fixtureId'] == config['fixtureId'] == case
    assert result['phase'] == root['phase'] == config['phase'] == phase
    for key in ['sourceIndex', 'fixtureSource', 'fixtureWit']:
        checked(result[key])
    assert (result['nativeSourceFiles'], result['externalEmbeddingSources'],
            result['fullMetadataFields'], result['selectedWholeManifests']) == (355, 3, 80, 11)
    assert descriptor(output / 'native-record-data.json')['sha256'] == DATA_SHA
    native = read(output / 'native-record-data.json')
    assert read(output / 'selected-whole-manifests.json') == native['bootstrap']['selectedManifests']
    assert len(native['bootstrap']['metadata']) == 80
    assert len(native['bootstrap']['metadata']['sourceManifest']) == 355
    assert len(native['bootstrap']['selectedManifests']) == 11
    for key in ['ordinaryGuestExportsInvoked', 'generatedApplicationModuleImported',
                'keyOrCryptoWorkloadsInvoked', 'operationalAdmission', 'runtimeAcceptanceClaim']:
        assert result[key] is False
    assert result['finalProtectionErrors'] == []
    report = dict(
        schemaVersion=1,
        state='ROOT_OBSERVED_COMBINED355_CALLER_PHASE_UNREVIEWED_V1',
        phase=phase, fixtureId=case,
        toolObservation=dict(sessionId=session, rawExitCode=tool_exit),
        sourceIndex=result['sourceIndex'], rootAuthority=descriptor(root_path),
        config=descriptor(config_path), invocation=descriptor(str(prefix) + '-root-invocation.json'),
        phaseResult=descriptor(output / 'result.json'),
        phaseIndex=descriptor(output / 'index.json'),
        phaseCompletion=descriptor(output / 'completion.json'),
        externalTerminal=descriptor(inner_path), outerTerminal=descriptor(outer_path),
        ownedChildPid=inner['pid'], outerOwnedParentPid=outer['pid'],
        nativeSourceFiles=355, externalEmbeddingSources=3,
        fullMetadataFields=80, selectedWholeManifests=11,
        publicationMembershipAndHashesVerified=True,
        sourceControlledFinalChecksPassed=True,
        ordinaryGuestExportsInvoked=False, generatedApplicationModuleImported=False,
        keyOrCryptoWorkloadsInvoked=False, operationalAdmission=False,
        runtimeAcceptanceClaim=False, overallSixFixtureAcceptance=False,
        requiresIndependentActualArtifactReview=phase == 'construct')
    if not expected_failure:
        assert result['primaryPresent'] is False and result['primary'] is None
        expected = 'COMBINED355_BUNDLE_COMPLETE_UNREVIEWED_V1' if phase == 'bundle' else 'COMBINED355_COMPONENT_COMPLETE_UNREVIEWED_V1'
        assert result['state'] == expected
        assert completion['state'] == 'COMPLETE_UNREVIEWED_EXTERNAL_RAW_ZERO_REQUIRED'
    if phase == 'bundle':
        bundle = checked(result['bundle'])
        returned = read(result['bundleReturn']['path'])
        assert returned['code'].encode() == Path(bundle['path']).read_bytes()
        assert returned['imports'] == result['expectedNativeResidualImports']
        assert returned['moduleIds'] == [result['fixtureSource']['path']]
        assert result['fixtureEvaluated'] is result['packagerLoaded'] is result['componentizationAttempted'] is False
        assert result['allElevenManifestsUsed'] is True
        inputs = dict(bundleReport=descriptor(output / 'result.json'), bundle=bundle,
                      bundleExternalTerminal=descriptor(inner_path))
        report.update(inputs, fixtureEvaluated=False, packagerLoaded=False)
        write_new(SCHEDULER / ('combined-native-component-v1-' + case + '-bundle-inputs.json'), inputs)
    else:
        loader_path = Path(str(prefix) + '-loader-root-authority.json')
        loader_config_path = Path(str(prefix) + '-loader-root-config.json')
        loader = read(loader_path)
        inputs = read(SCHEDULER / ('combined-native-component-v1-' + case + '-bundle-inputs.json'))
        for key, row in inputs.items():
            assert root[key] == row
            checked(row)
        assert root['guestSourceSha256'] == loader['guestSourceSha256'] == inputs['bundle']['sha256']
        assert root['guestSourceSha256'] == descriptor(output / 'bundle.mjs')['sha256']
        for key in ['nativeEngine', 'nativeMetadata', 'witWorldSha256', 'worldName',
                    'selectedInterfaces', 'disableFeatures', 'privateTemporaryRoot']:
            assert root[key] == loader[key]
        report.update(inputs, pairedLoaderRootAuthority=descriptor(loader_path),
                      pairedLoaderConfig=descriptor(loader_config_path),
                      pairedActualBundleShaBeforeLoaderVerified=True,
                      component=result.get('component'),
                      allGeneratedFiles=[descriptor(p) for p in sorted((output / 'transpiled').rglob('*')) if p.is_file()])
        if expected_failure:
            assert result['state'] == 'COMBINED355_CALLER_PHASE_FAILED_UNACCEPTED_V1'
            assert completion['state'] == 'FAILED_UNACCEPTED'
            assert result['primaryPresent'] is True and result['primary'] is not None
            assert result['component'] is None and result['componentizationAttempted'] is True
            report.update(state='ROOT_OBSERVED_COMBINED355_INIT_FATAL_CONSTRUCTION_FAILURE_UNREVIEWED_V1',
                          componentReturned=False, failure=result['primary'],
                          expectedInitializationRefusalClassificationRequiresIndependentReview=True)
        else:
            checked(result['component'])
            audit = read(output / 'interface-audit.json')
            assert audit['componentSha256'] == result['component']['sha256']
            assert audit['emittedImports'] == result['emittedImports']
            assert set(audit['emittedImports']) == set(root['selectedInterfaces'])
            report.update(emittedImports=result['emittedImports'],
                          emittedWit=descriptor(output / 'emitted.wit'),
                          interfaceAudit=descriptor(output / 'interface-audit.json'),
                          transpileMetadata=descriptor(output / 'transpile-return-shape.json'))
    publication(output)
    write_new(result_path, report)
    print(json.dumps(dict(rootReport=descriptor(result_path), phase=phase, fixtureId=case,
                          observedRawExitCode=tool_exit, component=report.get('component'))))


if __name__ == '__main__':
    main()
