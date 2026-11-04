# Executed only as appended read-only verifier source, never a host runner.
import copy

BASE = CAP.parent
PREHOST = BASE/'production-http-prehost-verification-v1'
checked(PREHOST/'index.json','80c31ce1fc1618d5f85f1e75f4bbe6bae12aa7acc945e962229f1246f8edfd41')
for row in read(PREHOST/'index.json')['files']:
    checked(PREHOST/row['path'],row['sha256'],row['bytes'])
checked(PREHOST/'results.json','fe7880ab12e5a7dc326ede5f54013f00e42dfaf3031d5baf98bfc862d1976621')
phase = BASE/'production-http-phase-review-v1'
phase_index = checked(phase/'index.json')
assert phase_index.startswith('0f25af46') and phase_index.endswith('e83c')
for row in read(phase/'index.json')['files']:
    checked(phase/row['path'],row['sha256'],row['bytes'])
checked(phase/'results.json','47bb24ddbd5c66b5f2e7b3d71c28abf81785ab26e3a42129cdac8fe259bd216a')
checked(CAP/'http-component-pins.json','84a92618f415942e8c2afc70cc0734fbe35db284157bc2ddf319f7dc2cdc8aa3')
assert (CAP/'http-component-pins.json').read_bytes() == (phase/'reviewed-http-component-pins.json').read_bytes()
assert read(phase/'previous-null-http-component-pins.json')['component'] is None
pins = read(CAP/'http-component-pins.json')
assert pins['component']['state'] == 'reviewed-real-runtime-http-component'
expected_component = dict(seal)
expected_component.update(state='reviewed-real-runtime-http-component',
    preHostIndependentReviewResultsPath='tests/node-compat/foundation-scheduler/production-http-prehost-verification-v1/results.json',
    preHostIndependentReviewResultsSha256='fe7880ab12e5a7dc326ede5f54013f00e42dfaf3031d5baf98bfc862d1976621',runtimeAcceptanceClaim=False)
assert pins['component'] == expected_component
assert (CAP/'http-component-pins.json').resolve() not in source_map
assert (CAP/'index.json').resolve() not in source_map
checked(CAP/'index.json','c1ba69b0c6845dc453d8205a5e87d61c88c8633147a04d0c53d7966dbdb89c13')
assert len(read(CAP/'index.json')['files']) == 59
for row in read(CAP/'index.json')['files']:
    checked(CAP/row['path'],row['sha256'],row['bytes'])

checked(ROOT/'http-results.json','99a8799a1649285d5d544dc63d9a1dc046fc32e8fb3d90a1a9ee151740b6d1fe')
aggregate = read(ROOT/'http-results.json')
assert aggregate['state'] == 'PRODUCTION306_HTTP_BOTH_UNMODIFIED_HOSTS_PASSED'
assert aggregate['nativeAdmission'] == a['currentProductionAdmission']
assert aggregate['nativeSourceManifest'] == metadata['sourceManifest']
assert aggregate['sourceFilesVerified'] == manifest['inputs']
assert aggregate['component']['sha256'] == seal['componentSha256']
assert aggregate['component']['bytes'] == 63639194
assert aggregate['component']['emittedImports'] == EXPECTED and aggregate['component']['emittedExports'] == EXPORTS
assert aggregate['component']['clockDependency'] == a['clockDependency']
assert aggregate['protectedAbortGroups'] == {'public':16,'nested':4,'receivers':9,'total':29}
assert aggregate['instanceReuseClaim'] is False and aggregate['foundationSchema'] == 5
for row in aggregate['artifacts']:
    checked(row['path'],row['sha256'],row['bytes'])

wt_path = OUT/'wasmtime-v1/wasmtime-results.json'
wc_path = ROOT/'http-joint-wasmcloud-results.json'
checked(wt_path,'8856c0389de6bea514245cc8f5600356a341723c78b68cde1bc1b877b9648169')
checked(wc_path,'4215f60c2ee5060362afa657204df5b44f83e6ecba8f061053053bf677a87f0e')
wt,wc = read(wt_path),read(wc_path)
wt_binary = Path(wt['command'][0])
checked(wt_binary,'a85dec9fcbbad23d0e038e5a99604114dbe9aa77bc784e4bce0f33013eb33c1c')
assert wt['wasmtime'] == 'wasmtime 42.0.1 (6844a83b5 2026-02-25)'
assert wt['command'] == [str(wt_binary),'serve','--addr','127.0.0.1:0',str(component_path)]
assert wt['componentSha256'] == seal['componentSha256'] and wt['componentBytes'] == 63639194
assert wt['emittedImports'] == EXPECTED and wt['emittedExports'] == EXPORTS
assert wt['address'].startswith('http://127.0.0.1:')
wash = wc['host']
assert wash['unmodifiedOfficialBinary'] is True and wash['version'] == '2.11.0'
assert wash['sourceCommit'] == 'bc5acfb8e15f7d6d199ca940354d82e590c2d5ff'
assert wash['embeddedWasmtimeVersion'] == '48.0.7'
assert wash['binarySha256'] == '365d896eaed3894f1c551a1ed7351c2aae9dfa5548ce82041ead92e6253d1954'
checked(wash['binaryPath'],wash['binarySha256'])
assert wc['component']['sha256'] == seal['componentSha256'] and wc['component']['bytes'] == 63639194
checked(wc['component']['deployedPath'],seal['componentSha256'],63639194)
assert wc['componentAudit'] == a
assert wc['component']['emittedImports'] == EXPECTED
assert sorted(wc['component']['allowedImports']) == EXPECTED and len(set(wc['component']['allowedImports'])) == 6
assert wc['hostInspection']['success'] is True
assert wc['hostInspection']['emittedImports'] == EXPECTED and wc['hostInspection']['emittedExports'] == EXPORTS
assert wc['hostInspection']['emittedWit'] == wit
assert wc['command'][0] == wash['binaryPath'] and wc['command'][-1] == 'dev'
assert wc['configuration'] == read(Path(wc['configPath']))
checked(wc['configPath'])
assert wc['configuration']['wit']['skip_fetch'] is True
for key in ['allowedHosts','allowedIpNameLookups','allowedHostLoopbackPorts']:
    assert wc['configuration']['workload'][key] == wc['effectiveConfiguration']['workload'][key] == []
