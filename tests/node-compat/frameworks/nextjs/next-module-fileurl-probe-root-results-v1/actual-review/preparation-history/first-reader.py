"""Portable finite probe DATA replay. Never imports actors or extracts files to disk."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, io, json, re, stat, tarfile, zlib

HERE = Path(__file__).resolve().parent
LIMIT = 64 * 1024**2


def sha(value):
    return hashlib.sha256(value).hexdigest()


def parse(value):
    def unique(items):
        result = {}
        for key, item in items:
            assert key not in result
            result[key] = item
        return result
    return json.loads(value, object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def identity(path):
    s = path.lstat()
    return [s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def clean(terminal):
    assert type(terminal['rawExitCode']) is int and terminal['rawExitCode'] == 0
    assert terminal['timeout'] is terminal['forcedCleanup'] is False
    assert terminal['parentOwnedGroupGone'] is terminal['allObservedOwnedGroupsGone'] is True
    assert all(terminal[k] == [] for k in ['errors', 'signals', 'interruptedSignals', 'remainingObservedPids'])
    assert all(row['alive'] is row['signalAllowed'] is False for row in terminal['finalGroups'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--draft', action='store_true')
    parser.add_argument('--current', action='store_true', help='Only selected retained text/Source originals, not binaries or omitted trees.')
    args = parser.parse_args()
    final = HERE / 'index.json'
    sealed = final.exists()
    if sealed:
        index = parse(final.read_bytes())
        nodes = list(HERE.rglob('*'))
        assert not any(p.is_symlink() for p in nodes)
        assert {p.relative_to(HERE).as_posix() for p in nodes if p.is_file()} == {r['path'] for r in index['files']} | {'index.json'}
        for row in index['files']:
            path = HERE / row['path']; value = path.read_bytes()
            assert path.resolve(strict=True) == path and path.is_file() and path.stat().st_nlink == 1
            assert (len(value), sha(value)) == (row['bytes'], row['sha256'])
    else:
        assert args.draft, 'Unsealed read requires explicit --draft'
    ix = parse((HERE / 'payload-index.json').read_bytes())
    assert ix['binaryApplicationPackageSdkOr825PayloadIncluded'] is ix['recursiveArchivesIncluded'] is False
    assert ix['actorOrToolOrNetworkInvoked'] is ix['nodeCompatibilityAccepted'] is ix['interopOrFullNextAccepted'] is False
    assert ix['allSelectedOriginalPhysicalAndContentBookendsUnchanged'] is ix['guardSafeRefusalOnly'] is True
    compressed = (HERE / ix['bundle']['path']).read_bytes()
    assert (sha(compressed), len(compressed)) == (ix['bundle']['sha256'], ix['bundle']['bytes'])
    unzip = zlib.decompressobj(16 + zlib.MAX_WBITS)
    expanded = unzip.decompress(compressed, LIMIT + 1)
    assert len(expanded) <= LIMIT and unzip.eof and not unzip.unused_data and not unzip.unconsumed_tail
    rows = {row['archivePath']: row for row in ix['files']}
    assert len(rows) == len(ix['files']) == ix['memberCount'] < 1000
    assert len({row['original']['path'] for row in rows.values()}) == len(rows)
    blobs, seen, end = {}, set(), 0
    with tarfile.open(fileobj=io.BytesIO(expanded), mode='r:') as archive:
        for member in archive:
            rel = PurePosixPath(member.name)
            assert member.isfile() and not rel.is_absolute() and '..' not in rel.parts
            assert member.name in rows and member.name not in seen
            assert member.offset == end and member.offset_data == member.offset + 512
            row = rows[member.name]
            assert member.size == row['original']['bytes'] < 8 * 1024**2 and member.mode == row['mode']
            value = archive.extractfile(member).read()
            assert sha(value) == row['original']['sha256']
            value.decode('utf-8'); assert b'\0' not in value
            blobs[row['original']['path']] = value; seen.add(member.name)
            end = member.offset_data + ((member.size + 511) // 512) * 512
    assert set(rows) == seen and len(expanded) - end >= 1024 and not any(expanded[end:])
    assert sum(len(value) for value in blobs.values()) == ix['logicalBytes']

    def data(path):
        return parse(blobs[str(path)])

    def ref(row):
        value = blobs[row['path']]
        assert (sha(value), len(value)) == (row['sha256'], row['bytes'])
        return value

    for source in ix['sourceFamilies']:
        index = parse(ref(source)); root = Path(source['path']).parent
        declared = {str(root / row['path']) for row in index['files']} | {source['path']}
        retained = {path for path in blobs if root in Path(path).parents}
        assert declared == retained
        for row in index['files']:
            rel = PurePosixPath(row['path']); assert not rel.is_absolute() and '..' not in rel.parts
            ref(dict(path=str(root / row['path']), sha256=row['sha256'], bytes=row['bytes']))

    def owner(root, seconds):
        root = Path(root)
        terminal, started = data(root / 'terminal.json'), data(root / 'started.json')
        clean(terminal)
        assert started['pid'] == terminal['pid'] and started['timeoutSeconds'] == seconds
        assert started['authority'] == terminal['authority']; ref(terminal['authority'])
        for key in ['stdout', 'stderr']: ref(terminal[key])
        records = [data(path) for path in sorted(blobs) if path.startswith(str(root) + '/owned-') and path.endswith('.json')]
        assert [row['sequence'] for row in records] == list(range(len(records)))
        assert [row['process'] for row in records] == terminal['observedProcesses']
        return terminal, started

    ctor = Path(ix['constructorRoot']); runtime = Path(ix['runtimeRoot'])
    cr, rr = data(ctor / 'result.json'), data(runtime / 'result.json')
    ca, ra = parse(ref(cr['rootAuthority'])), parse(ref(rr['rootAuthority']))
    cp, rp = parse(ref(cr['plan'])), parse(ref(ra['plan']))
    assert cr['passed'] is True and cr['error'] is None and cr['finalProtection'] == {'unchanged': True}
    assert cr['state'] == 'NEXT_NATIVE_COMPONENT_CONSTRUCTION_PASSED_UNREVIEWED_V2' and cr['entryMode'] == 'guard'
    assert ca['state'] == 'ROOT_NEXT_NATIVE_COMPONENT_CONSTRUCTION_V2' and ca['componentizeInitAllowed'] is True
    assert ca['entryMode'] == 'guard' and ca['callerIndex'] == cr['callerIndex']
    assert cr['callerIndex']['sha256'] == '683552b24345116ee43b382d3e1ef2ce34d6f88858a82b98b4f203b15021e865'
    assert cp['inputSourceIndex']['sha256'] == 'c355260ccfffd59a5d31468ee26cd4c40d3fd3aeaad37dfe75024c0f37ca018b'
    assert cp['entries'] == {'guard': cr['artifacts']['inputEntry']}
    outer, started = owner(Path(str(ctor) + '-external-root'), 2400)
    assert outer['authority'] == cr['rootAuthority']
    caller = Path(cr['callerIndex']['path']).parent
    assert started['argv'] == ['/Applications/Xcode.app/Contents/Developer/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3.9',
        '-I', '-B', str(caller / 'run.py'), '--authority', cr['rootAuthority']['path'], '--sha256', cr['rootAuthority']['sha256']]
    assert [command['label'] for command in cr['commands']] == ['componentize-init', 'component-validate', 'component-wit']
    for command, cap in zip(cr['commands'], [1800, 120, 120]):
        terminal, start = owner(ctor / command['label'], cap)
        assert command['rawExitCode'] == 0 and command['clean'] is True and command['capSeconds'] == cap
        assert start['argv'] == command['argv'] and terminal['authority'] == cr['rootAuthority']
        assert ref(command['terminal']) == blobs[str(ctor / command['label'] / 'terminal.json')]
        for key in ['stdout', 'stderr']:
            assert ref(command[key]) == blobs[str(ctor / command['label'] / (key + '.log'))]
    artifacts = cr['artifacts']
    audit = parse(ref(artifacts['componentAudit']))
    shape, imports = parse(ref(artifacts['returnedOwnShape'])), parse(ref(artifacts['returnedImports']))
    properties = {item['key']['string']: item for item in shape['properties']}
    assert shape['type'] == 'object' and len(properties) == len(shape['properties']) and set(properties) == {'component', 'imports', 'debug'}
    component = properties['component']['value']
    assert component['type'] == 'Uint8Array' and component['file'] == artifacts['component']
    assert component['byteLength'] == artifacts['component']['bytes'] and component['sha256'] == artifacts['component']['sha256']
    assert properties['debug']['value'] == {'type': 'undefined'}

    def decode(value):
        if value['type'] == 'string': return value['value']
        assert value['type'] == 'Array'
        items = {p['key']['string']: p for p in value['properties']}
        assert len(items) == len(value['properties'])
        length = items.pop('length')['value']['value']
        assert type(length) is int and length >= 0
        assert set(items) == {str(i) for i in range(length)}
        return [decode(items[str(i)]['value']) for i in range(length)]

    assert decode(properties['imports']['value']) == imports and len(imports) == 131
    assert audit['state'] == 'NEXT_NATIVE_COMPONENT_DATA_AUDIT_PASSED_V1' and audit['passed'] is True
    for key in ['component', 'engine', 'nativeMetadata']: assert audit[key] == artifacts[key]
    assert audit['entryMode'] == 'guard' and audit['allEmittedVersion'] == '0.2.10' and audit['noExternalPreview1OrCustomImports'] is True
    assert len(cp['selectedInterfaces']) == len(set(cp['selectedInterfaces'])) == 13
    assert len(audit['emittedImports']) == len(set(audit['emittedImports'])) == 13
    assert set(audit['emittedImports']) == set(cp['selectedInterfaces']) and all(x.endswith('@0.2.10') for x in audit['emittedImports'])
    assert audit['exports'] == ['wasi:http/incoming-handler@0.2.10']
    wit = blobs[str(ctor / 'component-wit/stdout.log')].decode('utf-8')
    parsed_imports, parsed_exports = re.findall(r'^\s*import ([^;\n]+);$', wit, re.M), re.findall(r'^\s*export ([^;\n]+);$', wit, re.M)
    assert len(parsed_imports) == len(re.findall(r'^\s*import\b', wit, re.M))
    assert len(parsed_exports) == len(re.findall(r'^\s*export\b', wit, re.M))
    assert parsed_imports == audit['emittedImports'] and parsed_exports == audit['exports']
    world = data(Path(str(ctor) + '-external-root') / 'world-guard.json')
    expected_world = dict(sourceIndex=cp['worldSourceIndex'], members=28, witFiles=8,
                          exactFileAndDirectoryMembership=True, noSymlinkOrHardlinkAliases=True)
    assert world['unchanged'] is True and world['before'] == world['after'] == expected_world
    assert cp['worldSourceIndex']['sha256'] == '802595f5a32dd93fc95c63eb95c901352ecb8da180152735982c344d6b827f58'
    assert ca['worldSourceIndex'] == cp['worldSourceIndex'] == rp['worldSourceIndex']
    metadata_bytes = blobs[str(ctor / 'api-return/native-metadata-input.json')]
    assert metadata_bytes == ref(ca['nativeMetadata']) and sha(metadata_bytes) == 'e674f7d2eebefd9f7885589344c9bf04e71e599ecf6ec1dfdea75ba7cee7ecbd'
    metadata = parse(metadata_bytes)
    assert metadata['metadataKind'] == 'EXPERIMENTAL_NEXT_INTL_NATIVE_BUILD_ACTUAL_V1'
    for key, expected in ca['metadataExpectedFixedValues'].items():
        assert json.dumps(metadata[key], sort_keys=True, allow_nan=False) == json.dumps(expected, sort_keys=True, allow_nan=False)
    assert metadata['engine'] == ca['engine'] == artifacts['engine'] == ra['engine']
    assert [metadata[k] for k in ['nativePolicyInputCount', 'buildSupportInputCount', 'embeddingInputCount']] == [435, 387, 3]
    assert len(metadata['actualCompileRows']) == 80 and len(metadata['actualSeparateEmbeddingCompileRows']) == 1
    assert [r for r in metadata['nativePolicyInputManifest'] if r['path'] == 'runtime/script_loader.cpp'][0]['sha256'] == 'fbc1d13eebc66d20b01b1828008f3918609752e060320dbd16837722d4216ab8'
    assert len(ca['engineBuildEvidence']) == 39 and len(ca['newSourceEvidence']) == 12
    for value in ca['engineBuildEvidence'] + ca['newSourceEvidence']: ref(value)
    for key in ['ordinaryExportsInvoked', 'httpServed', 'appMountedAtInit', 'productionProfilePromoted', 'metadataFrameProjected']:
        assert cr[key] is False
    ctor_review = parse(ref(ix['roles']['actual-construction-review.json']))
    assert ctor_review['verifiedPassed'] is True and ref(ctor_review['actualResult']) == blobs[str(ctor / 'result.json')]
    for key in ['component', 'componentAudit', 'engine', 'nativeMetadata']: assert ctor_review[key] == artifacts[key]
    assert ctor_review['runtimeAccepted'] is ctor_review['nodeParityProved'] is ctor_review['cjsInterop3856Selected'] is False

    # One actual ordinary deployed GET, distinct from the INIT construction.
    assert ra['state'] == 'ROOT_FILE_URL_GUARD_PROBE_AUTHORIZED_V1' and ra['sourceIndex']['sha256'] == 'f47a4845b558b4a54b184bdd891c75ad8ca76bff65f79728e4c9058d96f00ddd'
    assert ra['constructionResult'] == ctor_review['actualResult'] and ra['constructionDataReview'] == ix['roles']['actual-construction-review.json']
    for key in ['component', 'componentAudit', 'engine', 'nativeMetadata']: assert ra[key] == artifacts[key] == rr[key]
    assert ra['engineBuildEvidence'] == ca['engineBuildEvidence']
    assert ra['ordinaryProbeAllowed'] is ra['loopbackServeAllowed'] is ra['fixtureStagingAllowed'] is True
    assert all(ra[key] is False for key in ['componentConstructionAllowed', 'nodeControlAllowed', 'browserAllowed', 'appMountAllowed',
                                          'networkBeyondLoopbackAllowed', 'fullNextAcceptanceAllowed', 'adoptionAllowed'])
    runtime_outer = Path(str(runtime) + '-external-root')
    terminal, start = owner(runtime_outer, 180)
    actor_root = Path(ra['sourceIndex']['path']).parent
    assert start['authority'] == rr['rootAuthority'] and start['argv'] == [rp['node']['path'], str(actor_root / 'collect.mjs'), rr['rootAuthority']['path']]
    observation = data(runtime_outer / 'observation.json')
    assert observation['passed'] is observation['ownedGroupsClean'] is observation['protectedInputsPreserved'] is observation['guardProfileMatched'] is True
    assert observation['primaryError'] is observation['protectionError'] is None and observation['rawExitCode'] == 0
    assert ref(observation['terminal']) == blobs[str(runtime_outer / 'terminal.json')]
    assert ref(observation['result']) == blobs[str(runtime / 'result.json')]
    assert rr['state'] == 'GUARD_SAFE_REFUSAL_AND_BUILTIN_OBSERVED_V1'
    assert rr['observationsValid'] is rr['guardProfileMatched'] is rr['inputsPreserved'] is rr['fixtureCopyPreserved'] is True
    assert rr['errors'] == [] and rr['server']['forcedCleanup'] is False
    assert rr['server']['shutdownRequested'] is rr['server']['sigintSent'] is True
    assert rr['server']['exit'] == dict(code=0, signal=None, error=None)
    response = rr['response']; raw_body = ref(response['body'])
    assert response['method'] == 'GET' and response['url'] == rr['portLease']['origin'] + '/probe'
    assert rr['portLease']['singleAttempt'] is True and rr['portLease']['fallbackAllowed'] is False
    assert response['status'] == 200 and response['complete'] is True and response['overflow'] is False
    assert response['transportError'] is None and response['readerCleanupErrors'] == []
    assert response['receivedBytes'] == response['retainedPrefixBytes'] == len(raw_body) == 1065
    assert sha(raw_body) == 'b3f1085409114464c337cd62b937f3a9ee699769fa1594c241406650202fb41a'
    body = parse(raw_body); assert body == response['payload']
    assert body['schemaVersion'] == body['call'] == 1 and body['suite'] == 'REAL_COMPONENT_CJS_FILE_URL_PROBE_V1' and body['mode'] == 'guard'
    assert type(body['caseCount']) is type(body['expectedCaseCount']) is int and body['caseCount'] == body['expectedCaseCount'] == 2
    assert body['exactCaseIds'] is body['profilePassed'] is True
    assert [row['id'] for row in body['records']] == ['cjs-dynamic-builtin', 'guard-natural-fileurl-refusal']
    assert all(row['passed'] is True and 'error' not in row for row in body['records'])
    assert body['records'][0]['observation'] == dict(sameJoin=True, joined='/probe/child')
    refusal = body['records'][1]['observation']
    assert refusal['rejected'] is refusal['isTypeError'] is refusal['moduleMatchesActualSpecifier'] is True
    assert refusal['code'] == 'ERR_SM_MODULE_IMPORT_REFERRER' and refusal['operation'] == 'module_load_hook'
    assert refusal['error']['type'] == 'object' and refusal['error']['isNull'] is False
    for key, value in [('code', 'ERR_SM_MODULE_IMPORT_REFERRER'), ('operation', 'module_load_hook'), ('module', 'file:///probe/target.cjs')]:
        assert refusal['error'][key] == dict(type='string', value=value)
    for key in ['guardRefusalIsNodeCompatibilityPass', 'nodeReferenceExecuted', 'applicationImported', 'fullNextClaim',
                'namespaceLimit8192Exercised', 'symlinkReentrancyRealmOrRaceParityProved']:
        assert body[key] is False
    probe_plan = parse(ref(ra['plan']))
    assert probe_plan['mode'] == 'guard' and probe_plan['requests'] == 1 and probe_plan['reuseCount'] == 128 and probe_plan['idleInstanceTimeout'] == '60s'
    expected_fixture_root = runtime / 'fixtures'
    fixture = rr['fixtures']; assert fixture['root'] == str(expected_fixture_root) and fixture['mode'] == 0o555
    assert fixture['physicalReadOnlyOnly'] is True and fixture['readonlyWasiPreopenRightsProved'] is False
    assert len(fixture['files']) == len(probe_plan['fixtures']) == 8
    assert {row['path'] for row in fixture['files']} == {str(expected_fixture_root / row['relativePath']) for row in probe_plan['fixtures']}
    for observed, source in zip(fixture['files'], probe_plan['fixtures']):
        assert observed['path'] == str(expected_fixture_root / source['relativePath']) and observed['mode'] == 0o444 and observed['nlink'] == 1
        assert observed['sha256'] == source['source']['sha256'] and observed['bytes'] == source['source']['bytes']
        assert ref(observed) == ref(source['source'])
    command = rr['server']['command']; port = str(rr['portLease']['port'])
    assert command == [probe_plan['wasmtime']['path'], 'serve', '--addr', '127.0.0.1:' + port, '-S',
                       'cli=y,tcp=n,udp=n,allow-ip-name-lookup=n', '--max-instance-reuse-count', '128',
                       '--idle-instance-timeout', '60s', '--dir', str(expected_fixture_root) + '::/probe', artifacts['component']['path']]
    for key in ['wasmtime.stdout.log', 'wasmtime.stderr.log']: ref(rr['server'][key])
    root_world = parse(ref(ix['roles']['guard-ca84-probe-first-full-native-world-guard.json']))
    assert root_world['authority'] == rr['rootAuthority'] and root_world['before'] == root_world['after'] == expected_world
    assert root_world['unchanged'] is root_world['nativeInputsPreserved'] is True and root_world['rootReportedActorExitCode'] == 0
    assert root_world['freeBytesAtAdmission'] >= root_world['minimumFreeBytes'] == 1073741824
    for key in ['fullBuildGuardImplementation', 'worldGuardImplementation']: ref(ra[key])
    runtime_review = parse(ref(ix['roles']['actual-runtime-review.json']))
    assert runtime_review['dataConsistent'] is runtime_review['guardProfileMatched'] is True
    assert ref(runtime_review['actualResult']) == blobs[str(runtime / 'result.json')]
    assert runtime_review['response']['rawBody'] == response['body'] and runtime_review['rootFullNativeWorldReceipt'] == ix['roles']['guard-ca84-probe-first-full-native-world-guard.json']
    for flag in ['nodeCompatibilityAccepted', 'fullNextAcceptance', 'adoption']:
        assert rr[flag] is observation[flag] is False
    assert runtime_review['nodeCompatibilityAccepted'] is runtime_review['interopOrFullNextAccepted'] is False

    if args.current:
        current = []
        for row in ix['files']:
            path = Path(row['original']['path']); assert path.is_absolute() and path.resolve(strict=True) == path
            before = identity(path)
            assert before == row['physicalBefore'] and stat.S_ISREG(before[2]) and before[3] == 1
            assert stat.S_IMODE(before[2]) == row['mode'] and path.read_bytes() == ref(row['original'])
            assert identity(path) == before; current.append((path, before))
        root_stat = expected_fixture_root.lstat()
        assert stat.S_IMODE(root_stat.st_mode) == 0o555 and [root_stat.st_dev, root_stat.st_ino, root_stat.st_nlink] == [fixture['dev'], fixture['ino'], fixture['nlink']]
        assert {p.name for p in expected_fixture_root.iterdir()} == {row['relativePath'] for row in probe_plan['fixtures']}
        for observed, source in zip(fixture['files'], probe_plan['fixtures']):
            target_stat, source_stat = Path(observed['path']).stat(), Path(source['source']['path']).stat()
            assert (target_stat.st_dev, target_stat.st_ino) != (source_stat.st_dev, source_stat.st_ino)
        for path, before in current: assert identity(path) == before
    print(json.dumps(dict(portableDataPassed=True, capsuleSealed=sealed, members=len(rows), logicalBytes=ix['logicalBytes'],
                         currentRetainedOriginalsChecked=args.current, constructorInitPassed=True, standardInterfaces=13,
                         fullNativeCompileRows=80, separateEmbeddingRows=1, actualGuardCases=2,
                         builtinImportAndCodedSafeRefusalObserved=True, nodeCompatibilityAccepted=False,
                         interopOrFullNextAccepted=False, actorOrNetworkInvoked=False)))


if __name__ == '__main__':
    main()
