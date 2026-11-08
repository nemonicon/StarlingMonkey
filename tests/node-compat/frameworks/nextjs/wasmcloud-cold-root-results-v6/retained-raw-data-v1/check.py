"""Portable offline cold-eight DATA reader; no original paths or actors."""
import base64
import hashlib
import json
from pathlib import Path
import stat

HERE = Path(__file__).resolve().parent


def physical(p):
    s = p.lstat()
    return s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns


def bounded(p, size=None):
    assert p.resolve() == p and not p.is_symlink()
    before = physical(p)
    assert stat.S_ISREG(before[2]) and before[3] == 1 and 0 <= before[4] <= 2 * 1024 * 1024
    if size is not None:
        assert before[4] == size
    raw = p.read_bytes()
    assert physical(p) == before and len(raw) == before[4]
    return raw


def main():
    manifest = json.loads(bounded(HERE / 'manifest.json'))
    assert manifest['copiedFileCount'] == len(manifest['files']) == 45
    assert manifest['copiedPayloadBytes'] == sum(r['copied']['bytes'] for r in manifest['files']) == 749774
    assert manifest['maximumPayloadBytes'] == 33554432
    data, originals, ids = {}, {}, set()
    for item in manifest['files']:
        copied, original = item['copied'], item['original']
        rel = Path(copied['relativePath'])
        assert not rel.is_absolute() and '..' not in rel.parts and rel.parts[0] == 'files'
        assert copied['relativePath'] not in data and original['path'] not in originals
        raw = bounded(HERE / rel, copied['bytes'])
        assert hashlib.sha256(raw).hexdigest() == copied['sha256'] == original['sha256']
        assert copied['bytes'] == original['bytes'] and copied['mode'] == original['mode']
        identity = physical(HERE / rel)[:2]
        assert identity not in ids
        ids.add(identity)
        data[copied['relativePath']] = raw
        originals[original['path']] = item
    c = manifest['checker']
    assert c['relativePath'] == 'check.py'
    assert hashlib.sha256(bounded(HERE / 'check.py', c['bytes'])).hexdigest() == c['sha256']
    assert {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()} == set(data) | {'check.py', 'manifest.json'}
    actual_dirs = {p.relative_to(HERE).as_posix() for p in [HERE, *HERE.rglob('*')] if p.is_dir()}
    assert actual_dirs == {d['relativePath'] for d in manifest['copiedDirectories']}
    for name in actual_dirs:
        assert not (HERE / name).is_symlink()

    def load(rel):
        return json.loads(data['files/' + rel])

    def refbytes(ref):
        # Historical absolute paths are explicit DATA keys, never filesystem paths.
        item = originals[ref['path']]
        assert {k: item['original'][k] for k in ['path', 'sha256', 'bytes']} == ref
        return data[item['copied']['relativePath']]

    def refjson(ref):
        return json.loads(refbytes(ref))

    result = load('actor/result.json')
    authority = refjson(result['rootAuthority'])
    plan = refjson(authority['plan'])
    index = refjson(result['sourceIndex'])
    assert result['sourceIndex'] == authority['sourceIndex']
    for name in ['plan.json', 'cold-contract.json']:
        selected = next(row for row in index['files'] if row['path'] == name)
        raw = data['files/source/' + name]
        assert selected['bytes'] == len(raw) and selected['sha256'] == hashlib.sha256(raw).hexdigest()
    assert result['passed'] is result['eightCaptured'] is result['contractsPassed'] is True and result['errors'] == []
    false = ['physicalInstanceIdentityObserved', 'readonlyWasiDescriptorRightsProved', 'cacheSequenceExecuted', 'browserExecuted', 'retainedContractAcceptance', 'fullNextAcceptance', 'adoption']
    assert all(result[key] is False for key in false)
    assert len(result['commands']) == 2 and result['server'] == result['commands'][1]
    output = Path(result['outputRoot'])  # DATA only; never opened.
    prefix = [authority['wash']['path'], '--user-config', str(output / 'empty-user-config.json'), '-C', str(output / 'project')]
    assert result['commands'][0]['argv'] == prefix + ['--output', 'json', 'config', 'show']
    assert result['commands'][1]['argv'] == prefix + ['--log-level', 'info', '--meters', 'duration', 'dev']
    for command in result['commands']:
        assert command['exit'] == dict(code=0, signal=None, error=None)
        assert command['timeout'] is command['forcedCleanup'] is False
        refbytes(command['stdout'])
        refbytes(command['stderr'])
    assert result['server']['shutdownRequested'] is result['server']['sigintSent'] is True
    configured = refjson(result['configFiles'][0])
    assert refjson(result['configFiles'][1]) == {}
    shown = refjson(result['commands'][0]['stdout'])
    assert configured == result['configured'] and shown['success'] is True and shown['data'] == result['effectiveConfiguration']
    origin = result['portLease']['origin']
    for config in [configured, result['effectiveConfiguration']]:
        assert config['version'] == '2.11.0' and config['dev']['address'] == origin.removeprefix('http://')
        assert config['build']['command'] == config['dev']['command'] == 'test -f "$WASH_COMPONENT_PATH"'
        assert config['build']['component_path'] == config['dev']['component_path'] == result['component']['path']
        assert config['dev']['service'] is False and config['wit']['skip_fetch'] is True
        assert all(config['workload'][key] == [] for key in ['allowedHosts', 'allowedIpNameLookups', 'allowedHostLoopbackPorts'])
        assert config['workload']['environment']['config'] == dict(STARLING_NEXT_ORIGIN=origin, NODE_ENV='production', NEXT_TELEMETRY_DISABLED='1')
        assert config['dev']['volumes'] == [dict(host_path=str(output / 'app'), guest_path='/app'), dict(host_path=str(output / 'cache'), guest_path='/app/.next/cache')]
    assert configured['dev']['components'] == configured['dev']['plugins'] == configured['dev']['host_plugins'] == []
    ready = result['readiness']
    assert ready['tcpConnect'] is ready['workloadRegistered'] is True and ready['extraHttpRequests'] == 0 and ready['origin'] == origin
    stderr_lines = refbytes(result['server']['stderr']).decode().splitlines()
    for event in ready['completionEvents']:
        assert stderr_lines[event['lineNumber'] - 1] == event['line'] and event['address'] == origin
        assert 'INFO listening for HTTP requests address=' + origin in event['line']
    contract = load('source/cold-contract.json')
    assert len(result['responses']) == len(contract['requests']) == 8
    stream = None
    for response, expected in zip(result['responses'], contract['requests']):
        assert all(response[key] == expected[key] for key in ['id', 'method', 'path', 'status'])
        assert response['status'] == 200 and response['complete'] is True and response['contract'] == dict(passed=True, failures=[])
        body, chunks = refbytes(response['body']), refjson(response['chunkRecord'])
        assert chunks == response['chunks'] and response['wireSha256'] is None
        parts = [base64.b64decode(c['base64'], validate=True) for c in chunks]
        assert [len(p) for p in parts] == [c['bytes'] for c in chunks] and b''.join(parts) == body
        if 'json' in expected:
            obj = json.loads(body)
            assert all(obj[k] == v for k, v in expected['json'].items())
            if response['id'] == 'fs-crypto-probe':
                assert hashlib.sha256(obj['text'].encode()).hexdigest() == obj['sha256']
        assert all(marker.encode() in body for marker in expected.get('includes', []))
        if expected.get('stream'):
            assert len(parts) == 3 and response['shellChunk'] == next(i for i, p in enumerate(parts) if b'NEXT_STREAM_SHELL' in p) == 0
            assert response['readyChunk'] == next(i for i, p in enumerate(parts) if b'NEXT_STREAM_READY' in p) == 1
            stream = [len(p) for p in parts]
    start, terminal, observation = [load('owner/' + name + '.json') for name in ['started', 'terminal', 'observation']]
    assert start['pid'] == terminal['pid'] == 61905 and start['timeoutSeconds'] == 600 and terminal['rawExitCode'] == 0
    assert start['authority'] == terminal['authority'] == result['rootAuthority']
    assert start['argv'] == [plan['node']['path'], str(Path(result['sourceIndex']['path']).parent / 'deploy.mjs'), result['rootAuthority']['path']]
    assert terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
    assert terminal['timeout'] is terminal['forcedCleanup'] is False
    assert all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    assert len(terminal['observedProcesses']) == 3
    for i, process in enumerate(terminal['observedProcesses']):
        owned = load('owner/owned-' + str(i).zfill(4) + '.json')
        assert owned['sequence'] == i and owned['process'] == process
    refbytes(terminal['stdout'])
    assert refbytes(terminal['stderr']) == b''
    refjson(observation['terminal'])
    assert refjson(observation['result']) == result
    assert observation['rawExitCode'] == 0 and observation['ownedGroupsClean'] is observation['protectedInputsPreserved'] is observation['passed'] is True
    frames = [json.loads(line) for line in data['files/root/runtime.stdout.log'].splitlines() if line]
    assert frames == [dict(pid=61905, timeoutSeconds=600), observation] and data['files/root/runtime.stderr.log'] == b''
    world = load('root/cleanup-476b-cold-first-full-world-guard.json')
    assert world['authority'] == result['rootAuthority'] and world['before'] == world['after']
    assert world['unchanged'] is world['nativeInputsPreserved'] is True
    assert world['before']['sourceIndex'] == authority['worldSourceIndex'] and world['before']['members'] == 28 and world['before']['witFiles'] == 8
    primary = load('root/actual-runtime-review.json')
    assert primary['verifiedPassed'] is primary['coldEightRequestsPassed'] is True and refjson(primary['actualResult']) == result
    assert primary['rootAuthority'] == result['rootAuthority']
    print(json.dumps(dict(passed=True, state='PORTABLE_OFFLINE_CURRENT_COLD_EIGHT_DATA_VERIFIED_V1', copiedFiles=45, copiedBytes=749774, coldResponses=8, streamDecodedChunkBytes=stream, originalOwnerRawExit=0, configuredDenyAllLists=True, outboundProbeExecuted=False, descriptorReadWriteQualificationPreserved=True, originalPathsRead=False, actorOrHelperOrNetworkInvoked=False, historicalPhysicalClaimsDocumentary=True, liveCheckoutModesObserved=sorted({stat.S_IMODE((HERE / name).stat().st_mode) for name in data}), fullNextAcceptance=False, physicalStoreIdentityObserved=False)))


if __name__ == '__main__':
    main()