for key in ['plugins','host_plugins','components','volumes']:
    assert wc['configuration']['dev'][key] == []
assert wc['effectiveConfiguration']['dev']['service'] is False
assert wc['effectiveConfiguration']['dev']['wasi_otel'] is False and wc['effectiveConfiguration']['dev']['wasi_webgpu'] is False
assert wc['effectiveConfiguration']['dev']['wasm_proposals'] == []
isolation = wc['isolation']
assert isolation['publicListener'] is False and isolation['globalInstallationModified'] is False
assert isolation['userConfigOverridden'] is True and isolation['isolatedXdgDirectories'] is True
assert isolation['dockerUsed'] is False and isolation['natsUsed'] is False
for key in ['outgoingHostAllowlist','ipNameLookupAllowlist','hostLoopbackPortAllowlist','customHostPlugins','sidecars','volumes']:
    assert isolation[key] == []
assert isolation['address'] == wc['effectiveConfiguration']['dev']['address']
assert isolation['address'].startswith('127.0.0.1:')
user_config = Path(wc['command'][wc['command'].index('--user-config')+1])
checked(user_config)
assert read(user_config) == {}
assert wc['configInspectionCommand'][:5] == wc['command'][:5]
run_root = user_config.parent
checked(run_root/'host-results.json',sha(wc_path))
for host in [wt,wc]:
    assert host['process']['stopped'] is True and host['process']['exitStatus'] == {'code':0,'signal':None}
    checked(host['process']['logPath'])
    assert len(host['responses']) == 3 and host['retainedStateObserved'] is False

def normalized_body(body):
    body = copy.deepcopy(body)
    body.pop('requestTag')
    secure = body['native']['entropyIntegration']['secure']
    for key in ['bytes','uuid','multipartContentType']:
        secure.pop(key)
    return body

baseline = normalized_body(wt['responses'][0]['body'])
secure_bytes,secure_uuids = [],[]
host_summaries = []
for product,host in [('stock-wasmtime42',wt),('official-wash2.11',wc)]:
    counters = []
    for request,response in enumerate(host['responses'],1):
        assert response['status'] == 200
        body = response['body'];tag = '/node-compat?request='+str(request)
        assert body['requestTag'] == response.get('requestTag',response.get('request')) == tag
        assert body['schema'] == 1 and body['componentInstanceRequestCount'] == 1
        counters.append(body['componentInstanceRequestCount'])
        assert body['snapshotMarker'] == 'HTTP module initialized during componentization'
        assert normalized_body(body) == baseline
        native = body['native']
        assert native['coreVersion'] == 'sm-node-22.14.0-m0.11' and native['allocUnsafePolicy'] == 'zeroed-no-pool-direct-u8-v1'
        assert native['calls'] == 1 and native['strings'] == 381 and native['bytes'] == 250
        assert native['unavailableMethods'] == 91 and native['stubCalls'] == native['stubConstructors'] == 9
        assert native['globalBufferIdentity'] is True and native['staticCommonJS'] is True
        for key in ['unsupported','unsupportedConstructor']:
            failure = body[key]
            assert set(failure) == {'code','module','operation','profile'}
            assert failure['code'] == 'ERR_SM_NODE_UNSUPPORTED' and failure['module'] == 'node:child_process'
            assert failure['profile'] == 'sm-node-22.14.0-m0.11'
        entropy = native['entropyIntegration']
        assert entropy['policy'] == entropy['secure']['policy'] == 'runtime-only'
        assert len(entropy['snapshot']) == 4 and all(row['code']=='ERR_SM_ENTROPY_INITIALIZATION' for row in entropy['snapshot'])
        assert entropy['snapshotRsa']['succeeded'] is False
        assert entropy['rsa']['algorithm'] == 'RSASSA-PKCS1-v1_5' and entropy['rsa']['modulusLength'] == 2048
        assert re.fullmatch('[0-9a-f]{64}',entropy['secure']['bytes'])
        assert re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}',entropy['secure']['uuid'])
        assert entropy['secure']['multipartContentType'].startswith('multipart/form-data; boundary=--StarlingMonkeyFormBoundary')
        secure_bytes.append(entropy['secure']['bytes']);secure_uuids.append(entropy['secure']['uuid'])
        foundation = native['foundations']
        assert foundation['schema'] == 5 and foundation['calls'] == 1
        assert foundation['aliases']['firstDeployedCall'] is True and foundation['aliases']['computedBareImports'] is True
        assert [row['id'] for row in foundation['aliases']['aliases']] == a['foundationOracles']['dynamicBareAliases']
        assert all(row['cache'] is True and row['exportValues'] is True and row['defaultIdentity'] is True and row['thenType']=='undefined' for row in foundation['aliases']['aliases'])
        for key in ['publicCases','nestedOnceCases','receiverCases']:
            assert foundation['protectedAbort'][key] == a['foundationOracles']['protectedAbort'][key]
        assert [len(foundation['protectedAbort'][key]) for key in ['publicCases','nestedOnceCases','receiverCases']] == [16,4,9]
        assert foundation['stringDecoder']['passed'] is True and foundation['streamWeb']['passed'] is True
    assert counters == [1,1,1]
    host_summaries.append(dict(product=product,requests=3,statuses=[200]*3,counters=counters,stopped=True,exitStatus={'code':0,'signal':None}))
