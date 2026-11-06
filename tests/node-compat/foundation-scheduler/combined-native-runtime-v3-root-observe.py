"""Data-only observation of original completed runtime-v3 Root operations.

This never starts a process or imports the runtime owner. Tool session/exit
observations must be supplied from the actual original tool response.
"""
from pathlib import Path
import hashlib
import json
import os
import sys

REPO = Path('/Users/dan/dev/StarlingMonkey')
S = REPO / 'tests/node-compat/foundation-scheduler'


def row(path):
    p = Path(path)
    before = p.lstat()
    assert p.is_file() and not p.is_symlink()
    h = hashlib.sha256()
    with p.open('rb') as stream:
        for block in iter(lambda: stream.read(4194304), b''):
            h.update(block)
    after = p.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns,
            before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size,
                                    after.st_mtime_ns, after.st_ctime_ns)
    return dict(path=str(p), sha256=h.hexdigest(), bytes=after.st_size)


def read(path):
    return json.loads(Path(path).read_bytes())


def checked(descriptor):
    assert row(descriptor['path']) == descriptor
    return read(descriptor['path'])


def clean(descriptor, authority):
    t = checked(descriptor)
    assert t['authority'] == authority and t['rawExitCode'] == 0
    assert t['parentOwnedGroupGone'] is t['allObservedOwnedGroupsGone'] is True
    assert t['timeout'] is t['forcedCleanup'] is False
    for key in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids']:
        assert t[key] == []
    return t


def publication(base):
    base = Path(base)
    ix = row(base / 'index.json')
    result = row(base / 'result.json')
    completion = row(base / 'completion.json')
    names = {'index.json', 'completion.json'}
    files = read(ix['path'])['files']
    for f in files:
        name = f['path']
        assert name and not Path(name).is_absolute()
        assert '..' not in Path(name).parts and name not in names
        names.add(name)
        assert row(base / name) == dict(f, path=str(base / name))
    assert not any(p.is_symlink() for p in base.rglob('*'))
    assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()} == names
    assert sum(f['path'] == 'result.json' and f['sha256'] == result['sha256']
               and f['bytes'] == result['bytes'] for f in files) == 1
    c = read(completion['path'])
    assert c['externalRawZeroAndSeparateReviewRequired'] is True
    assert c['index'] == dict(ix, path='index.json')
    assert c['result'] == dict(result, path='result.json')
    return ix, result, completion, len(files)


assert len(sys.argv) == 5
phase, case, session, tool_exit = sys.argv[1:]
assert phase in ['map', 'run']
assert case in ['resource', 'clock-snapshot', 'surviving-interest', 'pure']
assert int(tool_exit) == 0 and int(session) > 0
prefix = S / ('combined-native-runtime-v3-' + case + '-' + phase)
authority = row(str(prefix) + '-root-authority.json')
config = row(str(prefix) + '-root-config.json')
invocation = row(str(prefix) + '-root-invocation.json')
r, cfg, inv = checked(authority), checked(config), checked(invocation)
assert cfg['rootAuthority'] == authority and cfg['sourceIndex'] == r['sourceIndex']
assert r['phase'] == cfg['phase'] == phase and r['fixtureId'] == cfg['fixtureId'] == case
assert inv['rootAuthority'] == authority and inv['config'] == config
assert r['state'] == 'ROOT_REVIEWED_COMBINED355_NATIVE_RUNTIME_PHASE_V3'
assert r['sourceIndex']['sha256'] == '54a70237f27aa9f0d1c0d6d0f7766f1575734031c806478017f304d9a73cd424'
assert row(r['sourceIndex']['path']) == r['sourceIndex']
output = Path(r['outputRoot'])
external = Path(r['externalOutputRoot'])
caller = Path(str(output) + '-root-caller')
inner_terminal, outer_terminal = row(external / 'terminal.json'), row(caller / 'terminal.json')
clean(inner_terminal, authority)
clean(outer_terminal, authority)
frames = [json.loads(line) for line in (external / 'stdout.log').read_text().splitlines()
          if line.startswith('{')]