assert len(set(secure_bytes)) == len(set(secure_uuids)) == 6
assert [host['counters'] for host in aggregate['hosts']] == [[1,1,1],[1,1,1]]
assert any('then-getter' in value and '1/1/0' in value and '0/0/0' in value for value in aggregate['limitations'])
for path in ROOT.glob('*.log'):
    checked(path)
for row in list(verified.values()):
    checked(row['path'],row['sha256'],row['bytes'])
result = dict(schemaVersion=1,state='INDEPENDENT_PRODUCTION_HTTP_POSTHOST_VERIFICATION_PASSED',verifiedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    aggregateResultsSha256=sha(ROOT/'http-results.json'),componentSha256=seal['componentSha256'],componentBytes=63639194,
    engineSha256=a['engineSha256'],prehostReviewIndexSha256=sha(PREHOST/'index.json'),phaseReviewIndexSha256=phase_index,
    httpPhasePinSha256=sha(CAP/'http-component-pins.json'),capabilityFinalIndexSha256=sha(CAP/'index.json'),capabilityIndexedFiles=59,
    sourceInputsUnchanged=778,nativeSources=306,frozenEngineCopiesRehashed=335,liveComputedInputsRehashed=8,
    binaryImports=sorted(imports),binaryExports=exports,clockBinaryAndTypeGraphDurationOnlyU64=True,clockCallableImports=[],clockCoreImports=[],
    rawAndEmbeddedCoreNoncustomSectionsIdentical=True,priorCoreCustomSectionExplanationPreserved=True,
    hosts=host_summaries,washOfficialBinarySha256=wash['binarySha256'],stockWasmtimeSha256=sha(wt_binary),washEffectiveAllowlistsEmpty=True,
    noCustomPluginsSidecarsVolumes=True,sameComponentBytesOnBothHosts=True,allSixResponseBodiesMatchExceptRequestTagAndThreeExplicitRandomFields=True,
    observedDistinctSecureByteStrings=6,observedDistinctUuids=6,protectedAbortGroupsPerResponse=29,firstDeployedBareAliasesPerResponse=14,
    observedInstanceCounters=[1,1,1],instanceReuseOrRequestIsolationClaim=False,phaseChangeExcludedFromSourceSeal=True,
    verifiedFiles=list(verified.values()),limitations=[
        'This independently reads and validates recorded host execution, not a rerun of either host, guest, packager, Node oracle or source test.',
        'Normalized complete response equality removes only requestTag and secure bytes/UUID/multipart boundary; distinct samples are observations, not an entropy-quality or general isolation proof.',
        'Binary parsing rechecks root imports/exports, exact duration-only clock type and embedded core imports; complete Component Model validation is not rerun.',
        'Known callback-return getter Node1/1/0 versus guest0/0/0, Symbol.dispose identity and GC co-ownership limits remain.',
        'Full Node HTTP/process/stream compatibility, explicit reset, ALS/request teardown and performance/memory advantages are not established.',
        'Latest milestone acceptance/archive is Root-owned; these bounded HTTP host results alone do not close the full roadmap.'],
    hostGuestNativeNinjaNodeOraclePackagerOrValidationToolExecuted=False,existingSourceArtifactsConfigsOrResultsModified=False)
with (HERE/'results.json').open('x') as stream:
    json.dump(result,stream,indent=2);stream.write('\n')
print(json.dumps(dict(state=result['state'],resultSha256=sha(HERE/'results.json'),verifiedPaths=len(verified),hostRequests=6)))