terminal_frames = [f for f in frames if f.get('state') == 'COMBINED355_RUNTIME_RAW_TERMINAL_UNREVIEWED_V3']
assert len(terminal_frames) == 1
assert terminal_frames[0]['phase'] == phase and terminal_frames[0]['fixtureId'] == case
assert terminal_frames[0]['terminal'] == inner_terminal and terminal_frames[0]['rawExitCode'] == 0
ix, result_row, completion, count = publication(output)
result = checked(result_row)
assert result['sourceIndex'] == r['sourceIndex'] and result['rootAuthority'] == authority
assert result['config'] == config and result['fixtureId'] == case
artifact = checked(r['actualArtifactReview']['result'])
assert result['component'] == artifact['artifacts']['component']
report = dict(schemaVersion=1,
              state='ROOT_OBSERVED_COMBINED355_' + case.replace('-', '_').upper() + '_' + phase.upper() + '_ZERO_UNREVIEWED_V3',
              toolObservation=dict(sessionId=int(session), rawExitCode=int(tool_exit)),
              sourceIndex=r['sourceIndex'], rootAuthority=authority, config=config,
              invocation=invocation, observer=row(Path(__file__).resolve()),
              actualIndex=ix, completion=completion, externalParentTerminal=inner_terminal,
              outerTerminal=outer_terminal, externalStdout=row(external / 'stdout.log'),
              completePublicationMembershipAndHashesVerified=True,
              payloadFileCount=count, totalFileCount=count + 2,
              sourceControlledFinalChecksPassed=True, component=result['component'],
              nativeSourceFiles=355, externalEmbeddingSources=3,
              fullMetadataFields=80, selectedWholeManifests=11,
              operationalAdmission=False, runtimeAcceptanceClaim=False)
if phase == 'map':
    assert result['state'] == 'COMBINED355_MAPPED_OUTPUT_COMPLETE_UNREVIEWED_V3'
    assert result['generatedApplicationImported'] is result['ordinaryExportsInvoked'] is False
    report.update(mappingResult=result_row, mappingOptions=result['mappingOptions'],
                  requestedMappingOptions=result['requestedMappingOptions'],
                  postCallOptionsShape=result['postCallOptionsShape'],
                  mappedFiles=result['mappedFiles'],
                  generatedApplicationImported=False, ordinaryExportsInvoked=False,
                  requiresIndependentActualMappedReview=True)
else:
    assert result['state'] == 'COMBINED355_RUNTIME_COMPLETE_UNREVIEWED_V3'
    for key in ['fullSixFixturesAccepted', 'all17GatesSatisfied', 'fullProfileAcceptance',
                'nativeOffsetInterestDropOrTeardownProved', 'expectedCallbackFailureProved',
                'fatalCallbackGateSatisfied', 'operationalAdmission', 'runtimeAcceptanceClaim']:
        assert result[key] is False
    if case == 'resource':
        assert result['coverage'] == dict(rawPublicStrings=35, runRecords=49,
              callbackObservations=98, newIds=322, retainedJcoRotations=3,
              freshJcoRotations=1, freshWasmtimeWithinExportRotations=3)
    for session_result in result['sessions']:
        t = checked(session_result['terminal'])
        assert t['closed'] is t['ownedGroupGone'] is t['terminalExitZeroObserved'] is True
        assert t['status'] == 0 and t['signal'] is None and t['spawnError'] is None
        assert t['timedOut'] is t['outputLimitExceeded'] is False
        assert t['externalSignal'] is None and t['errors'] == t['signals'] == []
    report.update(runtimeResult=result_row, sessions=result['sessions'],
                  coverage=result['coverage'], actualMappedReview=r['actualMappedReview'],
                  requiresIndependentActualRuntimeReview=True)
path = Path(str(prefix) + '-root-results.json')
with path.open('x') as stream:
    json.dump(report, stream, indent=2)
    stream.write('\n')
    stream.flush()
    os.fsync(stream.fileno())
print(json.dumps(dict(rootResult=row(path), files=count + 2, phase=phase, fixtureId=case)))
